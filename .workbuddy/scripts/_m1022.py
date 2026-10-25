# -*- coding: utf-8 -*-
"""平台稿相似度/保真比矩阵（复用 规范校验.py 口径）"""
import io, sys, importlib.util, itertools
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

DATE = "2026-10-22"
for d in sorted((ROOT / "drafts" / DATE).iterdir()):
    if not d.is_dir():
        continue
    fin = list(d.glob("终稿-*.md"))
    if not fin:
        continue
    fn = chk.count_body_chars(fin[0])
    ft = chk.extract_body_text(fin[0])
    print(f"\n### {d.name}  终稿 {fn}")
    pf = [f for f in sorted(d.glob("*.md")) if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)]
    data = {}
    for f in pf:
        n = chk.count_body_chars(f)
        sim = chk.text_similarity(chk.extract_body_text(f), ft)
        data[f.name] = (n, sim)
        print(f"  {f.name:28s} {n:5d} {n/fn*100:5.1f}%  vs终稿 {sim*100:5.2f}%")
    best = (0, "", "")
    for a, b in itertools.combinations(sorted(data), 2):
        s = chk.text_similarity(chk.extract_body_text(d / a), chk.extract_body_text(d / b))
        if s > best[0]:
            best = (s, a, b)
        print(f"    {a[:6]}×{b[:6]} {s*100:5.2f}%")
    print(f"  MAX_PAIR {best[0]*100:.2f}% ({best[1]} × {best[2]})")
