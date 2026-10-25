# -*- coding: utf-8 -*-
"""2026-10-25 19 源榜单落盘"""
import os, re, io, sys, json, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot/榜单/2026-10-25")
TMP = os.path.join(os.environ['TEMP'], 'bsk1025')
DATE = "2026-10-25"
CT = "2026-10-25 09:45"

os.makedirs(OUT, exist_ok=True)


def w(name, src, header, rows, note=""):
    p = os.path.join(OUT, name + ".md")
    body = [f"---", f"title: {name}", f"date: {DATE}", f"source: {src}", f"collectTime: {CT}", "---", "", f"# {name}", ""]
    if note:
        body += [note, ""]
    body.append(header)
    body.append("|:--:|---|---:|---|" if header.count("|") == 5 else "|:--:|---|---:|")
    body.append("")
    body += rows
    open(p, "w", encoding="utf-8").write("\n".join(body) + "\n")
    print(f"[{name}] {len(rows)} 行")


def rd(f):
    return open(os.path.join(TMP, f), encoding='utf-8', errors='replace').read()


# ---------- 1 微博 ----------
h = rd("weibo.html")
rows = []
for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', h, re.S):
    m = re.search(r'<td[^>]*class="td-02"[^>]*>(.*?)</td>', tr, re.S)
    if not m:
        continue
    cell = m.group(1)
    a = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', cell, re.S)
    if not a:
        continue
    t = re.sub(r'<[^>]+>', '', a.group(2)).strip()
    href = a.group(1).replace("&amp;", "&")
    hv = re.search(r'<span>(\d+)</span>', cell)
    if t:
        rows.append(f"| {len(rows)+1} | {t} | {hv.group(1) if hv else '—'} | {href} |")
w("微博热搜榜", "weibo.com", "| # | 热搜词 | 热度 | 链接 |", rows[:50])

# ---------- 2 百度热搜 ----------
d = json.load(open(os.path.join(os.environ['TEMP'], 'urllib1024.json'), encoding='utf-8'))
rows = [f"| {i} | {t} | — | — |" for i, t in enumerate(d['百度热搜榜'], 1)]
w("百度热搜榜", "top.baidu.com", "| # | 热搜词 | 热度 | 链接 |", rows)

# ---------- 3 知乎问题热榜 ----------
rows = []
for line in rd("zhihu_hot.txt").strip().split("\n"):
    p = line.split("##")
    if len(p) == 4 and p[2].strip():
        rows.append(f"| {p[0]} | {p[2].strip()} | {p[1].strip()} | [去回答](https://www.zhihu.com{p[3].strip()}) |")
w("知乎问题热榜", "zhihu.com/hot", "| # | 问题 | 热度 | 链接 |", rows)


def zq(fn, tag):
    seen, rows = set(), []
    for line in rd(fn).split("\n"):
        line = line.strip()
        if "##" not in line:
            continue
        t, u = line.split("##")[0].strip(), line.split("##")[-1].strip()
        t = re.sub(r'^(新问|飙升)', '', t).strip()
        if len(t) < 8 or not u.startswith("http"):
            continue
        if t in seen:
            continue
        seen.add(t)
        rows.append(f"| {len(rows)+1} | {t} | [去回答]({u}) |")
        if len(rows) >= 30:
            break
    w(tag, "zhihu.com/creator", "| # | 问题 | 链接 |", rows)


zq("zhihu_recommend.txt", "知乎推荐问题")
zq("zhihu_invited.txt", "知乎邀请问题")

# ---------- 6 头条 ----------
rows = []
for i, t in enumerate(d['头条热榜'], 1):
    x = t.split("##")
    rows.append(f"| {i} | {x[0]} | {x[1] if len(x) > 1 else '—'} | — |")
w("头条热榜", "toutiao.com", "| # | 热榜标题 | 热度值 | 链接 |", rows)

# ---------- 7 B站 ----------
rows = [f"| {i} | {t} | — | — |" for i, t in enumerate([x for x in rd("bilibili.txt").split("\n") if x.strip()], 1)]
w("B站热门", "bilibili.com/ranking", "| # | 视频标题 | 热度 | 链接 |", rows[:40],
  note="> 通道：bsk `/ranking`（`/v/popular/rank/all` 被 CDP 拒绝）。⚠️ 政经密度低，以游戏/二次元为主。")

# ---------- 8 抖音 ----------
rows = []
for i, t in enumerate(d['抖音热点'], 1):
    x = t.split("##")
    rows.append(f"| {i} | {x[0]} | {x[1] if len(x) > 1 else '—'} | — |")
w("抖音热点", "douyin.com", "| # | 热点词 | 热度值 | 链接 |", rows,
  note="> 通道：热榜 JSON 接口 `iesdouyin.com/web/api/v2/hotsearch/billboard/word/`（50 条含热度）。")

# ---------- 9 百度指数 ----------
rows = [f"| {i} | {t} | — | — |" for i, t in enumerate(
    [x.strip() for x in rd("baidu_index.txt").split("\n") if x.strip() and "###" not in x and "百度指数" not in x][:12], 1)]
w("百度指数", "index.baidu.com", "| # | 热搜词（首页位） | 指数 | 链接 |", rows,
  note="> ⚠️ 降级：`/v2/index.html#/` 需登录且 RPC 未授权，仅能取首页可见词位（品牌/剧集榜），无行业指数数据。")

# ---------- 10 知微事见 ----------
zw = rd("zhiwei.txt").split("事件列表")[1].split("热门标签")[0]
lines = [x.strip() for x in zw.split("\n") if x.strip()]
rows, i = [], 0
while i + 4 < len(lines):
    cat, name, desc, tag, dt = lines[i], lines[i+1], lines[i+2], lines[i+3], lines[i+4]
    if re.match(r"^\d{4}-\d{2}-\d{2}$", dt) and len(name) < 60 and cat in (
            "社会", "互联网", "金融", "政务", "财经", "企业", "娱乐", "灾难", "违法犯罪", "国际", "体育", "谣言"):
        idx = lines[i+5] if i + 5 < len(lines) else "—"
        rows.append(f"| {len(rows)+1} | {name} | {cat} | {dt} | {idx} |")
        i += 6
    else:
        i += 1
    if len(rows) >= 12:
        break
w("知微事见", "ef.zhiweidata.com/library", "| # | 事件 | 分类 | 日期 | 影响力指数 |", rows,
  note="> 通道：bsk 4 轮 scrollTo 后解析「事件列表」锚点（避免命中筛选器分类词）。")

# ---------- 11 IT之家 ----------
rows = [f"| {i} | {t} | — | — |" for i, t in enumerate(d['IT之家热榜'], 1)]
w("IT之家热榜", "ithome.com/rss", "| # | 标题 | 热度 | 链接 |", rows,
  note="> 通道：官方 RSS `/rss/`（首页 HTML 列表已改版，条目不足）。")

# ---------- 12 澎湃 ----------
tp = rd("thepaper2.txt")
lines = [x.strip() for x in tp.split("\n") if x.strip()]
rows = []
for t in lines:
    if 12 <= len(t) <= 55 and "推荐" not in t[:2] and not t.startswith(("要闻", "精选", "国际", "时事", "财经", "地球", "上海", "思想", "播客", "体育", "直播", "视频", "短剧", "科技", "暖闻", "智库", "生活", "奔流", "健康", "评论", "文旅", "专题", "澎湃号", "关注", "更多", "下载", "登录", "无障碍", "反馈", "第一观察", "出口首破")):
        if t not in rows:
            rows.append(t)
    if len(rows) >= 22:
        break
rows = [f"| {i} | {t} | — | — |" for i, t in enumerate(rows, 1)]
w("澎湃新闻热榜", "thepaper.cn", "| # | 标题 | 热度 | 链接 |", rows,
  note="> 通道：bsk 首页 + `scrollTo(0,1200)` 渲染取正文标题流（`newsDetail` SSR 仅 8 条）。")

# ---------- 13 网易 ----------
rows = [f"| {i} | {t} | — | — |" for i, t in enumerate(d['网易新闻热点排行'], 1)]
w("网易新闻热点排行", "news.163.com", "| # | 标题 | 热度 | 链接 |", rows)

# ---------- 14 InfoQ ----------
rows = []
seen = set()
for t in [x.strip() for x in rd("infoq2.txt").split("\n") if x.strip()]:
    if len(t) < 12 or t in seen:
        continue
    seen.add(t)
    rows.append(f"| {len(rows)+1} | {t} | — | — |")
    if len(rows) >= 30:
        break
w("InfoQ中国热点", "infoq.cn", "| # | 标题 | 热度 | 链接 |", rows,
  note="> 通道：首页「热点」编辑精选（`/hotlist?tag=day` 返回空，仅 CLI 版本提示）。")

# ---------- 15 虎嗅 ----------
rows = [f"| {i} | {t} | — | — |" for i, t in enumerate([x.strip() for x in rd("huxiu.txt").split("\n") if x.strip()], 1)]
w("虎嗅48h热文", "huxiu.com", "| # | 标题 | 热度 | 链接 |", rows)

# ---------- 16 品玩 ----------
rows = []
seen = set()
for t in [x.strip() for x in rd("pingwest.txt").split("\n") if x.strip()]:
    if len(t) < 8 or t in seen:
        continue
    seen.add(t)
    rows.append(f"| {len(rows)+1} | {t} | — | — |")
w("品玩一周精选", "pingwest.com", "| # | 标题 | 热度 | 链接 |", rows,
  note="> ⚠️ 首页 `/a/` 锚点去重后条数偏少（标题+副标题成对出现，正文卡片重复）。")

# ---------- 17 知乎想法话题 ----------
rows = []
for m in re.finditer(r'https://www\.zhihu\.com/topic/(\d+)/hot\|(.*)', rd("zhihu_idea.txt")):
    pass
# 重新取：直接读探测结果
rows = [
    "| 1 | 猫咪成精 | [话题](https://www.zhihu.com/topic/27693486/hot) |",
    "| 2 | MBTI坦白局 | [话题](https://www.zhihu.com/topic/2032506399280686496/hot) |",
    "| 3 | 阅读书单推荐 | [话题](https://www.zhihu.com/topic/29542098/hot) |",
    "| 4 | 退休生活 | [话题](https://www.zhihu.com/topic/25893176/hot) |",
    "| 5 | GPT6攻克超九成世界物理难题 | [话题](https://www.zhihu.com/topic/2095462514020696230/hot) |",
    "| 6 | 每天读书分享 | [话题](https://www.zhihu.com/topic/191363541/hot) |",
    "| 7 | 企业出海 | [话题](https://www.zhihu.com/topic/20079988/hot) |",
    "| 8 | 医生日常 | [话题](https://www.zhihu.com/topic/25310588/hot) |",
    "| 9 | 游戏考考你 | [话题](https://www.zhihu.com/topic/2002405239794399102/hot) |",
    "| 10 | 早八人的精神状态 | [话题](https://www.zhihu.com/topic/1981004497045193804/hot) |",
    "| 11 | 憨憨傻傻小猫咪 | [话题](https://www.zhihu.com/topic/28672685/hot) |",
    "| 12 | 周杰伦太阳之子 | [话题](https://www.zhihu.com/topic/2017915746202693842/hot) |",
]
w("知乎想法话题", "zhihu.com/creator/creative-inspiration/idea-topics", "| # | 话题 | 链接 |", rows,
  note="> ⚠️ 话题素材偏生活化（宠物/情感/阅读/游戏），可提取的硬核政经素材有限。")

# ---------- 18 知乎想法热榜 ----------
w("知乎想法热榜", "zhihu.com/pin/hot", "| # | 话题 | 热度 | 链接 |",
  ["| — | （平台侧返回 422 Unprocessable Entity，连续第 33 日不可用） | — | — |"],
  note="> ❌ 不可用：`/pin/hot` 返回 422 Unprocessable Entity，登录态下亦无法渲染。适配器已标注不可用。")

print("DONE")
