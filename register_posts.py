#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Register the 5 new comparison/list posts: blog index cards, sitemap URLs,
llms.txt section, and fix a pre-existing wrong markdown slug in llms.txt."""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

NEW = [
    ("best-ai-writing-tools-marketers-2026", "Writing", "\u270e",
     "Best Free AI Writing Tools for Marketers in 2026",
     "The free AI writing stack that handles the repetitive 80% of marketing writing."),
    ("chatgpt-vs-claude-vs-gemini-writing", "Writing", "\u26a1",
     "ChatGPT vs Claude vs Gemini: Which Should You Write With?",
     "How the three frontier models compare for everyday content work."),
    ("free-vs-pro-ai-tools", "Productivity", "$",
     "Free vs Pro AI Tools: When Should You Actually Upgrade?",
     "A clear framework for when paying for AI actually pays off."),
    ("ai-content-detector-comparison", "Writing", "\u2315",
     "AI Content Detector Comparison: Which One Is Most Accurate?",
     "How detectors work, what they miss, and how to use them honestly."),
    ("ai-tools-content-creator-starter-list", "Productivity", "\u2699",
     "10 AI Tools Every Content Creator Needs",
     "The ~10 tools that cover research, writing, design, and distribution."),
]

# ---------- blog/index.html cards ----------
p = os.path.join(ROOT, "blog", "index.html")
with open(p, encoding="utf-8") as f:
    html = f.read()
marker = "<!-- GEO-NEW-POSTS -->"
if marker not in html:
    cards = "\n".join(
        f'        <a class="post" href="blog/{slug}.html"><div class="thumb">{emoji}</div>'
        f'<div class="body"><div class="cat">{cat}</div><h3>{title}</h3>'
        f'<p>{desc}</p></div></a>' for slug, cat, emoji, title, desc in NEW)
    block = f"<!-- {marker} -->\n" + cards + "\n  "
    # insert before the grid-close (</a></div> immediately preceding </div></section>)
    html = html.replace("</a></div>\n  </div></section>",
                        "</a>\n" + block + "</div>\n  </div></section>", 1)
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

# ---------- llms.txt: fix wrong slug + add Comparisons section ----------
p = os.path.join(ROOT, "llms.txt")
with open(p, encoding="utf-8") as f:
    llms = f.read()
fixed = False
if "tools/markdown-to.html" in llms:
    llms = llms.replace("tools/markdown-to.html", "tools/markdown-to-html.html")
    fixed = True
sec_marker = "## Comparisons & Lists"
if sec_marker not in llms:
    lines = [
        "",
        "## Comparisons & Lists",
        "- [Best Free AI Writing Tools for Marketers](https://glintai.tools/blog/best-ai-writing-tools-marketers-2026.html): The free stack for marketing writing.",
        "- [ChatGPT vs Claude vs Gemini](https://glintai.tools/blog/chatgpt-vs-claude-vs-gemini-writing.html): Which model to write with.",
        "- [Free vs Pro AI Tools](https://glintai.tools/blog/free-vs-pro-ai-tools.html): When upgrading pays off.",
        "- [AI Content Detector Comparison](https://glintai.tools/blog/ai-content-detector-comparison.html): Which detector is most accurate.",
        "- [10 AI Tools for Content Creators](https://glintai.tools/blog/ai-tools-content-creator-starter-list.html): The complete starter list.",
        "",
    ]
    llms = llms.replace("\n## Resources", "\n".join(lines) + "## Resources", 1)
    with open(p, "w", encoding="utf-8") as f:
        f.write(llms)
    print("llms.txt: Comparisons section added" + (" + markdown slug fixed" if fixed else ""))
else:
    if fixed:
        with open(p, "w", encoding="utf-8") as f:
            f.write(llms)
        print("llms.txt: markdown slug fixed")
    else:
        print("llms.txt: SKIP (section exists, slug ok)")
