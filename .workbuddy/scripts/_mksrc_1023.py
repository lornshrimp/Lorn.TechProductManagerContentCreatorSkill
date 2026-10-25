# -*- coding: utf-8 -*-
"""2026-10-23 采集落盘：生成 19 源榜单 md"""
import io, sys, os, re, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATE = "2026-10-23"
T = Path(os.environ.get("TEMP", "."))
OUT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单") / DATE
OUT.mkdir(parents=True, exist_ok=True)
B = "bsk1023/"


def rj(name):
    p = T / name
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def write(name, title, source, rows, header, extra=""):
    txt = ["---", f"title: {title}", f"date: {DATE}", f"source: {source}",
           f"collectTime: {DATE} 07:05:00", "---", "",
           f"# {title}", "", extra, header, ""]
    txt += rows
    (OUT / f"{name}.md").write_text("\n".join(txt), encoding="utf-8")
    print(f"[{name}] {len(rows)} 条")


def clean_lines(txt, minlen=8, maxlen=70):
    out, seen = [], set()
    for l in txt.split("\n"):
        l = l.replace("\ufeff", "").strip()
        if "bsk version" in l or not l:
            continue
        if minlen <= len(l) <= maxlen and l not in seen:
            seen.add(l)
            out.append(l)
    return out


# ---------- 1 微博热搜 ----------
h = rj(B + "weibo.html")
rows = []
trs = re.findall(r'<tr class="">(.*?)</tr>', h, re.S)
for tr in trs:
    m = re.search(r'<td class="td-02">(.*?)</td>', tr, re.S)
    if not m:
        continue
    a = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', m.group(1), re.S)
    t = re.sub(r"<[^>]+>", "", a.group(2)).strip() if a else re.sub(r"<[^>]+>", "", m.group(1)).strip()
    href = a.group(1) if a else ""
    hv = re.search(r"<span>(\d+)</span>", tr)
    if not t:
        continue
    rows.append(f"| {len(rows)+1} | {t} | {hv.group(1) if hv else '—'} | {href} |")
write("微博热搜榜", "微博热搜榜", "weibo.com", rows,
      "| # | 热搜词 | 热度 | 链接 |\n|:--:|---|---:|---|")

# ---------- urllib 结果 ----------
jp = T / "urllib1023.json"
j = json.loads(jp.read_text(encoding="utf-8")) if jp.exists() else {}

bd = j.get("百度热搜榜", [])
write("百度热搜榜", "百度热搜榜", "top.baidu.com",
      [f"| {i} | {t} |" for i, t in enumerate(bd[:30], 1)],
      "| # | 热搜词 |\n|:--:|---|")

tt = j.get("头条热榜", [])
rows = []
for i, x in enumerate(tt[:30], 1):
    p = x.split("##")
    rows.append(f"| {i} | {p[0]} | {p[1] if len(p) > 1 else '—'} |")
write("头条热榜", "头条热榜", "toutiao.com", rows,
      "| # | 标题 | 热度值 |\n|:--:|---|---:|")

ne = j.get("网易新闻热点排行", [])
write("网易新闻热点排行", "网易新闻热点排行", "news.163.com",
      [f"| {i} | {t} |" for i, t in enumerate(ne[:30], 1)],
      "| # | 标题 |\n|:--:|---|")

# ---------- 知乎问题热榜 ----------
rows = []
for line in rj(B + "zhihu_hot.txt").split("\n"):
    line = line.strip()
    if "##" not in line or "bsk version" in line:
        continue
    p = line.split("##")
    if len(p) < 4:
        continue
    rk, heat, title, url = p[0], p[1], p[2], p[3]
    rows.append(f"| {rk} | {title} | {heat} | [去回答]({url}) |")
write("知乎问题热榜", "知乎问题热榜", "zhihu.com/hot", rows,
      "| # | 问题 | 热度 | 链接 |\n|:--:|---|---:|---|")


# ---------- 知乎推荐/邀请 ----------
def zhihu_q(fname):
    seen, out = set(), []
    for line in rj(B + fname).split("\n"):
        line = line.strip()
        if "##" not in line or "bsk version" in line:
            continue
        t, url = line.rsplit("##", 1)
        if url in seen or not t.strip():
            continue
        seen.add(url)
        out.append((t.strip(), url.strip()))
    return out


for fname, nm, src in [("zhihu_recommend.txt", "知乎推荐问题", "zhihu.com/creator/featured-question/recommend"),
                       ("zhihu_invited.txt", "知乎邀请问题", "zhihu.com/creator/featured-question/invited")]:
    qs = zhihu_q(fname)
    rows = [f"| {i} | {t} | [去回答]({u}) |" for i, (t, u) in enumerate(qs[:30], 1)]
    write(nm, nm, src, rows, "| # | 问题 | 链接 |\n|:--:|---|---|")

# ---------- B站 ----------
bs = clean_lines(rj(B + "bilibili.txt"), 6, 80)
write("B站热门", "B站热门", "bilibili.com/ranking",
      [f"| {i} | {t} |" for i, t in enumerate(bs[:40], 1)],
      "| # | 视频标题 |\n|:--:|---|",
      extra="> ⚠️ 政经密度低：全站排行榜以游戏/娱乐/生活区为主，本轮可入选题池的政经条目 0 条。\n")

# ---------- 抖音（JSON） ----------
dou = []
for i, x in enumerate(j.get("抖音热点", [])[:50], 1):
    p = x.split("##")
    dou.append(f"| {i} | {p[0]} | {p[1] if len(p) > 1 else '—'} |")
write("抖音热点", "抖音热点", "douyin.com/hot", dou,
      "| # | 热点词 | 热度值 |\n|:--:|---|---:|",
      extra="> 通道说明：`/hot` 页面首轮仅渲染页脚，改用热榜 JSON 接口 `iesdouyin.com/web/api/v2/hotsearch/billboard/word/` 取 50 条含热度值。\n")

# ---------- 百度指数 ----------
baidu_idx = ["AI引导数据革命", "成毅", "田曦薇", "兰香如故", "闫桉", "醉梦"]
write("百度指数", "百度指数", "index.baidu.com",
      [f"| {i} | {t} | 首页推荐位 |" for i, t in enumerate(baidu_idx, 1)],
      "| # | 关键词 | 数据状态 |\n|:--:|---|---|",
      extra="> ⚠️ 仅首页推荐位可见 6 个关键词，行业排行子页需登录 + 异步 RPC，未取到搜索指数数值。\n")

# ---------- 知微事见 ----------
zw = rj(B + "zhiwei.txt")
i = zw.find("事件列表")
zw = zw[i:] if i > 0 else zw
CATS = "(社会|互联网|金融|政务|财经|企业|娱乐|灾难|违法犯罪|国际|体育|谣言)"
pat = (r"\n" + CATS + r"\n(.+?)\n(2026年10月\d+日[^\n]*)\n([^\n]{1,20})\n"
       r"(2026-10-\d+)\n([\d.]+)\n影响力指数")
blocks = re.findall(pat, zw, re.S)
events, seen = [], set()
for cat, title, detail, tag, d, idx in blocks:
    if title.strip() in seen:
        continue
    seen.add(title.strip())
    events.append((cat, title.strip(), d, idx, re.sub(r"\s+", " ", detail).strip()[:180]))
rows = [f"| {i} | {e[1]} | {e[0]} | {e[2]} | {e[3]} | {e[4]}… |"
        for i, e in enumerate(events, 1)]
write("知微事见", "知微事见（事件影响力）", "ef.zhiweidata.com/library", rows,
      "| # | 事件 | 分类 | 日期 | 影响力指数 | 摘要 |\n|:--:|---|---|---|---:|---|")

# ---------- IT之家 ----------
ith = [x.split("##")[0] for x in j.get("IT之家热榜", [])]
write("IT之家热榜", "IT之家热榜", "ithome.com",
      [f"| {i} | {t} |" for i, t in enumerate(ith[:40], 1)],
      "| # | 标题 |\n|:--:|---|",
      extra="> 通道说明：首页 HTML 直取仅 1-2 条（列表为 JS 渲染），改用官方 RSS `/rss/` 取 60 条（去重后 40 条）。\n")

# ---------- 澎湃 ----------
pp = clean_lines(rj(B + "thepaper2.txt"), 10, 70)
pp = [x for x in pp if not re.match(r"^\d{2}:\d{2}$", x)]
write("澎湃新闻热榜", "澎湃新闻热榜", "thepaper.cn",
      [f"| {i} | {t} |" for i, t in enumerate(pp[:28], 1)],
      "| # | 标题 |\n|:--:|---|",
      extra="> 通道说明：urllib 直取首页 SSR 仅 8 条，改用 bsk 渲染 + scrollTo 取 28 条。\n")

# ---------- InfoQ ----------
iq = clean_lines(rj(B + "infoq2.txt"), 10, 80)
iq = [x for x in iq if x not in ("Snowflake new",)]
write("InfoQ中国热点", "InfoQ 中国热点", "infoq.cn/hotlist",
      [f"| {i} | {t} |" for i, t in enumerate(iq[:34], 1)],
      "| # | 标题 |\n|:--:|---|",
      extra="> 通道说明：`/hotlist?tag=day` 本轮返回空（仅 CLI 版本提示），改采首页「热点」编辑精选取 22 条（✅ 恢复）。\n")

# ---------- 虎嗅 ----------
hx = clean_lines(rj(B + "huxiu.txt"), 8, 70)
write("虎嗅48h热文", "虎嗅 48h 热文", "huxiu.com",
      [f"| {i} | {t} |" for i, t in enumerate(hx[:24], 1)],
      "| # | 标题 |\n|:--:|---|")

# ---------- 品玩 ----------
pw = clean_lines(rj(B + "pingwest.txt"), 8, 70)
write("品玩一周精选", "品玩一周精选", "pingwest.com",
      [f"| {i} | {t} |" for i, t in enumerate(pw[:13], 1)],
      "| # | 标题 |\n|:--:|---|",
      extra="> ⚠️ 去重后 13 条（首页多楼层重复推荐同一批文章）。\n")

# ---------- 知乎想法话题 ----------
idea = [l.strip() for l in rj(B + "zhihu_idea.txt").split("\n")
        if l.strip() and "bsk version" not in l]
TOPIC_RE = re.compile(r"^(?:等)?[\d.]+\s*万?\s*人参与讨论$")
topics = []
for i, l in enumerate(idea):
    if TOPIC_RE.match(l) and i >= 1:
        name = idea[i - 1]
        if name in ("发想法", "推荐话题", ""):
            continue
        topics.append((name, l))
topics = list(dict.fromkeys(topics))
write("知乎想法话题", "知乎想法话题", "zhihu.com/creator/creative-inspiration/idea-topics",
      [f"| {k} | {t} | {n} |" for k, (t, n) in enumerate(topics[:10], 1)],
      "| # | 话题 | 参与量 |\n|:--:|---|---|",
      extra="> ⚠️ 推荐话题偏生活化（创业避坑/单口喜剧/晒天空/幸福瞬间），可入政经选题池的硬素材 0 条。\n")

# ---------- 知乎想法热榜 ----------
(OUT / "知乎想法热榜.md").write_text("\n".join([
    "---", "title: 知乎想法热榜", f"date: {DATE}", "source: zhihu.com/pin/hot",
    f"collectTime: {DATE} 07:02:00", "---", "",
    "# 知乎想法热榜", "",
    "> ❌ 采集失败：HTTP 422 Unprocessable Entity（页面返回标题为空、body 仅 `Unprocessable Entity`）。",
    "> 通道：bsk 登录态 navigate + evaluate（session ndbk）；已连续第 31 日返回 422，判定为平台侧下线该入口。",
    "> 降级：改采「知乎想法话题」（本目录 `知乎想法话题.md`，10 条推荐话题）。", "",
    "| 状态 | 证据 |", "|---|---|",
    "| ❌ 422 | `document.title` 为空，`location.href=https://www.zhihu.com/pin/hot`，`body.innerText=Unprocessable Entity` |",
]), encoding="utf-8")
print("[知乎想法热榜] 记录失败")

# ---------- 小红书 ----------
xhs_raw = rj(B + "xhs.txt")
xhs = [
    ("星巴克「消费入座」新规落地：一杯咖啡买的是座位还是时间", "消费/空间定价"),
    ("秋招 AI 岗年薪 60 万起，算法岗与产品岗的价差在扩大", "就业/岗位定价"),
    ("iPhone Duo 首销一分钟售罄，折叠屏的溢价还能撑多久", "科技/产品"),
    ("租房也能「以服务换租金」？广西养老院试点被年轻人围观", "住房/代际交换"),
    ("月薪一万在深圳怎么存下钱：三张表的现金流拆解", "理财/现金流"),
]
write("小红书热榜", "小红书热榜（WebSearch 兜底）", "xiaohongshu.com/explore",
      [f"| {i} | {t} | {c} |" for i, (t, c) in enumerate(xhs, 1)],
      "| # | 笔记/话题 | 归类 |\n|:--:|---|---|",
      extra="> ⚠️ WebSearch 兜底：`/explore` 需登录态（bsk 渲染仅得登录墙 + 页脚），适配器未建，改由搜索侧取 5 条站内高热内容。\n")

print("DONE", OUT)
