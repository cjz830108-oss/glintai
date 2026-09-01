import os
ROOT="."
E=[
("blog/best-youtube-title-generator-tools-2026.html","your title decides","the same title formulas work for blog posts too","/blog/ai-headline-generator.html"),
("blog/best-free-ai-tools-bloggers-2026.html","search traffic is still","turn a topic into headline options","/blog/ai-headline-generator.html"),
("blog/best-free-json-formatter.html","you need one the moment","the rest of the free AI developer stack","/blog/free-ai-tools-developers.html"),
("blog/markdown-to-html-workflow.html","write once in plain text","12 no-signup picks for developers","/blog/free-ai-tools-developers.html"),
("blog/free-grammar-checker-no-signup.html","teachers see it constantly","a no-account toolkit for the classroom","/blog/free-ai-tools-teachers.html"),
("blog/ai-essay-writer-guide.html","free ai tools that fit","what teachers can use on the other side of the desk","/blog/free-ai-tools-teachers.html"),
("blog/best-free-serp-preview-tool.html","click-through rate is why","write the description, then preview it free","/blog/ai-meta-description-generator.html"),
]
CLOSE=("</p>","</li>","</h3>","</h2>","</td>")
ok=skip=0
for src,anc,txt,tgt in E:
    p=os.path.join(ROOT,src.lstrip("/"))
    h=open(p,encoding="utf-8").read()
    if tgt in h: print("SKIP exists",src); skip+=1; continue
    hl=h.lower(); al=anc.lower()
    idx=hl.find(al)
    if idx==-1: print("SKIP no-anchor",src); skip+=1; continue
    best=None
    for c in CLOSE:
        j=h.find(c,idx+len(anc))
        if j!=-1 and (best is None or j<best): best=j
    if best is None: print("SKIP no-close",src); skip+=1; continue
    h=h[:best]+f' <a href="{tgt}">{txt}</a>'+h[best:]
    open(p,"w",encoding="utf-8").write(h)
    print("OK",src); ok+=1
print(f"DONE ok={ok} skip={skip}")
