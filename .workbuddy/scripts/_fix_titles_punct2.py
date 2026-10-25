# -*- coding: utf-8 -*-
"""标点修复第二遍：对齐 09-16 跟踪表标题 + 校正字数单元格 + 全量复核字数单元格。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "drafts"
REPORT = ROOT / ".workbuddy" / "_标题标点修复复核.txt"

# (day, topic_substr, old, new) —— 针对已修复后的文本
SECOND = [
    ("2026-09-16", "国民经济",
     "工业 5.2%、社零 0.4%，中间那道口子是什么？",
     "工业 5.2%、社零 0.4%，中间那道口子到底是什么？"),
    # CSDN 8 月经济标题现为 17 字，跟踪表字数单元格写 18
    ("2026-09-16", "国民经济",
     "| CSDN | 拆解 8 月经济数据：三个检验与口径对照 | 18 | 1-60 |",
     "| CSDN | 拆解 8 月经济数据：三个检验与口径对照 | 17 | 1-60 |"),
]

buf = []
for day, sub, old, new in SECOND:
    dd = DRAFTS / day
    for tdir in [d for d in dd.iterdir() if d.is_dir() and sub in d.name]:
        f = tdir / "标题方案.md"
        t = f.read_text(encoding="utf-8")
        if old in t:
            f.write_text(t.replace(old, new), encoding="utf-8")
            buf.append(f"[OK] {day}/{tdir.name}: {new[:40]}")
        else:
            buf.append(f"[MISS] {day}/{tdir.name}: {old[:40]}")

# 复核：各标题方案「标题数据跟踪表」与「字数核对」列的字数是否与标题实测一致
buf.append("\n===== 字数单元格复核 =====")
for day in ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17"]:
    dd = DRAFTS / day
    if not dd.exists():
        continue
    for tdir in sorted(d for d in dd.iterdir() if d.is_dir()):
        f = tdir / "标题方案.md"
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        for ln in text.split("\n"):
            if not ln.strip().startswith("|"):
                continue
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if len(cells) >= 3 and re.fullmatch(r"\d+", cells[2] or "") and cells[0] in (
                    "知乎", "微信", "公众号", "微信公众号", "头条", "百家号", "CSDN", "小红书", "视频号"):
                ttl = cells[1]
                n = len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", ttl))
                if n != int(cells[2]):
                    buf.append(f"[字数不符] {day}/{tdir.name} {cells[0]}: 表内 {cells[2]} / 实测 {n} | {ttl}")

REPORT.write_text("\n".join(buf), encoding="utf-8")
print("OK lines=", len(buf))
