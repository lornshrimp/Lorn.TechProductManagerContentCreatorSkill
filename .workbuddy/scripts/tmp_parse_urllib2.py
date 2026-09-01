# -*- coding: utf-8 -*-
import json, re, html, os

D = r"C:/Users/lorns/AppData/Local/Temp/urllib_20260829"

def rd(n):
    raw = open(os.path.join(D, n), "rb").read()
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

def clean(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()

# ---------- 百度 ----------
print("===== BAIDU_RAW =====")
try:
    j = json.loads(rd("baidu_hot.json"))
    print(json.dumps(j, ensure_ascii=False)[:1200])
except Exception as e:
    print("ERR", e)

# ---------- 通用抓取 ----------
def grab(name, limit=30, minlen=6):
    s = strip(rd(name))
    print("\n===== %s (len=%d) =====" % (name, len(s)))
    seen = []
    pats = [
        r'<h1[^>]*>(.*?)</h1>', r'<h2[^>]*>(.*?)</h2>', r'<h3[^>]*>(.*?)</h3>',
        r'<a[^>]*title="([^"]{8,80})"',
        r'<a[^>]*>([^<]{8,80})</a>',
    ]
    for p in pats:
        for m in re.finditer(p, s, re.S):
            t = clean(m.group(1))
            if minlen < len(t) < 90 and t not in seen:
                seen.append(t)
    for i, t in enumerate(seen[:limit], 1):
        print("%d|%s" % (i, t))
    print("TOTAL", len(seen))

grab("ithome.html")
grab("pingwest.html")
grab("infoq.html")
grab("thepaper.html")
