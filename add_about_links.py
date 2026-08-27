# -*- coding: utf-8 -*-
"""Add an "About" internal link across the whole site for GEO internal linking.
Idempotent per-marker; skips files that don't contain the anchor or already
have the link. Handles 4 footer/nav variants found in the codebase."""
import os, glob

ROOT = os.path.dirname(os.path.abspath(__file__))

# (anchor, replacement) — replacement adds the About link right after the anchor.
PATTERNS = [
    # nav (homepage, /tools, make_pages pages)
    ('<a href="/extension/">Extension</a>',
     '<a href="/extension/">Extension</a><a href="/about/">About</a>'),
    # footer "Company" column (index, /tools, make_pages pages)
    ('<a href="/terms/">Terms</a></div>',
     '<a href="/terms/">Terms</a><a href="/about/">About</a></div>'),
    # blog post footer
    ('· <a href="/#blog">Blog</a></div></footer>',
     '· <a href="/#blog">Blog</a> · <a href="/about/">About</a></div></footer>'),
    # standalone tool-page footer
    ('· <a href="/#pricing">Pricing</a></p>',
     '· <a href="/#pricing">Pricing</a> · <a href="/about/">About</a></p>'),
]

GUARD = '/about/">About'
files = ['index.html', '404.html']
files += [os.path.join('tools', 'index.html')]
files += sorted(glob.glob(os.path.join(ROOT, 'tools', '*.html')))
files += sorted(glob.glob(os.path.join(ROOT, 'blog', '*.html')))
for d in ['extension', 'resources', 'ai-tools', 'privacy', 'terms', 'dashboard', 'about']:
    p = os.path.join(ROOT, d, 'index.html')
    if os.path.exists(p): files.append(p)

total = 0
for f in files:
    if not os.path.exists(f): continue
    html = open(f, 'r', encoding='utf-8').read()
    if GUARD in html:
        continue
    orig = html
    for anchor, repl in PATTERNS:
        if anchor in html:
            html = html.replace(anchor, repl, 1)
    if html != orig:
        open(f, 'w', encoding='utf-8').write(html)
        total += 1
        print('  + About link:', os.path.relpath(f, ROOT))
print('files updated:', total)
print('done')
