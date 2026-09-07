// /api/fiction/generate — chapter pipeline (client-driven steps, resumable, idempotent)
// step: outline → draft → continuity → edit → score → memory   |  'abort' cancels + refunds
import { admin, json, fail, cors, requireUser, ownNovel } from '../_lib/db.js';
import { generate, toCredits, ESTIMATES } from '../_lib/router.js';
import { AGENTS } from '../_lib/prompts.js';
import { buildChapterContext, contextToPrompt } from '../_lib/retrieval.js';
import { lockCredits, settleCredits, refundTask } from '../_lib/credits.js';
import { recordUsage } from '../_lib/usage.js';

export const maxDuration = 300;

const TARGET_WORDS = { 30: 2000, 50: 1800, 100: 1500 };

export default async function handler(req, res) {
  if (cors(req, res)) return;
  if (req.method !== 'POST') return fail(res, 405, 'method', 'Use POST.');
  return requireUser(req, res, async (user) => {
    const { taskId, novelId, chapterNo, step } = req.body || {};
    if (!taskId || !novelId || !chapterNo || !step) return fail(res, 400, 'bad_request', 'taskId, novelId, chapterNo, step required');
    const novel = await ownNovel(novelId, user.id);
    const ch = Number(chapterNo);

    // ---- task lifecycle (idempotent by taskId) ----
    let { data: task } = await admin.from('generation_tasks').select('*').eq('id', taskId).maybeSingle();
    if (!task) {
      const fee = ESTIMATES.chapter;
      await lockCredits(user.id, fee, taskId, { kind: 'chapter', novel: novel.id, chapter: ch });
      await admin.from('generation_tasks').insert({
        id: taskId, user_id: user.id, novel_id: novel.id, kind: 'chapter', step,
        status: 'processing', request: { chapterNo: ch, step }, locked_credits: fee,
      });
      task = { id: taskId, locked_credits: fee, used_credits: 0, status: 'processing' };
    }
    if (task.status === 'completed') return json(res, 200, { done: true, cached: true, result: task.result });

    const finishStep = async (name, result) => {
      await admin.from('generation_tasks').update({ step: name, result: { ...(task.result || {}), ...result }, used_credits: task.used_credits }).eq('id', taskId);
    };

    try {
      if (step === 'abort') {
        await settleCredits(user.id, taskId, task.used_credits || 0, task.locked_credits || 0);
        await admin.from('generation_tasks').update({ status: 'cancelled' }).eq('id', taskId);
        return json(res, 200, { ok: true, cancelled: true });
      }

      const ctxObj = await buildChapterContext(novel, ch);
      const ctx = contextToPrompt(ctxObj);
      const targetWords = TARGET_WORDS[novel.length_target] || 1800;

      // ---------- 1) OUTLINE ----------
      if (step === 'outline') {
        const plan = (await getBibleData(novel.id)).chapter_plan || [];
        const entry = plan.find((p) => Number(p.no) === ch) || { no: ch, synopsis: novel.idea, title: '' };
        const out = await generate({
          tier: 'light', json: true, temperature: 0.7, maxTokens: 6000, timeoutMs: 240000,
          system: 'You expand one chapter entry into a scene-by-scene shooting outline for a novelist. Output ONLY valid JSON.',
          user: `STORY MEMORY:\n${ctx}\n\nCHAPTER ${ch} ENTRY:\n${JSON.stringify(entry)}\n\nReturn JSON: {"title":"chapter title","scenes":[{"goal":"","location":"","characters":["Names"],"conflict":"","turn":"","hook":""}],"word_target":${targetWords}}\n3-5 scenes. Last scene's hook ends the chapter.`,
        });
        await saveOutput(taskId, novel.id, ch, 'outline', JSON.stringify(out.data), out);
        await charge(user.id, novel.id, taskId, 'planner', task, out);
        await finishStep('outline_done', { outline: out.data });
        return json(res, 200, { nextStep: 'draft', outline: out.data, task });
      }

      // ---------- 2) DRAFT ----------
      if (step === 'draft') {
        const outline = (task.result?.outline) || (await lastOutput(novel.id, ch, 'outline')) || { scenes: [], title: '' };
        const agent = AGENTS.novel_writer;
        const out = await generate({
          tier: agent.model, temperature: 0.85, maxTokens: 8000, timeoutMs: 240000,
          system: agent.system,
          user: agent.user({ ctx, outline: JSON.stringify(outline), chapterNo: ch, targetWords }),
        });
        const text = (out.text || '').trim();
        if (text.length < 300) throw Object.assign(new Error('Writer returned empty chapter'), { status: 502, code: 'empty_draft' });
        await upsertChapter(novel.id, ch, text);
        await saveOutput(taskId, novel.id, ch, 'draft', text, out);
        await charge(user.id, novel.id, taskId, 'writer', task, out);
        await finishStep('draft_done', { words: text.split(/\s+/).length });
        return json(res, 200, { nextStep: 'continuity', words: text.split(/\s+/).length, task });
      }

      // ---------- 3) CONTINUITY ----------
      if (step === 'continuity') {
        const chapterText = await getChapterText(novel.id, ch);
        const agent = AGENTS.continuity_editor;
        const out = await generate({
          tier: agent.model, json: true, temperature: 0.2, maxTokens: 16000, timeoutMs: 240000,
          system: agent.system,
          user: agent.user({ ctx, chapterText, chapterNo: ch }),
        });
        await saveOutput(taskId, novel.id, ch, 'continuity', JSON.stringify(out.data), out);
        await charge(user.id, novel.id, taskId, 'continuity', task, out);
        await finishStep('continuity_done', { verdict: out.data?.verdict || 'revise' });
        return json(res, 200, { nextStep: 'edit', issues: out.data?.issues || [], verdict: out.data?.verdict, task });
      }

      // ---------- 4) LITERARY EDIT ----------
      if (step === 'edit') {
        const chapterText = await getChapterText(novel.id, ch);
        const issues = (task.result && task.result.verdict !== undefined && task.result) || {};
        const issuesData = (await lastOutput(novel.id, ch, 'continuity')) || { issues: [] };
        const agent = AGENTS.literary_editor;
        const out = await generate({
          tier: agent.model, temperature: 0.7, maxTokens: 8000, timeoutMs: 240000,
          system: agent.system,
          user: agent.user({ chapterText, issues: issuesData.issues || [], targetWords }),
        });
        const text = (out.text || '').trim();
        if (text.length > 300) await upsertChapter(novel.id, ch, text);
        await saveOutput(taskId, novel.id, ch, 'edited', text, out);
        await charge(user.id, novel.id, taskId, 'editor', task, out);
        await finishStep('edit_done', {});
        return json(res, 200, { nextStep: 'score', task });
      }

      // ---------- 5) QUALITY SCORE ----------
      if (step === 'score') {
        const chapterText = await getChapterText(novel.id, ch);
        const agent = AGENTS.quality_scorer;
        const out = await generate({
          tier: agent.model, json: true, temperature: 0.3, maxTokens: 4000, timeoutMs: 240000,
          system: agent.system, user: agent.user({ chapterText }),
        });
        await admin.from('quality_scores').insert({ novel_id: novel.id, chapter_no: ch, scores: out.data?.scores || {}, overall: out.data?.overall || 0 });
        await saveOutput(taskId, novel.id, ch, 'score', JSON.stringify(out.data), out);
        await charge(user.id, novel.id, taskId, 'scorer', task, out);
        await finishStep('score_done', { overall: out.data?.overall });
        // quality gate: below studio standard (8.0) → one genuine rewrite pass
        const overall = Number(out.data?.overall || 0);
        const needsRewrite = overall > 0 && overall < 8.0;
        return json(res, 200, { nextStep: needsRewrite ? 'rewrite' : 'memory', quality: out.data, needsRewrite, overall, task });
      }

      // ---------- 5b) QUALITY-GATE REWRITE ----------
      if (step === 'rewrite') {
        const chapterText = await getChapterText(novel.id, ch);
        const scoreData = (await lastOutput(novel.id, ch, 'score')) || {};
        const cont = (await lastOutput(novel.id, ch, 'continuity')) || { issues: [] };
        const agent = AGENTS.reviser;
        const out = await generate({
          tier: agent.model, temperature: 0.75, maxTokens: 8000, timeoutMs: 240000,
          system: agent.system,
          user: agent.user({ chapterText, scores: scoreData.scores || {}, notes: scoreData.notes || '', issues: cont.issues || [], chapterNo: ch, targetWords }),
        });
        const text = (out.text || '').trim();
        if (text.length > 300) await upsertChapter(novel.id, ch, text);
        await saveOutput(taskId, novel.id, ch, 'rewrite', text, out);
        await charge(user.id, novel.id, taskId, 'editor', task, out);
        await finishStep('rewrite_done', { rewritten: true });
        return json(res, 200, { nextStep: 'memory', rewritten: true, task });
      }

      // ---------- 6) MEMORY UPDATE (finalizes + settles credits) ----------
      if (step === 'memory') {
        const chapterText = await getChapterText(novel.id, ch);
        const agent = AGENTS.memory_updater;
        const out = await generate({
          tier: agent.model, json: true, temperature: 0.2, maxTokens: 8000, timeoutMs: 240000,
          system: agent.system, user: agent.user({ chapterNo: ch, chapterText }),
        });
        const mem = out.data || {};
        await applyMemory(novel, ch, mem);
        await saveOutput(taskId, novel.id, ch, 'memory', JSON.stringify(mem), out);
        await charge(user.id, novel.id, taskId, 'memory', task, out);

        // settle: charge actual usage of the whole pipeline, refund the rest
        const used = Math.min(task.locked_credits || ESTIMATES.chapter, Math.max(task.used_credits || 0, 1));
        await settleCredits(user.id, taskId, used, task.locked_credits || ESTIMATES.chapter);
        await admin.from('generation_tasks').update({ status: 'completed', step: 'done', used_credits: used }).eq('id', taskId);
        return json(res, 200, { done: true, creditsUsed: used, task });
      }

      return fail(res, 400, 'bad_request', `unknown step: ${step}`);
    } catch (err) {
      await admin.from('generation_tasks').update({ status: 'failed', error: String(err.message).slice(0, 500) }).eq('id', taskId);
      return fail(res, err.status || 502, err.code || 'generation_failed', `${err.message} (task ${taskId} kept for retry; credits still locked — call step:"abort" to refund)`);
    }
  });
}

// ------------------------------------------------------------------ helpers
async function getBibleData(novelId) {
  const { data } = await admin.from('story_bibles').select('data').eq('novel_id', novelId).maybeSingle();
  return data || {};
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
async function saveOutput(taskId, novelId, ch, kind, content, out) {
  await admin.from('generation_outputs').insert({ task_id: taskId, novel_id: novelId, chapter_no: ch, kind, content: content.slice(0, 60000), model: out?.model, tokens: out?.usage });
}
async function lastOutput(novelId, ch, kind) {
  const { data } = await admin.from('generation_outputs').select('content').eq('novel_id', novelId).eq('chapter_no', ch).eq('kind', kind).order('created_at', { ascending: false }).limit(1);
  if (!data?.[0]) return null;
  try { return JSON.parse(data[0].content); } catch { return data[0].content; }
}
async function charge(userId, novelId, taskId, agent, task, out) {
  task.used_credits = (task.used_credits || 0) + toCredits(out.costUsd || 0, 1);
  await recordUsage(userId, novelId, taskId, agent, out, 0);
}

// apply memory updater output to all bible tables
async function applyMemory(novel, ch, mem) {
  await admin.from('chapter_summaries').upsert({
    novel_id: novel.id, chapter_no: ch,
    summary: mem.summary || '', events: mem.events || [], state_deltas: mem.state_deltas || {},
  }, { onConflict: 'novel_id,chapter_no' });

  const { data: chars } = await admin.from('characters').select('id,name,current_state').eq('novel_id', novel.id);
  const byName = Object.fromEntries((chars || []).map((c) => [c.name.toLowerCase(), c]));
  for (const [name, deltas] of Object.entries(mem.state_deltas || {})) {
    const c = byName[name.toLowerCase()];
    if (!c) continue;
    const st = { ...(c.current_state || {}) };
    for (const [k, v] of Object.entries(deltas)) {
      if (typeof v !== 'number') continue;
      st[k] = Math.max(0, Math.min(100, (st[k] ?? 50) + v));
    }
    await admin.from('characters').update({ current_state: st, last_chapter: ch }).eq('id', c.id);
  }
  for (const name of Object.keys(mem.state_deltas || {})) {
    const c = byName[name.toLowerCase()];
    if (c && c.first_chapter == null) await admin.from('characters').update({ first_chapter: ch }).eq('id', c.id);
  }

  const { data: rels } = await admin.from('relationships').select('id,data').eq('novel_id', novel.id);
  for (const ru of mem.relationship_updates || []) {
    const r = (rels || []).find((x) =>
      (x.data?.from_name || '').toLowerCase() === (ru.from || '').toLowerCase() &&
      (x.data?.to_name || '').toLowerCase() === (ru.to || '').toLowerCase());
    if (!r) continue;
    const d = { ...r.data };
    for (const k of ['trust', 'attraction', 'conflict']) if (typeof ru[k] === 'number') d[k] = Math.max(0, Math.min(100, (d[k] ?? 0) + ru[k]));
    if (ru.status) d.status = ru.status;
    await admin.from('relationships').update({ data: d }).eq('id', r.id);
  }

  for (const e of mem.timeline || []) {
    await admin.from('timeline_events').insert({
      novel_id: novel.id, chapter_no: ch, event: e.event || '', importance: e.importance || 'normal',
    });
  }
  for (const e of mem.events || []) {
    if ((e.importance || 'normal') === 'critical') {
      await admin.from('timeline_events').insert({
        novel_id: novel.id, chapter_no: ch, event: e.event || '', importance: 'critical',
        data: { characters: e.characters || [] },
      });
    }
  }
  for (const t of mem.plot_thread_updates || []) {
    await admin.from('plot_threads').update({ status: t.status || 'advancing', current_chapter: ch })
      .eq('novel_id', novel.id).ilike('title', t.title || '');
  }
  for (const f of mem.foreshadowing_updates || []) {
    await admin.from('foreshadowing').update({ status: f.status || 'reinforced' })
      .eq('novel_id', novel.id).ilike('title', f.title || '');
  }

  // bible facts + open questions
  const { data: bibleRow } = await admin.from('story_bibles').select('data').eq('novel_id', novel.id).maybeSingle();
  const bd = { ...(bibleRow?.data || {}) };
  bd.important_facts = [...(bd.important_facts || []), ...(mem.important_facts || [])].slice(-200);
  bd.open_questions = [...(bd.open_questions || []), ...(mem.open_questions || [])].slice(-100);
  await admin.from('story_bibles').upsert({ novel_id: novel.id, data: bd });

  const count = Math.max(novel.chapter_count || 0, ch);
  const patch = { chapter_count: count };
  if (ch >= novel.length_target) patch.status = 'completed';
  await admin.from('novels').update(patch).eq('id', novel.id);
}
