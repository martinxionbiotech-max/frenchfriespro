#!/usr/bin/env python3
"""Normalized content + link audit for the static export."""
import re, json, html, collections
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
PUBLIC=ROOT/'public'
SITE='https://frenchfriespro.com'
MAN=json.loads((ROOT/'src/data/pages.json').read_text())
pages={}
for x in MAN:
    p=unquote(x['path']); key=p.rstrip('/') or '/'
    pages[key]={**x,'key':key}
route_keys=set(pages)
def is_file(path):
    p=unquote(path)
    for root in (DIST, PUBLIC):
        q=root/p.lstrip('/')
        if q.is_file() or (q/'index.html').is_file():
            return True
    return False
def route_file(path):
    for root in (DIST, PUBLIC):
        q=root/path.lstrip('/')
        if (q/'index.html').is_file():
            return True
    return False

def norm(u, base):
    p=urlsplit(urljoin(base,u)); path=unquote(p.path or '/')
    return p, (path.rstrip('/') or '/')
def txt(h):
    h=re.sub(r'<script\b[\s\S]*?</script>|<style\b[\s\S]*?</style>',' ',h,flags=re.I)
    h=re.sub(r'<[^>]+>',' ',h)
    return re.sub(r'\s+',' ',html.unescape(h)).strip()
def word_count(h):
    t=txt(h); cjk=len(re.findall(r'[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7af]',t)); words=len(re.findall(r"[^\W\d_]+",t,re.UNICODE))
    return len(t),words,cjk
rows=[]; anchors=[]; asset_refs=[]; css_refs=[]; canon=[]; alts=[]; externals=collections.Counter()
for f in DIST.rglob('index.html'):
    rel='/'+str(f.relative_to(DIST)).replace('index.html','')
    key=unquote(rel).rstrip('/') or '/'
    if key not in route_keys:
        continue
    h=f.read_text(errors='ignore')
    base=SITE+rel
    title=html.unescape(re.search(r'<title[^>]*>([\s\S]*?)</title>',h,re.I).group(1)).strip() if re.search(r'<title[^>]*>',h,re.I) else ''
    m=re.search(r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)',h,re.I) or re.search(r'<meta\b[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',h,re.I)
    desc=html.unescape(m.group(1)).strip() if m else ''
    lang=(re.search(r'<html\b[^>]*lang=["\']([^"\']*)',h,re.I) or [None,''])[1] if re.search(r'<html\b[^>]*lang=["\']([^"\']*)',h,re.I) else ''
    h1s=re.findall(r'<h1\b[^>]*>([\s\S]*?)</h1>',h,re.I)
    ld=len(re.findall(r'<script\b[^>]*application/ld\+json[^>]*>',h,re.I))
    forms=len(re.findall(r'<form\b',h,re.I))
    length,words,cjk=word_count(h)
    m=re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)',h,re.I)
    if not m: m=re.search(r'<link\b[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']',h,re.I)
    canonical=html.unescape(m.group(1)).strip() if m else ''
    if canonical:
        cp,ck=norm(canonical,base); canon.append((key,canonical,cp.netloc,ck,ck in route_keys or route_file(ck)))
    for hm in re.finditer(r'<link\b[^>]*rel=["\']alternate["\'][^>]*>',h,re.I):
        tag=hm.group(0); lm=re.search(r'hreflang=["\']([^"\']+)',tag,re.I); gm=re.search(r'href=["\']([^"\']+)',tag,re.I)
        if lm and gm:
            p,hk=norm(html.unescape(gm.group(1)),base); alts.append((key,lm.group(1),hk,hk in route_keys or route_file(hk)))
    for am in re.finditer(r'<a\b[^>]*\bhref=["\']([^"\']*)["\']',h,re.I):
        raw=html.unescape(am.group(1)).strip()
        if not raw or raw.startswith(('#','mailto:','tel:','javascript:','data:')): continue
        p,k=norm(raw,base)
        if p.netloc not in ('frenchfriespro.com','www.frenchfriespro.com'):
            externals[p.netloc]+=1; continue
        if k in route_keys or route_file(k):
            anchors.append((key,raw,k,True)); continue
        if k.startswith(('/wp-content/','/wp-includes/')) or is_file(k):
            asset_refs.append((key,raw,k,is_file(k))); continue
        anchors.append((key,raw,k,False))
    for sm in re.finditer(r'\b(?:src|data-src|data-lazy-src)=["\']([^"\']+)',h,re.I):
        raw=html.unescape(sm.group(1)).strip()
        if not raw or raw.startswith(('data:','blob:','#')): continue
        p,k=norm(raw,base)
        if p.netloc in ('frenchfriespro.com','www.frenchfriespro.com'):
            asset_refs.append((key,raw,k,is_file(k)))
    for sm in re.finditer(r'\bsrcset=["\']([^"\']+)',h,re.I):
        for part in re.split(r',\s*',html.unescape(sm.group(1))):
            raw=part.strip().split()[0] if part.strip() else ''
            if not raw or raw.startswith(('data:','blob:')): continue
            p,k=norm(raw,base)
            if p.netloc in ('frenchfriespro.com','www.frenchfriespro.com'):
                asset_refs.append((key,raw,k,is_file(k)))
    rows.append(dict(key=key,filename=f.name,title=title,desc=desc,lang=lang,h1=len(h1s),ld=ld,forms=forms,length=length,words=words,cjk=cjk,canonical=canonical,alts=len([a for a in alts if a[0]==key])))
# css refs
for css in PUBLIC.rglob('*.css'):
    h=css.read_text(errors='ignore')
    for m in re.finditer(r'url\(\s*["\']?([^"\')]+)',h,re.I):
        raw=m.group(1).strip()
        if not raw or raw.startswith(('data:','blob:','#')): continue
        p=urlsplit(raw)
        if p.scheme or p.netloc: continue
        path=unquote(p.path)
        target=(PUBLIC/path.lstrip('/')) if path.startswith('/') else (css.parent/path)
        css_refs.append((str(css.relative_to(PUBLIC)),raw,target.resolve().is_file()))
# graph
edges=collections.defaultdict(set)
for src,raw,k,ok in anchors:
    if ok: edges[src].add(k)
reach={'/'}; frontier=['/']
while frontier:
    nxt=[]
    for n in frontier:
        for t in edges.get(n,()):
            if t not in reach: reach.add(t); nxt.append(t)
    frontier=nxt
allkeys={r['key'] for r in rows}
# content metrics by lang
def stats(vals):
    if not vals: return {}
    vals=sorted(vals); return {'n':len(vals),'min':vals[0],'median':vals[len(vals)//2],'max':vals[-1],'avg':round(sum(vals)/len(vals),1)}
by_lang=collections.defaultdict(list)
for r in rows: by_lang[r['lang']].append(r)
out={
 'pages':len(rows),
 'routes':len(allkeys),
 'title_gt60':sum(1 for r in rows if len(r['title'])>60),
 'title_empty':sum(1 for r in rows if not r['title']),
 'desc_empty':sum(1 for r in rows if not r['desc']),
 'desc_out_140_160':sum(1 for r in rows if r['desc'] and not (140<=len(r['desc'])<=160)),
 'desc_gt160':sum(1 for r in rows if len(r['desc'])>160),
 'h1_not_1':sum(1 for r in rows if r['h1']!=1),
 'h1_zero':sum(1 for r in rows if r['h1']==0),
 'jsonld_zero':sum(1 for r in rows if r['ld']==0),
 'forms':sum(r['forms'] for r in rows),
 'forms_pages':sum(1 for r in rows if r['forms']),
 'canonical':len(canon),
 'canonical_bad_target':sum(1 for x in canon if not x[4]),
 'canonical_non_source_host':sum(1 for x in canon if x[2] not in ('frenchfriespro.com','www.frenchfriespro.com')),
 'hreflang':len(alts),
 'hreflang_bad_target':sum(1 for x in alts if not x[3]),
 'anchors':len(anchors),
 'anchors_bad':sum(1 for x in anchors if not x[3]),
 'assets':len(asset_refs),
 'assets_bad':sum(1 for x in asset_refs if not x[3]),
 'css_refs':len(css_refs),
 'css_bad':sum(1 for x in css_refs if not x[2]),
 'external_links':sum(externals.values()),
 'external_domains':len(externals),
 'external_top':externals.most_common(15),
 'orphans':len(allkeys-reach),
 'unreachable':len(allkeys-reach),
 'click_depth':{d:sum(1 for k in reach if k in edges) if False else 0 for d in []},
 'by_lang':{l:{'pages':len(v),'length_median':stats([x['length'] for x in v]).get('median'),'words_median':stats([x['words'] for x in v]).get('median'),'cjk_median':stats([x['cjk'] for x in v]).get('median'),'forms':sum(x['forms'] for x in v),'title_gt60':sum(1 for x in v if len(x['title'])>60),'desc_empty':sum(1 for x in v if not x['desc'])} for l,v in sorted(by_lang.items())},
 'title_dups':[(t,c) for t,c in collections.Counter(r['title'] for r in rows if r['title']).items() if c>1][:20],
 'desc_dups':[(d,c) for d,c in collections.Counter(r['desc'] for r in rows if r['desc']).items() if c>1][:20],
 'canonical_mismatch':[(r['key'],r['canonical']) for r in rows if r['canonical'] and unquote(urlsplit(r['canonical']).path).rstrip('/') not in ('',r['key'])][:20],
 'bad_samples':[(a,b) for a,b,_,ok in anchors if not ok][:15],
 'asset_bad_samples':[(a,b) for a,b,_,ok in asset_refs if not ok][:15],
}
print(json.dumps(out,ensure_ascii=False,indent=2))
(ROOT/'docs').mkdir(exist_ok=True)
(ROOT/'docs/audit-2026-11-full.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
