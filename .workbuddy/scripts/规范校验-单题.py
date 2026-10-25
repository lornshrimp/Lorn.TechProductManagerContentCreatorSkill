# -*- coding: utf-8 -*-
"""规范校验-单题：只回传某一选题相关的校验块，便于并行生产中各自闭环。

用法：
    python 规范校验-单题.py --date 2026-09-15 --topic "灵活就业超2亿人"
输出：{项目根}/.workbuddy/_校验_{date}_{topic前12字}.txt
stdout 仅回传 ASCII 摘要（避开 PowerShell 编码问题）。
"""
import argparse
import pathlib
import re
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent.parent
CHECKER = BASE / ".workbuddy" / "scripts" / "规范校验.py"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--topic", required=True)
    args = ap.parse_args()

    r = subprocess.run(
        [sys.executable, str(CHECKER), "--date", args.date],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    text = r.stdout or ""
    # 报告块以行首 [ 开头；按选题名筛选相关块
    blocks = re.split(r"\n(?=\[)", text)
    keep = [b for b in blocks if args.topic in b]
    body = "\n".join(keep) if keep else "NO_BLOCK_FOUND_FOR_TOPIC"
    safe = re.sub(r"[^\w\u4e00-\u9fff]+", "", args.topic)[:12]
    out = BASE / ".workbuddy" / f"_校验_{args.date}_{safe}.txt"
    out.write_text(body, encoding="utf-8")
    n_err = body.count("\u274c")
    n_warn = body.count("\u26a0")
    print("OUT=", out.name, "| blocks=", len(keep), "| err=", n_err, "| warn=", n_warn)


if __name__ == "__main__":
    main()
