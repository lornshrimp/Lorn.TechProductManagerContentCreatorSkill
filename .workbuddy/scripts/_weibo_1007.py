# -*- coding: utf-8 -*-
"""解析微博热搜 HTML"""
import re, io, sys, os, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
p = os.path.join(os.environ['TEMP'], 'bsk1007', 'weibo.html')
h = open(p, encoding='utf-8', errors='replace').read()

# 微博热搜页：词条在 <a href=".../weibo?q=..."> 或 data 属性中
out = []
seen = set()
# 优先匹配 SWeibo / 热搜词条
for m in re.finditer(r'<a[^>]*href="[^"]*weibo\.com/weibo\?q=([^"&]+)[^"]*"[^>]*>(.*?)</a>', h):
    txt = re.sub(r'<[^>]+>', '', m.group(2))
    txt = re.sub(r'\s+', ' ', txt).strip()
    if txt and 2 <= len(txt) <= 40 and txt not in seen:
        seen.add(txt)
        out.append(txt)

if len(out) < 10:
    for m in re.finditer(r'"word"\s*:\s*"(.*?)"', h):
        t = m.group(1)
        if t and t not in seen and 2 <= len(t) <= 40:
            seen.add(t)
            out.append(t)

# 带热度值版本
hot = []
for m in re.finditer(r'<td[^>]*class="td-02"[^>]*>\s*<a[^>]*>(.*?)</a>', h):
    t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    if t:
        hot.append(t)

print("=== 词条(含q=链接) ===")
for i, t in enumerate(out[:60], 1):
    print(f'{i}. {t}')
print(f'N={len(out)}')
print("\n=== td-02 词条 ===")
for i, t in enumerate(hot[:60], 1):
    print(f'{i}. {t}')
print(f'N_hot={len(hot)}')

json.dump({'q': out[:60], 'td': hot[:60]},
          open(os.path.join(os.environ['TEMP'], 'bsk1007', 'weibo_parsed.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
