import re, os, sys
p = os.path.join(os.environ.get('TEMP','/tmp'), 'weibo_today.html')
html = open(p, encoding='utf-8', errors='ignore').read()
# 提取热搜条目：<td class="td-02"> ... <a ...>词条</a> ... <span>热度</span>
rows = re.findall(r'<td class="td-02">(.*?)</td>', html, re.S)
out = []
for i, r in enumerate(rows, 1):
    m = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r, re.S)
    if not m: continue
    title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    href = m.group(1)
    if not title or len(title) < 2: continue
    hm = re.search(r'<span[^>]*>([^<]*)</span>', r)
    hot = hm.group(1).strip() if hm else ''
    out.append(f"{i}##{title}##{hot}")
print(f"COUNT={len(out)}")
print('\n'.join(out[:60]))
