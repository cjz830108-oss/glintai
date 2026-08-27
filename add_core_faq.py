#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add FAQPage structured data + visible FAQ to core pages (idempotent).

- index.html: visible FAQ already exists -> inject FAQPage JSON-LD only.
- tools/index.html: add visible FAQ + FAQPage JSON-LD before footer.
- about/index.html: add visible FAQ + FAQPage JSON-LD before footer.

GEO rationale: pages that directly answer common questions are far more
likely to be cited verbatim by LLMs (Google SGE, ChatGPT browsing, Perplexity).
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---------- FAQ data ----------
INDEX_FAQ = [
    ("Is Glint AI really free?",
     "Yes — all 16 tools are free and run entirely in your browser. Pro adds AI-powered modes and the resource library."),
    ("Does my text get uploaded?",
     "No. Free tools process everything locally on your device. Pro AI features send text to the model only with your consent."),
    ("Will there be a Chrome extension?",
     "Yes. Each tool is designed to ship as a companion extension that drives traffic back to the hub (Pro feature)."),
    ("Can I use the tools commercially?",
     "Free tools are fine for commercial use. Team plan adds shared workspaces and white-label export."),
]

TOOLS_FAQ = [
    ("How many free tools are there?",
     "16 free, browser-based tools across writing, summarizing, analysis, formatting, SEO/social, and images."),
    ("Do I need to create an account?",
     "No. Every free tool runs locally in your browser with no signup. Accounts are only for Pro AI features."),
    ("Is my text uploaded to a server?",
     "Free tools process text on your device. Pro AI features send text to the model only when you choose."),
    ("What is the difference between Free and Pro?",
     "Free covers unlimited local use of all 16 tools. Pro adds GPT-level AI modes, the prompt library, Chrome extension access, and batch/API usage."),
]

ABOUT_FAQ = [
    ("What is Glint AI?",
     "Glint AI is the everyday AI toolkit for creators and marketers — 16 free browser-based tools plus a Pro plan for AI-powered modes."),
    ("Who builds Glint AI?",
     "A small team of writers, developers, and marketers who test every tool hands-on and publish privacy-first guides."),
    ("Is Glint AI free?",
     "Yes. All 16 tools are free forever; Pro is an optional upgrade for AI features."),
    ("How does Glint AI protect my privacy?",
     "Free tools run locally in your browser. We don't sell your data, and Pro AI features send text to the model only with your consent."),
]


def faq_jsonld(pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    }


def jsonld_script(obj):
    return ('  <script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=2)
            + '\n  </script>')


def visible_faq(pairs, marker):
    items = "\n".join(
        '      <div style="border:1px solid rgba(120,120,200,.22);border-radius:14px;padding:16px 20px;background:#0e0e1a;">\n'
        f'        <h3 style="margin:0 0 6px;font-size:17px;color:#e8e8f5;">{q}</h3>\n'
        f'        <p style="margin:0;color:#9aa0c0;font-size:15px;line-height:1.65;">{a}</p>\n'
        '      </div>' for q, a in pairs)
    return (
        f'  <!-- {marker} -->\n'
        '  <section id="faq" style="padding:56px 0;">\n'
        '    <div class="wrap" style="max-width:860px;">\n'
        '      <div style="text-align:center;margin-bottom:26px;"><h2 style="font-size:clamp(26px,4vw,36px);margin:0;letter-spacing:-.02em;color:#e8e8f5;">Frequently asked questions</h2></div>\n'
        '      <div style="display:grid;gap:14px;">\n'
        f'{items}\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>'
    )


def main():
    # 1) index.html — JSON-LD only (visible FAQ exists)
    p = os.path.join(ROOT, "index.html")
    with open(p, encoding="utf-8") as f:
        html = f.read()
    marker = "<!-- GEO-FAQ-INDEX -->"
    if marker not in html and "<!-- NEWSLETTER -->" in html:
        block = f"  {marker}\n" + jsonld_script(faq_jsonld(INDEX_FAQ))
        html = html.replace("  <!-- NEWSLETTER -->", block + "\n\n  <!-- NEWSLETTER -->", 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)
        print("index.html: FAQPage JSON-LD added")
    elif marker in html:
        print("index.html: SKIP (already done)")
    else:
        print("index.html: SKIP (NEWSLETTER marker missing)")

    # 2) tools/index.html — visible FAQ + JSON-LD before footer
    p = os.path.join(ROOT, "tools/index.html")
    with open(p, encoding="utf-8") as f:
        html = f.read()
    marker = "<!-- GEO-FAQ-TOOLS -->"
    if marker not in html and "<!-- FOOTER -->" in html:
        faq = visible_faq(TOOLS_FAQ, marker)
        # JSON-LD just before the visible block (so it sits near content)
        block = jsonld_script(faq_jsonld(TOOLS_FAQ)) + "\n" + faq
        html = html.replace("  <!-- FOOTER -->", "  " + block + "\n\n  <!-- FOOTER -->", 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)
        print("tools/index.html: FAQ + JSON-LD added")
    elif marker in html:
        print("tools/index.html: SKIP (already done)")
    else:
        print("tools/index.html: SKIP (FOOTER marker missing)")

    # 3) about/index.html — visible FAQ + JSON-LD before footer
    p = os.path.join(ROOT, "about/index.html")
    with open(p, encoding="utf-8") as f:
        html = f.read()
    marker = "<!-- GEO-FAQ-ABOUT -->"
    if marker not in html and "  <footer>" in html:
        faq = visible_faq(ABOUT_FAQ, marker)
        block = jsonld_script(faq_jsonld(ABOUT_FAQ)) + "\n" + faq
        html = html.replace("  <footer>", "  " + block + "\n\n  <footer>", 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)
        print("about/index.html: FAQ + JSON-LD added")
    elif marker in html:
        print("about/index.html: SKIP (already done)")
    else:
        print("about/index.html: SKIP (footer marker missing)")


if __name__ == "__main__":
    main()
