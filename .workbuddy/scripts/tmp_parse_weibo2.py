import re, sys, io
html = open(r"C:\Users\lorns\AppData\Local\Temp\weibo_20260909.html", encoding='utf-8', errors='ignore').read()
# 词条: <a href="//s.weibo.com/weibo?q=..." ...>词条</a>
items = []
for m in re.finditer(r'<a href="([^"]*weibo[^"]*)"[^>]*>(.*?)</a>', html, re.S):
    href, txt = m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()
    if txt and len(txt) < 40 and ('weibo.com/weibo' in href or 'weibo.com/wb' in href) and txt not in [x[0] for x in items]:
        items.append((txt, href))
# 去重保序，去掉明显导航
seen=set(); out=[]
for t,h in items:
    if t in seen: continue
    seen.add(t)
    out.append((t,h))
    if len(out)>=50: break
print(len(out))
for i,(t,h) in enumerate(out[:50],1):
    print(f"{i}\t{t}")
