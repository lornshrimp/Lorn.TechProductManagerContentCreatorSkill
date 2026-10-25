# -*- coding: utf-8 -*-
"""把 2026-10-09 采集到的原始数据落盘为 hotspot/榜单/2026-10-09/*.md"""
import json, os, io, sys, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot", "榜单", "2026-10-09")
T = r"C:\Users\lorns\AppData\Local\Temp"
B = os.path.join(T, "bsk1009")
os.makedirs(OUT, exist_ok=True)

CT = "2026-10-09 07:10"


def wr(name, title, body, source=None):
    src = source or name
    txt = (f"---\ntitle: {title}\ndate: 2026-10-09\nsource: {src}\n"
           f"collectTime: {CT}\n---\n\n{body}\n")
    with open(os.path.join(OUT, name + ".md"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"[{name}] {len(txt)} bytes")


def rd(p):
    for enc in ("utf-8", "gbk", "gb18030"):
        try:
            return open(p, encoding=enc, errors="ignore").read()
        except Exception:
            continue
    return ""


# ---- 微博 ----
wj = json.load(open(os.path.join(B, "weibo.json"), encoding="utf-8"))
rows = wj["微博热搜榜"]
b = ["## 微博热搜榜（实时）", "", "| 排名 | 词条 |", "|:--:|------|"]
for i, r in enumerate(rows, 1):
    w = r.split("##")[0]
    b.append(f"| {i} | {w} |")
wr("微博热搜榜", "微博热搜榜 · 2026-10-09", "\n".join(b))

# ---- 百度热搜 ----
u = json.load(open(os.path.join(T, "urllib1009.json"), encoding="utf-8"))
b = ["## 百度热搜榜（实时）", "", "| 排名 | 词条 |", "|:--:|------|"]
for i, r in enumerate(u["百度热搜榜"], 1):
    b.append(f"| {i} | {r} |")
wr("百度热搜榜", "百度热搜榜 · 2026-10-09", "\n".join(b))

# ---- 知乎问题热榜 ----
lines = [x for x in rd(os.path.join(B, "zhihu_hot.txt")).split("\n") if x.strip()]
b = ["## 知乎问题热榜", "", "| 排名 | 问题 | 热度 | 链接 |", "|:--:|------|:--:|:--:|"]
for ln in lines:
    p = ln.split("##")
    if len(p) < 4:
        continue
    rank, hot, t, url = p[0], p[1], p[2], p[3]
    b.append(f"| {rank} | {t} | {hot} | [去回答]({url}) |")
wr("知乎问题热榜", "知乎问题热榜 · 2026-10-09", "\n".join(b))


# ---- 知乎推荐/邀请问题 ----
def pair_file(p):
    out = []
    for ln in rd(p).split("\n"):
        ln = ln.strip()
        if "##" not in ln:
            continue
        t, url = ln.split("##", 1)
        t = re.sub(r"^(新问|飙升)", "", t)
        if len(t) > 8 and "www.zhihu.com/question" in url:
            out.append((t, url))
    seen, res = set(), []
    for t, url in out:
        if url not in seen:
            seen.add(url)
            res.append((t, url))
    return res


rp = pair_file(os.path.join(B, "zhihu_recommend.txt"))
b = ["## 知乎推荐问题", "", "| 排名 | 问题 | 链接 |", "|:--:|------|:--:|"]
for i, (t, url) in enumerate(rp[:40], 1):
    b.append(f"| {i} | {t} | [去回答]({url}) |")
wr("知乎推荐问题", "知乎推荐问题 · 2026-10-09", "\n".join(b))

ip = pair_file(os.path.join(B, "zhihu_invited.txt"))
b = ["## 知乎邀请问题", "", "| 排名 | 问题 | 链接 |", "|:--:|------|:--:|"]
for i, (t, url) in enumerate(ip[:20], 1):
    b.append(f"| {i} | {t} | [去回答]({url}) |")
wr("知乎邀请问题", "知乎邀请问题 · 2026-10-09", "\n".join(b))

# ---- 头条热榜 ----
b = ["## 头条热榜", "", "| 排名 | 标题 | 热度 |", "|:--:|------|:--:|"]
for i, r in enumerate(u["头条热榜"], 1):
    p = r.split("##")
    b.append(f"| {i} | {p[0]} | {p[1] if len(p)>1 else ''} |")
wr("头条热榜", "头条热榜 · 2026-10-09", "\n".join(b))

# ---- B站 ----
bl = [x.strip() for x in rd(os.path.join(B, "bilibili.txt")).split("\n") if x.strip() and len(x.strip()) > 5]
b = ["## B站全站排行榜（综合热门）", "", "| 排名 | 视频标题 |", "|:--:|------|"]
for i, r in enumerate(bl[:40], 1):
    b.append(f"| {i} | {r} |")
wr("B站热门", "B站热门 · 2026-10-09", "\n".join(b))

# ---- 抖音 ----
dy = rd(os.path.join(B, "douyin.txt"))
hits = re.findall(r"热点[:：](.{2,40}?)\n([\d.]+万?人在看)", dy)
b = ["## 抖音热榜（部分渲染）", "", "| 排名 | 热点 | 热度 |", "|:--:|------|:--:|"]
seen = set()
n = 0
for t, hv in hits:
    t = t.strip()
    if t in seen:
        continue
    seen.add(t)
    n += 1
    b.append(f"| {n} | {t} | {hv} |")
b.append("")
b.append("> 注：抖音热榜模块本轮仅部分渲染（页面主要渲染页脚与推荐流），取到 5 条热点词条，另采到若干热门视频。")
wr("抖音热点", "抖音热点 · 2026-10-09", "\n".join(b))

# ---- 百度指数 ----
bi = rd(os.path.join(B, "baidu_index.txt"))
b = ["## 百度指数（首页可见推荐位）", "", bi.strip(), "",
     "> ⚠️ 百度指数仅首页推荐位可见，行业排行子页需登录/RPC 超时，未取到完整榜单。"]
wr("百度指数", "百度指数 · 2026-10-09", "\n".join(b))

# ---- 知微事见 ----
zw = rd(os.path.join(B, "zhiwei.txt"))
idx = zw.find("事件列表")
zwb = zw[idx:] if idx > 0 else zw
b = ["## 知微事见 · 事件库（近 3 日高影响力事件）", "",
     "```", zwb.strip()[:6000], "```"]
wr("知微事见", "知微事见 · 2026-10-09", "\n".join(b))

# ---- IT之家 ----
b = ["## IT之家热榜", "", "| 排名 | 标题 |", "|:--:|------|"]
for i, r in enumerate(u["IT之家热榜"], 1):
    b.append(f"| {i} | {r} |")
b.append("")
b.append("> ⚠️ IT之家首页改版，本轮仅取到 3 条编辑精选标题（原 /0/ID/ID.htm 列表结构变更）。")
wr("IT之家热榜", "IT之家热榜 · 2026-10-09", "\n".join(b))

# ---- 澎湃 ----
b = ["## 澎湃新闻热榜", "", "| 排名 | 标题 |", "|:--:|------|"]
for i, r in enumerate(u["澎湃新闻热榜"], 1):
    b.append(f"| {i} | {re.sub(r'^推荐','',r)} |")
b.append("")
b.append("> ⚠️ 澎湃首页 SSR 可采条目偏少（9 条），WAF 限制深度抓取。")
wr("澎湃新闻热榜", "澎湃新闻热榜 · 2026-10-09", "\n".join(b))

# ---- 网易 ----
b = ["## 网易新闻热点排行", "", "| 排名 | 标题 |", "|:--:|------|"]
for i, r in enumerate(u["网易新闻热点排行"], 1):
    b.append(f"| {i} | {r} |")
wr("网易新闻热点排行", "网易新闻热点排行 · 2026-10-09", "\n".join(b))

# ---- InfoQ ----
iq = [x.strip() for x in rd(os.path.join(B, "infoq2.txt")).split("\n") if x.strip() and len(x.strip()) > 12]
b = ["## InfoQ 中国热点（首页编辑精选）", "", "| 排名 | 标题 |", "|:--:|------|"]
n = 0
for r in iq:
    if r.startswith("-") or r.startswith("0") or re.match(r"^[0-9]{2}\.[0-9]{2}", r):
        continue
    n += 1
    b.append(f"| {n} | {r} |")
b.append("")
b.append("> ⚠️ InfoQ `/hotlist` 接口本轮空返回，改采首页编辑精选，集中于大模型与 Agent 基建。")
wr("InfoQ中国热点", "InfoQ中国热点 · 2026-10-09", "\n".join(b))

# ---- 虎嗅 ----
hx = [x.strip() for x in rd(os.path.join(B, "huxiu.txt")).split("\n") if x.strip()]
seen, hx2 = set(), []
for r in hx:
    r = re.sub(r"^原创\s*", "", r)
    if r not in seen:
        seen.add(r)
        hx2.append(r)
b = ["## 虎嗅 48h 热文", "", "| 排名 | 标题 |", "|:--:|------|"]
for i, r in enumerate(hx2[:30], 1):
    b.append(f"| {i} | {r} |")
wr("虎嗅48h热文", "虎嗅48h热文 · 2026-10-09", "\n".join(b))

# ---- 品玩 ----
pw = [x.strip() for x in rd(os.path.join(B, "pingwest.txt")).split("\n") if x.strip()]
seen, pw2 = set(), []
for r in pw:
    if r not in seen:
        seen.add(r)
        pw2.append(r)
b = ["## 品玩一周精选", "", "| 排名 | 标题 |", "|:--:|------|"]
for i, r in enumerate(pw2[:25], 1):
    b.append(f"| {i} | {r} |")
wr("品玩一周精选", "品玩一周精选 · 2026-10-09", "\n".join(b))

# ---- 知乎想法话题 ----
zi = rd(os.path.join(B, "zhihu_idea.txt"))
b = ["## 知乎想法话题（创作中心）", "", "```", zi.strip()[:3500], "```",
     "", "> 参与度偏轻量（多为数千至数万人级），适合话题营销，不构成深度选题主源。"]
wr("知乎想法话题", "知乎想法话题 · 2026-10-09", "\n".join(b))

# ---- 知乎想法热榜 ----
b = ["## 知乎想法热榜", "", "**不可用**（HTTP 422 Unprocessable Entity · 连续第 23 日）", "",
     "> 平台侧接口持续下线，自 2026-09-17 起连续第 23 日不可用，已降级采「知乎想法话题」替代。"]
wr("知乎想法热榜", "知乎想法热榜 · 2026-10-09", "\n".join(b))

# ---- 小红书（WebSearch 兜底） ----
b = ["## 小红书热榜/话题（WebSearch 兜底）", "",
     "| 排名 | 话题/热点 | 类型 |", "|:--:|------|:--:|",
     "| 1 | 「繁荣主义」秋冬时尚趋势（浏览量 1.8 亿+） | 时尚 |",
     "| 2 | 「适我」居住趋势（讨论 626 万+，浏览量 20.4 亿+） | 家居 |",
     "| 3 | #穿汉服游神都（洛阳）单日新增笔记 120 万+ | 文旅 |",
     "| 4 | 国庆陪玩经济 / 搭子经济 / 孤独经济（#搭子自由） | 消费 |",
     "| 5 | 年轻人装修把茶几和床头柜「请」出家门 | 家居 |",
     "| 6 | 国庆「下次回来就是 2027 年了」返程共鸣 | 情感 |",
     "| 7 | 开封万岁山武侠城「NPC 自由行」 | 文旅 |",
     "| 8 | 山西古建巡礼 / 云冈石窟打卡 | 文旅 |",
     "| 9 | 「我的家庭旅行更像是打副本」 | 生活 |",
     "| 10 | 定格这一刻的日照金山 / 赛里木湖美景 | 旅行 |",
     "",
     "> ⚠️ 降级：小红书 explore 页在无头环境仅渲染登录页（需登录态），适配器未建，改采 WebSearch 公开趋势数据。"]
wr("小红书热榜话题", "小红书热榜/话题 · 2026-10-09", "\n".join(b), source="小红书热榜/话题")

print("DONE")
