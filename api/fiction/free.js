// /api/fiction/free — Free AI Story Generator (no signup)
// Fair use: 3 generations per IP per day (in-memory; resets on cold start — acceptable for V1).
// Generates a story opening + hook, then CTA into the studio.
import { cors, json, fail } from '../_lib/db.js';
import { generate } from '../_lib/router.js';

export const maxDuration = 60;

const LIMIT_PER_DAY = 3;
const hits = new Map(); // ip -> {date, count}

function rateLimited(ip) {
  const today = new Date().toISOString().slice(0, 10);
  const rec = hits.get(ip);
  if (!rec || rec.date !== today) {
    hits.set(ip, { date: today, count: 0 });
    return false;
  }
  if (rec.count >= LIMIT_PER_DAY) return true;
  return false;
}
function countHit(ip) {
  const rec = hits.get(ip);
  if (rec) rec.count += 1;
  // opportunistic cleanup
  if (hits.size > 5000) {
    const today = new Date().toISOString().slice(0, 10);
    for (const [k, v] of hits) if (v.date !== today) hits.delete(k);
  }
}

export default async function handler(req, res) {
  if (cors(req, res)) return;
  if (req.method !== 'POST') return fail(res, 405, 'method', 'Use POST.');
  const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';

  if (rateLimited(ip)) {
    return fail(res, 429, 'daily_limit', "You've used all 3 free generations today. Create a free account for 100 credits — keep everything you make.", { retryAfter: 'tomorrow' });
  }

  const { idea, genre = 'romance' } = req.body || {};
  if (!idea || idea.trim().length < 10) return fail(res, 400, 'bad_request', 'Give us a story idea (at least one sentence).');
  if (idea.length > 600) return fail(res, 400, 'bad_request', 'Keep the idea under 600 characters.');

  try {
    const out = await generate({
      tier: 'creative', temperature: 0.9, maxTokens: 4000, timeoutMs: 240000,
      system: `You are a fiction opening writer. You write gripping novel openings (250-350 words) that end on a hook. Genre-level craft only, no author imitation. Output ONLY the story text: first line "Chapter 1 — <title>", then the prose.`,
      user: `Story idea: ${idea.trim()}\nGenre: ${genre}\n\nWrite the opening of Chapter 1 (250-350 words) and end on a cliffhanger hook.`,
    });
    countHit(ip);
    json(res, 200, { story: (out.text || '').trim(), remaining: LIMIT_PER_DAY - 1 });
  } catch (err) {
    return fail(res, 502, 'generation_failed', err.message);
  }
}
