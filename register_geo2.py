#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Register the 2nd batch of 5 comparison posts (batch from 2026-08-27):
blog index cards, sitemap URLs. Uses a new marker so it won't double-register.
Emojis are BMP-safe unicode escapes to avoid surrogate write errors.
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# (slug, category, emoji-bmp, title, desc)
NEW = [
    ("best-ai-humanizer-tools-2026", "Writing", "\u2726",
     "Best AI Humanizer Tools in 2026 (Tested for Natural Output)",
     "We ran the leading AI humanizers on the same paragraph to see which sound human."),
    ("best-ai-paraphrasing-tools-2026", "Writing", "\u21bb",
     "Best AI Paraphrasing Tools in 2026 (QuillBot and Beyond)",
     "Paraphrasing tools compared on accuracy, tone control, and privacy."),
    ("best-ai-resume-builder-tools-2026", "Productivity", "\u270e",
     "Best AI Resume Builder Tools in 2026",
     "Rezi, Kickresume, Teal, Resume.io, and free local drafting with Glint AI."),
    ("best-free-pdf-summarizer-tools-2026", "Productivity", "\u25a6",
     "Best Free PDF Summarizer Tools in 2026",
     "Summarize PDFs without uploading to a server — local vs cloud compared."),
    ("best-ai-grammar-checker-2026", "Writing", "\u2713",
     "Best AI Grammar Checker in 2026 (Free and Paid Compared)",
     "Grammarly, ProWritingAid, LanguageTool, and free local alternatives."),
]

# ---------- blog/index.html cards ----------
p = os.path.join(ROOT, "blog", "index.html")
with open(p, encoding="utf-8") as f:
    html = f.read()
marker = "<!-- GEO-NEW-POSTS-2 -->"
if marker not in html:
    cards = "\n".join(
        f'        <a class="post" href="blog/{slug}.html"><div class="thumb">{emoji}</div>'
        f'<div class="body"><div class="cat">{cat}</div><h3>{title}</h3>'
        f'<p>{desc}</p></div></a>' for slug, cat, emoji, title, desc in NEW)
    block = f"<!-- {marker} -->\n" + cards + "\n"
    html = html.replace("</a>\n  </div>\n  </div></section>", "</a>\n" + block + "  </div>\n  </div></section>", 1)
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    print("blog/index.html: 5 cards added")
else:
    print("blog/index.html: SKIP (already done)")

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
