#!/usr/bin/env python3
"""
GEO content enhancement for Glint AI flagship blog posts.

Adds two high-leverage, machine-extractable blocks to each chosen post:
  1) Key Takeaways  -> <aside> right after the intro (LLMs love concise answers)
  2) Sources & further reading -> <section> before the author bio (E-E-A-T via
     authoritative outbound links + internal Glint links)

Idempotent: each block carries its own marker and is skipped if already present.
GEO CSS is appended once to the existing <style> block.
"""
import os

BLOG = "blog"

GEO_CSS = """
/* GEO-CSS */
.geo-takeaways{margin:24px 0;padding:18px 20px;border:1px solid rgba(0,240,255,.35);border-left:4px solid var(--brand);border-radius:14px;background:rgba(0,240,255,.06);box-shadow:0 0 24px rgba(0,240,255,.10)}
.geo-takeaways h3{margin:0 0 10px;font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:var(--brand)}
.geo-takeaways ul{margin:0;padding-left:20px}
.geo-takeaways li{margin:7px 0;color:var(--text);font-size:15px;line-height:1.6}
.geo-takeaways li b{color:var(--brand)}
.geo-sources{margin:34px 0 0;padding:20px 22px;border:1px solid var(--line);border-radius:14px;background:var(--soft)}
.geo-sources h2{margin:0 0 12px;font-size:20px;color:var(--text)}
.geo-sources ul{margin:0;padding-left:20px}
.geo-sources li{margin:9px 0;color:var(--muted);font-size:14.5px;line-height:1.65}
.geo-sources a{color:var(--brand);font-weight:600}
"""

# slug -> {takeaways:[...], sources:[(label, url, note), ...]}
DATA = {
    "best-free-json-formatter": {
        "takeaways": [
            "A JSON formatter turns one cramped line of API or config text into clean, indented, readable data in seconds.",
            "The biggest risk is privacy: server-side formatters may log or store pasted API keys, tokens, and customer records.",
            "Only Glint AI and QuickType process JSON fully client-side by default; Glint AI adds no signup and no storage.",
            "Good formatters report the exact line and column of a syntax error (trailing comma, missing quote, single quotes).",
            "Match the tool to the data: public samples can use any tool; secrets and personal data belong in a browser-only formatter.",
        ],
        "sources": [
            ("JSON.org", "https://www.json.org/json-en.html", "The official JSON syntax reference."),
            ("MDN: JSON", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON", "How browsers parse and stringify JSON."),
            ("Glint AI JSON Formatter", "/tools/json-formatter.html", "Free, client-side, no-signup formatter."),
            ("Why marketers need a JSON formatter", "/blog/why-marketers-need-a-json-formatter.html", "Everyday cases beyond engineering."),
        ],
    },
    "grammarly-alternative-free": {
        "takeaways": [
            "Grammarly's free plan hides many corrections behind a paid wall; free alternatives give accurate checks with no account.",
            "The best free Grammarly alternatives cover grammar, clarity, and tone without uploading your drafts to a server.",
            "Glint AI Grammar Checker is free, no signup, and runs privacy-first in your browser.",
            "Pick by use case: students, non-native writers, and quick email fixes each favor a different tool.",
            "You can switch without losing flow by exporting your text and pasting it into a browser-based checker.",
        ],
        "sources": [
            ("Purdue OWL: Grammar", "https://owl.purdue.edu/owl/general_writing/grammar/index.html", "Authoritative grammar reference."),
            ("Google: Helpful content", "https://developers.google.com/search/docs/fundamentals/creating-helpful-content", "Write clearly for people first."),
            ("Glint AI Grammar Checker", "/tools/grammar-checker.html", "Free, no-signup grammar help."),
            ("Free grammar checker, no signup", "/blog/free-grammar-checker-no-signup.html", "Why no-account checking wins."),
        ],
    },
    "quillbot-alternative-free": {
        "takeaways": [
            "QuillBot's free tier caps you at 125 words and one mode; free alternatives lift the limit and open more modes.",
            "A good free QuillBot alternative paraphrases without uploading your text to a server.",
            "Glint AI Paraphraser is unlimited, free, and needs no signup.",
            "Paraphrasing should preserve meaning: rework structure and vocabulary, do not just swap synonyms.",
            "Choose by use case: academic, SEO, or everyday rewriting each need different controls.",
        ],
        "sources": [
            ("Purdue OWL: Paraphrasing", "https://owl.purdue.edu/owl/research_and_citation/using_research/quoting_paraphrasing/index.html", "How to paraphrase without plagiarizing."),
            ("Glint AI Paraphraser", "/tools/paraphraser.html", "Unlimited, free, browser-only."),
            ("Paraphrase without plagiarizing", "/blog/paraphrase-without-plagiarizing.html", "Responsible rewriting workflow."),
            ("Glint AI Humanizer", "/tools/ai-humanizer.html", "Natural-sounding rewrites."),
        ],
    },
    "private-ai-detector": {
        "takeaways": [
            "A private AI detector checks whether text reads as AI-generated without sending your draft to a server or forcing signup.",
            "Detection works by spotting statistical patterns (perplexity, burstiness); it estimates likelihood, it does not prove authorship.",
            "Pair it with a humanizer or paraphraser when you want text to read more naturally, not to 'trick' detectors.",
            "Read the score as a probability: a high percentage means 'looks machine-like,' not 'definitely AI.'",
            "Use it for self-checking your own drafts, not for accusing others; detectors have real false-positive limits.",
        ],
        "sources": [
            ("Google: AI-generated content", "https://developers.google.com/search/docs/appearance/ai-generated-content", "Disclosure expectations for AI-assisted writing."),
            ("EFF: Privacy", "https://www.eff.org/issues/privacy", "Why client-side processing protects you."),
            ("Glint AI Content Detector", "/tools/ai-content-detector.html", "Private, in-browser detection."),
            ("Glint AI Humanizer", "/tools/ai-humanizer.html", "Make writing sound natural."),
        ],
    },
    "free-grammar-checker-no-signup": {
        "takeaways": [
            "A no-sign-up grammar checker lets you paste text, get fixes, and leave, with no email and no trial to cancel.",
            "Good free checkers catch grammar, spelling, clarity, and punctuation issues in one pass.",
            "They sit between a full editor and nothing: fastest for quick cleanups before sending.",
            "Free vs paid mostly loses advanced style and tone suggestions, not core correctness.",
            "Run a 30-second pre-send checklist: grammar, then clarity, then one human read.",
        ],
        "sources": [
            ("Purdue OWL: Grammar", "https://owl.purdue.edu/owl/general_writing/grammar/index.html", "Grammar reference."),
            ("Glint AI Grammar Checker", "/tools/grammar-checker.html", "Free, no-signup checker."),
            ("Free Grammarly alternatives", "/blog/grammarly-alternative-free.html", "Compared side by side."),
            ("Glint AI Privacy", "/privacy/", "How Glint AI keeps your text local."),
        ],
    },
    "humanize-ai-text": {
        "takeaways": [
            "AI text gets flagged because it leans on predictable phrasing, uniform sentence length, and filler transitions.",
            "Humanizing means making writing sound natural, vary rhythm, cut fluff, add a specific detail, not 'bypassing' detectors.",
            "Five fast fixes: shorten sentences, drop 'delve/leverage/tapestry,' use active voice, add a concrete example, read aloud.",
            "Glint AI Humanizer applies light, local edits so drafts read more like you wrote them.",
            "Do not humanize factual or regulated content where you must preserve exact wording.",
        ],
        "sources": [
            ("Google: AI-generated content", "https://developers.google.com/search/docs/appearance/ai-generated-content", "Write for people first."),
            ("Glint AI Humanizer", "/tools/ai-humanizer.html", "Light, local natural-sounding edits."),
            ("Glint AI Content Detector", "/tools/ai-content-detector.html", "Check before you publish."),
            ("Private AI detector guide", "/blog/private-ai-detector.html", "Understand how detection works."),
        ],
    },
    "best-free-serp-preview-tool": {
        "takeaways": [
            "A SERP preview tool shows how your title and meta description render in Google before you publish.",
            "CTR depends on a title under about 60 characters and a meta description around 150 to 160 characters that earns the click.",
            "The best free simulators are pixel-accurate and need no signup; mobile truncation matters most.",
            "Glint AI SERP Preview is free, browser-only, and previews both desktop and mobile.",
            "Write titles for the query, descriptions for the click: match search intent, then differentiate.",
        ],
        "sources": [
            ("Google: Snippet guidelines", "https://developers.google.com/search/docs/appearance/snippet", "Title and meta best practices."),
            ("Google: Helpful content", "https://developers.google.com/search/docs/fundamentals/creating-helpful-content", "Write for people first."),
            ("Glint AI SERP Preview", "/tools/serp-preview.html", "Free, pixel-accurate preview."),
            ("Meta description CTR guide", "/blog/meta-description-ctr-guide.html", "Copy tips that win clicks."),
        ],
    },
    "best-free-markdown-to-html-converter": {
        "takeaways": [
            "A Markdown to HTML converter turns plain-text drafts into clean, publishable HTML in seconds.",
            "The best free converters preview live and never upload your file to a server.",
            "Check GFM support: tables and fenced code blocks only render correctly in some tools.",
            "Glint AI Markdown to HTML is browser-only, live-preview, and needs no upload.",
            "Paste clean HTML into your CMS, no copy-paste formatting ghosts from a word processor.",
        ],
        "sources": [
            ("CommonMark", "https://commonmark.org/", "The Markdown specification."),
            ("GitHub Flavored Markdown", "https://github.github.com/gfm/", "Tables and code-block spec."),
            ("Glint AI Markdown to HTML", "/tools/markdown-to.html", "Live preview, browser-only."),
            ("Markdown to HTML workflow", "/blog/markdown-to-html-workflow.html", "Workflow tips."),
        ],
    },
}


def build_takeaways(items):
    lis = "\n".join(f"    <li>{t}</li>" for t in items)
    return (
        "<!-- GEO-TAKEAWAYS -->\n"
        '<aside class="geo-takeaways" aria-label="Key takeaways">\n'
        "  <h3>Key takeaways</h3>\n"
        "  <ul>\n"
        f"{lis}\n"
        "  </ul>\n"
        "</aside>\n"
    )


def build_sources(items):
    lis = "\n".join(
        f'    <li><a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a> &mdash; {note}</li>'
        for (label, url, note) in items
    )
    return (
        "<!-- GEO-SOURCES -->\n"
        '<section class="geo-sources" aria-label="Sources and further reading">\n'
        "  <h2>Sources &amp; further reading</h2>\n"
        "  <ul>\n"
        f"{lis}\n"
        "  </ul>\n"
        "</section>\n"
    )


def enhance(slug, d):
    path = os.path.join(BLOG, f"{slug}.html")
    if not os.path.exists(path):
        return (slug, "MISSING")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False

    # 1) CSS (once)
    if "/* GEO-CSS */" not in html:
        if "</style>" not in html:
            return (slug, "NO-STYLE")
        html = html.replace("</style>", GEO_CSS + "</style>", 1)
        changed = True

    # 2) Key Takeaways before <div class="content">
    if "<!-- GEO-TAKEAWAYS -->" not in html:
        if '<div class="content">' not in html:
            return (slug, "NO-CONTENT-ANCHOR")
        block = build_takeaways(d["takeaways"])
        html = html.replace('<div class="content">', block + '<div class="content">', 1)
        changed = True

    # 3) Sources before <div class="author-bio"
    if "<!-- GEO-SOURCES -->" not in html:
        if 'class="author-bio"' not in html:
            return (slug, "NO-AUTHORBIO-ANCHOR")
        block = build_sources(d["sources"])
        html = html.replace('<div class="author-bio"', block + '\n<div class="author-bio"', 1)
        changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return (slug, "OK")
    return (slug, "SKIP")


def main():
    print(f"{'slug':40} {'result':22}")
    print("-" * 62)
    for slug, d in DATA.items():
        slug, res = enhance(slug, d)
        print(f"{slug:40} {res:22}")


if __name__ == "__main__":
    main()
