# -*- coding: utf-8 -*-
import re, statistics, difflib
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
def stat(tag, b):
    cn=len(re.findall(r"[\u4e00-\u9fff]",b))
    sents=[s for s in re.split(r"[。！？\n]", b) if re.findall(r"[\u4e00-\u9fff]",s)]
    lens=[len(re.findall(r"[\u4e00-\u9fff]",s)) for s in sents]
    conn=["然而","此外","因此","值得注意的是","与此同时","更重要的是","综上","首先","其次","并且","同时","另一方面","总而言之","由此可见"]
    cdict={c:b.count(c) for c in conn if b.count(c)>0}
    formula=["不仅","而且","不只是","与其说","不是.{1,25}而是"]
    fc=sum(len(re.findall(p,b)) for p in formula)
    paras=[p.strip() for p in b.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    plens=[len(re.findall(r"[。！？]",p)) for p in paras]
    like=re.findall(r"[像仿佛如同似]", b)
    # 低频词：非常规词（黑话/口语/专名）近似——统计不同词数
    o=["【%s】" % tag, f"中文字符={cn}", f"句数={len(lens)} 句长均值={sum(lens)/len(lens):.1f} 标准差={statistics.pstdev(lens):.2f}",
       f"最长={max(lens)} 最短={min(lens)}",
       f"段数={len(paras)} 段句数标准差={statistics.pstdev(plens):.2f}" if len(plens)>1 else f"段数={len(paras)}",
       f"连接词={cdict} 合计{sum(cdict.values())} 密度{sum(cdict.values())/cn*1000:.2f}/千字",
       f"公式句={fc}", f"像类标记={len(like)}", f"破折号={b.count('——')}", f"加粗={len(re.findall(r'\*\*[^*]+\*\*',b))}"]
    return o
d=body(D/"草稿-限量这本账.md"); r=body(D/"润色稿-限量这本账.md")
out=stat("草稿",d)+[""]+stat("润色稿",r)+[""]
# 段落级 diff：找变化最大的段落
dp=[x.strip() for x in d.split("\n\n") if x.strip()]
rp=[x.strip() for x in r.split("\n\n") if x.strip()]
sm=difflib.SequenceMatcher(None, dp, rp, autojunk=False)
out.append(f"段落块相似度={sm.ratio():.4f} 草稿段={len(dp)} 润色段={len(rp)}")
Path(str(ROOT/".workbuddy"/"_stat2_B_out.txt")).write_text("\n".join(out),encoding="utf-8")
print("done")
