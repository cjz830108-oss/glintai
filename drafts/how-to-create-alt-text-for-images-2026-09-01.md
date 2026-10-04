# How to Write Alt Text for Images (Accessibility + SEO in 2 Minutes)

Alt text is the sentence you write so a screen reader can describe an image, and so Google can understand what the picture shows. Most people skip it, which shuts out users who cannot see the page and wastes a free SEO signal. Writing good alt text takes seconds once you know the shape. This guide covers the free, no-signup way to get alt text right — the craft rules, the 125-character guideline, empty alt for decorative images, the context test, and how to audit an existing page — plus what to leave out.

## What alt text is

Alt text is the alternative description in an image's HTML. When the image cannot load or a reader announces it, that text stands in. It is not a caption and not a place for keywords — it is a concise description of what the image conveys and why it matters in context.

### The standard behind it

Alt text is not a nice-to-have suggestion; it is the mechanism behind WCAG success criterion 1.1.1 (Non-text Content), a Level A requirement — the most fundamental tier of the Web Content Accessibility Guidelines, and the first checkpoint most auditors check. A page with meaningful images and no alt text fails it outright. Legal exposure follows the standard: accessibility lawsuits against websites routinely cite missing alt text among the easiest-to-detect failures, precisely because it is a one-line scan that automated tooling can flag in seconds.

There is a second failure mode people never think about: the broken image. When an image file 404s, the browser renders the alt text in the broken-image box instead of the picture. On slow connections, email clients that strip images, and corporate browsers that block remote assets, your alt text is what all readers actually see. Writing it well serves them too.

## Why it matters for accessibility and SEO

For accessibility, alt text is how blind and low-vision users perceive visuals; missing it leaves a blank — or worse. When the alt attribute is missing entirely (not empty, absent), most screen readers fall back to announcing the image's filename: "slash images slash IMG underscore 4 2 7 1 dot J P G". That is the insider detail most articles miss: an unnamed photo is not silent, it is noise, and it interrupts every page read. An explicitly empty alt (alt="") tells the reader "skip this deliberately." The difference between those two states is one attribute, and getting it wrong degrades every page visit for screen reader users.

For SEO, image search and general understanding both use alt text to place your picture in context. Google's own image publishing guidance treats alt text as the anchor that tells its crawlers what an image depicts, and descriptive filenames plus alt text are the two inputs it names explicitly. A short, accurate description serves both audiences at once, and it is one of the cheapest improvements you can make to a page.

## When to write it

- **Every content image** that carries meaning, not decoration.
- **Product photos** where the description helps shoppers and search — material, color, and size belong in the sentence.
- **Charts and graphs** where the takeaway should be stated in words, not "chart".
- **Infographics** summarized so the point survives without sight — the full text goes in surrounding copy, the alt carries the summary.
- **Logos and icons** where function (not brand) is the message.
- **Tutorial screenshots** where the alt names the step shown.
- **Linked images** — the alt becomes the link text a screen reader announces, so it must describe the destination, not the picture.

## How to write good alt text

State what the image shows and why it matters, in one sentence, without "image of" or "picture of" padding. If the image is decorative, mark it empty rather than forcing words. Lead with the subject, then the detail a reader needs. Because Glint's helpers run in your browser, you can draft alt text without uploading your image to a third party.

### Describe the purpose, not the pixels

The skill is writing for context. A photo of a meeting does not get "four people at a table with laptops" on a product page for a videoconferencing tool — it gets something like "a distributed team on a video call using the app's grid view." The same photograph in a news article gets the journalistic description: "Negotiators meet at the Paris summit on Tuesday." A chart's alt text should be its takeaway — "line chart: monthly signups rose from 200 to 900 in Q2" — not "bar chart." Ask: what does a reader miss if this image never loads? That sentence is your alt text.

### The 125-character guideline

Around 125 characters is the practical ceiling for a single alt string. It is not a WCAG requirement — it is a convention inherited from how older versions of the JAWS screen reader chunked long descriptions, effectively repeating or summarizing anything longer. Modern screen readers handle longer text, but the guideline survives because it enforces discipline: if you need more than a sentence, the long description belongs in visible text beside the image, and the alt carries the summary. For complex images like infographics, that adjacent-text pattern is the standard treatment — the deprecated HTML longdesc attribute is not the answer.

### Never "image of" — and never a filename

Screen readers announce "image" or "graphic" before reading alt text, so "image of a ceramic mug" is announced as "image, image of a ceramic mug." Delete the prefix everywhere. The same discipline kills filenames-as-alt: "IMG_4271.jpg" and "chart.png" are the absence of alt text wearing a filename's clothes.

### Decorative vs functional images

- **Decorative images** — background textures, divider flourishes, stock photos repeating adjacent text — get an explicitly empty alt (alt=""). The screen reader passes them by, which is the correct experience. This is one of the rare cases where doing nothing is the craft.
- **Functional images** — icons and buttons that do something — describe the action, not the drawing. A magnifying glass icon is "Search", a cart icon is "View cart", an envelope is "Email us." The alt text is the button label.
- **Text embedded in images** — banners, logos with slogans — gets the verbatim text as alt.

### The SEO angle, done right

Image search traffic converts when the description matches what the searcher wanted, which means natural language wins. A keyword belongs in alt text only when it genuinely describes the image — "blue ceramic coffee mug on a wooden table" naturally contains "blue ceramic mug" and needs no help. Alt text stuffed with "buy mug cheap mug best mug" is a recognized spam signal, can be flagged in search quality reviews, and helps nobody. Write for the reader who cannot see the image; the search engine reads the same sentence and is satisfied.

## A step-by-step method

1. **Identify the subject** — what is actually in the frame.
2. **State the context** — why this image is on the page. This decides the sentence.
3. **Add one detail** — color, size, result, or action — the one the reader needs.
4. **Drop the filler** — no "image of", no filenames, no keyword stuffing.
5. **Mark decorative images empty** so readers skip them, and label functional images with their action.

### Auditing and testing an existing page

On any live page, open the browser inspector and check img tags for a missing or filename alt attribute — or run a purpose-built tool: the WAVE browser extension highlights missing alt text inline, and Chrome DevTools' Lighthouse audit reports every image lacking an alt attribute as a failed accessibility check. The audit takes a minute on a ten-image page. For the real test, run a screen reader once: NVDA is free on Windows, VoiceOver is built into macOS (Command+F5), and on mobile both iOS and Android ship one. Listen to your own page the way a blind user does — the first page you hear with "IMG underscore" read aloud will change how you write alt text permanently.

## A worked example

The same subject, three treatments:

- **Product shot — bad alt:** img1
- **Product shot — good alt:** "Blue ceramic coffee mug on a wooden table, 12 oz"
- **Chart — bad alt:** chart
- **Chart — good alt:** "Line chart: monthly signups rose from 200 to 900 in Q2"
- **Decorative divider — correct alt:** empty (alt="")

The good versions name the subject and the relevant detail, which is exactly what a reader or search engine needs. The empty version is not laziness — it is the deliberate signal that the divider carries no information.

## Good vs bad alt text compared

- **Descriptive:** "Bar chart of 2025 revenue by quarter" — useful and specific; the takeaway survives without sight.
- **Keyword-stuffed:** "buy mug cheap mug best mug" — spammy, unhelpful, and a quality flag for search.
- **Padding:** "image of a picture of a mug" — says nothing and doubles the announcement.
- **Filename:** "IMG_4271.jpg" — what screen readers announce when the attribute is missing; effectively no alt text at all.
- **Empty on purpose:** alt="" on a decorative flourish — correct, because silence is the right experience there.

## A quick scenario: a small shop owner

A shop owner adds ten product photos to a new collection page and leaves alt blank by default. A friend using a screen reader says the page is "silent" on images. Using a free alt-text helper, the owner writes one sentence per photo: color, material, size.

The page becomes navigable for everyone, and the products appear in image search for specific terms like "blue ceramic mug 12 oz". No account, no upload of product shots to a random site. Alt text becomes a publish-step checkbox, not an afterthought, and the owner templates the pattern for future drops.

The habit compounds. Every upload ships described, the store becomes more usable, and image search slowly sends a trickle of ready-to-buy visitors. The cost was a sentence per photo, paid once.

## Common mistakes

Keyword-stuffing alt text is the main one — "buy blue mug cheap mug best mug" helps no one and reads as spam. Another is writing "image" or "photo" as if that were information. A third, quieter failure is the missing attribute versus the empty one: leaving alt out entirely makes screen readers announce filenames, which is worse than silence. Describing decorative images wastes the reader's time; mark those empty instead. And describing function-less pixels while ignoring functional icons — the search button announcing "magnifying glass" instead of "Search" — inverts what the alt text was for. Finally, never upload your catalog to a web tool just to generate alt text when a browser-based helper needs no upload.

## Who should use it (and who shouldn't)

Write alt text for every meaningful image on a public page. Skip it (use empty alt) for pure decoration. If you publish anything public, the answer is effectively always yes — and if the page matters commercially, audit it with an extension or inspector before you publish.

## How it fits a writing toolkit

Glint's [background remover](/blog/best-background-remover-tools-2026.html) is free and needs no account, and the [no-signup background remover guide](/blog/free-background-remover-no-signup.html) covers when a stripped-out background makes an image decorative (and therefore safe for empty alt). Pair it with the [SERP preview tool](/blog/best-free-serp-preview-tool.html) to see how your page, image and all, renders in search before you publish.

## Frequently asked questions

<p><b>Is alt text for SEO or accessibility?</b> Both — it helps screen readers and gives search engines context for the image. Writing for the blind reader satisfies the search engine automatically.</p>
<p><b>Should I include keywords in alt text?</b> Only if they describe the image accurately; stuffing keywords hurts more than it helps and reads as a spam signal.</p>
<p><b>What about decorative images?</b> Mark them with empty alt (alt="") so screen readers skip them gracefully. A missing attribute is not the same thing — it makes readers announce filenames.</p>
<p><b>Is a browser-based alt-text helper safe?</b> Yes, when it runs on the page and needs no image upload or account.</p>
<p><b>Is the Glint background remover really free with no signup?</b> Yes. It runs in your browser and requires no account.</p>
