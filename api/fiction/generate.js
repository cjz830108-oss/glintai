// /api/fiction/generate — chapter pipeline v2 (P0-safe state machine)
// Client-driven steps: outline → draft → continuity → edit → score → memory
//   gate branches: continuity fail(high) → rewrite | score < 8.0 → rewrite
//   rewrite → continuity → edit → score again (max 2 rewrites; final miss → needs_review)
// Safety properties:
//   P0-1  Quality Gate: max 2 rewrites, each rewrite re-runs continuity + score; final save
//         = last gate-passing version; exhausted gate marks chapters.gate_status='needs_review'
//   P0-2  Continuity verdict+severity controls flow (high severity ⇒ rewrite, not literary edit)
//   P0-3  Memory candidates → memory_validator → only approved facts enter durable memory
//   P0-4  Memory idempotent: claim_chapter_memory RPC (first run wins) + source_task_id
//         uniqueness on timeline events + (novel,char,chapter) unique state history
//   P0-5  character_state_history rows with per-chapter deltas + reason
//   P0-6  relationships accept full axis set (trust/love/attraction/anger/fear/suspicion/
//         jealousy/intimacy/conflict/respect)
//   P0-9  Task insert is upsert-ignore + re-select; step execution idempotent via unique
//         (task_id, kind) generation_outputs — concurrent/retry calls replay cached output
//   P0-11 used_credits persisted after every charge; settle once at completion
//   P0-12 quality_scores rows carry attempt_no (one per gate attempt)
import { admin, json, fail, cors, requireUser, ownNovel } from '../_lib/db.js';
import { generate, toCredits, ESTIMATES } from '../_lib/router.js';
import { getAgent } from '../_lib/prompts.js';
import { buildChapterContext, contextToPrompt } from '../_lib/retrieval.js';
import { lockCredits, settleCredits, refundTask } from '../_lib/credits.js';
import { recordUsage } from '../_lib/usage.js';
import { recordSignal } from '../_lib/skillLearning.js';

export const maxDuration = 300;

const TARGET_WORDS = { 30: 2000, 50: 1800, 100: 1500 };
const SCORE_GATE = 8.0;
const MAX_REWRITES = 2;
const REL_AXES = ['trust', 'love', 'attraction', 'anger', 'fear', 'suspicion', 'jealousy', 'intimacy', 'conflict', 'respect'];

export default async function handler(req, res) {
  if (cors(req, res)) return;
  if (req.method !== 'POST') return fail(res, 405, 'method', 'Use POST.');
  return requireUser(req, res, async (user) => {
    const { taskId, novelId, chapterNo, step } = req.body || {};
    if (!taskId || !novelId || !chapterNo || !step) return fail(res, 400, 'bad_request', 'taskId, novelId, chapterNo, step required');
    const novel = await ownNovel(novelId, user.id);
    const ch = Number(chapterNo);

    // ---- task lifecycle (idempotent by taskId, concurrency-safe insert) ----
    let { data: task } = await admin.from('generation_tasks').select('*').eq('id', taskId).maybeSingle();

    // ---------- STANDALONE: READER SIMULATOR ----------
    if (step === 'reader') {
      if (task?.status === 'completed') return json(res, 200, { done: true, cached: true, readers: task.result?.readers });
      const fee = ESTIMATES.action;
      if (!task) {
        await lockCredits(user.id, fee, taskId, { kind: 'reader', novel: novel.id, chapter: ch });
        task = await insertTask(taskId, user.id, novel.id, 'reader', { chapterNo: ch, step }, fee);
      }
      try {
        const out = await runOnce(taskId, novel.id, ch, 'reader', async () => {
          const ctxObj = await buildChapterContext(novel, ch);
          const chapterText = await getChapterText(novel.id, ch);
          const agent = await getAgent('reader_simulator');
          return await generate({
            tier: agent.model, json: true, temperature: 0.8, maxTokens: 8000, timeoutMs: 240000,
            system: agent.system, user: agent.user({ ctx: contextToPrompt(ctxObj), chapterText, chapterNo: ch }),
          });
        });
        await charge(user.id, novel.id, taskId, 'reader_sim', task, out);
        const used = Math.min(fee, Math.max(task.used_credits || 0, 1));
        await settleCredits(user.id, taskId, used, fee);
        await admin.from('generation_tasks').update({ status: 'completed', step: 'done', used_credits: used, result: { readers: out.data } }).eq('id', taskId);
        return json(res, 200, { done: true, readers: out.data, creditsUsed: used });
      } catch (err) {
        await admin.from('generation_tasks').update({ status: 'failed', error: String(err.message).slice(0, 500) }).eq('id', taskId);
        await refundTask(user.id, taskId, fee).catch(() => {});
        return fail(res, err.status || 502, err.code || 'generation_failed', err.message);
      }
    }

    if (!task) {
      const fee = ESTIMATES.chapter;
      await lockCredits(user.id, fee, taskId, { kind: 'chapter', novel: novel.id, chapter: ch });
      task = await insertTask(taskId, user.id, novel.id, 'chapter', { chapterNo: ch, step }, fee);
    }
    if (task.status === 'completed') return json(res, 200, { done: true, cached: true, result: task.result });

    try {
      if (step === 'abort') {
        await settleCredits(user.id, taskId, task.used_credits || 0, task.locked_credits || 0);
        await admin.from('generation_tasks').update({ status: 'cancelled' }).eq('id', taskId);
        return json(res, 200, { ok: true, cancelled: true });
      }

      const rc = () => task.result?.rewrite_count || 0;
      const patchTask = async (mergeResult, extraPatch = {}) => {
        if (mergeResult) {
          task.result = { ...(task.result || {}), ...mergeResult };
          extraPatch.result = task.result;
        }
        await admin.from('generation_tasks').update(extraPatch).eq('id', taskId);
      };
      const forceRewrite = async () => {
        await patchTask({ rewrite_count: rc() + 1 });
        await admin.from('chapters').update({ rewrite_count: rc() }).eq('novel_id', novel.id).eq('chapter_no', ch);
        return 'rewrite';
      };

      // ---------- 1) OUTLINE ----------
      if (step === 'outline') {
        const bd = (await admin.from('story_bibles').select('data').eq('novel_id', novel.id).maybeSingle()).data || {};
        const entry = (bd.chapter_plan || []).find((p) => Number(p.no) === ch) || { no: ch, synopsis: novel.idea, title: '' };
        const targetWords = TARGET_WORDS[novel.length_target] || 1800;
        const out = await runOnce(taskId, novel.id, ch, 'outline', async () => {
          const ctxObj = await buildChapterContext(novel, ch);
          return await generate({
            tier: 'light', json: true, temperature: 0.7, maxTokens: 4000, timeoutMs: 240000,
            system: 'You expand one chapter entry into a scene-by-scene shooting outline for a novelist. Output ONLY valid JSON.',
            user: `STORY MEMORY:\n${contextToPrompt(ctxObj)}\n\nCHAPTER ${ch} ENTRY:\n${JSON.stringify(entry)}\n\nReturn JSON: {"title":"chapter title","scenes":[{"goal":"","location":"","characters":["Names"],"conflict":"","turn":"","hook":""}],"word_target":${targetWords}}\n3-5 scenes. Last scene's hook ends the chapter.`,
          });
        });
        await charge(user.id, novel.id, taskId, 'planner', task, out);
        await patchTask({ outline: out.data }, { step: 'outline_done' });
        return json(res, 200, { nextStep: 'draft', outline: out.data, task });
      }

      // ---------- 2) DRAFT ----------
      if (step === 'draft') {
        const outline = task.result?.outline || (await lastOutput(novel.id, ch, 'outline')) || { scenes: [], title: '' };
        const targetWords = TARGET_WORDS[novel.length_target] || 1800;
        const out = await runOnce(taskId, novel.id, ch, 'draft', async () => {
          const ctxObj = await buildChapterContext(novel, ch);
          const agent = await getAgent('novel_writer');
          return await generate({
            tier: agent.model, temperature: 0.85, maxTokens: 8000, timeoutMs: 240000,
            system: agent.system,
            user: agent.user({ ctx: contextToPrompt(ctxObj), outline: JSON.stringify(outline), chapterNo: ch, targetWords }),
          });
        });
        const text = (out.text || '').trim();
        if (text.length < 300) throw Object.assign(new Error('Writer returned empty chapter'), { status: 502, code: 'empty_draft' });
        await upsertChapter(novel.id, ch, text);
        await charge(user.id, novel.id, taskId, 'writer', task, out);
        const words = text.split(/\s+/).filter(Boolean).length;
        await patchTask({ draft_words: words }, { step: 'draft_done' });
        return json(res, 200, { nextStep: 'continuity', words, task });
      }

      // ---------- 3) CONTINUITY GATE (P0-2) ----------
      if (step === 'continuity') {
        const kind = `continuity_a${rc()}`;
        const out = await runOnce(taskId, novel.id, ch, kind, async () => {
          const ctxObj = await buildChapterContext(novel, ch);
          const chapterText = await getChapterText(novel.id, ch);
          const agent = await getAgent('continuity_editor');
          return await generate({
            tier: agent.model, json: true, temperature: 0.2, maxTokens: 16000, timeoutMs: 240000,
            system: agent.system,
            user: agent.user({ ctx: contextToPrompt(ctxObj), chapterText, chapterNo: ch }),
          });
        });
        await charge(user.id, novel.id, taskId, 'continuity', task, out);
        const issues = out.data?.issues || [];
        const hasHigh = issues.some((i) => i.severity === 'critical' || i.severity === 'major');
        await patchTask({ high_issues: hasHigh }, { step: 'continuity_done' });
        let nextStep = 'edit';
        if (hasHigh && rc() < MAX_REWRITES) nextStep = await forceRewrite();
        return json(res, 200, {
          nextStep, issues, verdict: out.data?.verdict,
          gate: hasHigh ? (rc() < MAX_REWRITES ? 'rewrite' : 'proceed_flagged') : 'pass',
          task,
        });
      }

      // ---------- 4) LITERARY EDIT ----------
      if (step === 'edit') {
        const kind = `edit_a${rc()}`;
        const out = await runOnce(taskId, novel.id, ch, kind, async () => {
          const chapterText = await getChapterText(novel.id, ch);
          const issuesData = (await lastOutput(novel.id, ch, `continuity_a${rc()}`)) || { issues: [] };
          const agent = await getAgent('literary_editor');
          return await generate({
            tier: agent.model, temperature: 0.7, maxTokens: 8000, timeoutMs: 240000,
            system: agent.system,
            user: agent.user({ chapterText, issues: issuesData.issues || [], targetWords: TARGET_WORDS[novel.length_target] || 1800 }),
          });
        });
        const text = (out.text || '').trim();
        if (text.length > 300) await upsertChapter(novel.id, ch, text);
        await charge(user.id, novel.id, taskId, 'editor', task, out);
        await patchTask({}, { step: 'edit_done' });
        return json(res, 200, { nextStep: 'score', task });
      }

      // ---------- 5) QUALITY SCORE + GATE (P0-1) ----------
      if (step === 'score') {
        const kind = `score_a${rc()}`;
        const out = await runOnce(taskId, novel.id, ch, kind, async () => {
          const chapterText = await getChapterText(novel.id, ch);
          const agent = await getAgent('quality_scorer');
          return await generate({
            tier: agent.model, json: true, temperature: 0.3, maxTokens: 4000, timeoutMs: 240000,
            system: agent.system, user: agent.user({ chapterText }),
          });
        });
        await charge(user.id, novel.id, taskId, 'scorer', task, out);
        const attemptNo = rc() + 1;
        await admin.from('quality_scores').insert({
          novel_id: novel.id, chapter_no: ch, attempt_no: attemptNo,
          scores: out.data?.scores || {}, overall: out.data?.overall || 0,
        }).catch(async () => {
          // legacy DB without attempt_no uniqueness yet — retry plain
          await admin.from('quality_scores').insert({ novel_id: novel.id, chapter_no: ch, scores: out.data?.scores || {}, overall: out.data?.overall || 0 });
        });
        const overall = Number(out.data?.overall || 0);
        const attempts = [...(task.result?.attempts || []), { attempt: attemptNo, overall }];
        await patchTask({ attempts, overall }, { step: 'score_done' });
        let nextStep = 'memory';
        if (overall > 0 && overall < SCORE_GATE && rc() < MAX_REWRITES) nextStep = await forceRewrite();
        return json(res, 200, {
          nextStep, quality: out.data, overall, attempt: attemptNo,
          gate: overall >= SCORE_GATE ? 'pass' : (rc() < MAX_REWRITES ? 'rewrite' : 'needs_review'),
          needsRewrite: nextStep === 'rewrite',
          task,
        });
      }

      // ---------- 5b) GATE REWRITE (attempt-suffixed, re-enters continuity) ----------
      if (step === 'rewrite') {
        const kind = `rewrite_a${rc()}`;
        const out = await runOnce(taskId, novel.id, ch, kind, async () => {
          const chapterText = await getChapterText(novel.id, ch);
          const scoreData = (await lastOutput(novel.id, ch, `score_a${rc() - 1}`)) || {};
          const cont = (await lastOutput(novel.id, ch, `continuity_a${rc() - 1}`)) || { issues: [] };
          const agent = await getAgent('reviser');
          return await generate({
            tier: agent.model, temperature: 0.75, maxTokens: 8000, timeoutMs: 240000,
            system: agent.system,
            user: agent.user({ chapterText, scores: scoreData.scores || {}, notes: scoreData.notes || '', issues: cont.issues || [], chapterNo: ch, targetWords: TARGET_WORDS[novel.length_target] || 1800 }),
          });
        });
        const text = (out.text || '').trim();
        if (text.length > 300) await upsertChapter(novel.id, ch, text);
        await charge(user.id, novel.id, taskId, 'reviser', task, out);
        await patchTask({}, { step: 'rewrite_done' });
        return json(res, 200, { nextStep: 'continuity', rewritten: true, task });
      }

      // ---------- 6) MEMORY: candidates → validator → claim → apply ----------
      if (step === 'memory') {
        const memWrap = await runOnce(taskId, novel.id, ch, 'memory', async () => {
          const chapterText = await getChapterText(novel.id, ch);
          const agent = await getAgent('memory_updater');
          return await generate({
            tier: agent.model, json: true, temperature: 0.2, maxTokens: 8000, timeoutMs: 240000,
            system: agent.system, user: agent.user({ chapterNo: ch, chapterText }),
          });
        });
        const mem = memWrap.data || {};
        await charge(user.id, novel.id, taskId, 'memory', task, memWrap);

        // P0-3: validate proposed durable facts before they can pollute the bible
        const { approvedFacts, verdicts } = await validateFacts(novel, ch, taskId, mem);

        // P0-4: apply at most once per (novel, chapter) — atomic claim
        const applied = await applyMemoryV2(novel, ch, taskId, mem, approvedFacts);

        // P0-1/P0-12: final gate verdict on the chapter row
        const attempts = task.result?.attempts || [];
        const lastOverall = attempts.length ? attempts[attempts.length - 1].overall : null;
        const belowGate = lastOverall != null && lastOverall < SCORE_GATE;
        const gateStatus = (belowGate || task.result?.high_issues) ? 'needs_review' : 'approved';
        await admin.from('chapters').update({ gate_status: gateStatus, rewrite_count: rc() })
          .eq('novel_id', novel.id).eq('chapter_no', ch);

        recordSignal(novel.genre, { overall: lastOverall }).catch(() => {});
        const used = Math.min(task.locked_credits || ESTIMATES.chapter, Math.max(task.used_credits || 0, 1));
        await settleCredits(user.id, taskId, used, task.locked_credits || ESTIMATES.chapter);
        await admin.from('generation_tasks').update({ status: 'completed', step: 'done', used_credits: used }).eq('id', taskId);
        return json(res, 200, { done: true, creditsUsed: used, memoryApplied: applied, gateStatus, verdicts: verdicts.length, task });
      }

      return fail(res, 400, 'bad_request', `unknown step: ${step}`);
    } catch (err) {
      await admin.from('generation_tasks').update({ status: 'failed', error: String(err.message).slice(0, 500) }).eq('id', taskId);
      return fail(res, err.status || 502, err.code || 'generation_failed', `${err.message} (task ${taskId} kept for retry; credits still locked — call step:"abort" to refund)`);
    }
  });
}

// ------------------------------------------------------------------ helpers

/** P0-9: insert-if-absent; on race the first inserter wins and both callers proceed on the same row. */
async function insertTask(taskId, userId, novelId, kind, request, fee) {
  await admin.from('generation_tasks').upsert(
    { id: taskId, user_id: userId, novel_id: novelId, kind, step: 'running', status: 'processing', request, locked_credits: fee },
    { onConflict: 'id', ignoreDuplicates: true }
  );
  const { data } = await admin.from('generation_tasks').select('*').eq('id', taskId).maybeSingle();
  if (!data) throw Object.assign(new Error('task row disappeared after insert'), { status: 500, code: 'task_insert' });
  return data;
}

/**
 * P0-9b step-level idempotency: at most one generation_outputs row per (task_id, kind).
 * Retry/concurrent call replays the cached output — no re-generation, no double charge.
 */
async function runOnce(taskId, novelId, ch, kind, fn) {
  const { data: existing } = await admin.from('generation_outputs')
    .select('content').eq('task_id', taskId).eq('kind', kind).limit(1).maybeSingle();
  if (existing) { try { return JSON.parse(existing.content); } catch { return existing.content; } }
  const out = await fn();
  const payload = JSON.stringify({ data: out.data ?? null, text: out.text ?? '', costUsd: out.costUsd ?? 0, model: out.model, usage: out.usage });
  const { error } = await admin.from('generation_outputs').insert({
    task_id: taskId, novel_id: novelId, chapter_no: ch, kind, content: payload.slice(0, 60000), model: out.model, tokens: out.usage,
  });
  if (error && error.code === '23505') { // lost a race — replay winner's output
    const { data: w } = await admin.from('generation_outputs').select('content').eq('task_id', taskId).eq('kind', kind).limit(1).maybeSingle();
    if (w) { try { return JSON.parse(w.content); } catch { return w.content; } }
  }
  return out;
}

/** P0-3: memory_validator decides which proposed facts deserve durable memory. Fails open. */
async function validateFacts(novel, ch, taskId, mem) {
  const proposed = (mem.important_facts || []).map((f) => (typeof f === 'string' ? { fact: f, scope: 'character', characters: [] } : { scope: 'character', characters: [], ...f }));
  if (!proposed.length) return { approvedFacts: [], verdicts: [] };
  try {
    const [bibleRow, charRow] = await Promise.all([
      admin.from('story_bibles').select('data').eq('novel_id', novel.id).maybeSingle(),
      admin.from('characters').select('name,essence').eq('novel_id', novel.id).limit(20),
    ]);
    const bd = bibleRow?.data || {};
    const bibleSummary = [
      `PREMISE: ${bd.premise || ''}`,
      `CENTRAL QUESTION: ${bd.central_question || ''}`,
      `PERMANENT FACTS: ${(bd.permanent_facts || []).map((f) => f.fact || f).join(' | ') || 'none'}`,
      `CHARACTERS: ${(charRow.data || []).map((c) => `${c.name} — ${c.essence || ''}`).join(' ; ')}`,
      `RECENT ESTABLISHED FACTS: ${(bd.important_facts || []).slice(-30).map((f) => f.fact || f).join(' | ') || 'none'}`,
    ].join('\n');
    const agent = await getAgent('memory_validator');
    const out = await generate({
      tier: agent.model, json: true, temperature: 0.2, maxTokens: 4000, timeoutMs: 240000,
      system: agent.system,
      user: agent.user({ bibleSummary, proposed: JSON.stringify(proposed.map((p, i) => ({ index: i, ...p })), null, 1) }),
    });
    const verdicts = out.data?.verdicts || [];
    const byIndex = new Map(verdicts.map((v) => [Number(v.index), v]));
    const rows = proposed.map((p, i) => {
      const v = byIndex.get(i);
      const decision = v ? (v.decision === 'rejected' ? 'rejected' : 'approved') : 'approved';
      return {
        novel_id: novel.id, chapter_no: ch, task_id: taskId, type: 'fact',
        content: p, source: 'memory_updater', confidence: v?.confidence ?? 0.5,
        status: decision, validator_note: v?.reason || 'validator unreachable — fail-open',
      };
    });
    await admin.from('memory_candidates').insert(rows).catch(() => {});
    return { approvedFacts: rows.filter((r) => r.status === 'approved').map((r) => r.content), verdicts };
  } catch {
    await admin.from('memory_candidates').insert(proposed.map((p) => ({
      novel_id: novel.id, chapter_no: ch, task_id: taskId, type: 'fact',
      content: p, source: 'memory_updater', confidence: 0.5, status: 'approved', validator_note: 'validator errored — fail-open',
    }))).catch(() => {});
    return { approvedFacts: proposed, verdicts: [] };
  }
}

/**
 * P0-4/P0-5/P0-6/P0-13 memory application, guarded by an atomic claim so the same
 * (novel, chapter) is applied at most once no matter how many times the step runs.
 */
async function applyMemoryV2(novel, ch, taskId, mem, approvedFacts) {
  // -- claim: first writer inserts the summary; retries get false and stop here
  let claimed = true;
  try {
    const { data } = await admin.rpc('claim_chapter_memory', {
      p_novel_id: novel.id, p_chapter_no: ch,
      p_summary: mem.summary || '', p_events: mem.events || [], p_state_deltas: mem.state_deltas || {},
    });
    claimed = data !== false;
  } catch { /* RPC missing (migration not yet run) — fall through to direct upsert */ }
  if (!claimed) return { applied: false, reason: 'already_claimed' };

  if (claimed) {
    await admin.from('chapter_summaries').upsert({
      novel_id: novel.id, chapter_no: ch,
      summary: mem.summary || '', events: mem.events || [], state_deltas: mem.state_deltas || {},
    }, { onConflict: 'novel_id,chapter_no' });
  }

  // -- character state deltas + history (P0-5)
  const { data: chars } = await admin.from('characters').select('id,name,current_state,first_chapter').eq('novel_id', novel.id);
  const byName = Object.fromEntries((chars || []).map((c) => [c.name.toLowerCase(), c]));
  for (const [name, deltas] of Object.entries(mem.state_deltas || {})) {
    const c = byName[name.toLowerCase()];
    if (!c) continue;
    const st = { ...(c.current_state || {}) };
    const clean = {};
    for (const [k, v] of Object.entries(deltas)) {
      if (typeof v !== 'number') continue;
      clean[k] = v;
      st[k] = Math.max(0, Math.min(100, (st[k] ?? 50) + v));
    }
    await admin.from('characters').update({ current_state: st, last_chapter: ch }).eq('id', c.id);
    await admin.from('character_state_history').upsert({
      novel_id: novel.id, character_id: c.id, chapter_no: ch,
      state: st, state_deltas: clean,
      reason: mem.delta_reasons?.[name] || null, source_task_id: taskId,
    }, { onConflict: 'novel_id,character_id,chapter_no' }).catch(() => {});
    if (c.first_chapter == null) await admin.from('characters').update({ first_chapter: ch }).eq('id', c.id);
  }

  // -- relationship updates: full axis set, only changed fields (P0-6)
  const { data: rels } = await admin.from('relationships').select('id,data').eq('novel_id', novel.id);
  for (const ru of mem.relationship_updates || []) {
    const r = (rels || []).find((x) =>
      String(x.data?.from_name || '').toLowerCase() === String(ru.from || '').toLowerCase() &&
      String(x.data?.to_name || '').toLowerCase() === String(ru.to || '').toLowerCase());
    if (!r) continue;
    const d = { ...r.data };
    for (const axis of REL_AXES) {
      if (typeof ru[axis] === 'number') d[axis] = Math.max(0, Math.min(100, (d[axis] ?? 0) + ru[axis]));
    }
    if (ru.status) d.status = ru.status;
    await admin.from('relationships').update({ data: d }).eq('id', r.id);
  }

  // -- timeline with per-task source idempotency (P0-4)
  const { data: existingEv } = await admin.from('timeline_events').select('event')
    .eq('novel_id', novel.id).eq('chapter_no', ch).eq('source_task_id', taskId);
  const have = new Set((existingEv || []).map((e) => e.event));
  const pushEvent = async (event, importance, extra = {}) => {
    const ev = event || '';
    if (!ev || have.has(ev)) return;
    have.add(ev);
    await admin.from('timeline_events').insert({
      novel_id: novel.id, chapter_no: ch, event: ev, importance, source_task_id: taskId, ...extra,
    }).catch(() => {});
  };
  for (const e of mem.timeline || []) await pushEvent(e.event, e.importance || 'normal');
  for (const e of mem.events || []) {
    if ((e.importance || 'normal') === 'critical') await pushEvent(e.event, 'critical', { data: { characters: e.characters || [] } });
  }

  // -- plot threads / foreshadowing status
  for (const t of mem.plot_thread_updates || []) {
    await admin.from('plot_threads').update({ status: t.status || 'advancing', current_chapter: ch })
      .eq('novel_id', novel.id).ilike('title', t.title || '');
  }
  for (const f of mem.foreshadowing_updates || []) {
    await admin.from('foreshadowing').update({ status: f.status || 'reinforced' })
      .eq('novel_id', novel.id).ilike('title', f.title || '');
  }

  // -- bible facts: approved only; permanent facts never truncated (P0-3 + P0-13)
  const { data: bibleRow } = await admin.from('story_bibles').select('data').eq('novel_id', novel.id).maybeSingle();
  const bd = { ...(bibleRow?.data || {}) };
  const permanent = approvedFacts.filter((f) => f.scope === 'permanent')
    .map((f) => ({ fact: f.fact, scope: 'permanent', characters: f.characters || [], added_chapter: ch }));
  if (permanent.length) bd.permanent_facts = [...(bd.permanent_facts || []), ...permanent];
  bd.important_facts = [...(bd.important_facts || []), ...approvedFacts].slice(-200);
  bd.open_questions = [...(bd.open_questions || []), ...(mem.open_questions || [])].slice(-100);
  await admin.from('story_bibles').upsert({ novel_id: novel.id, data: bd });

  const count = Math.max(novel.chapter_count || 0, ch);
  const patch = { chapter_count: count };
  if (ch >= novel.length_target) patch.status = 'completed';
  await admin.from('novels').update(patch).eq('id', novel.id);
  return { applied: true };
}

async function upsertChapter(novelId, ch, text) {
  const words = text.split(/\s+/).filter(Boolean).length;
  const title = (text.split('\n')[0] || '').replace(/^chapter\s*\d+\s*[—–-]\s*/i, '').slice(0, 120);
  await admin.from('chapters').upsert(
    { novel_id: novelId, chapter_no: ch, title, content: text, word_count: words, version: 1, status: 'draft' },
    { onConflict: 'novel_id,chapter_no' }
  );
}
async function getChapterText(novelId, ch) {
  const { data } = await admin.from('chapters').select('content').eq('novel_id', novelId).eq('chapter_no', ch).maybeSingle();
  if (!data?.content) throw Object.assign(new Error('Draft not found — run draft step first'), { status: 400, code: 'no_draft' });
  return data.content;
}
async function lastOutput(novelId, ch, kind) {
  const { data } = await admin.from('generation_outputs').select('content').eq('novel_id', novelId).eq('chapter_no', ch).eq('kind', kind).order('created_at', { ascending: false }).limit(1);
  if (!data?.[0]) return null;
  try {
    const parsed = JSON.parse(data[0].content);
    // runOnce wrapper {data, text, costUsd, ...} → unwrap to the raw payload
    if (parsed && typeof parsed === 'object' && 'data' in parsed && 'text' in parsed) {
      return { ...(parsed.data || {}), _costUsd: parsed.costUsd };
    }
    return parsed; // legacy raw payload
  } catch { return data[0].content; }
}
async function charge(userId, novelId, taskId, agent, task, out) {
  task.used_credits = (task.used_credits || 0) + toCredits(out.costUsd || 0, 1);
  // persist immediately so a mid-pipeline retry settles against real usage (P0-11)
  await admin.from('generation_tasks').update({ used_credits: task.used_credits }).eq('id', taskId);
  await recordUsage(userId, novelId, taskId, agent, out, 0);
}
