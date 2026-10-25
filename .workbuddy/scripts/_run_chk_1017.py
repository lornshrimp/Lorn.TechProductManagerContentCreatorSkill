# -*- coding: utf-8 -*-
"""runpy 包装：接管 stdout（io.StringIO）+ UTF-8 落盘，兜住 SystemExit。"""
import io, runpy, sys, contextlib
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
OUT = ROOT / ".workbuddy" / "scripts" / "_校验_2026-10-17.txt"

buf = io.StringIO()
sys.argv = ["规范校验.py", "--date", "2026-10-17"]
try:
    with contextlib.redirect_stdout(buf):
        runpy.run_path(str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"), run_name="__main__")
except SystemExit:
    pass
except Exception as e:  # noqa
    buf.write("\n[EXC] %s: %s\n" % (type(e).__name__, e))
OUT.write_text(buf.getvalue(), encoding="utf-8")
print("WROTE", OUT, len(buf.getvalue()))
