"""由润色稿生成终稿：替换 frontmatter 头部"""
import sys
from pathlib import Path

pairs = [
    (r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-09-20\入职12年拒签自愿离职被调待岗-合法外壳里的解雇成本\润色稿-合法外壳里的解雇成本.md",
     r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-09-20\入职12年拒签自愿离职被调待岗-合法外壳里的解雇成本\终稿-合法外壳里的解雇成本.md",
     "合法外壳里的解雇成本"),
]

for src, dst, name in pairs:
    p = Path(src)
    txt = p.read_text(encoding="utf-8")
    # 截掉旧 frontmatter
    if txt.startswith("---"):
        end = txt.index("\n---", 3) + 4
        body = txt[end:]
    else:
        body = txt
    fm = (
        "---\n"
        "type: 终稿\n"
        "date: 2026-09-20\n"
        "topic: 入职12年拒签自愿离职被调待岗 · 合法外壳里的解雇成本\n"
        "genre: 深度分析体\n"
        "model: deai-review\n"
        "审核结论: 通过\n"
        "---\n"
    )
    Path(dst).write_text(fm + body, encoding="utf-8")
    print("OK", dst)
