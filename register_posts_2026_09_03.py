import re, os

SITE = "https://glintai.tools"
POSTS = [
    dict(slug="ai-headline-generator", thumb="thumb-headline.png", cat="Writing",
         card="AI Headline Generator",
         blurb="Seven reusable formulas to write titles that earn the click.",
         alt="Cyberpunk illustration for the free AI headline generator guide",
         llm="An AI headline generator that drafts blog, YouTube, and email titles with seven reusable, CTR-tested formulas — free, no signup, with a live SERP preview."),
    dict(slug="ai-meta-description-generator", thumb="thumb-metadesc.png", cat="SEO",
         card="AI Meta Description Generator",
         blurb="Write 150-160 character snippets, then preview them in Google.",
         alt="Cyberpunk illustration for the free AI meta description generator guide",
         llm="A free AI meta description generator that drafts 150-160 character snippets and previews them in Google — no signup, with pixel-width guidance."),
    dict(slug="does-google-detect-ai-content", thumb="thumb-googleai.png", cat="SEO",
         card="Does Google Detect AI Content?",
         blurb="What the 2026 spam policies really say — and a safe workflow.",
         alt="Cyberpunk illustration explaining how Google evaluates AI content",
         llm="Does Google detect AI content? Not by detector score — Google targets scaled, unhelpful pages. Here is what the 2026 spam policies say and a safe workflow."),
    dict(slug="free-ai-tools-developers", thumb="thumb-dev.png", cat="Developers",
         card="Free AI Tools for Developers",
         blurb="12 no-signup picks for code review, JSON, Markdown, and key safety.",
         alt="Cyberpunk illustration for the free AI tools for developers guide",
         llm="Twelve free AI tools for developers in 2026 — code review, JSON, Markdown, and key safety — no signup, browser-private."),
    dict(slug="free-ai-tools-teachers", thumb="thumb-teachers.png", cat="Education",
         card="Free AI Tools for Teachers",
         blurb="10 privacy-first picks for lesson plans, rubrics, and feedback.",
         alt="Cyberpunk illustration for the free AI tools for teachers guide",
         llm="Ten free, privacy-first AI tools for teachers — lesson plans, rubrics, feedback, and integrity checks — no signup, no student data uploaded."),
    dict(slug="free-ai-rewriter-no-signup", thumb="thumb-rewriter.png", cat="Writing",
         card="Free AI Rewriter (No Signup)",
         blurb="Reword text for clarity, tone, or originality — no upload.",
         alt="Cyberpunk illustration for the free AI rewriter guide",
         llm="A free AI rewriter that rewords text for clarity, tone, or originality without losing meaning — no signup, browser-private, no upload."),
    dict(slug="youtube-description-generator", thumb="thumb-yt-desc.png", cat="Video",
         card="YouTube Description Generator",
         blurb="Generate video descriptions with timestamps, links, and SEO fields.",
         alt="Cyberpunk illustration for the free YouTube description generator guide",
         llm="A free YouTube description generator that drafts hooks, timestamps, links, and SEO fields — no signup, browser-private, with a snippet preview."),
    dict(slug="free-ai-seo-tools-for-beginners", thumb="thumb-seo-begin.png", cat="SEO",
         card="Free AI SEO Tools for Beginners",
         blurb="SERP preview, meta tags, and content checks — no budget needed.",
         alt="Cyberpunk illustration for the free AI SEO tools for beginners guide",
         llm="A free, no-signup SEO toolkit for beginners — SERP preview, meta tags, content checks, and keyword-friendly writing, all browser-private."),
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
