# -*- coding: utf-8 -*-
"""2026-09-26 urllib 直连采集 v2：修复百度解码 + 扩展候选入口"""
import urllib.request, re, json, gzip, ssl, html as _html

ssl._create_default_https_context = ssl._create_unverified_context

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
HDR = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}
OUT = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\.workbuddy\scripts\_u0926_result.json"


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
    s = _html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


results, status = {}, {}


def try_src(name, fn):
    try:
        r = fn()
        results[name] = r or []
        status[name] = ("OK %d" % len(r)) if r else "EMPTY"
    except Exception as e:
        results[name] = []
        status[name] = "FAIL %s: %s" % (type(e).__name__, str(e)[:80])


def baidu():
    h = fetch("https://top.baidu.com/board?tab=realtime")
    out = []
    for m in re.finditer(r'"word":"(.*?)"', h):
        w = m.group(1)
        try:
            w = json.loads('"%s"' % w)
        except Exception:
            pass
        w = clean(w)
        if 4 <= len(w) <= 60 and w not in out:
            out.append(w)
    if not out:
        for m in re.finditer(r'class="c-single-text-ellipsis"[^>]*>(.*?)<', h):
            t = clean(m.group(1))
            if t and t not in out:
                out.append(t)
    return out[:30]


def ithome():
    h = fetch("https://www.ithome.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="https://www\.ithome\.com/0/\d+/\d+\.htm"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60 and t not in out:
            out.append(t)
    return out[:30]


def news163():
    h = fetch("https://news.163.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="https://www\.163\.com/(?:news|dy)/article/[^"]+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 10 <= len(t) <= 60 and t not in out:
            out.append(t)
    return out[:30]


def thepaper():
    h = fetch("https://www.thepaper.cn/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/newsDetail_forward_\d+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 10 <= len(t) <= 60 and t not in out:
            out.append(t)
    return out[:30]


def pingwest():
    h = fetch("https://www.pingwest.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/a/\d+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60 and t not in out:
            out.append(t)
    return out[:30]


def huxiu():
    h = fetch("https://www.huxiu.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/article/\d+\.html"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60 and t not in out:
            out.append(t)
    return out[:30]


def infoq():
    h = fetch("https://www.infoq.cn/hotlist?tag=day")
    out = []
    for m in re.finditer(r'"title":"(.*?)"', h):
        t = m.group(1)
        try:
            t = json.loads('"%s"' % t)
        except Exception:
            pass
        t = clean(t)
        if 8 <= len(t) <= 80 and t not in out:
            out.append(t)
    return out[:30]


def bilibili():
    h = fetch("https://www.bilibili.com/v/popular/rank/all")
    out = []
    for m in re.finditer(r'"title":"(.*?)"', h):
        t = m.group(1)
        try:
            t = json.loads('"%s"' % t)
        except Exception:
            pass
        t = clean(t)
        if 6 <= len(t) <= 80 and t not in out:
            out.append(t)
    return out[:30]


def zhiwei():
    h = fetch("https://ef.zhiweidata.com/library")
    out = []
    for m in re.finditer(r'"eventName":"(.*?)"', h):
        t = m.group(1)
        try:
            t = json.loads('"%s"' % t)
        except Exception:
            pass
        t = clean(t)
        if t and t not in out:
            out.append(t)
    return out[:30]


for n, f in [("百度热搜榜", baidu), ("IT之家热榜", ithome), ("网易新闻热点排行", news163),
             ("澎湃新闻热榜", thepaper), ("品玩一周精选", pingwest), ("虎嗅48h热文", huxiu),
             ("InfoQ中国热点", infoq), ("B站热门", bilibili), ("知微事见", zhiwei)]:
    try_src(n, f)

with open(OUT, "w", encoding="utf-8") as fp:
    json.dump({"results": results, "status": status}, fp, ensure_ascii=False, indent=1)
print("WROTE", OUT)
for k, v in status.items():
    print(k, "->", v)
