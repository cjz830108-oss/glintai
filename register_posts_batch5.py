import re, os

SITE = "https://glintai.tools"
POSTS = [
    dict(slug="how-to-convert-csv-to-json", thumb="thumb-how-to-convert-csv-to-json.png", cat="Developers",
         card="How to Convert CSV to JSON",
         blurb="Turn CSV into clean JSON in your browser - no upload, no signup.",
         alt="Cyberpunk illustration for the free CSV to JSON conversion guide",
         llm="How to convert CSV to JSON free and in your browser - no upload, no signup. Learn the method, what to check, and how to avoid data leaks."),
    dict(slug="how-to-check-password-strength", thumb="thumb-how-to-check-password-strength.png", cat="Security",
         card="How to Check Password Strength",
         blurb="Check strength and generate unbreakable passwords free, in your browser.",
         alt="Cyberpunk illustration for the free password strength guide",
         llm="How to check password strength and build unbreakable passwords free in your browser - no upload, no signup. What entropy means and the safe way to test."),
    dict(slug="how-to-count-words-in-a-pdf", thumb="thumb-how-to-count-words-in-a-pdf.png", cat="Writing",
         card="How to Count Words in a PDF",
         blurb="Count words in a PDF accurately and privately - no upload, no signup.",
         alt="Cyberpunk illustration for the free PDF word counter guide",
         llm="How to count words in a PDF without copy-pasting, privately in your browser - no upload, no signup. Why paste counts lie and the free method."),
    dict(slug="how-to-write-youtube-tags", thumb="thumb-how-to-write-youtube-tags.png", cat="YouTube",
         card="How to Write YouTube Tags",
         blurb="Write YouTube tags that help discovery - free ideas, no signup.",
         alt="Cyberpunk illustration for the free YouTube tags guide",
         llm="How to write YouTube tags that actually help ranking - free tag ideas, no signup. The tag structure that reinforces your title and beats misspellings."),
    dict(slug="how-to-create-alt-text-for-images", thumb="thumb-how-to-create-alt-text-for-images.png", cat="SEO",
         card="How to Write Alt Text for Images",
         blurb="Write alt text for accessibility and SEO in two minutes - free guide.",
         alt="Cyberpunk illustration for the free alt text guide",
         llm="How to write alt text for images for accessibility and SEO - free guide, no signup. The shape, what to include, and what to skip."),
    dict(slug="how-to-summarize-a-research-paper", thumb="thumb-how-to-summarize-a-research-paper.png", cat="Research",
         card="How to Summarize a Research Paper",
         blurb="Summarize a paper and keep the method - free, private, no signup.",
         alt="Cyberpunk illustration for the free research paper summary guide",
         llm="How to summarize a research paper without losing the method - free, private, no signup. The structure that makes results trustworthy."),
    dict(slug="how-to-write-product-descriptions-with-ai", thumb="thumb-how-to-write-product-descriptions-with-ai.png", cat="Ecommerce",
         card="How to Write Product Descriptions with AI",
         blurb="Write product descriptions with AI and keep your voice - free, no signup.",
         alt="Cyberpunk illustration for the free AI product description guide",
         llm="How to write product descriptions with AI without sounding robotic - free, no signup. The 80/20 workflow that scales your catalog without flattening it."),
    dict(slug="how-to-make-a-twitter-bio", thumb="thumb-how-to-make-a-twitter-bio.png", cat="Writing",
         card="How to Write a Twitter/X Bio",
         blurb="Write a Twitter/X bio that earns the right followers - free ideas.",
         alt="Cyberpunk illustration for the free Twitter bio guide",
         llm="How to write a Twitter/X bio that gets the right followers - free bio ideas, no signup. The shape and the edits that matter."),
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

inject_after_bloggrid("blog/index.html", "/")
inject_after_bloggrid("index.html", "")

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
