#!/usr/bin/env python3
"""Fix two artifacts introduced by the first geo_content.py run:
1) stray '<div ' before '<!-- GEO-SOURCES -->' (broken wrapper)
2) wrong markdown tool slug '/tools/markdown-to.html' -> '/tools/markdown-to-html.html'
"""
import os

BLOG = "blog"
S = "best-free-json-formatter grammarly-alternative-free quillbot-alternative-free private-ai-detector free-grammar-checker-no-signup humanize-ai-text best-free-serp-preview-tool best-free-markdown-to-html-converter".split()

n_wrap = 0
n_link = 0
for slug in S:
    p = os.path.join(BLOG, f"{slug}.html")
    with open(p, "r", encoding="utf-8") as f:
        h = f.read()
    if "<div <!-- GEO-SOURCES -->" in h:
        h = h.replace("<div <!-- GEO-SOURCES -->", "<!-- GEO-SOURCES -->", 1)
        n_wrap += 1
    if "/tools/markdown-to.html" in h:
        h = h.replace("/tools/markdown-to.html", "/tools/markdown-to-html.html")
        n_link += 1
    with open(p, "w", encoding="utf-8") as f:
        f.write(h)

print(f"wrappers fixed: {n_wrap}")
print(f"markdown links fixed: {n_link}")
