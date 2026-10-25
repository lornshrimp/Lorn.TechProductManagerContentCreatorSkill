# -*- coding: utf-8 -*-
"""2026-10-07 生成各源榜单 markdown 文件"""
import os, re, io, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体"
OUT = os.path.join(BASE, "hotspot/榜单/2026-10-07")
T = os.path.join(os.environ['TEMP'], 'bsk1007')
DATE = "2026-10-07"


def rd(name):
    for cand in [os.path.join(T, name), os.path.join(os.environ['TEMP'], name)]:
        if os.path.exists(cand):
            return open(cand, encoding='utf-8', errors='replace').read()
    return ''


def wf(fn, title, source, body, ct="2026-10-07 07:20"):
    txt = (f"---\ntitle: {title}\ndate: {DATE}\nsource: {source}\n"
           f"collectTime: {ct}\n---\n\n{body}\n")
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(txt)
    print(f"[{fn}] bytes={len(txt)}")


# ---------- 1 微博热搜榜 ----------
h = rd('weibo.html')
seen, wb = set(), []
for m in re.finditer(r'href="//s\.weibo\.com/weibo\?q=([^"]+)"[^>]*>\s*<span>(.*?)</span>', h):
    t = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    if t and t not in seen:
        seen.add(t); wb.append(t)
body = "## 微博热搜榜\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(wb, 1):
    body += f"| {i} | {t} |\n"
wf("微博热搜榜.md", f"微博热搜榜 · {DATE}", "微博热搜榜",
   body + "\n> 通道：bsk 登录态 `weibo.com/hot/search` + get-html + 正则解析（热度值未暴露于 DOM，仅取词条）")

# ---------- 2 百度热搜榜 ----------
bd = json.load(open(os.path.join(os.environ['TEMP'], 'baidu1007.json'), encoding='utf-8'))['百度热搜榜']
body = "## 百度热搜榜\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(bd, 1):
    body += f"| {i} | {t} |\n"
wf("百度热搜榜.md", f"百度热搜榜 · {DATE}", "百度热搜榜",
   body + "\n> 通道：urllib 直连 `top.baidu.com/board?tab=realtime`（SSR），已修正 UTF-8/latin-1 编码")

# ---------- 3 知乎问题热榜 ----------
zh = [l for l in rd('zhihu_hot.txt').split('\n') if l.strip()]
rows = []
for l in zh:
    p = l.split('##')
    if len(p) >= 4:
        rows.append((p[0].strip(), p[1].strip(), p[2].strip(), p[3].strip()))
body = "## 知乎问题热榜\n\n| 排名 | 热度 | 问题 | 链接 |\n|:--:|:--:|------|------|\n"
for r, hot, t, u in rows:
    body += f"| {r} | {hot} | {t} | [去回答]({u}) |\n"
wf("知乎问题热榜.md", f"知乎问题热榜 · {DATE}", "知乎问题热榜",
   body + "\n> 通道：bsk 登录态 `/hot`；排名/热度/标题/链接四元组在同一次 evaluate 内从同一 .HotItem 条目成对取出")

# ---------- 4 知乎推荐问题 ----------
def dedupe_zh(fn):
    seen, out = set(), []
    for l in rd(fn).split('\n'):
        l = l.strip()
        if '##' not in l:
            continue
        t, u = l.split('##', 1)
        t = t.strip(); u = u.strip()
        key = u.rstrip('/').split('/')[-1]
        if t and u.startswith('http') and key not in seen:
            seen.add(key); out.append((t, u))
    return out


rc = dedupe_zh('zhihu_recommend.txt')
body = f"## 知乎推荐问题（去重后 {len(rc)} 条）\n\n| # | 问题 | 链接 |\n|:--:|------|------|\n"
for i, (t, u) in enumerate(rc, 1):
    body += f"| {i} | {t} | [去回答]({u}) |\n"
wf("知乎推荐问题.md", f"知乎推荐问题 · {DATE}", "知乎推荐问题",
   body + "\n> 通道：bsk 登录态 `creator/featured-question/recommend`（4 轮导航去重）")

iv = dedupe_zh('zhihu_invited.txt')
body = f"## 知乎邀请问题（去重后 {len(iv)} 条）\n\n| # | 问题 | 链接 |\n|:--:|------|------|\n"
for i, (t, u) in enumerate(iv, 1):
    body += f"| {i} | {t} | [去回答]({u}) |\n"
wf("知乎邀请问题.md", f"知乎邀请问题 · {DATE}", "知乎邀请问题",
   body + "\n> 通道：bsk 登录态 `creator/featured-question/invited`（3 轮导航去重）")

# ---------- 6 头条热榜 ----------
tt = json.load(open(os.path.join(os.environ['TEMP'], 'urllib1007.json'), encoding='utf-8'))
ttl = tt['头条热榜']
body = "## 头条热榜\n\n| 排名 | 词条 | 热度 |\n|:--:|------|:--:|\n"
for i, t in enumerate(ttl, 1):
    if '##' in t:
        a, b = t.split('##', 1)
        body += f"| {i} | {a} | {b} |\n"
    else:
        body += f"| {i} | {t} | - |\n"
wf("头条热榜.md", f"头条热榜 · {DATE}", "头条热榜",
   body + "\n> 通道：urllib 直连官方接口 `toutiao.com/hot-event/hot-board`（30 条含热度值）")

# ---------- 7 B站热门 ----------
bl = [x.strip() for x in rd('bilibili.txt').split('\n') if x.strip()]
body = "## B站热门（排行榜）\n\n| 排名 | 视频标题 |\n|:--:|------|\n"
for i, t in enumerate(bl, 1):
    body += f"| {i} | {t} |\n"
wf("B站热门.md", f"B站热门 · {DATE}", "B站热门",
   body + "\n> 通道：bsk `bilibili.com/ranking` + evaluate `/video/` 条目；内容以游戏/动画/生活娱乐为主，政经密度低")

# ---------- 8 抖音热点 ----------
dy_raw = rd('douyin2.txt')
dy = []
m = re.search(r'抖音热榜\n(.*?)抖音热榜规则说明', dy_raw, re.S)
if m:
    seg = m.group(1)
    lines = [x.strip() for x in seg.split('\n') if x.strip()]
    i = 0
    while i < len(lines):
        cur = lines[i]
        if re.match(r'^\d+$', cur) and i + 2 < len(lines):
            title = lines[i + 1]
            hot = lines[i + 2]
            if '热度' in hot:
                dy.append((title, hot)); i += 3; continue
        if '热度' in cur and i > 0:
            title = lines[i - 1]
            if title not in [d[0] for d in dy]:
                dy.append((title, cur))
        i += 1
if not dy:
    lines = [x.strip() for x in dy_raw.split('\n') if x.strip()]
    for i, l in enumerate(lines):
        if '热度' in l and i > 0:
            dy.append((lines[i - 1], l))
body = "## 抖音热点（热榜）\n\n| 排名 | 词条 | 热度 |\n|:--:|------|:--:|\n"
for i, (t, hv) in enumerate(dy[:50], 1):
    body += f"| {i} | {t} | {hv} |\n"
wf("抖音热点.md", f"抖音热点 · {DATE}", "抖音热点",
   body + "\n> 通道：bsk 登录态 `douyin.com/hot`（首轮 CDP Detached，重试后热榜模块正常渲染，取 50 条含热度值）")

# ---------- 9 百度指数 ----------
body = ("## 百度指数（降级）\n\n**仅首页可见推荐位（非指数榜）**：AI引导数据革命 / 小城良方 / 余红旧事 / 美人余 / 赵今麦 / 兰香如故\n\n"
        "> ⚠️ **降级**：`index.baidu.com` 首页仅暴露账号自有推荐位；行业排行/品牌榜子页需异步 RPC 签名接口，bsk 登录态下不可达。")
wf("百度指数.md", f"百度指数 · {DATE}", "百度指数", body)

# ---------- 10 知微事见 ----------
zw_raw = rd('zhiwei.txt') + "\n" + rd('zhiwei2.txt')
ev = []
for m in re.finditer(r'\n(社会|互联网|金融|政务|财经|企业|娱乐|灾难|违法犯罪|国际|体育|谣言)\n(.*?)\n(20\d\d-\d\d-\d\d)\n([\d.]+)\n影响力指数', zw_raw, re.S):
    cat, desc, d, idx = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
    ev.append((cat, desc, d, idx))
body = "## 知微事见（事件库）\n\n| 分类 | 事件 | 日期 | 影响力指数 |\n|:--:|------|:--:|:--:|\n"
for cat, desc, d, idx in ev:
    body += f"| {cat} | {desc} | {d} | {idx} |\n"
wf("知微事见.md", f"知微事见 · {DATE}", "知微事见",
   body + "\n> 通道：bsk `ef.zhiweidata.com/library` + scroll + evaluate innerText（含事件名/日期/影响力指数/分类）")

# ---------- 11 IT之家 / 12 澎湃 / 13 网易 ----------
for fn, key, src, extra in [("IT之家热榜.md", "IT之家热榜", "IT之家热榜", ""),
                            ("澎湃新闻热榜.md", "澎湃新闻热榜", "澎湃新闻热榜", ""),
                            ("网易新闻热点排行.md", "网易新闻热点排行", "网易新闻热点排行", "")]:
    items = tt[key]
    body = f"## {src}\n\n| 排名 | 标题 |\n|:--:|------|\n"
    for i, t in enumerate(items, 1):
        body += f"| {i} | {t} |\n"
    wf(fn, f"{src} · {DATE}", src, body + f"\n> 通道：urllib 直连首页（SSR）{extra}")

# ---------- 14 InfoQ ----------
iq = [x.strip() for x in rd('infoq.txt').split('\n') if x.strip() and len(x.strip()) > 10]
seen, iq2 = set(), []
for t in iq:
    if t not in seen:
        seen.add(t); iq2.append(t)
body = "## InfoQ 中国热点（日榜）\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(iq2, 1):
    body += f"| {i} | {t} |\n"
wf("InfoQ中国热点.md", f"InfoQ中国热点 · {DATE}", "InfoQ中国热点",
   body + "\n> 通道：bsk navigate `infoq.cn/hotlist?tag=day` + scrollTo + evaluate")

# ---------- 15 虎嗅 ----------
hx = [x.strip() for x in rd('huxiu.txt').split('\n') if x.strip()]
seen, hx2 = set(), []
for t in hx:
    if t not in seen:
        seen.add(t); hx2.append(t)
body = "## 虎嗅 48h 热文\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(hx2, 1):
    body += f"| {i} | {t} |\n"
wf("虎嗅48h热文.md", f"虎嗅48h热文 · {DATE}", "虎嗅48h热文",
   body + "\n> 通道：bsk navigate + scrollTo + evaluate（urllib 被 WAF 拦）")

# ---------- 16 品玩 ----------
pw = [x.strip() for x in rd('pingwest.txt').split('\n') if x.strip()]
seen, pw2 = set(), []
for t in pw:
    if t not in seen:
        seen.add(t); pw2.append(t)
body = "## 品玩一周精选\n\n| # | 标题 |\n|:--:|------|\n"
for i, t in enumerate(pw2, 1):
    body += f"| {i} | {t} |\n"
wf("品玩一周精选.md", f"品玩一周精选 · {DATE}", "品玩一周精选",
   body + "\n> 通道：bsk navigate + scrollTo + evaluate（urllib 返回空）")

# ---------- 17 知乎想法话题 ----------
idea = rd('zhihu_idea.txt')
topics = re.findall(r'\n([^\n]{2,20})\n(?:\d+ 人参与讨论|快来参与讨论吧|等[\d.]+ 万人参与讨论)', idea)
seen, tp = set(), []
for t in topics:
    t = t.strip()
    if t and t not in seen and not t.startswith(('创作', '消息', '私信', '发布', '等你', '推荐问题', '想法话题', '内容', '评论', '数据', '账号', '关注', '收益', '品牌', '众邀', '好物', 'AI 训练', '芝士', '盐选', '送礼物', '活动', '创作成长', '创作者', '版权', '榜单', '个人', '设置', '关联', 'MCN', '圆桌', '常见', '瓦力')):
        seen.add(t); tp.append(t)
body = "## 知乎想法话题（降级）\n\n" + "\n".join(f"- {t}" for t in tp[:20])
wf("知乎想法话题.md", f"知乎想法话题 · {DATE}", "知乎想法话题",
   body + "\n\n> ⚠️ **降级**：素材偏生活化/娱乐化（旅游/书法/植物/情感），硬核政经素材稀缺（与历史一致）")

# ---------- 18 知乎想法热榜 ----------
body = ("## 知乎想法热榜\n\n**不可用** —— `zhihu.com/pin/hot` 返回 HTTP **422 Unprocessable Entity**\n\n"
        "> ❌ 平台侧接口持续下线，2026-09-11 起连续第 **21** 日不可用；已降级采「知乎想法话题」替代。")
wf("知乎想法热榜.md", f"知乎想法热榜 · {DATE}", "知乎想法热榜", body)

# ---------- 19 小红书 ----------
body = ("## 小红书热榜（降级 · WebSearch 兜底）\n\n"
        "| # | 话题 | 说明 |\n|:--:|------|------|\n"
        "| 1 | #RED LAND 2026 岛民与保洁阿姨的双向温柔 | 5.5 万浏览 / 近 400 评论，年度最出圈素人帖 |\n"
        "| 2 | 国庆出行 · 邢台「太行泉城」攻略 | 冲上小红书热搜 TOP3，抖音 #国庆去哪玩 播放 8.2 亿 |\n"
        "| 3 | 《兰香如故》大结局 · 蒋欣谭松韵跨剧对话 | 剧集联动话题登小红书热榜 |\n"
        "| 4 | 秋日氛围感穿搭 / 长穿常新 | 季节切换类穿搭话题持续上位 |\n"
        "| 5 | 大理民宿空置率上升 · 50 元床位无人住 | 旅游供给过剩的田野观察 |\n")
wf("小红书热榜.md", f"小红书热榜 · {DATE}", "小红书热榜",
   body + "\n> ⚠️ **降级**：适配器未建；explore 页在无头环境下仅渲染页脚，改采公开趋势数据（WebSearch 兜底 5 条）")

print("\nDONE")
