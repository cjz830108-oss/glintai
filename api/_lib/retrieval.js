// Glint Fiction — Memory Retrieval (V1: structured SQL retrieval + relevance scoring, no pgvector)
// Assembles the Writer Context for one chapter: relevance-ranked characters/states,
// relationships, plot threads, reveal-window foreshadowing, recent summaries,
// critical timeline events, author style preferences, learned lessons + genre rules.
// Never dumps the whole bible.

import { admin } from './db.js';
import { GENRE_SKILLS, ANTI_AI_RULES } from './skills.js';
import { computeLessons } from './skillLearning.js';

/** P0-8: foreshadowing retrieval priority — items near their planned reveal surge. */
function foreshadowPriority(f, chapterNo) {
  let score = 1;
  if (f.status === 'planted' || f.status === 'reinforced') {
    const reveal = f.planned_reveal_chapter;
    if (reveal != null) {
      const dist = reveal - chapterNo;
      if (dist >= 0 && dist <= 5) score += 6;        // reveal window — top priority
      else if (dist > 5 && dist <= 15) score += 3;   // approaching — reinforce
      else if (dist < 0) score -= 4;                 // overdue/missed — deprioritize
    }
    if (f.introduced_chapter != null && chapterNo - f.introduced_chapter <= 3) score += 2; // recently planted
    if (f.importance === 'major') score += 1;
  }
  return score;
}

export async function buildChapterContext(novel, chapterNo) {
  const novelId = novel.id;

  const [characters, relationships, threads, shadows, summaries, events, bibleRow, prefsRow] = await Promise.all([
    admin.from('characters').select('*').eq('novel_id', novelId).eq('active', true).order('created_at').limit(24),
    admin.from('relationships').select('*').eq('novel_id', novelId).limit(60),
    admin.from('plot_threads').select('*').eq('novel_id', novelId).in('status', ['open', 'advancing']).limit(30),
    admin.from('foreshadowing').select('*').eq('novel_id', novelId).in('status', ['planted', 'reinforced']).limit(40),
    admin.from('chapter_summaries').select('chapter_no,summary,events')
      .eq('novel_id', novelId).lt('chapter_no', chapterNo).order('chapter_no', { ascending: false }).limit(5),
    admin.from('timeline_events').select('*').eq('novel_id', novelId).eq('importance', 'critical').order('chapter_no', { ascending: false }).limit(40),
    admin.from('story_bibles').select('data').eq('novel_id', novelId).maybeSingle(),
    admin.from('user_preferences').select('data').eq('user_id', novel.user_id).maybeSingle(),
  ]);

  const bible = bibleRow?.data || {};
  const skill = GENRE_SKILLS[novel.genre] || GENRE_SKILLS.romance;
  const learned = await computeLessons(novel.genre);

  // --- P0-7: this chapter's plan drives relevance scoring ---
  const planEntry = (bible.chapter_plan || []).find((p) => Number(p.no) === Number(chapterNo)) || {};
  const castNames = (planEntry.characters || []).map((n) => String(n).toLowerCase());
  const planThreads = (planEntry.threads || []).map((t) => String(t).toLowerCase());
  const planForeshadow = (planEntry.foreshadowing || []).map((t) => String(t).toLowerCase());
  const planLocation = String(planEntry.location || '').toLowerCase();

  // characters: +5 planned in this chapter, +2 protagonist, +1 ordinary → keep top 14
  const rankedCharacters = (characters.data || [])
    .map((c) => {
      let score = 1;
      if (castNames.includes(c.name.toLowerCase())) score += 5;
      if ((c.data?.role || '') === 'protagonist') score += 2;
      if (c.last_chapter != null && chapterNo - c.last_chapter <= 2) score += 2; // on stage recently
      return { c, score };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, 14)
    .map((x) => x.c);

  // relationships involving ranked characters
  const rankedIds = new Set(rankedCharacters.map((c) => c.id));
  const rankedRels = (relationships.data || [])
    .filter((r) => rankedIds.has(r.from_character_id) && rankedIds.has(r.to_character_id))
    .slice(0, 20);

  // plot threads: +5 planned in this chapter, else 1 → keep top 12
  const rankedThreads = (threads.data || [])
    .map((t) => ({ t, score: planThreads.includes(t.title.toLowerCase()) ? 6 : 1 }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 12)
    .map((x) => x.t);

  // foreshadowing: reveal-window weighting (P0-8)
  const rankedShadows = (shadows.data || [])
    .map((f) => ({
      f,
      score: foreshadowPriority(f, chapterNo) + (planForeshadow.includes(f.title.toLowerCase()) ? 5 : 0),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 14)
    .map((x) => x.f);

  // world entities relevant to this chapter's location first
  const rankedWorld = (bible.world || [])
    .map((w) => ({ w, score: planLocation && String(w.name).toLowerCase().includes(planLocation) ? 5 : 1 }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 8)
    .map((x) => x.w);

  return {
    novel: {
      title: novel.title, genre: novel.genre, pov: novel.pov, tone: novel.tone,
      pacing: novel.pacing, target_chapters: novel.length_target, idea: novel.idea,
    },
    current_chapter: chapterNo,
    world: rankedWorld,
    style_guide: bible.style_guide || {},
    permanent_facts: (bible.permanent_facts || []),                    // never truncated (P0-13)
    important_facts: (bible.important_facts || []).slice(-20),
    forbidden_facts: bible.forbidden_facts || [],
    premise: bible.premise || '',
    central_question: bible.central_question || '',
    characters: rankedCharacters.map((c) => ({
      id: c.id, name: c.name, role: c.data?.role || '',
      essence: c.data?.essence || '',
      speech_style: c.data?.speech_style || '',
      arc: c.data?.character_arc || '',
      secrets: (c.data?.secrets || []).slice(0, 4),
      current_state: c.current_state || {},
      first_chapter: c.first_chapter,
    })),
    relationships: rankedRels.map((r) => ({
      from: r.data?.from_name, to: r.data?.to_name,
      type: r.data?.type, status: r.data?.status, trust: r.data?.trust, attraction: r.data?.attraction,
    })),
    plot_threads: rankedThreads.map((t) => ({
      title: t.title, kind: t.kind, status: t.status,
      current_chapter: t.current_chapter, planned_resolution: t.planned_resolution,
      open_questions: t.data?.open_questions || [],
    })),
    foreshadowing: rankedShadows.map((f) => ({
      title: f.title, description: f.description, introduced_chapter: f.introduced_chapter,
      planned_reveal_chapter: f.planned_reveal_chapter, importance: f.importance, status: f.status,
    })),
    recent_summaries: (summaries.data || []).reverse(), // oldest → newest of last 5
    critical_events: (events.data || []).map((e) => ({ chapter: e.chapter_no, event: e.event })).reverse(),
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
  if (ctx.permanent_facts?.length) {
    lines.push(`PERMANENT FACTS (canonical, never contradict, never truncate): ${ctx.permanent_facts.map((f) => (typeof f === 'string' ? f : f.fact)).join(' | ')}`);
  }
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
  lines.push('ACTIVE FORESHADOWING (ranked by reveal proximity):');
  for (const f of ctx.foreshadowing) {
    const reveal = f.planned_reveal_chapter;
    const gate = (reveal != null && f.status !== 'revealed' && reveal > ctx.current_chapter)
      ? ` — DO NOT REVEAL before ch.${reveal} (plant/reinforce only)`
      : (f.status !== 'revealed' && reveal != null ? ` — REVEAL WINDOW: may pay off now` : '');
    lines.push(`- ${f.title} (planted ch.${f.introduced_chapter}, reveal planned ch.${reveal ?? '?'}, ${f.importance}) — ${f.description}${gate}`);
  }
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
