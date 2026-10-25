# -*- coding: utf-8 -*-
import re, sys
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
f = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"/"草稿-限量这本账.md"
t = f.read_text(encoding="utf-8")
# 去 frontmatter
lines = t.split("\n")
if lines[0].strip()=="---":
    for i in range(1,len(lines)):
        if lines[i].strip()=="---":
            lines = lines[i+1:]; break
body = "\n".join(lines)
# 截止到 素材溯源表
for mk in ["## 素材溯源表","## 素材溯源","## 标题决策说明","## 质量自检报告"]:
    if mk in body:
        body = body.split(mk)[0]
cn = len(re.findall(r"[\u4e00-\u9fff]", body))
h2 = len(re.findall(r"^##\s+", body, re.MULTILINE))
out = [f"正文中文字符(粗口径 [\u4e00-\u9fff]) = {cn}", f"H2 数 = {h2}"]
paras = [p.strip() for p in body.split("\n\n") if p.strip()]
longs = []
for i,p in enumerate(paras,1):
    c = len(re.findall(r"[\u4e00-\u9fff]", p))
    if c > 300:
        longs.append((i,c,p[:60]))
out.append(f"段落数 = {len(paras)}")
out.append(f">300字段落 = {len(longs)}")
for i,c,s in longs:
    out.append(f"  [{i}] {c}字: {s}...")
Path(str(ROOT/".workbuddy"/"_para_B_out.txt")).write_text("\n".join(out), encoding="utf-8")
print("done")
