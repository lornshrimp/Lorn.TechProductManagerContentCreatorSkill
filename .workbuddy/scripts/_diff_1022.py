# -*- coding: utf-8 -*-
"""差异实测：草稿 vs 润色稿（正文区，autojunk=False）"""
import io, sys, re, difflib, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def body(p):
    return chk.extract_body_text(Path(p))


def ratio(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    blocks = [b for b in sm.get_opcodes() if b[0] != "equal"]
    return sm.ratio(), len(blocks)


for d in sys.argv[1:]:
    dp = Path(d)
    drafts = list(dp.glob("草稿-*.md"))
    pols = list(dp.glob("润色稿-*.md"))
    if not drafts or not pols:
        print(f"{dp.name}: 缺文件")
        continue
    a, b = body(drafts[0]), body(pols[0])
    r, nb = ratio(a, b)
    ca, cb = chk.count_body_chars(drafts[0]), chk.count_body_chars(pols[0])
    print(f"{dp.name}")
    print(f"  草稿 {ca} 字 / 润色稿 {cb} 字 / 变动 {(cb-ca)/ca*100:+.2f}%")
    print(f"  正文相似度 {r*100:.2f}% / 差异率 {(1-r)*100:.2f}% / 差异块 {nb}")
    print(f"  判定 {'✅ 真实编辑' if (1-r)>=0.05 else '❌ 未达5%'}")
