# -*- coding: utf-8 -*-
"""生成 2026-10-14 各源榜单 md 文件"""
import os, re, io, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
T = os.environ.get("TEMP", "C:/Users/lorns/AppData/Local/Temp")
B = os.path.join(T, "bsk1014")
ROOT = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot/榜单/2026-10-14")
os.makedirs(OUT, exist_ok=True)

CT = "2026-10-14 07:15"


def rd(p):
    return open(p, encoding="utf-8", errors="ignore").read()


def wf(name, title, source, body):
    txt = f"---\ntitle: {title}\ndate: 2026-10-14\nsource: {source}\ncollectTime: {CT}\n---\n\n" + body
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(txt)
    print("WROTE", name, len(txt))


def lines(p):
    return [l.strip() for l in rd(p).splitlines() if l.strip()]


U = json.load(open(os.path.join(T, "urllib1014.json"), encoding="utf-8"))

# ---- 1 微博 ----
weibo = json.load(open(os.path.join(T, "weibo1014.json"), encoding="utf-8"))["微博热搜榜"]
body = "## 微博热搜榜\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(weibo[:52], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk 登录态 `s.weibo.com/top/summary` + get-html（178KB）+ 正则解析 `<tr>` 内条目；热度值未暴露于 DOM。\n"
wf("微博热搜榜.md", "微博热搜榜 · 2026-10-14", "微博热搜榜", body)

# ---- 2 百度热搜榜 ----
bd = U["百度热搜榜"]
body = "## 百度热搜榜\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(bd[:30], 1):
    body += f"| {i} | {t} |\n"
body += "\n> urllib 直连 `top.baidu.com/board?tab=realtime`（SSR）；`latin-1→utf-8` 修正编码。\n"
wf("百度热搜榜.md", "百度热搜榜 · 2026-10-14", "百度热搜榜", body)

# ---- 3 知乎问题热榜 ----
zh = [l for l in lines(os.path.join(B, "zhihu_hot.txt")) if "##" in l]
body = "## 知乎问题热榜\n\n| 排名 | 问题 | 热度 | 链接 |\n|:--:|------|:--:|:--:|\n"
for l in zh[:30]:
    parts = l.split("##")
    if len(parts) < 4:
        continue
    r, hv, t, h = parts[0], parts[1], parts[2], parts[3]
    body += f"| {r} | {t} | {hv} | [去回答]({h}) |\n"
body += "\n> bsk 登录态 `/hot` 单次 evaluate 四元组对齐提取（排名/热度/标题/链接同条目取出）。\n"
wf("知乎问题热榜.md", "知乎问题热榜 · 2026-10-14", "知乎问题热榜", body)

# ---- 4/5 知乎推荐/邀请 ----
def zq(fn, label):
    raw = lines(os.path.join(B, fn))
    seen = {}
    for l in raw:
        if "##" not in l:
            continue
        t, h = l.rsplit("##", 1)
        t = t.strip()
        for badge in ("新问", "飙升", "最新", "热问"):
            if t.startswith(badge) and len(t) > len(badge) + 8:
                t = t[len(badge):].strip()
                break
        h = h.strip()
        if not t or ("zhihu.com/question" not in h and not h.startswith("/question/")):
            continue
        if not h.startswith("http"):
            h = "https://www.zhihu.com" + h
        if len(t) < 8 or t in ("推荐问题", "邀请问题"):
            continue
        if h not in seen:
            seen[h] = t
    items = list(seen.items())
    cap = 40 if "recommend" in fn else 25
    items = items[:cap]
    body = f"## {label}\n\n| # | 问题 | 链接 |\n|:--:|------|:--:|\n"
    for i, (h, t) in enumerate(items, 1):
        body += f"| {i} | {t} | [去回答]({h}) |\n"
    body += f"\n> bsk 登录态 `creator/featured-question/{'recommend' if 'recommend' in fn else 'invited'}` 多轮导航去重；成对提取标题+链接。\n"
    wf(label + ".md", label + " · 2026-10-14", label, body)
    return items

zq("zhihu_recommend.txt", "知乎推荐问题")
zq("zhihu_invited.txt", "知乎邀请问题")

# ---- 6 头条热榜 ----
tt = U["头条热榜"]
body = "## 头条热榜\n\n| 排名 | 词条 | 热度 |\n|:--:|------|:--:|\n"
for i, t in enumerate(tt[:30], 1):
    if "##" in t:
        a, b_ = t.split("##", 1)
        body += f"| {i} | {a} | {b_} |\n"
    else:
        body += f"| {i} | {t} | |\n"
body += "\n> urllib 直连官方接口 `toutiao.com/hot-event/hot-board`（含热度值）。\n"
wf("头条热榜.md", "头条热榜 · 2026-10-14", "头条热榜", body)

# ---- 7 B站 ----
bl = lines(os.path.join(B, "bilibili.txt"))
body = "## B站热门\n\n| # | 视频标题 |\n|:--:|------|\n"
for i, t in enumerate(bl[:40], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk `bilibili.com/ranking` + evaluate `/video/` 条目；内容以游戏/动画/生活娱乐为主，政经密度低。\n"
wf("B站热门.md", "B站热门 · 2026-10-14", "B站热门", body)

# ---- 8 抖音 ----
dy = ["习近平举行仪式欢迎博茨瓦纳总统访华", "欧冠加拉塔萨雷vs巴萨", "完美穿搭不浪费", "红星照耀中国",
      "国安客场1:0武里南联", "奥沙利文恭喜郑宇伯夺冠", "缅北魏家犯罪集团案一审宣判", "是秋天的魔法帽呀",
      "郑宇伯斯诺克900长沙站冠军", "发明柚子烤肉的人吃商极高", "所有人展示十月美甲", "怎么样才能回到以前",
      "无畏契约全新中国英雄爆料", "电动牙刷会伤害牙齿吗", "纯过日子人的双11必买清单", "太帅了 邢大人",
      "无畏契约10月15日停机更新公告", "NEON翻跳火速来袭", "阿隆索携博托莱托入驻抖音", "黄奇帆被查",
      "美人余奶狗爆改老公儿子", "期待另一双看向我的眼睛", "丞磊在我抖音摸一天麻将了", "当天气秋凉 当树叶泛黄",
      "太帅了檀大人", "小霸王张律婚礼熟人含量超标", "肖战官宣个人巡回演唱会", "福建宁德清水鲈鱼名不虚传",
      "阿里嘎多萌宠登场", "用AI粒子消散告别曾经的自己", "吴克群助力外卖急救侠再快一分钟", "每个宝宝都是天赐的礼物",
      "燕云正式推出DLSS5", "蒸蒸日上情感线好戳人", "白鹿方发布泰国见面会退票方案", "毛晓彤真是从诗中来的",
      "发视频拆你第一个宝宝测试盲盒", "火影手游11月版本前瞻", "我的教授拿了诺贝尔经济学奖", "拉丁舞版闪身步来了",
      "你不要那样看着我的眼睛", "宋亚轩深情狗狗眼的日常", "玉簟秋我比男主先爱上女主", "用ggez开启电竞模式",
      "一斩苍穹这番看了不烧心", "我这么有趣的人 你不喜欢吗", "八千里路明月照和王仁君适配拉满", "我就这样哥一天弟一天",
      "美人余李一桐打脸渣男好爽", "全看懂的前途一片短剧"]
body = "## 抖音热点\n\n| # | 词条 |\n|:--:|------|\n"
for i, t in enumerate(dy[:50], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk 登录态 `douyin.com/hot`：首轮 navigate 仅渲染页脚（bytes=270）→ **重试 navigate + scrollTo(0,900) + 12s 等待后 evaluate `a` 条目**，取 50 条（含政经/体育/娱乐混合）。\n"
wf("抖音热点.md", "抖音热点 · 2026-10-14", "抖音热点", body)

# ---- 9 百度指数 ----
body = ("## 百度指数\n\n**降级采集**（仅首页可见推荐位）\n\n"
        "| # | 可见项 |\n|:--:|------|\n| 1 | lornshrimp（个人账号） |\n| 2 | AI引导数据革命 |\n"
        "| 3 | 王安宇 / 扬州 / 王楚然 / 田曦薇 / 福州（推荐词条位） |\n"
        "| 4 | 趋势研究 / 需求图谱 / 人群画像（模块入口） |\n| 5 | 行业排行 / 最新动态（需异步 RPC 签名接口） |\n\n"
        "> bsk 登录态 `index.baidu.com/v2/index.html#/`；趋势/资讯指数面板显示「没有数据」（数据更新时段 12~16 时），"
        "行业排行与品牌榜子页需异步 RPC 签名接口，不可达。**连续多日降级，仅首页推荐位可读。**\n")
wf("百度指数.md", "百度指数 · 2026-10-14", "百度指数", body)

# ---- 10 知微事见 ----
zw = rd(os.path.join(B, "zhiwei.txt"))
events = []
pat_zw = (r'(社会|互联网|金融|政务|财经|企业|娱乐|灾难|违法犯罪|国际|体育|谣言)\n'
          r'([^\n]{4,60})\n[^\n]+\n([^\n]{2,40})\n(20\d\d-\d\d-\d\d)\n(\d+\.\d)\n影响力指数')
for m in re.finditer(pat_zw, zw):
    events.append((m.group(1), m.group(2), m.group(4), m.group(5)))
body = "## 知微事见（事件库）\n\n| # | 分类 | 事件 | 日期 | 影响力指数 |\n|:--:|:--:|------|:--:|:--:|\n"
for i, (c, t, d, s) in enumerate(events[:30], 1):
    body += f"| {i} | {c} | {t} | {d} | {s} |\n"
if not events:
    body += "| 1 | — | （事件列表见原始文本） | — | — |\n"
body += "\n> bsk `ef.zhiweidata.com/library` + evaluate innerText（含事件名/日期/影响力指数/分类）；当日最高为「黄奇帆被查」（69.0）。\n"
wf("知微事见.md", "知微事见 · 2026-10-14", "知微事见", body)

# ---- 11 IT之家 ----
ih = U["IT之家热榜"]
body = "## IT之家热榜\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(ih[:30], 1):
    body += f"| {i} | {t} |\n"
body += "\n> urllib 直连 `ithome.com/` 首页；**修复：链接为协议相对 `//www.ithome.com/\\d+/\\d+/\\d+.htm`**，改正则后命中 356 条、取前 30（此前正则要求 `https://` 前缀仅得 1 条）。\n"
wf("IT之家热榜.md", "IT之家热榜 · 2026-10-14", "IT之家热榜", body)

# ---- 12 澎湃 ----
pp = U["澎湃新闻热榜"]
body = "## 澎湃新闻热榜\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(pp[:20], 1):
    body += f"| {i} | {t} |\n"
body += "\n> urllib 直连 `thepaper.cn` 首页（SSR）；首页条目偏少（9 条）。\n"
wf("澎湃新闻热榜.md", "澎湃新闻热榜 · 2026-10-14", "澎湃新闻热榜", body)

# ---- 13 网易 ----
w163 = U["网易新闻热点排行"]
body = "## 网易新闻热点排行\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(w163[:30], 1):
    body += f"| {i} | {t} |\n"
body += "\n> urllib 直连 `news.163.com` 首页（SSR）；当日以时政/调研行主题为主。\n"
wf("网易新闻热点排行.md", "网易新闻热点排行 · 2026-10-14", "网易新闻热点排行", body)

# ---- 14 InfoQ ----
iq = [t for t in lines(os.path.join(B, "infoq.txt")) if 12 <= len(t) <= 80
      and not any(k in t for k in ("QCon", "AICon", "投稿", "合作", "反馈", "招聘", "geekbang", "Snowflake", "new"))]
seen = []
for t in iq:
    if t not in seen:
        seen.append(t)
body = "## InfoQ中国热点\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(seen[:30], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk navigate `infoq.cn/hotlist?tag=day` + scrollTo + evaluate（滚轮触发懒加载）。\n"
wf("InfoQ中国热点.md", "InfoQ中国热点 · 2026-10-14", "InfoQ中国热点", body)

# ---- 15 虎嗅 ----
hx = [t for t in lines(os.path.join(B, "huxiu.txt")) if 8 <= len(t) <= 60]
seen = []
for t in hx:
    if t not in seen:
        seen.append(t)
body = "## 虎嗅48h热文\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(seen[:25], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk navigate `huxiu.com/` + evaluate（urllib 被 WAF 拦）。\n"
wf("虎嗅48h热文.md", "虎嗅48h热文 · 2026-10-14", "虎嗅48h热文", body)

# ---- 16 品玩 ----
pw = [t for t in lines(os.path.join(B, "pingwest.txt")) if 8 <= len(t) <= 60]
seen = []
for t in pw:
    if t not in seen:
        seen.append(t)
body = "## 品玩一周精选\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(seen[:25], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk navigate `pingwest.com/` + scrollTo + evaluate（urllib 返回空）。\n"
wf("品玩一周精选.md", "品玩一周精选 · 2026-10-14", "品玩一周精选", body)

# ---- 17 知乎想法话题 ----
idea = rd(os.path.join(B, "zhihu_idea.txt"))
topics = re.findall(r'\n([^\n]{3,20})\n[\d,]+ 人参与讨论', idea)
if not topics:
    topics = re.findall(r'\n([^\n]{3,20})\n快来参与讨论吧', idea)
seen = []
for t in topics:
    if t not in seen:
        seen.append(t)
body = "## 知乎想法话题\n\n| # | 话题 |\n|:--:|------|\n"
for i, t in enumerate(seen[:15], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk 登录态 `creator/creative-inspiration/idea-topics`；**素材偏生活化/娱乐化（每日诗词、创业避坑等），硬核政经素材稀缺**（与历史一致）。\n"
wf("知乎想法话题.md", "知乎想法话题 · 2026-10-14", "知乎想法话题", body)

# ---- 18 知乎想法热榜 ----
body = ("## 知乎想法热榜\n\n**不可用**（HTTP 422 Unprocessable Entity · 连续第 25 日）\n\n"
        "> 平台侧接口持续下线，自 2026-09-17 起连续第 25 日不可用，已降级采「知乎想法话题」替代。\n")
wf("知乎想法热榜.md", "知乎想法热榜 · 2026-10-14", "知乎想法热榜", body)

# ---- 19 小红书 ----
body = ("## 小红书热榜/话题\n\n**降级采集**（explore 页在 Agent Window 未登录态下仅渲染登录页与页脚，适配器未建）\n\n"
        "| # | 趋势话题（WebSearch 兜底） | 信号 |\n|:--:|------|------|\n"
        "| 1 | #2026秋冬包包 / 美拉德棕色 | 单帖 3000+ 赞、1200+ 藏；行业综述称轻奢通勤托特 T 台占比涨幅 >28% |\n"
        "| 2 | #冷都女穿搭 | 9 月集中爆发，最高单帖 2.84 万赞、1.47 万藏 |\n"
        "| 3 | #缝纫治愈我 | 浏览量 >4.2 亿、笔记 >160 万篇（手工体验坊带动） |\n"
        "| 4 | #超长蛋挞退潮 | 网红单品快起快落，加长玩法失效 |\n"
        "| 5 | 网球风运动配饰 | 赛事流量外溢，运动配饰赛道升温 |\n\n"
        "> 适配器未建；explore 页需登录态，改以公开趋势数据兜底（来源：什么值得买/搜狐/中国新闻网转载的小红书话题数据）。\n")
wf("小红书热榜话题.md", "小红书热榜/话题 · 2026-10-14", "小红书热榜/话题", body)

print("DONE", len(events), "zhiwei events")
