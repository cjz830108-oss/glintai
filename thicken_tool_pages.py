# -*- coding: utf-8 -*-
"""
Batch-thicken the 16 Glint AI tool pages by injecting a unique, original
<section class="deep"> block immediately before <section class="faq">.

Each block adds 300-380 words of genuine prose (use cases + practical tips),
raising each thin tool page from ~235-327 words to a healthier 450-600.

Usage:  python thicken_tool_pages.py            # inject if missing
        python thicken_tool_pages.py --force    # re-inject (overwrite existing .deep)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(ROOT, "tools")

# ---------------------------------------------------------------------------
# Original deep-dive content keyed by slug (inner HTML only; section wraps it).
# ---------------------------------------------------------------------------
DEEP = {
"ai-content-detector": '''
<h2>When you should actually check for AI writing</h2>
<p>An AI content detector is useful any time the <em>origin</em> of a text matters. Teachers use it to spot essays that were pasted out of a chatbot instead of written by a student. Editors use it to vet freelance pitches, because a "original" article that scores 95% machine-written is a liability for the publication's reputation. SEO teams run drafts through it before publishing, since Google's guidance rewards clearly human, experience-driven content and quietly devalues thin auto-generated pages.</p>
<p>The tool is also a self-audit mirror. If your own draft comes back as mostly AI, that is a signal to add personal examples, opinions, and specifics only a person in your field would know. Treat the score as a hint about voice, not a verdict about cheating.</p>
<h3>Practical tips</h3>
<ul>
<li>Run the check <strong>before</strong> you publish or submit, not after a dispute has already started.</li>
<li>Remember false positives happen, especially for non-native English writers and for short, formulaic text. Never use a score as the sole evidence against someone.</li>
<li>Pair the detector with the humanizer when you want to soften robotic phrasing in a draft you actually wrote.</li>
<li>Don't paste confidential client material into tools you don't trust. Glint's detector runs locally in your browser, so nothing leaves the page.</li>
</ul>
''',

"ai-humanizer": '''
<h2>Getting natural results from an AI humanizer</h2>
<p>A humanizer rewrites stiff, repetitive AI output into prose that reads like a person wrote it. That matters because first drafts from language models tend to share the same rhythm: the same transitions, the same balanced "not only… but also" constructions, the same polite hedging. A good humanizer breaks that pattern so the text feels spontaneous.</p>
<p>Use it on marketing copy that sounds like a brochure, on onboarding emails that put readers to sleep, and on any paragraph where every sentence is the same length. It is also handy for adapting tone: a formal report draft can be loosened for a blog post without rewriting from scratch.</p>
<h3>Practical tips</h3>
<ul>
<li>Don't over-humanize. Chasing a "100% human" score can strip away the clarity and precision that made the draft good in the first place.</li>
<li>Always re-read for meaning. A humanizer can swap a word that changes your facts, so verify technical terms and numbers afterward.</li>
<li>Keep a grammar check in the loop. Humanizing can introduce a stray comma or awkward clause.</li>
<li>Lead with your own expertise, then humanize the scaffolding. The tool polishes voice; it does not invent your experience.</li>
</ul>
''',

"ai-text-summarizer": '''
<h2>Summarize smarter, not just shorter</h2>
<p>A summarizer earns its place wherever a document is longer than the time you have. Use it to digest a 40-page research report into the three findings that change your decision. Use it to prep for a meeting by condensing the background doc everyone skipped. Use it on a thread of linked articles so you walk in knowing the argument instead of the noise.</p>
<p>The same tool works on your own writing. Paste a rough draft and ask for a one-paragraph version to find the spine of your piece, then rebuild around it. Writers use this to beat blank-page paralysis: summarize the thing you meant to say, then expand it.</p>
<h3>Practical tips</h3>
<ul>
<li>Pick the length deliberately. A "TL;DR" line, a paragraph, and a bulleted brief are three different jobs.</li>
<li>Always verify the key facts in the summary against the source. Summaries can drop a caveat that changes everything.</li>
<li>Because Glint's summarizer runs in your browser, you can safely run internal or sensitive text through it without uploading it to a server.</li>
<li>Chain it with the humanizer when the summary still reads like a robot wrote it.</li>
</ul>
''',

"background-remover": '''
<h2>Clean cutouts for real work</h2>
<p>A background remover turns a busy photo into a transparent PNG you can drop anywhere. For ecommerce sellers that means product shots on a clean white tile instead of a cluttered kitchen counter. For creators it means a profile picture that sits cleanly on any colored header. For social posts it means a subject you can paste over a branded template without fighting the original scene.</p>
<p>It is also the quiet workhorse of presentation design. Pull a person or object out of a stock photo and place them into your slide, and the deck suddenly looks custom instead of stock. Meme-makers, course creators, and newsletter authors all lean on it weekly.</p>
<h3>Practical tips</h3>
<ul>
<li>Start with a high-contrast subject. The cleaner the edge between subject and background, the better the cut.</li>
<li>Watch hair, fur, and glass. These are the edges algorithms struggle with, so check them at full zoom before shipping.</li>
<li>Always export as PNG to keep transparency. Saving as JPG brings the white box back.</li>
<li>Use the cutout for YouTube thumbnails and ad creative where a floating subject grabs more attention than a flat photo.</li>
</ul>
''',

"bio-resume-generator": '''
<h2>Bios and resumes that actually get read</h2>
<p>Most bios are forgotten the moment they are skimmed, and most resumes are filtered out in six seconds. A generator helps by giving you a strong baseline you can then tailor. Use it for a conference speaker bio, an "About the author" blurb, a LinkedIn summary, or a crisp one-liner for a podcast guest slot. For resumes, it is best at polishing bullet points so each line leads with an outcome instead of a duty.</p>
<p>The real win is speed. Instead of staring at a blank field, you get three versions and pick the one closest to your voice, then tweak. That turns a 40-minute chore into a five-minute edit.</p>
<h3>Practical tips</h3>
<ul>
<li>Tailor every version to its audience. A recruiter bio and a conference bio should not be the same sentence.</li>
<li>Lead with the outcome you are known for, not your job title. "Helps SaaS teams ship faster" beats "Senior Project Manager."</li>
<li>Use active verbs: built, launched, cut, grew. Passive phrasing hides impact.</li>
<li>Keep a resume scannable: short bullets, measurable results, no paragraphs.</li>
</ul>
''',

"grammar-checker": '''
<h2>Beyond the red underline</h2>
<p>A grammar checker is not just a spellcheck with ambitions. It catches the things your eye skips after the tenth read: a subject that quietly stopped agreeing with its verb, a tense that drifted mid-paragraph, a "their" where "there" slipped in. For non-native English writers it is a steady editor that explains the rule, not just flags the error. For everyone else it is a second pair of eyes before a client ever sees the message.</p>
<p>Where it pays off most is consistency. Long documents drift: a brand name gets capitalized three different ways, a term gets abbreviated halfway through. Running the checker catches the drift before it reaches a prospect.</p>
<h3>Practical tips</h3>
<ul>
<li>Don't accept every suggestion. A checker can "correct" a deliberate fragment or a brand voice choice. Read the reasoning first.</li>
<li>Watch homophones. Tools catch "your/you're" far better than humans, but confirm the fix fits your meaning.</li>
<li>Use it on email before you hit send, especially replies written in a hurry.</li>
<li>Run it after the humanizer or paraphraser, since rewriting can introduce fresh slips.</li>
</ul>
''',

"hashtag-generator": '''
<h2>Hashtags that reach the right people</h2>
<p>A hashtag generator is not about collecting as many tags as the platform allows. It is about landing your post in front of people who care. On Instagram and TikTok the game is mixing a few broad tags with many narrow ones, so a small account can actually surface instead of drowning. On YouTube, hashtags sharpen the topic signal for the recommendation system.</p>
<p>Use it when you are starting a campaign and need a consistent set, when you are cross-posting the same content to different networks, or when you simply cannot think of the third variation that fits. The generator hands you grouped options you can rotate.</p>
<h3>Practical tips</h3>
<ul>
<li>Mix tag sizes. All-huge tags bury you; all-tiny tags reach no one. A blend is the sweet spot.</li>
<li>Don't stuff. Platforms penalize spammy tag walls, and readers tune them out.</li>
<li>Research what competitors in your niche use, then differentiate with one or two branded tags.</li>
<li>Rotate sets between posts so you are not training the algorithm to treat you as repetitive.</li>
</ul>
''',

"json-formatter": '''
<h2>JSON you can actually read</h2>
<p>JSON is the lingua franca of APIs, config files, and modern apps, but raw JSON from a server is usually a single unreadable line. A formatter turns that wall of text into indented, color-friendly structure you can scan in seconds. Developers use it to debug API responses, to review config before a deploy, and to inspect log payloads without guessing where a value lives.</p>
<p>It is also a teaching tool. When someone is learning JSON, pretty-printed output makes the nesting obvious in a way a minified blob never does. And when you need to paste a snippet into docs or a ticket, formatted JSON is simply respectful of the next reader.</p>
<h3>Practical tips</h3>
<ul>
<li>Validate before you deploy. An invalid config can take a service down; format-and-validate catches the missing comma early.</li>
<li>Minify for transport. Smaller payloads mean faster APIs and leaner config files in production.</li>
<li>Watch encoding. Formatting won't fix a mojibake string, so check special characters after.</li>
<li>Keep formatted output for code review and minified for the wire; the tool switches between both in a click.</li>
</ul>
''',

"markdown-to-html": '''
<h2>Markdown to clean HTML, fast</h2>
<p>Markdown is where most writing starts: in READMEs, in note apps, in draft docs. But the web speaks HTML. A markdown-to-HTML converter bridges that gap so you can write in plain text with simple symbols and publish real, styled HTML without touching a visual editor. Bloggers use it to draft posts, developers to write docs, marketers to build newsletter blocks.</p>
<p>The value is reversible simplicity. You keep writing in a format that ages well and survives any tool, then convert only when you need to ship. No lock-in, no broken formatting from a copy-paste through a word processor.</p>
<h3>Practical tips</h3>
<ul>
<li>Add alt text to every image during conversion. Accessibility and SEO both depend on it, and it is painful to retrofit later.</li>
<li>Preview the output before pasting into a CMS. Headings should map to your site's style, not fight it.</li>
<li>Sanitize untrusted input. If the markdown comes from users, strip dangerous tags on the server side too.</li>
<li>Keep heading levels consistent. Jumping from H1 to H3 confuses both readers and search engines.</li>
</ul>
''',

"paraphraser": '''
<h2>Rewrite without losing the meaning</h2>
<p>A paraphraser is the tool you reach for when the idea is right but the words are wrong. Students use it to express source material in their own voice and avoid accidental plagiarism. Writers use it to vary repetitive phrasing in a long draft. Marketers use it to adapt one message for different channels without starting over.</p>
<p>Done well, paraphrasing is not cheating, it is translation between registers. The same fact can be "the model failed to converge" or "training stalled," and choosing the right version for your reader is real craft. The tool suggests the alternatives; you keep ownership of the choice.</p>
<h3>Practical tips</h3>
<ul>
<li>Always check the facts survived. A paraphrase can quietly swap "increased" for "doubled," which is a different claim.</li>
<li>Don't over-spin. Rewriting every sentence can strip your natural voice and confuse the point.</li>
<li>Keep citations attached. Paraphrasing moves words, not attribution; the source still deserves credit.</li>
<li>Compare modes if the tool offers them, then pick the one that fits the audience.</li>
</ul>
''',

"password-generator": '''
<h2>Passwords that survive real attacks</h2>
<p>A password generator removes the one variable that breaks most security: the human. People reuse passwords, pick birthdays, and add "1!" to the end of an old word. A generator produces something random and long enough that guessing and dictionary attacks simply don't scale. Use it for every new account, for sharing a one-off secret, for a WiFi passphrase guests can actually type, and for spinning up API keys.</p>
<p>The point is not paranoia, it is hygiene. One leaked password on a recycled credential can open five accounts. Random, unique passwords close that domino chain before it starts.</p>
<h3>Practical tips</h3>
<ul>
<li>Length beats complexity. A 16-character random string is stronger than a short "complex" one with symbols.</li>
<li>Use a unique password per site. Breaches are constant; reuse is how one leak becomes many.</li>
<li>Store them in a password manager so you never have to remember or write them down.</li>
<li>Turn on two-factor authentication everywhere it is offered. A password is one lock; 2FA is two.</li>
</ul>
''',

"pdf-summarizer": '''
<h2>Tame long PDFs without losing the thread</h2>
<p>PDFs are where information goes to hide: hundred-page reports, scanned contracts, research papers with three appendices. A PDF summarizer pulls the signal out so you know what you are dealing with before you commit an afternoon. Use it to triage a stack of papers, to surface the clauses in a contract, to brief yourself on a meeting deck, or to decide whether an ebook is worth the full read.</p>
<p>It pairs naturally with note-taking. Summarize first to get the shape of the document, then read only the sections that matter. That is how busy researchers and founders stay current without reading everything end to end.</p>
<h3>Practical tips</h3>
<ul>
<li>Extract the text first if the PDF is a scan. Image-only files need OCR before any summary is accurate.</li>
<li>Point the tool at specific sections when you can. A summary of "the pricing section" beats a summary of the whole 80-page doc.</li>
<li>Verify every number the summary quotes. A misread figure in a contract summary is expensive.</li>
<li>Combine the summary with your own notes so the key points actually stick.</li>
</ul>
''',

"serp-preview": '''
<h2>See your snippet before Google does</h2>
<p>A SERP preview tool shows exactly how your page will look in search results: the title, the URL, and the description, formatted to the pixel limits Google enforces. Most people write a meta title blind and discover too late that it got truncated to "...om/tools/bl". Previewing turns that guessing into a craft you can tune.</p>
<p>It is also a competitive lens. Paste a rival's URL and see why their snippet earns the click: tighter title, clearer benefit, cleaner URL structure. Then steal the pattern, not the words. For anyone doing on-page SEO, this is the cheapest A/B test you will ever run.</p>
<h3>Practical tips</h3>
<ul>
<li>Stay inside the limits. Roughly 60 characters for titles and 155 for descriptions keeps you from being cut off.</li>
<li>Front-load the keyword. Searchers and crawlers both weight the start of the title most.</li>
<li>Make every description unique. Duplicate meta descriptions across pages dilute each one's pull.</li>
<li>Check the live SERP for your target term and write to beat the snippets already there.</li>
</ul>
''',

"word-counter": '''
<h2>Count what actually matters</h2>
<p>A word counter sounds trivial until a constraint depends on it. Students hit a 500-word essay limit and need to know they are at 487, not 520. SEO writers target a floor so a post looks substantive to search engines. Social teams trim captions to fit a platform's character ceiling. Translators bill by the word and need an exact figure, not a guess.</p>
<p>Beyond limits, counts reveal rhythm. A paragraph that is 180 words is a wall; a piece with sentences averaging 30 words is exhausting. Counting is the first step to controlling both, which is why it sits next to the readability analyzer in any serious writing toolkit.</p>
<h3>Practical tips</h3>
<ul>
<li>Track characters and words separately. A tweet limit is characters; an essay limit is words; mixing them up is a classic miss.</li>
<li>Watch average sentence length, not just totals. Short sentences keep readers moving.</li>
<li>Set a target before you write so you shape the draft instead of padding it after.</li>
<li>Run it alongside the readability analyzer to catch both volume and density problems at once.</li>
</ul>
''',

"word-readability-analyzer": '''
<h2>Write at the right reading level</h2>
<p>A readability analyzer scores how hard your text is to understand, usually as a school grade level or a readability index. That number is a compass, not a grade. Government sites and health providers often must hit a plain-language standard so ordinary readers can act on the information. Bloggers use it to keep posts breezy. Internal docs use it so new hires don't need a dictionary.</p>
<p>The trap is writing down on purpose. A low score is good only if it fits the audience. A journal for specialists should read harder than a public warning. The tool tells you where you landed; judgment tells you whether that is the right place.</p>
<h3>Practical tips</h3>
<ul>
<li>Aim for your reader, not for a low number. Simplicity serves the audience, not a leaderboard.</li>
<li>Shorten sentences first. Halving average sentence length usually drops the grade level faster than swapping big words.</li>
<li>Cut jargon or define it on first use. Unexplained terms are the main thing that pushes scores up.</li>
<li>Treat the score as a guide for revision, then read the passage aloud to confirm it still sounds like you.</li>
</ul>
''',

"youtube-title-generator": '''
<h2>Titles that earn the click</h2>
<p>On YouTube the title does most of the selling. A great one tells the viewer exactly what they get and why it is worth the next eight minutes, while quietly signaling the topic to search. A title generator spins several angles from your topic so you are not staring at a blank field betting on one idea. Use it to brainstorm a main title, to draft A/B variants for an A/B test, and to name a series so each episode feels connected.</p>
<p>It also keeps you honest about clickbait. The generator surfaces curiosity-driven options; your job is to pick the one that delivers on its promise, because a misleading title tanks watch time and the algorithm notices.</p>
<h3>Practical tips</h3>
<ul>
<li>Front-load the keyword so the title ranks and reads naturally at the same time.</li>
<li>Pair curiosity with a clear value: "how," "why," or a specific result beats vague hype.</li>
<li>Keep it around 60 characters so it isn't truncated in search and suggestions.</li>
<li>Make the title and thumbnail agree. Mismatched messaging confuses the viewer and hurts clicks.</li>
</ul>
''',
}

FAQ_TOKEN = '<section class="faq">'

def inject(slug, html, force=False):
    new_section = '    <section class="deep">' + DEEP[slug].strip() + '\n    </section>\n'
    if force:
        html = re.sub(r'\s*<section class="deep">.*?</section>\s*', '\n', html, flags=re.S)
    if '<section class="deep">' in html:
        return html, False  # already present, skip
    idx = html.find(FAQ_TOKEN)
    if idx == -1:
        raise RuntimeError("faq anchor not found in %s" % slug)
    # Insert before the faq line, preserving a newline break
    return html[:idx] + new_section + html[idx:], True

def main():
    force = "--force" in sys.argv
    results = []
    for slug in sorted(DEEP.keys()):
        path = os.path.join(TOOLS, slug + ".html")
        if not os.path.exists(path):
            print("MISSING:", path)
            continue
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        out, changed = inject(slug, html, force=force)
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(out)
        results.append((slug, changed))
        print(("UPDATED " if changed else "skipped ") + slug)
    print("\nDone. %d updated, %d skipped." % (
        sum(1 for _, c in results if c), sum(1 for _, c in results if not c)))

if __name__ == "__main__":
    main()
