// Glint Fiction — Memory Retrieval (V1: structured SQL retrieval, no pgvector)
// Assembles the Writer Context for one chapter: relevant characters, states,
// relationships, plot threads, active foreshadowing, recent summaries,
// critical timeline events, style + genre rules. Never dumps the whole bible.

import { admin } from './db.js';
import { GENRE_SKILLS, ANTI_AI_RULES } from './skills.js';
import { computeLessons } from './skillLearning.js';

export async function buildChapterContext(novel, chapterNo) {
  const novelId = novel.id;

  const [characters, relationships, threads, shadows, summaries, events, bibleRow, prefsRow] = await Promise.all([
    admin.from('characters').select('*').eq('novel_id', novelId).eq('active', true).order('created_at').limit(14),
    admin.from('relationships').select('*').eq('novel_id', novelId).limit(30),
    admin.from('plot_threads').select('*').eq('novel_id', novelId).in('status', ['open', 'advancing']).limit(12),
    admin.from('foreshadowing').select('*').eq('novel_id', novelId).in('status', ['planted', 'reinforced']).limit(14),
    admin.from('chapter_summaries').select('chapter_no,summary,events')
      .eq('novel_id', novelId).lt('chapter_no', chapterNo).order('chapter_no', { ascending: false }).limit(3),
    admin.from('timeline_events').select('*').eq('novel_id', novelId).eq('importance', 'critical').limit(24),
    admin.from('story_bibles').select('data').eq('novel_id', novelId).maybeSingle(),
    admin.from('user_preferences').select('data').eq('user_id', novel.user_id).maybeSingle(),
  ]);

  const bible = bibleRow?.data || {};
  const skill = GENRE_SKILLS[novel.genre] || GENRE_SKILLS.romance;
  const learned = await computeLessons(novel.genre);

  return {
    novel: {
      title: novel.title, genre: novel.genre, pov: novel.pov, tone: novel.tone,
      pacing: novel.pacing, target_chapters: novel.length_target, idea: novel.idea,
    },
    world: bible.world || [],
    style_guide: bible.style_guide || {},
    important_facts: (bible.important_facts || []).slice(-30),
    forbidden_facts: bible.forbidden_facts || [],
    premise: bible.premise || '',
    central_question: bible.central_question || '',
    characters: (characters.data || []).map((c) => ({
      id: c.id, name: c.name, role: c.data?.role || '',
      essence: c.data?.essence || '',
      speech_style: c.data?.speech_style || '',
      arc: c.data?.character_arc || '',
      secrets: (c.data?.secrets || []).slice(0, 4),
      current_state: c.current_state || {},
      first_chapter: c.first_chapter,
    })),
    relationships: (relationships.data || []).map((r) => ({
      from: r.data?.from_name, to: r.data?.to_name,
      type: r.data?.type, status: r.data?.status, trust: r.data?.trust, attraction: r.data?.attraction,
    })),
    plot_threads: (threads.data || []).map((t) => ({
      title: t.title, kind: t.kind, status: t.status,
      current_chapter: t.current_chapter, planned_resolution: t.planned_resolution,
      open_questions: t.data?.open_questions || [],
    })),
    foreshadowing: (shadows.data || []).map((f) => ({
      title: f.title, description: f.description, introduced_chapter: f.introduced_chapter,
      planned_reveal_chapter: f.planned_reveal_chapter, importance: f.importance,
    })),
    recent_summaries: (summaries.data || []).reverse(), // oldest → newest of last 3
    critical_events: (events.data || []).map((e) => ({ chapter: e.chapter_no, event: e.event })),
    genre_skill: skill,
    learned_lessons: learned.lessons || [],
    skill_metrics: learned.metrics || {},
    author_preferences: prefsRow?.data || {},
    anti_ai_rules: ANTI_AI_RULES,
  };
}

/** Compact the context object into a prompt-ready string budget (~4k tokens). */
export function contextToPrompt(ctx) {
  const lines = [];
  lines.push(`NOVEL: "${ctx.novel.title}" | genre=${ctx.novel.genre} | pov=${ctx.novel.pov} | tone=${ctx.novel.tone} | pacing=${ctx.novel.pacing}`);
  if (ctx.premise) lines.push(`PREMISE: ${ctx.premise}`);
  if (ctx.central_question) lines.push(`CENTRAL QUESTION: ${ctx.central_question}`);
  if (ctx.world?.length) lines.push(`WORLD: ${ctx.world.slice(0, 8).map((w) => `${w.name} (${w.type}) — ${w.description}`).join(' | ')}`);
  lines.push(`STYLE GUIDE: ${JSON.stringify(ctx.style_guide).slice(0, 600)}`);
  if (ctx.important_facts?.length) lines.push(`ESTABLISHED FACTS (never contradict): ${ctx.important_facts.map((f) => (typeof f === 'string' ? f : f.fact)).slice(-15).join(' | ')}`);
  if (ctx.forbidden_facts?.length) lines.push(`FORBIDDEN (must NOT happen): ${ctx.forbidden_facts.join(' | ')}`);

  lines.push('CHARACTERS (with current state):');
  for (const c of ctx.characters) {
    const st = Object.entries(c.current_state || {}).map(([k, v]) => `${k}:${v}`).join(',');
    lines.push(`- ${c.name}${c.role ? ` [${c.role}]` : ''} — ${c.essence} | speech: ${c.speech_style} | arc: ${c.arc}${c.secrets?.length ? ` | secrets: ${c.secrets.join('; ')}` : ''} | state{${st}}`);
  }
  lines.push('RELATIONSHIPS:');
  for (const r of ctx.relationships.slice(0, 14)) lines.push(`- ${r.from} → ${r.to}: ${r.type} (${r.status || ''}) trust=${r.trust ?? '?'} attraction=${r.attraction ?? '?'}`);
  lines.push('OPEN PLOT THREADS:');
  for (const t of ctx.plot_threads) lines.push(`- ${t.title} [${t.kind}/${t.status}]${t.planned_resolution ? ` → resolves ch.${t.planned_resolution}` : ''}${t.open_questions?.length ? ` Q: ${t.open_questions.join('; ')}` : ''}`);
  lines.push('ACTIVE FORESHADOWING (plant or reinforce where organic; reveal only if planned for this chapter):');
  for (const f of ctx.foreshadowing) lines.push(`- ${f.title} (planted ch.${f.introduced_chapter}, reveal planned ch.${f.planned_reveal_chapter ?? '?'}, ${f.importance}) — ${f.description}`);
  if (ctx.recent_summaries?.length) {
    lines.push('PREVIOUS CHAPTERS (summaries):');
    for (const s of ctx.recent_summaries) lines.push(`- Ch.${s.chapter_no}: ${s.summary}`);
  }
  if (ctx.critical_events?.length) lines.push(`CRITICAL TIMELINE FACTS: ${ctx.critical_events.map((e) => `ch${e.chapter}:${e.event}`).slice(-12).join(' | ')}`);
  if (ctx.learned_lessons?.length) {
    lines.push(`LESSONS LEARNED FROM QUALITY SCORES AND READER FEEDBACK (apply in this chapter): ${ctx.learned_lessons.map((l) => `- ${l}`).join(' ')}`);
  }
  lines.push(`GENRE SKILL — ${JSON.stringify(ctx.genre_skill).slice(0, 900)}`);
  const prefs = ctx.author_preferences || {};
  const prefLine = Object.entries(prefs).filter(([, v]) => v).map(([k, v]) => `${k.replace(/_/g, ' ')}: ${v}`).join(' | ');
  if (prefLine) lines.push(`AUTHOR PREFERENCES (the human author asked for this — follow it): ${prefLine.slice(0, 800)}`);
  lines.push(ctx.anti_ai_rules);
  return lines.join('\n');
}
