# -*- coding: utf-8 -*-
"""临时包装：运行 规范校验.py 并把 UTF-8 输出直接落盘，规避 PowerShell 管道编码损坏。"""
import subprocess, sys, pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent.parent
script = BASE / ".workbuddy" / "scripts" / "规范校验.py"
out = BASE / ".workbuddy" / "_校验_2026-09-13.txt"

r = subprocess.run([sys.executable, str(script), "--date", "2026-09-13"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
out.write_text((r.stdout or "") + (r.stderr or ""), encoding="utf-8")
print("OK bytes=", out.stat().st_size)
