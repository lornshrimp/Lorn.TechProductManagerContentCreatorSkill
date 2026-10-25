# -*- coding: utf-8 -*-
"""2026-09-14 采集原始数据 → 各源榜单 md 生成"""
import re, html, json, os
from pathlib import Path

BSK = Path("C:/Users/lorns/AppData/Local/Temp/bsk_raw")
RAW = Path("D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-14/_raw")
OUT = Path("D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-14")
DATE = "2026-09-14"
CT = "2026-09-14 07:15"

def rd(p):
    p = Path(p)
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

def wf(name, title, source, body):
    txt = f"""---
title: {title}
date: {DATE}
source: {source}
collectTime: {CT}
---

{body}
"""
    (OUT / name).write_text(txt, encoding="utf-8")
    print("WROTE", name, len(txt))

def strip_bsk_noise(s):
    return re.sub(r"^A new bsk version is available.*\n?", "", s, flags=re.M)

# ============ 1. 微博热搜榜 ============
h = rd(BSK / "weibo.html")
rows = re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S)
wb = []
for r in rows:
    a = re.search(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', r, re.S)
    if not a: continue
    t = html.unescape(re.sub(r"<[^>]+>", "", a.group(2)).strip())
    if not (2 <= len(t) <= 60) or t in ("登录",): continue
    heat = re.search(r"<td class=\"td-02\">(.*?)</td>", r, re.S)
    hv = ""
    if heat:
        hm = re.search(r"(\d[\d,\.]*)", re.sub(r"<[^>]+>", " ", heat.group(1)))
        hv = hm.group(1) if hm else ""
    wb.append((t, hv))
seen=set(); wb2=[]
for t,hv in wb:
    if t in seen: continue
    seen.add(t); wb2.append((t,hv))
body = "## 微博热搜榜\n\n| 排名 | 词条 | 热度 |\n|:--:|------|------|\n"
for i,(t,hv) in enumerate(wb2[:50],1):
    body += f"| {i} | {t} | {hv} |\n"
wf("微博热搜榜.md", f"微博热搜榜 · {DATE}", "微博热搜榜", body)

# ============ 2. 知乎问题热榜 ============
zh = strip_bsk_noise(rd(BSK / "zhihu_hot.txt"))
zhrows = []
for line in zh.strip().split("\n"):
    parts = line.split("##")
    if len(parts) == 4 and parts[3].startswith("http"):
        zhrows.append(parts)
body = "## 知乎问题热榜\n\n| 排名 | 问题标题 | 热度 | 链接 |\n|:--:|------|------|------|\n"
for p in zhrows:
    qid = p[3].rstrip("/").split("/")[-1]
    body += f"| {p[0]} | {p[2]} | {p[1]} | [去回答](https://www.zhihu.com/question/{qid}) |\n"
wf("知乎问题热榜.md", f"知乎问题热榜 · {DATE}", "知乎问题热榜", body)

# ============ 3/4. 知乎推荐 / 邀请问题 ============
def zhihu_qlist(fname, title, source):
    s = strip_bsk_noise(rd(BSK / fname))
    qs = []
    for m in re.finditer(r'link "([^"]{10,90})"', s):
        t = m.group(1)
        if t.startswith("欢迎进入") or t.startswith("创作分"): continue
        t = re.sub(r"^(飙升|火爆|新问|热榜|邀请)\s+", "", t).strip()
        if t not in qs: qs.append(t)
    b = f"## {source}\n\n| 序号 | 问题标题 | 状态 |\n|:--:|------|------|\n"
    for i, t in enumerate(qs, 1):
        b += f"| {i} | {t} | 待答 |\n"
    wf(fname.replace("_snap.txt", ".md"), title, source, b)
    return qs

rq = zhihu_qlist("zhihu_recommend_snap.txt", f"知乎推荐问题 · {DATE}", "知乎推荐问题")
iq = zhihu_qlist("zhihu_invited_snap.txt", f"知乎邀请问题 · {DATE}", "知乎邀请问题")

# ============ 5. 知乎想法话题 ============
idea = strip_bsk_noise(rd(BSK / "zhihu_idea.txt"))
topics = re.findall(r"\n([^\n]{2,14})\n(?:等[\d\.万]+ ?人参与讨论|快来参与讨论吧)", idea)
b = "## 知乎想法话题\n\n| 序号 | 话题 | 参与热度 |\n|:--:|------|------|\n"
for i, t in enumerate(dict.fromkeys(topics), 1):
    b += f"| {i} | {t} | - |\n"
wf("知乎想法话题.md", f"知乎想法话题 · {DATE}", "知乎想法话题", b)

# ============ 6. B站热门 ============
bl = strip_bsk_noise(rd(BSK / "bilibili.txt"))
bv = re.findall(r"\n(\d{1,2})\n([^\n]{8,80})\n([^\n]{2,20})\n([\d\.]+万)\n", bl)
b = "## B站综合热门（排行榜）\n\n| 排名 | 标题 | UP主 | 播放 |\n|:--:|------|------|------|\n"
for r in bv[:25]:
    b += f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |\n"
wf("B站热门.md", f"B站热门 · {DATE}", "B站热门", b)

# ============ 7. 抖音热点 ============
dy = strip_bsk_noise(rd(BSK / "douyin.txt"))
dys = [l.strip() for l in dy.split("\n") if 10 < len(l.strip()) < 60 and "#" in l.strip()]
b = "## 抖音热点\n\n| 序号 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(dys), 1):
    b += f"| {i} | {t} |\n"
wf("抖音热点.md", f"抖音热点 · {DATE}", "抖音热点", b)

# ============ 8. 头条热榜 ============
tt = strip_bsk_noise(rd(BSK / "toutiao.txt"))
noise = set("下载头条APP添加到桌面关于头条反馈关注推荐北京视频财经科技热点国际更多消息发布作品".split())
tts = []
for l in tt.split("\n"):
    l = l.strip()
    if not l or l in noise: continue
    if 6 <= len(l) <= 30 and not any(ch in l for ch in "℃　"):
        tts.append(l)
seen=set(); tts2=[]
for t in tts:
    if t in seen: continue
    seen.add(t); tts2.append(t)
b = "## 头条热榜（热点频道）\n\n| 序号 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(tts2[:30], 1):
    b += f"| {i} | {t} |\n"
wf("头条热榜.md", f"头条热榜 · {DATE}", "头条热榜", b)

# ============ 9. 虎嗅 ============
hx = strip_bsk_noise(rd(BSK / "huxiu.txt"))
hxs = []
lines = [l.strip() for l in hx.split("\n")]
for i, l in enumerate(lines):
    if l in ("金融财经","书影音","社会文化","前沿科技","车与出行","商业消费","观点","国际热点","出海","3C数码","健康","游戏娱乐","医疗","其他","24小时","视频"):
        if i+1 < len(lines) and 8 <= len(lines[i+1]) <= 45:
            hxs.append(f"{l}｜{lines[i+1]}")
b = "## 虎嗅48h热文\n\n| 序号 | 分类 | 标题 |\n|:--:|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(hxs), 1):
    c, ti = t.split("｜", 1)
    b += f"| {i} | {c} | {ti} |\n"
wf("虎嗅48h热文.md", f"虎嗅48h热文 · {DATE}", "虎嗅48h热文", b)

# ============ 10. InfoQ ============
iq2 = strip_bsk_noise(rd(BSK / "infoq.txt"))
iqs = [l.strip() for l in iq2.split("\n") if 12 <= len(l.strip()) <= 90 and not l.strip().startswith("作者")]
b = "## InfoQ中国热点（7天）\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(iqs), 1):
    b += f"| {i} | {t} |\n"
wf("InfoQ中国热点.md", f"InfoQ中国热点 · {DATE}", "InfoQ中国热点", b)

# ============ 11. 品玩 ============
pw = strip_bsk_noise(rd(BSK / "pingwest.txt"))
pws = [l.strip() for l in pw.split("\n") if 10 <= len(l.strip()) <= 60 and not re.match(r"^[\u4e00-\u9fa5]{1,4}\s*·", l.strip())]
b = "## 品玩一周精选\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(pws), 1):
    b += f"| {i} | {t} |\n"
wf("品玩一周精选.md", f"品玩一周精选 · {DATE}", "品玩一周精选", b)

# ============ 12. 知微事见 ============
zw = strip_bsk_noise(rd(BSK / "zhiwei.txt"))
b = "## 知微事见 · 事件库（含影响力指数）\n\n| 序号 | 分类 | 事件 | 影响力指数 |\n|:--:|:--:|------|:--:|\n"
seg = zw.split("事件列表", 1)[-1].split("查看更多", 1)[0]
blocks = [x for x in seg.split("\n") if x.strip()]
cat = ""
cnt = 0
i = 0
while i < len(blocks):
    l = blocks[i].strip()
    if l in ("社会","互联网","金融","政务","财经","企业","娱乐","灾难","违法犯罪","国际","体育","谣言"):
        cat = l
        name = blocks[i+1].strip() if i+1 < len(blocks) else ""
        idx = ""
        for k in range(i+2, min(i+8, len(blocks))):
            if re.match(r"^\d+\.\d+$", blocks[k].strip()):
                idx = blocks[k].strip(); break
        if idx:
            cnt += 1
            b += f"| {cnt} | {cat} | {name} | {idx} |\n"
    i += 1
wf("知微事见.md", f"知微事见 · {DATE}", "知微事见", b)

# ============ 13. 澎湃 ============
tp = strip_bsk_noise(rd(BSK / "thepaper.txt"))
b = "## 澎湃新闻热榜（要闻）\n\n| 序号 | 标题 |\n|:--:|------|\n"
tps = []
for l in tp.split("\n"):
    l = l.strip()
    if 15 <= len(l) <= 60 and ("习近平" in l or "金砖" in l or "王毅" in l or "媒体" in l or "江苏" in l or "苏州" in l or "辟谣" in l):
        tps.append(l)
for i, t in enumerate(dict.fromkeys(tps), 1):
    b += f"| {i} | {t} |\n"
wf("澎湃新闻热榜.md", f"澎湃新闻热榜 · {DATE}", "澎湃新闻热榜", b)

# ============ 14. 网易 ============
ne = rd(RAW / "163.html")
nes = []
for m in re.finditer(r'<a[^>]+href="[^"]*163\.com[^"]*"[^>]*>(.*?)</a>', ne, re.S):
    t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip())
    if 10 <= len(t) <= 60: nes.append(t)
b = "## 网易新闻热点排行\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(nes), 1):
    b += f"| {i} | {t} |\n"
wf("网易新闻热点排行.md", f"网易新闻热点排行 · {DATE}", "网易新闻热点排行", b)

# ============ 15. IT之家 ============
it = rd(RAW / "ithome.html")
its = []
for m in re.finditer(r'<a[^>]+href="(https?://[^"]*ithome\.com/[^"]*)"[^>]*>(.*?)</a>', it, re.S):
    t = html.unescape(re.sub(r"<[^>]+>", "", m.group(2)).strip())
    if 10 <= len(t) <= 60: its.append(t)
b = "## IT之家热榜\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(its), 1):
    b += f"| {i} | {t} |\n"
wf("IT之家热榜.md", f"IT之家热榜 · {DATE}", "IT之家热榜", b)

# ============ 16. 百度热搜 ============
j = json.loads(rd(RAW / "baidu_hot.json"))
items = []
for card in j.get("data", {}).get("cards", []):
    for c in card.get("content", []):
        for t in (c.get("content") or []):
            if isinstance(t, dict) and t.get("word"):
                items.append(t.get("word"))
b = "## 百度热搜榜（实时）\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(dict.fromkeys(items), 1):
    b += f"| {i} | {t} |\n"
wf("百度热搜榜.md", f"百度热搜榜 · {DATE}", "百度热搜榜", b)

print("\n=== 推荐问题 ===")
for q in rq: print(" ", q)
print("\n=== 邀请问题 ===")
for q in iq: print(" ", q)
