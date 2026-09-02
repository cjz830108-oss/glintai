# Free AI Tools for Podcasters: Titles, Show Notes, and Chapters

It is 11pm. The episode is edited, the artwork is attached, and the show notes box is still empty. The feed goes live at 6am and you still need a title, a description, chapter timestamps, a guest bio, and a post for your website. This guide shows which of those jobs you can finish tonight with free browser-based tools that ask for no account and upload nothing.

Independent podcasters rarely lose an evening to one hard problem. They lose it to a stack of small writing jobs that repeat weekly in the same shapes, with the same character limits and formatting rules. That is what a free tool handles well, and it is the part a $29 per month podcast SaaS locks behind a login.

## Where a weekly episode eats your evening

The record and the edit feel like the work. Then the publishing checklist starts, and it is all writing.

The title has to survive as one line between ten other episodes in a feed. The show notes are the only indexable text attached to an audio file. Chapter timestamps are rarely generated for you. The guest bio has to be written from a LinkedIn page at midnight. And the transcript arrives as one 9,000 word block with no paragraph breaks and "um" on every fourth line.

None are hard alone. Together they are two hours, and they are why plenty of shows that publish weekly for eight weeks quietly stop.

## Titles that survive the feed

A title has one job in the feed and a different job in search. In the feed it has to be scannable in two seconds. In search it has to contain words someone would type.

The most common failure is the "conversation with" title. "Ep. 142: Talking with Sarah about marketing" tells a listener nothing actionable. Compare "Ep. 142: How Sarah Grew a Newsletter to 20,000 Readers Without Paid Ads." Same guest, but the second names a result and a constraint, and holds four words someone might search.

The second failure is the abstract theme. "A conversation about burnout" reads like a conference panel. "Ep. 143: Burnout Is a Workload Problem, Not a Willpower Problem" makes a claim, and a claim earns the tap.

Keep the episode number first, then the payoff, then the guest name if the guest is the draw. Run your shortlist through the [YouTube Title Generator](/tools/youtube-title-generator.html) for variations worth pillaging, since the click logic behind a video thumbnail is the same logic behind a line in a podcast app. Our [YouTube title generator guide](/blog/youtube-title-generator-guide.html) covers the pattern in more detail.

Aim for 60 characters or fewer. Several apps truncate near there, and everything past the cut is work you did for free.

## Show notes that do real work

Show notes are your entire search presence, and most shows spend them on one summary line and five links.

Use four short blocks. Open with a sentence or two stating what the episode delivers, written so a stranger understands it without pressing play. Add three to five bullets in the vocabulary your listeners use. Then the links, each with a descriptive label rather than a bare URL. Close with one line asking for a rating.

Target 150 to 250 words. Under 100 leaves a search engine nothing to work with. Over 400 means an hour spent on text skimmed for six seconds. Check the draft in the [Word Counter](/tools/word-counter.html) before publishing, because the count tells you in one second that you have written 480 words of preamble again.

Apple truncates the podcast description at 4,000 characters and Spotify displays a similar amount, so there is no need to ration. But the first two lines are what show before the "more" tap on mobile, so the payoff goes there.

## Chapter timestamps

Chapters are the most underrated piece of podcast metadata. They let a listener jump to the part they care about, and on the video version they make a long upload survivable.

The format is simple and unforgiving. One chapter per line, timestamp first, then a space and the title. Use `mm:ss` under an hour and `hh:mm:ss` above it:

```
00:00 Cold open: the 11pm problem
01:12 Why show notes decide whether anyone finds you
08:40 The 200 word show note that works
17:05 Chapters, and why listeners skip without them
26:30 Cleaning a transcript in ten minutes
```

On YouTube the first chapter must start at `00:00`, you need at least three, and each must run at least 10 seconds. Most podcast players pick up the same text from your show notes automatically.

Do not scrub the timeline by hand. Pull the topic shifts out of the transcript instead. If your editor exports the script as a PDF, the [PDF Summarizer](/tools/pdf-summarizer.html) gives you the section breakdown first.

## Guest bios and transcript cleanup

A guest bio should run 50 to 75 words: who they are, what they do, one credential or result, and where to find them. Longer reads as a CV nobody finishes.

Paste the guest's about page into the [AI Text Summarizer](/tools/ai-text-summarizer.html) and ask for a short third person bio. You will still edit it, because summaries flatten voice, but you start from 60 words instead of a blank line. The same method works on the paper a guest sent an hour before recording, and [How to Summarize Long Articles](/blog/how-to-summarize-long-articles.html) walks through that case.

Transcript cleanup is the bigger job. Fix it in three passes. Split it into paragraphs every three or four exchanges so it reads as a page rather than a log. Remove filler words only where they interrupt comprehension, and keep them where they carry hesitation. Then fix speaker labels and proper nouns, which is where automated transcription fails most often.

Do not over-clean. A transcript polished into an essay sounds fake and destroys the quotes you wanted later.

## Turning one transcript into a blog post

Every episode contains a blog post, and most independents never publish it, because a transcript is not an article and converting one by hand takes an hour.

Work from the summary rather than the raw transcript. Condense it to a section skeleton, then rebuild: open with the most useful claim in the episode, write three or four sections with headings that restate each point in your own words, pull one verbatim quote per section, and close with the same links block plus an embedded player.

Target 700 to 900 words, long enough to rank for a specific query and short enough to finish in one sitting. If you draft in Markdown, the [Markdown to HTML converter](/tools/markdown-to-html.html) gives you markup that pastes cleanly into WordPress or Ghost, and our [Markdown to HTML workflow](/blog/markdown-to-html-workflow.html) covers the heading levels that survive a CMS paste.

## The video version

If you publish the video cut, it needs its own description. Do not paste the show notes. YouTube shows roughly the first two lines before the fold, and timestamps in the description become clickable chapters.

Structure it as a one or two line hook, the chapter list, three or four lines about the guest, then links and a subscribe line. Stay under the 5,000 character limit and load the hook into the first 125 characters. Our [YouTube description generator guide](/blog/youtube-description-generator.html) covers the full block layout, and [Best YouTube Title Generator Tools 2026](/blog/best-youtube-title-generator-tools-2026.html) compares title approaches.

## A quick scenario

It is 11pm on a Wednesday. You have a finished 62 minute interview with a first time guest, a raw transcript, and a 6am slot.

Your working title is "Episode 88: Chatting with Marcus." You generate variations, pick "Ep. 88: Marcus Built a Six-Figure Repair Shop With No Paid Ads," and count 54 characters. It fits.

For show notes, you paste the transcript into the [AI Text Summarizer](/tools/ai-text-summarizer.html) and get a section breakdown in under a minute. You turn it into a two sentence opener, four bullets, and a links block. The [Word Counter](/tools/word-counter.html) reads 212 words, inside your range, so you stop.

For chapters, you take that same breakdown and write six timestamps starting at `00:00`, one per line, using `mm:ss` with the hour marker only on the last one.

For the bio, you paste Marcus's about page into the summarizer, get 80 words, cut to 68, and add his shop's handle.

For the blog post, you write 800 words around the same skeleton with two verbatim quotes, then convert the Markdown with the [Markdown to HTML converter](/tools/markdown-to-html.html) so it pastes into your CMS cleanly.

For the video description, you write a fresh hook in the first two lines, paste the timestamps underneath, and reuse the bio and links.

You finish by 12:20. Nothing was uploaded, no account was created, and nothing you pasted left your device.

| Task | Tool | Why it fits |
|---|---|---|
| Episode and video titles | [YouTube Title Generator](/tools/youtube-title-generator.html) | Variations you can trim to 60 characters for the feed |
| Show notes from a transcript | [AI Text Summarizer](/tools/ai-text-summarizer.html) | Turns a 9,000 word transcript into a section breakdown |
| Chapter sections from a script | [PDF Summarizer](/tools/pdf-summarizer.html) | Pulls topic shifts out of a PDF export, no timeline scrubbing |
| Checking note and post length | [Word Counter](/tools/word-counter.html) | Confirms 150 to 250 words for notes, 700 to 900 for the post |
| Publishing the episode as a post | [Markdown to HTML](/tools/markdown-to-html.html) | Markup that survives a paste into WordPress or Ghost |

## Free vs paid podcast tools

Free covers the per-episode writing: titles, notes, chapters, bios, transcript cleanup, and the blog version. Those are the same shapes every week, and a browser tool that keeps files on your device handles them for nothing.

Paid earns its place when the problem stops being writing. Dynamic ad insertion, team approval workflows, a searchable transcript archive across 200 episodes, and analytics tied to chapters all need infrastructure, and a host that does them well is worth $20 to $40 a month.

The trap is paying for a writing subscription when what you need is a host. Keep the words free and put your money into distribution.

## Common mistakes

- Naming the guest in the title and leaving the payoff out, so the episode ranks for a name nobody searches.
- Writing show notes under 100 words, which gives a search engine almost nothing to index.
- Skipping chapters, then wondering why completion drops at the 20 minute mark on a 70 minute episode.
- Pasting the raw transcript into the blog and calling it a post instead of rewriting to 800 words with headings.
- Editing a transcript into an essay, which strips the quotes you wanted for social.
- Reusing the audio show notes as the YouTube description, where two lines are all anyone sees.
- Paying $29 a month for writing tools when writing is the part free tools do best.

## Frequently asked questions
<p><b>How long should podcast show notes be?</b> Aim for 150 to 250 words with three to five bullets, and put the payoff in the first two lines since that is what shows before the more link on mobile.</p>
<p><b>What timestamp format should podcast chapters use?</b> Use mm:ss for episodes under an hour and hh:mm:ss for longer ones, one chapter per line, and start the first at 00:00 so players and YouTube both recognise it.</p>
<p><b>Can I turn a transcript into a blog post automatically?</b> Not in one step, but summarising the transcript into a section breakdown first cuts the work to about twenty minutes of rewriting into 700 to 900 words.</p>
<p><b>Do these tools upload my episode transcript?</b> No. Every tool here runs in your browser, so an unreleased transcript, an unannounced guest, and your draft notes stay on your device.</p>
<p><b>When is a paid podcast tool worth the money?</b> When you need dynamic ad insertion, team approval workflows, a searchable transcript archive, or analytics tied to chapters, which are hosting problems rather than writing problems.</p>
