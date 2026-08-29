# -*- coding: utf-8 -*-
"""Audit-driven SEO fixes for Glint AI. Idempotent. Safe (string inject only)."""
import re, glob, os
ROOT = "C:/Users/Administrator/WorkBuddy/2026-08-06-17-48-44"
os.chdir(ROOT)
DOMAIN = "https://glintai.tools"
DEFAULT_OG = DOMAIN + "/blog/assets/og-default.png"

def read(f):
    return open(f, encoding="utf-8").read()
def write(f, s):
    open(f, "w", encoding="utf-8").write(s)

# ---------- load titles ----------
titles = {}
for f in glob.glob("blog/*.html"):
    slug = os.path.basename(f)
    m = re.search(r"<title>(.*?)</title>", read(f), re.S)
    titles[slug] = re.sub(r"\s+", " ", m.group(1)).strip() if m else slug

def abs_hero(hero):
    if not hero:
        return DEFAULT_OG
    if hero.startswith("http"):
        return hero
    if hero.startswith("/"):
        return DOMAIN + hero
    # relative like assets/xxx.png (resolved under /blog/)
    return DOMAIN + "/blog/" + hero

# ============================================================
# 1) P1: blog/index.html relative links -> absolute
# ============================================================
idx = "blog/index.html"
h = read(idx)
before = h.count('href="blog/') + h.count('src="blog/')
h = h.replace('href="blog/', 'href="/blog/').replace('src="blog/', 'src="/blog/')
after = h.count('href="blog/') + h.count('src="blog/')
write(idx, h)
print("[P1 blog/index] relative->absolute: %d -> %d remaining" % (before, after))

# ============================================================
# 2) M4: tool pages /index.html -> /
# ============================================================
m4 = 0
for f in sorted(glob.glob("tools/*.html")):
    hh = read(f)
    n = hh.count('href="/index.html"')
    if n:
        hh = hh.replace('href="/index.html"', 'href="/"')
        write(f, hh)
        m4 += n
print("[M4 tools] replaced /index.html -> / : %d" % m4)

# ============================================================
# 3) M1/M2a/L1: blog meta og:url, og:image, twitter:image, Article image
# ============================================================
blogs = [f for f in sorted(glob.glob("blog/*.html")) if os.path.basename(f) != "index.html"]
meta_done = 0
for f in blogs:
    hh = read(f)
    changed = False
    can = re.search(r'<link rel="canonical" href="([^"]+)"', hh)
    canonical = can.group(1) if can else ""
    # hero
    body = hh.split("</head>", 1)[-1]
    hero = re.search(r'class="[^"]*hero-img[^"]*"[^>]*src="([^"]+)"', hh)
    if not hero:
        hero = re.search(r'<img[^>]*class="[^"]*hero[^"]*"[^>]*src="([^"]+)"', hh)
    if not hero:
        hero = re.search(r'<img[^>]*src="([^"]+)"', body)
    hero_url = abs_hero(hero.group(1) if hero else "")
    # M1 og:url
    if 'property="og:url"' not in hh and canonical:
        hh = hh.replace('<link rel="canonical" href="%s" />' % canonical,
                        '<link rel="canonical" href="%s" />\n<meta property="og:url" content="%s" />' % (canonical, canonical), 1)
        changed = True
    # M2a og:image + twitter:image (after og:description)
    if 'property="og:image"' not in hh:
        ogdesc = re.search(r'<meta property="og:description" content="[^"]*" />', hh)
        if ogdesc:
            ins = '\n<meta property="og:image" content="%s" />\n<meta name="twitter:image" content="%s" />' % (hero_url, hero_url)
            hh = hh[:ogdesc.end()] + ins + hh[ogdesc.end():]
            changed = True
    # L1 Article image
    if '"@type":"Article"' in hh and '"image"' not in hh.split('"@type":"Article"', 1)[1].split("}", 1)[0]:
        hh = re.sub(r'("@type":"Article",)', r'\1"image":"%s",' % hero_url, hh, count=1)
        changed = True
    if changed:
        write(f, hh)
        meta_done += 1
print("[M1/M2a/L1 blog meta] updated %d / %d pages" % (meta_done, len(blogs)))

# ============================================================
# 4) Group B (P1): pillar blog -> comparison/orphan inbound links
# ============================================================
PILLAR_LINKS = {
    "grammar-checker-guide.html": ["best-ai-grammar-checker-2026.html", "free-grammar-checker-no-signup.html"],
    "free-grammar-checker-no-signup.html": ["best-ai-grammar-checker-2026.html", "grammarly-alternative-free.html"],
    "grammarly-alternative-free.html": ["best-ai-grammar-checker-2026.html", "free-grammar-checker-no-signup.html"],
    "humanize-ai-text.html": ["best-ai-humanizer-tools-2026.html", "ai-content-detector-comparison.html"],
    "ai-content-detector-guide.html": ["ai-content-detector-comparison.html", "best-ai-humanizer-tools-2026.html", "private-ai-detector.html"],
    "private-ai-detector.html": ["ai-content-detector-comparison.html", "best-ai-humanizer-tools-2026.html"],
    "paraphrase-without-losing-meaning.html": ["best-ai-paraphrasing-tools-2026.html", "quillbot-alternative-free.html"],
    "quillbot-alternative-free.html": ["best-ai-paraphrasing-tools-2026.html", "paraphrase-without-losing-meaning.html"],
    "write-resume-with-ai.html": ["best-ai-resume-builder-tools-2026.html", "ai-cover-letter-resume-guide.html"],
    "write-professional-bio-guide.html": ["best-ai-resume-builder-tools-2026.html", "ai-cover-letter-resume-guide.html"],
    "ai-cover-letter-resume-guide.html": ["best-ai-resume-builder-tools-2026.html", "write-resume-with-ai.html"],
    "how-to-summarize-long-articles.html": ["best-ai-text-summarizer-tools-2026.html", "best-free-pdf-summarizer-tools-2026.html"],
    "summarize-pdf-guide.html": ["best-ai-text-summarizer-tools-2026.html", "best-free-pdf-summarizer-tools-2026.html"],
    "markdown-to-html-workflow.html": ["best-free-markdown-to-html-converter.html"],
    "why-marketers-need-a-json-formatter.html": ["best-free-json-formatter.html"],
    "serp-preview-meta-tags.html": ["best-free-serp-preview-tool.html"],
    "meta-description-ctr-guide.html": ["best-free-serp-preview-tool.html", "best-youtube-title-generator-tools-2026.html", "best-ai-writing-tools-marketers-2026.html"],
    "reading-ease-score-landing-page.html": ["best-reading-ease-analyzer-tools-2026.html", "improve-reading-ease-score.html"],
    "improve-reading-ease-score.html": ["best-reading-ease-analyzer-tools-2026.html", "reading-ease-score-landing-page.html"],
    "word-character-counter.html": ["best-reading-ease-analyzer-tools-2026.html"],
    "youtube-title-generator-guide.html": ["best-youtube-title-generator-tools-2026.html", "meta-description-ctr-guide.html"],
    "hashtag-generator-guide.html": ["best-hashtag-generator-tools-2026.html"],
    "remove-background-image-guide.html": ["best-background-remover-tools-2026.html"],
    "ai-tools-content-creator-starter-list.html": ["best-free-ai-tools-bloggers-2026.html", "best-ai-writing-tools-marketers-2026.html", "chatgpt-vs-claude-vs-gemini-writing.html"],
    "best-free-ai-tools-bloggers-2026.html": ["best-ai-writing-tools-marketers-2026.html", "ai-tools-content-creator-starter-list.html"],
    "best-ai-writing-tools-marketers-2026.html": ["best-free-ai-tools-bloggers-2026.html", "ai-tools-content-creator-starter-list.html", "meta-description-ctr-guide.html"],
    "free-ai-tools-students-2026.html": ["free-vs-pro-ai-tools.html", "ai-tools-content-creator-starter-list.html"],
    "free-vs-pro-ai-tools.html": ["free-ai-tools-students-2026.html", "best-ai-writing-tools-marketers-2026.html"],
    "chatgpt-vs-claude-vs-gemini-writing.html": ["ai-content-detector-comparison.html", "ai-tools-content-creator-starter-list.html"],
}
def add_rel_link(hh, target, text):
    href = '/blog/%s' % target
    if href in hh:
        return hh, False
    m = re.search(r'<div class="rel">.*?</div>', hh, re.DOTALL)
    if not m:
        return hh, False
    block = m.group(0)
    head, tail = block.rsplit("</div>", 1)
    new_block = head + '<a href="%s">→ %s</a>\n  ' % (href, text) + "</div>" + tail
    return hh[:m.start()] + new_block + hh[m.end():], True

b_count = 0
for pillar, targets in PILLAR_LINKS.items():
    f = os.path.join("blog", pillar)
    if not os.path.exists(f):
        print("  [B] skip missing pillar", pillar); continue
    hh = read(f)
    did = False
    for t in targets:
        if t == pillar:
            continue
        hh, ok = add_rel_link(hh, t, titles.get(t, t))
        did = did or ok
    if did:
        write(f, hh); b_count += 1
print("[Group B inbound] updated %d pillar pages" % b_count)

# ============================================================
# 5) Group A (P2): tool Related guides -> themed blog links
# ============================================================
TOOL_LINKS = {
    "ai-text-summarizer.html": ["how-to-summarize-long-articles.html", "summarize-pdf-guide.html", "best-ai-text-summarizer-tools-2026.html", "humanize-ai-text.html"],
    "ai-humanizer.html": ["humanize-ai-text.html", "best-ai-humanizer-tools-2026.html", "paraphrase-without-losing-meaning.html", "ai-content-detector-comparison.html"],
    "ai-content-detector.html": ["ai-content-detector-guide.html", "ai-content-detector-comparison.html", "private-ai-detector.html", "best-ai-humanizer-tools-2026.html"],
    "markdown-to-html.html": ["markdown-to-html-workflow.html", "best-free-markdown-to-html-converter.html"],
    "json-formatter.html": ["why-marketers-need-a-json-formatter.html", "best-free-json-formatter.html", "ai-tools-content-creator-starter-list.html"],
    "password-generator.html": ["strong-password-generator-guide.html", "generate-api-keys-safely.html"],
    "youtube-title-generator.html": ["youtube-title-generator-guide.html", "best-youtube-title-generator-tools-2026.html", "meta-description-ctr-guide.html"],
    "serp-preview.html": ["serp-preview-meta-tags.html", "best-free-serp-preview-tool.html", "meta-description-ctr-guide.html"],
    "word-counter.html": ["word-character-counter.html", "improve-reading-ease-score.html", "best-reading-ease-analyzer-tools-2026.html"],
    "grammar-checker.html": ["grammar-checker-guide.html", "free-grammar-checker-no-signup.html", "best-ai-grammar-checker-2026.html", "grammarly-alternative-free.html"],
    "hashtag-generator.html": ["hashtag-generator-guide.html", "best-hashtag-generator-tools-2026.html"],
    "pdf-summarizer.html": ["summarize-pdf-guide.html", "best-free-pdf-summarizer-tools-2026.html", "how-to-summarize-long-articles.html"],
    "paraphraser.html": ["paraphrase-without-losing-meaning.html", "best-ai-paraphrasing-tools-2026.html", "quillbot-alternative-free.html"],
    "bio-resume-generator.html": ["write-professional-bio-guide.html", "write-resume-with-ai.html", "best-ai-resume-builder-tools-2026.html", "ai-cover-letter-resume-guide.html"],
    "background-remover.html": ["remove-background-image-guide.html", "best-background-remover-tools-2026.html"],
    "word-readability-analyzer.html": ["reading-ease-score-landing-page.html", "improve-reading-ease-score.html", "best-reading-ease-analyzer-tools-2026.html"],
}
def add_ul_link(hh, target, text):
    href = '/blog/%s' % target
    if href in hh:
        return hh, False
    m = re.search(r'(<section class="related">\s*<h2>Related guides</h2>\s*<ul>)(.*?)(</ul>)', hh, re.DOTALL)
    if not m:
        return hh, False
    new_li = '<li><a href="%s">%s</a></li>' % (href, text)
    new_ul = m.group(1) + m.group(2) + new_li + m.group(3)
    return hh[:m.start()] + new_ul + hh[m.end():], True

a_count = 0
for tool, targets in TOOL_LINKS.items():
    f = os.path.join("tools", tool)
    if not os.path.exists(f):
        print("  [A] skip missing tool", tool); continue
    hh = read(f)
    did = False
    for t in targets:
        hh, ok = add_ul_link(hh, t, titles.get(t, t))
        did = did or ok
    if did:
        write(f, hh); a_count += 1
print("[Group A tool->blog] updated %d tool pages" % a_count)
print("DONE")
