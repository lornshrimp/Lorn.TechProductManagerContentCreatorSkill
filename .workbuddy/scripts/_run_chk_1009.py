# -*- coding: utf-8 -*-
"""runpy 包装：运行 规范校验.py --date 2026-10-09，stdout 落盘 utf-8"""
import io, sys, runpy
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
OUT = ROOT / ".workbuddy" / "scripts" / "_校验_2026-10-09.txt"

buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
try:
    sys.argv = ["规范校验.py", "--date", "2026-10-09"]
    runpy.run_path(str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"), run_name="__main__")
except SystemExit as e:
    buf.write(f"\n[exit] {e.code}\n")
finally:
    sys.stdout = old

OUT.write_text(buf.getvalue(), encoding="utf-8")
print("WROTE", OUT)
