# -*- coding: utf-8 -*-
"""urllib 直连采集 SSR 源 v2：IT之家 / 澎湃新闻 / 网易新闻。落盘 %TEMP%/collect/*.txt"""
import os, re, ssl, time
import urllib.request as ur

D = os.path.join(os.environ.get("TEMP", "/tmp"), "collect")
os.makedirs(D, exist_ok=True)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch(url, timeout=30):
    req = ur.Request(url, headers=HDR)
    with ur.urlopen(req, timeout=timeout, context=ctx) as r:
        raw = r.read()
    for enc in ("utf-8", "gbk", "gb18030"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", "ignore")


def clean(s):
    s = re.sub(r"(?s)<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
    return re.sub(r"\s+", " ", s).strip()


def titles(html, pattern, limit=40):
    out, seen = [], set()
    for m in re.finditer(pattern, html, re.S):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60 and t not in seen:
            seen.add(t)
            out.append(t)
        if len(out) >= limit:
            break
    return out


JOBS = [
    ("ithome", "https://www.ithome.com/",
     r'<a[^>]+class="[^"]*title[^"]*"[^>]*>(.*?)</a>'),
    ("thepaper", "https://www.thepaper.cn/",
     r'<a[^>]+href="[^"]*newsDetail[^"]*"[^>]*>(.*?)</a>'),
    ("163news", "https://news.163.com/rank/",
     r'<a[^>]+href="[^"]*(?:article|news)[^"]*"[^>]*>(.*?)</a>'),
]

for name, url, pat in JOBS:
    out = os.path.join(D, name + ".txt")
    try:
        html = fetch(url)
        ts = titles(html, pat)
        if len(ts) < 5:
            ts = titles(html, r'<a[^>]+href="[^"]*(?:/a/|newsDetail|article|/20\d\d)[^"]*"[^>]*>(.*?)</a>', 40)
        with open(out, "w", encoding="utf-8") as f:
            f.write("URL: %s\nCOUNT: %d\n\n" % (url, len(ts)))
            f.write("\n".join("%d##%s" % (i + 1, t) for i, t in enumerate(ts)))
        print("%s OK titles=%d" % (name, len(ts)))
    except Exception as e:
        with open(out, "w", encoding="utf-8") as f:
            f.write("ERROR %s: %r\n" % (url, e))
        print("%s FAIL %r" % (name, e))
    time.sleep(1)
print("DONE_URLLIB2")
