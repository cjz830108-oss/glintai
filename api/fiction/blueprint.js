// /api/fiction/blueprint — POST actions on a novel's blueprint
// action: 'approve' (save edits + go to writing) | 'regenerate' (re-run architect) | 'expand' (characters + full outline)
import { admin, json, fail, cors, requireUser, ownNovel } from '../_lib/db.js';
import { generate, toCredits, ESTIMATES } from '../_lib/router.js';
import { AGENTS } from '../_lib/prompts.js';
import { lockCredits, settleCredits, refundTask } from '../_lib/credits.js';
import { recordUsage } from '../_lib/usage.js';

export const maxDuration = 300;

export default async function handler(req, res) {
  if (cors(req, res)) return;
  if (req.method !== 'POST') return fail(res, 405, 'method', 'Use POST.');
  return requireUser(req, res, async (user) => {
    const { taskId, novelId, action, blueprint } = req.body || {};
    if (!taskId || !novelId || !action) return fail(res, 400, 'bad_request', 'taskId, novelId, action required');
    const novel = await ownNovel(novelId, user.id);

    if (action === 'approve') {
      const patch = { status: 'writing' };
      if (blueprint) patch.blueprint = blueprint;
      const { error } = await admin.from('novels').update(patch).eq('id', novel.id);
      if (error) return fail(res, 500, 'db', error.message);
      if (blueprint) {
        await admin.from('story_bibles').update({
          data: { premise: blueprint.premise, central_question: blueprint.central_question, world: blueprint.world || [], important_facts: [], forbidden_facts: [] },
        }).eq('novel_id', novel.id);
      }
      return json(res, 200, { ok: true, status: 'writing' });
    }

    if (action === 'regenerate') {
      const fee = ESTIMATES.blueprint;
      await lockCredits(user.id, fee, taskId, { kind: 'blueprint_regen', novel: novel.id });
      try {
        const agent = AGENTS.story_architect;
        const out = await generate({
          tier: agent.model, system: agent.system,
          user: agent.user({ novel, idea: novel.idea }), temperature: 1.0, maxTokens: 3500, json: true, timeoutMs: 90000,
        });
        const bp = out.data;
        await admin.from('novels').update({ title: bp.title || novel.title, blueprint: bp }).eq('id', novel.id);
        await admin.from('story_bibles').update({ data: { premise: bp.premise, central_question: bp.central_question, world: bp.world || [], important_facts: [], forbidden_facts: [] } }).eq('novel_id', novel.id);
        await recordUsage(user.id, novel.id, taskId, 'architect', out, 0);
        const used = Math.min(fee, toCredits(out.costUsd, 4));
        await settleCredits(user.id, taskId, used, fee);
        return json(res, 200, { blueprint: bp, creditsUsed: used });
      } catch (err) {
        await refundTask(user.id, taskId, fee).catch(() => {});
        return fail(res, err.status || 502, err.code || 'generation_failed', err.message);
      }
    }

    if (action === 'expand') {
      const fee = ESTIMATES.expand;
      await lockCredits(user.id, fee, taskId, { kind: 'expand', novel: novel.id });
      try {
        const bp = novel.blueprint || {};
        // 1) Character Director (retry once; large casts can hit output caps)
        const charAgent = AGENTS.character_director;
        let cast = null, castOut = null;
        for (let attempt = 0; attempt < 2 && !cast; attempt++) {
          try {
            castOut = await generate({
              tier: charAgent.model, system: charAgent.system,
              user: charAgent.user({ blueprint: bp, novel }), temperature: 0.85, maxTokens: 8000, json: true, timeoutMs: 90000,
            });
            cast = castOut.data;
          } catch (e) {
            if (attempt === 1) throw e;
          }
        }

        // persist cast
        const nameToId = {};
        for (const c of cast.characters || []) {
          const { data: row } = await admin.from('characters')
            .insert({ novel_id: novel.id, name: c.name, data: c, current_state: c.current_state || {} })
            .select('id').single();
          nameToId[c.name] = row.id;
        }
        for (const r of cast.relationships || []) {
          if (!nameToId[r.from] || !nameToId[r.to]) continue;
          await admin.from('relationships').insert({
            novel_id: novel.id, from_character_id: nameToId[r.from], to_character_id: nameToId[r.to],
            data: { ...r, from_name: r.from, to_name: r.to },
          });
        }
        for (const w of bp.world || []) {
          await admin.from('world_entities').insert({ novel_id: novel.id, name: w.name, type: w.type || 'location', description: w.description || '' });
        }
        for (const t of bp.plot_threads || []) {
          await admin.from('plot_threads').insert({
            novel_id: novel.id, title: t.title, kind: t.kind || 'subplot', status: 'open',
            data: { plan: t.plan, open_questions: [] },
          });
        }
        for (const f of bp.foreshadowing || []) {
          await admin.from('foreshadowing').insert({
            novel_id: novel.id, title: f.title, description: f.description || '',
            introduced_chapter: f.introduced_chapter || null, planned_reveal_chapter: f.planned_reveal_chapter || null,
            importance: f.importance || 'normal', status: 'planted',
          });
        }

        // 2) Plot Planner — chapter outline in chunks (avoids JSON truncation on long books)
        const planAgent = AGENTS.plot_planner;
        const CHUNK = 12;
        let chapterPlan = [];
        let planCostUsd = 0;
        for (let start = 1; start <= novel.length_target; start += CHUNK) {
          const end = Math.min(start + CHUNK - 1, novel.length_target);
          let chunk = null;
          for (let attempt = 0; attempt < 2 && !chunk; attempt++) {
            try {
              const planOut = await generate({
                tier: planAgent.model, system: planAgent.system,
                user: planAgent.user({ blueprint: bp, novel, characters: cast.characters || [], range: [start, end], prev: chapterPlan.slice(-3) }),
                temperature: 0.8, maxTokens: 4000, json: true, timeoutMs: 240000,
              });
              chunk = planOut; planCostUsd = (planCostUsd || 0) + (planOut.costUsd || 0);
              await recordUsage(user.id, novel.id, taskId, 'planner', planOut, 0);
            } catch (e) {
              if (attempt === 1) throw e;
            }
          }
          chapterPlan = chapterPlan.concat((chunk?.data?.chapters || []).map((c, i) => ({ ...c, no: start + i })));
        }

        // store chapter plan in the bible
        const { data: bibleRow } = await admin.from('story_bibles').select('data').eq('novel_id', novel.id).maybeSingle();
        const bibleData = { ...(bibleRow?.data || {}), chapter_plan: chapterPlan };
        await admin.from('story_bibles').upsert({ novel_id: novel.id, data: bibleData });

        await recordUsage(user.id, novel.id, taskId, 'character', castOut, 0);
        const used = Math.min(fee, toCredits(castOut.costUsd + planCostUsd, 8));
        await settleCredits(user.id, taskId, used, fee);
        return json(res, 200, {
          chapterPlan, cast: (cast.characters || []).map((c) => c.name),
          creditsUsed: used,
        });
      } catch (err) {
        await refundTask(user.id, taskId, fee).catch(() => {});
        return fail(res, err.status || 502, err.code || 'generation_failed', err.message);
      }
    }

    return fail(res, 400, 'bad_request', `unknown action: ${action}`);
  });
}
