# -*- coding: utf-8 -*-
import importlib.util, difflib, re
from pathlib import Path
ROOT=Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
spec=importlib.util.spec_from_file_location("g",str(ROOT/".workbuddy"/"scripts"/"规范校验.py"))
g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
d=ROOT/"drafts"/"2026-09-25"/"美团抽成太多-25元外卖的三方账"
a=g._raw_body(sorted(d.glob("草稿-*.md"))[0])
b=g._raw_body(sorted(d.glob("润色稿-*.md"))[0])
A=[x.strip() for x in a.split("\n") if x.strip()]
B=[x.strip() for x in b.split("\n") if x.strip()]
sm=difflib.SequenceMatcher(a=A,b=B,autojunk=False)
out=["段落数 草稿=%d 润色=%d"%(len(A),len(B))]
n=0
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=="equal": continue
    n+=1
    out.append("### [%02d] %s  draft[%d:%d] -> polish[%d:%d]"%(n,tag,i1,i2,j1,j2))
    for x in A[i1:i2]: out.append("  - "+x)
    for x in B[j1:j2]: out.append("  + "+x)
(ROOT/".workbuddy"/"_diff_C.txt").write_text("\n".join(out),encoding="utf-8")

dc=g.count_body_chars(d/"草稿-三方账.md"); pc=g.count_body_chars(d/"润色稿-三方账.md")
sa=re.sub(r"\s","",a); sb=re.sub(r"\s","",b)
r=difflib.SequenceMatcher(None,sa,sb,autojunk=False).ratio()
print("DONE 变更块=%d"%n)
print("草稿=%d 润色=%d 去字率=%.2f%%"%(dc,pc,(dc-pc)/dc*100))
print("全文相似度=%.4f 差异率=%.2f%%"%(r,(1-r)*100))
