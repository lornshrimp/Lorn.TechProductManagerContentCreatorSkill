# -*- coding: utf-8 -*-
"""修复 2026-09-23 B/C 题标题方案「备选标题」字数偏短（5 项 ⚠️）。"""
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
B = ROOT / "drafts/2026-09-23/中国发现超大型铜金矿-战略矿产的定价权/标题方案.md"
C = ROOT / "drafts/2026-09-23/越南严查中国商品转运-原产地规则这本账/标题方案.md"

EDITS = [
    (B, "| 又发现超大型铜金矿，铜价会跌吗？ | #2",
        "| 又发现超大型铜金矿，铜价这回会跌吗？ | #2"),
    (B, "| 定价权不在矿点位置，在加工产能 | #1",
        "| 定价权不在矿点位置，而在加工产能手里 | #1"),
    (B, "储量是禀赋，定价权是产能 | #1 改写",
        "储量只是账面禀赋，定价权才是产能 | #1 改写"),
    (C, "原产地判定的四道门槛 | #3 |",
        "原产地规则的四道门槛与三条路 | #3 |"),
    (C, "谁写门槛，谁裁定附加值 | #1 |",
        "门槛由谁写，附加值就归谁裁定 | #1 |"),
]

log = []
for path, old, new in EDITS:
    t = path.read_text(encoding="utf-8")
    n = t.count(old)
    if n != 1:
        log.append(f"SKIP(n={n}) {path.name}: {old[:28]}")
        continue
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    log.append(f"OK  {path.name}: {new[:34]}")

(ROOT / ".workbuddy" / "_fix_titles_0923.txt").write_text("\n".join(log), encoding="utf-8")
print("DONE")
