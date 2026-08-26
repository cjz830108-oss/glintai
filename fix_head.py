# -*- coding: utf-8 -*-
"""Align homepage <head> with the new positioning (point 44 rebrand)."""
p = "index.html"
s = open(p, encoding="utf-8").read()

repl = [
    ('  <title>Glint AI — Free AI Tools for Creators, Marketers & Solo Founders</title>',
     '  <title>Glint AI — The Everyday AI Toolkit for Creators & Marketers</title>'),
    ('  <meta name="description" content="Glint AI is a growing toolbox of free AI-powered utilities for creators and marketers: text summarizer, readability analyzer, Markdown converter, JSON formatter, and password generator. No signup required for free tools." />',
     '  <meta name="description" content="Glint AI is the everyday AI toolkit for creators and marketers: 16 free tools to write better, create faster, and grow smarter. No signup, no tracking." />'),
    ('  <meta name="keywords" content="AI tools, text summarizer, readability checker, markdown to html, json formatter, password generator, free ai tools, content tools" />',
     '  <meta name="keywords" content="AI toolkit, AI tools, writing tools, content tools, marketing tools, text summarizer, grammar checker, free ai tools, creators" />'),
    ('  <meta property="og:title" content="Glint AI — Free AI Tools for Creators & Marketers" />',
     '  <meta property="og:title" content="Glint AI — The Everyday AI Toolkit" />'),
    ('  <meta property="og:description" content="A growing toolbox of free, fast AI-powered utilities. Summarize text, check readability, convert Markdown, format JSON, generate passwords." />',
     '  <meta property="og:description" content="16 free AI tools for creators and marketers. Write better, create faster, grow smarter." />'),
    ('  <meta name="twitter:title" content="Glint AI — Free AI Tools" />',
     '  <meta name="twitter:title" content="Glint AI — Everyday AI Toolkit" />'),
    ('  <meta name="twitter:description" content="Free AI-powered tools for creators and marketers." />',
     '  <meta name="twitter:description" content="16 free AI tools for creators & marketers." />'),
    ('    "description": "Free AI-powered tools for creators, marketers and solo founders.",',
     '    "description": "The everyday AI toolkit for creators and marketers — 16 free tools to write better, create faster, grow smarter.",'),
]

missed = []
for old, new in repl:
    if old not in s:
        missed.append(old[:60])
        continue
    s = s.replace(old, new, 1)

open(p, "w", encoding="utf-8").write(s)
if missed:
    raise SystemExit("MISSED:\n" + "\n".join(missed))
print("OK: homepage head realigned.")
