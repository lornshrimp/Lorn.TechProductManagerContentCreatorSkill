# -*- coding: utf-8 -*-
import re, html, io, sys, json

p = r"C:/Users/lorns/AppData/Local/Temp/weibo_hot.html"
raw = open(p, "rb").read()
for enc in ("utf-8", "gbk", "gb18030"):
    try:
        s = raw.decode(enc)
        break
    except Exception:
        continue
else:
    s = raw.decode("utf-8", "ignore")

print("LEN", len(s))

# 微博热搜结构: <td class="td-02"><a href="/weibo?q=%23...%23" ...>标题</a><span>热度</span>
items = []
# 尝试解析 table 行
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', s, re.S)
print("ROWS", len(rows))
for r in rows:
    m_a = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r, re.S)
    if not m_a:
        continue
    title = re.sub(r'<[^>]+>', '', m_a.group(2)).strip()
    title = html.unescape(title)
    m_span = re.search(r'<span[^>]*>(.*?)</span>', r, re.S)
    heat = re.sub(r'<[^>]+>', '', m_span.group(1)).strip() if m_span else ""
    if title:
        items.append((title, heat))

if not items:
    # 备用: 直接抓 #话题# 链接
    for m in re.finditer(r'href="/weibo\?q=([^"&]+)[^"]*"[^>]*>([^<]*)<', s):
        t = html.unescape(m.group(2)).strip()
        if t and not any(t == x[0] for x in items):
            items.append((t, ""))
        if len(items) >= 50:
            break

for i, (t, h) in enumerate(items[:52], 1):
    print("%d|%s|%s" % (i, t, h))
print("TOTAL", len(items))
