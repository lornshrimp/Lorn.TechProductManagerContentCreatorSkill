import re, sys, difflib
from pathlib import Path
TRUNC = ["## 素材溯源", "## 质量自检报告", "## 标题决策说明"]
def body(p):
    t = Path(p).read_text(encoding="utf-8")
    if t.startswith("---"):
        t = t.split("---", 2)[2]
    for m in TRUNC:
        i = t.find(m)
        if i != -1:
            t = t[:i]
    return re.sub(r"\s+", "", t)
a = body(sys.argv[1]); b = body(sys.argv[2])
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
ratio = sm.ratio()
diff_ratio = 1 - ratio
matched = sum(bl.size for bl in sm.get_matching_blocks())
# changed chars estimate
print("A_LEN:", len(a), "B_LEN:", len(b))
print("SIMILARITY: %.4f" % ratio)
print("DIFF: %.4f%%" % (diff_ratio*100))
ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
print("EDIT_OPS:", len(ops))
