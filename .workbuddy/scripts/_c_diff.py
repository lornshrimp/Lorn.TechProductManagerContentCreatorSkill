# -*- coding: utf-8 -*-
"""草稿 vs 润色稿：正文字数 + 差异率（difflib autojunk=False，去空白）"""
import sys, io, runpy, re, difflib
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
CHECKER = BASE / ".workbuddy" / "scripts" / "规范校验.py"

buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
ns = runpy.run_path(str(CHECKER), run_name="_notmain_")
sys.stdout = old

count_body_chars = ns["count_body_chars"]
extract_body_text = ns["extract_body_text"]

a, b = Path(sys.argv[1]), Path(sys.argv[2])
ta = re.sub(r"\s+", "", extract_body_text(a))
tb = re.sub(r"\s+", "", extract_body_text(b))
ratio = difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()
diff_rate = 1 - ratio
ca, cb = count_body_chars(a), count_body_chars(b)

out = [
    f"草稿正文中文字符: {ca}",
    f"润色稿正文中文字符: {cb}",
    f"字数留存率: {cb / ca:.4f}",
    f"相似度(difflib): {ratio:.4f}",
    f"差异率: {diff_rate:.4%}",
    f"差异率是否 >=5%: {diff_rate >= 0.05}",
]
txt = "\n".join(out)
(BASE / ".workbuddy" / "_c_diff.txt").write_text(txt, encoding="utf-8")
print(txt)
