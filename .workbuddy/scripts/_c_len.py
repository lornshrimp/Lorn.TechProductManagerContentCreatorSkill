# -*- coding: utf-8 -*-
"""通用单文件字数实测（校验脚本同口径）"""
import sys, io, runpy
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
CHECKER = BASE / ".workbuddy" / "scripts" / "规范校验.py"

# 同进程导入 count_body_chars / extract_body_text / text_similarity
buf = io.StringIO()
old_out = sys.stdout
sys.stdout = buf
ns = runpy.run_path(str(CHECKER), run_name="_notmain_")
sys.stdout = old_out

count_body_chars = ns["count_body_chars"]
text_similarity = ns["text_similarity"]

targets = sys.argv[1:]
out = []
for t in targets:
    p = Path(t)
    if not p.exists():
        out.append(f"MISSING: {t}")
        continue
    out.append(f"{p.name}: {count_body_chars(p)}")

# 相似度对（成对传入 2 个即比对）
if len(targets) == 2:
    out.append(f"similarity: {text_similarity(Path(targets[0]), Path(targets[1])):.4f}")

txt = "\n".join(out)
(BASE / ".workbuddy" / "_c_len.txt").write_text(txt, encoding="utf-8")
print(txt)
