# -*- coding: utf-8 -*-
import urllib.request, re, io, sys, ssl, gzip, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ssl._create_default_https_context = ssl._create_unverified_context
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
HDR={"User-Agent":UA,"Accept-Language":"zh-CN,zh;q=0.9"}
def fetch(u):
    req=urllib.request.Request(u,headers=HDR)
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=r.read()
        if r.headers.get("Content-Encoding")=="gzip": raw=gzip.decompress(raw)
        for e in ("utf-8","gbk","gb18030"):
            try: return raw.decode(e)
            except Exception: continue
        return raw.decode("utf-8","ignore")
def clean(s):
    s=re.sub(r"<[^>]+>","",s)
    s=s.replace("&nbsp;"," ").replace("&amp;","&").replace("&quot;",'"')
    return re.sub(r"\s+"," ",s).strip()
out=[]
for url in ["https://www.ithome.com/","https://it.ithome.com/","https://www.ithome.com/0/"]:
    try: h=fetch(url)
    except Exception as e:
        print(f"[{url}] FAIL {e}"); continue
    cand=[]
    for m in re.finditer(r'<a[^>]*href="(?:https?:)?//www\.ithome\.com/0/\d+/\d+\.htm"[^>]*>(.*?)</a>', h):
        t=clean(m.group(1))
        if 8<=len(t)<=70: cand.append(t)
    print(f"[{url}] html={len(h)} cand={len(cand)}")
    for t in cand:
        if t not in out: out.append(t)
out=out[:30]
print(f"\n### IT之家热榜 ({len(out)})")
for i,t in enumerate(out,1): print(f"{i}. {t}")
json.dump(out, open(os.path.join(os.environ["TEMP"],"ithome1020.json"),"w",encoding="utf-8"), ensure_ascii=False)
