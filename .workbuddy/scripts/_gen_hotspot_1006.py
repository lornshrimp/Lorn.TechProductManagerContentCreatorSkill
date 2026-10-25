# -*- coding: utf-8 -*-
"""2026-10-06 采集结果落盘：各源 .md + 融合榜单"""
import os, re, json, io

BASE = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体"
OUTD = os.path.join(BASE, "hotspot", "榜单", "2026-10-06")
os.makedirs(OUTD, exist_ok=True)
T = os.path.join(os.environ.get("TEMP", ""), "bsk1006")
DATE = "2026-10-06"
CT = "2026-10-06 08:45"


def w(name, fm, body):
    p = os.path.join(OUTD, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write("---\n" + fm.strip() + "\n---\n\n" + body.strip() + "\n")
    print(f"OK {name} {len(body)} chars")


def rd(p):
    try:
        return open(p, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""


# ---------- 1 微博热搜榜 ----------
weibo_raw = rd(os.path.join(T, "weibo_parsed.json"))
weibo = json.loads(weibo_raw) if weibo_raw.strip() else []
wb_rows = []
for i, x in enumerate(weibo, 1):
    wb_rows.append(f"| {i} | {x} |")
w("微博热搜榜.md", f"""title: 微博热搜榜 · {DATE}
date: {DATE}
source: 微博热搜榜
collectTime: {CT}""", "## 微博热搜榜（TOP 48）\n\n| 排名 | 热搜词 |\n|------|--------|\n" + "\n".join(wb_rows))

# ---------- 2 百度热搜榜 ----------
fix = json.load(open(os.path.join(BASE, ".workbuddy", "scripts", "_u1006_fix.json"), encoding="utf-8"))
baidu = fix["百度热搜榜"]
bd_rows = [f"| {i} | {x} |" for i, x in enumerate(baidu, 1)]
w("百度热搜榜.md", f"""title: 百度热搜榜 · {DATE}
date: {DATE}
source: 百度热搜榜
collectTime: {CT}""", "## 百度热搜榜（TOP 30）\n\n| 排名 | 热搜词 |\n|------|--------|\n" + "\n".join(bd_rows))

# ---------- 3 知乎问题热榜 ----------
zh_rows = []
for line in rd(os.path.join(T, "zhihu_hot.txt")).splitlines():
    parts = line.split("##")
    if len(parts) >= 4 and "zhihu.com/question" in parts[3]:
        zh_rows.append(f"| {parts[0]} | {parts[1]} | {parts[2]} | [去回答]({parts[3]}) |")
w("知乎问题热榜.md", f"""title: 知乎问题热榜 · {DATE}
date: {DATE}
source: 知乎问题热榜
collectTime: {CT}""", "## 知乎问题热榜（TOP 30）\n\n| 排名 | 热度 | 问题 | 链接 |\n|------|------|------|------|\n" + "\n".join(zh_rows))

# ---------- 4 知乎推荐问题 ----------
recs = []
for line in rd(os.path.join(T, "zhihu_recommend2.txt")).splitlines():
    if "##http" in line:
        t, h = line.split("##", 1)
        t = t.strip()
        if t and (t, h) not in recs:
            recs.append((t, h))
rec_rows = [f"| {i} | {t} | [去回答]({h}) |" for i, (t, h) in enumerate(recs, 1)]
w("知乎推荐问题.md", f"""title: 知乎推荐问题 · {DATE}
date: {DATE}
source: 知乎推荐问题
collectTime: {CT}""", f"## 知乎推荐问题（{len(recs)} 条）\n\n| 序号 | 问题 | 链接 |\n|------|------|------|\n" + "\n".join(rec_rows))

# ---------- 5 知乎邀请问题 ----------
inv = []
for line in rd(os.path.join(T, "zhihu_invited.txt")).splitlines():
    if "##http" in line:
        t, h = line.split("##", 1)
        t = t.strip()
        if t and (t, h) not in inv:
            inv.append((t, h))
inv_rows = [f"| {i} | {t} | [去回答]({h}) |" for i, (t, h) in enumerate(inv, 1)]
w("知乎邀请问题.md", f"""title: 知乎邀请问题 · {DATE}
date: {DATE}
source: 知乎邀请问题
collectTime: {CT}""", f"## 知乎邀请问题（{len(inv)} 条）\n\n| 序号 | 问题 | 链接 |\n|------|------|------|\n" + "\n".join(inv_rows))

# ---------- 6 头条热榜 ----------
tt = json.load(open(os.path.join(BASE, ".workbuddy", "scripts", "_u1006_result.json"), encoding="utf-8"))["results"]["头条热榜_json"]
tt_rows = []
for x in tt:
    p = x.split("\t")
    if len(p) >= 3:
        tt_rows.append(f"| {p[0]} | {p[1]} | {p[2]} |")
w("头条热榜.md", f"""title: 头条热榜 · {DATE}
date: {DATE}
source: 头条热榜
collectTime: {CT}""", "## 头条热榜（TOP 30）\n\n| 排名 | 标题 | 热度值 |\n|------|------|--------|\n" + "\n".join(tt_rows))

# ---------- 7 B站热门 ----------
bili = [l.strip() for l in rd(os.path.join(T, "bilibili.txt")).splitlines() if l.strip()]
bili = [x for x in bili if 6 < len(x) < 70]
b_rows = [f"| {i} | {x} |" for i, x in enumerate(bili, 1)]
w("B站热门.md", f"""title: B站热门 · {DATE}
date: {DATE}
source: B站热门
collectTime: {CT}""", f"## B站热门（{len(bili)} 条）\n\n| 排名 | 标题 |\n|------|------|\n" + "\n".join(b_rows))

# ---------- 8 抖音热点 ----------
dy = []
for l in rd(os.path.join(T, "douyin.txt")).splitlines():
    # note: retried output was printed, re-capture from file if present
    pass
dy_retry = """理政纪｜古树新翠
华为与高通达成专利许可协议
你说得对人是应该多出去走走
智慧交通助力国庆假期出行
国庆假期速度belike
出发吧路上都是同行人
冷空气已到货广东
听潮阁启冬眠国庆打卡手势舞
出游报复性穿搭人格
世界如此辽阔怎么走都不算错
心与心的朋友我不认识了
挑战看生化危机不被吓到惊跳
孙颖莎3:1战胜叶伊恬晋级
跑步真的伤膝盖吗
这些涉假期网络传言不要信
明珍珍死刑前画面曝光
一诺亚运会后的一封家书
用一张图证明你回到家乡了
白应苍临刑前画面曝光
国安部警示违规携带血样出境危害
威姆斯101:94击败白晶
郑钦文闯入中网16强
知名演员何麦去世
余红旧事郝洁拿老公换救命钱
国庆感受黑土地带来的震撼
千户苗寨落地签拍了
李一桐自曝曾被骗钱和感情
现在你再也推不开我了
川西旅行已渐入佳境
侯明昊Holy Moly展示网速""".splitlines()
dy = [x.strip() for x in dy_retry if x.strip()]
d_rows = [f"| {i} | {x} |" for i, x in enumerate(dy, 1)]
w("抖音热点.md", f"""title: 抖音热点 · {DATE}
date: {DATE}
source: 抖音热点
collectTime: {CT}""", f"## 抖音热点（{len(dy)} 条）\n\n| 排名 | 标题 |\n|------|------|\n" + "\n".join(d_rows))

# ---------- 10 知微事见 ----------
zw = rd(os.path.join(T, "zhiwei2.txt"))
# 提取 事件名 + 日期 + 影响力指数 + 分类 四行组
lines = [l.strip() for l in zw.splitlines() if l.strip()]
ev = []
i = 0
while i < len(lines):
    l = lines[i]
    if re.match(r"^20\d{2}-\d{2}-\d{2}$", l) and i >= 1:
        name = lines[i - 1]
        idx = lines[i + 1] if i + 1 < len(lines) and re.match(r"^[\d.]+$", lines[i + 1]) else ""
        cat = lines[i + 2] if i + 2 < len(lines) else ""
        if 4 < len(name) < 40:
            ev.append((name, l, idx, cat))
    i += 1
ev_rows = [f"| {i} | {n} | {d} | {x} | {c} |" for i, (n, d, x, c) in enumerate(ev, 1)]
w("知微事见.md", f"""title: 知微事见 · {DATE}
date: {DATE}
source: 知微事见
collectTime: {CT}""", f"## 知微事见·事件库（{len(ev)} 条）\n\n| 序号 | 事件 | 日期 | 影响力指数 | 分类 |\n|------|------|------|-----------|------|\n" + "\n".join(ev_rows))

# ---------- 11 IT之家热榜 ----------
ith = json.load(open(os.path.join(BASE, ".workbuddy", "scripts", "_u1006_result.json"), encoding="utf-8"))["results"]["IT之家热榜"]
ith_rows = [f"| {i} | {x} |" for i, x in enumerate(ith, 1)]
w("IT之家热榜.md", f"""title: IT之家热榜 · {DATE}
date: {DATE}
source: IT之家热榜
collectTime: {CT}""", f"## IT之家热榜（{len(ith)} 条）\n\n| 排名 | 标题 |\n|------|------|\n" + "\n".join(ith_rows))

# ---------- 12 澎湃新闻热榜 ----------
pp = fix["澎湃新闻热榜"]
pp_rows = [f"| {i} | {x} |" for i, x in enumerate(pp, 1)]
w("澎湃新闻热榜.md", f"""title: 澎湃新闻热榜 · {DATE}
date: {DATE}
source: 澎湃新闻热榜
collectTime: {CT}""", f"## 澎湃新闻热榜（{len(pp)} 条）\n\n| 排名 | 标题 |\n|------|------|\n" + "\n".join(pp_rows))

# ---------- 13 网易新闻热点排行 ----------
n163 = json.load(open(os.path.join(BASE, ".workbuddy", "scripts", "_u1006_result.json"), encoding="utf-8"))["results"]["网易新闻热点排行"]
n_rows = [f"| {i} | {x} |" for i, x in enumerate(n163, 1)]
w("网易新闻热点排行.md", f"""title: 网易新闻热点排行 · {DATE}
date: {DATE}
source: 网易新闻热点排行
collectTime: {CT}""", f"## 网易新闻热点排行（{len(n163)} 条）\n\n| 排名 | 标题 |\n|------|------|\n" + "\n".join(n_rows))

# ---------- 14 InfoQ中国热点 ----------
iq = [l.strip() for l in rd(os.path.join(T, "infoq.txt")).splitlines() if l.strip()]
iq = [x for x in iq if 10 < len(x) < 90]
iq_rows = [f"| {i} | {x} |" for i, x in enumerate(iq, 1)]
w("InfoQ中国热点.md", f"""title: InfoQ中国热点 · {DATE}
date: {DATE}
source: InfoQ中国热点
collectTime: {CT}""", f"## InfoQ中国热点（{len(iq)} 条）\n\n| 排名 | 标题 |\n|------|------|\n" + "\n".join(iq_rows))

# ---------- 15 虎嗅48h热文 ----------
hx = [l.strip() for l in rd(os.path.join(T, "huxiu.txt")).splitlines() if l.strip()]
seen = []
for x in hx:
    if x not in seen:
        seen.append(x)
hx_rows = [f"| {i} | {x} |" for i, x in enumerate(seen, 1)]
w("虎嗅48h热文.md", f"""title: 虎嗅48h热文 · {DATE}
date: {DATE}
source: 虎嗅48h热文
collectTime: {CT}""", f"## 虎嗅48h热文（{len(seen)} 条）\n\n| 排名 | 标题 |\n|------|------|\n" + "\n".join(hx_rows))

# ---------- 16 品玩一周精选 ----------
pw = [l.strip() for l in rd(os.path.join(T, "pingwest.txt")).splitlines() if l.strip()]
seen = []
for x in pw:
    if x not in seen:
        seen.append(x)
pw_rows = [f"| {i} | {x} |" for i, x in enumerate(seen, 1)]
w("品玩一周精选.md", f"""title: 品玩一周精选 · {DATE}
date: {DATE}
source: 品玩一周精选
collectTime: {CT}""", f"## 品玩一周精选（{len(seen)} 条）\n\n| 排名 | 标题 |\n|------|------|\n" + "\n".join(pw_rows))

# ---------- 17 知乎想法话题 ----------
idea = [l.strip() for l in rd(os.path.join(T, "zhihu_idea2.txt")).splitlines() if l.strip()]
idea = [x for x in idea if 4 < len(x) < 40 and not re.match(r"^(Lv|创作中心|消息|私信|发布内容|创作主页|等你来答|推荐问题|想法话题|内容管理|评论管理|创作分|关注者分析)", x)]
seen = []
for x in idea:
    if x not in seen:
        seen.append(x)
id_rows = [f"| {i} | {x} |" for i, x in enumerate(seen, 1)]
w("知乎想法话题.md", f"""title: 知乎想法话题 · {DATE}
date: {DATE}
source: 知乎想法话题
collectTime: {CT}""", f"## 知乎想法话题（{len(seen)} 条）\n\n| 序号 | 话题/内容 |\n|------|-----------|\n" + "\n".join(id_rows))

# ---------- 18 知乎想法热榜 ----------
w("知乎想法热榜.md", f"""title: 知乎想法热榜 · {DATE}
date: {DATE}
source: 知乎想法热榜
collectTime: {CT}
status: 不可用""", """## 知乎想法热榜 · 采集失败

**状态**：❌ 不可用（HTTP 422 Unprocessable Entity）

`https://www.zhihu.com/pin/hot` 返回 `Unprocessable Entity`，页面主体为空。该接口自 2026-09-11 起持续不可用（连续第 20 日），已由「知乎想法话题」源补充替代。

采集时间：{CT}""".replace("{CT}", CT))

# ---------- 19 百度指数 ----------
w("百度指数.md", f"""title: 百度指数 · {DATE}
date: {DATE}
source: 百度指数
collectTime: {CT}
status: 部分可用""", """## 百度指数 · 采集（首页可见词）

⚠️ 百度指数 `index.baidu.com` 需登录态且数据由 RPC 异步加载，本次未登录仅采到首页推荐词（0 条完整行业排行）。

| 序号 | 推荐词 |
|------|--------|
| 1 | 尚公主 |
| 2 | 嫁金钗 |
| 3 | 小城良方 |
| 4 | 王俊凯 |
| 5 | 田曦薇 |

> 行业排行子页 RPC 超时，品牌榜无当日数据。降级：仅记录首页可见热词。""")

print("DONE all source files")
print("DIR:", OUTD)
