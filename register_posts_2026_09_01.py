import re, os

SITE = "https://glintai.tools"
POSTS = [
    dict(slug="ai-headline-generator", thumb="thumb-headline.png", cat="Writing",
         card="AI Headline Generator: Titles That Get Clicks",
         blurb="Score headlines before you publish using clarity, curiosity and CTR formulas.",
         alt="Cyberpunk illustration for the AI headline generator guide",
         llm="Generate blog, YouTube and email headlines with a free AI headline generator. No signup, runs privately in your browser, with CTR-tested formulas you can check before publishing."),
    dict(slug="free-ai-tools-developers", thumb="thumb-devtools.png", cat="Developers",
         card="12 Free AI Tools for Developers (No Signup)",
         blurb="Coding assistants, JSON formatting, Markdown and key safety — all browser-private.",
         alt="Cyberpunk illustration for the free AI tools for developers guide",
         llm="Twelve free AI tools developers actually use in 2026, covering coding assistants, JSON formatting, Markdown conversion and API key safety. No signup, nothing uploaded."),
    dict(slug="free-ai-tools-teachers", thumb="thumb-teachers.png", cat="Education",
         card="10 Free AI Tools for Teachers (Privacy-First)",
         blurb="Plan lessons and give writing feedback without uploading student work anywhere.",
         alt="Cyberpunk illustration for the free AI tools for teachers guide",
         llm="Ten free AI tools for planning lessons, giving writing feedback and checking student work, chosen for privacy-first handling with no account and no student data uploaded."),
    dict(slug="ai-meta-description-generator", thumb="thumb-metadesc.png", cat="SEO",
         card="AI Meta Description Generator + Snippet Testing",
         blurb="Write 150-160 character snippets, then preview them exactly as Google shows them.",
         alt="Cyberpunk illustration for the AI meta description generator guide",
         llm="Generate meta descriptions that earn clicks, keep them inside the 150-160 character range, and preview the result in a SERP simulator before you ship the page."),
    dict(slug="does-google-detect-ai-content", thumb="thumb-gdetect.png", cat="SEO",
         card="Can Google Detect AI Content in 2026?",
         blurb="What the spam policies really target, and where detector scores mislead you.",
         alt="Cyberpunk illustration for the Google AI content detection guide",
         llm="Google does not ban AI content, but scaled and unhelpful pages get hit. What the spam policies really target, how detection actually works, and a safe 2026 workflow."),
]

def card_html(p, base):
    return (f'        <a class="post" href="{base}blog/{p["slug"]}.html">'
            f'<div class="thumb"><img src="{base}blog/assets/{p["thumb"]}" alt="{p["alt"]}" '
            f'loading="lazy" width="480" height="297"></div>'
            f'<div class="body"><div class="cat">{p["cat"]}</div>'
            f'<h3>{p["card"]}</h3><p>{p["blurb"]}</p></div></a>')

def inject_after_bloggrid(path, base):
    s = open(path, encoding="utf-8").read()
    if POSTS[0]["slug"] + ".html" in s:
        print("SKIP (already registered):", path); return
    m = re.search(r'( *)<div class="blog-grid">\s*\n', s)
    if not m:
        print("NO blog-grid in", path); return
    ins = m.end()
    block = "".join(card_html(p, base) + "\n" for p in POSTS)
    s = s[:ins] + block + s[ins:]
    open(path, "w", encoding="utf-8").write(s)
    print("OK cards ->", path)

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
