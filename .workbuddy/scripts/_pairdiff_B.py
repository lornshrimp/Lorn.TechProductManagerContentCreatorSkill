# -*- coding: utf-8 -*-
import re, difflib
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"
def body(p):
    t=p.read_text(encoding="utf-8"); lines=t.split("\n")
    if lines[0].strip()=="---":
        for i in range(1,len(lines)):
            if lines[i].strip()=="---": lines=lines[i+1:]; break
    b="\n".join(lines)
    for mk in ["## 素材溯源表","## 标题决策说明","## 质量自检报告","## 视觉与配图","## 配图搜索替换指令"]:
        if mk in b: b=b.split(mk)[0]
    return [x.strip() for x in b.split("\n\n") if x.strip()]
dp=body(D/"草稿-限量这本账.md"); rp=body(D/"润色稿-限量这本账.md")
sm=difflib.SequenceMatcher(None, dp, rp, autojunk=False)
out=[]
ops=sm.get_opcodes()
for tag,i1,i2,j1,j2 in ops:
    if tag=="equal": continue
    out.append(f"--- {tag} d[{i1}:{i2}] r[{j1}:{j2}] ---")
    for k in range(i1,i2):
        out.append(f"  旧: {dp[k][:110]}")
    for k in range(j1,j2):
        out.append(f"  新: {rp[k][:110]}")
Path(str(ROOT/".workbuddy"/"_pairdiff_B_out.txt")).write_text("\n".join(out),encoding="utf-8")
print(len(ops))
