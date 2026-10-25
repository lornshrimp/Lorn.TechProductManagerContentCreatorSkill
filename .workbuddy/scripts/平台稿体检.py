#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""平台稿体检（复用 规范校验.py 的口径函数，只读不改）

用途：给定日期，实测每个选题目录下 终稿/润色稿/5 平台稿 的
     正文中文字数、平台稿保真比、与终稿相似度、平台两两相似度、
     H2 小标题数、最长段落字数，输出 UTF-8 报告文件。

背景：2026-09-13 观点修订需要反复实测"终稿增字后平台稿是否跌破保真门禁"，
     本地手搓脚本效率低且口径易漂移——本脚本固化口径，防止估算。
用法：
     python 平台稿体检.py --date 2026-09-13
     （可选 --out 指定输出文件，默认 .workbuddy/_体检_{date}.txt）
"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "chk", str(BASE / ".workbuddy" / "scripts" / "规范校验.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PLATFORMS = ["知乎-", "微信-", "百家号-", "CSDN-", "头条-"]


def get_raw_body(path):
    """取原始正文（去 frontmatter、按附属区标记截断）——用于段落级统计。
    注：extract_body_text 会把换行归一化，段落统计必须用原始文本。"""
    c = path.read_text(encoding="utf-8", errors="ignore")
    # 去 frontmatter
    if c.startswith("---"):
        i = c.find("\n---", 3)
        if i != -1:
            c = c[i + 4:]
    # 按附属标记截断
    cut = len(c)
    for mk in ["\n## 素材溯源", "\n## 标题决策说明", "\n## 质量自检报告",
               "\n## 封面图", "\n## 内容简介", "\n## 互动引导", "\n## SEO",
               "\n## 配图详情", "\n# 附属内容区域", "\n## 配图搜索替换指令",
               "\n## 参考来源", "\n## 润色说明", "\n## 发布建议"]:
        p = c.find(mk)
        if p != -1:
            cut = min(cut, p)
    return c[:cut]


def count_h2(path):
    """H2 小标题个数。
    注意：extract_body_text 末尾 re.sub(r"\\s+","") 会抹掉 "## " 后的空格，
    导致 ^## 无法匹配——H2 统计必须用保留换行的原始正文。"""
    return len(re.findall(r"^## ", get_raw_body(path), re.M))


def count_paras(text):
    """返回 (段落数, 最长段落中文字符数)"""
    body = [p.strip() for p in re.split(r"\n\s*\n", text)]
    longest = 0
    n = 0
    for p in body:
        if not p or p.startswith("#") or p.startswith("|") or p.startswith(">"):
            continue
        n += 1
        longest = max(longest, len(re.findall(r"[\u4e00-\u9fff]", p)))
    return n, longest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    m = _load_checker()
    date = args.date or "2026-09-13"
    drafts = BASE / "drafts" / date
    out_path = Path(args.out) if args.out else (BASE / ".workbuddy" / f"_体检_{date}.txt")

    lines = [f"平台稿体检 · {date}", "=" * 60]

    for d in sorted(p for p in drafts.iterdir() if p.is_dir()):
        finals = sorted(d.glob("终稿-*.md"))
        if not finals:
            continue
        fpath = finals[0]
        fchars = m.count_body_chars(fpath)
        ftxt = m.extract_body_text(fpath)
        fn, flong = count_paras(get_raw_body(fpath))

        lines.append("")
        lines.append(f"■ {d.name}")
        lines.append(f"  终稿 {fpath.name}: {fchars} 字 | H2={count_h2(fpath)} | 段 {fn} 最长 {flong}")

        pol = sorted(d.glob("润色稿-*.md"))
        if pol:
            pchars = m.count_body_chars(pol[0])
            ptxt = m.extract_body_text(pol[0])
            pn, plong = count_paras(get_raw_body(pol[0]))
            sim_fp = m.text_similarity(ptxt, ftxt)
            lines.append(f"  润色稿: {pchars} 字（终稿 {fchars}）| H2={count_h2(pol[0])} | 段 {pn} 最长 {plong} | 与终稿相似 {sim_fp:.3f}")

        plats = {}
        for p in sorted(d.glob("*.md")):
            for pre in PLATFORMS:
                if p.name.startswith(pre):
                    plats[pre] = p
        for pre in PLATFORMS:
            if pre not in plats:
                lines.append(f"  {pre} 缺失")
                continue
            p = plats[pre]
            c = m.count_body_chars(p)
            t = m.extract_body_text(p)
            ratio = c / fchars if fchars else 0
            sim = m.text_similarity(t, ftxt)
            pn, plong = count_paras(get_raw_body(p))
            flags = []
            if sim >= m.COMPLIANCE_SIMILAR_TO_FINAL:
                flags.append("❌与终稿雷同")
            if ratio < 0.70:
                flags.append("❌保真不足")
            lines.append(
                f"  {pre:<7} {c:>5} 字 | 保真 {ratio:.3f} | 与终稿相似 {sim:.3f} "
                f"| H2={count_h2(p)} | 最长段 {plong} {' '.join(flags)}")
        # 平台两两
        keys = [k for k in PLATFORMS if k in plats]
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a = m.extract_body_text(plats[keys[i]])
                b = m.extract_body_text(plats[keys[j]])
                s = m.text_similarity(a, b)
                if s >= m.COMPLIANCE_SIMILAR_PLATFORMS:
                    lines.append(f"  ❌ 平台两两雷同 {keys[i]} vs {keys[j]} = {s:.3f}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.stdout.write(str(out_path) + "\n")


if __name__ == "__main__":
    main()
