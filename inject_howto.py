#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inject HowTo JSON-LD into every tool landing page (tools/*.html, except
tools/index.html). Steps are extracted from the existing <section class="how">
<ol><li> markup so the schema mirrors real on-page instructions (no invented
steps). Idempotent via the <!-- GEO-HOWTO --> marker.
"""
import os, re, json, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(ROOT, "tools")
MARKER = "<!-- GEO-HOWTO -->"

def strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()

count = 0
skip = 0
for f in sorted(glob.glob(os.path.join(TOOLS, "*.html"))):
    name = os.path.basename(f)
    if name == "index.html":
        continue
    html = open(f, encoding="utf-8").read()
    if MARKER in html:
        skip += 1
        continue
    m = re.search(r'class="how">(.*?)</section>', html, re.S)
    if not m:
        print(f"SKIP (no how-section): {name}")
        continue
    how = m.group(1)
    h2 = re.search(r"<h2>(.*?)</h2>", how, re.S)
    title = strip_tags(h2.group(1)) if h2 else "How to use this tool"
    ol = re.search(r"<ol>(.*?)</ol>", how, re.S)
    if not ol:
        print(f"SKIP (no ol): {name}")
        continue
    lis = re.findall(r"<li>(.*?)</li>", ol.group(1), re.S)
    if not lis:
        print(f"SKIP (no li): {name}")
        continue
    steps = []
    for i, li in enumerate(lis, 1):
        text = strip_tags(li)
        name_step = text if len(text) <= 60 else text[:57].rsplit(" ", 1)[0] + "..."
        steps.append({
            "@type": "HowToStep",
            "position": i,
            "name": name_step,
            "text": text,
        })
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": title,
        "step": steps,
    }
    block = f'{MARKER}\n<script type="application/ld+json">\n{json.dumps(howto, ensure_ascii=False)}\n</script>\n'
    # insert right before </head>
    if "</head>" not in html:
        print(f"SKIP (no </head>): {name}")
        continue
    html = html.replace("</head>", block + "</head>", 1)
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(html)
    count += 1
    print(f"OK: {name} ({len(steps)} steps)")

print(f"\nDone. Injected HowTo into {count} pages, skipped {skip} already-done.")
