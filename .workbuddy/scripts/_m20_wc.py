"""字数与差异率实测（校验脚本口径）"""
import sys, io, importlib.util
from pathlib import Path
import difflib

BASE = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("v", BASE / ".workbuddy" / "scripts" / "规范校验.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

out = []
def w(s):
    out.append(str(s))

targets = []
if len(sys.argv) > 1:
    for a in sys.argv[1:]:
        targets.append(Path(a))
else:
    d = BASE / "drafts" / "2026-09-20"
    for sub in sorted(d.iterdir()):
        for f in sorted(sub.glob("*.md")):
            targets.append(f)

for p in targets:
    try:
        n = m.count_body_chars(p)
    except Exception as e:
        n = f"ERR {e}"
    w(f"{p.parent.name}/{p.name} = {n}")

# 若给了草稿+润色稿对比
if len(sys.argv) == 3:
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        ta = m.extract_body_text(a)
        tb = m.extract_body_text(b)
        sa = "".join(ta.split())
        sb = "".join(tb.split())
        r = difflib.SequenceMatcher(None, sa, sb, autojunk=False).ratio()
        w(f"DIFF ratio(相同度)={r:.4f}  差异率={1-r:.4%}")
    except Exception as e:
        w(f"DIFF ERR {e}")

(BASE / ".workbuddy" / "scripts" / "_wc_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
