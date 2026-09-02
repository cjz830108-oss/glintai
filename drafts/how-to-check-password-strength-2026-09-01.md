# How to Check Password Strength and Build Unbreakable Ones

A password is only as strong as the math behind it, not the cleverness of the word you picked. "Dragon" with a number stuck on the end is still weak. The reliable way to judge a password is to check its entropy and provenance — and the safest place to do that is on your own device. This guide covers how to check strength, what the score actually means, how to generate passwords that hold up, and why where the check happens matters as much as the result.

## What "password strength" measures

Strength is roughly how many guesses an attacker would need. Length, randomness, and character variety all raise that count. A checker estimates entropy in bits; the more bits, the harder the brute force. The key word is estimate — a score is a guide, not a guarantee, because it cannot see whether the value appeared in a known breach.

## Why client-side checking matters

Password checkers that upload your entry to a server learn exactly what you typed. A browser-based checker measures entropy locally and never transmits the value. Given that the thing you are checking is, by definition, a secret, local checking is the only sane default. The alternative is telling a stranger your password to ask if it is good.

## When to check a password

- **Before reusing an old one** to see if it still clears the bar.
- **After a breach alert** to confirm you are not leaning on a compromised pattern.
- **When setting up an account** that enforces weak minimums.
- **For a shared vault entry** where one weak link risks everything.
- **To teach a team** why "Password1!" is not clever.
- **Before generating a new one** to confirm the generator's output is actually strong.

## How to check well

Use a checker that reports entropy and flags length, not just a red-to-green bar. Cross-check against known breach corpora where the tool does it locally or with k-anonymity, so the password itself is never sent. Then generate a fresh value rather than tweaking the old one. Because Glint's checker runs in your browser, you can test sensitive candidate passwords without uploading them.

## A step-by-step method

1. **Type the candidate** into a local checker — nothing leaves the device.
2. **Read the entropy** in bits, not just a color.
3. **Check breach status** via a k-anonymity method if offered.
4. **If weak, generate new** rather than patching the word.
5. **Store it** in a manager so you never have to memorize or reuse it.

## A worked example

| Check | Weak entry | Strong entry |
| --- | --- | --- |
| Length | 9 characters | 18 characters |
| Pattern | dictionary word + "1!" | random mix |
| Entropy | ~28 bits | ~95 bits |
| Verdict | cracks in minutes | centuries |

The weak entry looks "complex" to a human but is trivial to a machine. The strong entry is long and random, which is what actually matters.

## Strength signals compared

| Signal | What it tells you | What it misses |
| --- | --- | --- |
| Character rules | Has symbol, number, case | Dictionary base still weak |
| Entropy bits | Raw guess cost | Whether it was breached |
| Breach lookup | Appears in leaks | Local-only if done wrong |

## A quick scenario: a team lead

A team lead inherits a shared drive protected by "Company2023!". They run it through a local strength checker and see low entropy plus a dictionary base. Instead of patching the word, they generate a unique 20-character random passphrase per service.

Each account now has its own value, stored in a manager. When one vendor is breached, the others are untouched. The team stops sharing one magic word in a chat thread and starts using generated secrets that never leave the browser during creation. The checker becomes a gate at account setup, not an afterthought.

The habit compounds. Over a year, unique generated passwords turn a single point of failure into isolated, disposable credentials. The cost is one manager app; the payoff is sleeping through breach headlines.

## Common mistakes

Trusting a green bar is the main one — a checker that only counts rules ("has a symbol") misses that "P@ssw0rd" is still terrible. Another is reusing a "strong" password across sites, which collapses into one breach. Finally, writing the value on a sticky note or in a plain text file undoes the generation, and uploading it to a web checker hands the secret to a third party.

## Who should use it (and who shouldn't)

Check and generate passwords for every account that matters — email, banking, admin, code. Skip manual generation for things you access once and forget; use the manager's generator there too, but don't lose sleep. The principle holds: long, random, unique, local.

## How it fits a writing toolkit

Glint's password tool is free and needs no account. Pair it with the API-key generator for config secrets, and with the JSON formatter when you scaffold local config that stores tokens.

## Frequently asked questions
<p><b>Is a browser-based strength checker safe?</b> Yes, when it computes entropy on the page and does not upload what you type. No account means no stored copy.</p>
<p><b>What entropy should I aim for?</b> Aim for roughly 70 bits or more for important accounts; 12 to 16 random characters usually gets there.</p>
<p><b>Does adding symbols make a weak word strong?</b> No. "Password1!" is still a dictionary word with predictable swaps. Length and randomness beat symbol tricks.</p>
<p><b>Should I reuse one strong password?</b> No. Reuse means one breach compromises everything. Generate a unique value per site.</p>
<p><b>Is the Glint generator really free with no signup?</b> Yes. It runs in your browser and requires no account or upload.</p>
