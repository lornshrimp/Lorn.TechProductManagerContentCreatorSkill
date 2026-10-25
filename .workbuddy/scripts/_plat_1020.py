# -*- coding: utf-8 -*-
"""2026-10-20 三选题平台稿实测矩阵"""
import io, sys, json, difflib
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import importlib.util
spec = importlib.util.spec_from_file_location('chk', r'.workbuddy/scripts/规范校验.py')
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = "2026-10-20"
JOBS = [
    ("多地社银贷-灵活就业贷款缴社保-保障成本金融化这本账", "社银贷这本账",
     ["知乎", "微信", "百家号", "CSDN", "头条"]),
    ("圆通进线即投诉-一条考核规则把咨询生产成投诉", "投诉工单这本账",
     ["知乎", "微信", "百家号", "CSDN", "头条"]),
    ("近视防控镜片批发30零售1980-66倍价差这本账", "镜片价差这本账",
     ["知乎", "微信", "百家号", "CSDN", "头条"]),
]

out = {}
for dn, fn, plats in JOBS:
    d = ROOT / "drafts" / D / dn
    fin = d / f"终稿-{fn}.md"
    fc = chk.count_body_chars(fin)
    fb = chk.extract_body_text(fin)
    rows = []
    bodies = {}
    for pl in plats:
        p = d / f"{pl}-{fn}.md"
        n = chk.count_body_chars(p)
        b = chk.extract_body_text(p)
        bodies[pl] = b
        rows.append({
            "platform": pl,
            "chars": n,
            "ratio": round(n / fc, 4),
            "sim_final": round(difflib.SequenceMatcher(None, b, fb, autojunk=False).ratio(), 4),
            "anchors": chk.check_anchor_quality(p),
        })
    worst = 0
    pair = ""
    for i in range(len(plats)):
        for j in range(i + 1, len(plats)):
            s = difflib.SequenceMatcher(None, bodies[plats[i]], bodies[plats[j]], autojunk=False).ratio()
            if s > worst:
                worst, pair = s, f"{plats[i]}×{plats[j]}"
    nfig = {pl: len(set(chk.re.findall(r"\[配图\s*(\d+)\]", (d / f"{pl}-{fn}.md").read_text(encoding='utf-8')))) for pl in plats}
    draft = d / f"草稿-{fn}.md"
    polish = d / f"润色稿-{fn}.md"
    dr = 1 - difflib.SequenceMatcher(None, chk.extract_body_text(draft), chk.extract_body_text(polish), autojunk=False).ratio()
    out[fn] = {
        "final_chars": fc,
        "draft_chars": chk.count_body_chars(draft),
        "polish_chars": chk.count_body_chars(polish),
        "diff_draft_polish": round(dr, 4),
        "rows": rows,
        "worst_pairwise": round(worst, 4),
        "worst_pair": pair,
        "fig_count": nfig,
    }
    print(f"\n=== {fn} ===  终稿 {fc}")
    for r in rows:
        print(f"  {r['platform']}: {r['chars']} ({r['ratio']*100:.1f}%)  vs终稿 {r['sim_final']*100:.2f}%  配图{nfig[r['platform']]}  锚{r['anchors']}")
    print(f"  两两最高 {worst*100:.2f}% ({pair})")
    print(f"  草稿 {out[fn]['draft_chars']} → 润色 {out[fn]['polish_chars']}  差异率 {dr*100:.2f}%")

(ROOT / ".workbuddy" / "scripts" / "_metrics_2026-10-20.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("\nsaved")
