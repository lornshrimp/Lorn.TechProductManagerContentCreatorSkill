# -*- coding: utf-8 -*-
import urllib.request, urllib.error, ssl, re, json, os, sys, gzip, io

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
            for enc in ("utf-8", "gbk", "gb18030"):
                try:
                    return data.decode(enc)
                except Exception:
                    continue
            return data.decode("utf-8", "ignore")
    except Exception as e:
        return "ERR:%s" % e

def save(name, text):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print("SAVED %s len=%d head=%s" % (name, len(text), text[:80].replace("\n", " ")))

targets = {
    "ithome.html": "https://www.ithome.com/",
    "ithome_rank.html": "https://www.ithome.com/rank/",
    "163.html": "https://news.163.com/",
    "thepaper.html": "https://www.thepaper.cn/",
    "pingwest.html": "https://www.pingwest.com/",
    "baidu_hot.json": "https://top.baidu.com/api/board?platform=wise&tab=realtime",
    "baidu_board.html": "https://top.baidu.com/board?tab=realtime",
    "infoq.html": "https://www.infoq.cn/",
    "huxiu.html": "https://www.huxiu.com/",
}

for name, url in targets.items():
    t = fetch(url)
    save(name, t)

print("DONE")
