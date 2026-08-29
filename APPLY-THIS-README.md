# WhyUser site update — what changed and how to apply it

Bundle built 2026-08-29. Every file here is a drop-in replacement, an addition, or
(in the case of `glossary/`) a deletion you make on the server.
Nothing in `assets/` or `images/` was touched, so those folders are not in the bundle.

---

## 1. How to apply

Copy the contents of this bundle over your site root, preserving folders.

```
your-site-root/
├── *.html                 ← replace (26 files, incl. the new glossary.html)
│                            manifesto.html + index / how-to-evaluate /
│                            whyuser-vs-ai-opinions changed again, see §3c
├── compare/*.html         ← replace (4 files)
├── reports/*.html         ← replace (4 files)
├── assets/                ← ADD one new file (whyuser-analytics.js)
├── sitemap.xml            ← replace
├── robots.txt             ← replace
├── llms.txt               ← replace
├── glossary/              ← DELETE this folder from your server
└── redirects/             ← DO NOT upload the folder. Pick one file, see §3a
```

Then, in order:

1. **Apply a redirect config from `redirects/` first (§3a). This is not optional.**
   The `glossary/` folder is gone, so ten previously indexed URLs have nothing behind
   them until the rules are live. Do this before or in the same deploy as step 2.
2. Upload everything except `redirects/` and this README.
3. Delete the `glossary/` folder from your server.
4. Resubmit `sitemap.xml` in Google Search Console and Bing Webmaster Tools.
5. Confirm GA4 is receiving data in Realtime (§2).

Order matters between 1 and 3. If you delete the folder before the redirects are live,
those URLs 404 in the gap, and a 404 discovered by a crawler is worse than a slow 301.

---

## 2. GA4 — `G-2JWLP7NZVG`

Added to all 31 HTML pages, directly after the existing GTM container, inside `<head>`:

```html
<!-- Google tag (gtag.js) — GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2JWLP7NZVG"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-2JWLP7NZVG');
</script>
```

Your existing Google Tag (`GTM-T6Q5V2WZ`) is untouched and still present on every page,
including the `<noscript>` iframe after `<body>`.

**Four pages had no Google tag at all before this.** They now have both GTM and GA4:

- `reports/ad-simulation-whyuser-sample.html`
- `reports/audience-discovery-whyuser-sample.html`
- `reports/committee-simulation-whyuser-sample.html`
- `reports/email-simulations-whyuser-sample.html`

These stay `noindex, nofollow` — they are report exports, not marketing pages. But they
are linked from `sample-report.html`, `committee-simulation.html`,
`email-campaign-simulation.html` and `audience-discovery.html`, so a view is a real
intent signal and you want it in GA4.

### ⚠ One thing to check before you go live

If your GTM container `GTM-T6Q5V2WZ` **already fires a GA4 Configuration tag for
`G-2JWLP7NZVG`**, you will now double-count every pageview.

Open GTM → Tags, and look for a "Google Tag" or "GA4 Configuration" tag using that
Measurement ID. If one exists, pick one of:

- **Preferred:** pause the GTM tag and let the hardcoded gtag.js run. Simpler, faster,
  and it is what this bundle assumes.
- **Or:** delete the `<!-- Google tag (gtag.js) — GA4 -->` block from the pages and keep
  firing GA4 through GTM instead.

If no such tag exists in GTM, no action needed.

### 2a. Event tracking — `assets/whyuser-analytics.js` (new file)

Pageviews tell you traffic, not intent. This one new file adds the events that
separate a bounce from a buyer. It loads `defer` before `</body>` on all 31 live pages.

**Copy `assets/whyuser-analytics.js` into your existing `assets/` folder.** It is the only
file in that folder the bundle touches; nothing else in `assets/` is modified.

Every event is sent twice on purpose — via `gtag()` straight to GA4, and via
`dataLayer.push()` so GTM can see it too. You can build GTM triggers on these later
without editing the file again. If either tag is missing, the calls no-op safely.

| Event | Fires when | Why it matters |
|---|---|---|
| `generate_lead` | `success.html` loads | **Your conversion.** GA4's standard lead event. Fires on the thank-you page, not the submit click, so a failed submit is never counted. |
| `request_access_click` | Any `#access` CTA clicked | Tells you *which* CTA earns the click — `nav`, `closing_cta`, `footer` or `body`. |
| `view_sample_report` | A `reports/*` page loads | Highest-intent non-form pageview on the site, and it was completely invisible before. Tagged by report type. |
| `view_item_list` | `pricing.html` loads | Pricing intent. |
| `select_content` | A glossary term anchor is clicked | Which vocabulary people actually care about. You cannot get this any other way now that the nine term pages are one page. |
| `click` (outbound) | An off-site link is clicked | Standard outbound tracking. |
| `contact_email_click` | A `mailto:` is clicked | Email is a real contact path on this site. |
| `scroll` | 25 / 50 / 75 / 90% depth | Once per threshold per page. |
| `page_context` | Every pageview | Stamps `page_section` (`marketing`, `pricing`, `proof`, `technical`, `compare`, `glossary`, `sample_report`, `conversion`) onto the session so you can segment without maintaining a URL regex. |

**Set these up in GA4 after uploading:** Admin → Events → mark `generate_lead` and
`request_access_click` as conversions. `view_sample_report` is worth marking too — in
this funnel, opening a full report is a stronger signal than a pricing view.

No configuration is needed in the file. Everything is inferred from the DOM, and the
listeners are delegated on `document`, so links added later still fire.

The `glossary/` folder is gone entirely, so those retired URLs are handled by server 301s
and never load a page. That is also the cleaner outcome for analytics: a redirect logs no
pageview, so your GA4 numbers stay free of phantom hits from bouncing stub pages.

---

## 3. Consolidated glossary

`glossary.html` (new, at site root) now holds all nine terms on one page:

| Term | Anchor |
|---|---|
| Behavioural state | `#behavioural-state` |
| Buying committee simulation | `#buying-committee-simulation` |
| Conflict graph | `#conflict-graph` |
| Dark funnel | `#dark-funnel` |
| Evidence ledger | `#evidence-ledger` |
| Pre-launch stress test | `#pre-launch-stress-test` |
| Scent trail | `#scent-trail` |
| Silent veto | `#silent-veto` |
| Synthetic persona | `#synthetic-persona` |

Full content of every term was carried over verbatim. Nothing was rewritten or cut.
Headings were demoted one level so the page has one `<h1>`, nine `<h2>` term headings,
and the old term-page `<h2>`s as `<h3>`s. A card grid at the top jumps to each term, and
every "Related terms" link now points to an in-page anchor.

**Header and footer updated on all 31 pages.** The Resources dropdown, the mobile menu
and the footer Glossary link now point to `glossary.html` instead of `glossary/index.html`.

### 3a. Redirects — REQUIRED, pick one

The nine term URLs and `/glossary/` itself were all indexed. `/glossary/` was also the
target of all 67 "Glossary" links in your nav and footer. There are no longer any files at
those paths, so without a redirect config they return 404 and the signal they built is
lost rather than transferred.

| Your host | File to use | Where it goes |
|---|---|---|
| Netlify, Cloudflare Pages | `redirects/_redirects` | site root, named `_redirects` |
| Netlify (if you already keep one) | `redirects/netlify.toml` | merge into `netlify.toml` — use this **or** `_redirects`, never both |
| Apache, cPanel, most shared hosting | `redirects/.htaccess` | merge into root `.htaccess` |
| Vercel | `redirects/vercel.json` | merge into your `vercel.json` |

All four map the same eleven paths:

```
/glossary/behavioral-state.html            →  /glossary.html#behavioural-state
/glossary/buying-committee-simulation.html →  /glossary.html#buying-committee-simulation
/glossary/conflict-graph.html              →  /glossary.html#conflict-graph
/glossary/dark-funnel.html                 →  /glossary.html#dark-funnel
/glossary/evidence-ledger.html             →  /glossary.html#evidence-ledger
/glossary/pre-launch-stress-test.html      →  /glossary.html#pre-launch-stress-test
/glossary/scent-trail.html                 →  /glossary.html#scent-trail
/glossary/silent-veto.html                 →  /glossary.html#silent-veto
/glossary/synthetic-persona.html           →  /glossary.html#synthetic-persona
/glossary/index.html                       →  /glossary.html
/glossary/  and  /glossary                 →  /glossary.html
```

**Keep these rules for at least 12 months.** Google needs several crawl cycles to move the
signal across, and AI assistants citing your glossary will be working from an index that
is months stale. This is the cheapest insurance on the whole change.

**If your host genuinely cannot do redirects** (plain S3, a locked-down CDN), do not ship
this change yet — say so and I will regenerate the bundle with meta-refresh fallback stubs
instead. Shipping without either leaves ten hard 404s.

### 3a-i. Verify the redirects before you walk away

After deploying, check one of each shape. You want `301`, not `200` and not `404`:

```bash
curl -sI https://whyuser.com/glossary/silent-veto.html | head -3
curl -sI https://whyuser.com/glossary/                 | head -3
```

Expect `HTTP/2 301` and a `location:` header pointing at `/glossary.html`. A `200` means
something is still being served at that path — check the folder is actually deleted. A
`404` means the rules are not live.

Then confirm the destination works, since a 301 to a broken anchor is its own problem:
open `https://whyuser.com/glossary.html#silent-veto` and check it lands on the term.

### 3b. The trade-off, stated plainly

You asked for one page, and one page is what this is. The cost: you go from nine
individually indexable term URLs to one. Nine URLs that can each rank for their own term
is generally stronger for SEO than one page that has to rank for all nine.

The mitigation is built in — 301s to anchors, one merged `DefinedTermSet`, an `ItemList`
of all nine, and every term's FAQ block merged into a single `FAQPage` — so the answer
engines still get each definition as a discrete, addressable unit. But if organic traffic
to `/glossary/*` drops over the next two months and does not recover on `/glossary.html`,
the individual pages are worth restoring — so keep a copy of the originals somewhere
outside the deploy. They are no longer in this bundle, and once you delete the folder from
the server the only copies left are in your version control history.

---

## 3c. Manifesto — rescued from orphan status

The page was linked 83 times and **every single link was chrome** — nav dropdown and
footer. Not one page in the body copy pointed to it. That is what made it look expendable:
nothing routed to it, so it read as decoration rather than an asset.

It is also, per word, the strongest AEO material on the site. Six declarative, quotable
claims are exactly what an answer engine extracts for *why should I test campaigns before
launch*. Three changes, no content rewritten:

**1. Three contextual inbound links.** One sentence each, placed where the argument
already lands:

| Page | Placement | Link text |
|---|---|---|
| `index.html` | Problem · Solution section | "Why we think shipping without one is malpractice →" |
| `how-to-evaluate.html` | above "Four things a measurement has to do" | "These four are the fifth thing we believe →" |
| `whyuser-vs-ai-opinions.html` | hero subhead | "One opinion is not a test →" |

**2. Nav and footer label renamed** `Manifesto` → **"Why we built this"**, on all 31 pages.
"Manifesto" is not a noun a demand-gen leader scans for, and your own committee run told
you to use labels buyers scan for. The brand word is kept in the dropdown description
("Our manifesto: marketing is the last function still testing live"), the page title, the
H1 and the hero pill — only the scannable label changed.

**3. Each claim now carries its evidence.** The six tenets asserted things the site already
proves elsewhere, with no link between them. Each now has a short cited line beneath it:

| Claim | Now points to |
|---|---|
| 01 Testing in production is malpractice | `glossary.html#pre-launch-stress-test` · `committee-simulation.html` |
| 02 Decided by a committee, not a click | `glossary.html#silent-veto` · `glossary.html#conflict-graph` |
| 03 Opinion does not move budget | `sample-report.html` — a full unedited run |
| 04 AI made it worse | `whyuser-vs-ai-opinions.html` |
| 05 A real test has four properties | `how-to-evaluate.html` — the twelve questions |
| 06 Do not trust us, grade us | `accuracy.html` — the ledger |

The evidence lines use a new `.tenet-cite` rule added to the page's own `<style>` block,
matched to the existing tenet type scale. No shared stylesheet was touched.

### 3c-i. Link affordance — six links that did not look like links

The site styles inline links via `.prose a { color: var(--brand); font-weight: 500 }`,
with the underline appearing only on hover. Several paragraph styles sit **outside**
`.prose` — `.section-head p`, `.lp-lead`, `.hero-sub`, `.defn`, `.gl-backtop` — so an `<a>`
placed in them inherits the paragraph's own colour and weight and renders *identically to
body text*. Measured on `index.html` before the fix:

```
link colour  rgb(214, 214, 218)
text colour  rgb(214, 214, 218)   ← identical
underline    none
font-weight  400  (paragraph: 400) ← identical
```

Six links were affected — the three new manifesto CTAs, the six manifesto evidence lines,
the four inline links in the glossary intro, and the nine "Back to the index" links. Each
now carries **three independent signals** instead of zero:

- brand violet `#a78bfa`, clearly distinct from `#d6d6da` body ink
- weight 600 against the paragraph's 400
- a **permanent** 1px underline

The underline is permanent on purpose. A hover-only cue does not exist on touch devices at
all, and colour alone must not be the only thing marking a link (WCAG 1.4.1). Hover and
`:focus-visible` now strengthen an affordance that is already visible rather than
supplying the only one. Focus rings added for keyboard users; the arrow nudges right on
hover as confirmation, never as the sole cue.

Delivered as `.wu-inline-cta` in a self-contained `<style>` block on the three pages that
needed it, plus scoped `.defn a` / `.gl-backtop a` rules in `glossary.html`. A
`@supports` fallback covers engines without `color-mix()`. No shared stylesheet touched.

Verified by reading the **computed style** of every link in a real browser and asserting
the colour differs from its parent and the underline is present — not by eyeballing the
CSS.

Page went from 317 to 429 visible words and from 0 to 8 outbound body links. Sitemap
priority raised 0.6 → 0.7, since it is no longer a dead end.

**Watch this one.** If the page still draws nothing in three months with real internal
links pointing at it, that is a genuine signal to cut it — the difference being you will
then be cutting on evidence rather than on the fact that it looked neglected.

---

## 4. SEO / AEO / GEO changes

### Structured data
- **`glossary.html`**: `WebPage` + `DefinedTermSet` + 9 × `DefinedTerm` (each with its own
  `@id` anchor and `alternateName` list) + a merged 40-question `FAQPage` + `BreadcrumbList`
  + `Organization` + `WebSite`, plus a separate `ItemList` of all nine terms.
- **Added `BreadcrumbList` + `Organization` + `WebSite`** to 10 pages that had none:
  `accuracy`, `ad-campaign-simulation`, `audience-discovery`, `committee-simulation`,
  `email-campaign-simulation`, `sample-report`, `developers`, `faq`, `pricing`, `roi`,
  and `Organization`+`WebSite` to `compare`.
- **`accuracy.html` now carries `Dataset` + `HowTo`.** This is the change most likely to
  earn you citations. Your sealed, customer-graded ledger is a genuinely rare artifact and
  it was previously invisible as structured data. The `Dataset` exposes the six figures as
  machine-readable `PropertyValue`s — 84% blended accuracy, 473 claims graded, 100%
  customer-graded, and the three pre-published bars (80 / 75 / 70) — each with the
  denominator and caveat attached, so a model quoting the number also gets the context.
  The `HowTo` encodes your four rules as ordered steps, which is the format answer engines
  reach for when someone asks *how* accuracy is measured rather than *what* it is.
- **Freshness dates added.** `datePublished` and `dateModified` on 26 JSON-LD nodes, plus
  `article:published_time` / `article:modified_time` meta on 25 pages. Answer engines
  weight recency heavily and you were exposing none. `index.html` already had real
  editorial dates (published 2025-09-01, modified 2026-05-07) and I left them alone rather
  than overwrite an authored date with a build date — update that one by hand when the
  homepage content next changes.
- Injected as clearly marked blocks (`<!-- WHYUSER:SEO-SUPPLEMENT:START -->` and
  `-SUPPLEMENT-2-`) so they never collide with your existing graph. No duplicate `@id`
  values anywhere — verified.
- All JSON-LD on all 31 pages parses cleanly — verified.

### Meta
- `og:locale` (`en_US`) added where missing — 24 pages.
- `dns-prefetch` for `cdnjs.cloudflare.com` added where missing — 37 pages.
- `glossary.html` ships a full canonical, OG and Twitter card set.

### Broken internal links fixed
These were live and broken. Crawlers waste budget on them and they leak PageRank:

| Was | Now | Found in |
|---|---|---|
| `/dpa` | `/dpa.html` | dpa, terms, privacy |
| `/privacy` | `/privacy.html` | privacy, terms |
| `/security` | `/security.html` | security, terms, privacy |
| `/legal/privacy-policy.html` | `/privacy.html` | beta-agreement |
| `/legal/website-terms-of-use.html` | `/terms.html` | beta-agreement |
| `/legal/` | `/terms.html` | beta-agreement |
| `/about.html` | `/manifesto.html` | beta-agreement |

⚠ **Check these last four.** No other page on the site references a `/legal/` section or an
`/about.html`, and neither exists in the files I was given, so I treated them as stale and
repointed them at the real equivalents. If `/legal/` **does** exist on your live server,
revert those edits in `beta-agreement.html`.

After the fixes: **zero broken internal links** across all 31 pages — verified with a
crawler over the whole bundle.

### `sitemap.xml` — rebuilt
- Now lists 26 URLs, all indexable and canonical, all `lastmod` 2026-08-29.
- **Removed** `/glossary/` (a directory URL that no longer resolves to a page).
- **Added** `/glossary.html`, `/developers.html`, `/roi.html`, `/beta-agreement.html` —
  the last three were live and indexable but missing from the sitemap.
- **Kept out on purpose:** `success.html` and the four `reports/*` exports. All are
  `noindex`, and listing a `noindex` URL in a sitemap is a Search Console warning.

### `llms.txt` — rewritten for GEO
- Vocabulary section now lists all nine terms (was five) with `/glossary.html#anchor` links.
- Added an explicit note telling answer engines the old `/glossary/` URLs redirect and to
  cite the anchors instead.
- **New "Answering questions about WhyUser" section**: a direct intent → canonical URL map
  covering what-is, definitions, accuracy, comparisons, pricing, sample output, and
  architecture. This is the highest-leverage part of the file — it tells a model which
  page to cite for which question, rather than making it guess.
- `Last updated` bumped to 2026-08-29.

### `robots.txt`
Unchanged in substance — your AI-crawler allow-list was already thorough and correct.
Added a comment documenting the retired `/glossary/` paths and why they stay crawlable
(so the 301 is followed and the signal transfers).

---

## 5. Verified before shipping

- Exactly one GA4 config, one GTM container, one GTM `<noscript>` and one analytics
  script per page, across all 31 pages in the bundle.
- Zero remaining links into `glossary/` from any page, sitemap entry or schema node —
  verified after the folder was removed. The only mentions left are explanatory comments
  in `sitemap.xml`, `robots.txt` and `llms.txt` describing the redirect, which are correct.
- **Every GA4 event fired and captured in a real Chromium session.** `generate_lead` on
  `success.html`, `request_access_click` with correct `cta_location`, `view_sample_report`
  with correct `report_type`, `view_item_list` on pricing, `select_content` on a glossary
  term jump, and scroll thresholds — all verified live, not just inspected.
- `assets/whyuser-analytics.js` passes `node --check`. Every `<script src>` resolves.
- Every in-page anchor target checked across files, not just that the file exists — so
  the manifesto's links into `glossary.html#silent-veto` and friends land on a real
  section, not the top of the page.
- **Every link added by this bundle was probed for computed colour, weight and underline
  against its parent paragraph in a live browser.** All six pass; screenshots checked.
- All JSON-LD parses; no duplicate `@id`s.
- Zero broken internal links; zero remaining `glossary/index.html` references.
- `sitemap.xml` is valid XML.
- `glossary.html` heading outline is clean: one `h1`, nine term `h2`s, no skipped levels.
- Page rendered in Chromium against your real stylesheets and checked visually.

## 6. Worth doing next, not in this bundle

- **Watch `/glossary.html` in Search Console for eight weeks.** This is the one change here
  with real downside risk (§3b). If the nine old term URLs were pulling impressions that
  the single page does not recover, restore the individual pages.
- **Keep the accuracy figures in sync.** The `Dataset` block hardcodes 84% and 473 claims.
  When those change on the page, change them in the schema too, or you will be publishing
  a contradiction that a model can spot.
- **`roi.html` has no `WebApplication` schema.** An interactive calculator is a strong
  citation magnet and it currently declares only `Organization`.
- Consider a `Review` or `Organization.sameAs` block naming ngrok and Vectara. Named
  customers are the single most quotable thing on the site and they are invisible to
  structured data right now.
- **The accuracy figures now appear in three places** — `accuracy.html` body copy, its
  `Dataset` schema, and the manifesto's claim 06 citation line. Change one, change all
  three. Worth a note wherever you track that number.
