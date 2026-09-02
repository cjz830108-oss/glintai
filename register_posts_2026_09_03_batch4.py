import re, os

SITE = "https://glintai.tools"
POSTS = [
    dict(slug="ai-tools-for-consultants-2026", thumb="thumb-ai-tools-for-consultants-2026.png", cat="Consulting",
         card="Free AI Tools for Consultants",
         blurb="Summarize, rewrite, and proofread client work without leaking privileged text.",
         alt="Cyberpunk illustration for the free AI tools for consultants guide",
         llm="Free, no-signup AI tools for consultants — summarize, rewrite, and proofread in the browser so client material never leaves the device."),
    dict(slug="ai-tools-for-ecommerce-2026", thumb="thumb-ai-tools-for-ecommerce-2026.png", cat="Ecommerce",
         card="Free AI Tools for Ecommerce",
         blurb="Product copy, image backgrounds, JSON data, and SERP previews with zero budget.",
         alt="Cyberpunk illustration for the free AI tools for ecommerce guide",
         llm="Free, no-signup AI tools for ecommerce — product copy, background removal, JSON formatting, hashtags, and SERP previews."),
    dict(slug="ai-tools-for-lawyers-2026", thumb="thumb-ai-tools-for-lawyers-2026.png", cat="Legal",
         card="Free AI Tools for Lawyers",
         blurb="Faster drafting and summarization that keep client privilege intact.",
         alt="Cyberpunk illustration for the free AI tools for lawyers guide",
         llm="Free, no-signup AI tools for lawyers and paralegals — summarize, rewrite, and proofread in the browser without risking privilege."),
    dict(slug="ai-tools-for-real-estate-2026", thumb="thumb-ai-tools-for-real-estate-2026.png", cat="Real Estate",
         card="Free AI Tools for Real Estate",
         blurb="Listing descriptions, photo cleanup, agent bios, and local SEO previews.",
         alt="Cyberpunk illustration for the free AI tools for real estate guide",
         llm="Free, no-signup AI tools for real estate agents — listing copy, background removal, bio generation, and local SEO previews."),
    dict(slug="ai-tools-for-nonprofits-2026", thumb="thumb-ai-tools-for-nonprofits-2026.png", cat="Nonprofit",
         card="Free AI Tools for Nonprofits",
         blurb="Grant copy, donor emails, and impact reports on a zero-dollar budget.",
         alt="Cyberpunk illustration for the free AI tools for nonprofits guide",
         llm="Free, no-signup AI tools for nonprofits — grant proposals, donor emails, impact reports, and social posts."),
    dict(slug="ai-tools-for-podcasters-2026", thumb="thumb-ai-tools-for-podcasters-2026.png", cat="Podcasting",
         card="Free AI Tools for Podcasters",
         blurb="Episode titles, show notes, chapter timestamps, and guest bios.",
         alt="Cyberpunk illustration for the free AI tools for podcasters guide",
         llm="Free, no-signup AI tools for podcasters — titles, show notes, chapter timestamps, guest bios, and transcript-to-blog."),
    dict(slug="best-free-word-counter-tools-2026", thumb="thumb-best-free-word-counter-tools-2026.png", cat="Writing",
         card="Best Free Word Counter Tools 2026",
         blurb="Tested on real drafts — counts, reading time, density, and character limits.",
         alt="Cyberpunk illustration for the best free word counter tools guide",
         llm="The best free word counter tools in 2026, tested on real drafts — counts, reading time, keyword density, and character limits, with a privacy-first browser pick."),
    dict(slug="best-free-password-generator-tools-2026", thumb="thumb-best-free-password-generator-tools-2026.png", cat="Security",
         card="Best Free Password Generator Tools 2026",
         blurb="Ranked by one rule: client-side generation, no upload, no signup.",
         alt="Cyberpunk illustration for the best free password generator tools guide",
         llm="The best free password generator tools in 2026, ranked by client-side generation — strong passwords and API keys created in the browser."),
]

def card_html(p, base):
    return (f'        <a class="post" href="{base}blog/{p["slug"]}.html">'
            f'<div class="thumb"><img src="{base}blog/assets/{p["thumb"]}" alt="{p["alt"]}" '
            f'loading="lazy" width="480" height="297"></div>'
            f'<div class="body"><div class="cat">{p["cat"]}</div>'
            f'<h3>{p["card"]}</h3><p>{p["blurb"]}</p></div></a>')

def inject_after_bloggrid(path, base):
    s = open(path, encoding="utf-8").read()
    if all((p["slug"] + ".html") in s for p in POSTS):
        print("SKIP (all present):", path); return
    m = re.search(r'( *)<div class="blog-grid">\s*\n', s)
    if not m:
        print("NO blog-grid in", path); return
    ins = m.end()
    added = 0
    for p in POSTS:
        if p["slug"] + ".html" in s:
            continue
        card = card_html(p, base) + "\n"
        s = s[:ins] + card + s[ins:]
        ins += len(card)
        added += 1
    open(path, "w", encoding="utf-8").write(s)
    print("OK cards ->", path, "added:", added)

# 1) blog index (absolute paths)  2) homepage (relative paths)
inject_after_bloggrid("blog/index.html", "/")
inject_after_bloggrid("index.html", "")

# 3) sitemap.xml
sm = open("sitemap.xml", encoding="utf-8").read()
added = 0
for p in POSTS:
    url = f"{SITE}/blog/{p['slug']}.html"
    if url in sm:
        continue
    entry = (f"  <url>\n    <loc>{url}</loc>\n"
             f"    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n")
    sm = sm.replace("</urlset>", entry + "</urlset>")
    added += 1
if added:
    open("sitemap.xml", "w", encoding="utf-8").write(sm)
print("OK sitemap entries:", added, "total urls:", sm.count("<url>"))

# 4) llms.txt
ll = open("llms.txt", encoding="utf-8").read()
added = 0
for p in POSTS:
    url = f"{SITE}/blog/{p['slug']}.html"
    if url in ll:
        continue
    line = f"- [{p['card']}]({url}): {p['llm']}\n"
    idx = ll.find("\n## Resources")
    ll = ll[:idx+1] + line + ll[idx+1:]
    added += 1
if added:
    open("llms.txt", "w", encoding="utf-8").write(ll)
print("OK llms.txt entries:", added, "blog refs:", ll.count("/blog/"))
