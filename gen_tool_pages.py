# -*- coding: utf-8 -*-
"""Generate dedicated, SEO-optimized landing pages for Glint AI's 9 core tools.
Each page gets a unique URL, canonical, Open Graph tags, and JSON-LD
(SoftwareApplication + FAQPage). Panel UI is reused verbatim from index.html.
"""
import json, os

OUT = "tools"
os.makedirs(OUT, exist_ok=True)

# ---- Panel UI (verbatim from index.html, only the .tool-card block) ----
PANELS = {
"sum": '''<div class="tool-card">
  <h3>📝 AI Text Summarizer</h3>
  <div class="sub">Extractive summary using sentence-frequency scoring. <em>Free mode runs locally — Pro unlocks GPT-level abstractive summaries.</em></div>
  <textarea id="sumIn" rows="8" placeholder="Paste your article, transcript, or notes here…"></textarea>
  <div class="row">
    <div>
      <label for="sumRatio">Summary length</label>
      <input type="range" id="sumRatio" min="10" max="60" value="30" style="width:100%">
      <span class="hint" id="sumRatioLbl">~30% of original</span>
    </div>
    <div style="flex:0 0 auto; align-self:flex-end;">
      <button class="btn btn-primary mini" onclick="runSummarize()">Summarize</button>
    </div>
  </div>
  <div class="out" id="sumOut">Your summary will appear here.</div>
</div>''',

"read": '''<div class="tool-card">
  <h3>📊 Word &amp; Readability Analyzer</h3>
  <div class="sub">Live counts and a Flesch-style reading-ease estimate. Great for SEO and email copy.</div>
  <textarea id="readIn" rows="8" placeholder="Type or paste your copy here…" oninput="runRead()"></textarea>
  <div class="stats" id="readStats">
    <div class="stat"><b id="sWords">0</b><span>Words</span></div>
    <div class="stat"><b id="sChars">0</b><span>Characters</span></div>
    <div class="stat"><b id="sSent">0</b><span>Sentences</span></div>
    <div class="stat"><b id="sRead">0s</b><span>Read time</span></div>
    <div class="stat"><b id="sScore">–</b><span>Reading ease</span></div>
  </div>
  <div class="hint" id="readHint">Start typing to see live stats.</div>
</div>''',

"md": '''<div class="tool-card">
  <h3>⇄ Markdown ↔ HTML</h3>
  <div class="sub">Convert Markdown to clean HTML, or strip HTML back to Markdown.</div>
  <label for="mdIn">Markdown input</label>
  <textarea id="mdIn" rows="7" placeholder="# Heading&#10;&#10;Write **bold** and *italic*, lists, links…"></textarea>
  <div class="row" style="flex:0 0 auto;">
    <button class="btn btn-primary mini" onclick="mdToHtml()">Markdown → HTML</button>
    <button class="btn btn-ghost mini" onclick="htmlToMd()">HTML → Markdown</button>
    <button class="btn btn-ghost mini" onclick="copyOut('mdOut')">Copy</button>
  </div>
  <label for="mdOut">Output</label>
  <div class="out" id="mdOut">Output appears here.</div>
</div>''',

"json": '''<div class="tool-card">
  <h3>{} JSON Formatter &amp; Validator</h3>
  <div class="sub">Pretty-print, minify, and validate JSON instantly.</div>
  <textarea id="jsonIn" rows="8" placeholder="{'name':'Glint','tools':['summarize','format']}"></textarea>
  <div class="row" style="flex:0 0 auto;">
    <button class="btn btn-primary mini" onclick="jsonFmt()">Format</button>
    <button class="btn btn-ghost mini" onclick="jsonMin()">Minify</button>
    <button class="btn btn-ghost mini" onclick="copyOut('jsonOut')">Copy</button>
  </div>
  <div class="out" id="jsonOut">Result appears here.</div>
</div>''',

"pw": '''<div class="tool-card">
  <h3>🔐 Password &amp; Key Generator</h3>
  <div class="sub">Strong random passwords and API keys, generated locally.</div>
  <div class="row">
    <div>
      <label for="pwLen">Length: <span id="pwLenLbl">16</span></label>
      <input type="range" id="pwLen" min="6" max="64" value="16" oninput="document.getElementById('pwLenLbl').textContent=this.value" style="width:100%">
    </div>
  </div>
  <div class="row">
    <label style="flex:0 0 auto;"><input type="checkbox" id="pwUpper" checked style="width:auto;margin-right:6px;"> A-Z</label>
    <label style="flex:0 0 auto;"><input type="checkbox" id="pwLower" checked style="width:auto;margin-right:6px;"> a-z</label>
    <label style="flex:0 0 auto;"><input type="checkbox" id="pwNum" checked style="width:auto;margin-right:6px;"> 0-9</label>
    <label style="flex:0 0 auto;"><input type="checkbox" id="pwSym" style="width:auto;margin-right:6px;"> !@#$</label>
  </div>
  <div class="row" style="flex:0 0 auto; margin-top:10px;">
    <button class="btn btn-primary mini" onclick="genPw()">Generate</button>
    <button class="btn btn-ghost mini" onclick="copyOut('pwOut')">Copy</button>
  </div>
  <div class="out" id="pwOut" style="font-family:monospace;font-size:16px;">Click Generate.</div>
</div>''',

"yt": '''<div class="tool-card">
  <h3>🎬 YouTube Title &amp; Hook Generator</h3>
  <div class="sub">Drop a topic and keywords; get scroll-stopping titles and opening hooks. Runs locally — Pro adds AI tone tuning.</div>
  <textarea id="ytTopic" rows="4" placeholder="e.g. how to start a faceless YouTube channel"></textarea>
  <input id="ytKw" type="text" placeholder="Optional keywords (comma separated)" style="width:100%;margin-top:10px;padding:10px;border:1px solid var(--line);border-radius:10px;">
  <div class="row" style="flex:0 0 auto;margin-top:10px;">
    <button class="btn btn-primary mini" onclick="genYt()">Generate</button>
    <button class="btn btn-ghost mini" onclick="copyOut('ytOut')">Copy</button>
  </div>
  <div class="out" id="ytOut" style="white-space:pre-wrap;">Titles and hooks appear here.</div>
</div>''',

"hash": '''<div class="tool-card">
  <h3>#️⃣ Hashtag Generator</h3>
  <div class="sub">Enter a niche or topic; get grouped hashtags for Instagram, TikTok, YouTube, and X. No account needed.</div>
  <input id="hashTopic" type="text" placeholder="e.g. travel vlog, skincare, productivity" style="width:100%;padding:10px;border:1px solid var(--line);border-radius:10px;">
  <div class="row" style="flex:0 0 auto;margin-top:10px;">
    <button class="btn btn-primary mini" onclick="genHash()">Generate</button>
    <button class="btn btn-ghost mini" onclick="copyOut('hashOut')">Copy</button>
  </div>
  <div class="out" id="hashOut" style="white-space:pre-wrap;">Hashtags appear here.</div>
</div>''',

"serp": '''<div class="tool-card">
  <h3>🔎 SERP &amp; Meta Preview</h3>
  <div class="sub">See how your page looks in Google and whether title/description lengths are in the safe zone.</div>
  <input id="serpTitle" type="text" placeholder="Page title (≤ 60 chars ideal)" style="width:100%;padding:10px;border:1px solid var(--line);border-radius:10px;margin-bottom:8px;">
  <input id="serpUrl" type="text" placeholder="https://yoursite.com/page" style="width:100%;padding:10px;border:1px solid var(--line);border-radius:10px;margin-bottom:8px;">
  <textarea id="serpDesc" rows="3" placeholder="Meta description (≤ 155 chars ideal)"></textarea>
  <div class="row" style="flex:0 0 auto;margin-top:10px;"><button class="btn btn-primary mini" onclick="serpPreview()">Preview</button></div>
  <div class="out" id="serpOut" style="white-space:normal;background:#fff;color:#202124;border:1px solid #dfe1e5;border-radius:8px;">
    <div style="color:#202124;font-size:13px;margin-bottom:2px;" id="serpUrlPrev">yoursite.com › page</div>
    <div style="color:#1a0dab;font-size:20px;line-height:1.3;" id="serpTitlePrev">Page title preview</div>
    <div style="color:#4d5156;font-size:14px;line-height:1.4;" id="serpDescPrev">Meta description preview text appears here.</div>
    <div class="hint" id="serpHint" style="margin-top:8px;color:#70757a;">Tip: keep titles under 60 and descriptions under 155 characters.</div>
  </div>
</div>''',

"wc": '''<div class="tool-card">
  <h3>🔢 Word &amp; Character Counter</h3>
  <div class="sub">Live counts with platform limits for X, Instagram, YouTube, and meta tags.</div>
  <textarea id="wcIn" rows="8" placeholder="Type or paste your text here…" oninput="wcCount()"></textarea>
  <div class="stats" id="wcStats">
    <div class="stat"><b id="wcWords">0</b><span>Words</span></div>
    <div class="stat"><b id="wcChars">0</b><span>Characters</span></div>
    <div class="stat"><b id="wcCharsNo">0</b><span>No spaces</span></div>
    <div class="stat"><b id="wcSent">0</b><span>Sentences</span></div>
    <div class="stat"><b id="wcPara">0</b><span>Paragraphs</span></div>
    <div class="stat"><b id="wcRead">0m</b><span>Read time</span></div>
  </div>
  <div class="hint" id="wcHint">Start typing to see live counts.</div>
</div>''',
}

# ---- Tool specs (SEO copy + FAQ + internal links) ----
TOOLS = [
{
  "slug": "ai-text-summarizer", "key": "sum", "name": "AI Text Summarizer",
  "title": "Free AI Text Summarizer — Glint AI",
  "meta": "Summarize articles, transcripts, and notes in seconds with Glint's free AI text summarizer. Runs in your browser, no signup, no upload.",
  "keywords": "ai text summarizer, summarize text, article summarizer, text summary tool, free summarizer",
  "intro": "Paste any article, transcript, or meeting notes and get a tight extractive summary in seconds. Glint's summarizer scores sentences by keyword frequency and keeps the most important ones — entirely in your browser, so your text never leaves the page.",
  "steps": [
    "Paste your text into the box above.",
    "Drag the length slider to set how short you want the summary (10–60% of the original).",
    "Hit Summarize and copy the result. A Pro plan adds GPT-level abstractive summaries.",
  ],
  "faq": [
    ("Is the AI text summarizer really free?", "Yes. The extractive summarizer runs 100% in your browser and is free forever. A Pro plan adds GPT-powered abstractive summaries."),
    ("Do you upload my text to a server?", "No. The free summarizer processes everything locally in your browser. Nothing is sent to our servers, which keeps your drafts private."),
    ("What is the difference between extractive and abstractive summarization?", "Extractive picks and keeps the most important existing sentences. Abstractive rewrites the content in new words using a language model — a Pro feature for when you need smoother output."),
  ],
  "related": [("/blog/summarize-pdf-guide.html","How to Summarize a PDF in Minutes"), ("/blog/humanize-ai-text.html","How to Humanize AI Text So Detectors Don't Flag It")],
},
{
  "slug": "word-readability-analyzer", "key": "read", "name": "Word & Readability Analyzer",
  "title": "Free Word & Readability Analyzer — Glint AI",
  "meta": "Check reading ease, word count, sentence length, and reading time instantly. Glint's readability analyzer helps you write clearer SEO and email copy.",
  "keywords": "readability analyzer, reading ease score, flesch reading ease, word count tool, readability checker",
  "intro": "See how easy your copy is to read before you publish. Glint scores reading ease with a Flesch-style estimate and shows live word, sentence, and paragraph counts — ideal for SEO pages, emails, and landing copy.",
  "steps": [
    "Paste or type your copy into the box above.",
    "Watch the live stats update as you write.",
    "Aim for a reading-ease score in the 60–80 range for broad audiences; tighten long sentences if the score drops.",
  ],
  "faq": [
    ("What is a good reading ease score?", "On the Flesch scale, 60–70 is 'standard' and readable for most adults, 70–90 is 'easy'. Aim for 60+ for general web and SEO copy."),
    ("Does the readability analyzer store my text?", "No. Analysis happens in your browser; nothing is uploaded or saved."),
    ("Why does readability matter for SEO?", "Readable pages keep visitors engaged and reduce bounce rate. Clear copy also tends to earn more featured snippets and longer dwell time."),
  ],
  "related": [("/blog/meta-description-ctr-guide.html","How to Write Meta Descriptions That Improve CTR"), ("/blog/serp-preview-meta-tags.html","SERP and Meta Tag Preview Guide")],
},
{
  "slug": "markdown-to-html", "key": "md", "name": "Markdown ↔ HTML Converter",
  "title": "Free Markdown to HTML Converter — Glint AI",
  "meta": "Convert Markdown to clean HTML or strip HTML back to Markdown instantly. Free, browser-based, no signup required.",
  "keywords": "markdown to html, html to markdown, markdown converter, md to html, convert markdown",
  "intro": "Flip between Markdown and HTML in one click. Perfect for writing docs, formatting blog posts, or cleaning up pasted content — all processed locally in your browser.",
  "steps": [
    "Paste Markdown (or HTML) into the input box.",
    "Click Markdown → HTML to render clean HTML, or HTML → Markdown to strip it back.",
    "Copy the result and paste it wherever you need it.",
  ],
  "faq": [
    ("Is this Markdown to HTML converter free?", "Yes, completely free and runs in your browser with no account."),
    ("Does it support tables and code blocks?", "The converter handles headings, bold, italic, lists, links, and images. Complex tables and fenced code blocks are best done with a fuller Markdown parser, but most everyday content converts cleanly."),
    ("Is my content uploaded anywhere?", "No. Conversion happens entirely on your device."),
  ],
  "related": [("/blog/ai-content-detector-guide.html","How Accurate Are AI Detectors, Really?"), ("/blog/paraphrase-without-losing-meaning.html","How to Paraphrase Without Losing Meaning")],
},
{
  "slug": "json-formatter", "key": "json", "name": "JSON Formatter & Validator",
  "title": "Free JSON Formatter & Validator — Glint AI",
  "meta": "Pretty-print, minify, and validate JSON instantly in your browser. No upload, no signup — just paste and format.",
  "keywords": "json formatter, json validator, format json, json minify, pretty print json, validate json",
  "intro": "Paste any JSON and get it pretty-printed, minified, or validated in a click. Great for API responses, config files, and debugging — and it runs entirely in your browser.",
  "steps": [
    "Paste your JSON into the box above.",
    "Click Format for readable, indented output, or Minify to shrink it for transport.",
    "If the JSON is invalid, the tool tells you exactly what went wrong.",
  ],
  "faq": [
    ("Is the JSON formatter safe to use with secrets?", "Formatting happens locally in your browser — your JSON is never sent to a server. Still, avoid pasting production secrets into any web tool as a habit."),
    ("What does 'Invalid JSON' mean?", "It means the syntax is malformed — a missing comma, unquoted key, or trailing comma. The error message points to the problem so you can fix it."),
    ("Can I minify JSON for production?", "Yes. Minify strips whitespace to reduce payload size, which is useful for APIs and config files."),
  ],
  "related": [("/blog/generate-api-keys-safely.html","How to Generate and Store API Keys Safely"), ("/blog/ai-prompt-engineering-guide.html","Prompt Engineering Guide for Better AI Output")],
},
{
  "slug": "password-generator", "key": "pw", "name": "Password & Key Generator",
  "title": "Free Password & API Key Generator — Glint AI",
  "meta": "Generate strong random passwords and API keys locally in your browser. No upload, no tracking — just secure credentials in one click.",
  "keywords": "password generator, strong password, api key generator, random password, secure password",
  "intro": "Create strong, random passwords and API keys with full control over length and character sets. Everything is generated in your browser, so nothing is transmitted or logged.",
  "steps": [
    "Set the length with the slider (6–64 characters).",
    "Pick character sets: uppercase, lowercase, numbers, symbols.",
    "Click Generate, then copy the result. Longer plus mixed sets means stronger.",
  ],
  "faq": [
    ("How strong are these passwords?", "They use your browser's cryptographically secure random generator with the sets you select. 16+ mixed characters is strong for most accounts."),
    ("Do you store or transmit generated passwords?", "No. Generation happens on your device and is never uploaded or saved."),
    ("Should I use this for API keys too?", "Yes — generate a long random key here, then store it safely. See our guide on handling API keys responsibly."),
  ],
  "related": [("/blog/generate-api-keys-safely.html","How to Generate and Store API Keys Safely"), ("/blog/ai-essay-writer-guide.html","AI Essay Writer Guide")],
},
{
  "slug": "youtube-title-generator", "key": "yt", "name": "YouTube Title & Hook Generator",
  "title": "Free YouTube Title & Hook Generator — Glint AI",
  "meta": "Generate scroll-stopping YouTube titles and opening hooks from any topic. Free, browser-based, no signup.",
  "keywords": "youtube title generator, youtube title ideas, video hook generator, youtube headline generator",
  "intro": "Turn a topic into a list of click-worthy titles and opening hooks. Great for beating blank-page syndrome and A/B testing thumbnails — runs locally, no account needed.",
  "steps": [
    "Describe your video topic in the box above.",
    "Optionally add comma-separated keywords for tighter suggestions.",
    "Click Generate, then copy the titles and hooks you like.",
  ],
  "faq": [
    ("Are the titles SEO-friendly?", "They follow proven patterns (how-to, mistake, beginner's guide) that match common search intent. Pair them with your target keyword for best results."),
    ("Does this tool upload my topic?", "No. Generation runs in your browser."),
    ("How do I pick the best title?", "Match the title to your video's actual content and your keyword. Test two variants and keep the one with better click-through."),
  ],
  "related": [("/blog/ai-prompt-engineering-guide.html","Prompt Engineering Guide for Better AI Output"), ("/blog/meta-description-ctr-guide.html","How to Write Meta Descriptions That Improve CTR")],
},
{
  "slug": "hashtag-generator", "key": "hash", "name": "Hashtag Generator",
  "title": "Free Hashtag Generator for Instagram, TikTok & YouTube — Glint AI",
  "meta": "Get grouped hashtags for Instagram, TikTok, YouTube, and X in one click. Free, no account, runs in your browser.",
  "keywords": "hashtag generator, instagram hashtags, tiktok hashtags, youtube hashtags, hashtag tool",
  "intro": "Enter a niche or topic and get organized hashtag sets for Instagram, TikTok, YouTube, and X. Build reach without juggling spreadsheets — all in your browser.",
  "steps": [
    "Type a niche or topic (e.g. travel vlog, skincare).",
    "Click Generate to get grouped sets per platform.",
    "Copy the set for the platform you are posting to.",
  ],
  "faq": [
    ("How many hashtags should I use?", "Instagram allows up to 30 (10–15 is a safe sweet spot); TikTok and YouTube favor fewer, more relevant tags. The tool gives you sets sized per platform."),
    ("Does the generator need an account?", "No. It runs entirely in your browser."),
    ("Are these hashtags guaranteed to grow my reach?", "No tool can guarantee reach, but relevant, specific hashtags help the right audience discover your content."),
  ],
  "related": [("/blog/ai-prompt-engineering-guide.html","Prompt Engineering Guide for Better AI Output"), ("/blog/humanize-ai-text.html","How to Humanize AI Text So Detectors Don't Flag It")],
},
{
  "slug": "serp-preview", "key": "serp", "name": "SERP & Meta Preview",
  "title": "Free SERP & Meta Tag Preview Tool — Glint AI",
  "meta": "Preview how your page appears in Google and check title/description length. Free SERP snippet tool, no signup.",
  "keywords": "serp preview, meta tag preview, google snippet preview, meta description checker, title length checker",
  "intro": "See exactly how your page will look in Google search results and whether your title and description stay within the safe length zones. Essential pre-publish SEO QA.",
  "steps": [
    "Enter your page title, URL, and meta description.",
    "Click Preview to render the Google-style snippet.",
    "Adjust until the title is at most 60 and description at most 155 characters.",
  ],
  "faq": [
    ("What is the ideal meta title length?", "Aim for 50–60 characters. Google typically truncates around 60."),
    ("What is the ideal meta description length?", "Keep it under 155 characters so it is not cut off in results."),
    ("Does previewing upload my data?", "No. The preview is rendered locally in your browser."),
  ],
  "related": [("/blog/meta-description-ctr-guide.html","How to Write Meta Descriptions That Improve CTR"), ("/blog/serp-preview-meta-tags.html","SERP and Meta Tag Preview Guide")],
},
{
  "slug": "word-counter", "key": "wc", "name": "Word & Character Counter",
  "title": "Free Word & Character Counter — Glint AI",
  "meta": "Count words, characters, sentences, and paragraphs with live platform limits for X, Instagram, YouTube, and meta tags. Free, no signup.",
  "keywords": "word counter, character counter, count words, character count tool, word count online",
  "intro": "Get instant word, character, sentence, and paragraph counts with built-in limit checks for X, Instagram, YouTube, and meta descriptions. Perfect for social posts and SEO copy.",
  "steps": [
    "Paste or type your text into the box above.",
    "Watch the live counts and limit warnings update as you write.",
    "Use the read-time estimate to gauge pacing.",
  ],
  "faq": [
    ("What are the character limits shown?", "The tool flags the 280-char X limit, 2,200-char Instagram caption limit, and 5,000-char YouTube description limit, plus meta tag guidance."),
    ("Does the counter upload my text?", "No. Counting happens in your browser."),
    ("Is there a word counter for essays?", "Yes — the word and paragraph counts work for any long-form text, including essays and articles."),
  ],
  "related": [("/blog/ai-essay-writer-guide.html","AI Essay Writer Guide"), ("/blog/meta-description-ctr-guide.html","How to Write Meta Descriptions That Improve CTR")],
},
]

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>%%TITLE%%</title>
  <meta name="description" content="%%META%%" />
  <meta name="keywords" content="%%KEYWORDS%%" />
  <link rel="canonical" href="%%CANONICAL%%" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="%%OG_TITLE%%" />
  <meta property="og:description" content="%%OG_DESC%%" />
  <meta property="og:url" content="%%CANONICAL%%" />
  <meta property="og:site_name" content="Glint AI" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="/icon.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="/assets/tools.css" />
  %%LD_JSON%%
</head>
<body>
  <header class="nav">
    <div class="wrap nav-inner">
      <a class="logo" href="/index.html"><span class="dot">✦</span> Glint AI</a>
      <nav class="nav-links">
        <a href="/index.html#tools">Tools</a>
        <a href="/index.html#blog">Blog</a>
        <a href="/index.html#pricing">Pricing</a>
      </nav>
    </div>
  </header>

  <main class="wrap tool-page">
    <nav class="crumbs"><a href="/index.html">Home</a> › <span>%%H1%%</span></nav>
    <h1>%%H1%%</h1>
    <p class="lede">%%INTRO%%</p>
    <section class="tool-card-wrap">%%PANEL%%</section>
    <section class="how">
      <h2>How to use the %%H1%%</h2>
      <ol>%%STEPS%%</ol>
    </section>
    <section class="faq">
      <h2>Frequently asked questions</h2>
      %%FAQ%%
    </section>
    <section class="related">
      <h2>Related guides</h2>
      <ul>%%RELATED%%</ul>
    </section>
  </main>

  <footer class="foot">
    <div class="wrap">
      <a class="logo" href="/index.html"><span class="dot">✦</span> Glint AI</a>
      <p>Free AI tools for creators, marketers and solo founders.</p>
      <p class="muted"><a href="/index.html#tools">All tools</a> · <a href="/index.html#blog">Blog</a> · <a href="/index.html#pricing">Pricing</a></p>
    </div>
  </footer>
  <script src="/assets/tools.js"></script>
</body>
</html>'''

def build_ld(t):
    soft = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": t["name"],
        "operatingSystem": "Web",
        "applicationCategory": "UtilitiesApplication",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "url": "https://glintai.tools/tools/" + t["slug"] + ".html",
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for (q, a) in t["faq"]
        ],
    }
    return ('<script type="application/ld+json">' + json.dumps(soft, ensure_ascii=False) + '</script>\n  '
            + '<script type="application/ld+json">' + json.dumps(faq, ensure_ascii=False) + '</script>')

for t in TOOLS:
    steps_html = "".join("<li>" + s + "</li>" for s in t["steps"])
    faq_html = "".join('<div class="qa"><h3>' + q + "</h3><p>" + a + "</p></div>" for (q, a) in t["faq"])
    related_html = "".join('<li><a href="' + u + '">' + title + "</a></li>" for (u, title) in t["related"])
    html = (TEMPLATE
        .replace("%%TITLE%%", t["title"])
        .replace("%%META%%", t["meta"])
        .replace("%%KEYWORDS%%", t["keywords"])
        .replace("%%CANONICAL%%", "https://glintai.tools/tools/" + t["slug"] + ".html")
        .replace("%%OG_TITLE%%", t["title"])
        .replace("%%OG_DESC%%", t["meta"])
        .replace("%%LD_JSON%%", build_ld(t))
        .replace("%%H1%%", t["name"])
        .replace("%%INTRO%%", t["intro"])
        .replace("%%PANEL%%", PANELS[t["key"]])
        .replace("%%STEPS%%", steps_html)
        .replace("%%FAQ%%", faq_html)
        .replace("%%RELATED%%", related_html))
    with open(os.path.join(OUT, t["slug"] + ".html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", t["slug"] + ".html")
print("done:", len(TOOLS), "pages")
