# -*- coding: utf-8 -*-
"""runpy 包装：全量规范校验，stdout 落盘 UTF-8（避免 PowerShell 重定向按 cp936 解码乱码）"""
import io, runpy, sys
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
OUT = ROOT / ".workbuddy" / "scripts" / "_校验_2026-10-22.txt"

buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
code = 0
try:
    sys.argv = ["规范校验.py", "--date", "2026-10-22"]
    runpy.run_path(str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"), run_name="__main__")
except SystemExit as e:
    code = e.code or 0
finally:
    sys.stdout = old

text = buf.getvalue()
OUT.write_text(text, encoding="utf-8")
print(f"exit={code} bytes={len(text)} -> {OUT}")
print("今日段是否存在:", "drafts\\2026-10-22\\" in text or "drafts/2026-10-22/" in text)
