# -*- coding: utf-8 -*-
import re, statistics
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"
def body(p):
    t=p.read_text(encoding="utf-8"); lines=t.split("\n")
    if lines[0].strip()=="---":
        for i in range(1,len(lines)):
            if lines[i].strip()=="---": lines=lines[i+1:]; break
    b="\n".join(lines)
    b=re.sub(r"^#\s+.*$","",b,flags=re.MULTILINE)
    for mk in ["## 素材溯源表","## 标题决策说明","## 质量自检报告","## 视觉与配图","## 配图搜索替换指令"]:
        if mk in b: b=b.split(mk)[0]
    return b.strip()
def row(tag,b):
    cn=len(re.findall(r"[\u4e00-\u9fff]",b))
    paras=[p.strip() for p in b.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    pl=[len(re.findall(r"[\u4e00-\u9fff]",p)) for p in paras]
    return dict(cn=cn, h2=len(re.findall(r"^##\s+",b,re.M)), paras=len(paras),
        avg=sum(pl)/len(pl), mx=max(pl),
        de=len(re.findall("的",b)), le=len(re.findall("了",b)), shi=len(re.findall("是",b)),
        dash=b.count("——"), semi=b.count("；"), er=len(re.findall("而",b)),
        q=len(re.findall("？",b)), ex=len(re.findall("！",b)),
        yinci=sum(x in b for x in ["因此","综上","值得注意","首先","其次","不仅"]),
        dbl=len(re.findall(r"\*\*[^*]+\*\*",b)))
d=row("d",body(D/"草稿-限量这本账.md")); r=row("r",body(D/"润色稿-限量这本账.md"))
keys=[("cn","正文中文字符"),("h2","正文 H2 小标题数"),("paras","段落数"),("avg","平均段长"),("mx","最长段"),
 ("de","\"的\"字次数"),("le","\"了\"字次数"),("shi","\"是\"字次数"),("dash","破折号——"),("semi","分号；"),
 ("er","\"而\"字"),("q","问号？"),("ex","感叹号！"),("yinci","因此/综上/值得注意/首先其次/不仅"),("dbl","加粗句**..**")]
out=["| 指标 | 草稿 | 润色稿 | 变动 |","|---|:--:|:--:|:--:|"]
for k,name in keys:
    a,b2=d[k],r[k]
    delta=b2-a
    if isinstance(a,float):
        out.append(f"| {name} | {a:.1f} | {b2:.1f} | {delta:+.1f} |")
    else:
        out.append(f"| {name} | {a} | {b2} | {delta:+d} |")
out.append(f"| \"的\"字率 | {d['de']/d['cn']*100:.2f}% | {r['de']/r['cn']*100:.2f}% | {(r['de']/r['cn']-d['de']/d['cn'])*100:+.2f}pp |")
Path(str(ROOT/".workbuddy"/"_adv_B_out.txt")).write_text("\n".join(out),encoding="utf-8")
print("done")
