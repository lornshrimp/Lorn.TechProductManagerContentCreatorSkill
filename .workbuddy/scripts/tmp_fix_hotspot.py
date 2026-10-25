# -*- coding: utf-8 -*-
"""修正 IT之家/网易/虎嗅/头条/澎湃 + 补 知乎推荐/邀请/百度指数/想法热榜/小红书"""
import re, html, os, shutil
from pathlib import Path

BSK = Path("C:/Users/lorns/AppData/Local/Temp/bsk_raw")
RAW = Path("D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-14/_raw")
OUT = Path("D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-09-14")
DATE = "2026-09-14"; CT = "2026-09-14 07:15"

def rd(p):
    p = Path(p); return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
def wf(name, title, source, body, extra=""):
    txt = f"---\ntitle: {title}\ndate: {DATE}\nsource: {source}\ncollectTime: {CT}\n{extra}---\n\n{body}\n"
    (OUT / name).write_text(txt, encoding="utf-8"); print("WROTE", name, len(txt))

# ---------- IT之家（首页头条流，去导航） ----------
it = rd(RAW / "ithome.html")
noise = ("软媒", "立即下载", "App客户端", "关于我们", "投稿", "搜索", "登录", "注册", "版权", "IT之家", "RSS")
its = []
for m in re.finditer(r'<a[^>]+href="https?://(?:www\.)?ithome\.com/(?:0/\d+/\d+)?[^"]*"[^>]*>(.*?)</a>', it, re.S):
    t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip())
    if not (12 <= len(t) <= 60): continue
    if any(n in t for n in noise) or t.endswith(">"): continue
    its.append(t)
its = list(dict.fromkeys(its))
b = "## IT之家热榜\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(its[:30], 1): b += f"| {i} | {t} |\n"
wf("IT之家热榜.md", f"IT之家热榜 · {DATE}", "IT之家热榜", b)

# ---------- 网易新闻 ----------
ne = rd(RAW / "163.html")
nes = []
for m in re.finditer(r'<a[^>]+href="https?://(?:www\.)?163\.com/(?:news/article|dy/article|tech/article)[^"]*"[^>]*>(.*?)</a>', ne, re.S):
    t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip())
    if 10 <= len(t) <= 60: nes.append(t)
if len(nes) < 15:
    for m in re.finditer(r'<a[^>]+href="[^"]*163\.com[^"]*"[^>]*>(.*?)</a>', ne, re.S):
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip())
        if 12 <= len(t) <= 40 and not any(x in t for x in ("网易", "新闻", "邮箱", "游戏", "彩票", "直播", "视频", "财经", "体育", "汽车", "房产", "旅游", "教育", "健康", "数码", "手机")):
            nes.append(t)
nes = list(dict.fromkeys(nes))
b = "## 网易新闻热点排行\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(nes[:30], 1): b += f"| {i} | {t} |\n"
wf("网易新闻热点排行.md", f"网易新闻热点排行 · {DATE}", "网易新闻热点排行", b)

# ---------- 虎嗅（全文行扫描） ----------
hx = rd(BSK / "huxiu.txt")
hx = re.sub(r"^A new bsk version is available.*\n?", "", hx, flags=re.M)
lines = [l.strip() for l in hx.split("\n") if l.strip()]
cats = {"金融财经", "书影音", "社会文化", "前沿科技", "车与出行", "商业消费", "观点", "国际热点", "出海", "3C数码", "健康", "游戏娱乐", "医疗", "其他", "24小时", "源流", "视频"}
hxs = []
for i, l in enumerate(lines):
    if l in cats and i + 1 < len(lines) and 8 <= len(lines[i+1]) <= 45:
        hxs.append((l, lines[i+1]))
seen = set(); h2 = []
for c, t in hxs:
    if t in seen: continue
    seen.add(t); h2.append((c, t))
b = "## 虎嗅48h热文\n\n| 序号 | 分类 | 标题 |\n|:--:|:--:|------|\n"
for i, (c, t) in enumerate(h2, 1): b += f"| {i} | {c} | {t} |\n"
wf("虎嗅48h热文.md", f"虎嗅48h热文 · {DATE}", "虎嗅48h热文", b)

# ---------- 头条热榜（清洗） ----------
tt = re.sub(r"^A new bsk version is available.*\n?", "", rd(BSK / "toutiao.txt"), flags=re.M)
noise2 = {"下载头条APP添加到桌面关于头条反馈", "产品经理独孤虾", "关注", "推荐", "北京", "视频", "财经", "科技", "热点", "国际", "更多", "消息", "发布作品", "关于头条", "反馈"}
tts = []
for l in tt.split("\n"):
    l = l.strip()
    if not l or l in noise2: continue
    if re.search(r"(小时前|分钟前|评论|\d+图)$", l): continue
    if 5 <= len(l) <= 30 and "℃" not in l: tts.append(l)
tts = list(dict.fromkeys(tts))
b = "## 头条热榜（热点频道）\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(tts[:20], 1): b += f"| {i} | {t} |\n"
wf("头条热榜.md", f"头条热榜 · {DATE}", "头条热榜", b)

# ---------- 澎湃新闻 ----------
tp = re.sub(r"^A new bsk version is available.*\n?", "", rd(BSK / "thepaper.txt"), flags=re.M)
keys = ("习近平", "金砖", "王毅", "媒体", "江苏", "苏州", "辟谣", "特朗普", "卫国戍边", "话剧", "水均益")
tps = []
for l in tp.split("\n"):
    l = l.strip()
    if 12 <= len(l) <= 70 and any(k in l for k in keys): tps.append(l)
tps = list(dict.fromkeys(tps))
b = "## 澎湃新闻热榜（要闻）\n\n| 序号 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(tps[:20], 1): b += f"| {i} | {t} |\n"
wf("澎湃新闻热榜.md", f"澎湃新闻热榜 · {DATE}", "澎湃新闻热榜", b)

# ---------- 知乎推荐问题 / 邀请问题（重命名+规范名） ----------
for src, dst, title, sname in [
    ("zhihu_recommend_snap.txt", "知乎推荐问题.md", f"知乎推荐问题 · {DATE}", "知乎推荐问题"),
    ("zhihu_invited_snap.txt", "知乎邀请问题.md", f"知乎邀请问题 · {DATE}", "知乎邀请问题"),
]:
    s = re.sub(r"^A new bsk version is available.*\n?", "", rd(BSK / src), flags=re.M)
    qs = []
    for m in re.finditer(r'link "([^"]{10,90})"', s):
        t = m.group(1)
        if t.startswith("欢迎进入") or t.startswith("创作分"): continue
        t = re.sub(r"^(飙升|火爆|新问|热榜|邀请)\s+", "", t).strip()
        if t not in qs: qs.append(t)
    b = f"## {sname}\n\n| 序号 | 问题标题 | 状态 |\n|:--:|------|------|\n"
    for i, t in enumerate(qs, 1): b += f"| {i} | {t} | 待处理 |\n"
    wf(dst, title, sname, b)

# 删除旧命名
for old in ["zhihu_recommend.md", "zhihu_invited.md"]:
    p = OUT / old
    if p.exists(): p.unlink(); print("DEL", old)

# ---------- 百度指数 ----------
bi = re.sub(r"^A new bsk version is available.*\n?", "", rd(BSK / "baiduindex.txt"), flags=re.M)
words = [l.strip() for l in bi.split("\n") if 2 <= len(l.strip()) <= 20 and l.strip() not in ("首页","最新动态","行业排行","限时福利","关注微信","帮助中心","lornshrimp")]
b = ("## 百度指数（行业品牌榜，页面改版仅余品牌词条）\n\n⚠️ 采集说明：百度指数 v2 页面为登录态 SPA，本次 bsk 登录态下仅渲染出品牌/明星词条列表，未渲染搜索指数曲线与完整热词榜。\n\n"
     "| 序号 | 词条 |\n|:--:|------|\n")
for i, t in enumerate(dict.fromkeys(words), 1): b += f"| {i} | {t} |\n"
wf("百度指数.md", f"百度指数 · {DATE}", "百度指数", b)

# ---------- 知乎想法热榜（❌ 平台侧下线） ----------
pin = rd(BSK / "zhihu_pin.txt").strip()
b = ("## 知乎想法热榜\n\n❌ **本日采集失败**：`https://www.zhihu.com/pin/hot` 返回 HTTP 422 Unprocessable Entity，"
     "页面标题为空、正文无内容。该入口自 2026-09-11 起连续多日 422，判定为平台侧下线（非登录态问题）。\n\n"
     "**降级说明**：知乎想法类内容已通过「知乎想法话题」源（`/creator/creative-inspiration/idea-topics`）覆盖，"
     "该源本日采集成功，共提取 9 个推荐话题。\n\n"
     f"原始返回：`{pin[:120]}`\n")
wf("知乎想法热榜.md", f"知乎想法热榜 · {DATE}", "知乎想法热榜", b)

print("DONE")
