# -*- coding: utf-8 -*-
import re, difflib, runpy
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
ns = runpy.run_path(str(ROOT/".workbuddy"/"scripts"/"规范校验.py"), run_name="_m")
cbc = ns["count_body_chars"]; trunc = ns["BODY_TRUNCATE_MARKERS"]
D = ROOT/"drafts"/"2026-09-25"/"欧盟要求中国「自愿限制」汽车出口-限量这本账"
files = {"终稿":"终稿-限量这本账.md","知乎":"知乎-限量这本账.md","微信":"微信-限量这本账.md",
         "头条":"头条-限量这本账.md","百家号":"百家号-限量这本账.md","CSDN":"CSDN-限量这本账.md"}
def norm(n):
    t=(D/n).read_text(encoding="utf-8",errors="ignore")
    if t.startswith("---"):
        e=t.find("\n---",3)
        if e!=-1: t=t[e+4:]
    t=re.sub(r"^#\s+.*$","",t,flags=re.MULTILINE)
    for m in trunc:
        i=t.find(m)
        if i!=-1: t=t[:i]; break
    return re.sub(r"\s+","",t)
out=["=== 字数（count_body_chars 口径）==="]
sizes={}
for k,n in files.items():
    c=cbc(D/n); sizes[k]=c
    out.append(f"{k}: {c} 字")
z=sizes["终稿"]
out.append("")
out.append("=== 保真比（平台稿/终稿）===")
ratio={"知乎":0.90,"微信":0.85,"头条":0.70,"百家号":0.70,"CSDN":0.70}
for k in ["知乎","微信","头条","百家号","CSDN"]:
    r=sizes[k]/z
    out.append(f"{k}: {r*100:.2f}%  底线 {ratio[k]*100:.0f}%  [{'OK' if r>=ratio[k] else 'XX'}]")
out.append("")
out.append("=== 平台两两相似度（<85%）+ 与终稿（<99%）===")
plats=["知乎","微信","头条","百家号","CSDN"]
def sm(a,b): return difflib.SequenceMatcher(None,a,b,autojunk=False).ratio()
mx=0
for i in range(len(plats)):
    for j in range(i+1,len(plats)):
        r=sm(norm(files[plats[i]]),norm(files[plats[j]]))
        mx=max(mx,r)
        out.append(f"{plats[i]} vs {plats[j]}: {r:.4f} [{'OK' if r<0.85 else 'XX'}]")
out.append("")
nz=norm(files["终稿"])
for k in plats:
    r=sm(nz,norm(files[k]))
    out.append(f"终稿 vs {k}: {r:.4f} [{'OK' if r<0.99 else 'XX'}]")
out.append(f"平台两两最大相似度 = {mx:.4f}")
out.append("")
out.append("=== 结构 ===")
for k in files:
    t=(D/files[k]).read_text(encoding="utf-8")
    body=t
    for m in trunc:
        i=body.find(m)
        if i!=-1: body=body[:i]; break
    h2=len(re.findall(r"^##\s+",body,re.M))
    paras=[p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    longs=[(i,len(re.findall(r"[\u4e00-\u9fff]",p))) for i,p in enumerate(paras,1) if len(re.findall(r"[\u4e00-\u9fff]",p))>300]
    out.append(f"{k}: H2={h2} 超长段={len(longs)} {longs}")
Path(str(ROOT/".workbuddy"/"_plat_B_out.txt")).write_text("\n".join(out),encoding="utf-8")
print("done")
