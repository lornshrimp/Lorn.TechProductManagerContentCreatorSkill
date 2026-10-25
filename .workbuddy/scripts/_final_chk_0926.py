# -*- coding: utf-8 -*-
import re, io, sys
from pathlib import Path

BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/drafts/2026-09-26")
TRUNC = ["## 素材溯源", "## 质量自检报告", "## 标题决策说明", "## 配图搜索替换指令", "## 视觉与配图"]
out = io.StringIO()

def split_fm(t):
    if t.startswith("---"):
        p = t.split("---", 2)
        if len(p) >= 3:
            return p[1], p[2]
    return "", t

def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))

def body_only(t):
    fm, b = split_fm(t)
    for m in TRUNC:
        i = b.find(m)
        if i != -1:
            b = b[:i]
    return b.strip()

dirs = {
    "A": ("全国牛肉批发均价涨至一公斤71元-创两年新高", "终稿-牛肉创两年新高-CPI-只有-0-8-两个数为什么都是真的.md"),
    "B": ("Anthropic推演2030美国经济-钱继续流向有钱人", "终稿-Anthropic-自己算出了-钱继续流向有钱人-AI-的账-不在能力表上-在分配那一栏.md"),
    "C": ("央视曝光挂靠参保骗社保-灰色产业链如何运作", "终稿-1875元买一份假劳动关系-挂靠参保打不掉-是因为它的那一头连着需求.md"),
}

for k, (d, f) in dirs.items():
    p = BASE / d / f
    out.write("=" * 70 + "\n")
    out.write(f"[{k}] {p.name}\n")
    if not p.exists():
        out.write("  !! 文件不存在\n")
        continue
    raw = p.read_text(encoding="utf-8")
    fm, b = split_fm(raw)
    out.write("--- frontmatter ---\n")
    for line in fm.strip().splitlines():
        if line.strip():
            out.write("  " + line.strip() + "\n")
    keys = [l.split(":")[0].strip() for l in fm.strip().splitlines() if ":" in l and not l.strip().startswith("#")]
    out.write(f"  键: {keys}\n")
    body = body_only(raw)
    out.write(f"  正文中文字符: {cn(body)}\n")
    out.write(f"  H2 数: {len(re.findall(r'^## ', body, re.M))}\n")
    out.write(f"  含 ## 视觉与配图: {'## 视觉与配图' in raw}\n")
    out.write(f"  含 ## 配图搜索替换指令: {'## 配图搜索替换指令' in raw}\n")
    out.write(f"  含 ## 素材溯源: {'## 素材溯源' in raw}\n")
    out.write(f"  含 ## 质量自检报告: {'## 质量自检报告' in raw}\n")
    out.write(f"  互动引导独立小标题: {bool(re.search(r'^#{1,3}\s*(读者互动|互动引导)\s*$', raw, re.M))}\n")
    # para lengths
    paras = [x for x in body.split("\n\n") if x.strip() and not x.strip().startswith("#")]
    over = [(i, cn(x)) for i, x in enumerate(paras) if cn(x) > 300]
    out.write(f"  段数: {len(paras)}; >300字段落: {over if over else '无'}\n")
    # figure count
    figs = re.findall(r"^### 配图(\d+)", raw, re.M)
    out.write(f"  配图张数: {len(figs)} ({figs})\n")
    # cover prompt present
    out.write(f"  封面图提示词: {'### 封面图提示词' in raw}\n")
    out.write(f"  内容简介: {'### 内容简介' in raw}\n")
    # 首图提示词宽高比
    m = re.search(r"### 封面图提示词\s*\n+(.+?)(?=\n###|\n##|\Z)", raw, re.S)
    if m:
        ratio = "16:9" if "16:9" in m.group(1) else ("3:2" if "3:2" in m.group(1) else "?")
        out.write(f"  封面比例: {ratio}\n")
    # 字数实测段
    out.write(f"  包含「实测」字样: {'实测' in raw}\n")

Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/_final_chk_0926_out.txt").write_text(out.getvalue(), encoding="utf-8")
print("DONE")
