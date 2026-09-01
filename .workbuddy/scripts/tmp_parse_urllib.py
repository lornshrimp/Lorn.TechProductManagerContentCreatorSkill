# -*- coding: utf-8 -*-
import json, re, html, os

D = r"C:/Users/lorns/AppData/Local/Temp/urllib_20260829"

def rd(n):
    p = os.path.join(D, n)
    try:
        raw = open(p, "rb").read()
    except Exception as e:
        return "ERR %s" % e
    for enc in ("utf-8", "gbk", "gb18030"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", "ignore")

def strip(s):
    s = re.sub(r'(?is)<script.*?</script>', ' ', s)
    s = re.sub(r'(?is)<style.*?</style>', ' ', s)
    return s

# ---------- 百度热搜 API ----------
print("===== BAIDU =====")
try:
    j = json.loads(rd("baidu_hot.json"))
    out = []
    for card in j.get("data", {}).get("cards", []):
        for c in card.get("content", []):
            w = c.get("word") or c.get("query")
            if w:
                out.append((w, c.get("hotScore", ""), c.get("desc", "")[:60]))
    for i, (w, h, d) in enumerate(out[:40], 1):
        print("%d|%s|%s|%s" % (i, w, h, d))
    print("BAIDU_TOTAL", len(out))
except Exception as e:
    print("BAIDU_ERR", e)

# ---------- 通用：抽取标题 ----------
def titles(name, pattern, limit=30):
    s = strip(rd(name))
    print("\n===== %s (len=%d) =====" % (name, len(s)))
    seen = []
    for m in re.finditer(pattern, s, re.S):
        t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        t = html.unescape(t)
        t = re.sub(r'\s+', ' ', t)
        if 6 < len(t) < 90 and t not in seen:
            seen.append(t)
        if len(seen) >= limit:
            break
    for i, t in enumerate(seen, 1):
        print("%d|%s" % (i, t))
    print("TOTAL", len(seen))

titles("ithome.html", r'<h2[^>]*>(.*?)</h2>|<a[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</a>')
titles("163.html", r'<a[^>]*href="https?://news\.163\.com/[^"]*"[^>]*>(.*?)</a>')
titles("pingwest.html", r'<h[23][^>]*>(.*?)</h[23]>|<a[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</a>')
titles("infoq.html", r'<h[234][^>]*>(.*?)</h[234]>|<a[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</a>')

# 澎湃 Next.js
print("\n===== THEPAPER =====")
s = strip(rd("thepaper.html"))
m = re.search(r'__NEXT_DATA__[^>]*>(.*?)</script>', s, re.S)
if m:
    try:
        j = json.loads(m.group(1))
        def walk(o, acc):
            if isinstance(o, dict):
                if "name" in o and isinstance(o.get("name"), str) and len(o["name"]) > 5:
                    acc.append(o["name"])
                for v in o.values():
                    walk(v, acc)
            elif isinstance(o, list):
                for v in o:
                    walk(v, acc)
        acc = []
        walk(j.get("props", {}), acc)
        seen = []
        for t in acc:
            if t not in seen:
                seen.append(t)
        for i, t in enumerate(seen[:40], 1):
            print("%d|%s" % (i, t))
        print("TOTAL", len(seen))
    except Exception as e:
        print("PARSE_ERR", e)
        print(s[:600])
else:
    # fallback
    seen = []
    for mm in re.finditer(r'<h[23][^>]*>(.*?)</h[23]>|<a[^>]*href="/newsDetail[^"]*"[^>]*>(.*?)</a>', s, re.S):
        t = re.sub(r'<[^>]+>', '', mm.group(0)).strip()
        t = html.unescape(re.sub(r'\s+', ' ', t))
        if 6 < len(t) < 90 and t not in seen:
            seen.append(t)
    for i, t in enumerate(seen[:40], 1):
        print("%d|%s" % (i, t))
    print("FB_TOTAL", len(seen))
