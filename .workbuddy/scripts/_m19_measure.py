# -*- coding: utf-8 -*-
"""本地实测：正文字数（复用规范校验.py 的 count_body_chars 口径）+ 两文件差异率。"""
import sys, io, difflib, re
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
sys.path.insert(0, str(ROOT / ".workbuddy" / "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location("vld", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
vld = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vld)

def bc(p):
    return vld.count_body_chars(Path(p))

def body(p):
    t = Path(p).read_text(encoding="utf-8", errors="ignore")
    return t

def diffrate(a, b):
    """正文差异率：去 frontmatter/附属区、去空白后 difflib autojunk=False。"""
    ta = vld.extract_body_text(Path(a))
    tb = vld.extract_body_text(Path(b))
    na = re.sub(r"\s+", "", ta)
    nb = re.sub(r"\s+", "", tb)
    sm = difflib.SequenceMatcher(None, na, nb, autojunk=False)
    return 1 - sm.ratio(), len(na), len(nb)

if __name__ == "__main__":
    out = []
    cmd = sys.argv[1]
    if cmd == "wc":
        for p in sys.argv[2:]:
            out.append(f"{bc(p):>6}  {Path(p).name}")
    elif cmd == "diff":
        r, la, lb = diffrate(sys.argv[2], sys.argv[3])
        out.append(f"diff={r*100:.2f}%  A={la} B={lb}  {Path(sys.argv[2]).name} vs {Path(sys.argv[3]).name}")
    Path(ROOT / ".workbuddy" / "scripts" / "_wc_out.txt").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
