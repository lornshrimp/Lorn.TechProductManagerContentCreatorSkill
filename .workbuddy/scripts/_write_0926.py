# -*- coding: utf-8 -*-
import os, io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot/榜单/2026-09-26")
TMP = r"C:/Users/lorns/AppData/Local/Temp/bsk0926"
DATE = "2026-09-26"
CT = "2026-09-26 07:20"
os.makedirs(OUT, exist_ok=True)

def rd(name):
    p = os.path.join(TMP, name)
    if not os.path.exists(p): return ""
    return open(p, encoding="utf-8", errors="replace").read()

def clean(t):
    t = re.sub(r"^A new bsk version.*\n", "", t)
    return t.strip()

def w(fn, title, source, body, note):
    fm = f"---\ntitle: {title} · {DATE}\nsource: {source}\ndate: {DATE}\ncollectTime: {CT}\n---\n\n{body}\n\n> {note}\n"
    open(os.path.join(OUT, fn), "w", encoding="utf-8").write(fm)
    print("WROTE", fn)

# 1 微博热搜榜
lines = [l for l in clean(rd("weibo_api.txt")).split("\n") if l.strip()]
rows = []
for l in lines:
    p = l.split("##")
    if len(p) >= 3:
        rows.append((p[0], p[1], p[2]))
body = "## 微博热搜榜（TOP %d）\n\n| 排名 | 词条 | 热度值 |\n|:--:|------|------|\n" % len(rows)
body += "\n".join(f"| {r[0]} | {r[1]} | {r[2]} |" for r in rows)
w("微博热搜榜.md", "微博热搜榜", "微博热搜榜", body, f"采集通道：urllib 直连微博 PC 端 AJAX 接口 `weibo.com/ajax/side/hotSearch`（bsk get-html 仅得 SPA 空壳，故改用官方 JSON 接口）；采集时间 {CT}；共 {len(rows)} 条，含热度值。")

# 2 百度热搜榜
d = json.load(open(os.path.join(ROOT, ".workbuddy/scripts/_u0926_result.json"), encoding="utf-8"))
bd = d["results"]["百度热搜榜"]
body = "## 百度热搜榜（TOP %d）\n\n| 排名 | 词条 |\n|:--:|------|\n" % len(bd)
body += "\n".join(f"| {i} | {t} |" for i, t in enumerate(bd, 1))
w("百度热搜榜.md", "百度热搜榜", "百度热搜榜", body, f"采集通道：urllib 直连 `top.baidu.com/board?tab=realtime`（SSR）；采集时间 {CT}；共 {len(bd)} 条。")

# 3 知乎问题热榜
zh = [l for l in clean(rd("zhihu_hot.txt")).split("\n") if "##" in l]
body = "## 知乎问题热榜（TOP %d）\n\n| 排名 | 热度 | 问题标题 | 链接 |\n|:--:|------|------|------|\n" % len(zh)
for l in zh:
    p = l.split("##")
    if len(p) >= 4:
        body += f"| {p[0]} | {p[1]} | {p[2]} | [去回答]({p[3]}) |\n"
w("知乎问题热榜.md", "知乎问题热榜", "知乎问题热榜", body, f"采集通道：bsk 登录态 navigate + evaluate 条目内四元组对齐提取（排名/热度/标题/链接同次取出）；采集时间 {CT}；共 {len(zh)} 条。")

# 4 知乎推荐问题
def zlist(fn):
    seen, out = set(), []
    for l in clean(rd(fn)).split("\n"):
        if "##" not in l: continue
        t, u = l.rsplit("##", 1)
        t = t.strip()
        if t and t not in seen and u.startswith("http"):
            seen.add(t); out.append((t, u))
    return out
rec = zlist("zhihu_recommend.txt")
body = "## 知乎推荐问题（%d 条）\n\n| # | 问题标题 | 链接 |\n|:--:|------|------|\n" % len(rec)
body += "\n".join(f"| {i} | {t} | [去回答]({u}) |" for i, (t, u) in enumerate(rec, 1))
w("知乎推荐问题.md", "知乎推荐问题", "知乎推荐问题", body, f"采集通道：bsk 登录态 `creator/featured-question/recommend`（3 轮滚动去重）；采集时间 {CT}；共 {len(rec)} 条，含链接列。")

# 5 知乎邀请问题
inv = zlist("zhihu_invited.txt")
body = "## 知乎邀请问题（%d 条）\n\n| # | 问题标题 | 链接 |\n|:--:|------|------|\n" % len(inv)
body += "\n".join(f"| {i} | {t} | [去回答]({u}) |" for i, (t, u) in enumerate(inv, 1))
w("知乎邀请问题.md", "知乎邀请问题", "知乎邀请问题", body, f"采集通道：bsk 登录态 `creator/featured-question/invited`（3 轮去重）；采集时间 {CT}；共 {len(inv)} 条，含链接列。")

# 6 头条热榜
tt = [l.strip() for l in clean(rd("toutiao.txt")).split("\n") if l.strip() and not l.startswith("京") and not l.startswith("跟帖") and not l.startswith("网信") and not l.startswith("下载") and "ICP" not in l]
items = []
buf = None
for l in tt:
    if re.fullmatch(r"\d+", l):
        if buf: items.append((len(items)+1, buf)); buf = None
    else:
        buf = l
body = "## 头条热榜（TOP %d）\n\n| 排名 | 词条 |\n|:--:|------|\n" % len(items)
body += "\n".join(f"| {i} | {t} |" for i, t in items)
w("头条热榜.md", "头条热榜", "头条热榜", body, f"采集通道：bsk 登录态 `toutiao.com/?channel=hot&source=ch` + evaluate；采集时间 {CT}；共 {len(items)} 条（接口条目数较昨日下降，以中美元首外交与中秋/亚运为主）。")

# 7 B站热门
bl = [l.strip() for l in clean(rd("bilibili.txt")).split("\n") if l.strip()]
body = "## B站热门（TOP %d）\n\n| 排名 | 标题 |\n|:--:|------|\n" % len(bl)
body += "\n".join(f"| {i} | {t} |" for i, t in enumerate(bl, 1))
w("B站热门.md", "B站热门", "B站热门", body, f"采集通道：bsk `bilibili.com/ranking` + evaluate `.video` 条目；采集时间 {CT}；共 {len(bl)} 条，内容以游戏/动画/生活为主，政经密度低。")

print("PART1 DONE")
