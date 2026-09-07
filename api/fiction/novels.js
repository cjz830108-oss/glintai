// /api/fiction/novels — GET list · POST create (Story Architect step)
import { admin, json, fail, cors, requireUser, ownNovel } from '../_lib/db.js';
import { generate, toCredits, ESTIMATES } from '../_lib/router.js';
import { AGENTS } from '../_lib/prompts.js';
import { ensureWallet, lockCredits, settleCredits, refundTask } from '../_lib/credits.js';
import { recordUsage } from '../_lib/usage.js';

export const maxDuration = 300;

export default async function handler(req, res) {
  if (cors(req, res)) return;
  return requireUser(req, res, async (user) => {
    if (req.method === 'GET') {
      const { data, error } = await admin
        .from('novels')
        .select('id,title,genre,length_target,pov,tone,pacing,status,chapter_count,updated_at,blueprint')
        .eq('user_id', user.id)
        .is('deleted_at', null)
        .order('updated_at', { ascending: false });
      if (error) return fail(res, 500, 'db', error.message);
      return json(res, 200, {
        novels: (data || []).map((n) => ({
          id: n.id, title: n.title, genre: n.genre, status: n.status,
          chapterCount: n.chapter_count, target: n.length_target, updatedAt: n.updated_at,
          logline: n.blueprint?.logline || '',
        })),
      });
    }

    if (req.method !== 'POST') return fail(res, 405, 'method', 'Use GET or POST.');
    const { taskId, idea, genre, length, pov, tone, pacing } = req.body || {};
    if (!taskId || !idea || idea.trim().length < 10) {
      return fail(res, 400, 'bad_request', 'taskId and a story idea (10+ chars) are required.');
    }

    // idempotency: same taskId returns same result
    const { data: existing } = await admin.from('generation_tasks').select('*').eq('id', taskId).maybeSingle();
    if (existing?.status === 'completed') return json(res, 200, { novelId: existing.novel_id, blueprint: existing.result?.blueprint, cached: true });
    if (existing?.status === 'processing') return json(res, 202, { status: 'processing' });

    await ensureWallet(user.id);
    const fee = ESTIMATES.blueprint;
    await lockCredits(user.id, fee, taskId, { kind: 'blueprint' });
    await admin.from('generation_tasks').upsert({
      id: taskId, user_id: user.id, novel_id: null, kind: 'blueprint', step: 'architect',
      status: 'processing', request: { idea, genre, length, pov, tone, pacing }, locked_credits: fee,
    });

    const novelParams = { genre, length_target: Number(length) || 30, pov, tone, pacing };
    try {
      const agent = AGENTS.story_architect;
      const out = await generate({
        tier: agent.model, system: agent.system,
        user: agent.user({ novel: { ...novelParams, length_target: novelParams.length_target }, idea: idea.trim() }),
        temperature: 0.9, maxTokens: 3500, json: true, timeoutMs: 90000,
      });
      const blueprint = out.data;

      const { data: novel, error: insErr } = await admin
        .from('novels')
        .insert({
          user_id: user.id, title: blueprint.title || 'Untitled Story',
          idea: idea.trim(), blueprint,
          genre, length_target: Number(length) || 30, pov, tone, pacing, status: 'blueprint',
        })
        .select('id')
        .single();
      if (insErr) throw Object.assign(new Error(insErr.message), { status: 500, code: 'db' });

      await admin.from('story_bibles').upsert({ novel_id: novel.id, data: { premise: blueprint.premise, central_question: blueprint.central_question, world: blueprint.world || [], important_facts: [], forbidden_facts: [] } });
      await admin.from('generation_outputs').insert({ task_id: taskId, novel_id: novel.id, kind: 'blueprint', content: JSON.stringify(blueprint), model: out.model, tokens: out.usage });
      await recordUsage(user.id, novel.id, taskId, 'architect', out, 0);

      const used = Math.min(fee, toCredits(out.costUsd, 4));
      await settleCredits(user.id, taskId, used, fee);
      await admin.from('generation_tasks').update({ status: 'completed', step: 'done', novel_id: novel.id, used_credits: used, result: { blueprint } }).eq('id', taskId);

      return json(res, 200, { novelId: novel.id, blueprint });
    } catch (err) {
      await admin.from('generation_tasks').update({ status: 'failed', error: String(err.message).slice(0, 500) }).eq('id', taskId);
      await refundTask(user.id, taskId, fee).catch(() => {});
      return fail(res, err.status || 502, err.code || 'generation_failed', err.message);
    }
  });
}
