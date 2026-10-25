# -*- coding: utf-8 -*-
"""Step 8 复核：三篇润色稿的统计对抗独立复评 + 字数实测 + 分段统计。
输出落盘 _run_review_0927_out.txt（UTF-8），规避 PowerShell 乱码。
"""
import io
import re
import sys
import difflib
import importlib.util
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
D = ROOT / "drafts" / "2026-09-27"

# 加载规范校验.py 的权威 count_body_chars
spec = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

CASES = [
    ("A", D / "中美300亿美元对等降税落地-排除清单才是核心清单",
     "草稿-降了-300-亿美元关税，芯片一件没提，这比降税本身更值得看.md",
     "润色稿-降了-300-亿美元关税，芯片一件没提，这比降税本身更值得看.md"),
    ("B", D / "油价调控半年四次压缩涨幅-成品油定价这本账",
     "草稿-油价调控半年四次，少涨的-435-元到底谁承担.md",
     "润色稿-油价调控半年四次，少涨的-435-元到底谁承担.md"),
    ("C", D / "盖茨警告AI或致十亿人死亡-风险定义权与立法门槛",
     "草稿-盖茨说-AI-或致十亿人死亡，但重点不在这个数字.md",
     "润色稿-盖茨说-AI-或致十亿人死亡，但重点不在这个数字.md"),
]

MARKERS = ["## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 视觉与配图",
           "## 配图搜索替换指令", "## 参考来源", "## 润色说明", "## SEO 关键词"]


def body_of(p):
    t = Path(p).read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e != -1:
            t = t[e + 4:]
    t = re.sub(r"^#\s+.*$", "", t, flags=re.MULTILINE)
    cut = len(t)
    for m in MARKERS:
        i = t.find(m)
        if i != -1:
            cut = min(cut, i)
    return t[:cut]


def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def sents(t):
    t = re.sub(r"[#*>`\-\|\s]+", "", t)
    parts = [x for x in re.split(r"[。！？；\n]", t) if x.strip()]
    return [p for p in parts if cn(p) > 0]


buf = io.StringIO()


def P(*a):
    print(*a)
    print(*a, file=buf)


for tag, folder, draft_name, polish_name in CASES:
    dp, pp = folder / draft_name, folder / polish_name
    a, b = body_of(dp), body_of(pp)
    na, nb = cn(a), cn(b)
    ra, rb = re.sub(r"\s+", "", a), re.sub(r"\s+", "", b)
    sm = difflib.SequenceMatcher(None, ra, rb, autojunk=False)
    ratio = sm.ratio()
    diff_rate = (1 - ratio) * 100
    P(f"\n===== {tag} · {folder.name} =====")
    P(f"草稿正文 {na} 字 / 润色稿正文 {nb} 字 → 去字率 {(na-nb)/max(na,1)*100:.2f}%")
    P(f"相似度 {ratio:.4f}  差异率 {diff_rate:.2f}%")
    P(f"权威 count_body_chars 草稿 {chk.count_body_chars(dp)} / 润色稿 {chk.count_body_chars(pp)}")
    for t, name in ((a, "草稿"), (b, "润色稿")):
        ss = sents(t)
        L = [cn(s) for s in ss]
        mean = sum(L) / max(len(L), 1)
        std = (sum((x - mean) ** 2 for x in L) / max(len(L), 1)) ** 0.5
        paras = [p for p in t.split("\n\n") if cn(p) > 0]
        pL = [len([x for x in re.split(r"[。！？；]", p) if cn(x) > 0]) for p in paras]
        pm = sum(pL) / max(len(pL), 1)
        pstd = (sum((x - pm) ** 2 for x in pL) / max(len(pL), 1)) ** 0.5
        conn = sum(len(re.findall(k, t)) for k in ["然而", "此外", "因此", "同时", "并且", "更重要的是", "综上"])
        fml = sum(len(re.findall(k, t)) for k in [
            "不是[^。！？]{0,25}而是", "不只是[^。！？]{0,25}更是",
            "与其说[^。！？]{0,25}不如说", "不仅[^。！？]{0,25}而且"])
        xiang = len(re.findall(r"像[^。！？]{0,20}一样", t))
        q = len(re.findall(r"[？?]", t))
        P(f"[{name}] 句数 {len(ss)} 均长 {mean:.1f} 标准差 {std:.1f} | 段 {len(paras)} 段长标准差 {pstd:.1f} | "
          f"连接词 {conn} ({conn/max(cn(t)/1000,0.001):.2f}/千字) | 公式句 {fml} | 像…一样 {xiang} | 问号 {q}")

(ROOT / ".workbuddy" / "scripts" / "_run_review_0927_out.txt").write_text(buf.getvalue(), encoding="utf-8")
print("\n[saved] .workbuddy/scripts/_run_review_0927_out.txt")
