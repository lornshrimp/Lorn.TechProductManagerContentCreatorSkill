# -*- coding: utf-8 -*-
"""字数实测：统计草稿/润色稿/终稿正文的中文字符数。
口径：剥离 YAML frontmatter；从正文起点截到附属章节（素材溯源/标题决策说明/质量自检报告/配图/视觉与配图 等）之前。
用法：python count_body_chars.py <文件路径> [起始标记] [结束标记]
不带标记时自动识别：以第一个 "## " 标题之前的正文为起点（即跳过 frontmatter 与 H1 后的正文开始），
结束标记取第一个附属章节 H2。
"""
import re
import sys
from io import StringIO
from pathlib import Path

AUX_HEADS = [
    "## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 配图搜索替换指令",
    "## 视觉与配图", "## 配图详情", "## 封面图", "## 内容简介", "## SEO",
    "## 附属内容", "## 数据跟踪",
]
# 平台稿：正文在"## SEO 关键词"或"## 配图搜索替换指令"前截断
AUX_HEADS_PLATFORM = AUX_HEADS + ["## 视觉与配图"]


def count_chars(text: str, start_marker: str = None, end_marker: str = None,
                platform: bool = False) -> int:
    # 去 frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    # 去掉 H1 标题行（不算正文？规范未明确，通常 H1 计入很少；这里保留但不含）
    if start_marker:
        idx = text.find(start_marker)
        if idx >= 0:
            text = text[idx:]
    else:
        # 从第一个非标题正文自然段开始：跳过 H1
        m = re.search(r"^##\s+", text, re.MULTILINE)
        # 正文起点：H1 之后的第一个非空非标题行
        lines = text.split("\n")
        buf = []
        started = False
        for ln in lines:
            if not started:
                if ln.strip() and not ln.startswith("#") and not ln.startswith("|") and ln.strip() != "---":
                    started = True
                else:
                    continue
            buf.append(ln)
        text = "\n".join(buf)
    if end_marker:
        idx = text.find(end_marker)
        if idx >= 0:
            text = text[:idx]
    else:
        heads = AUX_HEADS_PLATFORM if platform else AUX_HEADS
        best = len(text)
        for h in heads:
            i = text.find("\n" + h)
            if 0 <= i < best:
                best = i
        text = text[:best]
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def main():
    out = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.exists():
            out.append(f"NOT_FOUND\t{arg}")
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        platform = any(p.name.startswith(x) for x in
                       ("知乎-", "微信-", "百家号-", "CSDN-", "头条-"))
        n = count_chars(text, platform=platform)
        out.append(f"{n}\t{p.name}")
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
