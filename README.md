# WhyUser fix bundle

Applies the changes agreed in this session. Every file here is a **drop-in
replacement** for a file you already have. Nothing was regenerated from
scratch — these are surgical edits to your current markup, so your design
system, class names and inline styles are untouched.

---

## Apply

```
# from your repo root, with the bundle unzipped alongside it
cp whyuser-fixes/assets/whyuser-pages.css  assets/
cp whyuser-fixes/index.html                .
cp whyuser-fixes/*.html                    .
cp whyuser-fixes/sitemap.xml               .
cp whyuser-fixes/llms.txt                  .
cp whyuser-fixes/robots.txt                .
cp whyuser-fixes/vercel.json               .     # or netlify.toml
```

Then **delete the old `compare/` folder** — its four pages now live at the
root, and 301s are in place for the old URLs.

Deploy. Check `/compare/whyuser-vs-chatgpt-and-claude.html` redirects to
`/whyuser-vs-chatgpt-and-claude.html`.

---

## 1 · The missing stylesheet (do this first)

`assets/whyuser-pages.css` **did not exist**. Seven pages linked it:

```
compare.html                 whyuser-vs-internal-review.html
glossary.html                whyuser-vs-building-it-yourself.html
how-to-evaluate.html         synthetic-personas-vs-buyer-panels.html
whyuser-vs-chatgpt-and-claude.html
```

Those are your proof pages — the ones a sceptical buyer opens before they
will believe the product — and they were rendering with unstyled comparison
tables, unstyled glossary definitions and unstyled example callouts.

The new file defines only the six classes nothing else defined:
`.cmp-wrap`, `.cmp-sec`, `.defn-label`, `.related`, `.eg`, `.eg-label`,
plus the `.scroll-smooth` utility. It declares **no tokens of its own** and
contains **zero `!important`**, so it cannot fight your palette.

Load order: after `whyuser-core.css` and `whyuser-shell.css`, before
`whyuser-readability.css`.

---

## 2 · Merged the two sections

`#agents` ("One opinion isn't data. 300 agents is.") and `#output`
("A report you forward…") are now **one section**, kept under `#output`.

It also **moved up**, to sit directly after Ground Reality instead of after
the product list. You said readers are scrollers, so the artifact now
arrives before the product menu rather than after it.

**Four tiles dropped.** Each survives somewhere it was already said:

| Dropped tile | Where it still lives |
|---|---|
| Weighted to your channel | `how-to-evaluate.html`, `whyuser-vs-internal-review.html` |
| The same answer, twice | folded into `#build` card 01 |
| Where the handoff breaks | already the hero conflict graph |
| Buyers that stay current | already "One compiled buyer" above |

**Four tiles kept**, because I checked and none of this exists anywhere
else on the site: `41 of 60` / `52 of 60`, chain-not-average scoring,
confidence + sample size, and the self-audit block.

The self-audit — *"Four published reports. One is this homepage, which
found our nav hard to scan and our proof thin"* — stayed **mid-page**
rather than moving to the closer. For a scroller, mid-page gets read and
the footer does not.

---

## 3 · "How WhyUser compares" section

**Retitled.** The headline freed up when `#agents` was merged away now does
the work here:

| | |
|---|---|
| Eyebrow | How WhyUser compares |
| Was | Four things a test has to do. |
| **Now** | **One opinion isn't data. 300 agents is.** |

Subtext, cut to 32 words: *"Your reviewers and your chatbot know the product
and pay attention. Your buyers do neither. Four things turn an opinion into
something you can act on. **Ask any tool here, including us.**"*

**Strip below it** is now 3 borderless cards. "Run it yourself" removed, and
the lead line "We do not win every row" is gone.

- **WhyUser vs ChatGPT and Claude** → `whyuser-vs-chatgpt-and-claude.html`
- **Six methods, side by side** → `compare.html`
- **How to evaluate a method** → `how-to-evaluate.html`

New CSS is appended to the homepage's existing `<style>` block. No
`!important`, existing tokens only, keyboard focus states included.

---

## 4 · compare/ flattened

31 files referenced `compare/`. All rewritten. The four pages moved to root
and their `../assets/` paths became `assets/`, which is also why they were
missing the stylesheet in the first place — the two problems shared a cause.

Redirects added to **both** `vercel.json` and `netlify.toml` (use one):

```
/compare/whyuser-vs-chatgpt-and-claude.html      -> /whyuser-vs-chatgpt-and-claude.html
/compare/whyuser-vs-internal-review.html         -> /whyuser-vs-internal-review.html
/compare/whyuser-vs-building-it-yourself.html    -> /whyuser-vs-building-it-yourself.html
/compare/synthetic-personas-vs-buyer-panels.html -> /synthetic-personas-vs-buyer-panels.html
/compare/*                                       -> /compare.html
```

`sitemap.xml` and `llms.txt` updated to match. This also kills the
`/compare.html` vs `/compare/` ambiguity that made you rename a page once
already.

---

## 5 · AEO / GEO / LLM optimisation

You asked to drop the "Before you ask" FAQ block, so **the section and its
`FAQPage` schema both came out.** That pairing is not optional: FAQ schema
without matching visible content on the same page is a structured-data
violation and gets the markup ignored or penalised.

No AEO was lost. `faq.html` already carries its own `FAQPage` with **14
questions**, which is where the visible content actually lives. The homepage
now points at it via `relatedLink` and `significantLink`.

**Schema graph: 4 nodes → 6.**

| Node | What it does |
|---|---|
| `HowTo` | the 4-step run, `totalTime: PT30M` |
| `BreadcrumbList` | site hierarchy |
| `WebPage.speakable` | points at `.h1`, `.hero-sub`, `.wu-out-p` |
| `Organization.knowsAbout` | 6 topic entities |
| `Organization.sameAs` | **placeholder — put your real profile URLs in** |
| `WebPage.significantLink` | sample report, accuracy, compare, how-to-evaluate, faq, pricing |

## 6 · Nav and footer

Applied to **all 28 pages** — desktop nav, mobile nav and footer.

**Why WhyUser** → 4 items:
Accuracy · Compare · Claude vs WhyUser · How to Evaluate It

Dropped from this menu: "The same page, twice", "Architecture & data flow",
"Security & DPA".

**Resources** → reordered, with a new **Security** sub-group:

```
Read before you buy
  ROI Calculator
  FAQ
  Why We Built This
  Glossary
Security
  Architecture & Data Flow
  Security
  DPA
  Privacy
```

**Footer** now mirrors the nav exactly. Five columns instead of four:

| Product | Why WhyUser | Resources | Security | Company |
|---|---|---|---|---|
| Landing Page Testing | Accuracy | ROI Calculator | Architecture & Data Flow | How it works |
| Ad Campaign Testing | Compare | FAQ | Security | Contact |
| Email Testing | Claude vs WhyUser | Why We Built This | DPA | Request access |
| Audience Research | How to Evaluate It | Glossary | Privacy | |
| See a sample report | | | | |
| Pricing | | | | |

Grid widened from `1.4fr repeat(3,1fr)` to `1.5fr repeat(4,1fr)`. The old
"For technical review" column is gone — its links live under Security now.
A duplicate "Why we built this" was removed from the Company column.

**Two things to know:**

**"How it works" left the Resources menu.** Your list of four didn't include
it, so I followed the list. It's still in the footer under Company, and the
`#how` anchor still works. One line to add back if that wasn't intended.

**`one-page-two-answers.html` is now unreachable from the homepage.** You
removed it from the strip and from the Why WhyUser menu in the same pass. It
still has inbound links from 25 other pages and is still in the sitemap, so
it isn't orphaned site-wide — but nothing on the homepage points at it any
more. Worth a deliberate decision rather than a side effect.

## 7 · Borderless pass

You asked for elements inline with the page rather than boxes. Your own
hero comment already says the same thing — *"Inline, not a card. No frame,
no fill, no shadow. The diagram is typeset into the page like a figure in
a report."* — so this makes the rest of the page agree with the hero.

Every content card lost its border, radius, fill and shadow. Separation is
now a single hairline rule.

| Element | Was | Now |
|---|---|---|
| `.wu-out-card` — what comes back | boxed + shadow | hairline top rule |
| `.wu-cmp-card` — compare strip | — | hairline top rule |
| `.ps-item` — the four test cards | boxed | hairline top rule |
| `.hub-source` — six evidence inputs | boxed | hairline left rule |
| `.wu-selfrun` — self-audit | boxed + brand bar | hairline top rule |
| `.wu-persona-fig` — persona graph | boxed | no frame |
| `.cta-card` — Get Started | boxed | hairline top rule |
| `.tally-wrap` | boxed + fill | hairline top rule |
| `.cmp-wrap` — comparison tables | boxed + zebra fill | hairline rules only |
| `.eg` — glossary examples | tinted panel | hairline rules only |

Hover states were rewritten to colour the hairline rule instead of a border
that no longer exists.

**Two things kept their frame on purpose:** `.product-frame` (the Evidence
Ledger) and `.flow-card` (the WhyUser step in the lifecycle). Those are mock
product UI — the frame is what makes them read as a screenshot rather than
a paragraph. Buttons, pills, chips and the nav dropdown kept their shape too,
because they are controls, not cards. Say the word and I'll flatten those as
well.

## 8 · Persona graph

This one I got wrong last time — I agreed to shrink it and the script never
touched it. Fixed now.

`.wu-persona-fig` had no `max-width`, so a 1440×1268 SVG stretched to the
full container and became the largest visual on the page. It is now capped at
**38rem and centred**, with the frame removed and the caption centred under it.

## 9 · Eyebrow rename

`#solution` eyebrow: **"Four tests" → "What you can test."** I went with a
noun phrase over "How to use" because it names what the reader gets rather
than describing the section. One-line change if you prefer yours.

`#build` heading retitled — see section 3.

---

## What the numbers actually did

Honest scorecard, measured on the output:

| | Before | After |
|---|---|---|
| Body words | 1,844 | 1,386 |
| Content tiles | 13 | 12 |
| Duplicate tiles | 4 | 0 |
| Boxed content cards | 8 | 0 |
| Schema nodes | 4 | 6 |
| Missing stylesheets | 1 | 0 |
| Pages rendering unstyled | 7 | 0 |

Word count fell **24%**. Four duplicate tiles came out and three compare
cards went in, so the page carries one tile fewer than it started with and
every remaining tile says something the page does not say elsewhere.

Nav: **21 destinations, unchanged in count**, but reorganised so Security is its own
labelled group rather than a footnote inside "Why WhyUser".

---

## Two things I did not do

**I did not number the four test cards.** The eyebrow is renamed, but the
cards still open in the buyer's voice — *"Everyone said yes. Nothing moved.
Nobody says why."* Numbering them "Feature 1–4" would throw that away, and
ngrok names its blocks rather than numbering them too.

**I did not consolidate the 989KB of inline CSS.** That's the biggest
remaining quality issue — 105KB of CSS inline on the homepage to deliver
1,601 words, copy-pasted across 28 pages so nothing caches, with 196
`!important` in two patch layers named `-fix` and `-readability`. It's also
the change most likely to break something visually, so it deserves its own
pass with a browser open. Worth doing next.

---

# Pass 8 — Sample Reports repositioned

Moved above Glossary within Resources. Desktop nav, mobile nav and footer,
all 28 pages.

```
Read before you buy
  ROI Calculator
  FAQ
  Sample Reports     <- was first, now third
  Glossary
Security
  Architecture & Data Flow
  Security
  DPA
  Privacy
```

Verified across all 28 pages in all three places: nav, mobile nav, footer.
