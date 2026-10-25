# -*- coding: utf-8 -*-
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("chk", ".workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec); sys.modules["chk"]=m; spec.loader.exec_module(m)
root = Path("drafts/2026-09-27")
out=[]
for d in sorted(root.iterdir()):
    if not d.is_dir(): continue
    tp = d/"标题方案.md"
    if not tp.exists(): continue
    out.append(f"===== {d.name}")
    for fn in (m.check_platform_title_length, m.check_platform_title_trace, m.check_platform_title_punctuation):
        r = fn(tp)
        out.append(f"  -- {fn.__name__}: {len(r)} 项")
        for x in r: out.append("    "+x.strip())
Path(".workbuddy/scripts/_tchk_0927_out.txt").write_text("\n".join(out), encoding="utf-8")
print("done")
