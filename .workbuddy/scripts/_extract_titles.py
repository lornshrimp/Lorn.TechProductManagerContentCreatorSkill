# -*- coding: utf-8 -*-
"""提取 09-14~09-17 三题《标题方案.md》平台适配表 + 标题数据跟踪表原始行，
供制定标点修复映射。输出 UTF-8 落盘。"""
import re
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "drafts"
OUT = ROOT / ".workbuddy" / "_标题原始行.txt"

days = ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17"]
buf = []

for d in days:
    day_dir = DRAFTS / d
    if not day_dir.exists():
        continue
    for topic_dir in sorted(day_dir.iterdir()):
        if not topic_dir.is_dir():
            continue
        f = topic_dir / "标题方案.md"
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        buf.append(f"\n{'='*8} {d} / {topic_dir.name} {'='*8}")
        # 抓平台适配段与跟踪表段内的表格行
        for sec, label in ((r"^#{2,4}\s*.*平台适配.*$", "平台适配"),):
            m = re.search(sec, text, re.MULTILINE)
            if not m:
                continue
            start = m.end()
            nxt = re.search(r"^##(?!#)\s+", text[start:], re.MULTILINE)
            seg = text[start: start + nxt.start()] if nxt else text[start:]
            buf.append(f"-- [{label}] --")
            for ln in seg.split("\n"):
                if ln.strip().startswith("|"):
                    buf.append(ln.rstrip())
        m2 = re.search(r"^#{2,4}\s*.*标题数据跟踪表.*$", text, re.MULTILINE)
        if m2:
            start = m2.end()
            nxt = re.search(r"^##(?!#)\s+", text[start:], re.MULTILINE)
            seg = text[start: start + nxt.start()] if nxt else text[start:]
            buf.append("-- [标题数据跟踪表] --")
            for ln in seg.split("\n"):
                if ln.strip().startswith("|"):
                    buf.append(ln.rstrip())

OUT.write_text("\n".join(buf), encoding="utf-8")
print("OK", len(buf))
