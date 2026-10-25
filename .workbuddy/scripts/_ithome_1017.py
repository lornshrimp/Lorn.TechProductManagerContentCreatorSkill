# -*- coding: utf-8 -*-
import urllib.request, re, json, io, sys, os, gzip, ssl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ssl._create_default_https_context = ssl._create_unverified_context
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
def fetch(u,t=25):
    req=urllib.request.Request(u,headers={"User-Agent":UA,"Accept-Language":"zh-CN,zh;q=0.9"})
    with urllib.request.urlopen(req,timeout=t) as r:
        raw=r.read()
        if r.headers.get("Content-Encoding")=="gzip": raw=gzip.decompress(raw)
        for e in ("utf-8","gbk","gb18030"):
            try: return raw.decode(e)
            except Exception: continue
        return raw.decode("utf-8","ignore")
def clean(s):
    s=re.sub(r"<[^>]+>","",s)
    for a,b in [("&nbsp;"," "),("&amp;","&"),("&quot;",'"'),("&#39;","'")]: s=s.replace(a,b)
    return re.sub(r"\s+"," ",s).strip()
h=fetch("https://www.ithome.com/")
out=[]
for m in re.finditer(r'<a[^>]*href="(https://www\.ithome\.com/[^"]+\.htm)"[^>]*>(.*?)</a>',h):
    t=clean(m.group(2))
    if 8<=len(t)<=60 and t not in out: out.append(t)
if len(out)<20:
    h2=fetch("https://m.ithome.com/")
    for m in re.finditer(r'<a[^>]*href="[^"]*\.htm"[^>]*>(.*?)</a>',h2):
        t=clean(m.group(1))
        if 8<=len(t)<=60 and t not in out: out.append(t)
print(f"IT之家 命中 {len(out)} 条")
for i,t in enumerate(out[:30],1): print(f"{i}. {t}")
p=os.path.join(os.environ.get("TEMP","."),"ithome1017.json")
json.dump(out[:30],open(p,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("SAVED",p)
