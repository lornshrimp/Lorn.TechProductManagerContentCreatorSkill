# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path
ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", str(ROOT/".workbuddy/scripts/规范校验.py"))
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)
D = ROOT/"drafts/2026-09-27"
for d in sorted(D.iterdir()):
    if not d.is_dir(): continue
    for f in sorted(d.glob("终稿-*.md")):
        print("==", d.name)
        print("  字数:", chk.count_body_chars(f))
        for x in chk.check_body_structure(f, "终稿-"): print(" ", x)
        for x in chk.check_anchor_quality(f): print(" ", x)
