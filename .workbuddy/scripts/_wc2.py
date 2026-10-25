import sys, importlib.util, re, difflib
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def body(txt, cut=True):
    lines = txt.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i+1:]
                break
    t = "\n".join(lines)
    if cut:
        for marker in ["## 素材溯源表", "## 质量自检报告", "## 标题决策说明", "## 视觉与配图", "## 配图搜索替换指令"]:
            if marker in t:
                t = t.split(marker)[0]
    return t

out = []
args = sys.argv[1:]
files = [a for a in args if a != "--diff"]
for p in files:
    pp = Path(p)
    n = m.count_body_chars(pp)
    t = pp.read_text(encoding="utf-8")
    b = body(t)
    h2 = len(re.findall(r"^##\s+", b, re.MULTILINE))
    out.append(f"{pp.name}: 正文中文字符={n}  H2(正文)={h2}")

if "--diff" in args and len(files) >= 2:
    a = body(Path(files[0]).read_text(encoding="utf-8"))
    b = body(Path(files[1]).read_text(encoding="utf-8"))
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ratio = sm.ratio()
    out.append(f"[DIFF] {Path(files[0]).name} vs {Path(files[1]).name}: 相似度={ratio:.4f} 差异率={(1-ratio)*100:.2f}%")

Path(str(ROOT / ".workbuddy" / "_wc_out.txt")).write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
