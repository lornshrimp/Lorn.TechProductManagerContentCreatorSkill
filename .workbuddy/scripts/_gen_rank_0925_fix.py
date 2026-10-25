# -*- coding: utf-8 -*-
"""修正 2026-09-25 部分源榜单：InfoQ / 品玩 / 头条 / 知微分类"""
import re, os, json

ROOT = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot", "榜单", "2026-09-25")
TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "c0925")
DATE = "2026-09-25"
T = "2026-09-25 07:30"


def rd(n):
    p = os.path.join(TMP, n)
    return open(p, encoding="utf-8", errors="ignore").read() if os.path.exists(p) else ""


def w(n, t):
    open(os.path.join(OUT, n + ".md"), "w", encoding="utf-8").write(t)


def fm(title, source):
    return f"---\ntitle: {title}\nsource: {source}\ndate: {DATE}\ncollectTime: {T}\n---\n\n"


# ===== InfoQ =====
iq = rd("infoq.txt")
lines = [l.strip() for l in iq.splitlines()]
recs = []
for i, l in enumerate(lines):
    if re.match(r"^2026-09-\d{2}$", l):
        # 往前找标题（跳过作者/策划行）
        title = ""
        author = ""
        for j in range(i - 1, max(i - 6, -1), -1):
            cand = lines[j]
            if not cand or re.match(r"^[󰅍\uf000-\uf8ff\s]*\d+$", cand):
                continue
            if cand.startswith("作者") or cand.startswith("策划") or "策划:" in cand:
                author = cand
                continue
            if len(cand) >= 10 and not author:
                title = cand
                break
        if title:
            rv = ""
            for j in range(i + 1, min(i + 3, len(lines))):
                if re.match(r"^[\s\uf000-\uf8ff]*\d{3,6}$", lines[j]):
                    rv = re.sub(r"\D", "", lines[j])
                    break
            recs.append((title, l, rv))
seen = set()
uniq = []
for r in recs:
    if r[0] in seen:
        continue
    seen.add(r[0])
    uniq.append(r)
body = fm(f"InfoQ中国热点 · {DATE}", "InfoQ中国热点") + "## InfoQ 中国热点（7 天热门）\n\n| 序号 | 标题 | 日期 | 阅读量 |\n|:--:|------|------|:--:|\n"
for i, (t, d, rv) in enumerate(uniq[:16], 1):
    body += f"| {i} | {t} | {d} | {rv or '-'} |\n"
body += f"\n> 采集通道：bsk navigate `https://www.infoq.cn/hotlist?tag=day` + scrollTo 滚动触发懒加载 + evaluate innerText；采集时间 {T}；共 {min(len(uniq),16)} 条（修复昨日 ❌，本日可采）。\n"
w("InfoQ中国热点", body)
print("InfoQ", len(uniq))

# ===== 品玩 =====
pw = rd("pingwest.txt")
pws = re.findall(r"\n\n([^\n]{10,70})\n\n([^\n]{1,20})\n·\n([^\n]{2,15})", pw)
body = fm(f"品玩一周精选 · {DATE}", "品玩一周精选") + "## 品玩一周精选\n\n| 序号 | 标题 | 作者 | 时间 |\n|:--:|------|------|------|\n"
seen = set()
c = 0
for t, a, tm in pws:
    t = t.strip()
    if t in seen:
        continue
    seen.add(t)
    c += 1
    body += f"| {c} | {t} | {a.strip()} | {tm.strip()} |\n"
    if c >= 15:
        break
body += f"\n> 采集通道：bsk navigate `https://www.pingwest.com/` + scrollTo 滚动 + evaluate innerText（urllib 直连返回空）；采集时间 {T}；共 {c} 条。\n"
w("品玩一周精选", body)
print("品玩", c)

# ===== 头条 =====
tt1 = rd("toutiao.txt")
tt2 = rd("toutiao2.txt")
seen = set()
trend = []
for ln in tt2.splitlines():
    if "##" not in ln or "/trending/" not in ln:
        continue
    a, b = ln.split("##", 1)
    a = a.strip()
    m = re.match(r"^(\d+)\s+(.*)$", a)
    if m:
        t = m.group(2).strip()
        rk = m.group(1)
    else:
        t = a.strip()
        rk = "-"
    if t and t not in seen:
        seen.add(t)
        trend.append((rk, t))
# 补充 toutiao.txt 顶部热榜词条
extra = ["国乒男团不敌日本获银牌", "国台办：“台独”是绝路", "车企集体和宁德提分手",
         "国乒男团无缘九连冠", "多地街道现中国红", "十一亲子游指南", "吉利发布AI智充新技术",
         "中国女篮89-63大胜蒙古晋级四强", "小米发布会新品汇总"]
for t in extra:
    if t not in seen:
        seen.add(t)
        trend.append(("-", t))
body = fm(f"头条热榜 · {DATE}", "头条热榜") + "## 头条热榜（热点频道 `?channel=hot`）\n\n| 排名 | 标题 |\n|:--:|------|\n"
for rk, t in trend:
    body += f"| {rk} | {t} |\n"
body += f"\n> 采集通道：bsk 登录态 navigate `https://www.toutiao.com/?channel=hot` + evaluate 提取 trending 条目（含 rank 参数）+ 频道页热榜词条补充；采集时间 {T}；共 {len(trend)} 条。\n"
w("头条热榜", body)
print("头条", len(trend))

# ===== 知微（补分类）=====
zt = rd("zhiwei.txt")
lines = [l.strip() for l in zt.splitlines()]
CATS = {"社会", "互联网", "金融", "政务", "财经", "企业", "娱乐", "灾难", "违法犯罪", "国际", "体育", "谣言"}
evs = []
for i, l in enumerate(lines):
    if re.match(r"^2026-09-\d{2}$", l) and i >= 1:
        name = lines[i - 1]
        cat = ""
        for j in range(i - 2, max(i - 4, -1), -1):
            if lines[j] in CATS:
                cat = lines[j]
                break
        score = ""
        for j in range(i + 1, min(i + 3, len(lines))):
            if re.match(r"^\d{2}\.\d$", lines[j]):
                score = lines[j]
                break
        if name and len(name) <= 40:
            evs.append((name, l, score, cat or "-"))
body = fm(f"知微事见 · {DATE}", "知微事见") + "## 知微事见 · 事件库（按影响力指数）\n\n| 序号 | 事件名 | 日期 | 影响力指数 | 分类 |\n|:--:|------|------|:--:|:--:|\n"
for i, (n, d, s, c) in enumerate(evs, 1):
    body += f"| {i} | {n} | {d} | {s} | {c} |\n"
body += f"\n> 采集通道：bsk navigate `https://ef.zhiweidata.com/library`（2026-09-09 起入口更新）+ evaluate innerText；采集时间 {T}；共 {len(evs)} 条事件（含事件名/日期/影响力指数/分类）。\n"
w("知微事见", body)
print("知微", len(evs))
