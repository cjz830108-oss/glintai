// /api/fiction/novel — GET the full Story Bible bundle for one novel
import { admin, json, fail, cors, requireUser, ownNovel } from '../_lib/db.js';
import { computeLessons } from '../_lib/skillLearning.js';

export const maxDuration = 15;

export default async function handler(req, res) {
  if (cors(req, res)) return;
  if (req.method !== 'GET') return fail(res, 405, 'method', 'Use GET.');
  return requireUser(req, res, async (user) => {
    const id = (req.query.novel || req.query.id || '').toString();
    if (!id) return fail(res, 400, 'bad_request', 'novel id required');
    const novel = await ownNovel(id, user.id);

    const [bible, characters, relationships, threads, shadows, timeline, chapters, scores, world, summaries] = await Promise.all([
      admin.from('story_bibles').select('data').eq('novel_id', id).maybeSingle(),
      admin.from('characters').select('*').eq('novel_id', id).order('created_at'),
      admin.from('relationships').select('*').eq('novel_id', id),
      admin.from('plot_threads').select('*').eq('novel_id', id).order('created_at'),
      admin.from('foreshadowing').select('*').eq('novel_id', id).order('planned_reveal_chapter'),
      admin.from('timeline_events').select('*').eq('novel_id', id).order('chapter_no'),
      admin.from('chapters').select('id,chapter_no,title,status,word_count,updated_at').eq('novel_id', id).order('chapter_no'),
      admin.from('quality_scores').select('chapter_no,scores,overall').eq('novel_id', id).order('created_at', { ascending: false }),
      admin.from('world_entities').select('*').eq('novel_id', id),
      admin.from('chapter_summaries').select('chapter_no,summary').eq('novel_id', id).order('chapter_no'),
    ]);

    const learned = await computeLessons(novel.genre).catch(() => ({ lessons: [], metrics: { samples: 0 } }));

    return json(res, 200, {
      novel: {
        id: novel.id, title: novel.title, genre: novel.genre, idea: novel.idea,
        pov: novel.pov, tone: novel.pacing ? novel.tone : novel.tone, pacing: novel.pacing,
        lengthTarget: novel.length_target, status: novel.status, chapterCount: novel.chapter_count,
        blueprint: novel.blueprint, updatedAt: novel.updated_at,
      },
      bible: bible?.data || {},
      characters: (characters.data || []).map((c) => ({ id: c.id, name: c.name, ...c.data, current_state: c.current_state, first_chapter: c.first_chapter, last_chapter: c.last_chapter })),
      relationships: relationships.data || [],
      plotThreads: threads.data || [],
      foreshadowing: shadows.data || [],
      timeline: timeline.data || [],
      world: world.data || [],
      chapters: chapters.data || [],
      summaries: summaries.data || [],
      qualityScores: scores.data || [],
      skillLessons: learned.lessons,
      skillMetrics: learned.metrics,
    });
  });
}
