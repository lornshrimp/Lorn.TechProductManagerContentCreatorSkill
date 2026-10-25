import sys, re
from pathlib import Path
sys.path.insert(0, r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts")
import importlib.util
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
d = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-16/约谈在线酒店预订平台-竞争秩序账本")
rows=[]
for f in sorted(d.glob("*.md")):
    try:
        n = m.count_body_chars(f)
        rows.append(f"{f.name}: {n}")
        if hasattr(m,'extract_body_text'):
            pass
        if f.name.startswith(("知乎","微信","百家号","CSDN","头条")):
            import difflib
            try:
                ft = d/"终稿-约谈在线酒店预订平台.md"
                a = m.extract_body_text(f); b = m.extract_body_text(ft)
                r = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
                rows.append(f"   ratio={r*100:.1f}%")
            except Exception as e:
                rows.append(f"   ratio-err {e}")
    except Exception as e:
        rows.append(f"{f.name}: ERR {e}")
Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/_m_a.txt").write_text("\n".join(rows), encoding="utf-8")
print("done")
