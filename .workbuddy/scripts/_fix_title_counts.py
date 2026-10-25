# -*- coding: utf-8 -*-
"""标点修复第三遍：把 09-14~09-17 标题方案「标题数据跟踪表」的字数单元格
按实测值重写（项目铁律：标题字数必须实测，禁止估算）。只改纯数字单元格。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "drafts"
REPORT = ROOT / ".workbuddy" / "_字数单元格校正.txt"

PLATS = ("知乎", "微信", "公众号", "微信公众号", "头条", "百家号", "CSDN", "小红书", "视频号")
buf = []
fixed = 0

for day in ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17"]:
    dd = DRAFTS / day
    if not dd.exists():
        continue
    for tdir in sorted(d for d in dd.iterdir() if d.is_dir()):
        f = tdir / "标题方案.md"
        if not f.exists():
            continue
        lines = f.read_text(encoding="utf-8").split("\n")
        dirty = False
        for i, ln in enumerate(lines):
            if not ln.strip().startswith("|"):
                continue
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) < 3 or cells[0] not in PLATS:
                continue
            if not re.fullmatch(r"\d+", cells[2] or ""):
                continue
            title = cells[1]
            n = len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", title))
            if n != int(cells[2]):
                raw = ln.strip("|").split("|")
                idx = 2
                raw[idx] = f" {n} "
                newline = "|" + "|".join(raw) + "|"
                lines[i] = newline
                dirty = True
                fixed += 1
                buf.append(f"[{day}/{tdir.name}] {cells[0]}: {cells[2]} → {n} | {title}")
        if dirty:
            f.write_text("\n".join(lines), encoding="utf-8")

REPORT.write_text(f"共校正 {fixed} 处\n\n" + "\n".join(buf), encoding="utf-8")
print("OK fixed=", fixed)
