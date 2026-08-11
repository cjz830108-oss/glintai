# Glint AI

Free, fast, zero-signup AI tools for creators, writers, and marketers — built as a static site with a cyberpunk UI.

🌐 **Live site:** https://glintai.tools

---

## What's inside

### 16 free tools

**Writing & Content**
- AI Text Humanizer
- AI Content Detector
- Paraphrase Tool
- Grammar Checker
- Professional Bio Generator

**Analysis & SEO**
- Word & Readability Analyzer
- Meta Description & CTR Guide
- SERP & Meta Preview
- YouTube Title & Hook Generator
- Hashtag Generator
- Word & Character Counter

**Productivity**
- Markdown ↔ HTML Converter
- JSON Formatter
- Password & API Key Generator
- PDF Summarizer
- Background Remover

All tools run client-side — no upload, no tracking, no account required.

### 17 SEO blog posts

Each major tool ships with a companion long-form guide (Article + FAQPage structured data) interlinked into a hub-and-spoke content network.

---

## Tech stack

- Pure static HTML/CSS/JS (`index.html` + modular tool scripts)
- Cyberpunk theme — dark `#07070d` base with neon cyan `#00f0ff` / magenta `#ff2e97`
- Auth & subscriptions: Supabase Auth + PayPal Subscriptions (Plans: Pro $9 / Team $29)
- Zero-cost tooling: CDN WASM for heavy ops (`pdf.js`, `@imgly/background-removal`)

---

## Deployment

This repo is connected to Vercel via GitHub. Every `git push` to `main` triggers an automatic production deploy.

```bash
git add -A
git commit -m "your change"
git push   # -> Vercel auto-deploys
