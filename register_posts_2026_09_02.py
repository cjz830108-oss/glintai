import re, os

SITE = "https://glintai.tools"
POSTS = [
    dict(slug="ai-tools-for-fiction-writers-2026", thumb="thumb-fiction.png", cat="Writing",
         card="Free AI Tools for Fiction Writers",
         blurb="Tighten prose, vary rhythm, and catch errors without flattening your voice.",
         alt="Cyberpunk illustration for the free AI tools for fiction writers guide",
         llm="A private, no-signup AI toolkit for fiction writers to tighten prose, vary rhythm, catch errors, and summarize chapters without flattening voice or storing drafts."),
    dict(slug="ai-tools-for-freelancers-2026", thumb="thumb-freelance.png", cat="Productivity",
         card="13 Free AI Tools for Freelancers (No Signup)",
         blurb="Writing, client comms, JSON, Markdown and visuals — browser-private.",
         alt="Cyberpunk illustration for the free AI tools for freelancers guide",
         llm="Thirteen free, no-signup AI tools for freelancers covering writing, client comms, JSON, Markdown, passwords and visuals, all browser-private so client text never leaves the device."),
    dict(slug="ai-tools-for-job-seekers-2026", thumb="thumb-jobseek.png", cat="Career",
         card="Free AI Tools for Job Seekers",
         blurb="Build a resume, bio and cover letter, then check them privately.",
         alt="Cyberpunk illustration for the free AI tools for job seekers guide",
         llm="A free, no-signup AI toolkit for job seekers to build a resume and bio, check grammar, hit word limits, and humanize drafts privately — write better applications, pay nothing per submission."),
    dict(slug="ai-tools-for-researchers-2026", thumb="thumb-research.png", cat="Research",
         card="Free AI Tools for Researchers",
         blurb="Triage PDFs, summarize papers, and clean prose privately.",
         alt="Cyberpunk illustration for the free AI tools for researchers guide",
         llm="A private, no-signup AI stack for researchers to triage PDFs, summarize papers, clean prose, and check readability without a lab budget or a privacy gamble."),
    dict(slug="ai-tools-for-small-business-2026", thumb="thumb-smb.png", cat="Business",
         card="Free AI Tools for Small Business (2026)",
         blurb="JSON, passwords, Markdown, SERP previews and visuals — zero bills.",
         alt="Cyberpunk illustration for the free AI tools for small business guide",
         llm="A free, no-signup AI toolkit for small business owners covering JSON, passwords, Markdown, grammar, SERP previews, hashtags and background removal — the daily chores with zero monthly bills."),
    dict(slug="ai-tools-for-social-media-managers-2026", thumb="thumb-social.png", cat="Marketing",
         card="Free AI Tools for Social Media Managers",
         blurb="Hashtags, titles, captions and visuals without a subscription.",
         alt="Cyberpunk illustration for the free AI tools for social media managers guide",
         llm="A free, no-signup toolkit for social media managers covering hashtags, video titles, captions, grammar, background removal and bios — handle the repetitive parts and keep client accounts private."),
    dict(slug="ai-writing-tools-non-native-english", thumb="thumb-esl.png", cat="Writing",
         card="Free AI Writing Tools for Non-Native English",
         blurb="Fix grammar, sound natural, and build confidence privately.",
         alt="Cyberpunk illustration for the free AI writing tools for non-native English guide",
         llm="A private, no-signup AI toolkit for non-native English writers to fix grammar, hit word limits, sound natural, and check their own work confidently, without a subscription or stored drafts."),
    dict(slug="free-ai-content-detector-no-upload", thumb="thumb-noupload.png", cat="Privacy",
         card="Private AI Detector (No Upload)",
         blurb="Checks your text in the browser, so nothing leaves your device.",
         alt="Cyberpunk illustration for the private no-upload AI content detector guide",
         llm="A no-upload AI content detector that checks your text in the browser so nothing leaves your device — learn how it works, when to use it, and what the score really means."),
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
