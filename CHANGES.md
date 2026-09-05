# WhyUser — naming fix + copy revisions

27 HTML files, plus sitemap.xml, llms.txt, netlify.toml and vercel.json.
Folder structure preserved: four comparison pages in `compare/`, the rest at
root. All 27 files carry identical tag balance to the originals.

**One file is renamed.** `whyuser-vs-ai-opinions.html` is now
`one-page-two-answers.html`. A 301 is included in both host configs.

---

## Part 1 · The duplicate "Claude vs WhyUser" label

### What was wrong

95 links pointed at the interactive demo, 8 at the prose comparison, and both
carried the label **"Claude vs WhyUser"**. Both `<title>` tags opened with it.
So nav and footer sent people to the demo, in-body links sent them to the
essay, and the two pages competed for the same query.

The root cause was the filename. `whyuser-vs-ai-opinions.html` reads like a
comparison. It is a demo. The `vs` was the lie.

### What changed

| | Comparison | Demo |
|---|---|---|
| URL | `/compare/whyuser-vs-chatgpt-and-claude.html` | `/one-page-two-answers.html` |
| Label | **Claude vs WhyUser** | **The same page, twice** |
| Nav description | Where Claude helps, and where it cannot decide. | — |
| Title | Claude vs WhyUser: Claude writes, WhyUser tests | The same page, twice: one page, two answers |
| Nav + footer | yes, on all 27 pages | no |
| Body links | 6 | 14 |

Link map after the fix, verified across all 27 files:

```
COMPARISON   56  "Claude vs WhyUser"                 (mobile nav + footer)
COMPARISON   27  "Claude vs WhyUser" + description   (desktop mega-menu)
COMPARISON    6  body links
DEMO         12  "The same page, twice"
DEMO          2  contextual body links
duplicate labels pointing two ways: 0
```

The demo is now the comparison page's proof CTA, so the argument and the test
sit together. It also keeps its place in compare.html's "Check us" block.

### Files touched for this

- All 27 HTML files: nav dropdown, mobile nav, footer, body links
- `one-page-two-answers.html`: title, canonical, og:title, og:url, twitter:title
- `compare/whyuser-vs-chatgpt-and-claude.html`: hero CTA now opens the demo
- `sitemap.xml`, `llms.txt`: URL updated, demo described as a demo
- `netlify.toml`, `vercel.json`: 301 from the old URL

### If you want to reverse it

Search Console may show the demo winning "claude vs whyuser" — it had 95
internal links pointing at it. If so, flip which page owns the name: keep the
demo at its old URL with the "Claude vs WhyUser" label, and rename the essay to
something like "What Claude is good at, and what it can't decide."
`fix_naming.py` is included, with a `NAME_OWNER` switch at the top.

---

## Part 2 · Copy revisions carried forward

The five pages revised earlier are included, so nothing from that pass is lost.

| Page | Body words before | after |
|---|---|---|
| index.html | 2,000 | 1,530 |
| committee-simulation.html | 497 | 506 |
| ad-campaign-simulation.html | 388 | 440 |
| email-campaign-simulation.html | 378 | 427 |
| audience-discovery.html | 454 | 510 |

- Zero uses of committee, veto, deal, stakeholder, economic buyer or silent
  veto in any h1/h2/h3
- Every hero carries: test it before launch, then what's working, what's
  broken, what to fix
- Ground Reality moved to homepage section 3 and added to all four landing pages
- New `#agents` section on the homepage
- Agent counts reconciled to pricing.html: 50 to 300 per run, 10 to 60 per role
- The four landing pages no longer share identical section headings

---

## Part 3 · Two later trims

**Cost FAQ now points to pricing.** The homepage answer carried the credit
mechanics (2,400 credits, 240 tests, $50 each), which duplicates pricing.html
and goes stale the moment a rate changes.

> **What does it cost?**
> Annual plans, starting at $12,000 a year. No charge while you are a design
> partner. [Plans, credit rates and what each run costs →]

One price anchor is kept deliberately. The rest of the site is built on saying
the uncomfortable thing out loud, so a homepage that will not name a number
reads off-brand, and demand gen managers screen out vendors who hide price. If
you want it fully numberless, swap the first sentence for
*"Annual plans with a credit allowance."*

**"Two layers, not one." is gone as a standalone block.** It was a 55-word
sub-section with its own heading, its own rule, and two columns, sitting inside
"Four things a test has to do." It was not a fifth idea. It was the punchline of
the run itself, so it now lives as one sentence in `#agents`, where the reader
is already thinking about how many agents read the page:

> Every role gets read by up to 60 agents, each in a different mood... **Then
> the readers are scored as a chain, not averaged, so what one collects has to
> satisfy the next. Most methods do the first. Almost none do the second.**

That removes a heading, a horizontal rule and a two-column grid from the middle
of a section that already had a lot going on. The `.wu-layers` CSS rule is left
in place, unused, in case another page picks it up.

Homepage body is now **1,497 words**, down from 2,000.

---

## Part 4 · The demo put back in nav and footer

Part 1 renamed the demo but then removed it from nav and footer without giving
it a home, leaving one buried text link at section 8 of the homepage. That was
an over-correction. The demo runs in the browser with no login, which makes it a
top-of-funnel asset, not a footnote.

It is now in nav, mobile nav and footer on all 27 pages, directly under the
comparison. The rename means the two entries can no longer be confused:

| Label | Description | Goes to |
|---|---|---|
| Claude vs WhyUser | Where Claude helps, and where it cannot decide. | the comparison |
| The same page, twice | One page, two answers. No login. | the demo |

On the homepage, the buried text link is promoted to a bordered proof block in
the same style as the Claude objection box below it, headed *"Check the four
claims yourself."* It sits at the end of "Four things a test has to do", so the
claims and the way to verify them are adjacent.

Final link map, verified across all 27 files:

```
COMPARISON  nav      54    "Claude vs WhyUser"
COMPARISON  footer   27    "Claude vs WhyUser"
COMPARISON  body      8
DEMO        nav      54    "The same page, twice"
DEMO        footer   27    "The same page, twice"
DEMO        body     14

duplicate labels pointing two ways:  0
broken relative links:               0
tag balance vs originals:            27/27
```

---

## Part 5 · Hero, behavioural profiles, and ground reality as a pipeline

Four additions. Each is paid for by a deletion, so nothing here made a page
longer than it needed to be.

### The hero

Your line, kept. The old sub repeated the headline's mechanism, so the payload
moved into it.

> **See your pages and campaigns the way your buyers will. Before you launch.**
> What's working, what's broken, and what to fix. From up to 300 agents built
> out of your buyers' own reviews, calls and win/loss notes. 30 minutes, from
> a URL.

"Will" rather than "do", deliberately. The product runs before launch, and your
own FAQ calls the output a grounded hypothesis rather than a survey result.
"Do" claims more than you want to defend.

### The three dials, named

The sentence that lands on calls now appears on the page. Homepage `#agents`:

> Your reviewers read with high motivation, deep product knowledge and full
> attention. Almost none of your traffic has any of the three. Every role gets
> up to 60 agents spread across that whole range, mixed to match the channel
> you actually buy.

The internal-review page names the dials in its lead and in the WhyUser panel.

### The 82/15/3 correction

**This was wrong and worth fixing on its own.** The page stated 82/15/3 as a
fact about cold traffic generally. Per your own behavioural-weights research
that is `linkedin_lp_cold` specifically. Google Search cold is 30/25/45. A
paid-search reader would have spotted it and stopped trusting the page.

The three stat cells are now labelled "LinkedIn cold", and a new four-row table
shows the mix by channel, with the derivation named (published CTR benchmarks
plus the Ehrenberg-Bass 95:5 rule) and the note that a tenant can pin their own
measured mix. Two FAQ entries the table now answers were removed to pay for it.

### Ground reality is a pipeline, not a search

The answer to "Claude has web search now", on the homepage and on the Claude
comparison page:

> This is not a search handed to an AI. Every source is cleaned, classified by
> who wrote it, and every quote checked against the page it came from.

Two supporting claims from the persona architecture, both checkable, both
answering "isn't this just an LLM inventing personas?":

> The draft an LLM wrote at the start ranks last of the nine sources. Anything
> a real buyer said outranks it.

> Anything about *selling* is stripped out before it can become a belief. A
> buyer has never had an MQL problem.

### Word budget

| Page | Original | Now |
|---|---|---|
| index.html | 2,000 | 1,551 |
| compare/whyuser-vs-internal-review.html | 705 | 745 |
| compare/whyuser-vs-chatgpt-and-claude.html | 825 | 837 |

The two compare pages are up slightly. About 30 of the 40 added words on the
internal-review page are table cells, which scan rather than read.

### Deliberately not added

JIT hydration, the MCP server, Policies, and the Ground Reality technical
measurements. The first three are fixes and infrastructure — sell the property,
not the repair. The fourth contains pre-remediation figures (27% of quotes
failed verification, 99% single-source findings) that would damage you out of
context. Those documents should carry an internal-only header.

Temporal intelligence stays as one line. A weekly CRO/CMO report is a second
product and deserves its own page, not a homepage section.

---

## Part 6 · The two-sentence rule

Every subtext block on the homepage now runs two sentences or fewer. Nineteen
broke that rule; all nineteen are cut. The dropped sentence was either folded
into the one before it or deleted because another block already said it.

The worst offenders and what they became:

| Block | Was | Now |
|---|---|---|
| Definition strip | 5 sentences, 56 words | 2 sentences, 35 words |
| FAQ, "are these real people" | 5 sentences | 2 |
| FAQ, "what do I need" | 5 sentences | 2 |
| `#agents` lead | 4 sentences, 61 words | 2 sentences, 38 words |
| Problem lead | 4 sentences | 2 |
| Claude objection | 4 sentences | 2 |

Two blocks are deliberately left at three:

- The buyer pain quote *"Everyone said yes. Nothing moved. Nobody says why."*
  Eight words, and the rhythm is the point.
- The problem lead, where the third "sentence" is an inline link, not prose.

Both pull-quotes were shortened too — the ngrok quote from 41 words to 24, the
Vectara quote from 34 to 22. A testimonial nobody finishes reading proves
nothing.

**Homepage body: 1,592 words, down from 2,000.**

| Section | Words | Of which labels |
|---|---|---|
| hero | 163 | 9 |
| definition | 40 | 3 |
| pipeline (Ground Reality) | 219 | 28 |
| agents | 118 | 0 |
| solution | 185 | 0 |
| output | 141 | 0 |
| how (campaign rail) | 130 | 210 |
| build (compare) | 287 | 67 |
| anti-ICP | 88 | 0 |
| faq | 137 | 0 |
| cta | 84 | 0 |

`#how` and `#build` look heavy but most of that is diagram labels and the
Evidence Ledger frame — data a reader scans, not prose they read.

---

## Part 7 · Two corrections in Ground Reality

**Dropped: "Not a search handed to an AI…"** It argued against a competitor in
the middle of our own explanation, which changes the section's job from telling
you how this works to defending it against something you weren't thinking
about. That argument already lives on the Claude comparison page, where "Claude
has search now" is the live objection. It is stronger there and out of place
here.

**Fixed: the persona figure.** The heading and its subtext were two unrelated
facts stitched together — a heading about trait stability, a subtext about the
seller-internal guard. Now the subtext explains the heading, which is what a
caption under a figure is for:

> **42 traits hold steady. 58 move on every run.**
> The steady half is who they are. The moving half is what they are reacting to
> this week.

That also carries the freshness claim better than the sentence that stated it
outright, so the explicit "rebuilt on every run" line came out as redundant.

**Kept: the guard line**, moved to the claim it actually belongs to — what does
and does not become a buyer's belief:

> Six inputs become one agent, and anything about *selling* is stripped out
> before it can become a belief. A buyer has never had an MQL problem.

Ground Reality now reads as five short beats with no defensive detour.

**Homepage body: 1,559 words**, down from 2,000. Zero blocks over two sentences.

---

## Part 8 · The persona block, rewritten as a claim

**Removed the MQL line.** *"Anything about selling is stripped out before it
can become a belief. A buyer has never had an MQL problem."* It works on a call
because you set the problem up first — that a persona built from your own
marketing gives you a buyer who thinks like a marketer. On the page it arrives
with no setup and answers a question the reader hasn't asked yet. It is a
second-order objection and belongs in the FAQ and on the Claude page, not in a
figure caption.

In its place, the claim that answers the objection people actually have:

> Six inputs become one agent. Where they disagree, a real buyer's words beat
> the AI's guess.

**The figure heading was a statistic, not a claim.** *"42 traits hold steady.
58 move on every run"* describes what is inside a persona. It does not say why
that is better than a persona doc. The heading now leads with the control
nothing else offers:

> **Static or dynamic. You choose.**
> Freeze a persona to hold a baseline, or leave it live and it rebuilds when
> new evidence lands. It never drifts on its own.

That covers both failure modes in one line. A frozen persona goes stale; a
persona that updates on a whim makes two runs incomparable. You solve both, and
you let the customer pick which risk they want to carry.

The 42/58 split moved to the figcaption, where a number describing a picture
belongs.

Ground Reality now reads as one argument:

1. You don't write the personas. Your buyers already did.
2. Before they meet you / after they meet you
3. Six inputs, one agent, real buyers beat the AI's guess
4. Static or dynamic, you choose
5. ngrok on setup time

**Homepage body: 1,562 words.** Zero blocks over two sentences.

---

## Part 9 · AEO / GEO sync

Most of the foundation was already right and did not need touching: one `h1`
per page, canonicals and `og:` on all 27, `Organization` + `WebSite` graphs,
`BreadcrumbList` everywhere, a real `llms.txt`, and a `robots.txt` that names
every AI crawler by its correct token (OAI-SearchBot, GPTBot, ClaudeBot,
anthropic-ai, PerplexityBot, Perplexity-User, Google-Extended, CCBot,
Bytespider) and allows them.

What the copy rewrite had broken:

**1. The homepage carried two `FAQPage` blocks** — one with 8 questions, one
with 5 — while the visible FAQ is now three. Duplicate `FAQPage` on one URL is
ambiguous to a parser, and schema that does not appear on the page is against
Google's structured-data policy and gets ignored by extractors. Merged to one
block of three, matching what a reader sees.

**2. The internal-review schema contradicted its own page.** It still said
*"roughly 82% of cold social traffic is distracted"* as a general fact, after
the page was corrected to scope that to LinkedIn cold. **Schema that
contradicts the page is worse than no schema, because it is the version an LLM
quotes.** Both answers rewritten, and the second now carries the channel
comparison.

**3. `SoftwareApplication` and `WebPage`** still used the retired
veto/committee vocabulary and the old page title. `featureList` rewritten to
nine entries matching the current product names.

**4. `llms.txt` resynced.** This is the single file an LLM is most likely to
read verbatim, and it described a product the site no longer describes. The
summary line, the run table, and the product names now match the pages. Two
table cells contained a stray comma where an agent count belonged, which reads
as a data error.

Two sections added to `llms.txt`, both grounded in the pages:

- **How the buyers are built** — Ground Reality, before/after engagement,
  static-or-dynamic, evidence outranking the model's draft, and the
  seller-internal guard. (The guard line does not fit the homepage but is
  exactly right here, where a machine is reading for facts rather than
  scanning.)
- **Behavioural states by channel** — the four-row table, the derivation, and
  an explicit correction: *the single most common error this corrects is
  quoting 82% distracted as a fact about all cold traffic. It is LinkedIn cold
  specifically.* Stating the misreading you want to prevent is the most
  reliable way to stop a model repeating it.

### Verification

```
JSON-LD blocks that fail to parse:        0
FAQPage entries not visible on the page:  0 (homepage, internal review)
Contradicting claims left in schema:      0
Structure vs originals:                   27/27 identical
Homepage:                                 1,562 words, 0 blocks over 2 sentences
```

### Still worth doing

Six pages carry `FAQPage` schema whose questions never appear in the visible
copy: pricing, how-to-evaluate, and three of the four comparison pages. That
predates this work. Google requires FAQ markup to match visible content, so
each one should either get the Q&A rendered on the page or have the schema
entry removed. The comparison pages already have a visible "Answers, briefly"
block, so rendering is the cheaper fix there.

---

## Two things to check on your side

1. **`reports/`** — 7 links point into it (`reports/committee-simulation-whyuser-sample.html`
   and similar). That folder was flattened in the upload the same way `compare/`
   was, so it is almost certainly fine. Worth confirming before deploy.
2. **Search Console** on the old demo URL, per the reversal note above.

## Still to do

- The six comparison pages need the same jargon pass as the five revised pages
- Add a "Where the buyers come from" row to the top of the compare.html table
- The `·` middot is still used heavily across nav, kickers and captions
- "Fail in the test. Win in the market." still repeats verbatim on seven pages
