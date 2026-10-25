import difflib
import io
import re
import sys
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")

PAIRS = [
    ("A-牛肉",
     "drafts/2026-09-26/全国牛肉批发均价涨至一公斤71元-创两年新高/草稿-牛肉创两年新高-CPI-只有-0-8-两个数为什么都是真的.md",
     "drafts/2026-09-26/全国牛肉批发均价涨至一公斤71元-创两年新高/润色稿-牛肉创两年新高-CPI-只有-0-8-两个数为什么都是真的.md"),
    ("B-Anthropic",
     "drafts/2026-09-26/Anthropic推演2030美国经济-钱继续流向有钱人/草稿-Anthropic-自己算出了-钱继续流向有钱人-AI-的账-不在能力表上-在分配那一栏.md",
     "drafts/2026-09-26/Anthropic推演2030美国经济-钱继续流向有钱人/润色稿-Anthropic-自己算出了-钱继续流向有钱人-AI-的账-不在能力表上-在分配那一栏.md"),
    ("C-挂靠",
     "drafts/2026-09-26/央视曝光挂靠参保骗社保-灰色产业链如何运作/草稿-1875元买一份假劳动关系-挂靠参保打不掉-是因为它的那一头连着需求.md",
     "drafts/2026-09-26/央视曝光挂靠参保骗社保-灰色产业链如何运作/润色稿-1875元买一份假劳动关系-挂靠参保打不掉-是因为它的那一头连着需求.md"),
]

TRUNC = ["## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 封面图", "## 内容简介"]


def body_of(text):
    t = text
    if t.startswith("---"):
        parts = t.split("---", 2)
        if len(parts) >= 3:
            t = parts[2]
    for m in TRUNC:
        i = t.find(m)
        if i != -1:
            t = t[:i]
    return t.strip()


def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


out = io.StringIO()
for name, dp, pp in PAIRS:
    df, pf = ROOT / dp, ROOT / pp
    out.write("=" * 70 + "\n")
    out.write(f"{name}\n")
    if not df.exists():
        out.write("  草稿不存在\n"); continue
    out.write(f"  草稿存在：{df.stat().st_size} 字节\n")
    if not pf.exists():
        out.write("  润色稿：❌不存在（待生成）\n"); continue
    dt = df.read_text(encoding="utf-8")
    pt = pf.read_text(encoding="utf-8")
    db, pb = body_of(dt), body_of(pt)
    out.write(f"  草稿正文中文字符：{cn(db)}\n")
    out.write(f"  润色稿正文中文字符：{cn(pb)}\n")
    if cn(db):
        cut = (cn(db) - cn(pb)) / cn(db) * 100
        out.write(f"  去字率：{cut:.2f}%\n")
    r = difflib.SequenceMatcher(None, db, pb, autojunk=False).ratio()
    out.write(f"  正文相似度：{r:.4f}  差异率：{(1-r)*100:.2f}%\n")
    if (1 - r) < 0.05:
        out.write("  ⚠️ 差异 <5%，可能未真实编辑\n")
    # H2
    h2 = re.findall(r"^## (?!#)(.+)$", pb, re.M)
    out.write(f"  润色稿 H2 数：{len(h2)}\n")
    inter = re.findall(r"^#{1,3}\s*(读者互动|互动引导)\s*$", pb, re.M)
    out.write(f"  互动引导独立小标题（须为空）：{inter}\n")
    # 超长段
    longps = [p[:30] for p in pb.split("\n\n") if cn(p) > 300]
    out.write(f"  >300 字段落：{longps if longps else '无'}\n")
    # notebook refs
    refs = set(re.findall(r"notebook/([^\s\)）`\]]+\.md)", pb))
    bad = [x for x in refs if not (ROOT / "notebook" / x).exists()]
    out.write(f"  notebook 引用：{sorted(refs)}\n")
    out.write(f"  失效引用：{bad if bad else '无'}\n")

(ROOT / ".workbuddy/scripts/_polish_chk_out.txt").write_text(out.getvalue(), encoding="utf-8")
print("done")
