# -*- coding: utf-8 -*-
"""2026-10-08 本地实测：正文字数（同 规范校验.py count_body_chars 口径）"""
import sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BODY_TRUNCATE_MARKERS = [
    "## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 封面图",
    "## 内容简介", "## 互动引导", "## SEO 关键词", "## 配图详情",
    "# 附属内容区域", "## 配图搜索替换指令", "## 参考来源",
    "## 润色说明", "## 发布建议",
]


def count_body_chars(path):
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
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
    return len(re.findall(r"[\u4e00-\u9fff]", text))


for p in sys.argv[1:]:
    pp = Path(p)
    if pp.is_file():
        print(f"{count_body_chars(pp):6d}  {pp.name}")
    elif pp.is_dir():
        for f in sorted(pp.glob("*.md")):
            print(f"{count_body_chars(f):6d}  {f.name}")
