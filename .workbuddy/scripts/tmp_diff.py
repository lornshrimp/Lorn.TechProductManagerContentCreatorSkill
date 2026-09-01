# -*- coding: utf-8 -*-
"""润色稿 vs 草稿 差异率实测（执行真实性铁律：差异 <5% 判未执行）
用法: python tmp_diff.py <草稿> <润色稿>
"""
import re, sys, difflib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tmp_wc import count_body_chars, BODY_TRUNCATE_MARKERS


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    text = re.sub(r"^#\s+.*$", "", text, flags=re.MULTILINE)
    cut = len(text)
    for m in BODY_TRUNCATE_MARKERS:
        i = text.find(m)
        if i != -1:
            cut = min(cut, i)
    return re.sub(r"\s+", "", text[:cut])


a, b = Path(sys.argv[1]), Path(sys.argv[2])
ta, tb = body(a), body(b)
sim = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False).ratio()
print("草稿字数 : %d" % count_body_chars(a))
print("润色稿字数: %d" % count_body_chars(b))
print("正文相似度: %.1f%%" % (sim * 100))
print("差异率   : %.1f%%  -> %s" % ((1 - sim) * 100, "✅ 真实执行" if (1 - sim) >= 0.05 else "❌ 疑似复制未执行"))
