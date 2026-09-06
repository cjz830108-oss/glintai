// Glint Fiction — Genre Skills + Anti-AI Writing Rules (V1 data, versioned in code;
// DB `skills`/`skill_versions` tables are ready for runtime versioning in P1)

export const GENRE_SKILLS = {
  romance: {
    tone: 'emotionally charged, intimate, hopeful undertone',
    pacing: 'steady escalation; alternate tension and tenderness',
    tropes: ['forced proximity', 'second chance', 'slow burn', 'hidden identity'],
    conflict: 'internal vulnerability vs external circumstances',
    dialogue: 'subtext-heavy; characters say less than they mean',
    emotion: 'show longing through small physical details, not labels',
    chapterStructure: ['hook line', 'scene goal', 'escalation', 'setback or cliffhanger'],
    hookStyle: 'open mid-tension — a look, a lie, a touch out of place',
    dynamics: 'power imbalance shifts scene by scene',
    ending: 'earned emotional resolution; avoid unearned grand gestures',
  },
  billionaire_romance: {
    tone: 'glamorous, high-stakes, desire vs pride',
    pacing: 'fast scenes; luxury detail; constant status friction',
    tropes: ['contract relationship', 'enemies to lovers', 'secret past', 'family opposition'],
    conflict: 'money and control vs genuine intimacy',
    dialogue: 'crisp, charged banter; power plays in every exchange',
    emotion: 'wealth as armor cracking in private moments',
    chapterStructure: ['status hook', 'negotiation', 'crack in the armor', 'cliff'],
    hookStyle: 'a deal, a demand, or an accidental intimacy',
    dynamics: 'dominance questioned, not glorified',
    ending: 'love outweighs the contract',
  },
  werewolf: {
    tone: 'primal, fated, dangerous',
    pacing: 'fast; every chapter touches pack politics or the bond',
    tropes: ['fated mates', 'rejected omega', 'rival packs', 'the moon curse'],
    conflict: 'duty to pack vs desire for the mate',
    dialogue: 'terse, territorial, loaded with hierarchy',
    emotion: 'the bond as physical sensation — heat, pull, ache',
    chapterStructure: ['bond beat', 'pack pressure', 'defiance', 'shift or cliffhanger'],
    hookStyle: 'a claim, a rejection, or a scent nobody should recognize',
    dynamics: 'rank friction; loyalty tests',
    ending: 'bond and pack reconciled at real cost',
  },
  fantasy: {
    tone: 'immersive, wondrous, grounded stakes',
    pacing: 'episode-per-chapter; each reveals one rule of the world',
    tropes: ['hidden power', 'prophecy doubted', 'found company', 'dead gods'],
    conflict: 'personal want vs world-level threat',
    dialogue: 'distinct registers per culture; avoid modern slang drift',
    emotion: 'awe and dread through sensory world detail',
    chapterStructure: ['goal', 'journey beat', 'world rule revealed', 'cost or cliffhanger'],
    hookStyle: 'an impossible sight or a broken rule',
    dynamics: 'magic always costs something',
    ending: 'victory with permanent scars',
  },
  thriller: {
    tone: 'tense, clipped, paranoid',
    pacing: 'short scenes; end 80% of chapters on new information',
    tropes: ['unreliable ally', 'ticking clock', 'buried crime', 'wrongly accused'],
    conflict: 'survival vs truth',
    dialogue: 'evasion, half-truths, questions that answer questions',
    emotion: 'fear as physical symptom; relief always premature',
    chapterStructure: ['threat beat', 'investigation', 'false relief', 'reveal or reversal'],
    hookStyle: 'evidence that contradicts what the reader believed',
    dynamics: 'everyone knows something they are not saying',
    ending: 'truth extracted at maximum personal cost',
  },
};

export const ANTI_AI_RULES = `Anti-AI writing rules (detect overuse by frequency + context, never blanket-ban words):
- No repetitive sentence openers; vary sentence length with at least one fragment per 300 words.
- Ban stock metaphors ("heart hammered", "breath hitched", "a beat of silence") if used in the last 5 chapters — replace with specific, physical, scene-grounded detail.
- Dialogue must dodge: characters deflect, interrupt, answer the wrong question.
- Max one abstract emotion label per 500 words; show the rest through action and sensation.
- No formulaic chapter endings ("little did she know") — end on a concrete image, line, or decision.
- No exposition dumps; deliver world facts through conflict.
- Avoid tidy transitions ("meanwhile", "later that day") more than once per chapter.
- Kill doubled adjectives ("cold, dark") unless rhythm demands it.`;
