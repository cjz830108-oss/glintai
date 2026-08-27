# -*- coding: utf-8 -*-
"""Batch 1 homepage restructure for Glint AI.
Applies anchored replacements to index.html (no rewrite of structure/JS logic)."""
import re, io

PATH = "index.html"
s = open(PATH, encoding="utf-8").read()

def sub(pat, new, flags=re.DOTALL):
    global s
    s2, n = re.subn(pat, lambda m: new, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit("PATTERN NOT MATCHED (n=%d):\n%s" % (n, pat[:120]))
    s = s2

# ---------- CSS: insert new classes before cyberpunk override ----------
CSS = r'''
  /* === homepage v2 (tools showcase) === */
  .cat-h { text-align:center; font-size:22px; margin:34px 0 16px; }
  .tool-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:18px; }
  .tcard { background:var(--bg-card); border:1px solid var(--line); border-radius:var(--radius); padding:20px; display:grid; grid-template-columns:auto 1fr; grid-template-rows:auto auto; column-gap:14px; align-items:center; transition:.15s; }
  .tcard:hover { transform:translateY(-3px); box-shadow:var(--shadow); border-color:var(--brand); }
  .tic { grid-row:1 / span 2; font-size:30px; }
  .tn { font-weight:700; font-size:16px; }
  .td { color:var(--text-soft); font-size:13.5px; }
  .tgo { grid-column:2; justify-self:end; color:var(--brand); font-size:13px; font-weight:700; }
  .cats { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px; }
  .cat-col { background:var(--bg-soft); border:1px solid var(--line); border-radius:var(--radius); padding:18px; }
  .cat-col h4 { margin:0 0 10px; font-size:15px; }
  .cat-col a { display:block; padding:5px 0; color:var(--text-soft); font-size:14px; }
  .cat-col a:hover { color:var(--brand); }
  .explore-cta { text-align:center; margin-top:36px; }
  .price-note { font-size:14px; color:var(--text-soft); margin:-4px 0 14px; }
  .price-note b { color:var(--brand); }
  .price-fine { font-size:12px; color:var(--text-soft); margin-top:8px; }
  .google-btn { display:flex; align-items:center; justify-content:center; gap:8px; }
  .google-btn::before { content:"G"; font-weight:800; color:#ea4335; }
'''
sub(r'  /\* === cyberpunk override === \*/', CSS + '\n  /* === cyberpunk override === */')

# ---------- NAV ----------
NAV = '''      <nav class="nav-links">
        <a href="/tools/">Tools</a>
        <a href="/resources/">Resources</a>
        <a href="#pricing">Pricing</a>
        <a href="#blog">Blog</a>
        <a href="/extension/">Extension</a>
      </nav>'''
sub(r'<nav class="nav-links">.*?</nav>', NAV)

# ---------- HERO ----------
HERO = '''<a id="top"></a>
  <section class="hero">
    <div class="wrap">
      <span class="badge">✦ AI TOOLS FOR CREATORS &amp; MARKETERS</span>
      <h1>Your everyday <span class="grad">AI toolkit</span><br/>for creators &amp; marketers</h1>
      <p>Write better. Create faster. Grow smarter. 16 free tools that run right in your browser — no signup, no tracking, no card to start.</p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="#tools">Try free tools →</a>
        <a class="btn btn-ghost" href="#pricing">See Pro plan</a>
      </div>
      <div class="trust">
        <span><b>Free</b> to start</span>
        <span><b>No</b> signup required</span>
        <span><b>Privacy</b>-friendly</span>
        <span><b>Fast</b> browser-based</span>
      </div>
    </div>
  </section>'''
sub(r'<!-- HERO -->(.*?)<!-- TOOLS -->', '<!-- HERO -->\n' + HERO + '\n  <!-- TOOLS -->')

# ---------- TOOLS (category showcase) ----------
TOOLS = '''<section id="tools">
    <div class="wrap">
      <div class="sec-head">
        <h2>16 free tools, organized by what you're doing</h2>
        <p>Pick a tool, use it instantly. Everything runs in your browser — your text never leaves the page.</p>
      </div>

      <h3 class="cat-h">Most popular</h3>
      <div class="tool-grid pop">
        <a class="tcard" href="/tools/ai-humanizer.html"><span class="tic">🤖</span><span class="tn">AI Humanizer</span><span class="td">Make AI text read naturally.</span><span class="tgo">Open →</span></a>
        <a class="tcard" href="/tools/ai-text-summarizer.html"><span class="tic">📝</span><span class="tn">Text Summarizer</span><span class="td">Key points in one click.</span><span class="tgo">Open →</span></a>
        <a class="tcard" href="/tools/grammar-checker.html"><span class="tic">✍️</span><span class="tn">Grammar Checker</span><span class="td">Catch the mistakes that matter.</span><span class="tgo">Open →</span></a>
        <a class="tcard" href="/tools/paraphraser.html"><span class="tic">🔄</span><span class="tn">Paraphraser</span><span class="td">Reword without losing meaning.</span><span class="tgo">Open →</span></a>
        <a class="tcard" href="/tools/pdf-summarizer.html"><span class="tic">📄</span><span class="tn">PDF Summarizer</span><span class="td">Summarize PDFs locally.</span><span class="tgo">Open →</span></a>
        <a class="tcard" href="/tools/background-remover.html"><span class="tic">🧹</span><span class="tn">Background Remover</span><span class="td">Erase backgrounds on-device.</span><span class="tgo">Open →</span></a>
      </div>

      <h3 class="cat-h">Browse by category</h3>
      <div class="cats">
        <div class="cat-col"><h4>✍️ Writing &amp; Editing</h4><a href="/tools/ai-humanizer.html">AI Humanizer</a><a href="/tools/paraphraser.html">Paraphraser</a><a href="/tools/grammar-checker.html">Grammar Checker</a><a href="/tools/ai-content-detector.html">AI Content Detector</a><a href="/tools/bio-resume-generator.html">Bio &amp; Resume Generator</a></div>
        <div class="cat-col"><h4>📝 Summarize</h4><a href="/tools/ai-text-summarizer.html">Text Summarizer</a><a href="/tools/pdf-summarizer.html">PDF Summarizer</a></div>
        <div class="cat-col"><h4>📊 Analyze</h4><a href="/tools/word-readability-analyzer.html">Readability Analyzer</a><a href="/tools/word-counter.html">Word &amp; Character Counter</a></div>
        <div class="cat-col"><h4>🔧 Convert &amp; Format</h4><a href="/tools/markdown-to-html.html">Markdown ↔ HTML</a><a href="/tools/json-formatter.html">JSON Formatter</a><a href="/tools/password-generator.html">Password &amp; Key Generator</a></div>
        <div class="cat-col"><h4>📡 SEO &amp; Social</h4><a href="/tools/youtube-title-generator.html">YouTube Titles</a><a href="/tools/hashtag-generator.html">Hashtag Generator</a><a href="/tools/serp-preview.html">SERP &amp; Meta Preview</a></div>
        <div class="cat-col"><h4>🖼️ Images</h4><a href="/tools/background-remover.html">Background Remover</a></div>
      </div>

      <div class="explore-cta"><a class="btn btn-primary" href="/tools/">Explore all 16 tools →</a></div>
    </div>
  </section>'''
sub(r'<!-- TOOLS -->(.*?)<!-- FEATURES -->', '<!-- TOOLS -->\n' + TOOLS + '\n  <!-- FEATURES -->')

# ---------- PRICING ----------
PRICING = '''<section id="pricing">
    <div class="wrap">
      <div class="sec-head">
        <h2>Simple, honest pricing</h2>
        <p>Start free forever. Upgrade when you want AI power and the resource library.</p>
      </div>
      <div class="price-grid">
        <div class="plan">
          <h3>Free</h3>
          <div class="price">$0<small> / forever</small></div>
          <ul>
            <li>All 16 free tools</li>
            <li>Unlimited local use</li>
            <li>No account needed</li>
            <li>Privacy-friendly (no tracking)</li>
          </ul>
          <a class="btn btn-ghost" href="#tools">Use free tools</a>
        </div>
        <div class="plan featured">
          <span class="tag">Most popular</span>
          <h3>Pro</h3>
          <div class="price">$9<small> / month</small></div>
          <ul>
            <li>GPT-level abstractive summaries</li>
            <li>Prompt &amp; template library</li>
            <li>Chrome extension access</li>
            <li>Higher monthly usage limits</li>
            <li>Priority support</li>
          </ul>
          <a class="btn btn-primary" id="buyPro" href="#" data-plan="pro">Start Pro</a>
          <div id="pp-pro" class="pp-box"></div>
        </div>
        <div class="plan">
          <h3>Team</h3>
          <div class="price">$29<small> / month</small></div>
          <div class="price-note">Coming soon</div>
          <ul>
            <li>Everything in Pro</li>
            <li>5 seats included</li>
            <li>Shared workspace</li>
            <li>White-label export</li>
          </ul>
          <a class="btn btn-ghost" id="buyTeam" href="/extension/#waitlist">Join the waitlist</a>
        </div>
      </div>
    </div>
  </section>'''
sub(r'<!-- PRICING -->(.*?)<!-- BLOG -->', '<!-- PRICING -->\n' + PRICING + '\n  <!-- BLOG -->')

# ---------- FOOTER ----------
FOOTER = '''<footer>
    <div class="wrap">
      <div class="foot-grid">
        <div>
          <a class="logo" href="/"><span class="dot">✦</span> Glint AI</a>
          <p style="margin:0;">The everyday AI toolkit for creators &amp; marketers. Built to be an asset you own.</p>
        </div>
        <div><h4>Tools</h4><a href="/tools/">All 16 tools</a><a href="/tools/ai-humanizer.html">AI Humanizer</a><a href="/tools/ai-text-summarizer.html">Text Summarizer</a><a href="/tools/grammar-checker.html">Grammar Checker</a><a href="/tools/background-remover.html">Background Remover</a><a href="/tools/serp-preview.html">SERP Preview</a></div>
        <div><h4>Resources</h4><a href="/blog/">Blog &amp; guides</a><a href="/resources/">Free templates</a><a href="/ai-tools/">Tool reviews</a><a href="/extension/">Chrome extension</a></div>
        <div><h4>Company</h4><a href="#pricing">Pricing</a><a href="#features">Why Glint</a><a href="#faq">FAQ</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a></div>
      </div>
      <div class="copy">© 2026 Glint AI. Payments via PayPal · Accounts via Supabase — configure in <code>supabase-auth.js</code> (see SETUP.md) to go live.</div>
    </div>
  </footer>'''
sub(r'<!-- FOOTER -->.*?</footer>', '<!-- FOOTER -->\n' + FOOTER)

# ---------- Replace big tool <script> with minimal (keep newsletter subscribe) ----------
SCRIPT = '''  <script>
    function subscribe(e) {
      e.preventDefault();
      const email = document.getElementById('email').value;
      if (!email) return;
      localStorage.setItem('glint_sub', email);
      document.getElementById('subMsg').textContent = '✓ Subscribed (' + email + '). Wire this to your ESP next.';
      document.getElementById('email').value = '';
    }
  </script>'''
sub(r'  <script>\n    // Tabs.*?</script>\n  <script src="p2-tools.js"></script>', SCRIPT)

# ---------- Auth modal: add Google login button ----------
GOOGLE = '''        <button type="button" class="btn btn-ghost google-btn" onclick="googleLogin()">Continue with Google</button>
        <button type="button" class="btn btn-ghost" onclick="magicLink(event)">Email me a magic link</button>'''
sub(r'        <button type="button" class="btn btn-ghost" onclick="magicLink\(event\)">Email me a magic link</button>', GOOGLE)

open(PATH, "w", encoding="utf-8").write(s)
print("OK: index.html restructured.")
