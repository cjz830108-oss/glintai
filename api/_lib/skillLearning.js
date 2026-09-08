// Glint Fiction — Skill Learning (V1: aggregate feedback + quality data into lessons)
// Reads quality_scores + generation_feedback for a genre, derives per-axis averages,
// turns the weakest signals into concrete writing lessons, and feeds them back into
// the writer context. Aggregates are cached (10 min TTL). Also bookkeeps skill_metrics.

import { admin } from './db.js';

const cache = new Map(); // genre -> { at, value }
const TTL = 10 * 60 * 1000;

const AXIS_ADVICE = {
  plot: 'tighten cause-and-effect: every scene must change the situation',
  character: 'show motivation through action and choice, not statement',
  emotion: 'ground feelings in the body and behavior; cut named emotions',
  dialogue: 'push subtext: characters ask, deflect and withhold instead of declaring',
  pacing: 'vary scene rhythm and cut throat-clearing transitions',
  continuity: 're-check who knows what and object/injury tracking before drafting',
  originality: 'replace the first easy image with a specific, unexpected detail',
  ai_likeness: 'break patterned sentence rhythm; cut AI-tell phrasing hard',
  reader_engagement: 'end scenes on unresolved tension; raise questions earlier',
};

export async function computeLessons(genre) {
  const hit = cache.get(genre);
  if (hit && Date.now() - hit.at < TTL) return hit.value;
  const value = await _compute(genre).catch(() => ({ lessons: [], metrics: { samples: 0 } }));
  cache.set(genre, { at: Date.now(), value });
  return value;
}

async function _compute(genre) {
  const { data: novels } = await admin.from('novels').select('id').eq('genre', genre).limit(60);
  const ids = (novels || []).map((n) => n.id);
  if (!ids.length) return { lessons: [], metrics: { samples: 0 } };

  const [scores, feedback] = await Promise.all([
    admin.from('quality_scores').select('scores,overall')
      .in('novel_id', ids).order('created_at', { ascending: false }).limit(80),
    admin.from('generation_feedback').select('rating,note')
      .in('novel_id', ids).order('created_at', { ascending: false }).limit(120),
  ]);
  const rows = scores.data || [];
  const fb = feedback.data || [];

  const axisSums = {};
  let overallSum = 0, belowGate = 0;
  for (const r of rows) {
    const o = Number(r.overall) || 0;
    overallSum += o;
    if (o > 0 && o < 8) belowGate++;
    for (const [k, v] of Object.entries(r.scores || {})) {
      axisSums[k] = axisSums[k] || { sum: 0, n: 0 };
      axisSums[k].sum += Number(v) || 0;
      axisSums[k].n++;
    }
  }
  const axisAvg = Object.fromEntries(
    Object.entries(axisSums).map(([k, { sum, n }]) => [k, sum / n])
  );
  const overall = rows.length ? overallSum / rows.length : 0;
  const ranked = Object.entries(axisAvg).sort((a, b) => a[1] - b[1]);

  const good = fb.filter((f) => f.rating === 'good').length;
  const bad = fb.filter((f) => f.rating === 'needs_improvement').length;
  const acceptance = fb.length ? good / fb.length : null;

  const lessons = [];
  for (const [axis, avg] of ranked.slice(0, 2)) {
    if (avg < 8) lessons.push(`Axis "${axis}" averages ${avg.toFixed(1)}/10 across recent chapters — ${AXIS_ADVICE[axis] || 'review recent chapters for weak spots'}.`);
  }
  if (rows.length >= 5 && overall < 8) {
    lessons.unshift(`Overall chapter quality averages ${overall.toFixed(1)}/10 over ${rows.length} scored chapters — raise the floor before taking risks.`);
  }
  if (bad >= 2 && acceptance !== null && acceptance < 0.7) {
    lessons.push(`Readers gave ${bad} needs-improvement vs ${good} good (${Math.round(acceptance * 100)}% acceptance) — favor safer, higher-impact beats.`);
  }
  if (ranked.length >= 3 && ranked[ranked.length - 1][1] >= 8) {
    const [axis, avg] = ranked[ranked.length - 1];
    lessons.push(`Axis "${axis}" is the strongest (${avg.toFixed(1)}/10) — keep doing what produces it.`);
  }
  const note = fb.find((f) => f.rating === 'needs_improvement' && f.note)?.note;
  if (note) lessons.push(`Author feedback to honor: "${String(note).slice(0, 140)}"`);

  return {
    lessons: lessons.slice(0, 5),
    metrics: {
      samples: rows.length,
      overall: Number(overall.toFixed(2)),
      rewrite_rate: rows.length ? Number((belowGate / rows.length).toFixed(2)) : 0,
      feedback: fb.length,
      acceptance: acceptance === null ? null : Number(acceptance.toFixed(2)),
    },
  };
}

/** Weekly skill_metrics bookkeeping — called from the memory step of each chapter. */
export async function recordSignal(genre, { overall } = {}) {
  try {
    const windowStart = new Date();
    windowStart.setUTCDate(windowStart.getUTCDate() - windowStart.getUTCDay() + 1); // Monday
    const ws = windowStart.toISOString().slice(0, 10);
    const { metrics } = await computeLessons(genre);
    await admin.from('skill_metrics').upsert({
      skill_key: `genre:${genre}`, skill_version: 1, window_start: ws,
      acceptance_rate: metrics.acceptance ?? 0,
      rewrite_rate: metrics.rewrite_rate ?? 0,
      regeneration_rate: 0,
      avg_quality: metrics.overall ?? 0,
      samples: metrics.samples ?? 0,
    }, { onConflict: 'skill_key,skill_version,window_start' });
  } catch { /* metrics bookkeeping must never break the pipeline */ }
}
