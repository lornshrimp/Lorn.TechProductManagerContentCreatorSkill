# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path
R = Path(".workbuddy/scripts/规范校验.py").resolve()
spec = importlib.util.spec_from_file_location("chk", R)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
D = Path("drafts/2026-09-26")
out = []
for topic in sorted([p for p in D.iterdir() if p.is_dir()]):
    fin = list(topic.glob("终稿-*.md"))[0]
    ft = m.extract_body_text(fin)
    out.append("=== %s" % topic.name)
    pf = sorted([f for f in topic.glob("*.md") if any(f.name.startswith(x) for x in m.PLATFORM_PREFIX)])
    txts = {}
    for f in pf:
        t = m.extract_body_text(f)
        txts[f.name] = t
        out.append("  与母稿 %.4f  %s" % (m.text_similarity(t, ft), f.name))
    names = sorted(txts)
    mx = 0.0; mxp = ""
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            s = m.text_similarity(txts[names[i]], txts[names[j]])
            if s > mx:
                mx = s; mxp = names[i] + " vs " + names[j]
    out.append("  平台两两最高 %.4f  %s" % (mx, mxp))
Path(".workbuddy/scripts/_sim_0926.txt").write_text("\n".join(out), encoding="utf-8")
print("ok")
