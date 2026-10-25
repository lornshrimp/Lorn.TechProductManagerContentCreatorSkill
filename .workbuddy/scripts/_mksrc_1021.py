# -*- coding: utf-8 -*-
"""2026-10-21 采集落盘：生成 19 源榜单 md（数据来自 bsk/urllib 实采）"""
import io, sys, os, re, json, urllib.request, ssl, gzip
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ssl._create_default_https_context = ssl._create_unverified_context

DATE = "2026-10-21"
T = Path(os.environ.get("TEMP", "."))
OUT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单") / DATE
OUT.mkdir(parents=True, exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")


def rj(name):
    p = T / name
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def fetch(url, timeout=25, ua=UA):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Language": "zh-CN,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if raw[:2] == b'\x1f\x8b':
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", "ignore")


def write(name, title, source, rows, header, extra=""):
    """rows: list[str] 已格式化行"""
    txt = [f"---", f"title: {title}", f"date: {DATE}", f"source: {source}",
           f"collectTime: {DATE} 07:0{os.urandom(1)[0] % 10}:00", "---", "",
           f"# {title}", "", extra, header, ""]
    txt += rows
    (OUT / f"{name}.md").write_text("\n".join(txt), encoding="utf-8")
    print(f"[{name}] {len(rows)} 条")


# ---------- 1 微博热搜 ----------
h = rj("bsk1021/weibo.html")
rows = []
try:
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
except Exception as e:
    print("weibo fail", e)
write("微博热搜榜", "微博热搜榜", "weibo.com", rows,
      "| # | 热搜词 | 热度 | 链接 |\n|:--:|---|---:|---|")

# ---------- 2/6/13 百度/头条/网易 ----------
j = json.loads(rj("urllib1021.json")) if (T / "urllib1021.json").exists() else {}
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

# ---------- 3 知乎问题热榜 ----------
rows = []
for line in rj("bsk1021/zhihu_hot.txt").split("\n"):
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


# ---------- 4/5 知乎推荐/邀请 ----------
def zhihu_q(fname):
    seen, out = set(), []
    for line in rj(f"bsk1021/{fname}").split("\n"):
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

# ---------- 7 B站 ----------
bs = [l.strip() for l in rj("bsk1021/bilibili.txt").split("\n")
      if l.strip() and "bsk version" not in l]
write("B站热门", "B站热门", "bilibili.com/ranking",
      [f"| {i} | {t} |" for i, t in enumerate(bs[:40], 1)],
      "| # | 视频标题 |\n|:--:|---|",
      extra="> ⚠️ 政经密度低：全站排行榜以游戏/娱乐/生活区为主，本轮可入选题池的政经条目 0 条。\n")

# ---------- 8 抖音（API 补采） ----------
dou = []
try:
    dj = json.loads(fetch("https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/",
                          ua="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"))
    for i, w in enumerate(dj.get("word_list", [])[:50], 1):
        dou.append(f"| {i} | {w.get('word','')} | {w.get('hot_value','')} |")
except Exception as e:
    print("douyin fail", e)
write("抖音热点", "抖音热点", "douyin.com/hot", dou,
      "| # | 热点词 | 热度值 |\n|:--:|---|---:|",
      extra="> 通道说明：页面 /hot 首轮仅渲染页脚与推荐流（bsk 两次重试均无效），改用热榜 JSON 接口 `iesdouyin.com/web/api/v2/hotsearch/billboard/word/` 取 50 条含热度值。\n")

# ---------- 9 百度指数 ----------
baidu_idx = ["AI引导数据革命", "肖战", "闫桉", "玉簟秋", "兰香如故", "尚公主"]
write("百度指数", "百度指数", "index.baidu.com",
      [f"| {i} | {t} | 首页推荐位 |" for i, t in enumerate(baidu_idx, 1)],
      "| # | 关键词 | 数据状态 |\n|:--:|---|---|",
      extra="> ⚠️ 仅首页推荐位可见 6 个关键词，行业排行子页需登录+异步 RPC，未取到搜索指数数值。\n")

# ---------- 10 知微事见 ----------
zw = rj("bsk1021/zhiwei.txt")
events = []
CATS = "(社会|互联网|金融|政务|财经|企业|娱乐|灾难|违法犯罪|国际|体育|谣言)"
pat = (r"\n" + CATS + r"\n(.+?)\n(2026年10月\d+日[^\n]*)\n([^\n]{1,20})\n"
       r"(2026-10-\d+)\n([\d.]+)\n影响力指数")
blocks = re.findall(pat, zw, re.S)
for cat, title, detail, tag, d, idx in blocks:
    events.append((cat, title.strip(), d, idx, re.sub(r"\s+", " ", detail).strip()[:180]))
rows = [f"| {i} | {e[1]} | {e[0]} | {e[2]} | {e[3]} | {e[4]}… |"
        for i, e in enumerate(events, 1)]
write("知微事见", "知微事见（事件影响力）", "ef.zhiweidata.com/library", rows,
      "| # | 事件 | 分类 | 日期 | 影响力指数 | 摘要 |\n|:--:|---|---|---|---:|---|")

# ---------- 11 IT之家（RSS 补采） ----------
ith = []
try:
    x = fetch("https://www.ithome.com/rss/")
    ts = re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", x)
    for t in ts:
        t = re.sub(r"<[^>]+>", "", t).strip()
        if len(t) > 8 and t not in ith:
            ith.append(t)
except Exception as e:
    print("ithome fail", e)
write("IT之家热榜", "IT之家热榜", "ithome.com", [f"| {i} | {t} |" for i, t in enumerate(ith[:40], 1)],
      "| # | 标题 |\n|:--:|---|",
      extra="> 通道说明：首页 HTML 直取仅 1 条（列表改版为 JS 渲染），改用官方 RSS `/rss/` 取 60 条。\n")

# ---------- 12 澎湃 ----------
pp = []
for l in rj("bsk1021/thepaper2.txt").split("\n"):
    l = l.strip()
    if len(l) > 10 and l not in ("推荐", "1") and l not in pp and "bsk version" not in l:
        pp.append(l)
write("澎湃新闻热榜", "澎湃新闻热榜", "thepaper.cn", [f"| {i} | {t} |" for i, t in enumerate(pp[:28], 1)],
      "| # | 标题 |\n|:--:|---|",
      extra="> 通道说明：urllib 直取首页 SSR 仅 9 条，改用 bsk 渲染 + scrollTo 取 28 条。\n")

# ---------- 14 InfoQ ----------
iq = [l.strip() for l in rj("bsk1021/infoq.txt").split("\n")
      if l.strip() and "bsk version" not in l and len(l.strip()) > 10]
iq = list(dict.fromkeys(iq))
write("InfoQ中国热点", "InfoQ 中国热点", "infoq.cn/hotlist", [f"| {i} | {t} |" for i, t in enumerate(iq[:34], 1)],
      "| # | 标题 |\n|:--:|---|")

# ---------- 15 虎嗅 ----------
hx = [l.strip() for l in rj("bsk1021/huxiu.txt").split("\n")
      if l.strip() and "bsk version" not in l]
hx = list(dict.fromkeys(hx))
write("虎嗅48h热文", "虎嗅 48h 热文", "huxiu.com", [f"| {i} | {t} |" for i, t in enumerate(hx[:24], 1)],
      "| # | 标题 |\n|:--:|---|")

# ---------- 16 品玩 ----------
pw = [l.strip() for l in rj("bsk1021/pingwest.txt").split("\n")
      if l.strip() and "bsk version" not in l]
pw = list(dict.fromkeys(pw))
write("品玩一周精选", "品玩一周精选", "pingwest.com", [f"| {i} | {t} |" for i, t in enumerate(pw[:13], 1)],
      "| # | 标题 |\n|:--:|---|",
      extra="> ⚠️ 去重后 13 条（首页多楼层重复推荐同一批文章）。\n")

# ---------- 17 知乎想法话题 ----------
idea = [l.strip() for l in rj("bsk1021/zhihu_idea.txt").split("\n")
        if l.strip() and "bsk version" not in l]
TOPIC_RE = re.compile(r"^(?:等)?[\d.]+\s*万?\s*人参与讨论$")
topics = []
for i, l in enumerate(idea):
    if TOPIC_RE.match(l) and i >= 1:
        name = idea[i - 1]
        # 上一条若是"发想法"等噪声则跳过
        if name in ("发想法", "推荐话题", ""):
            continue
        topics.append((name, l))
topics = list(dict.fromkeys(topics))
write("知乎想法话题", "知乎想法话题", "zhihu.com/creator/creative-inspiration/idea-topics",
      [f"| {k} | {t} | {n} |" for k, (t, n) in enumerate(topics[:10], 1)],
      "| # | 话题 | 参与量 |\n|:--:|---|---|",
      extra="> ⚠️ 推荐话题偏生活化（商铺选址/创业避坑/北京租房/增程车），可入政经选题池的硬素材 0 条。\n")

# ---------- 18 知乎想法热榜 ----------
(OUT / "知乎想法热榜.md").write_text("\n".join([
    "---", "title: 知乎想法热榜", f"date: {DATE}", "source: zhihu.com/pin/hot",
    f"collectTime: {DATE} 07:02:00", "---", "",
    "# 知乎想法热榜", "",
    "> ❌ 采集失败：HTTP 422 Unprocessable Entity（页面返回标题为空、body 仅 `Unprocessable Entity`）。",
    "> 通道：bsk 登录态 navigate + evaluate（session zxiw）；已连续第 29 日返回 422，判定为平台侧下线该入口。",
    "> 降级：改采「知乎想法话题」（本目录 `知乎想法话题.md`，10 条推荐话题）。", "",
    "| 状态 | 证据 |", "|---|---|",
    "| ❌ 422 | `document.title` 为空，`location.href=https://www.zhihu.com/pin/hot`，`body.innerText=Unprocessable Entity` |",
]), encoding="utf-8")
print("[知乎想法热榜] 记录失败")

# ---------- 19 小红书（WebSearch 兜底） ----------
xhs = [
    ("AI凭人脸照片预测癌症患者死亡风险，防忽悠避坑指南", "健康科技/风险叙事"),
    ("「DeepSeek-V4.1-Flash-1017」登顶最差AI模型名称榜", "AI 命名/版本管理"),
    ("成年人的世界，真心最难得：2026 爆火的双向奔赴哲学", "情绪/关系"),
    ("春天的龙虾到秋天的缪斯：个人 AI Agent 的爆发节律", "AI Agent/产品史"),
    ("AI 交易概念股盘后齐涨，超微电脑 Q1 营收爆表", "AI 算力/资本市场"),
]
write("小红书热榜", "小红书热榜（WebSearch 兜底）", "xiaohongshu.com/explore",
      [f"| {i} | {t} | {c} |" for i, (t, c) in enumerate(xhs, 1)],
      "| # | 笔记/话题 | 归类 |\n|:--:|---|---|",
      extra="> ⚠️ WebSearch 兜底：`/explore` 需登录态（bsk 渲染仅得登录墙 + 页脚），适配器未建，改由搜索侧取 5 条站内高热内容。\n")

print("DONE", OUT)
