# -*- coding: utf-8 -*-
"""差异率实测：润色稿 vs 草稿 正文（去空白），difflib autojunk=False"""
import sys, io, importlib.util, difflib, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
SPEC = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
chk = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chk)


def body(p):
    return re.sub(r"\s+", "", chk.extract_body_text(Path(p)))


a = body(sys.argv[1])  # 草稿
b = body(sys.argv[2])  # 润色稿
r = difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()
print(f"草稿正文={len(a)}  润色正文={len(b)}  相似度={r:.4f}  差异率={(1-r)*100:.2f}%")
print(f"字数(中文字符): 草稿={chk.count_body_chars(Path(sys.argv[1]))} 润色={chk.count_body_chars(Path(sys.argv[2]))}")
