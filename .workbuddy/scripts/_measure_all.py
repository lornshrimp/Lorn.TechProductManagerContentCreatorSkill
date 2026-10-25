# -*- coding: utf-8 -*-
"""实测指定日期目录下所有稿件字数/差异率/保真比/相似度。"""
import importlib.util, sys, difflib
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
SPEC = ROOT / ".workbuddy" / "scripts" / "规范校验.py"
spec = importlib.util.spec_from_file_location("guifan", str(SPEC))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

DATE = sys.argv[1] if len(sys.argv) > 1 else "2026-09-23"
BASE = ROOT / "drafts" / DATE
out = []
if not BASE.exists():
    out.append("NO DIR " + str(BASE))
else:
    for d in sorted([p for p in BASE.iterdir() if p.is_dir()]):
        out.append("=" * 70)
        out.append("TOPIC: " + d.name)
        files = {p.name: p for p in d.iterdir() if p.is_file()}
        def show(name):
            p = files.get(name)
            if p is None:
                out.append("  [MISS] " + name)
                return None
            try:
                n = g.count_body_chars(p)
            except Exception as e:
                n = "ERR:" + str(e)
            out.append("  {:52s} chars={}".format(name, n))
            return p
        # locate files by keyword
        def find(kw):
            for nm, p in files.items():
                if kw in nm:
                    return p
            return None
        draft = find("草稿-")
        polish = find("润色稿-")
        final = find("终稿-")
        for nm, p in sorted(files.items()):
            try:
                n = g.count_body_chars(p)
            except Exception as e:
                n = "ERR"
            out.append("  {:52s} chars={}".format(nm, n))
        def body(p):
            if p is None:
                return ""
            try:
                return g.extract_body_text(p)
            except Exception:
                return ""
        def sim(a, b):
            if not a or not b:
                return None
            return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()
        bd, bp, bf = body(draft), body(polish), body(final)
        if bd and bp:
            r = sim(bd, bp)
            # difference ratio: 1 - longest common? use 1-sim
            out.append("  DIFF draft vs polish: sim={:.4f} diff={:.2%}".format(r, 1 - r))
        if bp and bf:
            r = sim(bp, bf)
            out.append("  SIM polish vs final: {:.4f}".format(r))
        # platform files
        plats = [p for nm, p in files.items() if any(k in nm for k in ["知乎-", "微信-", "百家号-", "CSDN-", "头条-"])]
        if bf and plats:
            for p in sorted(plats, key=lambda x: x.name):
                r = sim(body(p), bf)
                out.append("  PLATFORM {:16s} fidelity={:.4f}  chars={}".format(p.name, r if r else 0, g.count_body_chars(p)))
            for i in range(len(plats)):
                for j in range(i + 1, len(plats)):
                    r = sim(body(plats[i]), body(plats[j]))
                    if r and r >= 0.80:
                        out.append("  !! PAIR {}/{} sim={:.4f}".format(plats[i].name, plats[j].name, r))
        # structure
        for p in [draft, polish, final] + plats:
            if p is None:
                continue
            try:
                issues = g.check_body_structure(p, p.name)
                for it in issues:
                    out.append("  STRUCT ISSUE: " + str(it))
            except Exception as e:
                out.append("  STRUCT ERR " + p.name + ": " + str(e))

(ROOT / ".workbuddy" / ("_measure_" + DATE.replace("-", "") + ".txt")).write_text("\n".join(out), encoding="utf-8")
print("DONE")
