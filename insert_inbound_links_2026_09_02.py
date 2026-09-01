import re, os
ROOT="."
# source, unique_substring, anchor_text, target
E=[
("blog/youtube-title-generator-guide.html","Two failure modes dominate","how to avoid those same failure modes in your blog headlines","/blog/ai-headline-generator.html"),
("blog/best-youtube-title-generator-tools-2026.html","your title decides","the same title formulas work for blog posts too","/blog/ai-headline-generator.html"),
("blog/best-free-ai-tools-bloggers-2026.html","search traffic is still","turn a topic into headline options","/blog/ai-headline-generator.html"),
("tools/youtube-title-generator.html","Match the title to your video's actual content","apply the same method to your blog headlines","/blog/ai-headline-generator.html"),
("blog/best-free-json-formatter.html","you need one the moment","the rest of the free AI developer stack","/blog/free-ai-tools-developers.html"),
("blog/generate-api-keys-safely.html","team of one","audit the rest of your free AI stack","/blog/free-ai-tools-developers.html"),
("blog/markdown-to-html-workflow.html","write once in plain text","12 no-signup picks for developers","/blog/free-ai-tools-developers.html"),
("tools/json-formatter.html","Formatting happens locally in your browser","the full free developer toolkit","/blog/free-ai-tools-developers.html"),
("blog/private-ai-detector.html","fast, free signal","10 privacy-first picks for teachers","/blog/free-ai-tools-teachers.html"),
("blog/free-grammar-checker-no-signup.html","teachers see it constantly","a no-account toolkit for the classroom","/blog/free-ai-tools-teachers.html"),
("blog/ai-essay-writer-guide.html","free ai tools that fit","what teachers can use on the other side of the desk","/blog/free-ai-tools-teachers.html"),
("blog/meta-description-ctr-guide.html","rank on page one","generate and test descriptions in one pass","/blog/ai-meta-description-generator.html"),
("blog/best-free-serp-preview-tool.html","click-through rate is why","write the description, then preview it free","/blog/ai-meta-description-generator.html"),
("blog/serp-preview-meta-tags.html","description won","an AI generator plus a pixel-accurate preview","/blog/ai-meta-description-generator.html"),
("tools/serp-preview.html","serp preview","how to generate meta descriptions with AI","/blog/ai-meta-description-generator.html"),
("blog/ai-content-detector-comparison.html","Different training data, different thresholds, and different definitions","what Google's rules actually say about AI text","/blog/does-google-detect-ai-content.html"),
("blog/private-ai-detector.html","A genuinely private detector runs","Google's real spam policies","/blog/does-google-detect-ai-content.html"),
("blog/ai-content-detector-guide.html","one signal","where detector scores mislead you","/blog/does-google-detect-ai-content.html"),
]
CLOSE=("</p>","</li>","</h3>","</h2>","</td>")
def ins_at(h,i):
    # insert before next closing tag after i
    best=None
    for c in CLOSE:
        j=h.find(c,i)
        if j!=-1 and (best is None or j<best): best=j
    return best
ok=skip=0
for src,anc,txt,tgt in E:
    p=os.path.join(ROOT,src.lstrip("/"))
    if not os.path.exists(p): print("SKIP no-file",src); skip+=1; continue
    h=open(p,encoding="utf-8").read()
    if tgt in h: print("SKIP exists",src,"->",tgt); skip+=1; continue
    idx=h.find(anc)
    if idx==-1: print("SKIP no-anchor",src,"::",anc); skip+=1; continue
    j=ins_at(h,idx+len(anc))
    if j is None: print("SKIP no-close",src); skip+=1; continue
    link=f' <a href="{tgt}">{txt}</a>'
    h=h[:j]+link+h[j:]
    open(p,"w",encoding="utf-8").write(h)
    print("OK",src,"->",tgt); ok+=1
print(f"\nDONE ok={ok} skip={skip}")
