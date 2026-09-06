// /api/fiction/chapter — GET read · PATCH save (author edits) · POST AI action (continue/rewrite/improve...)
import { admin, json, fail, cors, requireUser, ownNovel } from '../_lib/db.js';
import { generate, toCredits, ESTIMATES } from '../_lib/router.js';
import { AGENTS } from '../_lib/prompts.js';
import { buildChapterContext, contextToPrompt } from '../_lib/retrieval.js';
import { lockCredits, settleCredits, refundTask } from '../_lib/credits.js';
import { recordUsage } from '../_lib/usage.js';

export const maxDuration = 60;

const ACTIONS = {
  continue:        'Continue writing seamlessly from where the text stops, for about 600 words. Match voice, tense and POV exactly.',
  improve:         'Improve the prose: stronger verbs, sharper rhythm, deeper emotion — keep every event and fact identical.',
  more_emotional:  'Rewrite to heighten emotional intensity and interiority while keeping all events identical.',
  improve_dialogue:'Rewrite the dialogue to be more natural, subtextual and character-specific. Keep meaning and plot identical.',
  shorten:         'Tighten the text to about 70% of its length. Cut filler, keep every plot beat.',
  expand:          'Expand the text by about 40% with richer scene detail, sensory grounding and dialogue. Keep plot identical.',
};

export default async function handler(req, res) {
  if (cors(req, res)) return;
  return requireUser(req, res, async (user) => {
    const novelId = (req.query.novel || req.body?.novelId || '').toString();

    // ---------- GET: read one chapter ----------
    if (req.method === 'GET') {
      if (!novelId) return fail(res, 400, 'bad_request', 'novel required');
      await ownNovel(novelId, user.id);
      const no = Number(req.query.no);
      if (!no) return fail(res, 400, 'bad_request', 'chapter no required');
      const { data } = await admin.from('chapters').select('*').eq('novel_id', novelId).eq('chapter_no', no).maybeSingle();
      return json(res, 200, { chapter: data || null });
    }

    // ---------- PATCH: author save ----------
    if (req.method === 'PATCH') {
      const { novelId: nid, chapterNo, content, title, status } = req.body || {};
      if (!nid || !chapterNo) return fail(res, 400, 'bad_request', 'novelId, chapterNo required');
      const novel = await ownNovel(nid, user.id);
      const words = (content || '').split(/\s+/).filter(Boolean).length;
      const patch = { word_count: words };
      if (content != null) patch.content = content;
      if (title != null) patch.title = title;
      if (status) patch.status = status;
      const { error } = await admin.from('chapters').update(patch).eq('novel_id', novel.id).eq('chapter_no', Number(chapterNo));
      if (error) return fail(res, 500, 'db', error.message);
      return json(res, 200, { ok: true, wordCount: words });
    }

    // ---------- POST: AI action ----------
    if (req.method === 'POST') {
      const { taskId, novelId: nid, chapterNo, action, selection, note, pov } = req.body || {};
      if (!taskId || !nid || !action) return fail(res, 400, 'bad_request', 'taskId, novelId, action required');
      const novel = await ownNovel(nid, user.id);

      let instruction = ACTIONS[action];
      if (!instruction && action === 'change_pov') {
        if (!pov) return fail(res, 400, 'bad_request', 'pov required for change_pov');
        instruction = `Rewrite the text in ${pov.replace('_', ' ')} point of view. Keep all events identical.`;
      }
      if (!instruction) return fail(res, 400, 'bad_request', `unknown action: ${action}`);
      if (note) instruction += ` Author note: ${note}`;

      // idempotency
      const { data: existing } = await admin.from('generation_tasks').select('*').eq('id', taskId).maybeSingle();
      if (existing?.status === 'completed') return json(res, 200, { content: existing.result?.content, replacement: existing.result?.replacement, cached: true });

      const fee = ESTIMATES.action;
      await lockCredits(user.id, fee, taskId, { kind: 'action', action, novel: novel.id, chapter: chapterNo });
      await admin.from('generation_tasks').upsert({
        id: taskId, user_id: user.id, novel_id: novel.id, kind: 'action', step: 'running',
        status: 'processing', request: { action, chapterNo }, locked_credits: fee,
      });

      try {
        const ch = Number(chapterNo || 0);
        const ctxObj = await buildChapterContext(novel, ch || 1);
        const ctx = contextToPrompt(ctxObj);
        const agent = AGENTS.action;
        const text = selection || (ch ? await getChapterText(novel.id, ch) : '');
        if (!text) return fail(res, 400, 'bad_request', 'chapter not found and no selection given');

        const out = await generate({
          tier: agent.model, temperature: action === 'continue' ? 0.9 : 0.7,
          maxTokens: action === 'expand' ? 3600 : 2800, timeoutMs: 150000,
          system: agent.system, user: agent.user({ instruction, text, ctx }),
        });
        const result = (out.text || '').trim();
        if (!result) throw Object.assign(new Error('Model returned empty output'), { status: 502, code: 'empty' });

        // continue → append to the chapter
        if (action === 'continue' && ch) {
          const { data: cur } = await admin.from('chapters').select('content,word_count').eq('novel_id', novel.id).eq('chapter_no', ch).maybeSingle();
          const merged = `${cur?.content || ''}\n\n${result}`;
          const words = merged.split(/\s+/).filter(Boolean).length;
          await admin.from('chapters').update({ content: merged, word_count: words }).eq('novel_id', novel.id).eq('chapter_no', ch);
        }

        await recordUsage(user.id, novel.id, taskId, 'writer', out, 0);
        const used = Math.min(fee, toCredits(out.costUsd, 2));
        await settleCredits(user.id, taskId, used, fee);
        await admin.from('generation_tasks').update({
          status: 'completed', step: 'done', used_credits: used,
          result: action === 'continue' ? {} : { content: result, replacement: action.startsWith('rewrite') || selection ? result : undefined },
        }).eq('id', taskId);

        return json(res, 200, {
          content: action === 'continue' ? undefined : result,
          replacement: selection ? result : undefined,
          creditsUsed: used,
        });
      } catch (err) {
        await admin.from('generation_tasks').update({ status: 'failed', error: String(err.message).slice(0, 500) }).eq('id', taskId);
        await refundTask(user.id, taskId, fee).catch(() => {});
        return fail(res, err.status || 502, err.code || 'generation_failed', err.message);
      }
    }

    return fail(res, 405, 'method', 'Use GET, PATCH or POST.');
  });
}

async function getChapterText(novelId, ch) {
  const { data } = await admin.from('chapters').select('content').eq('novel_id', novelId).eq('chapter_no', ch).maybeSingle();
  if (!data?.content) throw Object.assign(new Error('Chapter not found'), { status: 404, code: 'not_found' });
  return data.content;
}
