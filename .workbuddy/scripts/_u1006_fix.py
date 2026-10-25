# -*- coding: utf-8 -*-
import urllib.request, re, json, ssl, gzip
ssl._create_default_https_context = ssl._create_unverified_context
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
HDR = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        for e in ("utf-8", "gbk", "gb18030"):
            try:
                return raw.decode(e)
            except Exception:
                continue
        return raw.decode("utf-8", "ignore")

def unesc(s):
    if "\\u" in s:
        try:
            return s.encode("latin-1", "ignore").decode("unicode_escape")
        except Exception:
            return s
    return s

def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
    return re.sub(r"\s+", " ", s).strip()

out = {}

# 百度热搜
h = fetch("https://top.baidu.com/board?tab=realtime")
r = []
for m in re.finditer(r'"word":"(.*?)"', h):
    w = unesc(m.group(1))
    if w and w not in r:
        r.append(w)
out["百度热搜榜"] = r[:30]

# 澎湃首页（提取新闻标题，非栏目名）
h = fetch("https://www.thepaper.cn/")
r = []
for m in re.finditer(r'"name":"(.*?)"', h):
    t = unesc(m.group(1))
    if t and 8 < len(t) < 60 and t not in r:
        r.append(t)
if len(r) < 8:
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', h):
        t = clean(m.group(1))
        if t and 8 < len(t) < 60 and t not in r:
            r.append(t)
out["澎湃新闻热榜"] = r[:25]

json.dump(out, open(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\.workbuddy\scripts\_u1006_fix.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items():
    print("====", k, len(v))
    for x in v[:12]:
        print("  ", x)
