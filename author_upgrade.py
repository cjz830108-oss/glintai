# -*- coding: utf-8 -*-
"""Upgrade blog author from a generic Organization to a Person entity (GEO/E-E-A-T),
and append a visible author bio box. Idempotent — safe to re-run."""
import os, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(ROOT, 'blog', '*.html')))

AUTHOR_OLD = '''  "author": {
    "@type": "Organization",
    "name": "Glint AI"
  },'''
AUTHOR_NEW = '''  "author": {
    "@type": "Person",
    "name": "Glint AI Editorial Team",
    "url": "https://glintai.tools/about/",
    "sameAs": [
      "https://www.youtube.com/@glintai",
      "https://www.tiktok.com/@glintai"
    ]
  },'''

AUTHOR_OLD_ONE = '"author":{"@type":"Organization","name":"Glint AI"}'
AUTHOR_NEW_ONE = ('"author":{"@type":"Person","name":"Glint AI Editorial Team",'
                  '"url":"https://glintai.tools/about/",'
                  '"sameAs":["https://www.youtube.com/@glintai","https://www.tiktok.com/@glintai"]}')

META_OLD = '<meta name="author" content="Glint AI" />'
META_NEW = '<meta name="author" content="Glint AI Editorial Team" />'

BYLINE_OLD = 'by Glint AI<'
BYLINE_NEW = 'by Glint AI Editorial Team<'

BIO = ('''
<div class="author-bio" style="margin:30px 0;padding:18px 20px;border:1px solid #2a2a44;border-radius:14px;background:rgba(18,18,32,.45);">
<h3 style="margin:0 0 6px;font-size:16px;color:#e8e8f5;">About the author</h3>
<p style="margin:0;color:#9aa0c0;font-size:14.5px;">Written by the <b style="color:#e8e8f5;">Glint AI Editorial Team</b> &mdash; writers, developers, and marketers who test every tool hands-on and publish practical, privacy-first guides. <a href="/about/" style="color:#00f0ff;">Learn more about Glint AI &rarr;</a></p>
</div>
''')

n_author = n_meta = n_byline = n_bio = 0
for f in files:
    html = open(f, 'r', encoding='utf-8').read()
    changed = False
    if AUTHOR_OLD in html:
        html = html.replace(AUTHOR_OLD, AUTHOR_NEW, 1)
        n_author += 1; changed = True
    if AUTHOR_OLD_ONE in html:
        html = html.replace(AUTHOR_OLD_ONE, AUTHOR_NEW_ONE, 1)
        n_author += 1; changed = True
    if META_OLD in html and 'content="Glint AI Editorial Team"' not in html:
        html = html.replace(META_OLD, META_NEW, 1)
        n_meta += 1; changed = True
    if BYLINE_OLD in html and BYLINE_NEW not in html:
        html = html.replace(BYLINE_OLD, BYLINE_NEW)
        n_byline += 1; changed = True
    if 'class="author-bio"' not in html and '<footer>' in html:
        idx = html.rfind('<footer>')
        html = html[:idx] + BIO + html[idx:]
        n_bio += 1; changed = True
    if changed:
        open(f, 'w', encoding='utf-8').write(html)

print('blog files scanned :', len(files))
print('  author -> Person :', n_author)
print('  meta author      :', n_meta)
print('  byline updated   :', n_byline)
print('  bio box added    :', n_bio)
print('done')
