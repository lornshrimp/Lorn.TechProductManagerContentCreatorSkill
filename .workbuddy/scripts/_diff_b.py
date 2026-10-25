# -*- coding: utf-8 -*-
import re, difflib, statistics
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"
def body(p):
    t=p.read_text(encoding="utf-8"); lines=t.split("\n")
    if lines[0].strip()=="---":
        for i in range(1,len(lines)):
            if lines[i].strip()=="---": lines=lines[i+1:]; break
    b="\n".join(lines)
    for mk in ["## 素材溯源表","## 标题决策说明","## 质量自检报告","## 视觉与配图","## 配图搜索替换指令","## 素材溯源"]:
        if mk in b: b=b.split(mk)[0]
    return b.strip()
d=body(D/"草稿-限量这本账.md"); r=body(D/"润色稿-限量这本账.md")
ratio=difflib.SequenceMatcher(None,d,r,autojunk=False).ratio()
diff=(1-ratio)*100
cd_=len(re.findall(r"[\u4e00-\u9fff]",d)); cr=len(re.findall(r"[\u4e00-\u9fff]",r))
out=[f"草稿正文中文字符 = {cd_}", f"润色稿正文中文字符 = {cr}",
     f"字符级相似度 = {ratio:.4f}  → 差异率 = {diff:.2f}%",
     f"去字率 = {(cd_-cr)/cd_*100:.2f}%  （{'OK ≤5%' if (cd_-cr)/cd_*100<=5 else 'XX 超标'}）",
     f"润色稿/草稿 = {cr/cd_*100:.2f}%  （≥95% 底线）",
     f"差异率判定 = {'OK 真实编辑(≥5%)' if diff>=5 else 'XX 疑似脚本复制(<5%)'}"]
# 结构：H2 数 + 超长段
h2=len(re.findall(r"^##\s+", r, re.MULTILINE))
paras=[p.strip() for p in r.split("\n\n") if p.strip() and not p.strip().startswith("#")]
longs=[(i,len(re.findall(r"[\u4e00-\u9fff]",p)),p[:40]) for i,p in enumerate(paras,1) if len(re.findall(r"[\u4e00-\u9fff]",p))>300]
sents=[s for s in re.split(r"[。！？\n]", r) if re.findall(r"[\u4e00-\u9fff]",s)]
lens=[len(re.findall(r"[\u4e00-\u9fff]",s)) for s in sents]
conn=["然而","此外","因此","值得注意的是","与此同时","更重要的是","综上","首先","其次","并且","同时","另一方面","总而言之","由此可见"]
cdict={c:r.count(c) for c in conn if r.count(c)>0}
out += [f"H2 数 = {h2}", f"段落数 = {len(paras)}  超 300 字段落 = {len(longs)}",
        f"句数 = {len(lens)}  句长均值 = {sum(lens)/len(lens):.1f}  标准差 = {statistics.pstdev(lens):.2f}",
        f"连接词 = {cdict} 合计 {sum(cdict.values())} 次 密度 {sum(cdict.values())/cr*1000:.2f}/千字",
        f"破折号（——） = {r.count('——')} 处",
        f"加粗句 = {len(re.findall(r'\*\*[^*]+\*\*', r))} 处"]
Path(str(ROOT/".workbuddy"/"_diff_B_out.txt")).write_text("\n".join(out),encoding="utf-8")
print("done")
