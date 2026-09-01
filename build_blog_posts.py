#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert the 5 Phase-2 markdown drafts into full Glint AI blog HTML pages.

Reuses the site's existing cyberpunk CSS (cloned from blog/humanize-ai-text.html),
adds og:image / twitter:image / Article.image (post-audit state), BreadcrumbList
JSON-LD (briefs require it), a hero PNG per post, Key Takeaways, visible FAQ, and
a Sources section. Idempotent: skips pages that already exist.
"""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BLOG = os.path.join(ROOT, "blog")
ASSETS = os.path.join(BLOG, "assets")
TEMPLATE = os.path.join(BLOG, "humanize-ai-text.html")
DATE = "2026-09-01"
SITE = "https://glintai.tools"


def extract_css():
    html = open(TEMPLATE, encoding="utf-8").read()
    return re.search(r"<style>(.*?)</style>", html, re.S).group(1)


CSS = extract_css()


def j(val):
    return json.dumps(val, ensure_ascii=False)


# ---------- markdown -> html (subset used by the drafts) ----------
def inline(s):
    s = re.sub(r'\[([^\]]+)\]\((/[^)]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = s.replace(' & ', ' &amp; ')
    return s


def table_to_html(rows):
    cells = []
    for r in rows:
        r = r.strip()
        if r.startswith('|'):
            r = r[1:]
        if r.endswith('|'):
            r = r[:-1]
        cells.append([c.strip() for c in r.split('|')])
    head, body = cells[0], cells[2:]
    thead = '<tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr>'
    tbody = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>' for row in body)
    return f'<table><thead>{thead}</thead><tbody>{tbody}</tbody></table>'


def md_to_html(md):
    lines = [ln for ln in md.split('\n')
             if not re.match(r'^\s*<p><b>.*?</b>.*?</p>\s*$', ln, re.S)]
    lines = '\n'.join(lines).split('\n')
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1; continue
        if line.startswith('### '):
            out.append(f'<h3>{inline(line[4:])}</h3>'); i += 1; continue
        if line.startswith('## '):
            h = inline(line[3:])
            if h.lower().startswith('frequently asked questions'):
                out.append('<!--FAQ-->'); i += 1; continue
            out.append(f'<h2>{h}</h2>'); i += 1; continue
        if line.startswith('# '):
            i += 1; continue
        if line.strip().startswith('|'):
            tbl = []
            while i < n and lines[i].strip().startswith('|'):
                tbl.append(lines[i]); i += 1
            out.append(table_to_html(tbl)); continue
        if re.match(r'^\d+\.\s', line):
            items = []
            while i < n and re.match(r'^\d+\.\s', lines[i]):
                items.append(lines[i]); i += 1
            out.append('<ol>' + ''.join(f'<li>{inline(x.split(".", 1)[1].strip())}</li>' for x in items) + '</ol>'); continue
        if line.strip().startswith('- '):
            items = []
            while i < n and lines[i].strip().startswith('- '):
                items.append(lines[i]); i += 1
            out.append('<ul>' + ''.join(f'<li>{inline(x.strip()[2:])}</li>' for x in items) + '</ul>'); continue
        para = []
        while (i < n and lines[i].strip() and not lines[i].lstrip().startswith(('#', '|', '- '))
               and not re.match(r'^\d+\.\s', lines[i])):
            para.append(lines[i]); i += 1
        out.append('<p>' + inline(' '.join(para)) + '</p>'); continue
    return '\n'.join(out)


def extract_faq(md):
    return [(q.strip(), a.strip()) for q, a in re.findall(r'<p><b>(.*?)</b>\s*(.*?)</p>', md, re.S)]


def extract_h1(md):
    return md.split('\n', 1)[0].lstrip('# ').strip()


# ---------- hero image (defensive; falls back to og-default) ----------
def make_hero(slug, accent, title, category):
    out = os.path.join(ASSETS, f"{slug}.png")
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        W, H = 1200, 630
        img = Image.new('RGBA', (W, H), (7, 7, 13, 255))
        top, bot = (18, 16, 40, 255), (7, 7, 13, 255)
        for y in range(H):
            t = y / H
            col = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(4))
            ImageDraw.Draw(img).line([(0, y), (W, y)], col)
        ac = tuple(int(accent[i:i + 2], 16) for i in (1, 3, 5)) + (38,)
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for x in range(0, W, 48):
            d.line([(x, 0), (x, H)], ac)
        for y in range(0, H, 48):
            d.line([(0, y), (W, y)], ac)
        img = Image.alpha_composite(img, ov)
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([W - 540, H - 380, W + 140, H + 280], fill=ac[:3] + (130,))
        glow = glow.filter(ImageFilter.GaussianBlur(85))
        img = Image.alpha_composite(img, glow)
        draw = ImageDraw.Draw(img)
        try:
            fb = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 30)
            fc = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 26)
            ft = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 56)
        except Exception:
            fb = fc = ft = ImageFont.load_default()
        draw.text((60, 56), "✨ GLINT AI", font=fb, fill=(0, 240, 255, 255))
        draw.text((60, 104), category.upper(), font=fc, fill=(154, 160, 192, 255))
        words, cur, lines = title.split(), '', []
        for w in words:
            if len(cur + ' ' + w) < 32:
                cur = (cur + ' ' + w).strip()
            else:
                lines.append(cur); cur = w
        if cur:
            lines.append(cur)
        ty = 300
        for ln in lines[:3]:
            draw.text((60, ty), ln, font=ft, fill=(232, 232, 245, 255))
            ty += 66
        img.convert('RGB').save(out)
        return True
    except Exception as e:
        print(f"  hero FAIL {slug}: {e}")
        return False


# ---------- post config ----------
POSTS = [
    dict(
        slug="ai-headline-generator",
        title="AI Headline Generator: Write Titles That Get Clicks",
        description="Generate blog, YouTube and email headlines with our free AI headline generator. No signup, private in-browser, CTR-tested formulas. Try it free now.",
        keywords="ai headline generator, blog title generator free, ai blog title ideas, catchy headline generator, article title generator no signup",
        category="Writing",
        accent="#00f0ff",
        readtime=10,
        related=[
            ("YouTube Title Generator Guide", "/blog/youtube-title-generator-guide.html"),
            ("Best YouTube Title Generators", "/blog/best-youtube-title-generator-tools-2026.html"),
            ("Write Meta Descriptions That Boost CTR", "/blog/meta-description-ctr-guide.html"),
            ("Best Free SERP Preview Tool", "/blog/best-free-serp-preview-tool.html"),
            ("Try the free Title Generator", "/tools/youtube-title-generator.html"),
        ],
        sources=[
            ("Google Search Central: Title Links", "https://developers.google.com/search/docs/appearance/title-link", "How titles are generated and truncated."),
            ("Google Search Central: Snippets", "https://developers.google.com/search/docs/appearance/snippet", "How snippets appear in results."),
            ("Nielsen Norman Group: How Users Read", "https://www.nngroup.com/articles/how-users-read-web/", "Reading behavior and scannability."),
            ("Glint AI Title Generator", "/tools/youtube-title-generator.html", "Free, no signup."),
            ("Glint AI SERP Preview", "/tools/serp-preview.html", "Preview before publishing."),
        ],
        takeaways=[
            "Your title does most of the work of earning the click — spend real time on it.",
            "Seven reusable formulas cover almost any topic: number+benefit, how-to, question, negative, secret, comparison, list.",
            "The real limit is pixel width, not character count — always preview your title in search.",
            "Use a free, no-signup generator for ideas, then edit for your voice and test.",
            "Titles differ by platform: blog, video, email, and social each need a different frame.",
        ],
        closing='Open the free <a href="/tools/youtube-title-generator.html">AI title generator</a> and the <a href="/tools/serp-preview.html">SERP preview tool</a>, write one better title today, and measure the difference.',
    ),
    dict(
        slug="free-ai-tools-developers",
        title="Free AI Tools for Developers: 12 No-Signup Picks",
        description="Compare 12 free AI tools for developers in 2026 — code review, JSON, Markdown, key safety. No signup, browser-private. Start free now.",
        keywords="free ai tools for developers, ai coding tools free, best ai tools for programmers, free developer ai tools no signup, local ai tools that keep code private",
        category="Developers",
        accent="#39ff14",
        readtime=11,
        related=[
            ("Best Free JSON Formatter", "/blog/best-free-json-formatter.html"),
            ("Best Free Markdown to HTML Converter", "/blog/best-free-markdown-to-html-converter.html"),
            ("Generate API Keys Safely", "/blog/generate-api-keys-safely.html"),
            ("Build Unbreakable Passwords", "/blog/strong-password-generator-guide.html"),
            ("Try the free JSON Formatter", "/tools/json-formatter.html"),
        ],
        sources=[
            ("MDN Web Docs: JSON", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON", "JSON syntax and parsing."),
            ("CommonMark Spec", "https://spec.commonmark.org/", "Markdown standardization."),
            ("NIST SP 800-63B", "https://pages.nist.gov/800-63-3/sp800-63b.html", "Authenticator and password guidance."),
            ("Glint AI JSON Formatter", "/tools/json-formatter.html", "Free, browser-private."),
            ("Glint AI Markdown to HTML", "/tools/markdown-to-html.html", "Free converter."),
        ],
        takeaways=[
            "Most 'AI for developers' lists ignore the daily chores: formatting, converting, and secrets.",
            "Glint AI's JSON formatter, Markdown converter, and password generator are free, no signup, and run in your browser.",
            "Local tools (Ollama, Continue) keep your code on your machine — best for proprietary work.",
            "Check the free-tier limits and privacy posture before pasting anything sensitive.",
            "A privacy-first free stack covers most daily work without a credit card.",
        ],
        closing='Start with the free <a href="/tools/json-formatter.html">JSON formatter</a>, <a href="/tools/markdown-to-html.html">Markdown converter</a>, and <a href="/tools/password-generator.html">password generator</a> — no account, no upload.',
    ),
    dict(
        slug="free-ai-tools-teachers",
        title="Free AI Tools for Teachers: 10 Privacy-First Picks",
        description="Discover 10 free AI tools for teachers — lesson plans, rubrics, feedback and integrity checks. Privacy-first, no signup, no student data uploaded. Try free.",
        keywords="free ai tools for teachers, ai tools for educators, best free ai for teachers 2026, ai lesson plan generator free, detect ai writing in student work",
        category="Education",
        accent="#ff2e97",
        readtime=10,
        related=[
            ("How Accurate Are AI Detectors?", "/blog/ai-content-detector-guide.html"),
            ("Private AI Detector Guide", "/blog/private-ai-detector.html"),
            ("AI Detector Comparison", "/blog/ai-content-detector-comparison.html"),
            ("Free AI Tools for Students", "/blog/free-ai-tools-students-2026.html"),
            ("Try the free Grammar Checker", "/tools/grammar-checker.html"),
        ],
        sources=[
            ("UNESCO: AI in Education", "https://www.unesco.org/en/artificial-intelligence/education", "Responsible AI use in education."),
            ("Purdue OWL: Avoiding Plagiarism", "https://owl.purdue.edu/owl/teacher_resources/plagiarism.html", "Academic integrity reference."),
            ("ISTE: AI Guidance", "https://www.iste.org/standards/ai", "Classroom AI and data privacy."),
            ("Glint AI Content Detector", "/tools/ai-content-detector.html", "Private, no upload."),
            ("Glint AI Grammar Checker", "/tools/grammar-checker.html", "Free feedback."),
        ],
        takeaways=[
            "The best free AI tools for teachers protect student privacy first.",
            "Use AI for planning, grading feedback, and differentiation — keep the human judgment.",
            "AI detectors have false positives; never use a score as the sole evidence of cheating.",
            "Browser-based tools process student text locally, so nothing is uploaded.",
            "Pair this with the student toolkit for a matched, privacy-first set.",
        ],
        closing='Check student work fairly with the free <a href="/tools/ai-content-detector.html">AI content detector</a>, and give feedback with the <a href="/tools/grammar-checker.html">grammar checker</a> — both run privately in your browser.',
    ),
    dict(
        slug="ai-meta-description-generator",
        title="AI Meta Description Generator: Free Tool + How to Test",
        description="Use our free AI meta description generator to write 150-160 character snippets, then preview them in Google. No signup. Try it free now.",
        keywords="ai meta description generator, meta description generator free, ai meta tags generator, meta description writer no signup, meta description pixel width 2026",
        category="SEO",
        accent="#a855f7",
        readtime=10,
        related=[
            ("Write Meta Descriptions That Boost CTR", "/blog/meta-description-ctr-guide.html"),
            ("SERP Preview: Write Meta Titles & Descriptions", "/blog/serp-preview-meta-tags.html"),
            ("Best Free SERP Preview Tool", "/blog/best-free-serp-preview-tool.html"),
            ("Try the SERP Preview Tool", "/tools/serp-preview.html"),
            ("Try the Word Counter", "/tools/word-counter.html"),
        ],
        sources=[
            ("Google Search Central: Snippets", "https://developers.google.com/search/docs/appearance/snippet", "Description length and auto-generation."),
            ("Google Search Central: Title Links", "https://developers.google.com/search/docs/appearance/title-link", "Title and description together."),
            ("Moz: Meta Description Best Practices", "https://moz.com/learn/seo/meta-description", "Industry best practices."),
            ("Glint AI SERP Preview", "/tools/serp-preview.html", "Live snippet preview."),
            ("Glint AI Word Counter", "/tools/word-counter.html", "Character and word counts."),
        ],
        takeaways=[
            "An AI meta description generator drafts snippets fast, but pixel width — not just 160 characters — is the real limit.",
            "Generate three variants, preview the snippet, trim to fit, and check uniqueness.",
            "Glint's generator is free, no signup, and includes a live SERP preview.",
            "Judge output by search intent, uniqueness, honesty, and truncation survival.",
            "Don't let Google auto-generate every description — write the important ones.",
        ],
        closing='Generate and preview with the free <a href="/tools/serp-preview.html">SERP preview tool</a>, and verify length with the <a href="/tools/word-counter.html">word counter</a> before you publish.',
    ),
    dict(
        slug="does-google-detect-ai-content",
        title="Does Google Detect AI Content? 2026 Rules Explained",
        description="Does Google detect AI content? Not by detector score. Google targets scaled, unhelpful pages — here's what the 2026 spam policies really say, and a safe workflow.",
        keywords="does google detect ai content, can google detect ai writing, google ai content penalty 2026, is ai content bad for seo, how to humanize ai text for seo",
        category="SEO",
        accent="#ffb020",
        readtime=11,
        related=[
            ("How Accurate Are AI Detectors?", "/blog/ai-content-detector-guide.html"),
            ("AI Detector Comparison", "/blog/ai-content-detector-comparison.html"),
            ("Private AI Detector Guide", "/blog/private-ai-detector.html"),
            ("How to Humanize AI Text", "/blog/humanize-ai-text.html"),
            ("Try the free AI Content Detector", "/tools/ai-content-detector.html"),
        ],
        sources=[
            ("Google: Creating helpful content", "https://developers.google.com/search/docs/fundamentals/creating-helpful-content", "Reward helpful content, regardless of method."),
            ("Google: Spam policies (Scaled content abuse)", "https://developers.google.com/search/docs/essentials/spam-policies", "What actually gets penalized."),
            ("Google: Search Quality Rater Guidelines", "https://www.google.com/search/howsearchworks/our-approach/", "Quality and E-E-A-T signals."),
            ("Glint AI Content Detector", "/tools/ai-content-detector.html", "Private first check."),
            ("Glint AI Humanizer", "/tools/ai-humanizer.html", "Private local edits."),
        ],
        takeaways=[
            "Google does not penalize AI-written text; it penalizes unhelpful, scaled, or manipulative content.",
            "No published evidence that Google runs an AI detector to penalize pages.",
            "AI detectors have false positives and should never be sole proof of misconduct.",
            "A safe workflow: draft with AI, add your expertise, check privately, humanize, edit.",
            "Disclose AI use where required; otherwise focus on helping the reader.",
        ],
        closing='Check a draft privately with the free <a href="/tools/ai-content-detector.html">AI content detector</a>, then smooth flat passages with the <a href="/tools/ai-humanizer.html">AI humanizer</a> — both run in your browser.',
    ),
]

HERO_ALT = {
    "ai-headline-generator": "Glint AI headline generator showing seven title formulas for one blog topic",
    "free-ai-tools-developers": "Comparison of 12 free AI tools for developers by category and signup requirement",
    "free-ai-tools-teachers": "Ten free AI tools for teachers arranged by lesson planning and grading use",
    "ai-meta-description-generator": "AI meta description generator with a 155-character snippet and a SERP preview",
    "does-google-detect-ai-content": "Diagram of how Google evaluates AI content: helpfulness versus scaled content abuse",
}


def faq_jsonld(pairs):
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in pairs],
    }


def build(d, body, faq_pairs, hero_url):
    li_take = "\n".join(f"    <li>{t}</li>" for t in d["takeaways"])
    li_src = "\n".join(f'    <li><a href="{u}" target="_blank" rel="noopener noreferrer">{t}</a> &mdash; {n}.</li>' for t, u, n in d["sources"])
    li_rel = "\n".join(f'    <a href="{u}">&rarr; {t}</a>' for t, u in d["related"])
    vis_faq = "\n".join(f"<p><b>{q}</b> {a}</p>" for q, a in faq_pairs)
    faq_block = (f'<h2>Frequently asked questions</h2>\n{vis_faq}') if faq_pairs else ''
    body = body.replace('<!--FAQ-->', faq_block)
    hero_alt = HERO_ALT.get(d["slug"], d["title"])
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": d["title"], "image": hero_url,
        "description": d["description"],
        "author": {"@type": "Person", "name": "Glint AI Editorial Team",
                   "url": "https://glintai.tools/about/",
                   "sameAs": ["https://www.youtube.com/@glintai", "https://www.tiktok.com/@glintai"]},
        "publisher": {"@type": "Organization", "name": "Glint AI"},
        "datePublished": DATE, "dateModified": DATE,
        "mainEntityOfPage": f"{SITE}/blog/{d['slug']}.html",
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": d["title"], "item": f"{SITE}/blog/{d['slug']}.html"},
        ],
    }
    faq_ld = faq_jsonld(faq_pairs)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{d["title"]}</title>
<meta name="description" content="{d["description"]}" />
<meta name="keywords" content="{d["keywords"]}" />
<meta name="author" content="Glint AI Editorial Team" />
<link rel="canonical" href="{SITE}/blog/{d['slug']}.html" />
<meta property="og:url" content="{SITE}/blog/{d['slug']}.html" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{d["title"]}" />
<meta property="og:description" content="{d["description"]}" />
<meta property="og:image" content="{hero_url}" />
<meta name="twitter:image" content="{hero_url}" />
<meta property="og:image:alt" content="{hero_alt}" />
<meta name="twitter:card" content="summary_large_image" />
<script type="application/ld+json">
{j(article)}
</script>
<script type="application/ld+json">
{j(faq_ld)}
</script>
<script type="application/ld+json">
{j(breadcrumb)}
</script>
<style>
{CSS}
</style>
</head>
<body>
<header class="nav"><div class="wrap nav-inner">
<a class="logo" href="/"><span class="dot">&#10042;</span> Glint AI</a>
<a class="btn" href="/#tools">Try the free tools &rarr;</a>
</div></header>

<div class="wrap">
<span class="cat">{d["category"]}</span>
<h1>{d["h1"]}</h1>
<div class="meta">Updated {DATE} &middot; {d["readtime"]} min read &middot; by Glint AI Editorial Team</div>
<p class="lead">{d["lead"]}</p>
<img src="/blog/assets/{d['slug']}.png" width="1200" height="630" alt="{hero_alt}" loading="eager" fetchpriority="high" class="hero-img" />

<aside class="geo-takeaways" aria-label="Key takeaways">
  <h2>Key takeaways</h2>
  <ul>
{li_take}
  </ul>
</aside>
<div class="content">
{body}
</div>

<div class="rel">
<h3>Keep reading</h3>
{li_rel}
</div>

<p>{d["closing"]}</p>

<section class="geo-sources" aria-label="Sources and further reading">
  <h2>Sources &amp; further reading</h2>
  <ul>
{li_src}
  </ul>
</section>

<div class="author-bio" style="margin:30px 0;padding:18px 20px;border:1px solid #2a2a44;border-radius:14px;background:rgba(18,18,32,.45);">
<h3 style="margin:0 0 6px;font-size:16px;color:#e8e8f5;">About the author</h3>
<p style="margin:0;color:#9aa0c0;font-size:14.5px;">Written by the <b style="color:#e8e8f5;">Glint AI Editorial Team</b> &mdash; writers, developers, and marketers who test every tool hands-on and publish practical, privacy-first guides. <a href="/about/" style="color:#00f0ff;">Learn more about Glint AI &rarr;</a></p>
</div>
</div>
<footer><div class="wrap">&copy; 2026 Glint AI &middot; <a href="/">Home</a> &middot; <a href="/#tools">Tools</a> &middot; <a href="/#blog">Blog</a> &middot; <a href="/about/">About</a></div></footer>
  <script defer src="/analytics.js"></script>
  <script src="/usage.js"></script>
  <script src="/ads.js"></script>
  <script src="/geo.js"></script>
</body>
</html>'''


import sys

# --force rebuilds pages even if the HTML already exists;
# optional slug args restrict the run to those posts only.
FORCE = "--force" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]


def main():
    for d in POSTS:
        if ONLY and d["slug"] not in ONLY:
            continue
        draft = os.path.join(ROOT, "drafts", f"{d['slug']}-2026-09-01.md")
        md = open(draft, encoding="utf-8").read()
        d["h1"] = extract_h1(md)
        faq_pairs = extract_faq(md)
        body = md_to_html(md)
        hero_ok = make_hero(d["slug"], d["accent"], d["title"], d["category"])
        hero_url = f"{SITE}/blog/assets/{d['slug']}.png" if hero_ok else f"{SITE}/blog/assets/og-default.png"
        d["lead"] = body.split('</p>', 1)[0].replace('<p>', '').strip()
        body = body.split('</p>', 1)[1]  # drop the lead copy so it isn't duplicated in .content
        out = os.path.join(BLOG, d["slug"] + ".html")
        if os.path.exists(out) and not FORCE:
            print(f"SKIP (exists): {d['slug']}")
            continue
        with open(out, "w", encoding="utf-8") as f:
            f.write(build(d, body, faq_pairs, hero_url))
        print(f"OK: {d['slug']}  (faq={len(faq_pairs)} faq_pairs, hero={'yes' if hero_ok else 'default'})")


if __name__ == "__main__":
    main()
