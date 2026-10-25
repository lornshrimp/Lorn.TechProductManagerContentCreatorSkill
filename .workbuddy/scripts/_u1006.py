# -*- coding: utf-8 -*-
"""2026-10-06 urllib 直连采集：SSR 源 + 可直连源"""
import urllib.request, re, json, ssl, gzip

ssl._create_default_https_context = ssl._create_unverified_context

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
HDR = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}
OUT = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\.workbuddy\scripts\_u1006_result.json"


def fetch(url, timeout=25, enc=None):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        for e in ([enc] if enc else ["utf-8", "gbk", "gb18030"]):
            try:
                return raw.decode(e)
            except Exception:
                continue
        return raw.decode("utf-8", "ignore")


def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
    return re.sub(r"\s+", " ", s).strip()


results = {}
status = {}


def try_src(name, fn):
    try:
        r = fn()
        if r:
            results[name] = r
            status[name] = f"OK {len(r)}"
        else:
            results[name] = []
            status[name] = "EMPTY"
    except Exception as e:
        results[name] = []
        status[name] = f"FAIL {type(e).__name__}: {e}"


def baidu():
    h = fetch("https://top.baidu.com/board?tab=realtime")
    out = []
    for m in re.finditer(r'"word":"(.*?)"', h):
        try:
            w = m.group(1).encode().decode("unicode_escape")
        except Exception:
            w = m.group(1)
        if w and w not in out:
            out.append(w)
    if not out:
        for m in re.finditer(r'class="c-single-text-ellipsis"[^>]*>(.*?)<', h):
            out.append(clean(m.group(1)))
    return out[:30]


def ithome():
    h = fetch("https://www.ithome.com/")
    out = []
    for m in re.finditer(r'<a[^>]+href="https://www\.ithome\.com/0/\d+/\d+\.htm"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if t and t not in out:
            out.append(t)
    return out[:30]


def thepaper():
    h = fetch("https://www.thepaper.cn/")
    out = []
    for m in re.finditer(r'"name":"(.*?)"', h):
        try:
            t = m.group(1).encode().decode("unicode_escape")
        except Exception:
            t = m.group(1)
        if t and 6 < len(t) < 60 and t not in out:
            out.append(t)
    return out[:30]


def news163():
    h = fetch("https://news.163.com/")
    out = []
    for m in re.finditer(r'<a[^>]+href="https://www\.163\.com/[^"]+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if t and 6 < len(t) < 60 and t not in out:
            out.append(t)
    return out[:30]


def weibo_json():
    """微博热搜官方 JSON 接口"""
    h = fetch("https://weibo.com/ajax/side/hotSearch")
    d = json.loads(h)
    out = []
    for it in d.get("data", {}).get("realtime", []):
        w = it.get("word", "")
        n = it.get("num", "")
        if w:
            out.append(f"{w}\t{n}")
    return out[:50]


def toutiao_hot():
    """头条热榜接口"""
    h = fetch("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc")
    d = json.loads(h)
    out = []
    for idx, it in enumerate(d.get("data", []), 1):
        out.append(f"{idx}\t{it.get('Title','')}\t{it.get('HotValue','')}")
    return out[:30]


try_src("百度热搜榜", baidu)
try_src("IT之家热榜", ithome)
try_src("澎湃新闻热榜", thepaper)
try_src("网易新闻热点排行", news163)
try_src("微博热搜榜_json", weibo_json)
try_src("头条热榜_json", toutiao_hot)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"status": status, "results": results}, f, ensure_ascii=False, indent=1)

print("=== STATUS ===")
for k, v in status.items():
    print(f"{k}: {v}")
