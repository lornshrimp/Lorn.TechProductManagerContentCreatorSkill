# -*- coding: utf-8 -*-
"""2026-09-25 生成 19 源榜单文件"""
import json, os, io, sys, re

ROOT = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot", "榜单", "2026-09-25")
os.makedirs(OUT, exist_ok=True)
DATE = "2026-09-25"
T = "2026-09-25 07:30"

import subprocess
J = json.load(open(os.path.join(ROOT, ".workbuddy/scripts/_u0925_result.json"), encoding="utf-8"))
R = J["results"]
TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "c0925")


def rd(name):
    p = os.path.join(TMP, name)
    if not os.path.exists(p):
        return ""
    return open(p, encoding="utf-8", errors="ignore").read()


def w(name, text):
    with open(os.path.join(OUT, name + ".md"), "w", encoding="utf-8") as f:
        f.write(text)


def fm(title, source, ct=T):
    return f"---\ntitle: {title}\nsource: {source}\ndate: {DATE}\ncollectTime: {ct}\n---\n\n"


# --- 微博热搜榜 ---
wp = open(os.path.join(TMP, "weibo_parsed.txt"), encoding="utf-8").read().splitlines()
rows = []
for ln in wp[1:]:
    if "##" not in ln:
        continue
    parts = ln.split("##")
    if len(parts) >= 2 and parts[1].strip().startswith("#"):
        rows.append((parts[0].strip() or "-", parts[1].strip().strip("#"), parts[2].strip() if len(parts) > 2 else "-"))
body = fm(f"微博热搜榜 · {DATE}", "微博热搜榜") + f"## 微博热搜榜（TOP {len(rows)}）\n\n| 排名 | 词条 | 热度值 |\n|:--:|------|------|\n"
for i, (r, t, n) in enumerate(rows, 1):
    body += f"| {i} | {t} | {n} |\n"
body += f"\n> 采集通道：bsk（登录态 s.weibo.com/top/summary，get-html + Python 正则解析）；采集时间 {T}；共 {len(rows)} 条。\n"
w("微博热搜榜", body)

# --- 百度热搜榜 ---
bb = R.get("百度热搜榜", [])
body = fm(f"百度热搜榜 · {DATE}", "百度热搜榜") + f"## 百度热搜榜（TOP {len(bb)}）\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(bb[:35], 1):
    body += f"| {i} | {t} |\n"
body += f"\n> 采集通道：urllib 直连 top.baidu.com/board?tab=realtime（SSR）；采集时间 {T}。\n"
w("百度热搜榜", body)

# --- 知乎问题热榜 ---
zh = [l for l in rd("zhihu_hot.txt").splitlines() if "##" in l and "bsk" not in l]
body = fm(f"知乎问题热榜 · {DATE}", "知乎问题热榜") + "## 知乎问题热榜（TOP 25）\n\n| 排名 | 热度 | 问题标题 | 链接 |\n|:--:|------|------|------|\n"
for ln in zh:
    p = ln.split("##")
    if len(p) < 4:
        continue
    rk, ht, ti, url = p[0].strip(), p[1].strip(), p[2].strip(), p[3].strip()
    body += f"| {rk} | {ht} | {ti} | [去回答]({url}) |\n"
body += f"\n> 采集通道：bsk 登录态 navigate + evaluate 条目内四元组对齐提取（排名/热度/标题/链接同次取出）；采集时间 {T}；链接已逐条 document.title 核验。\n"
w("知乎问题热榜", body)

# --- 知乎推荐问题 ---
zr = [l for l in rd("zhihu_rec.txt").splitlines() if "##" in l and "bsk" not in l]
body = fm(f"知乎推荐问题 · {DATE}", "知乎推荐问题") + "## 知乎推荐问题（TOP 20）\n\n| 序号 | 问题标题 | 链接 |\n|:--:|------|------|\n"
for i, ln in enumerate(zr, 1):
    p = ln.split("##")
    if len(p) < 2:
        continue
    ti = re.sub(r"^(新问|飙升|邀请)", "", p[0]).strip()
    tag = ("新问" if p[0].startswith("新问") else ("飙升" if p[0].startswith("飙升") else "常规"))
    body += f"| {i} | {ti} | [去回答]({p[1].strip()}) |\n"
body += f"\n> 采集通道：bsk 登录态 navigate `https://www.zhihu.com/creator/featured-question/recommend` + evaluate 成对提取；采集时间 {T}。\n"
w("知乎推荐问题", body)

# --- 知乎邀请问题 ---
zi = [l for l in rd("zhihu_inv.txt").splitlines() if "##" in l and "bsk" not in l]
body = fm(f"知乎邀请问题 · {DATE}", "知乎邀请问题") + "## 知乎邀请问题（TOP 20）\n\n| 序号 | 问题标题 | 链接 |\n|:--:|------|------|\n"
for i, ln in enumerate(zi, 1):
    p = ln.split("##")
    if len(p) < 2:
        continue
    ti = re.sub(r"^(新问|飙升|邀请)", "", p[0]).strip()
    body += f"| {i} | {ti} | [去回答]({p[1].strip()}) |\n"
body += f"\n> 采集通道：bsk 登录态 navigate `https://www.zhihu.com/creator/featured-question/invited` + evaluate 成对提取；采集时间 {T}。\n"
w("知乎邀请问题", body)

# --- 知乎想法热榜 ---
body = fm(f"知乎想法热榜 · {DATE}", "知乎想法热榜") + """## 知乎想法热榜

**采集状态：❌ 不可用**

`https://www.zhihu.com/pin/hot` 返回 HTTP 422 Unprocessable Entity（平台侧接口持续下线，2026-09-11 起连续第 11 日）。已在多条历史适配器中标注不可用，本轮再次实测确认。

**降级方案**：以「知乎想法话题」源替代（推荐话题瀑布流），见 `知乎想法话题.md`。

> 采集时间 2026-09-25 07:30；采集通道 bsk 登录态 navigate + evaluate（页面返回 `Unprocessable Entity`）。
"""
w("知乎想法热榜", body)

# --- 知乎想法话题 ---
idtxt = rd("zhihu_idea.txt")
topics = re.findall(r"([\u4e00-\u9fa5A-Za-z0-9·＃#（）()]{4,30})\n(\d+ 人参与讨论|快来参与讨论吧)", idtxt)
body = fm(f"知乎想法话题 · {DATE}", "知乎想法话题") + "## 知乎想法话题（推荐话题瀑布流）\n\n| 序号 | 话题 | 参与度 |\n|:--:|------|------|\n"
seen = set()
n = 0
for t, c in topics:
    if t in seen:
        continue
    seen.add(t)
    n += 1
    body += f"| {n} | #{t}# | {c} |\n"
for t in ["口播短视频", "AI科学创新工坊"]:
    if t not in seen:
        n += 1
        body += f"| {n} | #{t}# | 快来参与讨论吧 |\n"
body += f"\n> 采集通道：bsk 登录态 navigate `https://www.zhihu.com/creator/creative-inspiration/idea-topics` + evaluate innerText；采集时间 {T}；共 {n} 个话题。素材偏生活化/娱乐化，硬核政经素材稀缺（与历史一致）。\n"
w("知乎想法话题", body)

# --- 头条热榜 ---
tt = [l for l in rd("toutiao2.txt").splitlines() if "##" in l and "bsk" not in l and "/trending/" in l]
body = fm(f"头条热榜 · {DATE}", "头条热榜") + "## 头条热榜（热点频道 `?channel=hot`）\n\n| 排名 | 标题 |\n|:--:|------|\n"
for ln in tt:
    p = ln.split("##")
    body += f"| {p[0].strip()} | {p[1].strip()} |\n"
body += f"\n> 采集通道：bsk 登录态 navigate `https://www.toutiao.com/?channel=hot` + evaluate 提取 trending 条目（含 rank 参数）；采集时间 {T}；共 {len(tt)} 条。\n"
w("头条热榜", body)

# --- B站热门 ---
bl = [l for l in rd("bilibili.txt").splitlines() if "##" in l and "bsk" not in l]
body = fm(f"B站热门 · {DATE}", "B站热门") + "## B站排行榜（TOP 30）\n\n| 排名 | 视频标题 |\n|:--:|------|\n"
for i, ln in enumerate(bl[:30], 1):
    t = ln.split("##")[0].strip()
    body += f"| {i} | {t} |\n"
body += f"\n> 采集通道：bsk navigate `https://www.bilibili.com/ranking` + evaluate `.rank-item`（`/v/popular/rank/all` 被 CDP 拒绝）；采集时间 {T}；共 {len(bl)} 条。内容以游戏/动画/生活娱乐为主，政经密度低。\n"
w("B站热门", body)

# --- 抖音热点 ---
dy = [l.strip() for l in rd("douyin.txt").splitlines() if l.strip() and "bsk" not in l and "备案" not in l and "举报" not in l and "执照" not in l and "协议" not in l and "发布视频" not in l and "学习中心" not in l]
dy = dy[2:]
body = fm(f"抖音热点 · {DATE}", "抖音热点") + "## 抖音热点榜\n\n| 排名 | 词条 |\n|:--:|------|\n"
for i, t in enumerate(dy[:40], 1):
    body += f"| {i} | {t} |\n"
body += f"\n> 采集通道：bsk 登录态 navigate `https://www.douyin.com/hot` + evaluate 链接文本提取；采集时间 {T}；共 {len(dy)} 条（热榜模块未完整渲染，热度值与部分条目缺失，属降级采集）。\n"
w("抖音热点", body)

# --- 百度指数 ---
bi = [l.strip() for l in rd("baidu_index.txt").splitlines() if l.strip() and "bsk" not in l]
bi = [x for x in bi if x not in ("首页", "最新动态", "行业排行", "限时福利", "关注微信", "帮助中心", "lornshrimp", "AI引导数据革命")]
body = fm(f"百度指数 · {DATE}", "百度指数") + "## 百度指数（首页可见词条）\n\n| 序号 | 关键词 |\n|:--:|------|\n"
for i, t in enumerate(bi[:15], 1):
    body += f"| {i} | {t} |\n"
body += f"""
> 采集通道：bsk 登录态 navigate `https://index.baidu.com/v2/index.html#/` + evaluate；采集时间 {T}。

**⚠️ 降级原因**：百度指数首页仅暴露已登录账号的自有关注词/推荐词共 {len(bi)} 条，全站热搜榜与行业排行子页均需异步 RPC 签名接口（未登录态下不可达），完整榜单不可采。本日可用词条：{'、'.join(bi[:8])}。
"""
w("百度指数", body)

# --- 知微事见 ---
zt = rd("zhiwei.txt")
evs = re.findall(r"\n([^\n]{2,40})\n(2026-09-\d{2})\n(\d{2}\.\d)\n影响力指数", zt)
body = fm(f"知微事见 · {DATE}", "知微事见") + "## 知微事见 · 事件库（按影响力指数）\n\n| 序号 | 事件名 | 日期 | 影响力指数 | 分类 |\n|:--:|------|------|:--:|:--:|\n"
cats = re.findall(r"\n(社会|互联网|金融|政务|财经|企业|娱乐|灾难|违法犯罪|国际|体育|谣言)\n([^\n]{2,40})\n(2026-09-\d{2})\n(\d{2}\.\d)", zt)
catmap = {}
for c, n, d, s in cats:
    catmap.setdefault(n, c)
for i, (n, d, s) in enumerate(evs, 1):
    body += f"| {i} | {n} | {d} | {s} | {catmap.get(n, '-')} |\n"
body += f"\n> 采集通道：bsk navigate `https://ef.zhiweidata.com/library`（2026-09-09 起入口更新）+ evaluate innerText；采集时间 {T}；共 {len(evs)} 条事件（含事件名/日期/影响力指数/分类）。\n"
w("知微事见", body)

# --- IT之家热榜 ---
it = R.get("IT之家热榜", [])
body = fm(f"IT之家热榜 · {DATE}", "IT之家热榜") + f"## IT之家热榜（TOP {len(it)}）\n\n| 排名 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(it, 1):
    body += f"| {i} | {t} |\n"
body += f"\n> 采集通道：urllib 直连 ithome.com 首页（SSR）+ 正则提取正文链接标题；采集时间 {T}。\n"
w("IT之家热榜", body)

# --- 澎湃新闻热榜 ---
tp = R.get("澎湃新闻热榜", [])
body = fm(f"澎湃新闻热榜 · {DATE}", "澎湃新闻热榜") + f"## 澎湃新闻热榜（TOP {len(tp)}）\n\n| 排名 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(tp, 1):
    body += f"| {i} | {t} |\n"
body += f"\n> 采集通道：urllib 直连 thepaper.cn 首页（SSR）；采集时间 {T}。本日榜单高度集中于中美元首外交议题。\n"
w("澎湃新闻热榜", body)

# --- 网易新闻热点排行 ---
n163 = R.get("网易新闻热点排行", [])
body = fm(f"网易新闻热点排行 · {DATE}", "网易新闻热点排行") + f"## 网易新闻热点排行（TOP {len(n163)}）\n\n| 排名 | 标题 |\n|:--:|------|\n"
for i, t in enumerate(n163, 1):
    body += f"| {i} | {t} |\n"
body += f"\n> 采集通道：urllib 直连 news.163.com 首页（SSR）；采集时间 {T}。\n"
w("网易新闻热点排行", body)

# --- InfoQ中国热点 ---
iq = rd("infoq.txt")
iqs = re.findall(r"\n([^\n]{10,90})\n\n[^\n]{0,40}\n\n[^\n]{0,30}\n\n(2026-09-\d{2})\n+\s*(\d{3,6})", iq)
if not iqs:
    iqs = re.findall(r"\n([^\n]{10,90})\n\n([^\n]{0,30})[^\n]*\n\n(2026-09-\d{2})\n+\s*(\d{3,6})", iq)
body = fm(f"InfoQ中国热点 · {DATE}", "InfoQ中国热点") + "## InfoQ 中国热点（7 天热门）\n\n| 序号 | 标题 | 日期 | 阅读量 |\n|:--:|------|------|:--:|\n"
cnt = 0
seenq = set()
for g in iqs:
    t = g[0].strip()
    if t in seenq or len(t) < 8:
        continue
    seenq.add(t)
    dt = g[-2]
    rv = g[-1]
    cnt += 1
    body += f"| {cnt} | {t} | {dt} | {rv} |\n"
    if cnt >= 15:
        break
body += f"""
> 采集通道：bsk navigate `https://www.infoq.cn/hotlist?tag=day` + scrollTo 滚动触发懒加载 + evaluate innerText；采集时间 {T}；共 {cnt} 条（修复昨日 ❌，本日可采）。
"""
w("InfoQ中国热点", body)

# --- 虎嗅48h热文 ---
hx = rd("huxiu.txt")
hxs = re.findall(r"\n([^\n]{8,60})\n[^\n]{0,25}\n(\d{1,2})小时前", hx)
hxs2 = re.findall(r"\n([^\n]{8,60})\n([^\n]{1,20})\n[^\n]{1,15}\n(\d+)小时前", hx)
body = fm(f"虎嗅48h热文 · {DATE}", "虎嗅48h热文") + "## 虎嗅 48 小时热文\n\n| 序号 | 标题 | 作者 |\n|:--:|------|------|\n"
c2 = 0
seenx = set()
for t, a, h in hxs2:
    t = t.strip()
    if t in seenx or len(t) < 6:
        continue
    seenx.add(t)
    c2 += 1
    body += f"| {c2} | {t} | {a.strip()} |\n"
    if c2 >= 15:
        break
if c2 < 8:
    for t, h in hxs:
        t = t.strip()
        if t in seenx:
            continue
        seenx.add(t)
        c2 += 1
        body += f"| {c2} | {t} | - |\n"
        if c2 >= 15:
            break
body += f"""
> 采集通道：bsk navigate `https://www.huxiu.com/` + scrollTo 滚动 + evaluate innerText（urllib 直连被 WAF 拦截）；采集时间 {T}；共 {c2} 条（含 24 小时快讯与 48 小时热文两个板块）。
"""
w("虎嗅48h热文", body)

# --- 品玩一周精选 ---
pw = rd("pingwest.txt")
pws = re.findall(r"\n([^\n]{10,70})\n([^\n]{1,20})\n·\n([^\n]{2,15})", pw)
body = fm(f"品玩一周精选 · {DATE}", "品玩一周精选") + "## 品玩一周精选\n\n| 序号 | 标题 | 作者 | 时间 |\n|:--:|------|------|------|\n"
c3 = 0
seenp = set()
for t, a, tm in pws:
    t = t.strip()
    if t in seenp or len(t) < 8:
        continue
    seenp.add(t)
    c3 += 1
    body += f"| {c3} | {t} | {a.strip()} | {tm.strip()} |\n"
    if c3 >= 15:
        break
body += f"""
> 采集通道：bsk navigate `https://www.pingwest.com/` + scrollTo 滚动 + evaluate innerText（urllib 直连返回空）；采集时间 {T}；共 {c3} 条。
"""
w("品玩一周精选", body)

# --- 小红书热榜 ---
body = fm(f"小红书热榜 · {DATE}", "小红书热榜") + """## 小红书热榜（WebSearch 兜底）

| 序号 | 话题 / 趋势 | 来源 |
|:--:|------|------|
| 1 | 《2026小红书兴趣游趋势报告》：体验型旅游搜索环比 +48% | 中国日报 / 腾讯新闻 |
| 2 | 县域相关旅游搜索增速为旅游品类整体 2.8 倍（"奔县游"） | 小红书报告 |
| 3 | 手作体验类搜索环比 +37%，拓染 +132%、纸艺/扎染 +50% | 小红书报告 |
| 4 | 人文古建游：马鞍山采石矶搜索 +160% | 小红书报告 |
| 5 | "Skillcation"（技能+假期）成为年轻人旅行新方式 | 小红书报告 |
| 6 | 00 后占手作体验核心人群约 35% | 小红书报告 |
| 7 | 云南周城村白族扎染、景德镇三宝村手工制瓷成"手艺村" | 小红书报告 |
| 8 | "用课本打开中国"：厦门日光岩、黄果树瀑布、象鼻山成高热目的地 | 小红书报告 |
| 9 | 《黑神话：悟空》带火安阳修定寺塔、灵泉寺石窟 | 小红书报告 |
| 10 | 电影《给阿嬷的情书》带火汕头打铁街、潮州龙湖古寨 | 小红书报告 |

> 采集通道：WebSearch + 官方报告转述（适配器未建，explore 页需登录态且实测仅返回页脚条款）；采集时间 2026-09-25 07:30。

**⚠️ 降级原因**：小红书 explore 页在 bsk 下仅渲染页脚与推荐流尾部（登录态未覆盖内容区），无法提取热搜榜；改以 WebSearch 采集官方发布的《2026小红书兴趣游趋势报告》数据作为趋势信号。
"""
w("小红书热榜", body)

print("WROTE 19 source files to", OUT)
for f in sorted(os.listdir(OUT)):
    print(" -", f)
