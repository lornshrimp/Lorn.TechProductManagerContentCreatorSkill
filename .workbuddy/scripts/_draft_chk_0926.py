#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""草稿 H2 结构与正文字数实测（含互动引导小标题门禁 + notebook 引用核实）"""
import re, sys
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")

files = [
    ROOT / "drafts/2026-09-26/全国牛肉批发均价涨至一公斤71元-创两年新高/草稿-牛肉创两年新高-CPI-只有-0-8-两个数为什么都是真的.md",
    ROOT / "drafts/2026-09-26/Anthropic推演2030美国经济-钱继续流向有钱人/草稿-Anthropic-自己算出了-钱继续流向有钱人-AI-的账-不在能力表上-在分配那一栏.md",
    ROOT / "drafts/2026-09-26/央视曝光挂靠参保骗社保-灰色产业链如何运作/草稿-1875元买一份假劳动关系-挂靠参保打不掉-是因为它的那一头连着需求.md",
]

buf = []
for p in files:
    buf.append("=" * 70)
    buf.append(str(p.name))
    if not p.exists():
        buf.append("  ❌ 不存在")
        continue
    txt = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n.*?\n---\n", txt, re.S)
    body = txt[m.end():] if m else txt
    # 截断附属内容
    markers = ["## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 互动引导", "## 读者互动"]
    cut = len(body)
    for mk in markers:
        i = body.find(mk)
        if i != -1:
            cut = min(cut, i)
    body = body[:cut]
    zh = len(re.findall(r"[\u4e00-\u9fff]", body))
    buf.append(f"  正文中文字符：{zh}")
    h2 = re.findall(r"^##\s+(.+)$", body, re.MULTILINE)
    buf.append(f"  H2 数：{len(h2)}")
    for h in h2:
        buf.append(f"    - {h}")
    # 互动引导小标题门禁
    bad = re.findall(r"^#{1,3}\s*(读者互动|互动引导)\s*$", body, re.MULTILINE)
    buf.append(f"  互动引导独立小标题（须为空）：{bad}")
    # 超长段
    for i, para in enumerate([x for x in body.split("\n") if x.strip() and not x.strip().startswith("#")], 1):
        n = len(re.findall(r"[\u4e00-\u9fff]", para))
        if n > 300:
            buf.append(f"  ❌ 超长段 {i}：{n} 字")
    # notebook 引用核实
    refs = set(re.findall(r"notebook/([\w\u4e00-\u9fff\-\.]+\.md)", txt))
    nb = ROOT / "notebook"
    for r in sorted(refs):
        ok = (nb / r).exists()
        buf.append(f"  notebook 引用 notebook/{r}: {'OK' if ok else '❌不存在'}")

(ROOT / ".workbuddy/scripts/_draft_chk_out.txt").write_text("\n".join(buf), encoding="utf-8")
print("done")
