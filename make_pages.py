# -*- coding: utf-8 -*-
"""Generate on-brand static pages for Glint AI (extension/resources/ai-tools/
privacy/terms/dashboard/404). Shared cyberpunk template, no frameworks."""
import os

CSS = """    :root{
      --bg:#07070d; --bg-soft:#0d0d18; --bg-card:rgba(18,18,32,0.72);
      --text:#e8e8f5; --text-soft:#9aa0c0; --line:rgba(120,120,200,0.20);
      --brand:#00f0ff; --brand-2:#ff2e97; --brand-soft:rgba(0,240,255,0.10);
      --ok:#39ff14; --warn:#ffb000; --shadow:0 0 30px rgba(0,240,255,0.15);
      --radius:16px; --maxw:1120px;
    }
    *{box-sizing:border-box;}
    html{scroll-behavior:smooth;}
    body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--text);background:#07070d;
      background-image:radial-gradient(1200px 600px at 50% -300px,rgba(0,240,255,.12),transparent),radial-gradient(900px 500px at 100% 0,rgba(255,46,151,.08),transparent),linear-gradient(rgba(0,240,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(0,240,255,.045) 1px,transparent 1px);
      background-size:auto,auto,44px 44px,44px 44px;background-attachment:fixed;line-height:1.6;-webkit-font-smoothing:antialiased;}
    a{color:inherit;text-decoration:none;}
    .wrap{max-width:var(--maxw);margin:0 auto;padding:0 20px;}
    h1,h2,h3{line-height:1.2;letter-spacing:-0.02em;}
    .muted{color:var(--text-soft);}
    header.nav{position:sticky;top:0;z-index:50;background:rgba(7,7,13,.8);backdrop-filter:saturate(180%) blur(10px);border-bottom:1px solid var(--line);box-shadow:0 0 24px rgba(0,240,255,.08);}
    .nav-inner{display:flex;align-items:center;justify-content:space-between;height:64px;}
    .logo{display:flex;align-items:center;gap:10px;font-weight:800;font-size:19px;}
    .logo .dot{width:30px;height:30px;border-radius:9px;background:linear-gradient(135deg,var(--brand),var(--brand-2));display:grid;place-items:center;color:#02121a;font-size:16px;box-shadow:0 0 16px rgba(0,240,255,.5);}
    .nav-links{display:flex;gap:26px;font-size:15px;color:var(--text-soft);}
    .nav-links a:hover,.nav-links a.active{color:var(--brand);text-shadow:0 0 12px rgba(0,240,255,.6);}
    .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:11px 20px;border-radius:999px;font-weight:700;font-size:15px;cursor:pointer;border:1px solid transparent;transition:.15s;white-space:nowrap;}
    .btn-primary{background:linear-gradient(135deg,var(--brand),var(--brand-2));color:#02121a;box-shadow:0 0 22px rgba(0,240,255,.45);}
    .btn-primary:hover{transform:translateY(-1px);box-shadow:0 0 30px rgba(255,46,151,.5);}
    .btn-ghost{background:var(--bg-soft);color:var(--text);border-color:var(--line);}
    .btn-ghost:hover{border-color:var(--brand);color:var(--brand);box-shadow:0 0 16px rgba(0,240,255,.3);}
    .btn-sm{padding:8px 16px;font-size:14px;}
    section{padding:60px 0;}
    .hero{padding:80px 0 40px;text-align:center;background:radial-gradient(1200px 400px at 50% -120px,var(--brand-soft),transparent);}
    .hero .badge{display:inline-flex;align-items:center;gap:8px;padding:6px 14px;border-radius:999px;background:var(--brand-soft);color:var(--brand);font-size:13px;font-weight:700;margin-bottom:18px;}
    .hero h1{font-size:clamp(32px,5vw,54px);margin:0 0 16px;}
    .hero h1 .grad{background:linear-gradient(135deg,var(--brand),var(--brand-2));-webkit-background-clip:text;background-clip:text;color:transparent;}
    .hero p{font-size:19px;color:var(--text-soft);max-width:640px;margin:0 auto 28px;}
    .hero-cta{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;}
    .card{background:var(--bg-card);border:1px solid var(--line);border-radius:var(--radius);padding:24px;backdrop-filter:blur(6px);}
    .grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px;}
    .grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:22px;}
    .card h3{margin:0 0 8px;font-size:18px;}
    .card p{margin:0;color:var(--text-soft);font-size:14.5px;}
    .tag{display:inline-block;font-size:12px;font-weight:700;color:var(--brand);text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px;}
    form.waitlist{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;max-width:480px;margin:0 auto;}
    form.waitlist input{flex:1;min-width:220px;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:rgba(7,7,13,.6);color:var(--text);font-size:15px;font-family:inherit;}
    .note{font-size:13px;color:var(--text-soft);margin-top:14px;}
    .disc{font-size:13px;color:var(--text-soft);border-left:3px solid var(--brand);padding:6px 14px;margin:18px 0;}
    footer{border-top:1px solid var(--line);padding:40px 0 30px;color:var(--text-soft);font-size:14px;}
    .foot-grid{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:24px;}
    .foot-grid h4{color:var(--text);font-size:14px;margin:0 0 12px;}
    .foot-grid a{display:block;padding:4px 0;}
    .foot-grid a:hover{color:var(--brand);}
    .copy{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);font-size:13px;}
    @media(max-width:720px){.nav-links{display:none;}.foot-grid{grid-template-columns:1fr 1fr;}}
"""

NAV = """      <nav class="nav-links">
        <a href="/tools/"[[tools]]>Tools</a>
        <a href="/resources/"[[res]]>Resources</a>
        <a href="/#pricing">Pricing</a>
        <a href="/blog/"[[blog]]>Blog</a>
        <a href="/extension/"[[ext]]>Extension</a>
      </nav>"""

FOOTER = """    <div class="foot-grid">
      <div>
        <a class="logo" href="/"><span class="dot">✦</span> Glint AI</a>
        <p style="margin:10px 0 0;">The everyday AI toolkit for creators &amp; marketers. Built to be an asset you own.</p>
      </div>
      <div><h4>Tools</h4><a href="/tools/">All 16 tools</a><a href="/tools/ai-humanizer.html">AI Humanizer</a><a href="/tools/ai-text-summarizer.html">Text Summarizer</a><a href="/tools/grammar-checker.html">Grammar Checker</a><a href="/tools/background-remover.html">Background Remover</a></div>
      <div><h4>Resources</h4><a href="/blog/">Blog &amp; guides</a><a href="/resources/">Free templates</a><a href="/ai-tools/">Tool reviews</a><a href="/extension/">Chrome extension</a></div>
      <div><h4>Company</h4><a href="/#pricing">Pricing</a><a href="/#features">Why Glint</a><a href="/#faq">FAQ</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a></div>
    </div>
    <div class="copy">© 2026 Glint AI. Payments via PayPal · Accounts via Supabase.</div>"""

MODAL = """  <div id="authModal" style="display:none;position:fixed;inset:0;background:rgba(10,10,30,.5);z-index:100;align-items:center;justify-content:center;padding:20px;">
    <div style="background:#fff;border-radius:18px;max-width:380px;width:100%;padding:28px;box-shadow:0 20px 60px rgba(0,0,0,.25);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;">
        <h3 style="margin:0;font-size:20px;">Glint AI account</h3>
        <button onclick="closeModal()" style="border:none;background:none;font-size:22px;cursor:pointer;color:#5b5b6b;">×</button>
      </div>
      <form id="authForm" style="display:flex;flex-direction:column;gap:12px;">
        <input type="email" id="authEmail" placeholder="you@email.com" required style="padding:12px 14px;border:1px solid #ddd;border-radius:12px;font-size:15px;font-family:inherit;" />
        <input type="password" id="authPass" placeholder="Password (or use magic link)" style="padding:12px 14px;border:1px solid #ddd;border-radius:12px;font-size:15px;font-family:inherit;" />
        <button type="submit" class="btn btn-primary" id="authSubmit">Log in</button>
        <button type="button" class="btn btn-ghost" onclick="googleLogin()">Continue with Google</button>
        <button type="button" class="btn btn-ghost" onclick="magicLink(event)">Email me a magic link</button>
        <button type="button" class="btn btn-ghost" id="toggleAuth" onclick="toggleMode()">Need an account? Sign up</button>
      </form>
      <p id="authMsg" style="margin:14px 0 0;font-size:13.5px;color:#5b5b6b;min-height:18px;"></p>
    </div>
  </div>
  <script src="/vendor/supabase.min.js" onerror="this.onerror=null;this.src='https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js'"></script>
  <script src="/supabase-auth.js"></script>"""

def page(title, h1, badge, body, active, canonical, extra_head="", with_auth=False, robots=""):
    nav = NAV.replace("[[tools]]", ' class="active"' if active=="tools" else '') \
             .replace("[[res]]", ' class="active"' if active=="res" else '') \
             .replace("[[blog]]", ' class="active"' if active=="blog" else '') \
             .replace("[[ext]]", ' class="active"' if active=="ext" else '')
    rb = ('  <meta name="robots" content="%s" />\n' % robots) if robots else ""
    modal = MODAL if with_auth else ""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__TITLE__</title>
  <meta name="description" content="__DESC__" />
  <link rel="icon" href="/icon.svg" type="image/svg+xml" />
  <link rel="canonical" href="__CANON__" />
  __ROBOTS____EXTRA__
  <style>__CSS__</style>
</head>
<body>
  <header class="nav"><div class="wrap nav-inner">
    <a class="logo" href="/"><span class="dot">✦</span> Glint AI</a>
    __NAV__
    <a class="btn btn-ghost btn-sm" id="loginBtn" href="#">Log in</a>
    <a class="btn btn-primary btn-sm" id="getProBtn" href="/#pricing">Get Pro</a>
  </div></header>

  <section class="hero"><div class="wrap">
    __BADGE____H1__
    __BODY__
  </div></section>

  <footer><div class="wrap">__FOOTER__</div></footer>
__MODAL__
</body>
</html>
""".replace("__TITLE__", title).replace("__DESC__", title).replace("__CANON__", canonical) \
  .replace("__ROBOTS__", rb).replace("__EXTRA__", extra_head).replace("__CSS__", CSS) \
  .replace("__NAV__", nav).replace("__BADGE__", ('<span class="badge">'+badge+'</span>' if badge else '')) \
  .replace("__H1__", h1).replace("__BODY__", body).replace("__FOOTER__", FOOTER).replace("__MODAL__", modal)

# ---------- content ----------
EXT_BODY = """<div style="max-width:680px;margin:0 auto;">
  <p class="muted">Glint AI is going portable. Each popular tool is being rebuilt as a lightweight Chrome extension that runs the same private, in-browser logic — and sends a steady stream of users back to the hub.</p>
  <div class="grid3" style="margin:28px 0;">
    <div class="card"><span class="tag">First</span><h3>🤖 AI Humanizer</h3><p>Humanize text right on any page you're writing.</p></div>
    <div class="card"><span class="tag">Next</span><h3>📝 Summarizer</h3><p>Summarize articles without leaving the tab.</p></div>
    <div class="card"><span class="tag">Planned</span><h3>✍️ Grammar Check</h3><p>Live grammar nudges as you type online.</p></div>
  </div>
  <h2 style="text-align:center;">Get notified when it ships</h2>
  <form class="waitlist" id="waitlist" onsubmit="joinWaitlist(event)">
    <input type="email" id="wlEmail" placeholder="you@email.com" required />
    <button class="btn btn-primary" type="submit">Join the waitlist</button>
  </form>
  <p class="note" id="wlMsg"></p>
  <p class="note">We'll only email you about the extension launch. No spam, unsubscribe anytime.</p>
</div>
<script>
  function joinWaitlist(e){e.preventDefault();var em=document.getElementById('wlEmail').value;if(!em)return;localStorage.setItem('glint_ext_waitlist',em);document.getElementById('wlMsg').textContent='You are on the list ('+em+').';document.getElementById('wlEmail').value='';}
</script>"""

RES_BODY = """<div class="grid2">
  <div class="card"><span class="tag">Free</span><h3>📚 Blog &amp; playbooks</h3><p>SEO-optimized guides on writing, SEO, and productivity — all free, no signup.</p><p style="margin-top:14px;"><a class="btn btn-ghost btn-sm" href="/blog/">Read the blog →</a></p></div>
  <div class="card"><span class="tag">Free</span><h3>🧰 Tool guides</h3><p>Step-by-step walkthroughs for every Glint AI tool, with copy-paste prompts.</p><p style="margin-top:14px;"><a class="btn btn-ghost btn-sm" href="/tools/">Browse tools →</a></p></div>
  <div class="card"><span class="tag">Pro</span><h3>💎 Prompt &amp; template library</h3><p>Curated prompt packs and templates for marketers and creators. Unlocks with Pro.</p><p style="margin-top:14px;"><a class="btn btn-ghost btn-sm" href="/#pricing">See Pro →</a></p></div>
  <div class="card"><span class="tag">Soon</span><h3>📄 Downloadable kits</h3><p>Content calendars, SEO checklists, and swipe files — coming to the resource library.</p></div>
</div>
<p class="note" style="text-align:center;">Resources are added constantly. Subscribe on the homepage to hear about new drops.</p>"""

AITOOLS_BODY = """<div class="disc">Disclosure: Glint AI may earn a commission if you sign up for a tool through our links, at no extra cost to you. We only list tools we'd genuinely recommend to a creator or marketer.</div>
<div class="grid2">
  <div class="card"><span class="tag">Writing</span><h3>Best AI grammar checker</h3><p>Our pick for catching the mistakes that matter without nagging you.</p><p style="margin-top:14px;"><a class="btn btn-ghost btn-sm" href="#">Read review →</a></p></div>
  <div class="card"><span class="tag">Writing</span><h3>Best AI humanizer</h3><p>Tools that restore natural rhythm to AI drafts (use responsibly).</p><p style="margin-top:14px;"><a class="btn btn-ghost btn-sm" href="#">Read review →</a></p></div>
  <div class="card"><span class="tag">Productivity</span><h3>Best AI note-taker</h3><p>Turn meetings and articles into actionable notes.</p><p style="margin-top:14px;"><a class="btn btn-ghost btn-sm" href="#">Read review →</a></p></div>
  <div class="card"><span class="tag">Image</span><h3>Best background remover</h3><p>On-device and cloud options compared for speed and privacy.</p><p style="margin-top:14px;"><a class="btn btn-ghost btn-sm" href="#">Read review →</a></p></div>
</div>
<p class="note" style="text-align:center;">Affiliate links are placeholders for now — drop in your real partner URLs in <code>make_pages.py</code> or directly in this file.</p>"""

PRIV_BODY = """<div class="card" style="max-width:820px;margin:0 auto;">
  <h3>What we collect</h3>
  <p>Glint AI is built privacy-first. The free tools run entirely in your browser — your text never leaves your device, and we do not place tracking cookies.</p>
  <h3>Accounts &amp; email</h3>
  <p>If you create an account or join a waitlist, we store the email you provide (via Supabase). We use it only to deliver the feature you signed up for. You can request deletion anytime.</p>
  <h3>Payments</h3>
  <p>Pro subscriptions are processed by PayPal. We never see or store your card details. Subscription status is written to your account by PayPal's webhook.</p>
  <h3>Analytics</h3>
  <p>We use privacy-friendly, aggregated analytics (no cross-site tracking, no personal profiles). We do not sell your data.</p>
  <p class="note">Last updated: 2026-08-12.</p>
</div>"""

TERMS_BODY = """<div class="card" style="max-width:820px;margin:0 auto;">
  <h3>Use responsibly</h3>
  <p>Glint AI tools are provided "as is". You are responsible for how you use generated content — don't use them to produce illegal, deceptive, or harmful material.</p>
  <h3>Accounts</h3>
  <p>You are responsible for keeping your account credentials safe. One person, one account for free tier.</p>
  <h3>Billing (Pro)</h3>
  <p>Pro is billed by PayPal on a recurring basis. Cancellation takes effect at the end of the current period. Refunds follow PayPal's policy.</p>
  <h3>Intellectual property</h3>
  <p>The Glint AI brand, design, and code are owned by Glint AI. Tool outputs belong to you.</p>
  <p class="note">Last updated: 2026-08-12.</p>
</div>"""

DASH_BODY = """<div class="card" style="max-width:720px;margin:0 auto;">
  <div id="loggedOut">
    <p class="muted">Log in to see your plan, usage, and Pro features.</p>
    <div class="hero-cta" style="justify-content:flex-start;">
      <button class="btn btn-primary" onclick="openModal()">Log in / Sign up</button>
      <a class="btn btn-ghost" href="/#pricing">See Pro plan</a>
    </div>
  </div>
  <div id="loggedIn" style="display:none;">
    <p>Welcome back, <b id="dashEmail">—</b>.</p>
    <p>Plan: <b id="dashPlan">free</b></p>
    <div id="usage" class="muted" style="margin-top:10px;">Usage tracking rolls out with the Pro usage system.</div>
    <button class="btn btn-ghost btn-sm" onclick="doLogout()">Log out</button>
  </div>
</div>
<script>
  // reflect session into dashboard once supabase-auth.js loads
  window.addEventListener('DOMContentLoaded', function(){
    if (typeof client === 'undefined' || !client) return;
    client.auth.getSession().then(({data})=>{ if(data.session) renderDash(data.session.user); });
    client.auth.onAuthStateChange((_e,s)=>{ if(s) renderDash(s.user); else resetDash(); });
  });
  function renderDash(user){
    var lo=document.getElementById('loggedOut'), li=document.getElementById('loggedIn');
    if(!lo||!li) return;
    lo.style.display='none'; li.style.display='block';
    document.getElementById('dashEmail').textContent = user.email;
    // plan via supabase-auth.reflectUser pattern
    if (client) client.from('profiles').select('plan').eq('id',user.id).single().then(({data})=>{
      document.getElementById('dashPlan').textContent = (data&&data.plan)||'free';
    });
  }
  function resetDash(){ var lo=document.getElementById('loggedOut'),li=document.getElementById('loggedIn'); if(lo)lo.style.display='block'; if(li)li.style.display='none'; }
</script>"""

NF_BODY = """<p style="text-align:center;">The page you're looking for doesn't exist or moved.</p>
<div class="hero-cta">
  <a class="btn btn-primary" href="/">Go home</a>
  <a class="btn btn-ghost" href="/tools/">Browse tools</a>
</div>"""

pages = [
    ("extension", "extension/index.html", "Glint AI — Chrome Extension (Coming Soon)",
     "<h1>Chrome Extension</h1>", "🧩 COMING SOON", EXT_BODY, "ext",
     "https://glintai.tools/extension/", True, ""),
    ("resources", "resources/index.html", "Glint AI — Free Resources & Templates",
     "<h1>Free resources &amp; templates</h1>", "📦 FOR CREATORS", RES_BODY, "res",
     "https://glintai.tools/resources/", True, ""),
    ("ai-tools", "ai-tools/index.html", "Glint AI — AI Tool Reviews (Affiliate)",
     "<h1>AI tools we recommend</h1>", "🔗 HAND-PICKED", AITOOLS_BODY, "",
     "https://glintai.tools/ai-tools/", True, ""),
    ("privacy", "privacy/index.html", "Glint AI — Privacy Policy",
     "<h1>Privacy Policy</h1>", "", PRIV_BODY, "",
     "https://glintai.tools/privacy/", True, ""),
    ("terms", "terms/index.html", "Glint AI — Terms of Service",
     "<h1>Terms of Service</h1>", "", TERMS_BODY, "",
     "https://glintai.tools/terms/", True, ""),
    ("dashboard", "dashboard/index.html", "Glint AI — Your Dashboard",
     "<h1>Your dashboard</h1>", "", DASH_BODY, "",
     "https://glintai.tools/dashboard/", True, "noindex"),
    ("404", "404.html", "Glint AI — Page not found",
     "<h1>404</h1>", "", NF_BODY, "",
     "https://glintai.tools/", True, "noindex"),
]

for key, path, title, h1, badge, body, active, canon, *rest in pages:
    with_auth = rest[0] if rest else False
    robots = rest[1] if len(rest) > 1 else ""
    html = page(title, h1, badge, body, active, canon, with_auth=with_auth, robots=robots)
    d = os.path.dirname(path)
    if d: os.makedirs(d, exist_ok=True)
    open(path, "w", encoding="utf-8").write(html)
    print("wrote", path, "(%d bytes)" % len(html))
