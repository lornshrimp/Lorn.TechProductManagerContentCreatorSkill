# -*- coding: utf-8 -*-
"""字数实测工具：与 .workbuddy/scripts/规范校验.py count_body_chars 完全同口径。
用法: python wc_body.py <file1> [file2 ...]
口径: 去 frontmatter / H1 / 附属区(素材溯源/质量自检/封面/配图等) 后统计中文字符 [\\u4e00-\\u9fff]
注意: 数字与标点不计入——与校验脚本一致。
"""
import re, sys
from pathlib import Path

BODY_TRUNCATE_MARKERS = [
    "## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 封面图",
    "## 内容简介", "## 互动引导", "## SEO 关键词", "## 配图详情",
    "# 附属内容区域", "## 配图搜索替换指令", "## 参考来源",
    "## 润色说明", "## 发布建议",
]


def count_body_chars(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    text = re.sub(r"^#\s+.*$", "", text, flags=re.MULTILINE)
    cut = len(text)
    for marker in BODY_TRUNCATE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    text = text[:cut]
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def count_body_h2(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    cut = len(text)
    for marker in BODY_TRUNCATE_MARKERS + ["[封面图提示词]", "[内容简介]", "[配图"]:
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    text = text[:cut]
    return len(re.findall(r"^##(?!#)\s+", text, flags=re.MULTILINE))


def max_para(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    cut = len(text)
    for marker in BODY_TRUNCATE_MARKERS + ["[封面图提示词]", "[内容简介]", "[配图"]:
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    text = text[:cut]
    paras = [p for p in text.split("\n\n") if p.strip()]
    best = 0
    for p in paras:
        if p.strip().startswith(("#", "|", ">", "-", "*", "[")):
            continue
        n = len(re.findall(r"[\u4e00-\u9fff]", p))
        best = max(best, n)
    return best


if __name__ == "__main__":
    for a in sys.argv[1:]:
        p = Path(a)
        print("%-64s %5d 字  H2=%d  最长段=%d" % (
            p.name, count_body_chars(p), count_body_h2(p), max_para(p)))
