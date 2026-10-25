# -*- coding: utf-8 -*-
"""微博热度修正 + 品玩/InfoQ 清洗"""
import re, html
from pathlib import Path
BSK = Path("C:/Users/lorns/AppData/Local/Temp/bsk_raw")
OUT = Path("D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-14")
DATE = "2026-09-14"; CT = "2026-09-14 07:25"

def rd(p):
    p = Path(p); return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
def wf(name, title, source, body):
    (OUT / name).write_text(f"---\ntitle: {title}\ndate: {DATE}\nsource: {source}\ncollectTime: {CT}\n---\n\n{body}\n", encoding="utf-8")
    print("WROTE", name, len(body))

# ---- 微博：按 tr 取 rank / word / heat（heat 取该 tr 内最后一个纯数字 span） ----
h = rd(BSK / "weibo.html")
rows = re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S)
wb = []
for r in rows:
    a = re.search(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', r, re.S)
    if not a: continue
    t = html.unescape(re.sub(r"<[^>]+>", "", a.group(2)).strip())
    if not (2 <= len(t) <= 60): continue
    # 排名
    rk = re.search(r'class="td-01[^"]*"[^>]*>\s*(\d+)', r)
    # 热度：第三个 td 内的纯数字
    tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
    heat = ""
    for td in tds:
        m = re.search(r"(\d{5,})", re.sub(r"<[^>]+>", " ", td))
        if m: heat = m.group(1); break
    label = ""
    if "新" in r and "td-03" in r: label = "新"
    if "沸" in r: label = "沸"
    if "爆" in r: label = "爆"
    wb.append((rk.group(1) if rk else "", t, heat, label))
seen=set(); wb2=[]
for x in wb:
    if x[1] in seen: continue
    seen.add(x[1]); wb2.append(x)
b = "## 微博热搜榜\n\n| 排名 | 词条 | 热度 | 标记 |\n|:--:|------|------|:--:|\n"
for rk, t, heat, lb in wb2[:50]:
    b += f"| {rk} | {t} | {heat} | {lb} |\n"
wf("微博热搜榜.md", f"微博热搜榜 · {DATE}", "微博热搜榜", b)

# ---- 品玩：只留标题行（排除描述句/导航） ----
pw = re.sub(r"^A new bsk version is available.*\n?", "", rd(BSK / "pingwest.txt"), flags=re.M)
pws = []
for l in pw.split("\n"):
    l = l.strip()
    if not (10 <= len(l) <= 60): continue
    if l.startswith("首页 实时要闻"): continue
    if l.endswith("。") and len(l) > 18: continue      # 描述句
    if re.match(r"^[\u4e00-\u9fa5A-Za-z]{1,6}$", l): continue
    pws.append(l)
pws = list(dict.fromkeys(pws))
b = "## 品玩一周精选\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(pws[:15], 1): b += f"| {i} | {t} |\n"
wf("品玩一周精选.md", f"品玩一周精选 · {DATE}", "品玩一周精选", b)

# ---- InfoQ：只留标题行 ----
iq = re.sub(r"^A new bsk version is available.*\n?", "", rd(BSK / "infoq.txt"), flags=re.M)
iqs = []
for l in iq.split("\n"):
    l = l.strip()
    if not (14 <= len(l) <= 90): continue
    if l.startswith("作者") or l.startswith("登录") or "。" in l: continue
    if re.match(r"^\d{4}-\d{2}-\d{2}$", l): continue
    iqs.append(l)
iqs = list(dict.fromkeys(iqs))
b = "## InfoQ中国热点（7天）\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(iqs[:15], 1): b += f"| {i} | {t} |\n"
wf("InfoQ中国热点.md", f"InfoQ中国热点 · {DATE}", "InfoQ中国热点", b)
print("DONE")
