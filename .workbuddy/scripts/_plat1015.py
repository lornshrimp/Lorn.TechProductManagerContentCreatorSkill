# -*- coding: utf-8 -*-
"""2026-10-15 三选题平台保真矩阵（字数 / 占终稿比 / 与终稿相似度 / 两两最大）"""
import sys, io, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

base = ROOT / "drafts" / "2026-10-15"
for d in sorted(base.iterdir()):
    if not d.is_dir():
        continue
    finals = list(d.glob("终稿-*.md"))
    if not finals:
        continue
    fc = chk.count_body_chars(finals[0])
    print(f"\n=== {d.name} | 终稿 {fc} 字 ===")
    plats = [f for f in sorted(d.glob('*.md')) if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)]
    texts = {}
    for pf in plats:
        n = chk.count_body_chars(pf)
        sim = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(finals[0]))
        texts[pf.name] = chk.extract_body_text(pf)
        print(f"  {pf.name}: {n} 字 = 终稿 {n*100//fc}% | 与终稿相似 {sim:.2%}")
    nm = sorted(texts)
    mx = 0.0
    pair = ""
    for i in range(len(nm)):
        for j in range(i + 1, len(nm)):
            s = chk.text_similarity(texts[nm[i]], texts[nm[j]])
            if s > mx:
                mx, pair = s, f"{nm[i]} vs {nm[j]}"
    print(f"  两两最大: {mx:.2%} ({pair})")
