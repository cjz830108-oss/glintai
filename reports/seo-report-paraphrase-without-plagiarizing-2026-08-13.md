# SEO Audit Report — paraphrase-without-plagiarizing
**Phase 3 pre-publish audit** | Date: 2026-08-13 | Auditor: 欧化成 (SEO Optimizer)

---

## 1. SEO Readiness Score
**71 / 100**
Thorough, well-organized content (16 H2s) with strong internal linking (18 valid links) and a clean 5-step list primed for snippets. Held back by a **0% exact primary-keyword density in the body**, a **title 2 chars over the 60 max**, and a **duplicated FAQ** entry.

---

## 2. Primary keyword & density
- **Primary keyword:** `paraphrase without plagiarizing`
- **Exact occurrences in `content`:** **0**
- **Total content words (tag-stripped prose):** **2,079**
- **Exact-phrase density:** **0.0%** → ⚠️ **FLAGGED** (outside the 1–2% target)
- **Note:** The body uses "paraphrasing", "plagiarizing", "reword", and "cite" heavily but **never the exact contiguous phrase** "paraphrase without plagiarizing" (it appears only in `title`, `meta`, `keywords`, `lead`). Topical relevance is solid; exact-match anchoring is missing. Recommendation: add the exact phrase **2–3 times** naturally (an H2 like "How to paraphrase without plagiarizing in 5 steps", the intro, and a CTA) — no over-stuffing.

---

## 3. Meta title variants (50–60 chars, includes primary keyword)
1. `Paraphrase Without Plagiarizing: A Safe Method to Use` (53)
2. `How to Paraphrase Without Plagiarizing Sources Safely` (53)
3. `Paraphrase Without Plagiarizing: Reword and Cite Safely` (55)
4. `Paraphrase Without Plagiarizing Using 5 Safe Steps` (50)
5. `Paraphrase Without Plagiarizing: The Free Tool Guide` (52)

---

## 4. Meta description variants (150–160 chars, plain text, no double quotes)
1. Learn to paraphrase without plagiarizing by restating the idea in your own words and citing it. Glint AI's free paraphraser rewords text safely, no sign up. (155)
2. Paraphrase without plagiarizing using a simple five step method: read, set aside, rewrite, compare, and cite. Keep your writing original and properly credited. (159)
3. Want to paraphrase without plagiarizing? Reword the idea, keep your own voice, and add the citation. This guide shows the method plus a free tool to help. (154)
4. Paraphrase without plagiarizing by changing the words and the structure, then crediting the source. Avoid the synonym swap trap that still counts as plagiarism. (160)
5. Master how to paraphrase without plagiarizing with a clear, repeatable workflow. Understand the source, restate it independently, and credit the source. (156)

---

## 5. Schema audit
Fields consumed by `gen_blog.py` for **Article + FAQPage** JSON-LD:
- `title` ✅ present
- `meta` ✅ present
- `date` ✅ present (`2026-08-13`)
- `faqs` ✅ present — count = **5** (≥4 ✓)
- `hero_alt` ✅ present
- ⚠️ **Defect:** FAQ #1 is duplicated verbatim as FAQ #5 ("Do I need to cite a paraphrase in my own published work?"). This emits a duplicate `FAQPage` Question node. **Fix:** replace the duplicate with a unique 5th question (e.g., "Can I paraphrase a paraphrase?" or "Does paraphrasing change the meaning of the source?").
- Minor: rich `keywords` field present — confirm it maps into Article `keywords` in the JSON-LD.

---

## 6. Featured Snippet advice
**Most snippet-likely H2:** `The 5-step method that keeps you safe` — already an ordered list (`<ol>`), ideal for a steps snippet.
**Concrete tweaks:**
1. Lead the H2 with a **40–55 word definition**, e.g., *"To paraphrase without plagiarizing, restate the source idea in your own words and credit it. The five steps below turn that rule into a repeatable habit: read, set aside, rewrite, compare, and cite."* This lets Google lift both a paragraph and the steps.
2. Keep each `<li>` to **one short clause** (verb-led) so the list is snippet-extractable as numbered steps.

---

## 7. Internal-link audit
**`related` hrefs (6):**
- `/tools/paraphraser.html` ✅
- `/tools/grammar-checker.html` ✅
- `/tools/ai-humanizer.html` ✅
- `/blog/paraphrase-without-losing-meaning.html` ✅
- `/blog/grammar-checker-guide.html` ✅
- `/#tools` ✅

**Inline `<a href>` in `content` (12):**
- `/tools/paraphraser.html` ✅
- `/tools/grammar-checker.html` ✅
- `/tools/paraphraser.html` ✅
- `/tools/paraphraser.html` ✅
- `/tools/grammar-checker.html` ✅
- `/tools/ai-humanizer.html` ✅
- `/blog/paraphrase-without-losing-meaning.html` ✅
- `/blog/grammar-checker-guide.html` ✅
- `/tools/paraphraser.html` ✅
- `/tools/grammar-checker.html` ✅
- `/tools/ai-humanizer.html` ✅
- `/blog/paraphrase-without-losing-meaning.html` ✅

**Total internal links = 18** (≥5 ✓). **No defects** — every link ends in `.html` or is `/#tools`. (Note: `/tools/paraphraser.html` repeats 5× inline; diversify 1–2 anchors if easy — not a blocker.)

---

## 8. Pre-publish checklist
- [ ] **Title length 50–60:** FAIL — current 62 chars (`Paraphrase Without Plagiarizing: Reword and Cite the Right Way`). Trim to ≤60 using a §3 variant.
- [x] **Meta length 150–160:** PASS — 153 chars.
- [ ] **Keyword density 1–2%:** FAIL — exact phrase 0.0% in body. Weave exact phrase into 2–3 natural spots.
- [x] **≥4 FAQs:** PASS — 5 (but fix the duplicate, see §5).
- [x] **≥5 internal links:** PASS — 18.
- [x] **All links end in .html:** PASS — 0 defects.
- [x] **hero_alt present:** PASS.
- [x] **Content 2000–2500 words:** PASS — 2,079.
