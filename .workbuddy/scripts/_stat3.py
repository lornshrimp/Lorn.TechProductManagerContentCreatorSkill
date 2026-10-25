import re, difflib
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT / "drafts" / "2026-09-25" / "中美第八轮经贸磋商达成多项共识-从谈判到机制"

def body(txt):
    lines = txt.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i+1:]; break
    t = "\n".join(lines)
    for marker in ["## 素材溯源表", "## 视觉与配图", "## 配图搜索替换指令"]:
        if marker in t: t = t.split(marker)[0]
    return t

def stats(t):
    zh = re.findall(r"[\u4e00-\u9fff]", t)
    n = len(zh)
    paras = [p.strip() for p in t.split("\n") if p.strip() and not p.strip().startswith("#") and not p.strip().startswith("|")]
    lens = [len(re.findall(r"[\u4e00-\u9fff]", p)) for p in paras]
    d = {
        "中文字符": n,
        "段落数": len(paras),
        "平均段长": round(sum(lens)/len(lens), 1) if lens else 0,
        "最长段": max(lens) if lens else 0,
        "的": t.count("的"),
        "了": t.count("了"),
        "是": t.count("是"),
        "破折号—": t.count("——"),
        "分号；": t.count("；"),
        "而": t.count("而"),
        "因此": t.count("因此"),
        "综上": t.count("综上"),
        "值得注意": t.count("值得注意"),
        "首先其次": t.count("首先")+t.count("其次"),
        "不仅是": t.count("不仅"),
        "感叹号!": t.count("！"),
        "问号？": t.count("？"),
    }
    d["的字率%"] = round(d["的"]/n*100, 2)
    return d

a = body((D/"草稿-从谈判到机制.md").read_text(encoding="utf-8"))
b = body((D/"润色稿-从谈判到机制.md").read_text(encoding="utf-8"))
sa, sb = stats(a), stats(b)
out = ["指标 | 草稿 | 润色稿"]
for k in sa:
    out.append(f"{k} | {sa[k]} | {sb[k]}")
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
out.append(f"字符差异率 | - | {(1-sm.ratio())*100:.2f}%")
# paragraph-level diff
pa = [p.strip() for p in a.split("\n") if p.strip()]
pb = [p.strip() for p in b.split("\n") if p.strip()]
smp = difflib.SequenceMatcher(None, pa, pb, autojunk=False)
out.append(f"段落级相似度 | - | {smp.ratio():.4f}")
changed = 0
for i,(x,y) in enumerate(zip(pa,pb)):
    if x != y: changed += 1
out.append(f"逐段不一致段数 | - | {changed}/{len(pa)}")
Path(str(ROOT/".workbuddy"/"_wc_out.txt")).write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
