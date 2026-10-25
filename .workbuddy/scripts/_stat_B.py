# -*- coding: utf-8 -*-
import re, sys
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
f = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"/"草稿-限量这本账.md"
t = f.read_text(encoding="utf-8")
lines = t.split("\n")
if lines[0].strip()=="---":
    for i in range(1,len(lines)):
        if lines[i].strip()=="---":
            lines=lines[i+1:]; break
body="\n".join(lines)
for mk in ["## 素材溯源表","## 标题决策说明","## 质量自检报告"]:
    if mk in body: body=body.split(mk)[0]
cn=len(re.findall(r"[\u4e00-\u9fff]",body))
# 句长
sents=[s for s in re.split(r"[。！？\n]", body) if re.findall(r"[\u4e00-\u9fff]",s)]
lens=[len(re.findall(r"[\u4e00-\u9fff]",s)) for s in sents]
import statistics
sd=statistics.pstdev(lens) if len(lens)>1 else 0
# 连接词
conn=["然而","此外","因此","值得注意的是","与此同时","更重要的是","综上","首先","其次","并且","同时","另一方面","总而言之","由此可见"]
cd_={c:body.count(c) for c in conn if body.count(c)>0}
# 路标/公式
formula=["不仅","而且","从.{1,8}到.{1,8}","不是.{1,20}而是","不只是","与其说"]
fc=sum(len(re.findall(p,body)) for p in formula)
# 破折号
dash=body.count("——")
bold=len(re.findall(r"\*\*[^*]+\*\*",body))
# 比喻标记
like=len(re.findall(r"[像仿佛如同似]",body))
# 段长
paras=[p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
plens=[len(re.findall(r"[。！？]",p)) for p in paras]
psd=statistics.pstdev(plens) if len(plens)>1 else 0
out=[f"正文中文字符 = {cn}", f"句数 = {len(lens)}  句长均值 = {sum(lens)/len(lens):.1f}  标准差 = {sd:.2f}",
     f"段落数 = {len(paras)}  段句数标准差 = {psd:.2f}",
     f"连接词 = {cd_}  合计 {sum(cd_.values())} 次（密度 {sum(cd_.values())/cn*1000:.2f}/千字）",
     f"公式句匹配 = {fc} 处", f"破折号（——） = {dash} 处", f"加粗金句（**..**） = {bold} 处",
     f"'像/仿佛/如同/似' = {like} 次",
     f"最长句 = {max(lens)}  最短句 = {min(lens)}"]
Path(str(ROOT/".workbuddy"/"_stat_B_out.txt")).write_text("\n".join(out),encoding="utf-8")
print("done")
