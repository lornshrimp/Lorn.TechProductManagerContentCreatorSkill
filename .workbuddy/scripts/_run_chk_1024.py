# -*- coding: utf-8 -*-
"""runpy 包装：全量规范校验，stdout 落盘 UTF-8（避免 PowerShell cp936 乱码）"""
import io, sys, runpy, contextlib

P = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体"
OUT = P + r"/.workbuddy/scripts/_校验_2026-10-24.txt"

buf = io.StringIO()
sys.argv = ["规范校验.py", "--date", "2026-10-24"]
old = sys.stdout
sys.stdout = buf
try:
    runpy.run_path(P + "/.workbuddy/scripts/规范校验.py", run_name="__main__")
except SystemExit:
    pass
finally:
    sys.stdout = old

txt = buf.getvalue()
open(OUT, "w", encoding="utf-8").write(txt)
print("WROTE", OUT, len(txt))
