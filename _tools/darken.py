"""Dark mode for whyuser.com.

Rewrites every hardcoded colour in assets/*.css and the site's HTML as
var(--dk-<role>-<hex>, <original>), then regenerates assets/dark-theme.css,
which defines those --dk-* tokens only when the visitor's system is not set
to light. With the system on light the tokens are undefined, every rule falls
back to its original colour, and light mode is unchanged.

Run from the repo root after adding pages or hardcoded colours:

    python3 _tools/darken.py .            # dry run: prints what would change
    python3 _tools/darken.py . --write    # rewrite files + regenerate dark-theme.css

Safe to run more than once: already-converted colours are left alone.
Sample reports in reports/ are skipped (they stay light, like a PDF).
Hand-written dark rules go in _tools/dark_extra.css; the file header in
_tools/dark_header.css.
"""
import re, sys, glob, os, colorsys, collections

ROOT = sys.argv[1]
WRITE = '--write' in sys.argv
PAGE = (0x0b, 0x0d, 0x12)          # dark page colour all contrast is measured against

# ── colour maths ──────────────────────────────────────────────────────
def parse_hex(h):
    h = h.lstrip('#')
    if len(h) in (3, 4): h = ''.join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
    return (r, g, b), a

def to_hex(rgb):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(c))) for c in rgb)

def lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(ch, rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def hls(rgb):
    return colorsys.rgb_to_hls(*(c / 255 for c in rgb))

def from_hls(h, l, s, gray=False):
    if gray: h, s = 222 / 360, min(s, 0.08)   # cool grey, leaning to the cobalt brand
    return tuple(c * 255 for c in colorsys.hls_to_rgb(h, max(0, min(1, l)), max(0, min(1, s))))

def neutral(rgb):
    return max(rgb) - min(rgb) < 22

# ── role mappings: return a dark hex, or None to leave the colour alone ──
def map_text(rgb):
    h, l, s = hls(rgb)
    if neutral(rgb):
        if l >= 0.55: return None                     # already light: sits on a dark element
        return to_hex(from_hls(h, 1 - l * 0.82, 0.05, gray=True))
    if contrast(rgb, PAGE) >= 5.2: return None
    if l > 0.8:                                       # pale tint used as text: leave
        return None
    nl = l
    while contrast(from_hls(h, nl, s), PAGE) < 5.2 and nl < 0.92:
        nl += 0.02
    return to_hex(from_hls(h, nl, min(s, 0.85)))

def map_bg(rgb):
    h, l, s = hls(rgb)
    if l < 0.78: return None                          # mid/dark fills (buttons, bars, bands) stay
    if not neutral(rgb) and s > 0.25 and l < 0.86: return None   # saturated mid tones stay
    nl = 0.07 + (1 - l) * 1.6
    ns = 0.06 if neutral(rgb) else min(s, 0.45)
    return to_hex(from_hls(h, min(nl, 0.32), ns, gray=neutral(rgb)))

def map_line(rgb):
    h, l, s = hls(rgb)
    if l >= 0.75:
        nl = 0.13 + (1 - l) * 0.9
        ns = 0.05 if neutral(rgb) else min(s, 0.5)
        return to_hex(from_hls(h, min(nl, 0.36), ns, gray=neutral(rgb)))
    if neutral(rgb) and l < 0.3:                      # strong dark outline → light outline
        return to_hex(from_hls(h, min(1 - l * 0.85, 0.62), 0.04, gray=True))
    if not neutral(rgb): return map_text(rgb)
    return None

def map_accent(rgb):
    h, l, s = hls(rgb)
    if neutral(rgb):
        if l < 0.5: return map_text(rgb)
        if l > 0.8: return map_bg(rgb)
        return None
    if l > 0.85: return map_bg(rgb)
    return map_text(rgb)

# Cobalt (Nov 2026): the light site is violet; dark mode is cobalt. Every
# violet or indigo colour (hue 240-300) is turned to the cobalt hue before its
# role mapping, and is always given a dark token, even where the colour would
# otherwise be kept as it is (readable text, mid fills, coloured washes).
COBALT_HUE = 223 / 360

def is_violet(rgb):
    if neutral(rgb): return False
    return 240 <= hls(rgb)[0] * 360 <= 300

def to_cobalt(rgb):
    h, l, s = hls(rgb)
    return tuple(c * 255 for c in colorsys.hls_to_rgb(COBALT_HUE, l, s))

FILL = (0x3d, 0x6b, 0xe0)             # --dk-brand-fill: white text on it is 4.8:1

def cobalt_role(fn, fill=False):
    def mapped(rgb):
        if not is_violet(rgb): return fn(rgb)
        c = to_cobalt(rgb)
        d = fn(c)
        if d: return d
        if fill:                          # a kept mid fill: no lighter than the brand fill,
            h, l, s = hls(c)              # so white text on it stays readable
            while lum(c) > lum(FILL) and l > 0.3:
                l -= 0.01; c = tuple(x * 255 for x in colorsys.hls_to_rgb(h, l, s))
        return to_hex(c)
    return mapped

ROLE_FN = {'t': cobalt_role(map_text), 'b': cobalt_role(map_bg, fill=True),
           'l': cobalt_role(map_line), 'a': cobalt_role(map_accent)}

# ── curated core palette (only for tokens declared on :root / html / body) ──
CORE = {
    'paper': '#0b0d12', 'paper-cool': '#10131a', 'paper-warm': '#171b24', 'paper-light': '#12151d',
    'surface': '#13161e', 'card': '#13161e',
    'ink': '#f2f4f8', 'ink-soft': '#e3e7ee', 'ink-muted': '#d1d6df', 'ink-faint': '#9ca3b4',
    'mute': '#b0b6c4', 'dim': '#9ca3b4', 'faint': '#7d8496', 'quote-ink': '#d1d6df',
    'rule': 'rgba(255,255,255,.10)', 'rule-strong': 'rgba(255,255,255,.16)', 'rule-bold': 'rgba(255,255,255,.24)',
    'line': 'rgba(255,255,255,.10)', 'line-soft': 'rgba(255,255,255,.06)',
    'brand': '#8aa8ff', 'brand-soft': 'rgba(61,107,224,.22)', 'lp-brand': '#8aa8ff',
    'frame': '#12151d', 'frame-surface': '#191d27', 'frame-elevated': '#212632',
    'frame-rule': 'rgba(255,255,255,.09)', 'frame-rule-strong': 'rgba(255,255,255,.18)',
    'frame-text': '#f5f7fb', 'frame-mute': '#a7aebd', 'frame-dim': '#7f8798',
    'signal-green': '#34d399', 'signal-green-bright': '#34d399', 'signal-red': '#f87171',
    'signal-red-bright': '#fb7185', 'signal-amber': '#fbbf24', 'signal-amber-bright': '#fbbf24',
    # signal-blue is teal in dark, so charts do not blur with the cobalt brand
    'signal-blue': '#2dd4bf', 'emerald': '#34d399', 'green': '#34d399', 'green-b': '#34d399',
    'red': '#f87171', 'amber': '#fbbf24', 'gold': '#fbbf24',
}
CORE_SEL = re.compile(r'^\s*(:root|html|body|html:root)(\s*,\s*(:root|html|body))*\s*$')

# ── token bookkeeping ─────────────────────────────────────────────────
tokens = {}                      # token name -> dark value
stats = collections.Counter()
KEPT = collections.Counter()

def tok_for(role, rgb, alpha):
    dark = ROLE_FN[role](rgb)
    if dark is None: return None
    key = to_hex(rgb)[1:]
    if alpha < 1 and neutral(rgb) and lum(rgb) < 0.2:
        key += '%02x' % round(alpha * 255)
        name = f'--dk-{role}-{key}'; tokens[name] = f'rgba(255,255,255,{alpha:.3f})'; return name
    if alpha < 1:
        key += '%02x' % round(alpha * 255)
        r, g, b = parse_hex(dark)[0]
        dark = f'rgba({r},{g},{b},{alpha:.2f})'
    name = f'--dk-{role}-{key}'
    tokens[name] = dark
    return name

HEX = re.compile(r'(?<![&\w])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b')
RGBF = re.compile(r'rgba?\(\s*(\d+)(\s*,\s*|\s+)(\d+)\s*(?:,\s*|\s+)(\d+)\s*(?:(,|/)\s*([\d.]+%?))?\s*\)')
KW = re.compile(r'(?<![\w-])(white|black)(?![\w-])')

def rewrite_value(val, role):
    """Rewrite every literal colour in a declaration value. role: t/b/l/a."""
    if 'var(--dk-' in val: return val
    # protect url(...) so ids like url(#abc123) are untouched
    urls = []
    def keep(m):
        urls.append(m.group(0)); return f'\x00{len(urls)-1}\x00'
    v = re.sub(r'url\([^)]*\)', keep, val)

    def hexsub(m):
        rgb, a = parse_hex(m.group(0))
        t = tok_for(role, rgb, a)
        if not t: stats['kept'] += 1; KEPT[(role, m.group(0).lower())] += 1; return m.group(0)
        stats['tok'] += 1
        return f'var({t}, {m.group(0)})'
    def rgbsub(m):
        rgb = (int(m.group(1)), int(m.group(3)), int(m.group(4)))
        a = m.group(6)
        alpha = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith('%') else float(a))
        if alpha < 1 and neutral(rgb) and lum(rgb) < 0.2 and role is not None:
            stats['overlay'] += 1
            full = m.group(0)
            o = full.index('(') + 1
            trip = re.match(r'\s*\d+(?:\s*,\s*|\s+)\d+(?:\s*,\s*|\s+)\d+', full[o:]).group(0)
            ov = '--dk-ovs' if ',' not in trip else '--dk-ov'
            return full[:o] + f'var({ov}, {trip.strip()})' + full[o + len(trip):]
        if alpha < 1 and not (role == 'b' and alpha >= 0.5 and lum(rgb) > 0.8) and not is_violet(rgb):
            stats['kept'] += 1; return m.group(0)       # coloured washes and white glints stay
        if alpha < 1:
            t = tok_for(role, rgb, alpha)
            if not t: return m.group(0)
            stats['wash'] += 1
            return f'var({t}, {m.group(0)})'
        t = tok_for(role, rgb, 1.0)
        if not t: stats['kept'] += 1; return m.group(0)
        stats['tok'] += 1
        return f'var({t}, {m.group(0)})'
    def kwsub(m):
        rgb = (255, 255, 255) if m.group(1) == 'white' else (0, 0, 0)
        t = tok_for(role, rgb, 1.0)
        if not t: return m.group(0)
        stats['tok'] += 1
        return f'var({t}, {m.group(1)})'
    v = HEX.sub(hexsub, v)
    v = RGBF.sub(rgbsub, v)
    v = KW.sub(kwsub, v)
    return re.sub(r'\x00(\d+)\x00', lambda m: urls[int(m.group(1))], v)

def role_for_prop(prop):
    p = prop.lower()
    if p.startswith('background'): return 'b'
    if p in ('color', 'caret-color', '-webkit-text-fill-color', 'accent-color') or p.startswith('text-decoration'):
        return 't'
    if p == 'fill': return 'b'      # CSS fill on shapes; text fills handled by selector check
    if p == 'stroke': return 'l'
    if p == 'stop-color': return 'b'
    if 'border' in p or p.startswith('outline') or p.startswith('column-rule') or p == '-webkit-text-stroke-color':
        return 'l'
    return None

def role_for_token(name):
    n = name.lower()
    if n in ('t', 'fg', 'tc', 'txt', 'col-t'): return 't'
    if re.search(r'(^|-)(ink|text|mute|dim|faint|fg|quote|onink)(-soft|-muted|-faint|\d)?$', n) and not re.search(r'card|bg|paper|rule|line', n):
        return 't'
    if re.search(r'rule|line|border|divider|hair|stroke', n): return 'l'
    if re.search(r'paper|surface|bg|card|soft|tint|wash|panel|fill', n): return 'b'
    if re.search(r'ink|text|mute|dim|faint|fg|label|quote', n): return 't'
    return 'a'

INK_BG = re.compile(r'background(-color)?\s*:\s*[^;]*var\(--(ink|ink-soft|vz-ink|sq-ink|wc-ink|ab-ink|text|bs-text)\b')
BRAND_BG = re.compile(r'background(-color)?\s*:\s*[^;]*var\(--(brand|vz-brand|lp-brand|ab-brand|sq-wu|wc-wu)\b')

def light_literal(val):
    m = HEX.search(val)
    if m:
        rgb, a = parse_hex(m.group(0)); return lum(rgb) > 0.6
    if KW.search(val): return 'white' in val
    m = RGBF.search(val)
    if m: return lum((int(m.group(1)), int(m.group(3)), int(m.group(4)))) > 0.6
    return False

CHIPS = {'ink': set(), 'brand': set()}
def chip_parent(sel):
    for part in sel.split(','):
        part = part.strip()
        for kind in ('ink', 'brand'):
            for c in CHIPS[kind]:
                if part.startswith(c + ' ') or part.startswith(c + '>') or part.startswith(c + ' >'):
                    return kind
    return None

def prescan(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    for m in re.finditer(r'([^{}]*)\{([^{}]*)\}', css):
        sel = m.group(1).split('}')[-1].split(';')[-1].strip(); body = m.group(2)
        if not sel or sel.startswith('@') or BAND.search(sel) or re.search(r'color\s*:\s*var\(--onink', body): continue
        kind = 'ink' if INK_BG.search(body) else 'brand' if BRAND_BG.search(body) else None
        if kind:
            for part in sel.split(','):
                part = part.strip()
                if part and ':' not in part: CHIPS[kind].add(part)

BAND = re.compile(r'footer|close-card|-band\b|merge-out|\.hub\b|-code\b|terminal')

PSEUDO = re.compile(r':(hover|focus|focus-visible|focus-within|active)\b')

def hover_kind(sel):
    """'ink' or 'brand' when sel is the hover/focus/active state of a chip
    whose background is the ink or brand colour (those chips turn light in
    dark mode, so a darker hover would hide their dark text)."""
    if not sel: return None
    for part in sel.split(','):
        part = part.strip()
        if not PSEUDO.search(part): continue
        base = PSEUDO.sub('', part).strip()
        for kind in ('ink', 'brand'):
            if base in CHIPS[kind]: return kind
    return None

def _dark_lit(lit):
    m = HEX.search(lit) or RGBF.search(lit) or KW.search(lit)
    if not m: return False
    if m.re is HEX: rgb = parse_hex(m.group(0))[0]
    elif m.re is RGBF: rgb = (int(m.group(1)), int(m.group(3)), int(m.group(4)))
    else: rgb = (0, 0, 0) if m.group(1) == 'black' else (255, 255, 255)
    return lum(rgb) < 0.12

def rewrite_hover(body, kind):
    """Point dark hover fills and borders of ink/brand chips at
    --dk-<kind>-hover, a lighter shade, instead of near-black."""
    tok = f'--dk-{kind}-hover'
    if tok in body: return body
    def decl(m):
        lead, prop, colon, val = m.group(1), m.group(2), m.group(3), m.group(4)
        if prop not in ('background', 'background-color', 'border-color'): return m.group(0)
        v, imp = split_imp(val)
        # an earlier run may already have wrapped the literal: unwrap it
        w = re.fullmatch(r'var\(--dk-[a-z]-[0-9a-f]+,\s*(.+)\)', v)
        lit = w.group(1) if w else v
        if 'var(' in lit or not _dark_lit(lit): return m.group(0)
        stats['hover-' + kind] += 1
        return f'{lead}{prop}{colon}var({tok}, {lit}){imp}'
    return re.sub(r'((?:^|;)\s*)([-a-z]+)(\s*:\s*)([^;]*)', decl, body)

def split_imp(val):
    m = re.match(r'(.*?)(\s*!\s*important\s*)?$', val.strip(), re.S)
    return m.group(1).strip(), (m.group(2) or '')

def rewrite_block(sel, body):
    """One declaration block. sel = selector text (may be '' for style attrs)."""
    on_ink = bool(INK_BG.search(body)); on_brand = bool(BRAND_BG.search(body))
    if 'var(--dk-band' in body: return body
    if on_ink and ((sel and BAND.search(sel)) or re.search(r'color\s*:\s*var\(--onink', body)):
        # a full-width dark band in light mode: stays dark, text untouched
        stats['band'] += 1
        def band(m):
            v, imp = split_imp(m.group(2))
            return m.group(1) + f'var(--dk-band, {v}){imp}'
        return re.sub(r'(background(?:-color)?\s*:\s*)([^;]*var\(--[a-z-]*ink[^;]*)', band, body)
    if on_brand and '--dk-brand-fill' not in body:
        def fill(m):
            v, imp = split_imp(m.group(3))
            stats['brand-fill'] += 1
            return f'{m.group(1)}{m.group(2)}var(--dk-brand-fill, {v}){imp}'
        # only a plain brand fill (var(--brand) or var(--brand, #hex)); tints such as
        # var(--brand-soft), gradients and var(--c, var(--brand)) keep their colour
        body = re.sub(r'((?:^|;)\s*)(background(?:-color)?\s*:\s*)(var\(--(?:brand|vz-brand|lp-brand|ab-brand|sq-wu|wc-wu)(?:\s*,\s*[^();]*)?\)\s*(?:!\s*important)?\s*)(?=;|$)', fill, body)
    hov = hover_kind(sel)
    if hov:
        body = rewrite_hover(body, hov)
    is_text_el = bool(re.search(r'(^|[\s>,])text\b|tspan', sel or '')) or bool(re.search(r'font-(size|family|weight)|text-anchor|(^|;)\s*font\s*:', body))
    core = bool(sel and CORE_SEL.match(sel))
    out = []
    for decl in re.split(r'(;)', body):
        m = re.match(r'((?:\s|\x01\d+\x01)*)([-a-zA-Z0-9_]+)(\s*:\s*)(.*)$', decl, re.S)
        if not m: out.append(decl); continue
        ws, prop, colon, val = m.groups()
        if prop.startswith('--'):
            name = prop[2:]
            if core and name in CORE and not val.strip().startswith('var('):
                tokens['--dk-' + name] = CORE[name]
                stats['core'] += 1
                v, imp = split_imp(val)
                out.append(f'{ws}{prop}{colon}var(--dk-{name}, {v}){imp}' + (val[len(val.rstrip()):] if val != val.rstrip() else ''))
                continue
            r = role_for_token(name)
            if r == 'b' and re.search(r'soft', name) and not re.search(r'paper|surface|bg|card|tint|wash|panel|fill', name):
                lit = HEX.search(val)
                if lit and lum(parse_hex(lit.group(0))[0]) < 0.15: r = 't'
            out.append(f'{ws}{prop}{colon}{rewrite_value(val, r)}'); continue
        role = role_for_prop(prop)
        if role is None: out.append(decl); continue
        if 'var(--dk-' in val: out.append(decl); continue
        if prop.lower() == 'color' and not (on_ink or on_brand) and sel and light_literal(val):
            parent = chip_parent(sel)
            if parent:
                stats['on-ink-child'] += 1
                v, imp = split_imp(val)
                out.append(f'{ws}{prop}{colon}var(--dk-on-{parent}, {v}){imp}'); continue
        if prop.lower() == 'color' and (on_ink or on_brand) and light_literal(val):
            t = '--dk-on-ink' if on_ink else '--dk-on-brand'
            stats['on-ink'] += 1
            v, imp = split_imp(val)
            out.append(f'{ws}{prop}{colon}var({t}, {v}){imp}'); continue
        if prop.lower() == 'fill' and is_text_el: role = 't'
        out.append(f'{ws}{prop}{colon}{rewrite_value(val, role)}')
    return ''.join(out)

def rewrite_css(css):
    # mask comments and strings
    keep = []
    def mask(m):
        keep.append(m.group(0)); return f'\x01{len(keep)-1}\x01'
    c = re.sub(r'/\*.*?\*/|"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'', mask, css, flags=re.S)
    def blk(m):
        sel = m.group(1).split('}')[-1].split(';')[-1].strip()
        sel = re.sub(r'\x01\d+\x01', '', sel).strip()
        return m.group(1) + '{' + rewrite_block(sel, m.group(2)) + '}'
    c = re.sub(r'([^{}]*)\{([^{}]*)\}', blk, c)
    return re.sub(r'\x01(\d+)\x01', lambda m: keep[int(m.group(1))], c)

SVG_TAG = re.compile(r'<(path|rect|circle|ellipse|line|polyline|polygon|text|tspan|g|stop|use)\b[^>]*>', re.S)
def rewrite_svg_attrs(html):
    def tag(m):
        t = m.group(0); name = m.group(1)
        if 'var(--dk-' in t: return t          # already done
        adds = []
        def attr(a):
            v = a.group(2)
            if not re.match(r'#|rgb|white$|black$', v): return a.group(0)
            if a.group(1) == 'fill': role = 't' if name in ('text', 'tspan') else 'b'
            elif a.group(1) == 'stroke': role = 'l'
            else: role = 'b'
            nv = rewrite_value(v, role)
            if nv == v: return a.group(0)
            adds.append(f'{a.group(1)}:{nv}')
            return a.group(0)          # keep attribute as the light value; style wins in dark
        t2 = re.sub(r'\s(fill|stroke|stop-color)="([^"]*)"', attr, t)
        if not adds: return t
        css = ';'.join(adds)
        if re.search(r'\sstyle="', t2):
            return re.sub(r'\sstyle="([^"]*)"', lambda s: f' style="{s.group(1).rstrip(";")};{css}"', t2, count=1)
        return re.sub(r'(/?>)$', f' style="{css}"\\1', t2)
    return SVG_TAG.sub(tag, html)

def rewrite_html(s):
    s = re.sub(r'(<style\b[^>]*>)(.*?)(</style>)', lambda m: m.group(1) + rewrite_css(m.group(2)) + m.group(3), s, flags=re.S)
    def sty(m):
        return m.group(1) + rewrite_block('', m.group(2)) + m.group(3)
    s = re.sub(r'(\sstyle=")([^"]*)(")', sty, s)
    s = rewrite_svg_attrs(s)
    return s

def targets():
    for p in sorted(glob.glob(ROOT + '/assets/*.css')):
        if os.path.basename(p) in ('dark-theme.css',): continue
        yield p
    for p in sorted(glob.glob(ROOT + '/**/*.html', recursive=True)):
        if '/reports/' in p or '/.git/' in p: continue
        s = open(p, encoding='utf-8').read()
        if 'http-equiv="refresh"' in s and len(s) < 3000: continue
        yield p

for p in targets():
    src = open(p, encoding='utf-8').read()
    for block in ([src] if p.endswith('.css') else re.findall(r'<style\b[^>]*>(.*?)</style>', src, re.S)):
        prescan(block)

changed = []
for p in targets():
    s = open(p, encoding='utf-8').read()
    n = rewrite_css(s) if p.endswith('.css') else rewrite_html(s)
    if n != s:
        changed.append(os.path.relpath(p, ROOT))
        if WRITE: open(p, 'w', encoding='utf-8').write(n)

# ── rebuild dark-theme.css from every --dk-* token the site references ──
FIXED = {'ink-hover': '#dbe3ff', 'brand-hover': '#a9c1ff', 'brand-fill': '#8aa8ff',
         'ov': '255, 255, 255', 'ovs': '255 255 255', 'on-ink': '#0b0d12',
         'on-brand': '#0b0d12', 'band': '#12151d'}   # light cobalt fills, dark text (8.5:1)
def value_for(name):
    if name in FIXED: return FIXED[name]
    if name in CORE: return CORE[name]
    m = re.fullmatch(r'([tbla])-([0-9a-f]{6})([0-9a-f]{2})?', name)
    if not m: return None
    rgb = parse_hex(m.group(2))[0]
    alpha = int(m.group(3), 16) / 255 if m.group(3) else 1.0
    if alpha < 1 and neutral(rgb) and lum(rgb) < 0.2: return f'rgba(255,255,255,{alpha:.3f})'
    d = ROLE_FN[m.group(1)](rgb)
    if d is None: return None
    if alpha < 1:
        r, g, b = parse_hex(d)[0]; return f'rgba({r},{g},{b},{alpha:.2f})'
    return d

used = set()
for p in targets():
    used |= set(re.findall(r'var\(--dk-([a-z0-9-]+)', open(p, encoding='utf-8').read()))
missing = sorted(n for n in used if value_for(n) is None)
fixed = [n for n in ('ov', 'ovs', 'on-ink', 'on-brand', 'band', 'ink-hover', 'brand-hover', 'brand-fill') if n in used or n in ('ov', 'ovs')]
core = sorted(n for n in used if n in CORE)
gen = sorted(n for n in used if n not in CORE and n not in FIXED and value_for(n))
HEADER = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dark_header.css')).read()
out = [HEADER, '@media screen and (not (prefers-color-scheme: light)) {', '  :root {', '    color-scheme: dark;']
out += [f'    --dk-{n}: {FIXED[n]};' for n in fixed]
out += ['', '    /* core palette, hand-picked */'] + [f'    --dk-{n}: {CORE[n]};' for n in core]
out += ['', '    /* derived: one per original colour and role */'] + [f'    --dk-{n}: {value_for(n)};' for n in gen]
out += ['  }', '']
EXTRA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dark_extra.css')
if os.path.exists(EXTRA): out.append(open(EXTRA).read().rstrip())
out += ['}', '']
if WRITE:
    open(os.path.join(ROOT, 'assets', 'dark-theme.css'), 'w').write('\n'.join(out))
print(dict(stats)); print('files', len(changed), 'tokens used', len(used), 'missing', missing[:10])
