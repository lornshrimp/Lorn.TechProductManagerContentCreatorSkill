# -*- coding: utf-8 -*-
"""2026-09-27 urllib 直连采集：SSR 源 + 可直连源（结果直写 UTF-8 JSON）"""
import urllib.request, re, json, io, sys, os, gzip, ssl

ssl._create_default_https_context = ssl._create_unverified_context

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HDR = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9", "Referer": "https://weibo.com/hot/search"}
OUT = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\.workbuddy\scripts\_u0927_result.json"


def fetch(url, timeout=25, enc=None, hdr=None):
    req = urllib.request.Request(url, headers=hdr or HDR)
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


def fetch_json(url, timeout=25, hdr=None):
    return json.loads(fetch(url, timeout=timeout, hdr=hdr))


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


def weibo():
    d = fetch_json("https://weibo.com/ajax/side/hotSearch")
    band = d.get("data", {}).get("realtime", [])
    out = []
    for i, x in enumerate(band[:50], 1):
        w = x.get("word") or x.get("note") or ""
        if w:
            out.append(f"{i}##{w}##{x.get('num', '')}")
    return out


def baidu():
    h = fetch("https://top.baidu.com/board?tab=realtime")
    out = []
    for m in re.finditer(r'"word":"(.*?)"(?:.*?"desc":"(.*?)")?', h):
        w = m.group(1).encode().decode("unicode_escape")
        out.append(w)
    if not out:
        for m in re.finditer(r'class="c-single-text-ellipsis"[^>]*>(.*?)<', h):
            out.append(clean(m.group(1)))
    return out[:30]


def ithome():
    h = fetch("https://www.ithome.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="https://www\.ithome\.com/0/\d+/\d+\.htm"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60:
            out.append(t)
    return out[:30]


def news163():
    h = fetch("https://news.163.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="https://www\.163\.com/(?:news|dy)/article/[^"]+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 10 <= len(t) <= 60:
            out.append(t)
    return out[:30]


def thepaper():
    h = fetch("https://www.thepaper.cn/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/newsDetail_forward_\d+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 10 <= len(t) <= 60:
            out.append(t)
    return out[:30]


def pingwest():
    h = fetch("https://www.pingwest.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/a/\d+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60:
            out.append(t)
    return out[:30]


def huxiu():
    h = fetch("https://www.huxiu.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/article/\d+\.html"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60:
            out.append(t)
    return out[:30]


def infoq():
    h = fetch("https://www.infoq.cn/hotlist?tag=day")
    out = []
    for m in re.finditer(r'"title":"(.*?)"', h):
        t = m.group(1).encode().decode("unicode_escape")
        if 8 <= len(t) <= 80:
            out.append(t)
    return out[:30]


def bilibili():
    h = fetch("https://www.bilibili.com/ranking")
    out = []
    for m in re.finditer(r'"title":"(.*?)"', h):
        t = m.group(1).encode().decode("unicode_escape")
        if 6 <= len(t) <= 80:
            out.append(t)
    return out[:30]


def zhiwei():
    h = fetch("https://ef.zhiweidata.com/library")
    out = []
    for m in re.finditer(r'"eventName":"(.*?)"', h):
        t = m.group(1).encode().decode("unicode_escape")
        out.append(t)
    return out[:30]


def toutiao():
    h = fetch("https://www.toutiao.com/api/pc/list/feed?channel_id=hot")
    out = []
    for m in re.finditer(r'"title":"(.*?)"', h):
        t = m.group(1).encode().decode("unicode_escape")
        if 8 <= len(t) <= 60:
            out.append(t)
    return out[:30]


for n, f in [("微博热搜榜", weibo), ("百度热搜榜", baidu), ("IT之家热榜", ithome), ("网易新闻热点排行", news163),
             ("澎湃新闻热榜", thepaper), ("品玩一周精选", pingwest), ("虎嗅48h热文", huxiu),
             ("InfoQ中国热点", infoq), ("B站热门", bilibili), ("知微事见", zhiwei), ("头条热榜", toutiao)]:
    try_src(n, f)

with open(OUT, "w", encoding="utf-8") as fp:
    json.dump({"results": results, "status": status}, fp, ensure_ascii=False, indent=1)
print("WROTE", OUT)
for k, v in status.items():
    print(f"  {k}: {v}")
