# -*- coding: utf-8 -*-
"""Move '## 读者互动' block into the article body and drop the heading.
Strategy: MOVE the two interaction paragraphs verbatim (no retyping) so the
text is byte-identical; only their position changes and the heading is removed.
"""
import sys, io, pathlib

BASE = pathlib.Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-16")

JOBS = [
    {
        "path": BASE / "约谈在线酒店预订平台-竞争秩序账本" / "微信-约谈在线酒店预订平台.md",
        "check_last": "规则好不好",
        "i_last": 89,     # line 90
        "i_vis": 91,      # line 92  ## 视觉与配图
        "i_head": 112,    # line 113 ## 读者互动
        "i_p1": 114,      # line 115
        "i_p2": 116,      # line 117
        "i_next": 118,    # line 119 ## 配图搜索替换指令
    },
    {
        "path": BASE / "科技贷款认定口径收紧-指标挤水分" / "微信-科技贷款的指标挤水分.md",
        "check_last": "尺子换了",
        "i_last": 91,     # line 92
        "i_vis": 93,      # line 94  ## 视觉与配图
        "i_head": 114,    # line 115 ## 读者互动
        "i_p1": 116,      # line 117
        "i_p2": 118,      # line 119
        "i_next": 120,    # line 121 ## 配图搜索替换指令
    },
]

for job in JOBS:
    p = job["path"]
    text = p.read_text(encoding="utf-8")
    lines = text.split("\n")

    ok = True
    if not lines[job["i_last"]].startswith(job["check_last"]):
        print("FAIL A", job["path"].name, lines[job["i_last"]][:20]); ok = False
    if lines[job["i_vis"]].strip() != "## 视觉与配图":
        print("FAIL B", job["path"].name, lines[job["i_vis"]][:20]); ok = False
    if lines[job["i_head"]].strip() != "## 读者互动":
        print("FAIL C", job["path"].name, lines[job["i_head"]][:20]); ok = False
    if lines[job["i_next"]].strip() != "## 配图搜索替换指令":
        print("FAIL D", job["path"].name, lines[job["i_next"]][:20]); ok = False
    if not ok:
        print("ABORT", job["path"].name)
        continue

    p1 = lines[job["i_p1"]]
    p2 = lines[job["i_p2"]]
    assert p1.strip() and p2.strip(), "empty interaction paragraph"

    # insert after the last body line, before the '## 视觉与配图' section
    head = lines[: job["i_last"] + 1] + ["", p1, "", p2]
    # keep visual section, drop heading + blank + p1 + blank + p2 + blank
    mid = lines[job["i_vis"] : job["i_head"]]
    tail = lines[job["i_next"] :]
    new = head + mid + tail

    p.write_text("\n".join(new), encoding="utf-8")
    print("OK", job["path"].name, "moved", len(p1) + len(p2), "chars")

print("DONE")
