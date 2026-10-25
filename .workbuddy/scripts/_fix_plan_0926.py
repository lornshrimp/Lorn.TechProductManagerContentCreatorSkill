# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path
R = Path(".workbuddy/scripts/规范校验.py").resolve()
spec = importlib.util.spec_from_file_location("chk", R)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
D = Path("drafts/2026-09-26")
out = []
for topic in sorted([p for p in D.iterdir() if p.is_dir()]):
    fin = list(topic.glob("终稿-*.md"))
    fc = m.count_body_chars(fin[0]) if fin else 0
    out.append("=== %s  （终稿 %d）" % (topic.name, fc))
    for pf in sorted([f for f in topic.glob("*.md") if any(f.name.startswith(p) for p in m.PLATFORM_PREFIX)]):
        pfx = next((p for p in m.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "?")
        need = int(fc * m.PLATFORM_MIN_RATIO[pfx])
        cur = m.count_body_chars(pf)
        gap = need + 30 - cur
        mark = "OK " if cur >= need else "FIX"
        out.append("  [%s] %-58s %5d / 需 %5d  缺口 %+5d" % (mark, pf.name, cur, need, gap))
Path(".workbuddy/scripts/_fix_plan_0926.txt").write_text("\n".join(out), encoding="utf-8")
print("done")
