# -*- coding: utf-8 -*-
"""Add new indexable pages to sitemap.xml and private disallows to robots.txt."""

# ---- sitemap ----
sm = open("sitemap.xml", encoding="utf-8").read()
new_urls = """  <url>
    <loc>https://glintai.tools/tools/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://glintai.tools/extension/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://glintai.tools/resources/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://glintai.tools/ai-tools/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://glintai.tools/privacy/</loc>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://glintai.tools/terms/</loc>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
"""
anchor = "\n  <url>\n    <loc>https://glintai.tools/tools/ai-text-summarizer.html</loc>"
assert anchor in sm, "sitemap anchor not found"
sm = sm.replace(anchor, "\n" + new_urls.rstrip("\n") + anchor, 1)
open("sitemap.xml", "w", encoding="utf-8").write(sm)
print("sitemap URLs:", sm.count("<loc>"))

# ---- robots ----
rb = open("robots.txt", encoding="utf-8").read()
if "Disallow" not in rb:
    rb = rb.rstrip() + "\n\n# Private / build paths\nDisallow: /dashboard/\nDisallow: /api/\n"
    open("robots.txt", "w", encoding="utf-8").write(rb)
print("robots.txt updated:")
print(rb)
