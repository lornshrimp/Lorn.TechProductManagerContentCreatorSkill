# -*- coding: utf-8 -*-
import re
from pathlib import Path
base = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-09-13\车市价格带断裂-购车能力退出")
new = (base / "知乎-车市均价连涨为什么5万元以下的车反而没人造了.md").read_text(encoding="utf-8")
fin = (base / "终稿-车市均价上升的真相是便宜车消失了.md").read_text(encoding="utf-8")

def body(t):
    if t.startswith("---"):
        e = t.find("\n---", 3)
        t = t[e+4:] if e != -1 else t
    for mk in ["# 附属内容区域", "## 素材溯源", "## 配图详情"]:
        i = t.find(mk)
        if i != -1:
            t = t[:i]
    return t

pat = re.compile(r"\d+(?:\.\d+)?%?")
nb = set(pat.findall(body(new)))
fb = set(pat.findall(body(fin)))
out = []
out.append("== 知乎稿有、终稿无的数字token ==")
out.append(sorted(nb - fb))
out.append("== 终稿有、知乎稿无的数字token ==")
out.append(sorted(fb - nb))
open(base.parent.parent / "_numdiff.txt", "w", encoding="utf-8").write("\n".join(str(x) for x in out))
