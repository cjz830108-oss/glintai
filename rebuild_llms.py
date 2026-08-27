#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild llms.txt with the FULL blog index (every post, grouped by category),
extracted automatically from each blog HTML's <title>, meta description, and
<span class="cat">. Keeps the Tools and Resources sections intact.
This closes the GEO gap where llms.txt only listed ~17 of 43 posts.
"""
import os, re, glob
from collections import OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))
BLOG = os.path.join(ROOT, "blog")

posts = []
for f in sorted(glob.glob(os.path.join(BLOG, "*.html"))):
    name = os.path.basename(f)
    if name == "index.html":
        continue
    html = open(f, encoding="utf-8").read()
    slug = name[:-5]
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    d = re.search(r'<meta name="description" content="(.*?)"', html)
    c = re.search(r'<span class="cat">(.*?)</span>', html)
    title = t.group(1).strip() if t else slug
    desc = d.group(1).strip() if d else ""
    cat = c.group(1).strip() if c else "Guides"
    posts.append((cat, title, slug, desc))

groups = OrderedDict()
for cat, title, slug, desc in posts:
    groups.setdefault(cat, []).append((title, slug, desc))

lines = ["## Blog & Guides"]
for cat in sorted(groups.keys()):
    lines.append(f"### {cat}")
    for title, slug, desc in groups[cat]:
        lines.append(f"- [{title}](https://glintai.tools/blog/{slug}.html): {desc}")
    lines.append("")
blog_block = "\n".join(lines)

TOOLS = """## Tools
- [AI Text Summarizer](https://glintai.tools/tools/ai-text-summarizer.html): Summarize long articles and docs in your browser, with no upload.
- [Word & Readability Analyzer](https://glintai.tools/tools/word-readability-analyzer.html): Check reading ease, grade level, and word counts.
- [Markdown to HTML](https://glintai.tools/tools/markdown-to-html.html): Convert Markdown to clean HTML instantly.
- [JSON Formatter](https://glintai.tools/tools/json-formatter.html): Pretty-print and validate JSON client-side, with no server.
- [Password & Key Generator](https://glintai.tools/tools/password-generator.html): Generate strong passwords and API keys locally.
- [YouTube Title & Hook Generator](https://glintai.tools/tools/youtube-title-generator.html): Brainstorm click-worthy titles and hooks.
- [Hashtag Generator](https://glintai.tools/tools/hashtag-generator.html): Build platform-ready hashtag sets.
- [SERP & Meta Preview](https://glintai.tools/tools/serp-preview.html): Preview how titles and meta appear in search results.
- [Word & Character Counter](https://glintai.tools/tools/word-counter.html): Count words, characters, and reading time.
- [AI Humanizer](https://glintai.tools/tools/ai-humanizer.html): Light, local edits that make AI drafts read more naturally.
- [AI Content Detector](https://glintai.tools/tools/ai-content-detector.html): Estimate how likely text looks AI-generated.
- [Paraphraser](https://glintai.tools/tools/paraphraser.html): Reword text while keeping the meaning.
- [PDF Summarizer](https://glintai.tools/tools/pdf-summarizer.html): Summarize PDFs in the browser.
- [Grammar Checker](https://glintai.tools/tools/grammar-checker.html): Catch grammar and clarity issues.
- [Bio & Resume Generator](https://glintai.tools/tools/bio-resume-generator.html): Draft bios and resume bullets.
- [Background Remover](https://glintai.tools/tools/background-remover.html): Remove image backgrounds locally."""

RESOURCES = """## Resources
- [All Tools](https://glintai.tools/tools/): The full free toolkit.
- [Blog](https://glintai.tools/blog/): Guides and comparisons.
- [Resources](https://glintai.tools/resources/): Templates and playbooks.
- [AI Tool Reviews](https://glintai.tools/ai-tools/): Hand-picked affiliate recommendations.
- [Chrome Extension](https://glintai.tools/extension/): Coming soon, join the waitlist.
- [About Glint AI](https://glintai.tools/about/): Who we are and our privacy stance.
- [Pricing](https://glintai.tools/#pricing): Free, Pro, and Team plans."""

HEADER = """# Glint AI

> Glint AI is the everyday AI toolkit for creators and marketers: 16 free, privacy-first, browser-based AI tools to write better, create faster, and grow smarter. Free tools need no signup; Pro ($9/mo) unlocks higher usage. The site is built to be an asset you own — no tracking cookies, no server-side processing of your text."""

out = HEADER + "\n\n" + TOOLS + "\n\n" + blog_block + "\n\n" + RESOURCES + "\n"
with open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8") as f:
    f.write(out)
print(f"llms.txt rebuilt: {len(posts)} blog posts across {len(groups)} categories")
