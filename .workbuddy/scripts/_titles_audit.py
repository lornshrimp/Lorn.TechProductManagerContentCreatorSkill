# -*- coding: utf-8 -*-
"""平台标题体检：扫描指定日期区间的平台稿 frontmatter title，
量化「无标点长串 / 疑问词无问号 / 字数区间」三类问题。

用法：python _titles_audit.py 2026-09-15 2026-09-17
输出：.workbuddy/_标题体检_{起}_{止}.txt
"""
import re
import sys
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent.parent
PLATFORMS = ["知乎", "微信", "百家号", "CSDN", "头条"]
# 允许出现的标点（中文标题常用）
PUNCT = set("，。、：；？！——“”‘’…《》()（）")
QUESTION_WORDS = ["什么", "谁", "为什么", "怎么", "哪", "如何", "多少", "是不是", "吗"]
SKIP_MARK = ["素材溯源", "质量自检", "视觉与配图", "配图搜索替换", "SEO 关键词", "平台适配"]


def count_chars(s: str) -> int:
    """与规范校验脚本同口径：汉字+字母+数字"""
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", s))


def main():
    start, end = sys.argv[1], sys.argv[2]
    drafts = BASE / "drafts"
    out_lines = []
    rows = []

    dates = sorted([d.name for d in drafts.iterdir()
                    if d.is_dir() and start <= d.name <= end])
    for date in dates:
        ddir = drafts / date
        for topic in sorted([t for t in ddir.iterdir() if t.is_dir()]):
            for f in sorted(topic.glob("*.md")):
                name = f.stem
                plat = next((p for p in PLATFORMS if name.startswith(p)), None)
                if not plat:
                    continue
                text = f.read_text(encoding="utf-8", errors="replace")
                m = re.search(r"^title:\s*(.+)$", text, re.M)
                title = m.group(1).strip().strip('"').strip("'") if m else ""
                if not title:
                    continue
                n = count_chars(title)
                has_punct = any(c in PUNCT for c in title)
                qw = [w for w in QUESTION_WORDS if w in title]
                flag_punct = (n >= 12) and (not has_punct)
                flag_q = bool(qw) and ("？" not in title) and ("?" not in title)
                rows.append((date, topic.name[:18], plat, n, title,
                             has_punct, flag_punct, flag_q, ",".join(qw)))

    # 按日期分组输出
    cur = None
    for (date, topic, plat, n, title, hp, fp, fq, qw) in rows:
        if date != cur:
            out_lines.append(f"\n===== {date} =====")
            cur = date
        marks = []
        if fp:
            marks.append("❌无标点长串")
        if fq:
            marks.append(f"❌疑问词({qw})无问号")
        if not hp:
            marks.append("·无标点")
        out_lines.append(f"[{plat:4}] {n:>2}字 {title}   {' '.join(marks)}   «{topic}»")

    # 汇总
    tot = len(rows)
    bad_p = sum(1 for r in rows if r[6])
    bad_q = sum(1 for r in rows if r[7])
    nopunct = sum(1 for r in rows if not r[5])
    out_lines.append("\n\n===== 汇总 =====")
    out_lines.append(f"平台稿标题总数：{tot}")
    out_lines.append(f"❌ 无标点长串（≥12字且零标点）：{bad_p}  ({bad_p/tot*100:.1f}%)" if tot else "")
    out_lines.append(f"❌ 疑问词无问号：{bad_q}  ({bad_q/tot*100:.1f}%)" if tot else "")
    out_lines.append(f"·零标点标题总数：{nopunct}  ({nopunct/tot*100:.1f}%)" if tot else "")

    out = BASE / ".workbuddy" / f"_标题体检_{start}_{end}.txt"
    out.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"OUT={out.name} | total={tot} | bad_punct={bad_p} | bad_question={bad_q} | no_punct={nopunct}")


if __name__ == "__main__":
    main()
