# -*- coding: utf-8 -*-
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("chk", ".workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec)
sys.modules["chk"] = m
spec.loader.exec_module(m)
root = Path("drafts/2026-09-27")
out = []
for d in sorted(root.iterdir()):
    if not d.is_dir(): continue
    fs = sorted(d.glob("终稿-*.md"))
    if not fs: continue
    n = m.count_body_chars(fs[0])
    out.append(f"{d.name}\n  {fs[0].name}\n  count_body_chars = {n}\n")
Path(".workbuddy/scripts/_wc3_0927_out.txt").write_text("\n".join(out), encoding="utf-8")
print("done")
