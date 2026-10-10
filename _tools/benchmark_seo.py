#!/usr/bin/env python3
"""Search and answer-engine pass for the benchmark data pages.

Run from the repo root after copying a fresh build into benchmarks/<slug>/:

    python3 _tools/benchmark_seo.py           # update every benchmarks/<slug>/index.html
    python3 _tools/benchmark_seo.py --check   # report only, change nothing

Safe to re-run: everything it adds sits between wu-seo markers and is
rebuilt from the page's own data (the `var D=` JSON), so a number here can
never disagree with the page. Stdlib only.

What it does to each page:
  1. <title> and meta description that name the category and the year.
  2. robots, og:site_name/locale/image:alt, twitter:* tags.
  3. One JSON-LD @graph: WebPage, Dataset (every count as a PropertyValue
     with its denominator), BreadcrumbList, Organization, WebSite.
  4. Every company row as plain HTML inside a <details>, so crawlers that
     don't run JavaScript can read the quotes.
  5. Links to the sibling benchmark pages.
  6. The 48 KB dog mark, inlined twice, moves to one shared file
     (benchmarks/mark.png). Saves about 128 KB per page.
And it warns when sitemap.xml, llms.txt or the hub don't list a page.

Leaves alone: the findings, cards, spotted cards, forms and all scripts.
Mirror these changes in build_page.py when it is next edited.
"""
import base64
import datetime as dt
import glob
import html
import json
import os
import re
import sys

SITE = "https://whyuser.com/"
ORG = SITE + "#organization"
WEBSITE = SITE + "#website"
HUB = SITE + "benchmarks/"
LOGO = SITE + "images/whyuser-logo.png"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"

# Plain wording for each check key in the page data (D.companies[].c / .f).
CHECK = {
    "Says what it is": "say what the product is",
    "Says who it's for": "say who it's for",
    "Says what it replaces": "say what it replaces",
    "Says why it's better": "say why it's better, in specifics",
    "Social proof": "show logos, user counts or quotes",
    "Value proof": "show a named customer's result",
    "ROI proof": "put a number on money or time saved",
    "Trust proof": "name a certification, an SLA or a trust center",
    "Technical proof": "show benchmarks, open source or code",
    "Third-party proof": "cite analysts, review sites or awards",
    "Risk reversal": "offer a free tier or a trial",
}
FACT = {
    "Names the tool it replaces": "name the tool or rival they replace",
    "Mentions SOC 2": "mention SOC 2",
    "Links to a trust page": "link to a trust page",
    "Links to pricing": "link to pricing",
    "Has a demo button": "have a demo button",
    "Has a free-start button": "have a free-start button",
    "Links to a customer story": "link to a customer story",
    "Section for security review": "have a section written for security review or procurement",
}

HEAD_RE = re.compile(r"<!-- wu-seo:head -->.*?<!-- /wu-seo:head -->\n?", re.S)
ROWS_RE = re.compile(r"<!-- wu-seo:rows -->.*?<!-- /wu-seo:rows -->\n?", re.S)
SIB_RE = re.compile(r'<a class="wu-sib"[^>]*>.*?</a>')
DATA_RE = re.compile(r"var D=(\{.*?\});\n", re.S)
MARK_RE = re.compile(r'data:image/png;base64,[A-Za-z0-9+/=]+')

CSS = """.allrows{margin-top:32px;border-top:1px solid var(--rule);padding-top:14px}
.allrows>summary{font-weight:600;font-size:14.5px;cursor:pointer;color:var(--ink)}
.allrows .intro{margin:10px 0 0;color:var(--ink3);font-size:14px}
.rows{display:grid;margin-top:10px}
@media (min-width:960px){.rows{grid-template-columns:1fr 1fr;column-gap:48px}}
.srow{border-top:1px solid var(--rule2);padding:14px 0;min-width:0}
.srow h3{font-size:16px;letter-spacing:-.01em}
.srow h3 small{font-weight:500;font-size:13px;color:var(--ink3);margin-left:6px}
.srow ul{margin:8px 0 0;padding-left:18px;font-size:14px;line-height:1.45;color:var(--ink2)}
.srow li{margin:4px 0}
.srow q{font-family:var(--fd);overflow-wrap:anywhere}
.srow p{margin:6px 0 0;font-size:13.5px;line-height:1.45;color:var(--ink3);overflow-wrap:anywhere}
.srow a{text-underline-offset:3px}"""


def esc(s):
    return html.escape(str(s or ""), quote=True)


def low(s):
    return s[:1].lower() + s[1:] if s and not s[:2].isupper() else s


def iso_date(when):
    return dt.datetime.strptime(when, "%d %b %Y").date().isoformat()


def load(path):
    s = open(path, encoding="utf-8").read()
    m = DATA_RE.search(s)
    if not m:
        sys.exit(f"{path}: no `var D=` data block. Is this a benchmark page?")
    return s, json.loads(m.group(1))


def counts(D):
    """Every count, computed from the rows. Returns a list of (name, n, sentence-tail)."""
    cos, N = D["companies"], D["N"]
    if len(cos) != N:
        sys.exit(f"{D['slug']}: D.N is {N} but there are {len(cos)} rows.")

    def c(co, key):
        hit = [x for x in co["c"] if x["k"] == key]
        return hit[0] if hit else {"y": False, "fs": None}

    def f(co, key):
        hit = [x for x in co["f"] if x["k"] == key]
        return bool(hit and hit[0]["y"])

    out = []
    for key, words in CHECK.items():
        out.append((key, sum(1 for co in cos if c(co, key)["y"]), words))
    out.append(("Says what it is, on the first screen",
                sum(1 for co in cos if c(co, "Says what it is")["y"] and c(co, "Says what it is").get("fs") is True),
                "say what the product is on the first screen"))
    out.append(("Says who it's for, on the first screen",
                sum(1 for co in cos if c(co, "Says who it's for")["y"] and c(co, "Says who it's for").get("fs") is True),
                "say who they're for on the first screen"))
    four = ["Says what it is", "Says who it's for", "Says what it replaces", "Says why it's better"]
    out.append(("Answers all four positioning questions",
                sum(1 for co in cos if all(c(co, k)["y"] for k in four)),
                "answer all four: what it is, who it's for, what it replaces, why it's better"))
    out.append(("No ROI proof and no third-party proof",
                sum(1 for co in cos if not c(co, "ROI proof")["y"] and not c(co, "Third-party proof")["y"]),
                "show no ROI proof and no third-party proof"))
    out.append(("Logos or quotes and nothing more",
                sum(1 for co in cos if c(co, "Social proof")["y"] and not c(co, "Value proof")["y"] and not c(co, "ROI proof")["y"]),
                "show logos or quotes and nothing more: no named customer's result, no money or time saved"))
    for key, words in FACT.items():
        out.append((key, sum(1 for co in cos if f(co, key)), words))
    demo = lambda co: f(co, "Has a demo button")
    free = lambda co: f(co, "Has a free-start button")
    out.append(("Offers both a free start and a demo", sum(1 for co in cos if demo(co) and free(co)),
                "offer both a free start and a demo"))
    out.append(("Offers neither a free start nor a demo", sum(1 for co in cos if not demo(co) and not free(co)),
                "offer neither a free start nor a demo"))
    return out


def row_html(D, co):
    yes_n = sum(1 for x in co["c"] if x["y"])
    dom = re.sub(r"^https?://(www\.)?", "", co["u"]).rstrip("/")
    items, nos = [], []
    for x in co["c"]:
        if x["y"]:
            fs = " (first screen)" if x.get("fs") is True else ""
            q = f": <q>{esc(x['q'])}</q>" if x.get("q") else ""
            items.append(f"<li><b>{esc(x['k'])}</b>{fs}{q}</li>")
        else:
            nos.append(low(x["k"]))
    facts = []
    for x in co["f"]:
        if x["y"]:
            q = x.get("q") or ""
            facts.append(low(x["k"]) + (f" (<q>{esc(q)}</q>)" if len(q) > 12 else ""))
    out = [f'<article class="srow" id="row-{esc(co["a"])}">',
           f'<h3>{esc(co["n"])} <small>passes {yes_n} of {D["nchecks"]}</small></h3>',
           f'<p><a href="{esc(co["u"])}" rel="nofollow noopener" target="_blank">{esc(dom)}</a> · '
           f'<a href="#{esc(co["a"])}">Open this row</a></p>']
    if items:
        out.append("<ul>" + "".join(items) + "</ul>")
    if nos:
        out.append(f"<p><b>No:</b> {esc(', '.join(nos))}.</p>")
    if facts:
        out.append(f"<p><b>Page facts:</b> {', '.join(facts)}.</p>")
    out.append("</article>")
    return "".join(out)


def build(path, siblings, mark_rel, check):
    s, D = load(path)
    N, name, slug, when = D["N"], D["name"], D["slug"], D["when"]
    day = iso_date(when)
    base = D["base"]
    if base != f"{HUB}{slug}/":
        sys.exit(f"{path}: D.base {base} does not match the folder.")
    K = {k: n for k, n, _ in counts(D)}
    h1 = html.unescape(re.search(r"<h1>(.*?)</h1>", s).group(1))
    og_title = html.unescape(re.search(r'<meta property="og:title" content="([^"]*)">', s).group(1))
    og_desc = html.unescape(re.search(r'<meta property="og:description" content="([^"]*)">', s).group(1))
    og_img = re.search(r'<meta property="og:image" content="([^"]*)">', s).group(1)

    title = f"{name} homepage benchmark {day[:4]}: {N} pages | WhyUser"
    # The builder's lead finding is the first sentence of og:description (this pass never edits it).
    lead = og_desc.split(". ")[0].rstrip(".") + "."
    desc = f"{N} {name} homepages, counted. {lead} Every yes shows the line it came from."
    img_alt = f"Counted: {N} {name} homepages. {h1} {lead}"

    variables = [{"@type": "PropertyValue", "name": k, "value": n, "maxValue": N, "unitText": "homepages",
                  "description": f"{n} of {N} {name} homepages {w}."} for k, n, w in counts(D)]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": base + "#webpage", "url": base, "name": title, "description": desc,
         "inLanguage": "en", "isPartOf": {"@id": WEBSITE}, "publisher": {"@id": ORG},
         "dateModified": day, "breadcrumb": {"@id": base + "#breadcrumb"},
         "mainEntity": {"@id": base + "#dataset"}, "about": {"@id": base + "#dataset"},
         "primaryImageOfPage": {"@type": "ImageObject", "url": og_img, "width": 1200, "height": 630}},
        {"@type": "Dataset", "@id": base + "#dataset", "name": f"{name} homepage benchmark: {N} homepages counted, {when}",
         "alternateName": D["title"], "url": base,
         "description": (f"{N} {name} homepages, captured {when} and checked for 11 things a buyer looks for: what the "
                         "product is, who it's for, what it replaces, why it's better, and seven kinds of proof (social, "
                         "value, ROI, trust, technical, third-party and risk reversal). Every yes rests on a line copied "
                         "word for word from the page, and code confirmed each line is there. Nothing is simulated or "
                         "estimated. Every company has its own row. WhyUser's own customers and design partners are left out."),
         "creator": {"@id": ORG}, "publisher": {"@id": ORG}, "isAccessibleForFree": True, "license": LICENSE,
         "keywords": [f"{name} homepage benchmark", "B2B homepage benchmark", "homepage positioning",
                      "B2B buying committee", "social proof", "ROI proof", "SOC 2", "homepage messaging"],
         "temporalCoverage": day, "datePublished": day, "dateModified": day, "version": day,
         "image": og_img,
         "measurementTechnique": ("A real browser opened each homepage on the capture date at desktop size, dismissed "
                                  "the cookie banner and scrolled the full page. A yes needs an exact quote from the page; "
                                  "a quote code could not find became a no. First screen means the top 900 pixels."),
         "includedInDataCatalog": {"@type": "DataCatalog", "name": "WhyUser benchmarks", "url": HUB},
         "variableMeasured": variables},
        {"@type": "BreadcrumbList", "@id": base + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "WhyUser", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "Benchmarks", "item": HUB},
            {"@type": "ListItem", "position": 3, "name": f"{name} benchmark", "item": base}]},
        {"@type": "Organization", "@id": ORG, "name": "WhyUser", "url": SITE, "logo": LOGO},
        {"@type": "WebSite", "@id": WEBSITE, "url": SITE, "name": "WhyUser", "publisher": {"@id": ORG}},
    ]}
    ld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")

    head = "\n".join([
        "<!-- wu-seo:head -->",
        '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">',
        '<meta name="author" content="WhyUser">',
        '<meta property="og:site_name" content="WhyUser"><meta property="og:locale" content="en_US">',
        f'<meta property="og:image:alt" content="{esc(img_alt)}">',
        f'<meta property="article:modified_time" content="{day}T00:00:00+00:00">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(og_title)}"><meta name="twitter:description" content="{esc(og_desc)}">',
        f'<meta name="twitter:image" content="{esc(og_img)}"><meta name="twitter:image:alt" content="{esc(img_alt)}">',
        f'<link rel="icon" type="image/png" href="{mark_rel}">',
        f'<script type="application/ld+json">{ld}</script>',
        f"<style>{CSS}</style>",
        "<!-- /wu-seo:head -->", ""])

    rows = "\n".join([
        "<!-- wu-seo:rows -->",
        f'  <details class="allrows"><summary>Read all {N} rows as text</summary>',
        f'  <p class="intro">The same rows as the picker above, one company after another. Captured {esc(when)}.</p>',
        '  <div class="rows">' + "\n".join(row_html(D, co) for co in D["companies"]) + "</div>",
        "  </details>",
        "<!-- /wu-seo:rows -->", ""])

    t = HEAD_RE.sub("", s)
    t = ROWS_RE.sub("", t)
    t = SIB_RE.sub("", t)
    # Builder tags this pass replaces.
    t = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", t, flags=re.S)
    t = re.sub(r'<link rel="icon" href="data:[^"]*">\n?', "", t)
    t = re.sub(r'<meta name="twitter:card" content="[^"]*">\n?', "", t)
    t = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", t, count=1, flags=re.S)
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', t, count=1)
    t = t.replace('<link rel="preconnect" href="https://fonts.googleapis.com">', head + '<link rel="preconnect" href="https://fonts.googleapis.com">', 1)
    t = re.sub(r'(<img class="mark" src=")data:image/png;base64,[A-Za-z0-9+/=]+(")', rf"\g<1>{mark_rel}\g<2>", t, count=1)
    t = re.sub(r'href="mailto:[^"]*"', lambda m: m.group(0).replace(" ", "%20"), t)
    # Rows go right after the find-your-company grid.
    m = re.search(r'<article class="card panel" id="panel"[^>]*>.*?</article>\s*</div>\n', t, re.S)
    if not m:
        sys.exit(f"{path}: could not find the #panel grid to place the rows after.")
    t = t[:m.end()] + rows + t[m.end():]
    sib = "".join(f'<a class="wu-sib" href="../{esc(sl)}/">{esc(ti)}</a>' for sl, ti in siblings if sl != slug)
    if sib:
        anchor = '<a href="../">All WhyUser benchmarks</a>'
        if anchor not in t:
            sys.exit(f"{path}: could not find the 'All WhyUser benchmarks' link.")
        t = t.replace(anchor, anchor + sib, 1)

    for need in ("wu-seo:head", "wu-seo:rows", 'application/ld+json'):
        if t.count(need) < 1:
            sys.exit(f"{path}: {need} missing after rewrite.")
    if t.count('application/ld+json') != 1:
        sys.exit(f"{path}: expected one JSON-LD block.")

    changed = t != s
    if not check and changed:
        open(path, "w", encoding="utf-8").write(t)
    print(f"{'would update' if check and changed else 'updated' if changed else 'unchanged'}: {path} "
          f"({len(s)//1024} KB -> {len(t)//1024} KB)")
    print(f"  title: {title} ({len(title)} chars)\n  description: {desc} ({len(desc)} chars)")
    return D


def main():
    check = "--check" in sys.argv
    root = os.getcwd()
    if not os.path.isdir(os.path.join(root, "benchmarks")):
        sys.exit("Run from the website repo root.")
    pages = sorted(p for p in glob.glob("benchmarks/*/index.html"))
    if not pages:
        sys.exit("No benchmarks/<slug>/index.html pages found.")
    siblings = []
    for p in pages:
        _, D = load(p)
        siblings.append((D["slug"], D["title"]))

    # Shared mark: write it once from the first page that still inlines it.
    mark = "benchmarks/mark.png"
    if not os.path.exists(mark):
        for p in pages:
            m = re.search(r'<img class="mark" src="data:image/png;base64,([A-Za-z0-9+/=]+)"', open(p).read())
            if m:
                if not check:
                    open(mark, "wb").write(base64.b64decode(m.group(1)))
                print(f"{'would write' if check else 'wrote'}: {mark}")
                break

    for p in pages:
        build(p, siblings, "../mark.png", check)

    # Warn about places that should list every page.
    warn = 0
    for f in ("sitemap.xml", "llms.txt", "benchmarks/index.html"):
        txt = open(f, encoding="utf-8").read() if os.path.exists(f) else ""
        for slug, _ in siblings:
            needle = f"{HUB}{slug}/" if f != "benchmarks/index.html" else f"{slug}/"
            if needle not in txt:
                warn += 1
                print(f"WARN: {f} does not link {needle}")
    print("check done" + (f", {warn} warning(s)" if warn else ", no warnings"))


if __name__ == "__main__":
    main()
