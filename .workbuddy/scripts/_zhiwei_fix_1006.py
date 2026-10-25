# -*- coding: utf-8 -*-
import os, re
T = os.path.join(os.environ.get("TEMP", ""), "bsk1006")
BASE = r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体"
OUTD = os.path.join(BASE, "hotspot", "榜单", "2026-10-06")
DATE = "2026-10-06"

raw = ""
for fn in ["zhiwei.txt", "zhiwei2.txt", "zhiwei3.txt"]:
    p = os.path.join(T, fn)
    if os.path.exists(p):
        raw += open(p, encoding="utf-8", errors="ignore").read() + "\n"

lines = [l.strip() for l in raw.splitlines() if l.strip()]
ev = []
seen = set()
for i, l in enumerate(lines):
    if re.match(r"^20\d{2}-\d{2}-\d{2}$", l) and i >= 1:
        name = lines[i - 1]
        if i + 3 < len(lines) and lines[i + 2] == "影响力指数":
            val = lines[i + 1]
            cat = lines[i + 3]
        else:
            val, cat = "", ""
        if 3 < len(name) < 40 and not re.match(r"^20\d{2}", name):
            key = name
            if key not in seen:
                seen.add(key)
                ev.append((name, l, val, cat))
# 补抓 zhiwei3 的标签与前段（另一部分事件）
# 尝试抓「事件名 日期 影响力指数」模式若上面为空
if len(ev) < 5:
    for i, l in enumerate(lines):
        if l == "影响力指数" and i >= 2:
            val = lines[i - 1]
            name = lines[i - 2]
            date = lines[i - 3] if re.match(r"^20\d{2}-\d{2}-\d{2}$", lines[i - 3]) else ""
            cat = lines[i + 1] if i + 1 < len(lines) else ""
            if name not in seen:
                seen.add(name)
                ev.append((name, date, val, cat))

body = f"## 知微事见·事件库（{len(ev)} 条）\n\n| 序号 | 事件 | 日期 | 影响力指数 | 分类 |\n|------|------|------|-----------|------|\n"
body += "\n".join(f"| {i} | {n} | {d} | {v} | {c} |" for i, (n, d, v, c) in enumerate(ev, 1))

p = os.path.join(OUTD, "知微事见.md")
with open(p, "w", encoding="utf-8") as f:
    f.write(f"---\ntitle: 知微事见 · {DATE}\ndate: {DATE}\nsource: 知微事见\ncollectTime: 2026-10-06 08:45\n---\n\n" + body + "\n")
print("知微 events:", len(ev))
for e in ev:
    print("  ", e)
