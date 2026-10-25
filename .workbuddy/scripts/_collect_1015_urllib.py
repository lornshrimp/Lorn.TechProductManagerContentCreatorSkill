# -*- coding: utf-8 -*-
"""2026-10-09 urllib 直连采集：SSR 源 + 可直连源"""
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


ESC = chr(92) + 'u'


def baidu():
    h = fetch("https://top.baidu.com/board?tab=realtime")
    out = []
    for m in re.finditer(r'"word":"(.*?)"', h):
        w = m.group(1)
        if ESC in w:
            w = w.encode().decode("unicode_escape")
        else:
            try:
                w = w.encode("latin-1").decode("utf-8")
            except Exception:
                pass
        if w and w not in out:
            out.append(w)
    if not out:
        for m in re.finditer(r'class="c-single-text-ellipsis"[^>]*>(.*?)<', h):
            out.append(clean(m.group(1)))
    return out[:30]


def toutiao():
    h = fetch("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc")
    j = json.loads(h)
    out = []
    for it in j.get("data", []):
        t = it.get("Title", "")
        hv = it.get("HotValue", "")
        if t:
            out.append(f"{t}##{hv}")
    return out[:30]


def ithome():
    h = fetch("https://www.ithome.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="https://www\.ithome\.com/0/\d+/\d+\.htm"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 8 <= len(t) <= 60:
            out.append(t)
    seen = []
    for t in out:
        if t not in seen:
            seen.append(t)
    return seen[:30]


def news163():
    h = fetch("https://news.163.com/")
    out = []
    for m in re.finditer(r'<a[^>]*href="https://www\.163\.com/(?:news|dy)/article/[^"]+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 10 <= len(t) <= 60:
            out.append(t)
    seen = []
    for t in out:
        if t not in seen:
            seen.append(t)
    return seen[:30]


def thepaper():
    h = fetch("https://www.thepaper.cn/")
    out = []
    for m in re.finditer(r'<a[^>]*href="/newsDetail_forward_\d+"[^>]*>(.*?)</a>', h):
        t = clean(m.group(1))
        if 10 <= len(t) <= 60:
            out.append(t)
    seen = []
    for t in out:
        if t not in seen:
            seen.append(t)
    return seen[:30]


for n, f in [("百度热搜榜", baidu), ("头条热榜", toutiao), ("IT之家热榜", ithome),
             ("网易新闻热点排行", news163), ("澎湃新闻热榜", thepaper)]:
    try_src(n, f)

print("\n" + "=" * 70)
for k, v in results.items():
    print(f"\n### {k} ({len(v)})")
    for i, t in enumerate(v[:30], 1):
        print(f"{i}. {t}")

with open(os.path.join(os.environ.get("TEMP", "."), "urllib1015.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("\nSAVED")

