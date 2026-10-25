# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path
R = Path(".workbuddy/scripts/规范校验.py").resolve()
spec = importlib.util.spec_from_file_location("chk", R)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
D = Path("drafts/2026-09-26")
out = []
tot_issues = 0
for topic in sorted([p for p in D.iterdir() if p.is_dir()]):
    out.append("=" * 70)
    out.append("### %s" % topic.name)
    fin = list(topic.glob("终稿-*.md"))
    if fin:
        fc = m.count_body_chars(fin[0])
        out.append("  终稿 %-60s %d 字" % (fin[0].name, fc))
        out.append("  终稿结构门禁: %s" % (m.check_body_structure(fin[0], "终稿-") or "OK"))
        out.append("  终稿视觉要素: %s" % (m.check_visual_elements(fin[0]) if hasattr(m,"check_visual_elements") else "N/A"))
    for pf in sorted([f for f in topic.glob("*.md") if any(f.name.startswith(x) for x in m.PLATFORM_PREFIX)]):
        pfx = next((p for p in m.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "?")
        need = int(fc * m.PLATFORM_MIN_RATIO[pfx]) if fin else 0
        n = m.count_body_chars(pf)
        ys = m.check_yaml_required(pf, m.PLATFORM_YAML_KEYS)
        bs = m.check_body_structure(pf, pfx)
        an = m.check_anchor_quality(pf)
        iss = ys + bs + an
        tot_issues += len(iss)
        flag = "OK " if (n >= need and not iss) else "!! "
        out.append("  [%s] %-55s %5d/需%5d  问题%d" % (flag, pf.name[:55], n, need, len(iss)))
        for i in iss:
            out.append("        " + i.strip())
    comp = list(topic.glob("合规自检表.md"))
    out.append("  合规自检表: %s" % ("存在" if comp else "缺失"))
out.append("=" * 70)
out.append("今日平台稿问题总数: %d" % tot_issues)
Path(".workbuddy/scripts/_final_audit_0926.txt").write_text("\n".join(out), encoding="utf-8")
print("done")
