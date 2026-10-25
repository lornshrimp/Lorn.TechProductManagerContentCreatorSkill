# -*- coding: utf-8 -*-
import re, io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
p = os.path.join(os.environ["TEMP"], "bsk1020", "weibo.html")
h = open(p, encoding="utf-8", errors="ignore").read()
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', h, re.S)
out=[]
for r in rows:
    m = re.search(r'<td[^>]*class="td-02"[^>]*>(.*?)</td>', r, re.S)
    if not m: continue
    seg = m.group(1)
    a = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', seg, re.S)
    if not a: continue
    t = re.sub(r"<[^>]+>", "", a.group(2)).strip()
    href = a.group(1)
    if not t or t in ("查看更多>","热搜榜"): continue
    hv = re.search(r'<span[^>]*>(\d+)</span>', seg)
    if t not in [x[0] for x in out]:
        out.append((t, hv.group(1) if hv else "", href))
print(f"### 微博热搜榜 ({len(out)})")
for i,(t,hv,href) in enumerate(out[:50],1):
    print(f"{i}. {t}##{hv}")
json.dump(out[:50], open(os.path.join(os.environ["TEMP"],"weibo1020.json"),"w",encoding="utf-8"), ensure_ascii=False)
