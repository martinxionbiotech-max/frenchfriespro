#!/usr/bin/env python3
import re, html, json, urllib.request, urllib.parse, pathlib, concurrent.futures
from urllib.parse import urljoin,urlsplit,unquote
from pathlib import Path
BASE='https://frenchfriespro.com'
ROOT=Path(__file__).resolve().parents[1]
urls=[x.strip() for x in (ROOT/'raw/urls.txt').read_text().splitlines() if x.strip()]
known={urlsplit(u).path for u in urls}
def key(u):
 p=urlsplit(u).path.strip('/'); return 'home' if not p else p.replace('/','__')
def norm_href(raw,base):
 u=html.unescape(raw).strip()
 if not u or u.startswith(('#','mailto:','tel:','javascript:','data:')): return None
 p=urlsplit(urljoin(base,u))
 if p.netloc not in ('frenchfriespro.com','www.frenchfriespro.com'): return None
 path=p.path or '/'
 if path.startswith(('/wp-content/','/wp-includes/','/wp-json','/xmlrpc','/wp-login','/wp-admin','/feed','/comments/feed','/cdn-cgi')): return None
 return path
# discover missing paths from saved pages
missing=set()
for f in (ROOT/'raw/html').glob('*.html'):
 h=f.read_text(errors='ignore')
 for raw in re.findall(r'<a\b[^>]*\bhref=["\']([^"\']*)',h,re.I):
  p=norm_href(raw,BASE+'/')
  if p and p not in known: missing.add(p)
print('initial missing',len(missing),flush=True)
def fetch(path):
 url=BASE+urllib.parse.quote(path,safe='/%:@')
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; FrenchFries-static-export/1.0)'})
  with urllib.request.urlopen(req,timeout=45) as r:
   b=r.read(); return path,r.status,b,r.headers.get('content-type','')
 except Exception as e: return path,0,str(e).encode(),''
# loop up to 3 discovery rounds, cap 1200 URLs
for roundno in range(3):
 todo=sorted(p for p in missing if p not in known)
 print('round',roundno,'todo',len(todo),flush=True)
 if not todo: break
 found=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for i,(path,code,b,ct) in enumerate(ex.map(fetch,todo),1):
   if code==200 and b and 'text/html' in ct:
    dest=ROOT/'raw/html'/f'{key(BASE+path)}.html'; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(b)
    found.append(BASE+path); known.add(path)
    # discover links from the new page
    h=b.decode('utf-8','ignore')
    for raw in re.findall(r'<a\b[^>]*\bhref=["\']([^"\']*)',h,re.I):
     q=norm_href(raw,BASE+path)
     if q and q not in known: missing.add(q)
   else:
    print('not html/200',code,path,flush=True)
   if i%50==0: print('fetched',i,'/',len(todo),flush=True)
 urls += found
 (ROOT/'raw/urls.txt').write_text('\n'.join(dict.fromkeys(urls))+'\n')
 print('found',len(found),'missing now',len(missing-known),flush=True)
