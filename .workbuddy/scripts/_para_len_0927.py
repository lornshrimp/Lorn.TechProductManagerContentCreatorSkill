# -*- coding: utf-8 -*-
import re
from pathlib import Path
D = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-09-27")
files = [
 "中美300亿美元对等降税落地-排除清单才是核心清单/润色稿-降了-300-亿美元关税，芯片一件没提，这比降税本身更值得看.md",
 "油价调控半年四次压缩涨幅-成品油定价这本账/润色稿-油价调控半年四次，少涨的-435-元到底谁承担.md",
 "盖茨警告AI或致十亿人死亡-风险定义权与立法门槛/润色稿-盖茨说-AI-或致十亿人死亡，但重点不在这个数字.md",
]
for f in files:
    c = (D/f).read_text(encoding="utf-8")
    s = 0
    if c.startswith("---"):
        e = c.find("\n---",3); s = e+4
    m = re.search(r"^# .*$", c[s:], re.MULTILINE)
    if m: s += m.end()
    body = c[s:]
    mx = []
    for blk in re.split(r"\n\s*\n", body):
        b = blk.strip()
        if not b or b.startswith(("#","|",">","-","*","1.","2.","3.","4.","[","```")): continue
        cn = len(re.findall(r"[\u4e00-\u9fff]", b))
        if cn > 200: mx.append(cn)
    print(Path(f).name[:24], "H2:", len(re.findall(r"^## ", body, re.MULTILINE)), "超200字段落:", sorted(mx, reverse=True)[:5])
