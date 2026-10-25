# -*- coding: utf-8 -*-
"""InfoQ 精确解析 v4：标题=日期上方最远的非作者长行"""
import re, os, json

ROOT = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体"
OUT = os.path.join(ROOT, "hotspot", "榜单", "2026-09-25")
TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "c0925")
DATE, T = "2026-09-25", "2026-09-25 07:30"

PUA = re.compile(r"[\ue000-\uf8ff\U000f0000-\U000fffff]")
iq = open(os.path.join(TMP, "infoq.txt"), encoding="utf-8", errors="ignore").read()
lines = [PUA.sub("", l).strip() for l in iq.splitlines()]
idx = [i for i, l in enumerate(lines) if re.match(r"^2026-09-\d{2}$", l)]

    AUTH = re.compile(r"^(作者|策划|译者|文\s*[:：]|来源)|策划:")
    nb = []
    for j in range(i - 1, max(i - 8, -1), -1):
        c = lines[j]
        if not c or c in CATS or re.match(r"^[\d\s]+$", c):
            continue
        nb.append(c)
        if len(nb) >= 3:
            break
    if not nb:
        continue
    if AUTH.search(nb[0]):            # [0]=作者行
        title = nb[1] if len(nb) > 1 else nb[0]
    else:                             # [0]=作者行(无AUTH特征)或摘要 → 取更远的
        title = nb[2] if len(nb) > 2 else (nb[1] if len(nb) > 1 else nb[0])
    rv = ""
    for j in range(i + 1, min(i + 3, len(lines))):
        m = re.search(r"(\d{3,6})", lines[j])
        if m:
            rv = m.group(1)
            break
    recs.append((title, lines[i], rv))

seen, uniq = set(), []
for r in recs:
    if r[0] in seen:
        continue
    seen.add(r[0])
    uniq.append(r)

body = (f"---\ntitle: InfoQ中国热点 · {DATE}\nsource: InfoQ中国热点\ndate: {DATE}\ncollectTime: {T}\n---\n\n"
        "## InfoQ 中国热点（7 天热门）\n\n| 序号 | 标题 | 日期 | 阅读量 |\n|:--:|------|------|:--:|\n")
for i, (t, d, rv) in enumerate(uniq[:16], 1):
    body += f"| {i} | {t} | {d} | {rv or '-'} |\n"
body += (f"\n> 采集通道：bsk navigate `https://www.infoq.cn/hotlist?tag=day` + scrollTo 滚动触发懒加载 + evaluate innerText；"
         f"采集时间 {T}；共 {min(len(uniq),16)} 条（修复昨日 ❌，本日可采）。\n")
open(os.path.join(OUT, "InfoQ中国热点.md"), "w", encoding="utf-8").write(body)
json.dump([[r[0], r[1], r[2]] for r in uniq[:16]],
          open(os.path.join(ROOT, ".workbuddy/scripts/_infoq_0925.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("InfoQ", len(uniq))
