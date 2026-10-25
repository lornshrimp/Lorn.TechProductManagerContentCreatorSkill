import importlib.util, sys, io
from pathlib import Path

root = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("guifan", root / ".workbuddy" / "scripts" / "规范校验.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

out = []
targets = sys.argv[1:]
for t in targets:
    p = Path(t)
    if p.exists():
        out.append(f"{p.parent.name}/{p.name}\t{mod.count_body_chars(p)}")
    else:
        out.append(f"MISSING\t{t}")
Path(root / ".workbuddy" / "scripts" / "_count_out.txt").write_text("\n".join(out), encoding="utf-8")
print("OK")
