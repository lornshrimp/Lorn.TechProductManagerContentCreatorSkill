# -*- coding: utf-8 -*-
"""测量 C 题平台稿两两相似度 + 与终稿相似度（精确复刻校验脚本口径）。"""
import difflib
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent.parent.parent
D = BASE / "drafts" / "2026-09-19" / "8月16-24岁失业率18.9%-统计口径这本账"

BODY_TRUNCATE_MARKERS = [
    "## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 封面图",
    "## 内容简介", "## 互动引导", "## SEO 关键词", "## 配图详情",
    "# 附属内容区域", "## 配图搜索替换指令", "## 参考来源",
    "## 润色说明", "## 发布建议",
]


def extract_body_text(p: pathlib.Path) -> str:
    text = p.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    text = re.sub(r"^#\s+.*$", "", text, flags=re.MULTILINE)
    for marker in BODY_TRUNCATE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
            break
    return re.sub(r"\s+", "", text)


def sim(a, b):
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


files = {
    "知乎": D / "知乎-统计口径这本账.md",
    "微信": D / "微信-统计口径这本账.md",
    "百家号": D / "百家号-统计口径这本账.md",
    "CSDN": D / "CSDN-统计口径这本账.md",
    "头条": D / "头条-统计口径这本账.md",
}
final = D / "终稿-统计口径这本账.md"

tb = {k: extract_body_text(v) for k, v in files.items()}
ft = extract_body_text(final)
print("终稿 chars =", len(ft))
for k, v in tb.items():
    print(f"  {k}: {len(v)} chars | 与终稿 {sim(v, ft):.1%}")
print("--- 两两 ---")
ks = sorted(tb)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        s = sim(tb[ks[i]], tb[ks[j]])
        flag = "  <<<FAIL" if s >= 0.85 else ""
        print(f"  {ks[i]} vs {ks[j]}: {s:.1%}{flag}")
