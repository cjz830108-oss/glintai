#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Register the 3rd batch of 5 comparison posts (2026-08-29):
blog index cards + sitemap URLs. Uses a NEW marker (GEO-NEW-POSTS-3) so it
won't double-register and won't collide with batch 2's marker.
Emojis are explicit non-BMP code points (utf-8 safe).
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# (slug, category, emoji, title, desc)
NEW = [
    ("best-ai-text-summarizer-tools-2026", "Productivity", "\U0001F4DD",
     "Best AI Text Summarizer Tools in 2026 (Free & Accurate)",
     "We compare the leading AI text summarizers on accuracy, speed, and privacy."),
    ("best-reading-ease-analyzer-tools-2026", "Writing", "\U0001F4CA",
     "Best Reading Ease & Readability Checkers in 2026",
     "Glint AI Reading Ease, Hemingway, Readable, and Grammarly — scored and compared."),
    ("best-youtube-title-generator-tools-2026", "Productivity", "\U0001F3AC",
     "Best YouTube Title & Hook Generators in 2026",
     "Glint AI, TubeBuddy, VidIQ, and CoSchedule compared on CTR, keywords, and workflow."),
    ("best-background-remover-tools-2026", "Design", "\U0001F5BC",
     "Best Background Remover Tools in 2026 (Free & Pro)",
     "Glint AI, Remove.bg, Adobe Express, Canva, and PhotoRoom compared on quality and privacy."),
    ("best-hashtag-generator-tools-2026", "Productivity", "\U0001F511",
     "Best Hashtag Generator Tools in 2026 (TikTok, Instagram, YouTube)",
     "Glint AI, Later, All Hashtag, and RiteTag compared on reach, relevance, and workflow."),
]

# ---------- blog/index.html cards ----------
p = os.path.join(ROOT, "blog", "index.html")
with open(p, encoding="utf-8") as f:
    html = f.read()
marker = "<!-- GEO-NEW-POSTS-3 -->"
if marker in html:
    print("blog/index.html: SKIP (already done)")
else:
    anchor = "<!-- GEO-NEW-POSTS-2 -->"
    if anchor not in html:
        print("blog/index.html: ERROR anchor missing, abort")
    else:
        cards = "\n".join(
            f'        <a class="post" href="blog/{slug}.html"><div class="thumb">{emoji}</div>'
            f'<div class="body"><div class="cat">{cat}</div><h3>{title}</h3>'
            f'<p>{desc}</p></div></a>' for slug, cat, emoji, title, desc in NEW)
        block = cards + "\n" + f"<!-- {marker} -->\n"
        html = html.replace(anchor, block + anchor, 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)
        print("blog/index.html: 5 cards added before GEO-NEW-POSTS-2")

# ---------- sitemap.xml URLs ----------
p = os.path.join(ROOT, "sitemap.xml")
with open(p, encoding="utf-8") as f:
    sm = f.read()
need = False
add = ""
for slug, *_ in NEW:
    if f"blog/{slug}.html" not in sm:
        need = True
        add += (
            f"  <url>\n"
            f"    <loc>https://glintai.tools/blog/{slug}.html</loc>\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>0.8</priority>\n"
            f"  </url>\n")
if need and "</urlset>" in sm:
    sm = sm.replace("</urlset>", add + "</urlset>", 1)
    with open(p, "w", encoding="utf-8") as f:
        f.write(sm)
    print("sitemap.xml: 5 URLs added")
else:
    print("sitemap.xml: SKIP (already present or no </urlset>)")
