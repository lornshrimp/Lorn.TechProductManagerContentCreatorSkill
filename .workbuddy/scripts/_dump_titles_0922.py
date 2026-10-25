# -*- coding: utf-8 -*-
"""导出三选题各平台稿的 frontmatter title 与 H1，用于与标题方案表比对同步"""
import re
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
drafts = ROOT / "drafts/2026-09-22"
PLATS = ["知乎", "微信", "百家号", "CSDN", "头条"]

out = []
for d in sorted(drafts.iterdir()):
    if not d.is_dir():
        continue
    out.append(f"########## {d.name} ##########")
    for pf in sorted(d.glob("*.md")):
        stem = pf.name.split("-")[0]
        if stem not in PLATS:
            continue
        text = pf.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        title = ""
        src_label = ""
        src_url = ""
        if m:
            fm = m.group(1)
            mt = re.search(r"^title:\s*(.*)$", fm, re.MULTILINE)
            if mt:
                title = mt.group(1).strip()
            ms = re.search(r"^source_label:\s*(.*)$", fm, re.MULTILINE)
            if ms:
                src_label = ms.group(1).strip()
            mu = re.search(r"^source_url:\s*(.*)$", fm, re.MULTILINE)
            if mu:
                src_url = mu.group(1).strip()
        h1 = ""
        mh = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
        if mh:
            h1 = mh.group(1).strip()
        out.append(f"--- {pf.name}")
        out.append(f"    frontmatter title: {title}")
        out.append(f"    H1: {h1}")
        if src_label or src_url:
            out.append(f"    source_label: {src_label} | source_url: {src_url}")

txt = "\n".join(out)
(ROOT / ".workbuddy/_titles_0922.txt").write_text(txt, encoding="utf-8")
print("done")
