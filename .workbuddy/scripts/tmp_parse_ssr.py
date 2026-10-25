# -*- coding: utf-8 -*-
"""2026-09-14 SSR 源解析"""
import json, re, os, sys, html
from pathlib import Path

RAW = Path("D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-14/_raw")

def rd(n):
    p = RAW / n
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")

out = {}

# ---------- 百度热搜 ----------
try:
    j = json.loads(rd("baidu_hot.json"))
    items = []
    for card in j.get("data", {}).get("cards", []):
        for c in card.get("content", []):
            w = c.get("word") or c.get("query") or c.get("title")
            if not w:
                # nested topContent
                tc = c.get("topContent") or []
                for t in tc:
                    if t.get("word"):
                        items.append((t.get("word"), t.get("hotScore") or t.get("hotChange") or ""))
            else:
                items.append((w, c.get("hotScore") or c.get("hotChange") or ""))
    seen = set(); uni = []
    for w, s in items:
        if w in seen: continue
        seen.add(w); uni.append((w, s))
    out["baidu"] = uni[:40]
except Exception as e:
    out["baidu"] = [("ERR", str(e))]

# ---------- IT之家 ----------
h = rd("ithome.html")
its = []
for m in re.finditer(r'<a[^>]+href="(https?://[^"]*ithome\.com/[^"]*)"[^>]*>(.*?)</a>', h, re.S):
    t = re.sub(r"<[^>]+>", "", m.group(2)).strip()
    t = html.unescape(t)
    if 8 <= len(t) <= 60 and not t.startswith("IT之家"):
        its.append(t)
seen = set(); its2 = []
for t in its:
    if t in seen: continue
    seen.add(t); its2.append(t)
out["ithome"] = its2[:30]

# ---------- 网易 ----------
h = rd("163.html")
nes = []
for m in re.finditer(r'<a[^>]+href="(https?://(?:www\.)?163\.com/[^"]*|https?://news\.163\.com/[^"]*)"[^>]*>(.*?)</a>', h, re.S):
    t = re.sub(r"<[^>]+>", "", m.group(2)).strip()
    t = html.unescape(t)
    if 10 <= len(t) <= 60:
        nes.append(t)
seen = set(); nes2 = []
for t in nes:
    if t in seen: continue
    seen.add(t); nes2.append(t)
out["163"] = nes2[:30]

# ---------- 澎湃 ----------
h = rd("thepaper.html")
tps = re.findall(r'"name":"([^"]{10,60})"', h)
seen = set(); tps2 = []
for t in tps:
    t = html.unescape(t.strip())
    if t in seen: continue
    seen.add(t); tps2.append(t)
if len(tps2) < 8:
    tps2 = list(dict.fromkeys(re.findall(r'"title":"([^"]{10,60})"', h)))
out["thepaper"] = tps2[:30]

# ---------- 品玩 ----------
h = rd("pingwest.html")
pws = []
for m in re.finditer(r'<a[^>]+href="(/a/\d+)"[^>]*>(.*?)</a>', h, re.S):
    t = re.sub(r"<[^>]+>", "", m.group(2)).strip()
    t = html.unescape(t)
    if 8 <= len(t) <= 60:
        pws.append(t)
pws = re.findall(r'"title":"([^"]{8,60})"', h) or pws
out["pingwest"] = list(dict.fromkeys(pws))[:30]

# ---------- InfoQ ----------
h = rd("infoq.html")
iq = re.findall(r'"article_title":"([^"]{8,80})"', h) or re.findall(r'"title":"([^"]{8,80})"', h)
out["infoq"] = list(dict.fromkeys(iq))[:30]

# ---------- 虎嗅 ----------
h = rd("huxiu.html")
if "aliyun_waf" in h or len(h) < 20000:
    out["huxiu"] = [("WAF", "urllib 被 WAF 拦截，需 bsk")]
else:
    hx = re.findall(r'"title":"([^"]{8,80})"', h)
    out["huxiu"] = list(dict.fromkeys(hx))[:30]

for k, v in out.items():
    print("=" * 20, k, len(v))
    for x in v[:25]:
        print("  ", x)
