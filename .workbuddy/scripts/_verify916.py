# -*- coding: utf-8 -*-
"""一次性验校脚本：跑 规范校验.py，把 ASCII 摘要落盘，避开控制台编码/回显问题。"""
import pathlib, subprocess, sys

BASE = pathlib.Path(__file__).resolve().parent.parent.parent
CHECKER = BASE / ".workbuddy" / "scripts" / "规范校验.py"
DATE = "2026-09-16"

r = subprocess.run([sys.executable, str(CHECKER), "--date", DATE],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
text = (r.stdout or "") + "\n" + (r.stderr or "")

lines = text.splitlines()
marker = "drafts\\" + DATE + "\\"
today_lines = [i for i, ln in enumerate(lines) if marker in ln]

# 找今日目录块（若存在）里的 ❌ / ⚠️
problems = [ln for ln in lines if ("❌" in ln or "⚠️" in ln) and marker in ln]
err_cnt = sum(1 for ln in lines if "❌" in ln and marker in ln)
warn_cnt = sum(1 for ln in lines if "⚠️" in ln and marker in ln)
summary = [ln for ln in lines if ln.startswith("共发现")]

out = BASE / ".workbuddy" / "_verify916.txt"
report = []
report.append("date=%s" % DATE)
report.append("checker_rc=%s" % r.returncode)
report.append("out_bytes=%d" % len(text))
report.append("today_marker_lines=%s" % (today_lines if today_lines else "NONE"))
report.append("today_err_count=%d" % err_cnt)
report.append("today_warn_count=%d" % warn_cnt)
report.append("total_summary=%s" % (summary[-1] if summary else "n/a"))
report.append("today_problem_lines:")
report.extend(problems if problems else ["  (none)"])
out.write_text("\n".join(report), encoding="utf-8")
