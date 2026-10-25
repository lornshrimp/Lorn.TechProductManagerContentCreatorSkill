# -*- coding: utf-8 -*-
"""临时：核验 A 题终稿与润色稿是否逐字相同（含取舍段）。"""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
d = BASE / "drafts" / "2026-09-15" / "灵活就业超2亿人与社保基数上移-劳动保障覆盖率的账本"
pol = (d / "润色稿-劳动保障覆盖率的账本.md").read_text(encoding="utf-8")
fin = (d / "终稿-劳动保障覆盖率的账本.md").read_text(encoding="utf-8")
same = pol == fin
out = [f"exact_equal = {same}", f"polish_len = {len(pol)}", f"final_len = {len(fin)}"]
if not same:
    import difflib
    diff = list(difflib.unified_diff(pol.splitlines(), fin.splitlines(), lineterm="", n=1))
    out.append(f"diff_lines = {len(diff)}")
    out.extend(diff[:30])
(BASE / ".workbuddy" / "_eq_0915.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("EQ", same)
