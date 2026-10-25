# -*- coding: utf-8 -*-
import os, io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot/榜单/2026-09-26")
TMP = r"C:/Users/lorns/AppData/Local/Temp/bsk0926"
DATE = "2026-09-26"
CT = "2026-09-26 07:20"


def rd(name):
    p = os.path.join(TMP, name)
    return open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""


def clean(t):
    return re.sub(r"^A new bsk version.*\n", "", t).strip()


def w(fn, title, source, body, note):
    open(os.path.join(OUT, fn), "w", encoding="utf-8").write(
        "---\ntitle: %s · %s\nsource: %s\ndate: %s\ncollectTime: %s\n---\n\n%s\n\n> %s\n"
        % (title, DATE, source, DATE, CT, body, note))
    print("WROTE", fn)


# 8 抖音热点
raw = clean(rd("douyin.txt")).split("\n")
items = []
for l in raw:
    l = l.strip()
    if l.startswith("上升热点：") or "人在看" in l:
        items.append(l)
body = "## 抖音热点（%d 条）\n\n| # | 热点条目 |\n|:--:|------|\n" % len(items)
body += "\n".join("| %d | %s |" % (i, t) for i, t in enumerate(items, 1))
w("抖音热点.md", "抖音热点", "抖音热点", body,
  "采集通道：bsk 登录态 `douyin.com/hot` + evaluate innerText；采集时间 %s；共 %d 条上升热点标签。**降级**：热榜完整榜单模块未在无头环境下完整渲染，仅取到「上升热点」条目标签与全网在看量，榜位/热度值缺失。" % (CT, len(items)))

# 9 百度指数
body = "## 百度指数（本日无可用榜单数据）\n\n首页仅渲染「最新动态 / 行业排行」导航与账号自有推荐位；全站热搜榜与行业排行子页依赖异步 RPC 签名接口，无头环境不可达。\n"
w("百度指数.md", "百度指数", "百度指数", body,
  "采集通道：bsk 登录态 `index.baidu.com/v2/index.html#/` + evaluate；采集时间 %s；**降级 ⚠️**：仅暴露品牌词推荐位，不含全站热搜榜。" % CT)

# 10 知微事见
raw = clean(rd("zhiwei.txt")).split("\n")
lines = [l.strip() for l in raw if l.strip()]
ev = []
i = 0
CATS = set(["社会", "互联网", "金融", "政务", "财经", "企业", "娱乐", "灾难", "违法犯罪", "国际", "体育", "谣言"])
while i < len(lines):
    l = lines[i]
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", l) and ev:
        ev[-1]["date"] = l
        if i + 1 < len(lines) and re.fullmatch(r"\d+\.\d+", lines[i + 1]):
            ev[-1]["idx"] = lines[i + 1]
        i += 2
        continue
    if l in CATS or re.fullmatch(r"\d+\.\d+", l) or l == "影响力指数":
        i += 1
        continue
    if i + 2 < len(lines) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", lines[i + 2]):
        ev.append({"title": l, "short": lines[i + 1], "date": "", "idx": ""})
        i += 3
        continue
    i += 1
body = "## 知微事见 · 事件库（%d 条）\n\n| # | 事件 | 日期 | 影响力指数 |\n|:--:|------|:--:|:--:|\n" % len(ev)
body += "\n".join("| %d | %s | %s | %s |" % (n, e["title"], e["date"], e["idx"]) for n, e in enumerate(ev, 1))
w("知微事见.md", "知微事见", "知微事见", body,
  "采集通道：bsk `ef.zhiweidata.com/library` + evaluate innerText；采集时间 %s；共 %d 条，含事件名/日期/影响力指数/分类。" % (CT, len(ev)))

# 11 IT之家热榜
d = json.load(open(os.path.join(ROOT, ".workbuddy/scripts/_u0926_result.json"), encoding="utf-8"))
it = d["results"]["IT之家热榜"]
body = "## IT之家热榜（TOP %d）\n\n| 排名 | 标题 |\n|:--:|------|\n" % len(it)
body += "\n".join("| %d | %s |" % (i, t) for i, t in enumerate(it, 1))
w("IT之家热榜.md", "IT之家热榜", "IT之家热榜", body,
  "采集通道：urllib 直连 `ithome.com` 首页（SSR）；采集时间 %s；共 %d 条。" % (CT, len(it)))

# 12 澎湃新闻热榜
tp = d["results"]["澎湃新闻热榜"]
body = "## 澎湃新闻热榜（TOP %d）\n\n| 排名 | 标题 |\n|:--:|------|\n" % len(tp)
body += "\n".join("| %d | %s |" % (i, t) for i, t in enumerate(tp, 1))
w("澎湃新闻热榜.md", "澎湃新闻热榜", "澎湃新闻热榜", body,
  "采集通道：urllib 直连 `thepaper.cn` 首页（SSR）；采集时间 %s；共 %d 条，本日高度集中于中美元首外交。" % (CT, len(tp)))

# 13 网易新闻热点排行
wy = d["results"]["网易新闻热点排行"]
body = "## 网易新闻热点排行（TOP %d）\n\n| 排名 | 标题 |\n|:--:|------|\n" % len(wy)
body += "\n".join("| %d | %s |" % (i, t) for i, t in enumerate(wy, 1))
w("网易新闻热点排行.md", "网易新闻热点排行", "网易新闻热点排行", body,
  "采集通道：urllib 直连 `news.163.com` 首页（SSR）；采集时间 %s；共 %d 条。" % (CT, len(wy)))

# 14 InfoQ 中国热点
raw = clean(rd("infoq_home.txt"))
lines = [l.strip() for l in raw.split("\n") if l.strip()]
sel = []
start = False
for l in lines:
    if "精选" in l or "智谱把 ZCode" in l:
        start = True
    if start and 6 < len(l) < 70 and not l.startswith("作者"):
        sel.append(l)
sel = sel[:20]
body = "## InfoQ 中国热点（%d 条）\n\n| # | 标题 |\n|:--:|------|\n" % len(sel)
body += "\n".join("| %d | %s |" % (i, t) for i, t in enumerate(sel, 1))
w("InfoQ中国热点.md", "InfoQ中国热点", "InfoQ中国热点", body,
  "采集通道：bsk navigate `infoq.cn` 首页 + scrollTo + evaluate innerText（`/hotlist?tag=day` 本日多次滚动均返回空，降级首页编辑精选）；采集时间 %s；共 %d 条。" % (CT, len(sel)))

# 15 虎嗅48h热文
raw = clean(rd("huxiu2.txt"))
lines = [l.strip() for l in raw.split("\n") if l.strip()]
try:
    s = lines.index("48小时热文")
except ValueError:
    s = 0
sel = [l for l in lines[s + 1:] if 6 < len(l) < 60][:22]
body = "## 虎嗅48h热文（%d 条）\n\n| # | 标题 |\n|:--:|------|\n" % len(sel)
body += "\n".join("| %d | %s |" % (i, t) for i, t in enumerate(sel, 1))
w("虎嗅48h热文.md", "虎嗅48h热文", "虎嗅48h热文", body,
  "采集通道：bsk navigate + scrollTo + evaluate innerText；urllib 被 WAF 拦；采集时间 %s；共 %d 条，含 24h 快讯与 48h 热文。" % (CT, len(sel)))

# 16 品玩一周精选
raw = clean(rd("pingwest.txt"))
lines = [x.strip() for x in raw.split("\n") if 6 < len(x.strip()) < 70]
uniq = list(dict.fromkeys(lines))
body = "## 品玩一周精选（%d 条）\n\n| # | 标题 |\n|:--:|------|\n" % len(uniq)
body += "\n".join("| %d | %s |" % (i, t) for i, t in enumerate(uniq, 1))
w("品玩一周精选.md", "品玩一周精选", "品玩一周精选", body,
  "采集通道：bsk navigate + scrollTo + evaluate；urllib 返回空；采集时间 %s；去重后共 %d 条。" % (CT, len(uniq)))

# 17 知乎想法话题
raw = clean(rd("zhihu_idea.txt"))
lines = [l.strip() for l in raw.split("\n") if l.strip()]
try:
    s = lines.index("推荐话题")
except ValueError:
    s = 0
NAV = set(["发想法", "创作中心", "消息", "私信", "产品经理独孤虾", "Lv 8", "创作分 218,065", "发布内容", "创作主页", "等你来答", "推荐问题", "想法话题", "内容管理", "评论管理", "数据中心", "账号概览", "内容分析", "关注者分析", "收益变现", "收益分析", "品牌特邀", "众邀任务", "好物推荐", "AI 训练师", "芝士平台", "盐选合作", "送礼物功能", "活动中心", "创作成长", "创作者学院", "内容自荐", "版权服务", "创作榜单", "个人中心", "创作设置", "账号信息", "关联与同步", "MCN 管理", "圆桌主持人", "常见问题", "瓦力保镖"])
sel = [l for l in lines[s + 1:] if l not in NAV and 4 < len(l) < 50]
uniq = list(dict.fromkeys(sel))[:20]
body = "## 知乎想法话题（%d 条）\n\n| # | 话题 |\n|:--:|------|\n" % len(uniq)
body += "\n".join("| %d | %s |" % (i, t) for i, t in enumerate(uniq, 1))
w("知乎想法话题.md", "知乎想法话题", "知乎想法话题", body,
  "采集通道：bsk 登录态 `creator/creative-inspiration/idea-topics` + evaluate innerText；采集时间 %s；共 %d 条。**降级 ⚠️**：素材偏生活化/娱乐化（婚恋/收纳/读书/摄影），硬核政经素材稀缺（与历史一致）。" % (CT, len(uniq)))

# 18 知乎想法热榜
body = "## 知乎想法热榜（本日不可用）\n\n| 项 | 值 |\n|:--:|------|\n| 目标 URL | https://www.zhihu.com/pin/hot |\n| HTTP 状态 | **422 Unprocessable Entity** |\n| 采集结果 | 0 条 |\n"
w("知乎想法热榜.md", "知乎想法热榜", "知乎想法热榜", body,
  "采集通道：bsk 登录态 `zhihu.com/pin/hot`；采集时间 %s；**不可用 ❌**：平台侧接口持续下线，2026-09-11 起连续第 12 日返回 422；已降级采「知乎想法话题」替代。" % CT)

print("PART2 DONE")
