import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-16/8月国民经济数据剪刀差-生产热与消费冷的对账")
out=[]
for f in sorted(d.glob("*.md")):
    try: out.append(f"{f.name}: {m.count_body_chars(f)}")
    except Exception as e: out.append(f"{f.name}: ERR {e}")
Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/_m_c.txt").write_text("\n".join(out), encoding="utf-8")
print("ok")
