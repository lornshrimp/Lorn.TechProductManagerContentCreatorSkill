# -*- coding: utf-8 -*-
"""字数与结构实测工具（复用 规范校验.py 的口径）"""
import sys, io, re, difflib
from pathlib import Path

sys.path.insert(0, str(Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts")))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT / "drafts" / "2026-09-16"

out = []
def P(*a):
    out.append(" ".join(str(x) for x in a))

for topic_dir in sorted([p for p in D.iterdir() if p.is_dir()]):
    P("=" * 70)
    P("TOPIC:", topic_dir.name)
    outline = topic_dir / "大纲.md"
    genre = "深度分析体"
    if outline.exists():
        ofm, _ = chk.parse_yaml_frontmatter(outline.read_text(encoding="utf-8", errors="ignore"))
        genre = (ofm.get("genre") or "深度分析体").strip() or "深度分析体"
    minw = chk.GENRE_MIN_WORDS.get(genre, 2500)
    P(f"genre={genre} min={minw}")
    final_refs = list(topic_dir.glob("终稿-*.md"))
    final_chars = chk.count_body_chars(final_refs[0]) if final_refs else 0
    for f in sorted(topic_dir.glob("*.md")):
        n = chk.count_body_chars(f)
        extra = ""
        m = re.match(r"^(终稿|草稿|润色稿|知乎|微信|百家号|CSDN|头条|去AI化报告)", f.name)
        if m:
            lbl = m.group(1)
            if lbl in ("终稿", "草稿", "润色稿"):
                extra = f" [{'OK' if n >= minw else 'FAIL<'+str(minw)}]"
            elif lbl == "去AI化报告":
                extra = ""
            else:
                pfx = lbl + "-"
                ratio_min = chk.PLATFORM_MIN_RATIO.get(pfx)
                if ratio_min and final_chars:
                    r = n / final_chars
                    extra = f" [ratio={r*100:.1f}% need>={ratio_min*100:.0f}%{' OK' if r>=ratio_min else ' FAIL'}]"
            if lbl in ("终稿", "知乎", "微信", "百家号", "CSDN", "头条"):
                iss = chk.check_body_structure(f, {"终稿":"终稿-","知乎":"知乎-","微信":"微信-","百家号":"百家号-","CSDN":"CSDN-","头条":"头条-"}[lbl])
                if iss:
                    extra += " STRUCT:" + " | ".join(i.strip() for i in iss)
        P(f"  {f.name}: {n}{extra}")
    # platform pairwise + vs final
    plats = [f for f in sorted(topic_dir.glob("*.md")) if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)]
    for i in range(len(plats)):
        for j in range(i+1, len(plats)):
            s = chk.text_similarity(chk.extract_body_text(plats[i]), chk.extract_body_text(plats[j]))
            flag = " !!!>=0.85" if s >= 0.85 else ""
            P(f"  SIM {plats[i].name} vs {plats[j].name}: {s*100:.1f}%{flag}")
    if final_refs:
        for pf in plats:
            s = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(final_refs[0]))
            flag = " !!!>=0.99" if s >= 0.99 else ""
            P(f"  SIMfinal {pf.name}: {s*100:.1f}%{flag}")
            coh = chk.check_platform_coherence(pf, final_refs[0])
            if coh:
                P("   COH:" + " | ".join(c.strip() for c in coh))
    # title diversity
    if plats:
        td = chk.check_platform_title_diversity(plats, final_refs[0] if final_refs else None)
        if td:
            P("   TITLE:" + " | ".join(t.strip() for t in td))
    anq = []
    for pf in plats:
        anq += chk.check_anchor_quality(pf)
    if anq:
        P("   ANCHOR:" + " | ".join(a.strip() for a in anq))
    fc = chk.check_figure_count_uniformity(plats)
    if fc:
        P("   FIG:" + " | ".join(a.strip() for a in fc))
    # title plan checks
    tf = topic_dir / "标题方案.md"
    if tf.exists():
        P(f"  candidates={len(chk.extract_title_candidates(tf))}")
        for i in chk.check_platform_title_trace(tf):
            P("   TRACE:" + i.strip())
        for i in chk.check_platform_title_length(tf):
            P("   LEN:" + i.strip())
    for qf in sorted(topic_dir.glob("去AI化报告-*.md")):
        for i in chk.check_qaihua_report(qf):
            P("   QAIHUA:" + i.strip())

Path(ROOT / ".workbuddy" / "scripts" / "_check_out.txt").write_text("\n".join(out), encoding="utf-8")
print("WROTE", len(out), "lines")
