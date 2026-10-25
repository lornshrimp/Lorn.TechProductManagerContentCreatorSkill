import re, difflib, importlib.util
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT / "drafts" / "2026-09-25" / "中美第八轮经贸磋商达成多项共识-从谈判到机制"
spec = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

final = D / "终稿-从谈判到机制.md"
final_paras = [re.sub(r"\s+","",p) for p in re.split(r"\n{2,}", m._raw_body(final)) if len(re.sub(r"\s+","",p))>=60]

out=[]
for p in sorted(D.glob("*.md")):
    if not any(p.name.startswith(x) for x in ["知乎-","微信-","百家号-","CSDN-","头条-"]):
        continue
    body = m._raw_body(p)
    paras = [x.strip() for x in re.split(r"\n{2,}", body) if x.strip()]
    n = lambda s: re.sub(r"\s+","",s)
    copied=[]
    for i,pp in enumerate(paras):
        np_=n(pp)
        if len(np_)<60: continue
        if any(m.text_similarity(np_, fp)>=0.9 for fp in final_paras):
            copied.append(i)
    dup_res=[]
    cset=set(copied)
    for ci in copied:
        for j in range(ci):
            if j in cset: continue
            s=m.text_similarity(n(paras[ci]), n(paras[j]))
            if s>=0.55:
                dup_res.append((j,ci,s,paras[ci][:50],paras[j][:50]))
    out.append(f"=== {p.name} | paras={len(paras)} | copied={copied}")
    for j,ci,s,ctext,jtext in dup_res:
        out.append(f"  DUP ci={ci+1} j={j+1} sim={s:.0%}")
        out.append(f"    CI: {ctext}")
        out.append(f"    J : {jtext}")
Path(str(ROOT/".workbuddy"/"_diag_out.txt")).write_text("\n".join(out), encoding="utf-8")
print("done")
