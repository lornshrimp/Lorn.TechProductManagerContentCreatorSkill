"""由润色稿生成终稿：替换 frontmatter 头部（B/C 通用）"""
import sys
from pathlib import Path

BASE = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
D20 = BASE / "drafts" / "2026-09-20"

JOBS = [
    ("多家银行逆势上调存款利率-负债端的定价权账",
     "负债端的定价权账",
     "多家银行逆势上调存款利率 · 负债端的定价权账"),
    ("央视曝光回流药黑产业链-票据与追溯码的双轨缝隙",
     "票据与追溯码的双轨缝隙",
     "央视曝光回流药黑产业链 · 票据与追溯码的双轨缝隙"),
]

for dname, stem, topic in JOBS:
    d = D20 / dname
    src = d / f"润色稿-{stem}.md"
    dst = d / f"终稿-{stem}.md"
    if not src.exists():
        print("SKIP (no polish):", src)
        continue
    txt = src.read_text(encoding="utf-8")
    if txt.startswith("---"):
        end = txt.index("\n---", 3) + 4
        body = txt[end:]
    else:
        body = txt
    fm = (
        "---\n"
        "type: 终稿\n"
        "date: 2026-09-20\n"
        f"topic: {topic}\n"
        "genre: 深度分析体\n"
        "model: deai-review\n"
        "审核结论: 通过\n"
        "---\n"
    )
    dst.write_text(fm + body, encoding="utf-8")
    print("OK", dst)
