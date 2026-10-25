# -*- coding: utf-8 -*-
"""解析微博热搜 HTML"""
import re, io, sys, os, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

p = os.path.join(os.environ.get("TEMP", "/tmp"), "bsk1008", "weibo.html")
h = open(p, encoding="utf-8", errors="ignore").read()
print("html len", len(h))

# 微博热搜表格：<td class="td-02"><a href="...">词条</a>...<td>热度</td>
rows = []
for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', h, re.S):
    row = m.group(1)
    a = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', row, re.S)
    if not a:
        continue
    txt = re.sub(r'<[^>]+>', '', a.group(2)).strip()
    if not txt or txt in ("热搜榜", "文娱榜", "要闻榜", "我的"):
        continue
    # 热度
    hv = ""
    hm = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
    for cell in hm:
        c = re.sub(r'<[^>]+>', '', cell).strip()
        if re.fullmatch(r'\d{5,}', c):
            hv = c
    rows.append((txt, hv))

seen = []
out = []
for t, hv in rows:
    if t not in [x[0] for x in out]:
        out.append((t, hv))

for i, (t, hv) in enumerate(out[:50], 1):
    print(f"{i}. {t}##{hv}")
print("N=", len(out))
json.dump({"微博热搜榜": [f"{t}##{hv}" for t, hv in out[:50]]},
          open(os.path.join(os.environ["TEMP"], "bsk1008", "weibo.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
