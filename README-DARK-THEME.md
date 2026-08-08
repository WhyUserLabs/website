# WhyUser dark theme bundle

Everything here is drop-in. One new stylesheet, plus every HTML page with a
single `<link>` added. No existing CSS was edited.

---

## What's in the bundle

| File | What changed |
|---|---|
| `assets/dark-theme.css` | **New file.** The entire dark theme. |
| `index.html` | Copy revisions from earlier + dark link. |
| 30 other `.html` files | Dark link + `color-scheme` / `theme-color` meta only. No copy or markup changes. |

---

## How to apply

1. Upload `assets/dark-theme.css` to your existing `assets/` folder, alongside
   `whyuser-pages.css`.
2. Replace the HTML files. **The files in this bundle are flat, matching the
   snapshot you gave me. Put each one back in the folder it came from:**

   - 18 files at the site root
   - 9 files in `glossary/` — `behavioral-state`, `buying-committee-simulation`,
     `conflict-graph`, `dark-funnel`, `evidence-ledger`,
     `pre-launch-stress-test`, `scent-trail`, `silent-veto`, `synthetic-persona`
   - 4 files in `compare/` — `synthetic-personas-vs-buyer-panels`,
     `whyuser-vs-building-it-yourself`, `whyuser-vs-chatgpt-and-claude`,
     `whyuser-vs-internal-review`

   The link path is already correct per file (`assets/…` at root,
   `../assets/…` one level deep), matching how you reference
   `whyuser-pages.css` today.

**To revert any page**, delete its one `<link>` line. To revert the whole site,
delete `dark-theme.css`.

---

## How it works

The theme is a token override plus component patches, loaded last so it wins on
source order.

The one non-obvious decision: **in light mode your product frames contrast by
being dark.** On a dark canvas that reads as a hole in the layout. So the
relationship inverts — the canvas is `#08080b` and the frames sit *lighter* at
`#131318`, lifted by border and shadow. That's why the Conflict Graph and
Evidence Ledger still read as objects.

Other things that don't flip automatically and needed explicit handling:

- **Brand violet** `#6d28d9` fails contrast on black → lifted to `#a78bfa`.
- **Primary button** was `background: var(--ink)` + `color: white`, which became
  white-on-white → now dark text on a white button.
- **`--dim`** at `#71717a` is unreadable on black and carries every mono
  eyebrow → lifted to `#8e8e99`.
- **Anti-ICP block and footer** were `background: var(--ink)` → would have
  become white slabs.
- **Dot grid** dots were `rgba(9,9,11,0.05)`, invisible on black.
- **Logos and wordmark** ship dark-on-light → inverted with a CSS filter.
- **ROI calculator** sets several inks with `!important`, so those needed
  matching weight to override.
- **contact.html / success.html** render from the Tailwind CDN, so their colours
  are utility classes, patched separately.

### Sections you can delete without breaking anything

- The two `radial-gradient` washes in the `body` rule — the only decorative
  flourish. Delete for a flat black page.
- Section 9 (`@media print`) forces the ROI workbook back to black-on-white so
  it doesn't print as a black rectangle for a CFO. Keep this.

---

## QA that was run

All 31 pages rendered headless at 1440px:

- 31/31 resolve the dark token
- 0 JS errors
- 0 dark-on-dark text (automated luminance contrast sweep over every text node,
  walking up the DOM for the effective background)

Four bugs the sweep caught and that are now fixed: the ROI calculator's
`!important` inks, `contact.html`'s violet eyebrow, `success.html`'s
`text-slate-950` headings, and a light nav bar from `bg-white/80`.

---

## Three things still open

**1. The Tally form can't be themed from CSS.** It's a cross-origin iframe, so
page CSS cannot reach inside it, and your embed uses `transparentBackground=1`
— Tally's dark text would sit on your dark page and vanish. The theme holds the
form on a deliberate light card so the page stays usable. **The real fix is
theming the form inside Tally's own designer**, then deleting the `.tally-wrap`
rule. Right now it's the one element that looks like a patch.

**2. The 13 shared-CSS pages need a visual pass.** `assets/whyuser-pages.css`
wasn't in the snapshot you gave me, so I could not see it. Those pages use the
same class names as the rest of the site (`nav`, `footer`, `btn-primary`,
`wrap`, `cmp`, `prose`), so the component patches should cover them — but I
verified the token flip, not the composited result. Load one glossary page and
one compare page first.

**3. Your product screenshots are captures of the light UI.** `*_simulation.png`
and `audience_discovery.png` glare against a dark page. The theme dims them
slightly as a stopgap. Recapture them from a dark build when you can.

---

## One judgement worth revisiting

Your credibility system was built on *contrast between page and product*: a
calm light document with dark product artifacts inside it. Going dark spends
that contrast and buys it back with elevation and shadow, which is a subtler
effect. The hero, the comparison table and the four trust blocks are all better
dark. The anti-ICP section is weaker — it was a dark slab in a bright page, and
that tonal shift is gone. The theme gives it a brand-tinted edge and glow to
compensate, but it no longer stops you the way it did.

Worth scrolling both versions end to end before you commit.
