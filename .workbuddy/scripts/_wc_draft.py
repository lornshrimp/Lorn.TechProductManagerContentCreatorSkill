import re, sys
from pathlib import Path
TRUNC = ["## 素材溯源", "## 质量自检报告", "## 标题决策说明"]
def body(p):
    t = Path(p).read_text(encoding="utf-8")
    # strip frontmatter
    if t.startswith("---"):
        t = t.split("---", 2)[2]
    for m in TRUNC:
        i = t.find(m)
        if i != -1:
            t = t[:i]
    return t
def count(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))
p = sys.argv[1]
b = body(p)
print("BODY_CJK:", count(b))
# paragraph check
long_paras = []
for para in b.split("\n"):
    p2 = para.strip()
    if not p2 or p2.startswith("#"):
        continue
    n = count(p2)
    if n > 300:
        long_paras.append((n, p2[:40]))
print("LONG_PARAS(>300):", len(long_paras))
for n, s in long_paras:
    print("  ", n, s)
print("H2:", len(re.findall(r"(?m)^##\s", b)))
