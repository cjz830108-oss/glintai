// Glint Fiction — shared server helpers (Vercel serverless, ESM)
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_ROLE = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SERVICE_ROLE) {
  console.error('Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env vars');
}

export const admin = createClient(SUPABASE_URL || 'http://localhost', SERVICE_ROLE || 'public-anon', {
  auth: { persistSession: false, autoRefreshToken: false },
});

export function json(res, status, data) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.status(status).json(data);
}

export function fail(res, status, code, message, extra = {}) {
  json(res, status, { error: { code, message, ...extra } });
}

export function cors(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return true;
  }
  return false;
}

/** Verify the caller's Supabase JWT and return { user } or null. */
export async function getUser(req) {
  const auth = req.headers.authorization || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : null;
  if (!token) return null;
  const { data, error } = await admin.auth.getUser(token);
  if (error || !data?.user) return null;
  return data.user;
}

/** Wrap a handler with auth + ownership checks. */
export async function requireUser(req, res, fn) {
  const user = await getUser(req);
  if (!user) return fail(res, 401, 'unauthorized', 'Sign in required.');
  try {
    return await fn(user);
  } catch (err) {
    console.error('[fiction]', err);
    return fail(res, err.status || 500, err.code || 'internal', err.message || 'Internal error');
  }
}

/** Ensure the novel exists, belongs to user, and is not deleted. Returns row. */
export async function ownNovel(novelId, userId) {
  const { data, error } = await admin
    .from('novels')
    .select('*')
    .eq('id', novelId)
    .eq('user_id', userId)
    .is('deleted_at', null)
    .maybeSingle();
  if (error) throw Object.assign(new Error(error.message), { status: 500, code: 'db' });
  if (!data) throw Object.assign(new Error('Novel not found.'), { status: 404, code: 'not_found' });
  return data;
}
