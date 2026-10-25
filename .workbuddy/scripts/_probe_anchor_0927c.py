# -*- coding: utf-8 -*-
"""探针3：验证最终候选锚文本（正文唯一 + 段首）。"""
import re
from pathlib import Path

D = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-09-27")
cand = {
    "A": ("中美300亿美元对等降税落地-排除清单才是核心清单/润色稿-降了-300-亿美元关税，芯片一件没提，这比降税本身更值得看.md",
          ["一头在降，一头纹丝不动", "被塞进清单的品类", "被排除的是这几样"]),
    "B": ("油价调控半年四次压缩涨幅-成品油定价这本账/润色稿-油价调控半年四次，少涨的-435-元到底谁承担.md",
          ["9 月 24 日 24 时这一轮调价", "它不会凭空消失", "先看应涨多少。"]),
    "C": ("盖茨警告AI或致十亿人死亡-风险定义权与立法门槛/润色稿-盖茨说-AI-或致十亿人死亡，但重点不在这个数字.md",
          ["规则真要立", "加州走的是最实的一步。", "定义权只是上半场。"]),
}
for tag, (rel, anchors) in cand.items():
    raw = (D / rel).read_text(encoding="utf-8")
    print(f"\n=== {tag} ===")
    for a in anchors:
        cnt = raw.count(a)
        i = raw.find(a)
        seg = raw[:i] if i != -1 else ""
        ss = seg.rfind("\n\n")
        tail = seg[ss + 2:] if ss != -1 else seg
        start_ok = tail.strip() == ""
        print(f"  [{cnt}] {a!r}  段首={'✅' if (cnt == 1 and start_ok) else '❌'}  前文={tail[:24]!r}")
