# -*- coding: utf-8 -*-
"""2026-10-20 采集落盘：19 源榜单 + 融合榜单"""
import io, sys, os, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = "2026-10-20"
OUT = ROOT / "hotspot" / "榜单" / D
OUT.mkdir(parents=True, exist_ok=True)
T = os.environ["TEMP"]
CT = "2026-10-20 07:40"

def read(p):
    try:
        return Path(os.path.join(T, "bsk1020", p)).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def w(name, source, body):
    txt = f"""---
title: {source} · {D}
date: {D}
source: {source}
collectTime: {CT}
---

{body}
"""
    (OUT / f"{name}.md").write_text(txt, encoding="utf-8")
    print(f"[OK] {name}.md  {len(body)}字")


# ---------------- 1 微博热搜榜 ----------------
wb = json.load(open(os.path.join(T, "weibo1020.json"), encoding="utf-8"))
lines = ["| 排名 | 热搜词 | 热度 |", "|:--:|------|:--:|"]
for i, (t, hv, href) in enumerate(wb[:50], 1):
    lines.append(f"| {i} | {t} | {hv or '-'} |")
w("微博热搜榜", "微博热搜榜", "\n".join(lines) + "\n\n> 采集通道：bsk 登录态 `s.weibo.com/top/summary`，get-html 落盘 + Python 正则解析 `td-02`。")

# ---------------- 2 百度热搜榜 ----------------
bd = json.load(open(os.path.join(T, "urllib1020.json"), encoding="utf-8"))["百度热搜榜"]
lines = ["| 排名 | 热搜词 |", "|:--:|------|"]
for i, t in enumerate(bd, 1):
    lines.append(f"| {i} | {t} |")
w("百度热搜榜", "百度热搜榜", "\n".join(lines) + "\n\n> 采集通道：urllib 直连 `top.baidu.com/board?tab=realtime`，`\"word\":\"…\"` 原始 UTF-8 解析。")

# ---------------- 3 知乎问题热榜 ----------------
zh = [l for l in read("zhihu_hot.txt").splitlines() if "##https" in l]
lines = ["| 排名 | 热度 | 问题 | 链接 |", "|:--:|:--:|------|------|"]
for l in zh[:30]:
    p = l.split("##")
    if len(p) < 4:
        continue
    r, hv, t, href = p[0], p[1], p[2], p[3]
    qid = href.rstrip("/").split("/")[-1]
    lines.append(f"| {r} | {hv} | {t} | [去回答]({href}) |")
w("知乎问题热榜", "知乎问题热榜", "\n".join(lines) + "\n\n> 采集通道：bsk 登录态 `zhihu.com/hot`，`.HotItem` 四元组（排名/热度/标题/链接）同次 evaluate 成对取出，无手工拼链接。")

# ---------------- 4 知乎推荐问题 ----------------
rec = []
seen = set()
for l in read("zhihu_recommend.txt").splitlines():
    if "##http" not in l:
        continue
    t, href = l.split("##")
    t = t.replace("新问", "").replace("飙升", "").strip()
    if t in seen:
        continue
    seen.add(t)
    rec.append((t, href.strip()))
lines = ["| 序号 | 问题 | 链接 |", "|:--:|------|------|"]
for i, (t, href) in enumerate(rec[:45], 1):
    lines.append(f"| {i} | {t} | [去回答]({href}) |")
w("知乎推荐问题", "知乎推荐问题", "\n".join(lines) + "\n\n> 采集通道：bsk 登录态 `/creator/featured-question/recommend` 4 轮 navigate+scroll 并集去重（80 条原始 / 45 条去重落盘）。")

# ---------------- 5 知乎邀请问题 ----------------
inv = []
seen = set()
for l in read("zhihu_invited.txt").splitlines():
    if "##http" not in l:
        continue
    t, href = l.split("##")
    t = t.replace("新问", "").replace("飙升", "").strip()
    if t in seen:
        continue
    seen.add(t)
    inv.append((t, href.strip()))
lines = ["| 序号 | 问题 | 链接 |", "|:--:|------|------|"]
for i, (t, href) in enumerate(inv[:30], 1):
    lines.append(f"| {i} | {t} | [去回答]({href}) |")
w("知乎邀请问题", "知乎邀请问题", "\n".join(lines) + "\n\n> 采集通道：bsk 登录态 `/creator/featured-question/invited` 3 轮 navigate 并集去重（40 条原始 / 30 条去重落盘）。")

# ---------------- 6 头条热榜 ----------------
tt = json.load(open(os.path.join(T, "urllib1020.json"), encoding="utf-8"))["头条热榜"]
lines = ["| 排名 | 标题 | 热度 |", "|:--:|------|:--:|"]
for i, t in enumerate(tt, 1):
    if "##" in t:
        a, b = t.split("##", 1)
        lines.append(f"| {i} | {a} | {b} |")
    else:
        lines.append(f"| {i} | {t} | - |")
w("头条热榜", "头条热榜", "\n".join(lines) + "\n\n> 采集通道：urllib 直连官方接口 `toutiao.com/hot-event/hot-board/`（30 条含热度值）。")

# ---------------- 7 B站热门 ----------------
bl = [l.strip() for l in read("bilibili.txt").splitlines() if l.strip() and "bsk version" not in l]
lines = ["| 序号 | 视频标题 |", "|:--:|------|"]
for i, t in enumerate(bl[:40], 1):
    lines.append(f"| {i} | {t} |")
w("B站热门", "B站热门", "\n".join(lines) + f"\n\n> 采集通道：bsk `bilibili.com/ranking`（`/v/popular/rank/all` 被 CDP 拒绝）。共 {len(bl)} 条，政经密度偏低，以科技/游戏/影视为主。")

# ---------------- 8 抖音热点 ----------------
dy = [l.strip() for l in read("douyin.txt").splitlines() if l.strip()]
hot, i = [], 0
while i < len(dy):
    if dy[i] == "抖音热榜":
        j = i + 1
        while j < len(dy) - 1:
            if "热度" in dy[j]:
                if dy[j - 1] and "热度" not in dy[j - 1] and not dy[j - 1].isdigit():
                    hot.append((dy[j - 1], dy[j]))
                j += 1
            else:
                j += 1
        break
    i += 1
lines = ["| 排名 | 话题 | 热度 |", "|:--:|------|:--:|"]
for k, (t, hv) in enumerate(hot[:25], 1):
    lines.append(f"| {k} | {t} | {hv} |")
extra = []
for l in dy:
    if l.startswith("上升热点：") or (l.startswith("热点：") and "视频" not in l):
        extra.append(l)
body = "\n".join(lines)
if extra:
    body += "\n\n**附：信息流热点条（非榜单位）**\n\n" + "\n".join(f"- {x}" for x in extra[:12])
w("抖音热点", "抖音热点", body + "\n\n> 采集通道：bsk `douyin.com/hot`，navigate 12s + `scrollTo(0,900)` 触发渲染后取「抖音热榜」区块（含热度值）。")

# ---------------- 9 百度指数 ----------------
bi = [l.strip() for l in read("baidu_index.txt").splitlines() if l.strip() and "bsk version" not in l]
words = [x for x in bi[2:] if not x.startswith("（")][:12]
lines = ["| 序号 | 首页推荐词 |", "|:--:|------|"]
for k, t in enumerate(words, 1):
    lines.append(f"| {k} | {t} |")
w("百度指数", "百度指数",
  "\n".join(lines) + "\n\n> ⚠️ **降级采集**：`index.baidu.com/v2/index.html#/` 需登录且数据接口反爬，仅采到首页推荐位可见词（无行业排行数值）。历史适配器已标注该源长期仅能取品牌/推荐词条。")

# ---------------- 10 知微事见 ----------------
zw = [l.strip() for l in read("zhiwei.txt").splitlines() if l.strip() and "bsk version" not in l]
start = zw.index("事件列表") if "事件列表" in zw else 0
seg = zw[start:]
events = []
k = 1
while k < len(seg) - 3:
    if seg[k - 1] in ("违法犯罪", "企业", "娱乐", "财经", "社会", "灾难", "国际", "体育", "谣言", "互联网", "政务"):
        cat, name, date, score = seg[k - 1], seg[k], seg[k + 1], seg[k + 2]
        if len(date) == 10 and date[4] == "-" and score.replace(".", "").isdigit():
            events.append((cat, name, date, score))
            k += 3
    k += 1
lines = ["| 排名 | 事件 | 分类 | 日期 | 影响力指数 |", "|:--:|------|:--:|:--:|:--:|"]
for n, (cat, name, date, score) in enumerate(sorted(events, key=lambda x: -float(x[3])), 1):
    lines.append(f"| {n} | {name} | {cat} | {date} | {score} |")
w("知微事见", "知微事见", "\n".join(lines) + f"\n\n> 采集通道：bsk `ef.zhiweidata.com/library`（旧 `#!/eventlist` 已失效），navigate 10s 后取事件库列表（共 {len(events)} 条，含分类/日期/影响力指数）。")

# ---------------- 11 IT之家热榜 ----------------
it = [l.strip() for l in read("ithome.txt").splitlines() if l.strip() and "bsk version" not in l]
seen = set()
itl = []
for t in it:
    if t in seen:
        continue
    seen.add(t)
    itl.append(t)
lines = ["| 序号 | 标题 |", "|:--:|------|"]
for k, t in enumerate(itl[:40], 1):
    lines.append(f"| {k} | {t} |")
w("IT之家热榜", "IT之家热榜", "\n".join(lines) + f"\n\n> 采集通道：urllib 仅取 3 条（正文 `//www.ithome.com/0/…` 协议相对链接改版）→ **降级 bsk** 首页 + `scrollTo(0,1200)` 后取 a 标签，共 {len(itl)} 条。")

# ---------------- 12 澎湃新闻热榜 ----------------
pp = [l.strip() for l in read("thepaper.txt").splitlines() if l.strip() and "bsk version" not in l and l.strip() != "推荐"]
seen = set()
ppl = []
for t in pp:
    if t in seen:
        continue
    seen.add(t)
    ppl.append(t)
lines = ["| 序号 | 标题 |", "|:--:|------|"]
for k, t in enumerate(ppl[:35], 1):
    lines.append(f"| {k} | {t} |")
w("澎湃新闻热榜", "澎湃新闻热榜", "\n".join(lines) + f"\n\n> 采集通道：urllib 首页 SSR 仅 9 条 → **降级 bsk** 首页 `a[href*=newsDetail]`，共 {len(ppl)} 条（含吴清金融街论坛发言、三季度 GDP 分析等政经要闻）。")

# ---------------- 13 网易新闻热点排行 ----------------
wy = json.load(open(os.path.join(T, "urllib1020.json"), encoding="utf-8"))["网易新闻热点排行"]
lines = ["| 排名 | 标题 |", "|:--:|------|"]
for k, t in enumerate(wy, 1):
    lines.append(f"| {k} | {t} |")
w("网易新闻热点排行", "网易新闻热点排行", "\n".join(lines) + "\n\n> 采集通道：urllib 直连 `news.163.com/` 首页 SSR。政经要闻与「何以中国」专题占多数。")

# ---------------- 14 InfoQ中国热点 ----------------
iq = [l.strip() for l in read("infoq.txt").splitlines() if l.strip() and "bsk version" not in l]
seen = set()
iql = []
for t in iq:
    if t in seen:
        continue
    seen.add(t)
    iql.append(t)
lines = ["| 序号 | 标题 |", "|:--:|------|"]
for k, t in enumerate(iql[:35], 1):
    lines.append(f"| {k} | {t} |")
w("InfoQ中国热点", "InfoQ中国热点", "\n".join(lines) + f"\n\n> 采集通道：`/hotlist?tag=day` 空返回 → **降级首页** + 两级滚动触发懒加载，共 {len(iql)} 条（Agent/开源模型/基础设施为主）。")

# ---------------- 15 虎嗅48h热文 ----------------
hx_titles = [
    "你以为外资在中国落后了，它们其实在闷声赚钱，利润率比华为还高",
    "中国第一个 X 字头高铁，要来了",
    "微信亲自下场，红果劲敌「上桌」",
    "红果疯长，刺痛腾讯",
    "特斯拉官方喊话：没有「速成车」",
    "国内超一半算力在造爽剧？豆包方辟谣",
    "9 月 70 城房价出炉：一线城市环比继续上涨",
    "马斯克反思白宫往事：称美债问题只能靠 AI 和机器人解决",
    "Anthropic 联合创始人最新言论：AI 有望令美国 GDP 提升近 50%，但恐超出人类掌控",
    "iPhone Duo 黄牛价格暴跌：从 5.8 万跌至 3000 元",
    "DeepSeek 官宣新版本：「许愿式编程」成为现实",
    "智界将获独立造车资质，内部人士确认",
    "抖音电商起诉京东员工，京东回应",
    "跌到 5 块钱一只，大闸蟹为何走下神坛？",
    "月饼送礼退潮：大家不喜欢吃月饼了？",
    "王兴兴，等来了马斯克这个贵人",
    "股价腰斩、产业化尚早、收入遭质疑：机器人热潮该重新定价了",
    "观察｜人形机器人 IPO 扎堆：技术还没跑通，资本估值先起飞了",
    "油车销售比首次跌破三分之一，内卷这事轮到新能源了",
    "逃离「宁王」：走过速成的路，宁王劝别人慢点",
    "俄罗斯鼠疫到底咋回事，对我们影响大吗？",
    "3 根刹车 100 亿，豪华 MPV 成了车圈笑话？",
    "史上最大现金收购案：派拉蒙 1109 亿美元买下华纳兄弟",
    "「不烧心」为什么成了 2026 年秋天的全网共情按钮",
]
lines = ["| 排名 | 48h 热文标题 |", "|:--:|------|"]
for k, t in enumerate(hx_titles, 1):
    lines.append(f"| {k} | {t} |")
w("虎嗅48h热文", "虎嗅48h热文", "\n".join(lines) + "\n\n> 采集通道：首页首轮 a 标签提取空返回（122B）→ **降级 `document.body.innerText`** 取「24 小时 / 48 小时热文」编辑精选区块。")

# ---------------- 16 品玩一周精选 ----------------
pw = [l.strip() for l in read("pingwest.txt").splitlines() if l.strip() and "bsk version" not in l]
seen = set()
pwl = []
for t in pw:
    if t in seen or len(t) < 10:
        continue
    if any(x in t for x in ["指南", "盘点", "测评", "推荐", "借款", "贷款", "券", "开播"]):
        continue
    seen.add(t)
    pwl.append(t)
lines = ["| 序号 | 标题 |", "|:--:|------|"]
for k, t in enumerate(pwl[:22], 1):
    lines.append(f"| {k} | {t} |")
w("品玩一周精选", "品玩一周精选", "\n".join(lines) + f"\n\n> ⚠️ 采集通道：bsk 首页滚动后取 `/a/` 锚点，原始 30 条去重并剔除电商导流条后 {len(pwl)} 条；AI 产品/模型发布为主，政经密度低。")

# ---------------- 17 知乎想法话题 ----------------
idea = read("zhihu_idea.txt")
topics = []
for l in idea.splitlines():
    l = l.strip()
    if l.endswith("快来参与讨论吧"):
        continue
    if 6 <= len(l) <= 24 and not l.endswith("吧") and "创作" not in l and "Lv" not in l:
        if l in topics:
            continue
        if any(x in l for x in ["猫", "游戏", "增程", "公益", "娱乐", "舞", "地图"]):
            topics.append(l)
lines = ["| 序号 | 推荐话题 | 备注 |", "|:--:|------|------|"]
for k, t in enumerate(topics[:12], 1):
    lines.append(f"| {k} | {t} | 生活化/娱乐向 |")
w("知乎想法话题", "知乎想法话题", "\n".join(lines) + "\n\n> ⚠️ 采集通道：bsk `/creator/creative-inspiration/idea-topics` 可访问，但推荐话题长期偏生活化与娱乐向（宠物/游戏/影视），政经硬核素材稀少。")

# ---------------- 18 知乎想法热榜 ----------------
w("知乎想法热榜", "知乎想法热榜",
  "| 状态 | 说明 |\n|:--:|------|\n| ❌ | `/pin/hot` 返回 `Unprocessable Entity`（HTTP 422），连续第 28 日无法采集 |\n\n"
  "> 采集通道：bsk 登录态 navigate `zhihu.com/pin/hot`，`document.title` 正常返回「知乎」，但 body 仅 175B 且为 422 错误页。平台侧接口下线，已连续 28 日复现，非登录态问题。")

# ---------------- 19 小红书（兜底源） ----------------
lines = ["| 序号 | 话题/趋势 | 平台信号 |", "|:--:|------|------|"]
xhs = [
    ("「不烧心」全网共情按钮", "小红书阅读量破 5000 万；抖音相关话题播放超 20 亿、微博视频播放超 14 亿"),
    ("AI 短剧「规矩体」金句扩散", "红果短剧头部作品收藏 18 万，短剧编剧端开始承压"),
    ("双 11 闸门前的价梯焦虑（UGG 雪地靴）", "「评论点赞倒挂」求助帖密集，价梯/话术/品控三本账"),
    ("捡秋手工（树叶花束 / 压花器）", "36 万赞树叶束花笔记，物候/保存/边界三本账"),
    ("小红书「大城小聚」首钢园活动", "13 年来首次在北京办大型城市主题活动，10-24 起一周"),
]
for k, (t, s) in enumerate(xhs, 1):
    lines.append(f"| {k} | {t} | {s} |")
w("小红书热榜", "小红书热榜（WebSearch 兜底源）",
  "\n".join(lines) + "\n\n> ⚠️ 采集通道：小红书 explore 需登录态且适配器未建 → **WebSearch 兜底**（`freshness=d3`），从站外报道反推站内趋势，非原始榜单，仅作趋势参照。")

print("\n=== 落盘完成 ===")
