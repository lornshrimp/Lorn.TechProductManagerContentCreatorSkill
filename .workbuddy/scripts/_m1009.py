# -*- coding: utf-8 -*-
"""字数实测：复用 规范校验.py 的 count_body_chars（正文中文字符），传文件路径参数"""
import sys, io, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
SPEC = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
chk = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chk)

for p in sys.argv[1:]:
    pp = Path(p)
    try:
        print(f"{chk.count_body_chars(pp):6d}  {pp.name}")
    except Exception as e:
        print(f"  ERR  {pp.name}: {e}")
