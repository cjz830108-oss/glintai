// GET /api/fiction/config — public runtime config for Studio pages
import { cors, json } from '../_lib/db.js';

export const maxDuration = 10;

export default async function handler(req, res) {
  if (cors(req, res)) return;
  const url = process.env.SUPABASE_URL;
  const anon = process.env.SUPABASE_ANON_KEY;
  if (!url || !anon) {
    return json(res, 503, { error: { code: 'not_configured', message: 'Studio is not configured yet (missing SUPABASE_URL / SUPABASE_ANON_KEY).' } });
  }
  json(res, 200, { supabaseUrl: url, supabaseAnonKey: anon });
}
