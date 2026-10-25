# -*- coding: utf-8 -*-
"""规范校验-落盘：运行 规范校验.py 并把 UTF-8 输出直接写文件。

背景：PowerShell 5.1 管道捕获 python 的 UTF-8 输出时按系统 ANSI(GBK) 解码，
      中文全部变乱码（Set-Content -Encoding UTF8 也救不回）。本脚本让 python
      自己写文件，绕开 PowerShell 中间层。
用法：
    python 规范校验-落盘.py                 # 默认日期 2026-09-13
    python 规范校验-落盘.py --date 2026-09-14
输出：{项目根}/.workbuddy/_校验_{date}.txt
"""
import argparse
import pathlib
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent.parent
CHECKER = BASE / ".workbuddy" / "scripts" / "规范校验.py"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-09-13")
    args = ap.parse_args()

    out = BASE / ".workbuddy" / f"_校验_{args.date}.txt"
    r = subprocess.run(
        [sys.executable, str(CHECKER), "--date", args.date],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    out.write_text((r.stdout or "") + (r.stderr or ""), encoding="utf-8")
    # 只回传 ASCII 摘要，避免再次触发 PowerShell 编码问题
    text = r.stdout or ""
    today_marker = f"drafts\\{args.date}\\"
    has_today_block = today_marker in text
    tail = [ln for ln in text.splitlines() if ln.startswith("共发现")]
    print("OUT=", out.name, "| bytes=", out.stat().st_size,
          "| today_block=", has_today_block,
          "| summary=", (tail[-1] if tail else "n/a").encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
