# How to Detect AI in Student Work (Free, No Upload)

If you want to detect AI in student work without burning trust, start with an uncomfortable fact: no detector on the market can prove authorship. AI detectors estimate the probability that a text was machine-written by measuring style, and they get things wrong in both directions. OpenAI's own classifier — released in January 2023 — correctly flagged only 26% of AI-written text while falsely labeling 9% of human writing as AI, and the company shut it down that July, citing its low rate of accuracy. Used as one signal among many, a detector helps start a conversation rather than end a grade. This guide shows the free, browser-only way to screen student writing and avoid the false-accusation trap.

## What an AI detector measures

A detector analyzes writing patterns — sentence uniformity, predictable word choice, and low "burstiness" (the natural variation human writing has). GPTZero, one of the first consumer tools here, built its pitch on two jargon terms: perplexity (how predictable each word choice is) and burstiness (how much sentence structure varies). It outputs a probability, often as a percentage, that the text was generated.

It does not know authorship; it infers from style. That inference is useful as a hint and useless as a verdict, because careful human writing can look machine-like and edited AI text can look human.

### What the score is actually doing

When a detector says "92% AI," it is not saying "92% of these sentences were machine-written." It is saying the document resembles the statistical profile of machine-written text more than 92% of documents in its calibration set — a different claim that collapses the moment a strong human writer submits formal prose or an ESL student submits a carefully built paragraph. Read the number as a similarity score, not a content mix.

## Why it is not proof

Detectors were trained on specific models and drift as models change. The record here is not subtle:

- OpenAI released its AI-text classifier in January 2023 and discontinued it in July 2023, publicly citing a low rate of accuracy.
- Turnitin, the dominant institutional player, publishes its own caveats: the AI indicator is probabilistic, instructor review comes before any action, and the false-positive target is under 1% per document. Turnitin itself tells you not to treat the indicator as evidence.
- A widely covered 2023 Stanford study (Liang et al., later published in the journal Patterns) ran GPT detectors over TOEFL essays by non-native English speakers and flagged more than 60% as AI-generated, while the same detectors flagged roughly 5% of essays by US-born students.

That number deserves a pause: in a class of 100 that includes international students, it means several false flags a term — each an appeal, each a damaged relationship.

A high score is a reason to look closer, never a reason to accuse. The ethical line is clear: use the score to prompt a conversation, not to fail a student on its own.

## When to use it (and when not)

- **As a triage signal** when a submission's voice suddenly differs from past work.
- **To open a dialogue** in a one-to-one meeting about process and drafts.
- **Alongside drafts** so you can see the thinking, not just the final product.
- **Skip it** as the sole basis for any penalty — that is both unfair and appealable.
- **Skip it** for low-stakes or formative work where the cost of error is high, and for multilingual writers without extra care — the Stanford findings apply directly.

One practical rule: the higher the stakes, the more evidence you need beyond the score. A 5-point homework set can tolerate a detector-driven question; a plagiarism hearing cannot.

## How to use it responsibly

Run the text through a detector, but treat the number as one clue. Compare it to the student's earlier writing and to a short in-class sample. Ask to see the draft history or notes. Then, if something looks off, have a calm conversation about how the piece was produced. The goal is learning and integrity, not gotcha policing.

### Process evidence beats output scanning

Experienced teachers stop leaning on detectors because better evidence is one click away. Process evidence is what the student actually did, and it cannot be spoofed by a paraphrasing tool:

- **Version history.** In Google Docs, open File → Version history → See version history: a genuinely written essay shows dozens of edits spread across days, while a pasted-in AI essay often shows one giant dump at 11:47 p.m. Word with OneDrive or SharePoint does the same job.
- **Outlines and notes.** Require a short outline before the essay: fabricating convincing notes that match a final text is harder than writing the essay honestly.
- **In-class baseline.** Keep one low-stakes timed writing sample per student early in the term. It costs one class period and gives you a reference voice.
- **The spoken check.** Ask the student to explain one paragraph aloud — what they meant, why that example. Writers retrieve their own reasoning effortlessly; adapters of text they did not write usually cannot.

### The conversation-first playbook

When a score or a version history raises a flag, the meeting — not the penalty — is the tool. Approaches that surface the truth without an accusation:

- **"Walk me through your sources."** Ask where a specific quote or statistic came from. A student who did the reading knows instantly; one who generated the text fumbles or invents.
- **"Why did you structure it this way?"** Genuine writers have opinions about their own choices ("my first draft buried the argument, so I moved it up").
- **"Rewrite this passage in your own words, right now, from memory."** Five minutes, no internet, and the gap between the polished essay and the live retelling tells you what you need to know.
- **"Define this word as you used it."** Pick a sophisticated term from the essay. AI-pasted work often contains vocabulary the student cannot gloss.

They check comprehension, not style — and comprehension is what education is for.

## A step-by-step method

1. **Establish a baseline** from the student's prior, trusted work — ideally the in-class sample you collected early.
2. **Run the detector** and note the score as a probability, not a fact.
3. **Compare voice** against past submissions for sudden shifts in vocabulary, sentence rhythm, and typical errors (an ESL student's error patterns vanishing overnight is a classic tell — but see the Stanford caveat first).
4. **Check process evidence** — version history, outline, notes — before you talk to anyone.
5. **Talk, don't accuse** — use the signal to start a conversation about process, with the door open for an honest explanation.

Notice the order: the detector is last in the evidence chain for penalties, first only as a triage nudge. Teachers who walk steps 1 and 4 first usually find it changes nothing.

## A worked example

- **Student's past essay — 8% AI.** The human baseline: rough edges, natural burstiness, a few quirky word choices.
- **Sudden formal submission — 91% AI.** Combined with a single-edit version history and a student who cannot gloss their own vocabulary, this is worth a conversation.
- **Edited, personal draft — 22% AI.** Probably human, just polished; heavy revision or a grammar checker can score here.

The middle case is a prompt to talk, not to fail — and in every row the detector is the weakest evidence on the list; the version history and the conversation carry the case.

## Common shapes compared

- **AI detector.** Strength: a fast first signal when something feels off. Weakness: false positives on careful humans, documented bias against non-native writers, drift as models update.
- **Plagiarism check.** Strength: finds copied source text with high confidence. Weakness: blind to original AI-generated text, which by definition copies nothing.
- **Process evidence (drafts, version history, baselines).** Strength: context, fairness, and evidence that survives an appeal. Weakness: slower, and it requires assignments that capture the process.
- **Human review via conversation.** Strength: the only method that measures understanding directly. Weakness: takes time and depends on your judgment.

The methods are complements, not substitutes — the strongest case uses all four; the weakest, only the first.

## A quick scenario: a teacher

A high school teacher receives a flawless essay on The Great Gatsby from a student whose previous work was rough. The detector returns 88%. Instead of marking zero, she checks the version history — one edit, submitted at 11:52 p.m. — and asks the student to walk her through the draft. Asked to define "nihilism" as used in the third paragraph, the student cannot.

The student used a chatbot for the whole essay. Because the conversation was framed around process rather than guilt, she admits it, and the teacher assigns a rewrite with a required outline and a five-minute oral walkthrough — a teachable moment about disclosure, not a disciplinary file.

The punitive path looks different: a zero based on the score alone, an appeal from parents, a teacher defending a number she cannot explain. The conversation-first approach is not just kinder — it holds up.

The practice builds trust over a term: students know the tool prompts reflection rather than setting traps, so they are more honest about process.

## Common mistakes

The worst mistake is accusing a student on a number alone — unfair, often wrong, and frequently reversed on appeal. Other recurring ones:

- **Ignoring false positives for non-native writers**, who get flagged at far higher rates — a detector-based policy is, in effect, one that audits your international students first.
- **Penalizing without process evidence.** Version history and a baseline sample cost nothing to collect after week one and are worth more than any score.
- **Using it punitively on formative work**, where a wrong call costs a relationship over a 10-point draft.
- **Announcing a blanket ban.** A vague "no AI" policy turns every grammar checker and autocomplete into a potential violation students cannot self-police.
- **Relying on a single tool**, throwing away the voice and draft context that makes the signal meaningful.
- **Testing the detector on AI text but never on human text.** Paste in your own five strongest paragraphs. If your own writing scores high, you have personally verified the false-positive problem.

## Who should use it (and who shouldn't)

Teachers, tutors, and editors can use detectors as one input to a fairness-minded review. Skip them as the sole arbiter of any grade, and avoid them where a wrong call carries a heavy personal cost. Pair them with human judgment and, for research contexts, with the broader question of whether AI text helps or hurts the reader.

### Policy design: boundaries beat bans

The programs that age well state AI-use boundaries per assignment, not per institution:

- **AI allowed with citation.** For drafting, brainstorming, or feedback — the student discloses what they used and how.
- **AI allowed for brainstorming only.** Ideas and outlines may come from AI; sentences may not.
- **AI not allowed.** Submitted prose must be the student's own, with process evidence available on request.

Apply the same boundary the same way every time — selective enforcement is what gets departments into appeal hearings. And skip detector-only punitive policies: they generate false accusations at predictable rates and age badly as models improve, while a policy you can actually enforce — "explain your sources and your process" — needs no detector at all.

## How it fits a writing toolkit

Glint's [AI content detector](/blog/free-ai-content-detector-no-upload.html) runs in your browser and never stores the text, so student work stays private — a real FERPA-adjacent concern, since a traditional detector service receives every essay you paste, including writing by minors. Browser-local analysis means the essay never leaves the device. The [private AI detection guide](/blog/private-ai-detector.html) covers what "no upload" does and does not mean; the [non-native English writing guide](/blog/ai-writing-tools-non-native-english.html) explains why false positives hit ESL students hardest. For research-heavy assignments, the [researchers' AI guide](/blog/ai-tools-for-researchers-2026.html) and the ["does Google detect AI content" explainer](/blog/does-google-detect-ai-content.html) help frame the policy you communicate to students, and [our free tools for teachers](/blog/free-ai-tools-teachers.html) cover the rest of the grading workflow. All are free with no signup.

## Frequently asked questions
<p><b>Can an AI detector prove a student cheated?</b> No. OpenAI shut down its own classifier in 2023 for low accuracy, and Turnitin publishes caveats telling instructors not to act on the score alone. It estimates probability; use it to prompt a conversation, never to fail someone on its own.</p>
<p><b>Why do detectors get it wrong?</b> They lean on patterns like uniformity and low burstiness that also appear in careful human writing — and a Stanford study found they falsely flag more than 60% of essays by non-native English writers.</p>
<p><b>Does Google penalize AI text in student work?</b> Google targets unhelpful scaled content, not AI per se; the writing's quality matters more than its origin.</p>
<p><b>How should I combine signals?</b> Pair the score with a short writing sample, a conference, prior work, and version history — never the score alone.</p>
<p><b>Is the Glint detector free with no upload?</b> Yes. It runs in your browser and never stores the text, so student writing — including minors' work — never leaves the device.</p>
