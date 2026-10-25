# -*- coding: utf-8 -*-
"""runpy 包装：全量规范校验，UTF-8 落盘（规避 PowerShell cp936 乱码）"""
import runpy, io, sys
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
try:
    sys.argv = ["规范校验.py", "--date", "2026-10-25"]
    runpy.run_path(str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"), run_name="__main__")
except SystemExit:
    pass
finally:
    sys.stdout = old

out = buf.getvalue()
p = ROOT / ".workbuddy" / "scripts" / "_校验_2026-10-25.txt"
p.write_text(out, encoding="utf-8")
print("WROTE", p, "chars", len(out))
