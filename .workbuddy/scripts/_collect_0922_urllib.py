# -*- coding: utf-8 -*-
"""2026-09-22 urllib 直连采集：SSR 源 + 可直连源"""
import urllib.request, re, json, io, sys, os, gzip, ssl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ssl._create_default_https_context = ssl._create_unverified_context

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
HDR = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}


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


def try_src(name, fn):
    try:
        r = fn()
        results[name] = r if r else ["(空)"]
        print(f"[{name}] OK {len(results[name])} 条")
    except Exception as e:
        results[name] = []
        print(f"[{name}] FAIL {type(e).__name__}: {e}")


# 1. 百度热搜
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


# 2. IT之家
def ithome():
    h = fetch("https://www.ithome.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="https://www\.ithome\.com/0/\d+/\d+\.htm"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60:
            out.append(t)
    return out[:30]


# 3. 网易新闻
def news163():
    h = fetch("https://news.163.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="https://www\.163\.com/(?:news|dy)/article/[^"]+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 10 <= len(t) <= 60:
            out.append(t)
    return out[:30]


# 4. 澎湃
def thepaper():
    h = fetch("https://www.thepaper.cn/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/newsDetail_forward_\d+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 10 <= len(t) <= 60:
            out.append(t)
    return out[:30]


# 5. 品玩
def pingwest():
    h = fetch("https://www.pingwest.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/a/\d+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60:
            out.append(t)
    return out[:30]


# 6. 虎嗅
def huxiu():
    h = fetch("https://www.huxiu.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/article/\d+\.html"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60:
            out.append(t)
    return out[:30]


# 7. InfoQ
def infoq():
    h = fetch("https://www.infoq.cn/hotlist?tag=day")
    out = []
    for m in re.finditer(r'"title":"(.*?)"', h):
        t = m.group(1).encode().decode("unicode_escape")
        if 8 <= len(t) <= 80:
            out.append(t)
    return out[:30]


# 8. B站排行榜
def bilibili():
    h = fetch("https://www.bilibili.com/ranking")
    out = []
    for m in re.finditer(r'"title":"(.*?)"', h):
        t = m.group(1).encode().decode("unicode_escape")
        if 6 <= len(t) <= 80:
            out.append(t)
    return out[:30]


# 9. 知微事见
def zhiwei():
    h = fetch("https://ef.zhiweidata.com/library")
    out = []
    for m in re.finditer(r'"eventName":"(.*?)"', h):
        t = m.group(1).encode().decode("unicode_escape")
        out.append(t)
    return out[:30]


for n, f in [("百度热搜榜", baidu), ("IT之家热榜", ithome), ("网易新闻热点排行", news163),
             ("澎湃新闻热榜", thepaper), ("品玩一周精选", pingwest), ("虎嗅48h热文", huxiu),
             ("InfoQ中国热点", infoq), ("B站热门", bilibili), ("知微事见", zhiwei)]:
    try_src(n, f)

print("\n" + "=" * 70)
for k, v in results.items():
    print(f"\n### {k} ({len(v)})")
    for i, t in enumerate(v[:25], 1):
        print(f"{i}. {t}")
