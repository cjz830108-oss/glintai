# -*- coding: utf-8 -*-
"""Build /tools/index.html from the committed homepage (keeps all 16 interactive
tool panels), stripping duplicate hero/features/blog/faq/newsletter to avoid
SEO cannibalization with the homepage."""
import re, subprocess

src = subprocess.check_output(["git", "show", "HEAD:index.html"], text=True)
s = src

def sub(pat, new, flags=re.DOTALL):
    global s
    s2, n = re.subn(pat, lambda m: new, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit("NOT MATCHED (n=%d): %s" % (n, pat[:80]))
    s = s2

# --- head: title / canonical / og / twitter / description ---
s = s.replace(
    "  <title>Glint AI — Free AI Tools for Creators, Marketers & Solo Founders</title>",
    "  <title>Glint AI — All 16 Free AI Tools for Creators & Marketers</title>")
s = s.replace(
    '  <link rel="canonical" href="https://glintai.tools/" />',
    '  <link rel="canonical" href="https://glintai.tools/tools/" />')
s = s.replace(
    '  <meta property="og:title" content="Glint AI — Free AI Tools for Creators & Marketers" />',
    '  <meta property="og:title" content="Glint AI — All 16 Free AI Tools" />')
s = s.replace(
    '  <meta name="twitter:title" content="Glint AI — Free AI Tools" />',
    '  <meta name="twitter:title" content="Glint AI — All 16 Free AI Tools" />')
s = s.replace(
    '  <meta name="description" content="Glint AI is a growing toolbox of free AI-powered utilities for creators and marketers: text summarizer, readability analyzer, Markdown converter, JSON formatter, and password generator. No signup required for free tools"',
    '  <meta name="description" content="All 16 free AI tools from Glint AI in one workspace: humanizer, summarizer, paraphraser, grammar checker, PDF summarizer, JSON formatter, background remover, and more. No signup, runs in your browser."')

# --- add .active nav style before cyberpunk override ---
s = s.replace(
    "  /* === cyberpunk override === */",
    "  .nav-links a.active{color:var(--brand);text-shadow:0 0 12px rgba(0,240,255,.6)}\n  /* === cyberpunk override === */")

# --- nav ---
NAV = '''      <nav class="nav-links">
        <a href="/tools/" class="active">Tools</a>
        <a href="/resources/">Resources</a>
        <a href="/#pricing">Pricing</a>
        <a href="/blog/">Blog</a>
        <a href="/extension/">Extension</a>
      </nav>'''
sub(r'<nav class="nav-links">.*?</nav>', NAV)

# --- hero → tools header ---
HERO = '''<a id="top"></a>
  <section class="hero">
    <div class="wrap">
      <span class="badge">✦ 16 FREE AI TOOLS · NO SIGNUP</span>
      <h1>Every <span class="grad">AI tool</span> you need,<br/>in one workspace</h1>
      <p>Use any tool instantly in your browser. Summarize, humanize, format, generate — free, private, and fast.</p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="#tools">Open the toolkit →</a>
        <a class="btn btn-ghost" href="/#pricing">See Pro plan</a>
      </div>
    </div>
  </section>'''
sub(r'<!-- HERO -->(.*?)<!-- TOOLS -->', '<!-- HERO -->\n' + HERO + '\n  <!-- TOOLS -->')

# --- strip duplicate sections (keep markers for PRICING/FOOTER) ---
sub(r'<!-- FEATURES -->.*?<!-- PRICING -->', '<!-- PRICING -->')
sub(r'<!-- BLOG -->.*?<!-- FAQ -->', '<!-- FAQ -->')
sub(r'<!-- FAQ -->.*?<!-- NEWSLETTER -->', '<!-- NEWSLETTER -->')
sub(r'<!-- NEWSLETTER -->.*?<!-- FOOTER -->', '<!-- FOOTER -->')

# --- footer → absolute + new pages ---
FOOTER = '''<footer>
    <div class="wrap">
      <div class="foot-grid">
        <div>
          <a class="logo" href="/"><span class="dot">✦</span> Glint AI</a>
          <p style="margin:0;">The everyday AI toolkit for creators &amp; marketers. Built to be an asset you own.</p>
        </div>
        <div><h4>Tools</h4><a href="/tools/">All 16 tools</a><a href="/tools/ai-humanizer.html">AI Humanizer</a><a href="/tools/ai-text-summarizer.html">Text Summarizer</a><a href="/tools/grammar-checker.html">Grammar Checker</a><a href="/tools/background-remover.html">Background Remover</a><a href="/tools/serp-preview.html">SERP Preview</a></div>
        <div><h4>Resources</h4><a href="/blog/">Blog &amp; guides</a><a href="/resources/">Free templates</a><a href="/ai-tools/">Tool reviews</a><a href="/extension/">Chrome extension</a></div>
        <div><h4>Company</h4><a href="/#pricing">Pricing</a><a href="/#features">Why Glint</a><a href="/#faq">FAQ</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a></div>
      </div>
      <div class="copy">© 2026 Glint AI. Payments via PayPal · Accounts via Supabase — configure in <code>supabase-auth.js</code> (see SETUP.md) to go live.</div>
    </div>
  </footer>'''
sub(r'<!-- FOOTER -->.*?</footer>', '<!-- FOOTER -->\n' + FOOTER)

# --- absolute script srcs (page lives in /tools/) ---
s = s.replace('src="vendor/supabase.min.js"', 'src="/vendor/supabase.min.js"')
s = s.replace('src="supabase-auth.js"', 'src="/supabase-auth.js"')
s = s.replace('src="p2-tools.js"', 'src="/p2-tools.js"')

import os
os.makedirs("tools", exist_ok=True)
open("tools/index.html", "w", encoding="utf-8").write(s)
print("OK: tools/index.html written (%d lines)" % s.count("\n"))
