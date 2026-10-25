# -*- coding: utf-8 -*-
"""用「规范校验.py」自身的 count_body_chars 实测字数（权威口径）。
用法：python _chk_wc.py <文件1> [<文件2> ...]
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("guifan", ROOT / "规范校验.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

lines = []
for arg in sys.argv[1:]:
    p = Path(arg)
    if not p.exists():
        lines.append(f"NOT_FOUND\t{arg}")
        continue
    lines.append(f"{mod.count_body_chars(p)}\t{p.name}")
Path(ROOT / "_chk_wc_out.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
