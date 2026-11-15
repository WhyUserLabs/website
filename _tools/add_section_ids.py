"""Give every <section> on the site an id, so any section can be linked.

The id comes from the section's first heading (e.g. "Six jobs teams bring"
becomes #six-jobs-teams-bring). Sections that already have an id, or are
labelled by a heading that has one, are left alone. Existing ids never change.
Pages with no <section> get ids on their <h2>s instead.

    python3 _tools/add_section_ids.py .            # dry run: lists new ids
    python3 _tools/add_section_ids.py . --write    # add them

Links into closed tabs and <details> are opened by assets/whyuser-anchors.js.
"""
import re,sys,glob,os,html,json
root=sys.argv[1]; write='--write' in sys.argv
STOP={'a','an','the','and','or','of','to','in','on','for','with','your','you','is','are','it','its','we','our','by','at','be','that','this','what','how'}
def slug(t,maxw=5):
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)).strip()
    t=re.sub(r'^(section\s+)?\d+(\.\d+)*\.?\s+','',t,flags=re.I)
    t=re.split(r'[.?!:;—–]|\s-\s',t.strip())[0] if t.strip() else ''
    words=re.findall(r'[a-z0-9]+',t.lower().replace("’","").replace("'",""))
    # drop stopwords at the ends only
    while words and words[0] in ('a','an','the'): words.pop(0)
    words=words[:maxw]
    while words and words[-1] in STOP: words.pop()
    return '-'.join(words)
def pages():
    for p in sorted(glob.glob(root+'/**/*.html',recursive=True)):
        if '/.git/' in p: continue
        s=open(p,encoding='utf-8').read()
        if 'http-equiv="refresh"' in s and len(s)<3000: continue
        yield p,s
report={}
OVR={('one-page-two-answers.html','section'):'same-question-twice',('404.html','happy-looked-everywhere'):'not-found',('pricing.html','proofstrip'):'annual-plans',('focus-group-alternatives.html','pick'):'pick-by-need'}
LEGAL={'beta-agreement.html','dpa.html','privacy.html','security.html','terms.html'}
for p,s in pages():
    rel=os.path.relpath(p,root)
    ids=set(re.findall(r'\bid="([^"]+)"',s))
    secs=list(re.finditer(r'<section\b[^>]*>',s,re.S))
    edits=[]
    targets=[]
    if secs:
        for i,m in enumerate(secs):
            if re.search(r'\sid=',m.group(0)): continue
            lb=re.search(r'aria-labelledby="([^"]+)"',m.group(0))
            if lb and lb.group(1) in ids: continue
            cls=re.search(r'class="([^"]*)"',m.group(0)); cls=cls.group(1) if cls else ''
            fixed=None
            if re.search(r'\b(cta-section|wu-close|page-cta)\b',cls): fixed='access'
            elif rel.endswith('roi.html') and 'sec' in cls.split(): fixed='calculator'
            elif rel in LEGAL and i==1: fixed='full-text'
            elif 'trust-band' in cls: fixed='customers'
            if fixed:
                targets.append((m,fixed,'section')); continue
            end=secs[i+1].start() if i+1<len(secs) else len(s)
            body=s[m.end():end]
            h=re.search(r'<h([1-4])\b[^>]*>(.*?)</h\1>',body,re.S)
            sl=slug(h.group(2)) if h else ''
            if not sl:
                lab=re.search(r'aria-label="([^"]+)"',m.group(0))
                sl=slug(lab.group(1)) if lab else ''
            if not sl:
                cls=re.search(r'class="([^"]+)"',m.group(0))
                sl=re.sub(r'[^a-z0-9-]','',cls.group(1).split()[0]) if cls else ''
                sl=re.sub(r'^(bs|wu|v3)-','',sl)
            if not sl or len(sl)<3: sl='section'
            targets.append((m,sl,'section'))
    else:
        for m in re.finditer(r'<h2\b[^>]*>(.*?)</h2>',s,re.S):
            tag=s[m.start():s.find('>',m.start())+1]
            if ' id=' in tag: continue
            targets.append((m,slug(m.group(1)) or 'section','h2'))
    out=[]
    for m,sl,kind in targets:
        sl=OVR.get((rel,sl),sl)
        base=sl;n=2
        while sl in ids: sl=f'{base}-{n}'; n+=1
        ids.add(sl); out.append((m.start(),kind,sl))
    if out:
        report[rel]=[x[2] for x in out]
        if write:
            # insert id right after '<section' / '<h2'
            for pos,kind,sl in sorted(out,reverse=True):
                tl=len('<'+kind)
                s=s[:pos+tl]+f' id="{sl}"'+s[pos+tl:]
            open(p,'w',encoding='utf-8').write(s)
for k,v in report.items(): print(k,'→',', '.join(v))
print('TOTAL',sum(len(v) for v in report.values()))
