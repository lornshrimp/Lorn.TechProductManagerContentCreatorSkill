# -*- coding: utf-8 -*-
"""复刻 规范校验.py 的平台稿门禁逻辑，针对单日目录输出真人可读诊断。"""
import importlib.util, sys
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
SPEC = ROOT / ".workbuddy" / "scripts" / "规范校验.py"
spec = importlib.util.spec_from_file_location("guifan", str(SPEC))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

DATE = sys.argv[1] if len(sys.argv) > 1 else "2026-09-23"
BASE = ROOT / "drafts" / DATE
out = []
if not BASE.exists():
    out.append("NO DIR")
for d in sorted([p for p in BASE.iterdir() if p.is_dir()]):
    out.append("=" * 72)
    out.append("TOPIC: " + d.name)
    files = [p for p in d.iterdir() if p.is_file()]
    plat = [f for f in files if any(f.name.startswith(p) for p in g.PLATFORM_PREFIX)]
    finals = list(d.glob("终稿-*.md"))
    final = finals[0] if finals else None
    fc = g.count_body_chars(final) if final else 0
    out.append("  final_chars = " + str(fc))
    for pf in sorted(plat):
        pn = g.count_body_chars(pf)
        pfx = next((p for p in g.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
        ratio_min = g.PLATFORM_MIN_RATIO.get(pfx, 0)
        need = int(fc * ratio_min)
        ok = "OK " if pn >= need else "FAIL"
        out.append("  [{}] {:34s} chars={:5d} need>={:5d} ({:.0f}%min)".format(
            ok, pf.name, pn, need, ratio_min * 100))
        if final:
            sim = g.text_similarity(g.extract_body_text(pf), g.extract_body_text(final))
            flag = "SIM>=0.99!!!" if sim >= g.COMPLIANCE_SIMILAR_TO_FINAL else ""
            out.append("        sim_vs_final = {:.4f} {}".format(sim, flag))
        for it in g.check_anchor_quality(pf):
            out.append("        ANCHOR: " + it.strip())
        for pfx2, rules in g.PLATFORM_PREFIX.items():
            if pf.name.startswith(pfx2):
                if pfx2 != "知乎-":
                    for kws, rdesc in rules:
                        for it in g.check_content(pf, kws, rdesc):
                            out.append("        KW: " + it.strip())
                break
        for vk, (vkw, vdesc) in g.PLATFORM_VISUAL_CHECKS.items():
            if not pf.name.startswith("头条-"):
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    out.append("        VISUAL MISS: " + vdesc)
        for it in g.check_body_structure(pf, next((p for p in g.BODY_STRUCTURE_H2_MIN if pf.name.startswith(p)), "平台")):
            out.append("        STRUCT: " + it.strip())
        if final:
            for it in g.check_platform_coherence(pf, final):
                out.append("        COHER: " + it.strip())
    for i in range(len(plat)):
        for j in range(i + 1, len(plat)):
            s = g.text_similarity(g.extract_body_text(plat[i]), g.extract_body_text(plat[j]))
            if s >= 0.60:
                flag = "  <<< FAIL" if s >= g.COMPLIANCE_SIMILAR_PLATFORMS else ""
                out.append("  PAIR {:.4f} {} / {}{}".format(s, plat[i].name, plat[j].name, flag))
    for it in g.check_platform_title_diversity(plat, final):
        out.append("  TITLEDIV: " + it.strip())
    for it in g.check_figure_count_uniformity(plat):
        out.append("  FIGUNIF: " + it.strip())
    # 报告类文件
    for kw, chk in [("去AI化报告", g.check_qaihua_report)]:
        for f in files:
            if f.name.startswith(kw):
                for it in chk(f):
                    out.append("  {}: {}".format(kw, it.strip()))
    if not any(f.name.startswith("去AI化报告") for f in files):
        out.append("  MISSING 去AI化报告")
    if not any(f.name.startswith("编辑终审签报") for f in files):
        out.append("  MISSING 编辑终审签报")
    if not any("合规自检表" in f.name for f in files):
        out.append("  MISSING 合规自检表")

(ROOT / ".workbuddy" / ("_gate_" + DATE.replace("-", "") + ".txt")).write_text("\n".join(out), encoding="utf-8")
print("DONE")
