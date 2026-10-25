import re
html = open(r"C:\Users\lorns\AppData\Local\Temp\weibo_20260909.html", encoding='utf-8', errors='ignore').read()
rows = re.findall(r'<td class="td-01[^"]*">\s*(\d+)\s*</td>\s*<td class="td-02">\s*<a href="(/weibo\?q=[^"]+)"[^>]*>(.*?)</a>\s*(?:<span>\s*([\d万+]*)\s*</span>)?', html, re.S)
seen=set(); out=[]
for rank,href,title,hot in rows:
    t=re.sub(r'<[^>]+>','',title).strip()
    if not t or t in seen: continue
    seen.add(t); out.append((rank,t,hot))
print(len(out))
for r,t,h in out[:50]:
    print(f"{r}\t{t}\t{h}")
