# -*- coding: utf-8 -*-
"""诊断 B 题各平台稿的连贯性门禁命中情况"""
import sys, io, re
from pathlib import Path
import importlib.util

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
sys.modules["chk"] = chk
spec.loader.exec_module(chk)

d = ROOT / "drafts/2026-09-22/中办国办分类推进高校改革-教育供给的错配账"
final = d / "终稿-教育供给的错配账.md"

plat_files = sorted([p for p in d.glob("*.md") if p.name.split("-")[0] in
                     {"知乎", "微信", "百家号", "CSDN", "头条"}])

out = []
for p in plat_files:
    iss = chk.check_platform_coherence(p, final)
    out.append(f"=== {p.name} : {len(iss)} 项 ===")
    for i in iss:
        out.append(i)
    # 若命中，打印段落诊断
    if iss:
        body = chk._raw_body(p)
        paras = [x.strip() for x in re.split(r"\n{2,}", body) if x.strip()]
        def _n(x):
            return re.sub(r"\s+", "", x)
        fparas = [_n(x) for x in re.split(r"\n{2,}", chk._raw_body(final)) if len(_n(x)) >= 60]
        copied = []
        for i, pp in enumerate(paras):
            npp = _n(pp)
            if len(npp) < 60:
                continue
            if any(chk.text_similarity(npp, fp) >= 0.9 for fp in fparas):
                copied.append(i)
        copied_set = set(copied)
        for ci in copied:
            for j in range(ci):
                if j in copied_set:
                    continue
                s = chk.text_similarity(_n(paras[ci]), _n(paras[j]))
                if s >= 0.55:
                    out.append(f"  [pair] ci={ci+1} (段首40字: {paras[ci][:40]})")
                    out.append(f"         j ={j+1} (段首40字: {paras[j][:40]}) sim={s:.3f}")
                    out.append(f"         ci全文: {paras[ci]}")
                    out.append(f"         j 全文: {paras[j]}")
                    break
    out.append("")

txt = "\n".join(out)
(ROOT / ".workbuddy/_diag_B.txt").write_text(txt, encoding="utf-8")
print("done", len(txt))
