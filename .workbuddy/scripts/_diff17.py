# -*- coding: utf-8 -*-
"""差异率实测：草稿 vs 润色稿（正文去空白 + difflib autojunk=False）。"""
import sys, difflib, importlib.util, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gb", HERE / "规范校验.py")
gb = importlib.util.module_from_spec(spec); spec.loader.exec_module(gb)
a, b = sys.argv[1], sys.argv[2]
ta = re.sub(r"\s+", "", gb.extract_body_text(Path(a)))
tb = re.sub(r"\s+", "", gb.extract_body_text(Path(b)))
s = difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()
print(f"draft={len(ta)}  polish={len(tb)}  sim={s*100:.2f}%  diff={(1-s)*100:.2f}%")
