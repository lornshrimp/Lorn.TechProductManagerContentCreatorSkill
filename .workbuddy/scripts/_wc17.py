# -*- coding: utf-8 -*-
"""字数与差异率实测工具（复用 规范校验.py 的 count_body_chars 口径）。"""
import sys, difflib, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gb", HERE / "规范校验.py")
gb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gb)


def body(p):
    return gb.count_body_chars(Path(p))


def sim(a, b):
    ta = gb.extract_body_text(Path(a))
    tb = gb.extract_body_text(Path(b))
    return difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()


if __name__ == "__main__":
    args = sys.argv[1:]
    # 模式1: 单文件字数  wc file...
    # 模式2: 比率  ratio a b  ->  b相对a的比率 + 相似度
    if args and args[0] == "ratio":
        a, b = args[1], args[2]
        wa, wb = body(a), body(b)
        print(f"base={wa}  cur={wb}  ratio={wb/wa*100:.1f}%  sim={sim(a,b)*100:.1f}%")
    else:
        for p in args:
            print(f"{body(p)}\t{Path(p).name}")
