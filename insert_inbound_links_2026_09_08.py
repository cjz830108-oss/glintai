import os

ROOT = "."

# (source_file, anchor_substring, link_text, target_url)
E = [
    # --- cold email (Sales) ---
    ("blog/ai-tools-for-freelancers-2026.html", "client comms",
     "free AI tools for cold email", "/blog/ai-tools-for-cold-email-2026.html"),
    ("blog/ai-tools-for-consultants-2026.html", "Consulting runs on other people",
     "free AI tools for cold email outreach", "/blog/ai-tools-for-cold-email-2026.html"),
    # --- photographers (Creative) ---
    ("blog/ai-tools-for-social-media-managers-2026.html",
     "Social media managers ship constant content across platforms",
     "free AI tools for photographers", "/blog/ai-tools-for-photographers-2026.html"),
    ("blog/best-background-remover-tools-2026.html",
     "A clean cutout makes a product shot or avatar look pro.",
     "free AI tools for photographers", "/blog/ai-tools-for-photographers-2026.html"),
    ("blog/how-to-create-alt-text-for-images.html",
     "Alt text is the sentence you write so a screen reader can describe an image",
     "free AI tools for photographers", "/blog/ai-tools-for-photographers-2026.html"),
    # --- therapists (Health) ---
    ("blog/private-ai-detector.html",
     "A private AI detector tells you whether text reads as AI-generated",
     "free AI tools for therapists and coaches", "/blog/ai-tools-for-therapists-2026.html"),
    ("blog/ai-tools-for-lawyers-2026.html",
     "A solo practitioner pastes a client",
     "free privacy-first AI tools for therapists", "/blog/ai-tools-for-therapists-2026.html"),
    # --- accountants (Finance) ---
    ("blog/how-to-convert-csv-to-json.html",
     "CSV is how spreadsheets talk, and JSON is how software listens.",
     "free AI tools for accountants", "/blog/ai-tools-for-accountants-2026.html"),
    ("blog/best-free-json-formatter.html",
     "A free JSON formatter turns a wall of unreadable text into clean",
     "free AI tools for accountants", "/blog/ai-tools-for-accountants-2026.html"),
    # --- remote teams (Remote Work) ---
    ("blog/ai-tools-for-small-business-2026.html", "wear every hat",
     "free AI tools for remote teams", "/blog/ai-tools-for-remote-teams-2026.html"),
    ("blog/ai-tools-for-freelancers-2026.html", "Subscriptions add up fast",
     "free AI tools for remote teams", "/blog/ai-tools-for-remote-teams-2026.html"),
]

CLOSE = ("</p>", "</li>", "</h3>", "</h2>", "</td>")


def ins_at(h, i):
    best = None
    for c in CLOSE:
        j = h.find(c, i)
        if j != -1 and (best is None or j < best):
            best = j
    return best


ok = skip = 0
for src, anc, txt, tgt in E:
    p = os.path.join(ROOT, src.lstrip("/"))
    if not os.path.exists(p):
        print("SKIP no-file", src); skip += 1; continue
    h = open(p, encoding="utf-8").read()
    if tgt in h:
        print("SKIP exists", src, "->", tgt); skip += 1; continue
    idx = h.find(anc)
    if idx == -1:
        print("SKIP no-anchor", src, "::", anc); skip += 1; continue
    j = ins_at(h, idx + len(anc))
    if j is None:
        print("SKIP no-close", src); skip += 1; continue
    link = ' <a href="%s">%s</a>' % (tgt, txt)
    h = h[:j] + link + h[j:]
    open(p, "w", encoding="utf-8").write(h)
    print("OK", src, "->", tgt); ok += 1

print("\nDONE ok=%d skip=%d" % (ok, skip))
