# -*- coding: utf-8 -*-
import io, sys, runpy, contextlib
from pathlib import Path

# 走 runpy 包装：接管 stdout 避免 PowerShell cp936 乱码
TARGET = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
OUT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/_std_chk_0926_out.txt")

buf = io.StringIO()
sys.argv = [str(TARGET), "--date", "2026-09-26"]
old = sys.stdout
sys.stdout = buf
try:
    runpy.run_path(str(TARGET), run_name="__main__")
except SystemExit:
    pass
except Exception as e:
    buf.write("\n[WRAPPER EXC] %r\n" % (e,))
finally:
    sys.stdout = old

OUT.write_text(buf.getvalue(), encoding="utf-8")
print("OK")
