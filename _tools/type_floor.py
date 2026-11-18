"""Raise the smallest text on whyuser.com (Nov 2026).

Light text on a dark page reads thinner than dark text on white, so the
smallest sizes suffer most in dark mode. This raises the floor only; body
text (16px) and headings are untouched.

    under 12px            -> 12px   (mono labels)  / 12.5px (other text)
    12.5px - 13.5px       -> 14px for notes, captions and card text only
    14px / 15px paragraph -> 15px / 16px (selectors ending in p, li, dd,
                             blockquote, figcaption, or a -p/-desc/-lead/
                             -body/-copy/-note/-cap/-text class)

Skips: icons, arrows and bullets; whyuser-viz.css (chart parts); SVG/chart text (selectors with text, tspan, svg, axis, tick, label
inside a chart), reports/ and benchmarks/ (built by their own tools), and
clamp()/calc()/em values.

RUN ONCE. A second run would bump some sizes again (13 -> 14 -> 15), so the
script writes a marker into assets/whyuser-type-fix.css and refuses to run
when it finds it. New CSS should simply use 12px as its smallest size.

    python3 _tools/type_floor.py .           # dry run
    python3 _tools/type_floor.py . --write
"""
import re, sys, glob, os, collections
ROOT = sys.argv[1]; WRITE = '--write' in sys.argv
MARK = '/* type_floor.py applied (Nov 2026). Do not run it again. Smallest text size: 12px. */'
MARK_FILE = os.path.join(ROOT, 'assets', 'whyuser-type-fix.css')
if MARK in open(MARK_FILE, encoding='utf-8').read():
    sys.exit('type_floor.py has already been applied; see the marker in assets/whyuser-type-fix.css')
SKIP_SEL = re.compile(r'(^|[\s>,.#-])(text|tspan|svg|axis|tick|g)\b|-svg|chart|graph|spark|og-|share-img|print', re.I)
# icons, arrows, bullets and counters: sized to their box, not read as text
ICON = re.compile(r'(\s|>)i(:[\w()-]+)*$|::?(before|after|marker)$|-(ic|ico|icon|caret|arrow|dot|pip|pips)$|\bfa-', re.I)
PARA = re.compile(r'(^|[\s>])(p|li|dd|blockquote|figcaption)$|-(p|desc|lead|body|copy|note|notes|cap|caption|text|t|sub|src|n|q)$', re.I)
NOTE = re.compile(r'note|cap|caption|src|source|foot|small|meta|sub|desc|figcaption|cite|dd$|(^|[\s>])p$|-p$|-t$|-n$', re.I)
stats = collections.Counter(); samples = collections.defaultdict(list)

def px(v):
    m = re.fullmatch(r'\s*([\d.]+)(px|rem)\s*', v)
    if not m: return None
    n = float(m.group(1)); return n * 16 if m.group(2) == 'rem' else n

def fmt(n, unit):
    return (f'{n/16:.4f}'.rstrip('0').rstrip('.') + 'rem') if unit == 'rem' else (f'{n:g}px')

def new_size(n, sel, mono):
    last = sel.split(',')[-1].strip() if sel else ''
    if n < 12:  return 12 if mono else 12.5
    if n < 12.5: return n
    if n < 14:  return 14 if (NOTE.search(last) and not mono) else n
    if sel and PARA.search(last) and not mono:
        if n == 14: return 15
        if n == 15: return 16
    return n

def fix_block(sel, body, where):
    if sel and SKIP_SEL.search(sel): return body
    if sel and all(ICON.search(part.strip()) for part in sel.split(',')): return body
    mono = bool(re.search(r'Geist Mono|monospace|--font-mono|--mono', body))
    def decl(m):
        lead, val, imp = m.group(1), m.group(2), m.group(3) or ''
        n = px(val)
        if n is None: return m.group(0)
        unit = 'rem' if 'rem' in val else 'px'
        nn = new_size(n, sel, mono)
        if nn == n: return m.group(0)
        stats[f'{n:g}->{nn:g}'] += 1
        if len(samples[f'{n:g}->{nn:g}']) < 6: samples[f'{n:g}->{nn:g}'].append(f'{where}: {(sel or "style=")[:60]}')
        return f'{lead}{fmt(nn, unit)}{imp}'
    return re.sub(r'((?:^|[;{\s])font-size\s*:\s*)([^;!}]+?)(\s*!important)?(?=\s*(;|$|}))', decl, body)

def fix_css(css, where):
    keep = []
    def mask(m): keep.append(m.group(0)); return f'\x01{len(keep)-1}\x01'
    c = re.sub(r'/\*.*?\*/', mask, css, flags=re.S)
    def blk(m):
        sel = re.sub(r'\x01\d+\x01', '', m.group(1).split('}')[-1].split(';')[-1]).strip()
        if sel.startswith('@'): return m.group(0)
        return m.group(1) + '{' + fix_block(sel, m.group(2), where) + '}'
    c = re.sub(r'([^{}]*)\{([^{}]*)\}', blk, c)
    return re.sub(r'\x01(\d+)\x01', lambda m: keep[int(m.group(1))], c)

def fix_html(s, where):
    s = re.sub(r'(<style\b[^>]*>)(.*?)(</style>)', lambda m: m.group(1) + fix_css(m.group(2), where) + m.group(3), s, flags=re.S)
    # inline styles: floor only, never on SVG elements
    def sty(m):
        if re.match(r'<(svg|text|tspan|g|rect|path|circle|line)\b', m.group(1)): return m.group(0)
        return m.group(1) + m.group(2) + fix_block('', m.group(3), where) + m.group(4)
    return re.sub(r'(<[a-zA-Z][^>]*?)(\sstyle=")([^"]*)(")', sty, s)

files = [p for p in sorted(glob.glob(ROOT + '/assets/*.css')) if not re.search(r'(dark-theme|whyuser-viz)\.css$', p)]
files += [p for p in sorted(glob.glob(ROOT + '/**/*.html', recursive=True))
          if not re.search(r'/(reports|benchmarks|\.git)/', p)]
changed = []
for p in files:
    s = open(p, encoding='utf-8').read()
    w = os.path.relpath(p, ROOT)
    n = fix_css(s, w) if p.endswith('.css') else fix_html(s, w)
    if n != s:
        changed.append(w)
        if WRITE: open(p, 'w', encoding='utf-8').write(n)
for k in sorted(stats, key=lambda k: float(k.split('->')[0])):
    print(f'{k:>12}  x{stats[k]}'); [print('      ', x) for x in samples[k][:3]]
if WRITE and changed:
    with open(MARK_FILE, 'a', encoding='utf-8') as f: f.write('\n' + MARK + '\n')
print('files', len(changed))
