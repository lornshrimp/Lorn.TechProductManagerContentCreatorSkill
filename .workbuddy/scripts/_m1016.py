# -*- coding: utf-8 -*-
"""实测字数 + 相似度矩阵 + 差异率（复用 规范校验.py 口径）"""
import sys, io, os, runpy, difflib
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts")
import importlib.util
spec = importlib.util.spec_from_file_location("chk", r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = "2026-10-16"


def cbc(p):
    return chk.count_body_chars(Path(p))


def body(p):
    return chk.extract_body_text(Path(p))


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def diffrate(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return 1 - sm.ratio()


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "dir":
        base = ROOT / "drafts" / D / args[1]
        names = {"草稿": None, "润色": None, "终稿": None}
        for f in sorted(base.glob("*.md")):
            n = f.name
            if n.startswith("草稿-"): names["草稿"] = f
            elif n.startswith("润色稿-"): names["润色"] = f
            elif n.startswith("终稿-"): names["终稿"] = f
        print("== 字数 ==")
        for k, f in names.items():
            if f: print(f"  {k}: {cbc(f)} 字  ({f.name})")
        if names["草稿"] and names["润色"]:
            print(f"  草稿→润色 差异率: {diffrate(body(names['草稿']), body(names['润色'])):.2%}  (需 ≥5%)")
        if names["润色"] and names["终稿"]:
            print(f"  润色→终稿 差异率: {diffrate(body(names['润色']), body(names['终稿'])):.2%}")
        fin = names["终稿"]
        if fin:
            fc = cbc(fin)
            print("== 平台稿保真 ==")
            for pref, ratio in [("知乎-", 0.90), ("微信-", 0.85), ("百家号-", 0.70), ("CSDN-", 0.70), ("头条-", 0.70)]:
                for pf in sorted(base.glob(pref + "*.md")):
                    pn = cbc(pf)
                    s = sim(body(pf), body(fin))
                    ok1 = "OK" if pn >= fc * ratio else "LOW"
                    ok2 = "OK" if s < 0.99 else "COPY"
                    print(f"  {pf.name}: {pn} ({pn*100//fc}%) [{ratio:.0%} {ok1}] 与终稿相似 {s:.2%} [{ok2}]")
            print("== 平台两两 ==")
            pfs = [f for f in sorted(base.glob("*.md")) if any(f.name.startswith(p) for p in ["知乎-", "微信-", "百家号-", "CSDN-", "头条-"])]
            worst = 0; pair = ""
            for i in range(len(pfs)):
                for j in range(i + 1, len(pfs)):
                    s = sim(body(pfs[i]), body(pfs[j]))
                    if s > worst: worst, pair = s, f"{pfs[i].name} vs {pfs[j].name}"
            print(f"  最高两两相似度: {worst:.2%} ({pair})  [需 <85%]")
    else:
        for p in args:
            print(f"{cbc(p)} 字  {p}")
