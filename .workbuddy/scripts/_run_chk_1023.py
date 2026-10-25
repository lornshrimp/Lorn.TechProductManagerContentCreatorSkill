# -*- coding: utf-8 -*-
"""runpy 包装：跑 规范校验.py --date 2026-10-23，stdout 落 UTF-8 文件（规避 PowerShell cp936 乱码）"""
import io
import sys
import runpy
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
OUT = ROOT / ".workbuddy/scripts/_校验_2026-10-23.txt"

buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
try:
    sys.argv = ["规范校验.py", "--date", "2026-10-23"]
    runpy.run_path(str(ROOT / ".workbuddy/scripts/规范校验.py"), run_name="__main__")
except SystemExit:
    pass
finally:
    sys.stdout = old
    OUT.write_text(buf.getvalue(), encoding="utf-8")
print("WROTE", OUT, len(buf.getvalue()))
