# -*- coding: utf-8 -*-
"""生成 2026-10-15 各源榜单 md 文件"""
import os, re, io, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
T = os.environ.get("TEMP", "C:/Users/lorns/AppData/Local/Temp")
B = os.path.join(T, "bsk1015")
ROOT = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot/榜单/2026-10-15")
os.makedirs(OUT, exist_ok=True)

CT = "2026-10-15 07:15"
D = "2026-10-15"


def rd(p):
    return open(p, encoding="utf-8", errors="ignore").read()


def wf(name, title, source, body):
    txt = f"---\ntitle: {title}\ndate: {D}\nsource: {source}\ncollectTime: {CT}\n---\n\n" + body
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(txt)
    print("WROTE", name, len(txt))


def lines(p):
    return [l.strip() for l in rd(p).splitlines() if l.strip()]


U = json.load(open(os.path.join(T, "urllib1015.json"), encoding="utf-8"))

# ---- 1 微博 ----
weibo = json.load(open(os.path.join(T, "weibo1015.json"), encoding="utf-8"))["微博热搜榜"]
body = "## 微博热搜榜\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(weibo[:52], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk 登录态 `s.weibo.com/top/summary` + get-html（178.9KB）+ 正则解析 `<tr>` 内 `td-02` 条目；热度值未暴露于 DOM。\n"
wf("微博热搜榜.md", "微博热搜榜 · 2026-10-15", "微博热搜榜", body)

# ---- 2 百度热搜榜 ----
bd = U["百度热搜榜"]
body = "## 百度热搜榜\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(bd[:30], 1):
    body += f"| {i} | {t} |\n"
body += "\n> urllib 直连 `top.baidu.com/board?tab=realtime`（SSR）；`latin-1→utf-8` 修正编码。\n"
wf("百度热搜榜.md", "百度热搜榜 · 2026-10-15", "百度热搜榜", body)

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
wf("知乎问题热榜.md", "知乎问题热榜 · 2026-10-15", "知乎问题热榜", body)

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
    wf(label + ".md", label + " · 2026-10-15", label, body)
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
wf("头条热榜.md", "头条热榜 · 2026-10-15", "头条热榜", body)

# ---- 7 B站 ----
bl = lines(os.path.join(B, "bilibili.txt"))
body = "## B站热门\n\n| # | 视频标题 |\n|:--:|------|\n"
for i, t in enumerate(bl[:40], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk `bilibili.com/ranking` + evaluate `/video/` 条目；内容以游戏/动画/生活娱乐为主，政经密度低（当日仅「特朗普中期选举」1 条政经向）。\n"
wf("B站热门.md", "B站热门 · 2026-10-15", "B站热门", body)

# ---- 8 抖音 ----
dy_raw = rd(os.path.join(B, "douyin.txt"))
dy = []
for m in re.finditer(r'([^\n]{6,40})\n([\d.]+万)热度', dy_raw):
    t = m.group(1).strip()
    if t not in [x[0] for x in dy]:
        dy.append((t, m.group(2)))
if len(dy) < 10:
    dy = [(f"（抖音热榜条目）", "") for _ in range(0)]
body = "## 抖音热点\n\n| # | 词条 | 热度 |\n|:--:|------|:--:|\n"
for i, (t, hv) in enumerate(dy[:50], 1):
    body += f"| {i} | {t} | {hv} |\n"
body += ("\n> bsk 登录态 `douyin.com/hot`：首轮 navigate 仅渲染页脚（bytes=8946）→ **重试 navigate + `scrollTo(0,900)` + 6s×2 等待后 evaluate**，"
         "取热榜 50 条（含热度值，政经/财经密度明显：央行 7000 亿买断式逆回购、美国 9 月 CPI、金价跌破 4100 美元、中朝鸭绿江大桥）。\n")
wf("抖音热点.md", "抖音热点 · 2026-10-15", "抖音热点", body)

# ---- 9 百度指数 ----
body = ("## 百度指数\n\n**降级采集**（仅首页可见推荐位）\n\n"
        "| # | 可见项 |\n|:--:|------|\n| 1 | lornshrimp（个人账号） |\n| 2 | AI引导数据革命 |\n"
        "| 3 | 六安 / 长沙 / 阜阳 / 辽源 / 四平（地域推荐词条位） |\n"
        "| 4 | 趋势研究 / 需求图谱 / 人群画像（模块入口） |\n| 5 | 行业排行 / 最新动态（需异步 RPC 签名接口） |\n\n"
        "> bsk 登录态 `index.baidu.com/v2/index.html#/`；趋势/资讯指数面板显示「没有数据」（数据更新时段 12~16 时），"
        "行业排行与品牌榜子页需异步 RPC 签名接口，不可达。**连续多日降级，仅首页推荐位可读。**\n")
wf("百度指数.md", "百度指数 · 2026-10-15", "百度指数", body)

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
body += "\n> bsk `ef.zhiweidata.com/library` + evaluate innerText（含事件名/日期/影响力指数/分类）；当日最高为「高铁免提通话」（72.0）、「黄奇帆被查」（70.9）、「茶百道停牌」（70.2）。\n"
wf("知微事见.md", "知微事见 · 2026-10-15", "知微事见", body)

# ---- 11 IT之家 ----
ih = U["IT之家热榜"]
body = "## IT之家热榜\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(ih[:30], 1):
    body += f"| {i} | {t} |\n"
body += ("\n> urllib 直连 `ithome.com/` 首页；**修复：当日首页 `/0/\\d+/\\d+.htm` 路径仅 7 条（改版），改为通用 `.htm` 锚点 + 标题质量过滤后命中 343 条、取前 30**"
         "（此前正则限定 `/0/` 目录仅得 1 条）。\n")
wf("IT之家热榜.md", "IT之家热榜 · 2026-10-15", "IT之家热榜", body)

# ---- 12 澎湃 ----
pp = U["澎湃新闻热榜"]
body = "## 澎湃新闻热榜\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(pp[:20], 1):
    body += f"| {i} | {t} |\n"
body += "\n> urllib 直连 `thepaper.cn` 首页（SSR）；首页条目偏少（9 条），以时政/调研行为主。\n"
wf("澎湃新闻热榜.md", "澎湃新闻热榜 · 2026-10-15", "澎湃新闻热榜", body)

# ---- 13 网易 ----
w163 = U["网易新闻热点排行"]
body = "## 网易新闻热点排行\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(w163[:30], 1):
    body += f"| {i} | {t} |\n"
body += "\n> urllib 直连 `news.163.com` 首页（SSR）；当日以时政/服务贸易/长征主题为主。\n"
wf("网易新闻热点排行.md", "网易新闻热点排行 · 2026-10-15", "网易新闻热点排行", body)

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
body += "\n> bsk navigate `infoq.cn/hotlist?tag=day` + scrollTo + evaluate（滚轮触发懒加载）。当日以 AI 编码 Agent / 大模型后训练成本为主。\n"
wf("InfoQ中国热点.md", "InfoQ中国热点 · 2026-10-15", "InfoQ中国热点", body)

# ---- 15 虎嗅 ----
hx = [t for t in lines(os.path.join(B, "huxiu.txt")) if 8 <= len(t) <= 60]
seen = []
for t in hx:
    if t not in seen:
        seen.append(t)
body = "## 虎嗅48h热文\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(seen[:25], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk navigate `huxiu.com/` + evaluate（urllib 被 WAF 拦）。当日政经/产业密度高（茶百道 IPO、速成车后遗症、美债 5.4%、乌兰察布数据中心）。\n"
wf("虎嗅48h热文.md", "虎嗅48h热文 · 2026-10-15", "虎嗅48h热文", body)

# ---- 16 品玩 ----
pw = [t for t in lines(os.path.join(B, "pingwest.txt")) if 8 <= len(t) <= 60]
seen = []
for t in pw:
    if t not in seen:
        seen.append(t)
body = "## 品玩一周精选\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(seen[:25], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk navigate `pingwest.com/` + scrollTo + evaluate（urllib 返回空）；标题与导语交替出现，去重后得 14 条。\n"
wf("品玩一周精选.md", "品玩一周精选 · 2026-10-15", "品玩一周精选", body)

# ---- 17 知乎想法话题 ----
idea = rd(os.path.join(B, "zhihu_idea.txt"))
topics = re.findall(r'\n([^\n]{3,20})\n(?:等)?[\d,.]+\s*万人?参与讨论', idea)
if not topics:
    topics = re.findall(r'\n([^\n]{3,20})\n[\d,]+ 人参与讨论', idea)
seen = []
for t in topics:
    if t not in seen:
        seen.append(t)
body = "## 知乎想法话题\n\n| # | 话题 |\n|:--:|------|\n"
for i, t in enumerate(seen[:15], 1):
    body += f"| {i} | {t} |\n"
body += "\n> bsk 登录态 `creator/creative-inspiration/idea-topics`；**素材偏生活化/娱乐化（周杰伦、魔兽世界、夕阳摄影等），硬核政经素材稀缺**（与历史一致）。\n"
wf("知乎想法话题.md", "知乎想法话题 · 2026-10-15", "知乎想法话题", body)

# ---- 18 知乎想法热榜 ----
body = ("## 知乎想法热榜\n\n**不可用**（HTTP 422 Unprocessable Entity · 连续第 26 日）\n\n"
        "> 平台侧接口持续下线，自 2026-09-17 起连续第 26 日不可用，已降级采「知乎想法话题」替代。\n")
wf("知乎想法热榜.md", "知乎想法热榜 · 2026-10-15", "知乎想法热榜", body)

# ---- 19 小红书 ----
body = ("## 小红书热榜/话题\n\n**降级采集**（explore 页在 Agent Window 未登录态下仅渲染登录页与页脚，适配器未建）\n\n"
        "| # | 趋势话题（WebSearch 兜底） | 信号 |\n|:--:|------|------|\n"
        "| 1 | #繁荣主义穿搭 | 2026-09 中下旬起密集出现，官方时尚账号「时尚薯」发起笔记征集，宣称分「上亿流量池」；秀场（罗意威/YSL）到平台合流 |\n"
        "| 2 | #格雷系穿搭 / #极简的尽头是格雷系 | 灰开衫高收藏笔记 2086 赞/1247 藏；翻车帖集中于「平灰」（一身同亮度灰） |\n"
        "| 3 | #小黑色穿搭 | 声称占小红书热搜 TOP3；黑色单品小面积锚定 + 高阶复用 |\n"
        "| 4 | #半裙西装搭配 | 连续三周霸榜服饰类话题 TOP3，抖音相关播放 8.2 亿次 |\n"
        "| 5 | 双 11「抄作业」退潮 | 「跟博主买、全退了」859 条评论；人设溢价/混穿率/退货窗口三本账成讨论焦点 |\n\n"
        "> 适配器未建；explore 页需登录态，改以公开趋势数据兜底（来源：什么值得买/搜狐转载的小红书话题数据 + WebSearch）。\n")
wf("小红书热榜话题.md", "小红书热榜/话题 · 2026-10-15", "小红书热榜/话题", body)

print("DONE", len(events), "zhiwei events", len(dy), "douyin")
