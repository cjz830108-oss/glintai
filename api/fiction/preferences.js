// /api/fiction/preferences — GET / PATCH the author's writing preferences (User Memory)
// Stored in user_preferences.data; fed into the writer context for every chapter.
import { admin, json, fail, cors, requireUser } from '../_lib/db.js';

export const maxDuration = 15;

export default async function handler(req, res) {
  if (cors(req, res)) return;
  return requireUser(req, res, async (user) => {
    if (req.method === 'GET') {
      const { data } = await admin.from('user_preferences').select('data,updated_at').eq('user_id', user.id).maybeSingle();
      return json(res, 200, { preferences: data?.data || {}, updatedAt: data?.updated_at || null });
    }

    if (req.method === 'PATCH') {
      const incoming = req.body || {};
      if (typeof incoming !== 'object' || Array.isArray(incoming)) return fail(res, 400, 'bad_request', 'body must be an object');
      // whitelisted keys only, string values, hard size cap
      const ALLOWED = ['favorite_genres', 'pov', 'tone', 'pacing', 'tropes_to_avoid', 'content_notes', 'ending_preference', 'extra_style'];
      const clean = {};
      for (const k of ALLOWED) if (typeof incoming[k] === 'string') clean[k] = incoming[k].slice(0, 600);
      const { error } = await admin.from('user_preferences').upsert({ user_id: user.id, data: clean });
      if (error) return fail(res, 500, 'db', error.message);
      return json(res, 200, { ok: true, preferences: clean });
    }

    return fail(res, 405, 'method', 'Use GET or PATCH.');
  });
}
