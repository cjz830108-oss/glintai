// /api/fiction/import — "Continue My Novel": upload a TXT, rebuild the Story Bible, keep writing.
// Pipeline: client sends parsed chapters → we sample + extract memory with light LLM calls →
// novel created with status 'writing', bible populated → user continues from chapter N+1.
import { admin, json, fail, cors, requireUser } from '../_lib/db.js';
import { generate, toCredits, ESTIMATES } from '../_lib/router.js';
import { getAgent } from '../_lib/prompts.js';
import { lockCredits, settleCredits, refundTask } from '../_lib/credits.js';
import { recordUsage } from '../_lib/usage.js';

export const maxDuration = 300;

export default async function handler(req, res) {
  if (cors(req, res)) return;
  if (req.method !== 'POST') return fail(res, 405, 'method', 'Use POST.');
  return requireUser(req, res, async (user) => {
    const { taskId, title, genre, chapters } = req.body || {};
    if (!taskId || !Array.isArray(chapters) || chapters.length < 2) {
      return fail(res, 400, 'bad_request', 'taskId and at least 2 chapters required');
    }
    const fee = ESTIMATES.chapter; // extraction ≈ one chapter pipeline of calls
    await lockCredits(user.id, fee, taskId, { kind: 'import', chapters: chapters.length });

    try {
      // 1) create the novel shell
      const { data: novel, error: insErr } = await admin
        .from('novels')
        .insert({
          user_id: user.id,
          title: (title || 'Imported Novel').slice(0, 160),
          genre: genre || 'romance', length_target: Math.max(chapters.length, 2),
          pov: 'third_limited', tone: 'emotional', pacing: 'balanced',
          idea: `Imported novel with ${chapters.length} existing chapters.`,
          status: 'writing', chapter_count: chapters.length,
        })
        .select('id').single();
      if (insErr) throw Object.assign(new Error(insErr.message), { status: 500, code: 'db' });

      // 2) store full chapters as-is (author's canon)
      for (const c of chapters) {
        const text = String(c.content || '').slice(0, 120000);
        if (!text.trim()) continue;
        await admin.from('chapters').upsert(
          { novel_id: novel.id, chapter_no: Number(c.no) || 0, title: String(c.title || '').slice(0, 140), content: text, word_count: text.split(/\s+/).filter(Boolean).length, status: 'final' },
          { onConflict: 'novel_id,chapter_no' }
        );
      }

      // 3) sample chapters for memory extraction: first 2 + last 2 (+ middle if long)
      const nos = chapters.map((c) => Number(c.no) || 0).sort((a, b) => a - b);
      const sampleNos = [...new Set([...nos.slice(0, 2), ...(nos.length > 6 ? [nos[Math.floor(nos.length / 2)]] : []), ...nos.slice(-2)])];
      const byNo = Object.fromEntries(chapters.map((c) => [Number(c.no) || 0, c]));

      let analysis = {};
      let cost = 0;
      const excerpt = sampleNos.map((n) => {
        const t = String(byNo[n]?.content || '');
        return `--- CHAPTER ${n} (${String(byNo[n]?.title || '')}) ---\n${t.slice(0, 6000)}${t.length > 6000 ? '\n[...truncated...]' : ''}`;
      }).join('\n\n');

      const out = await generate({
        tier: 'deep', json: true, temperature: 0.3, maxTokens: 8000, timeoutMs: 240000,
        system: `You reverse-engineer a Story Bible from existing novel chapters. You are precise and only record what the text supports. Output ONLY valid JSON.`,
        user: `Rebuild the story memory for this ongoing novel (sampled chapters shown):
${excerpt}

Return JSON exactly like:
{"premise":"","central_question":"","main_conflict":"","style_guide":{"pov":"","tone":"","notes":""},
 "characters":[{"name":"","role":"","essence":"","speech_style":"","arc":"","secrets":["only if revealed in text"],"current_state":{"trust":50,"love":0,"anger":0,"fear":0,"suspicion":0,"confidence":50,"jealousy":0}}],
 "relationships":[{"from":"","to":"","type":"","status":"","trust":50,"attraction":0,"conflict":0}],
 "world":[{"name":"","type":"","description":""}],
 "plot_threads":[{"title":"","kind":"","status":"open","open_questions":[""]}],
 "foreshadowing":[{"title":"","description":"","introduced_chapter":N,"planned_reveal_chapter":null,"importance":"normal|major"}],
 "important_facts":["durable canon facts"],"open_questions":["what the story still owes"],"timeline":[{"chapter":N,"event":"","importance":"normal|critical"}]}`,
      });
      analysis = out.data || {};
      cost += out.costUsd || 0;
      await recordUsage(user.id, novel.id, taskId, 'architect', out, 0);

      // 4) populate the bible tables
      const nameToId = {};
      for (const c of analysis.characters || []) {
        const { data: row } = await admin.from('characters')
          .insert({ novel_id: novel.id, name: c.name, data: c, current_state: c.current_state || {} })
          .select('id').single();
        nameToId[c.name] = row.id;
      }
      for (const r of analysis.relationships || []) {
        if (!nameToId[r.from] || !nameToId[r.to]) continue;
        await admin.from('relationships').insert({
          novel_id: novel.id, from_character_id: nameToId[r.from], to_character_id: nameToId[r.to],
          data: { ...r, from_name: r.from, to_name: r.to },
        });
      }
      for (const w of analysis.world || []) {
        await admin.from('world_entities').insert({ novel_id: novel.id, name: w.name, type: w.type || 'location', description: w.description || '' });
      }
      for (const t of analysis.plot_threads || []) {
        await admin.from('plot_threads').insert({ novel_id: novel.id, title: t.title, kind: t.kind || 'subplot', status: t.status || 'open', data: { open_questions: t.open_questions || [] } });
      }
      for (const f of analysis.foreshadowing || []) {
        await admin.from('foreshadowing').insert({
          novel_id: novel.id, title: f.title, description: f.description || '',
          introduced_chapter: f.introduced_chapter ?? null, planned_reveal_chapter: f.planned_reveal_chapter ?? null,
          importance: f.importance || 'normal', status: 'planted',
        });
      }
      for (const e of analysis.timeline || []) {
        await admin.from('timeline_events').insert({ novel_id: novel.id, chapter_no: e.chapter ?? null, event: e.event || '', importance: e.importance || 'normal' });
      }

      // 5) summaries for the sampled chapters (writer context for "continue")
      const sumAgent = await getAgent('memory_updater');
      for (const n of sampleNos) {
        const text = String(byNo[n]?.content || '').slice(0, 9000);
        if (!text.trim()) continue;
        try {
          const s = await generate({
            tier: 'light', json: true, temperature: 0.2, maxTokens: 4000, timeoutMs: 240000,
            system: sumAgent.system,
            user: sumAgent.user({ chapterNo: n, chapterText: text }),
          });
          cost += s.costUsd || 0;
          await recordUsage(user.id, novel.id, taskId, 'memory', s, 0);
          await admin.from('chapter_summaries').upsert({
            novel_id: novel.id, chapter_no: n, summary: s.data?.summary || '', events: s.data?.events || [],
            state_deltas: s.data?.state_deltas || {},
          }, { onConflict: 'novel_id,chapter_no' });
        } catch { /* summarization is best-effort */ }
      }

      await admin.from('story_bibles').upsert({
        novel_id: novel.id,
        data: {
          premise: analysis.premise || '', central_question: analysis.central_question || '',
          main_conflict: analysis.main_conflict || '', style_guide: analysis.style_guide || {},
          important_facts: analysis.important_facts || [], forbidden_facts: [],
          open_questions: analysis.open_questions || [],
          imported: true, imported_chapters: chapters.length, summarized_chapters: sampleNos,
        },
      });

      const used = Math.min(fee, Math.max(toCredits(cost, 6), 6));
      await settleCredits(user.id, taskId, used, fee);
      await admin.from('generation_tasks').update({ status: 'completed', step: 'done', novel_id: novel.id, used_credits: used, result: { imported: chapters.length } }).eq('id', taskId);

      return json(res, 200, {
        novelId: novel.id, chaptersImported: chapters.length,
        characters: (analysis.characters || []).map((c) => c.name),
        memoryNote: `Sampled & summarized chapters: ${sampleNos.join(', ')}. The writer uses these plus the bible to continue.`,
        creditsUsed: used,
      });
    } catch (err) {
      await refundTask(user.id, taskId, fee).catch(() => {});
      await admin.from('generation_tasks').update({ status: 'failed', error: String(err.message).slice(0, 400) }).eq('id', taskId);
      return fail(res, err.status || 502, err.code || 'import_failed', err.message);
    }
  });
}
