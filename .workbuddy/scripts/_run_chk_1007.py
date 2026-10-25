# -*- coding: utf-8 -*-
"""runpy 包装规范校验，落盘 UTF-8（规避 PowerShell 重定向 cp936 乱码）"""
import io, os, runpy, sys, traceback
from pathlib import Path

BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
OUT = BASE / ".workbuddy" / "_chk_out1007.txt"
sys.argv = ["规范校验.py", "--date", "2026-10-07", "--root", str(BASE)]
buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
try:
    runpy.run_path(str(BASE / ".workbuddy" / "scripts" / "规范校验.py"), run_name="__main__")
except SystemExit as e:
    buf.write(f"\n[exit {e.code}]\n")
except Exception:
    buf.write("\n[EXC]\n" + traceback.format_exc())
finally:
    sys.stdout = old
OUT.write_text(buf.getvalue(), encoding="utf-8")
print("WROTE", OUT, "len", len(buf.getvalue()))
