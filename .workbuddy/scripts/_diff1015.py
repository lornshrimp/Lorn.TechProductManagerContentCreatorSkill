# -*- coding: utf-8 -*-
"""2026-10-15 差异率 + 相似度实测（difflib，正文去空白）"""
import sys, io, re, difflib, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def body(p):
    p = Path(p)
    if not p.is_absolute():
        p = ROOT / p
    return chk.extract_body_text(p)


def sim(a, b):
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


def run(title, files):
    texts = {Path(f).name: body(f) for f in files}
    print(f"\n=== {title} ===")
    print(f"difflib 差异率({Path(files[0]).name} vs {Path(files[1]).name}) = {1 - sim(texts[Path(files[0]).name], texts[Path(files[1]).name]):.2%}")
    names = list(texts)
    if len(names) > 2:
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                print(f"  sim {names[i]} vs {names[j]} = {sim(texts[names[i]], texts[names[j]]):.2%}")


if __name__ == "__main__":
    d = sys.argv[1]
    run("草稿 vs 润色稿", [f"{d}/{sys.argv[2]}", f"{d}/{sys.argv[3]}"])
