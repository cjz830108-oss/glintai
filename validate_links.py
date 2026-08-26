# -*- coding: utf-8 -*-
"""Validate that every internal link/src in the site resolves to a real file."""
import os, re, glob

ROOT = "."
files = ["index.html"] + glob.glob("tools/*.html") + glob.glob("blog/*.html") \
        + glob.glob("extension/*.html") + glob.glob("resources/*.html") \
        + glob.glob("ai-tools/*.html") + glob.glob("privacy/*.html") \
        + glob.glob("terms/*.html") + glob.glob("dashboard/*.html") + ["404.html"]

def resolve(path):
    # strip query/hash
    path = path.split("#")[0].split("?")[0]
    if path == "" or path.startswith("http") or path.startswith("//") or path == "/api/sb":
        return None  # external or runtime — skip
    if path == "/":
        return "index.html"
    if path.endswith("/"):
        return path.lstrip("/") + "index.html"
    return path.lstrip("/")

problems = []
checked = 0
for f in files:
    html = open(f, encoding="utf-8").read()
    refs = re.findall(r'(?:href|src)="(/[^"]*)"', html)
    for r in refs:
        tgt = resolve(r)
        if tgt is None:
            continue
        checked += 1
        if not os.path.exists(tgt):
            problems.append((f, r, tgt))

print("Files scanned:", len(files))
print("Internal refs checked:", checked)
if problems:
    print("DEAD LINKS:")
    for f, r, tgt in problems:
        print("  %s -> %s  (missing %s)" % (f, r, tgt))
else:
    print("OK: no dead internal links.")
