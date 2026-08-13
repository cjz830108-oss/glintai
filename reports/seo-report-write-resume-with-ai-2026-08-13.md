# SEO Audit Report — write-resume-with-ai
**Phase 3 pre-publish audit** | Date: 2026-08-13 | Auditor: 欧化成 (SEO Optimizer)

---

## 1. SEO Readiness Score
**69 / 100**  ← *lowest of the five*
Solid structure (17 H2s), strong internal linking (18 valid links), and a clear steps section for snippets. But it carries the **worst title overflow (64 chars, +4 over max)**, an **exact primary-keyword density of only ~0.1%** in the body, and the **site-wide duplicated FAQ** defect — the most combined relevance + technical gaps of the batch.

---

## 2. Primary keyword & density
- **Primary keyword:** `write a resume with ai`
- **Exact occurrences in `content`:** **2**
- **Total content words (tag-stripped prose):** **2,091**
- **Exact-phrase density:** **0.096%** → ⚠️ **FLAGGED** (outside the 1–2% target)
- **Note:** The exact phrase "write a resume with AI" appears just twice (intro/H2 area); the body mostly uses "resume with AI", "the generator", and "your resume". Topically relevant, but exact-match anchoring is weak. Recommendation: add the exact phrase **2–3 more times** naturally (an H2 such as "Why write a resume with AI instead of from scratch", a workflow intro, and a CTA) — without over-stuffing.

---

## 3. Meta title variants (50–60 chars, includes primary keyword)
1. `Write a Resume With AI: ATS Friendly in Minutes Free` (52)
2. `Write a Resume With AI: Build a Clean CV, Free Today` (52)
3. `How to Write a Resume With AI, Step by Step Quickly` (51)
4. `Write a Resume With AI and Keep Your Voice for Free` (50)
5. `Write a Resume With AI: Free Generator, No Sign Up` (50)

---

## 4. Meta description variants (150–160 chars, plain text, no double quotes)
1. Write a resume with AI to get a structured first draft in minutes, then humanize the voice and proof it for you. Glint AI's free generator needs no sign up. (152)
2. Write a resume with AI and beat the blank page. Generate a clean, ATS friendly CV, refine the wording, and tailor it to each job without losing your voice. (155)
3. Learn to write a resume with AI that sounds human. Draft with the generator, soften the tone with the humanizer, and catch errors with the grammar checker. (155)
4. Write a resume with AI to turn ten years of experience into a clean CV fast. Free browser tool, no account, and your details stay off a vendor server. (150)
5. Write a resume with AI the safe way: let the tool draft, you stay in control. Build an ATS friendly CV, then humanize and proof it before you hit send. (151)

---

## 5. Schema audit
Fields consumed by `gen_blog.py` for **Article + FAQPage** JSON-LD:
- `title` ✅ present
- `meta` ✅ present
- `date` ✅ present (`2026-08-13`)
- `faqs` ✅ present — count = **5** (≥4 ✓)
- `hero_alt` ✅ present
- ⚠️ **Defect:** FAQ #1 is duplicated verbatim as FAQ #5 ("Should I use one resume for every job?"). This emits a duplicate `FAQPage` Question node. **Fix:** replace the duplicate with a unique 5th question (e.g., "Can the generator handle a career gap?" or "Should I include a photo on my resume?").
- Minor: rich `keywords` field present — confirm it maps into Article `keywords` in the JSON-LD.

---

## 6. Featured Snippet advice
**Most snippet-likely H2:** `The human-in-the-loop resume workflow` — an ordered 3-step list (`<ol>`), ideal for a steps snippet.
**Concrete tweaks:**
1. Lead the H2 with a **40–55 word definition**, e.g., *"The human-in-the-loop resume workflow keeps you in charge: the AI drafts, you humanize the voice, and the grammar checker proofs. This three-pass loop produces a resume with AI that still sounds like you."* This gives Google a liftable paragraph plus the steps.
2. Keep each `<li>` to **one verb-led clause** so the list is extractable as numbered steps.

---

## 7. Internal-link audit
**`related` hrefs (6):**
- `/tools/bio-resume-generator.html` ✅
- `/tools/ai-humanizer.html` ✅
- `/tools/grammar-checker.html` ✅
- `/blog/write-professional-bio-guide.html` ✅
- `/blog/ai-cover-letter-resume-guide.html` ✅
- `/#tools` ✅

**Inline `<a href>` in `content` (12):**
- `/tools/bio-resume-generator.html` ✅
- `/tools/ai-humanizer.html` ✅
- `/tools/grammar-checker.html` ✅
- `/tools/bio-resume-generator.html` ✅
- `/tools/ai-humanizer.html` ✅
- `/blog/write-professional-bio-guide.html` ✅
- `/blog/ai-cover-letter-resume-guide.html` ✅
- `/tools/bio-resume-generator.html` ✅
- `/tools/ai-humanizer.html` ✅
- `/blog/ai-cover-letter-resume-guide.html` ✅
- `/tools/ai-humanizer.html` ✅
- `/tools/bio-resume-generator.html` ✅

**Total internal links = 18** (≥5 ✓). **No defects** — every link ends in `.html` or is `/#tools`. (Note: `/tools/bio-resume-generator.html` repeats 4× and `/tools/ai-humanizer.html` 4× inline; diversify 1–2 anchors if easy — not a blocker.)

---

## 8. Pre-publish checklist
- [ ] **Title length 50–60:** FAIL — current 64 chars (`Write a Resume With AI: Build a Clean ATS-Friendly CV in Minutes`). Trim to ≤60 using a §3 variant.
- [x] **Meta length 150–160:** PASS — 156 chars.
- [ ] **Keyword density 1–2%:** FAIL — exact phrase ~0.1% in body. Weave exact phrase into 2–3 natural spots.
- [x] **≥4 FAQs:** PASS — 5 (but fix the duplicate, see §5).
- [x] **≥5 internal links:** PASS — 18.
- [x] **All links end in .html:** PASS — 0 defects.
- [x] **hero_alt present:** PASS.
- [x] **Content 2000–2500 words:** PASS — 2,091.
