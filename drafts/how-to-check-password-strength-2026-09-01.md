# How to Check Password Strength and Build Unbreakable Ones

If you want to check password strength honestly, forget the red-to-green bar and start with the math. A password is only as strong as the number of guesses an attacker would need, not the cleverness of the word you picked. "Dragon" with a number stuck on the end is still weak; so is "P@ssw0rd!", which passes every complexity check while sitting in every cracking ruleset published in the last decade. The reliable way to judge a password is to check its entropy and provenance — and the safest place to do that is on your own device. This guide covers how to check strength, what the score actually means, and why where the check happens matters as much as the result.

## What "password strength" measures

Strength is roughly how many guesses an attacker would need. Length, randomness, and character variety all raise that count. A checker estimates entropy in bits; the more bits, the harder the brute force. The key word is estimate — a score is a guide, not a guarantee, because it cannot see whether the value appeared in a known breach. A 60-bit password leaked in a 2019 dump is worth zero bits today.

### The entropy math, step by step

Entropy in bits equals length × log2 of the character-set size: 26 for lowercase letters, 62 for mixed-case plus digits, 94 for full printable ASCII, 7,776 for a Diceware-style passphrase word list. Four real examples:

- **"password123"** — 11 characters over a 36-symbol set (letters plus digits) gives a naive estimate of 11 × 5.17 ≈ 57 bits. That number is fiction: it is a dictionary word plus a sequence, every cracking tool tries it in the first seconds, and a realistic score is under 5 bits.
- **"Summer2026!"** — 11 characters over ~94 symbols yields a naive ~72 bits, which looks excellent. But the pattern is [capitalized season][year][symbol], a template every ruleset models. A score like 72 bits describes the worst-case attacker; the realistic attacker breaks it in minutes.
- **A 16-character random string over a–z, A–Z, 0–9** — 16 × log2(62) ≈ 16 × 5.95 ≈ 95 bits. With no pattern to exploit, the naive math is the real math.
- **A 5-word passphrase from a 7,776-word list** — 5 × log2(7,776) ≈ 5 × 12.92 ≈ 65 bits. Weaker than the 16-character string but memorable, which matters when the alternative is a sticky note. Add a random sixth word and you gain about 13 bits.

The gap between naive and pattern-adjusted entropy is what a good checker tells you — and what composition checkers cannot see.

### Offline vs online attacks: which threat is your score for?

Strength only matters against the offline case, where an attacker has stolen a website's password hashes and can guess at machine speed. Published hashcat benchmarks put a single flagship GPU like the RTX 4090 at roughly 150–170 billion NTLM guesses per second, and serious cracking rigs stack 8 to 24 of them. Against 95 bits, that hardware needs more time than civilization has. Against an 8-character password, the same rig needs hours at most. One nuance: slow, salted hashes like bcrypt or Argon2 cut guessing rates by orders of magnitude — but you do not control which hash a site uses; the breached company does.

The online case — guessing against a live login page — is rate-limited to a few attempts before lockout. No password survives an online attack because it never faces one; what protects you there is uniqueness and MFA. Reuse is catastrophic for the same reason: credential stuffing replays email-and-password pairs from one breach across hundreds of login pages.

## Why client-side checking matters

Password checkers that upload your entry to a server learn exactly what you typed. A browser-based checker measures entropy locally and never transmits the value. Given that the thing you are checking is, by definition, a secret, local checking is the only sane default. The alternative is telling a stranger your password to ask if it is good.

### How k-anonymity keeps the password local

The best-known breach-lookup service, Have I Been Pwned's Pwned Passwords, shows how any tool can check a secret against a database without learning it. The page hashes your password with SHA-1 in the browser, sends only the first five characters of that hash to the server over HTTPS, and receives back every hash suffix in its corpus of 800+ million breached passwords that starts with those five characters. The final match happens on your device; the server sees a prefix that could match hundreds of passwords and never learns which is yours. Any checker worth trusting either computes everything locally or uses this exact pattern.

## When to check a password

- **Before reusing an old one** to see if it still clears the bar.
- **After a breach alert** to confirm you are not leaning on a compromised pattern.
- **When setting up an account** that enforces weak minimums.
- **For a shared vault entry** where one weak link risks everything.
- **To teach a team** why "Password1!" is not clever.
- **Before generating a new one** to confirm the generator's output is actually strong.
- **When auditing a password manager's** master password — the one secret that unlocks everything.

## How to check well

Use a checker that reports entropy and flags length, not just a red-to-green bar. Cross-check against known breach corpora where the tool does it locally or with k-anonymity, so the password itself is never sent. Then generate a fresh value rather than tweaking the old one. Because Glint's checker runs in your browser, you can test sensitive candidate passwords without uploading them.

### Pattern checkers vs composition checkers

There are two generations of strength checkers, and the difference is the difference between "P@ssw0rd!" scoring strong and scoring terrible. Composition checkers count character classes: has uppercase, has digit, has symbol — green. Pattern checkers, exemplified by zxcvbn (Dropbox's open-source estimator, released in 2016), model attacker behavior: dictionary words, l33t substitutions (a→4, e→3, o→0), keyboard walks, repeats, dates, and years — then compute entropy from the patterns found. zxcvbn rates "P@ssw0rd!" with trivially low entropy, exactly as a cracking rig would. The test question for any checker: does it rate "P@ssw0rd!" as weak? If not, it is counting classes, not modeling attackers.

### Reference tables worth knowing

The [Hive Systems password table](https://www.hivesystems.com/password), published annually, shows crack times for different lengths and character sets against different hash types on a 12-GPU rig — the chart security teams screenshot for their slides. The visual takeaway: length dominates. An 8-character password fails offline in seconds to months depending on the hash; a 16-character random one is out of reach regardless.

## A step-by-step method

1. **Type the candidate** into a local checker — nothing leaves the device.
2. **Read the entropy** in bits, not just a color, and check that the score reflects patterns, not just character classes.
3. **Check breach status** via a k-anonymity method — first five characters of the hash, match happens locally.
4. **If weak, generate new** rather than patching the word — no symbol-for-letter swaps on a dictionary base.
5. **Store it** in a password manager so you never have to memorize or reuse it, and reserve the memorable passphrase for the manager's master password.

## A worked example

- **Weak entry — 9 characters, dictionary word + "1!" suffix.** Naive entropy ~28 bits; pattern-adjusted, close to nothing. Cracks in minutes offline, and it appears in breach corpora, so stuffing attacks have it pre-computed.
- **Strong entry — 18 characters, random mix.** Entropy ≈ 18 × 5.95 ≈ 107 bits over the full alphanum-plus-symbol set. Not in any corpus, no pattern to model; centuries against realistic offline rigs.

The weak entry looks "complex" to a human but is trivial to a machine; the strong entry is long and random. The breach check matters here too — any password you invent yourself has some chance of already being in a leak.

## Strength signals compared

- **Character rules (has symbol, number, case).** Tells you it passes legacy complexity policies; misses that a dictionary base plus predictable substitutions is still weak.
- **Entropy bits (naive math).** Tells you raw guess cost against a worst-case attacker; misses whether a pattern shrinks the search space and whether the value was already breached.
- **Pattern-adjusted entropy (zxcvbn-style).** Tells you the realistic guess cost; misses breach status, so pair it with a corpus check.
- **Breach lookup (k-anonymity).** The only signal that catches a "strong-looking" password attackers already have.

No single signal is sufficient. The honest workflow runs all of them: pattern-adjusted entropy, breach status, then generation if either fails.

## A quick scenario: a team lead

A team lead inherits a shared drive protected by "Company2023!". They run it through a local strength checker and see low entropy plus a dictionary base — plus a breach-lookup hit, since year-suffix patterns show up in leaked corpora constantly. Instead of patching the word, they generate a unique 20-character random value per service.

Each account now has its own secret, stored in a manager. When one vendor is breached, the others are untouched. The team stops sharing one magic word in a chat thread and starts using generated secrets that never leave the browser during creation. The checker becomes a gate at account setup, not an afterthought.

They also add MFA on the accounts that matter — not because the new passwords are weak, but because strength has no answer to a phishing page. A 107-bit password typed into a fake login form is handed over in one screen; MFA is the layer that catches it.

The habit compounds. Over a year, unique generated passwords turn a single point of failure into isolated, disposable credentials. The cost is one manager app; the payoff is sleeping through breach headlines.

## Common mistakes

Trusting a green bar is the main one — a checker that only counts rules ("has a symbol") misses that "P@ssw0rd!" is still terrible. Others:

- **Believing substitutions add real strength.** a→@, e→3, s→$ are in every standard cracking ruleset (hashcat's best64 alone models the most common few dozen); attackers wrote the substitutions down years ago.
- **Adding a year to a word.** "Summer2026!" pattern-cracks because years are a bounded, enumerated range.
- **Reusing a "strong" password across sites**, which collapses into one breach. This is the mistake strength cannot fix — uniqueness, not entropy, stops stuffing.
- **Rotation by incrementing.** Forced 90-day changes produce "Spring2026!" after "Winter2026!" — a pattern, not a new password. NIST guidance (SP 800-63B) dropped mandatory rotation for exactly this reason: forced changes degrade passwords; breach-list screening works.
- **Writing it on a sticky note or in a plain text file** undoes the generation; uploading it to a web checker hands the secret to a third party.

## Who should use it (and who shouldn't)

Check and generate passwords for every account that matters — email, banking, admin, code. Skip manual generation for things you access once and forget; use the manager's generator there too, but don't lose sleep. The principle holds: long, random, unique, local.

### The honest limit of strength

Entropy defends the stolen-hash database. Uniqueness defends against credential stuffing. MFA defends the live login page. Strength defends none of them alone, and nothing against a phished password — an attacker who tricked you into typing a 40-character random string into their site receives all 40 characters. Hence a checklist, not a single move:

- **Length ≥ 14 characters**, random-generated for anything that matters.
- **Unique per site**, no exceptions for "low-risk" accounts.
- **A memorable passphrase** — 5+ random words — reserved for the master password.
- **A password manager** stores the rest.
- **MFA on top** of every account that offers it.

## How it fits a writing toolkit

Glint's password tool is free and needs no account. Pair it with our [strong password generator guide](/blog/strong-password-generator-guide.html) for the generation workflow, the [creating strong passwords explainer](/blog/how-to-create-a-strong-password.html) for the principles behind the checklist, and our roundup of [best free password generator tools](/blog/best-free-password-generator-tools-2026.html) if you are comparing options. For developers, the [API keys safety guide](/blog/generate-api-keys-safely.html) covers config secrets, and the [JSON formatter](/blog/best-free-json-formatter.html) helps when you scaffold local config that stores tokens.

## Frequently asked questions
<p><b>Is a browser-based strength checker safe?</b> Yes, when it computes entropy on the page and does not upload what you type — or uses k-anonymity, sending only a short hash prefix that cannot reveal your password.</p>
<p><b>What entropy should I aim for?</b> Aim for roughly 70 bits or more for important accounts; 14+ random characters clears 80 bits, and a 5-word passphrase lands around 65.</p>
<p><b>Does adding symbols make a weak word strong?</b> No. "Password1!" is still a dictionary word with predictable swaps, and cracking tools model substitutions explicitly. Length and randomness beat symbol tricks.</p>
<p><b>Should I reuse one strong password?</b> No. Reuse means one breach compromises everything through credential stuffing. Generate a unique value per site.</p>
<p><b>Is the Glint generator really free with no signup?</b> Yes. It runs in your browser and requires no account or upload.</p>
