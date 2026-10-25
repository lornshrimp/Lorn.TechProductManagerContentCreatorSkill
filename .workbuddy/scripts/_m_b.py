import importlib.util, difflib, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-16/科技贷款认定口径收紧-指标挤水分")
out=[]
for f in sorted(d.glob("*.md")):
    try:
        out.append(f"{f.name}: {m.count_body_chars(f)}")
    except Exception as e:
        out.append(f"{f.name}: ERR {e}")
Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/_m_b.txt").write_text("\n".join(out), encoding="utf-8")
print("ok")
