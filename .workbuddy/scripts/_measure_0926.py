# -*- coding: utf-8 -*-
import importlib.util, io
from pathlib import Path
R = Path(".workbuddy/scripts/规范校验.py").resolve()
spec = importlib.util.spec_from_file_location("chk", R)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

D = Path("drafts/2026-09-26")
out = []
for topic in sorted([p for p in D.iterdir() if p.is_dir()]):
    out.append("=== %s ===" % topic.name)
    for f in sorted(topic.glob("*.md")):
        try:
            n = m.count_body_chars(f)
        except Exception as e:
            n = "ERR %r" % (e,)
        out.append("  %-70s %s" % (f.name, n))
Path(".workbuddy/scripts/_measure_0926_out.txt").write_text("\n".join(out), encoding="utf-8")
print("done")
