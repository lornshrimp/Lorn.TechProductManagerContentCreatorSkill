import sys, importlib.util, re, difflib
from pathlib import Path
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
D = ROOT / "drafts" / "2026-09-25" / "中美第八轮经贸磋商达成多项共识-从谈判到机制"
spec = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def body(txt, platform=None):
    lines = txt.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i+1:]; break
    t = "\n".join(lines)
    cuts = ["## 素材溯源表", "## 质量自检报告", "## 视觉与配图", "## 配图搜索替换指令", "## SEO 关键词",
            "[封面图提示词]", "[内容简介]", "[配图1]"]
    if platform:
        # 百家号截于 SEO 关键词；其余截于 配图搜索替换指令/封面图提示词
        cuts = ["## SEO 关键词", "## 视觉与配图", "[封面图提示词]", "## 配图搜索替换指令"] if platform == "百家号" else \
               ["## 配图搜索替换指令", "[封面图提示词]", "[内容简介]", "[配图1]"]
    for c in cuts:
        if c in t: t = t.split(c)[0]
    return t

out = []
final = D / "终稿-从谈判到机制.md"
nf = m.count_body_chars(final)
out.append(f"终稿: {nf} 字 (深度分析体≥2500: {'OK' if nf>=2500 else 'FAIL'})")

plats = {
    "知乎-": (D / "知乎-从谈判到机制.md", 0.90),
    "微信-": (D / "微信-从谈判到机制.md", 0.85),
    "百家号-": (D / "百家号-从谈判到机制.md", 0.70),
    "CSDN-": (D / "CSDN-从谈判到机制.md", 0.70),
    "头条-": (D / "头条-从谈判到机制.md", 0.70),
}
pnames = {}
for pfx, (p, minr) in plats.items():
    n = m.count_body_chars(p)
    ratio = n / nf
    plat = pfx.rstrip("-")
    pnames[plat] = body(p.read_text(encoding="utf-8"), plat)
    flag = "OK" if ratio >= minr else "FAIL"
    out.append(f"{plat}: {n} 字 / 终稿 = {ratio:.1%} (底线 {minr:.0%}: {flag})")

fb = body(final.read_text(encoding="utf-8"))
for plat, t in pnames.items():
    sm = difflib.SequenceMatcher(None, fb, t, autojunk=False)
    r = sm.ratio()
    out.append(f"{plat} vs 终稿 相似度 = {r:.4f} ({'纯复述-超限!' if r>=0.99 else 'OK'})")

keys = list(pnames)
for i in range(len(keys)):
    for j in range(i+1, len(keys)):
        sm = difflib.SequenceMatcher(None, pnames[keys[i]], pnames[keys[j]], autojunk=False)
        r = sm.ratio()
        out.append(f"{keys[i]} vs {keys[j]} = {r:.4f} ({'超85%!' if r>=0.85 else 'OK'})")

# 配图张数
for plat, (p, _) in plats.items():
    t = p.read_text(encoding="utf-8")
    n = len(re.findall(r"\[配图\d+\]", t))
    out.append(f"{plat.rstrip('-')} 配图数 = {n}")

# H2 计数（正文）
for plat, (p, _) in plats.items():
    t = body(p.read_text(encoding="utf-8"), plat.rstrip("-"))
    out.append(f"{plat.rstrip('-')} 正文 H2 = {len(re.findall(r'^## ', t, re.M))}")

Path(str(ROOT / ".workbuddy" / "_wc_out.txt")).write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
