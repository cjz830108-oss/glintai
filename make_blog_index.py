# -*- coding: utf-8 -*-
"""Create /blog/index.html — a real blog archive, reusing the homepage's
34-post grid markup (no retyping). Adds the card CSS the shared template lacks."""
import re, os

idx = open("index.html", encoding="utf-8").read()
m = re.search(r'<div class="blog-grid">\n(.*?)\n      </div>\n    </div>\n  </section>', idx, re.DOTALL)
if not m:
    raise SystemExit("blog grid not found")
grid = m.group(1)

CSS_BLOG = """
  .blog-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px;}
  .post{background:rgba(18,18,32,.72);backdrop-filter:blur(6px);border:1px solid rgba(120,120,200,.20);border-radius:16px;overflow:hidden;transition:.15s;}
  .post:hover{transform:translateY(-3px);box-shadow:0 0 30px rgba(0,240,255,.15);}
  .post .thumb{height:130px;background:linear-gradient(135deg,rgba(0,240,255,.18),rgba(255,46,151,.18));overflow:hidden;display:grid;place-items:center;font-size:30px;}
  .post .thumb img{width:100%;height:100%;object-fit:cover;display:block;}
  .post .body{padding:18px;}
  .post .cat{font-size:12px;font-weight:700;color:#00f0ff;text-transform:uppercase;letter-spacing:.04em;}
  .post h3{margin:6px 0 8px;font-size:17px;}
  .post p{margin:0;color:#9aa0c0;font-size:14px;}
"""

# Reuse the same layout shell as other pages (compact inline copy)
PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Glint AI — Blog & Playbooks for Creators & Marketers</title>
  <meta name="description" content="SEO-optimized guides on writing, SEO, and productivity from Glint AI. Free, no signup." />
  <link rel="icon" href="/icon.svg" type="image/svg+xml" />
  <link rel="canonical" href="https://glintai.tools/blog/" />
  <style>
    :root{--bg:#07070d;--bg-soft:#0d0d18;--text:#e8e8f5;--text-soft:#9aa0c0;--line:rgba(120,120,200,.20);--brand:#00f0ff;--brand-2:#ff2e97;--radius:16px;--maxw:1120px;}
    *{box-sizing:border-box;}
    body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--text);background:#07070d;
      background-image:radial-gradient(1200px 600px at 50% -300px,rgba(0,240,255,.12),transparent),radial-gradient(900px 500px at 100% 0,rgba(255,46,151,.08),transparent),linear-gradient(rgba(0,240,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(0,240,255,.045) 1px,transparent 1px);
      background-size:auto,auto,44px 44px,44px 44px;background-attachment:fixed;line-height:1.6;-webkit-font-smoothing:antialiased;}
    a{color:inherit;text-decoration:none;}
    .wrap{max-width:var(--maxw);margin:0 auto;padding:0 20px;}
    header.nav{position:sticky;top:0;z-index:50;background:rgba(7,7,13,.8);backdrop-filter:saturate(180%) blur(10px);border-bottom:1px solid var(--line);box-shadow:0 0 24px rgba(0,240,255,.08);}
    .nav-inner{display:flex;align-items:center;justify-content:space-between;height:64px;}
    .logo{display:flex;align-items:center;gap:10px;font-weight:800;font-size:19px;}
    .logo .dot{width:30px;height:30px;border-radius:9px;background:linear-gradient(135deg,var(--brand),var(--brand-2));display:grid;place-items:center;color:#02121a;font-size:16px;box-shadow:0 0 16px rgba(0,240,255,.5);}
    .nav-links{display:flex;gap:26px;font-size:15px;color:var(--text-soft);}
    .nav-links a:hover,.nav-links a.active{color:var(--brand);text-shadow:0 0 12px rgba(0,240,255,.6);}
    .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:11px 20px;border-radius:999px;font-weight:700;font-size:15px;cursor:pointer;border:1px solid transparent;transition:.15s;}
    .btn-primary{background:linear-gradient(135deg,var(--brand),var(--brand-2));color:#02121a;box-shadow:0 0 22px rgba(0,240,255,.45);}
    .btn-ghost{background:var(--bg-soft);color:var(--text);border-color:var(--line);}
    .btn-sm{padding:8px 16px;font-size:14px;}
    section{padding:60px 0;}
    .sec-head{text-align:center;max-width:680px;margin:0 auto 40px;}
    .sec-head h2{font-size:clamp(26px,3.5vw,38px);margin:0 0 10px;}
    .sec-head p{color:var(--text-soft);font-size:17px;margin:0;}
    __CSSBLOG__
    footer{border-top:1px solid var(--line);padding:40px 0 30px;color:var(--text-soft);font-size:14px;}
    .foot-grid{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:24px;}
    .foot-grid h4{color:var(--text);font-size:14px;margin:0 0 12px;}
    .foot-grid a{display:block;padding:4px 0;}
    .foot-grid a:hover{color:var(--brand);}
    .copy{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);font-size:13px;}
    @media(max-width:720px){.nav-links{display:none;}.foot-grid{grid-template-columns:1fr 1fr;}}
  </style>
</head>
<body>
  <header class="nav"><div class="wrap nav-inner">
    <a class="logo" href="/"><span class="dot">✦</span> Glint AI</a>
    <nav class="nav-links">
      <a href="/tools/">Tools</a>
      <a href="/resources/">Resources</a>
      <a href="/#pricing">Pricing</a>
      <a href="/blog/" class="active">Blog</a>
      <a href="/extension/">Extension</a>
    </nav>
    <a class="btn btn-ghost btn-sm" id="loginBtn" href="#">Log in</a>
    <a class="btn btn-primary btn-sm" id="getProBtn" href="/#pricing">Get Pro</a>
  </div></header>

  <section><div class="wrap">
    <div class="sec-head">
      <h2>Guides &amp; playbooks</h2>
      <p>SEO-optimized articles that bring search traffic and feed the funnel.</p>
    </div>
    <div class="blog-grid">__GRID__</div>
  </div></section>

  <footer><div class="wrap">
    <div class="foot-grid">
      <div><a class="logo" href="/"><span class="dot">✦</span> Glint AI</a><p style="margin:10px 0 0;">The everyday AI toolkit for creators &amp; marketers. Built to be an asset you own.</p></div>
      <div><h4>Tools</h4><a href="/tools/">All 16 tools</a><a href="/tools/ai-humanizer.html">AI Humanizer</a><a href="/tools/ai-text-summarizer.html">Text Summarizer</a><a href="/tools/grammar-checker.html">Grammar Checker</a><a href="/tools/background-remover.html">Background Remover</a></div>
      <div><h4>Resources</h4><a href="/blog/">Blog &amp; guides</a><a href="/resources/">Free templates</a><a href="/ai-tools/">Tool reviews</a><a href="/extension/">Chrome extension</a></div>
      <div><h4>Company</h4><a href="/#pricing">Pricing</a><a href="/#features">Why Glint</a><a href="/#faq">FAQ</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a></div>
    </div>
    <div class="copy">© 2026 Glint AI. Payments via PayPal · Accounts via Supabase.</div>
  </div></footer>
  <script src="/vendor/supabase.min.js" onerror="this.onerror=null;this.src='https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js'"></script>
  <script src="/supabase-auth.js"></script>
</body>
</html>
"""

html = PAGE.replace("__CSSBLOG__", CSS_BLOG).replace("__GRID__", grid)
os.makedirs("blog", exist_ok=True)
open("blog/index.html", "w", encoding="utf-8").write(html)
print("wrote blog/index.html (%d bytes, %d posts)" % (len(html), grid.count('<a class="post"')))
