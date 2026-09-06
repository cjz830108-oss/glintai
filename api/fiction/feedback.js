// /api/fiction/feedback — POST user feedback (feeds the future Skill Learning layer)
import { admin, json, fail, cors, requireUser, ownNovel } from '../_lib/db.js';

export const maxDuration = 10;

export default async function handler(req, res) {
  if (cors(req, res)) return;
  if (req.method !== 'POST') return fail(res, 405, 'method', 'Use POST.');
  return requireUser(req, res, async (user) => {
    const { novelId, chapterNo, rating, categories, note } = req.body || {};
    if (!novelId || !rating) return fail(res, 400, 'bad_request', 'novelId, rating required');
    await ownNovel(novelId, user.id);
    const { error } = await admin.from('generation_feedback').insert({
      user_id: user.id, novel_id: novelId, chapter_no: chapterNo || null,
      rating, categories: categories || [], note: note || null,
    });
    if (error) return fail(res, 500, 'db', error.message);
    json(res, 200, { ok: true });
  });
}
