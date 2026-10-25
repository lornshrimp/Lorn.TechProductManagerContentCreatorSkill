# -*- coding: utf-8 -*-
"""核验三选题去AI化报告关键数字（字数变动/差异率/stop-slop）与终稿实测值是否一致"""
import re, importlib.util, difflib
from pathlib import Path

root = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("guifan", root / ".workbuddy" / "scripts" / "规范校验.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

TOPICS = [
    ("A", "前8个月税收增5.9%-纳税集中度的分配读数", "纳税集中度的分配读数"),
    ("B", "中办国办分类推进高校改革-教育供给的错配账", "教育供给的错配账"),
    ("C", "反外国制裁法新案例安世21.39亿财产被查封-资产保全的定价权", "资产保全的定价权"),
]
out = []
for tag, dn, stem in TOPICS:
    d = root / "drafts" / "2026-09-22" / dn
    draft = d / f"草稿-{stem}.md"
    polish = d / f"润色稿-{stem}.md"
    final = d / f"终稿-{stem}.md"
    rep = d / f"去AI化报告-{stem}.md"
    dc = mod.count_body_chars(draft)
    pc = mod.count_body_chars(polish)
    fc = mod.count_body_chars(final)
    a = re.sub(r"\s+", "", mod.extract_body_text(draft))
    b = re.sub(r"\s+", "", mod.extract_body_text(polish))
    sim = difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()
    dtxt = rep.read_text(encoding="utf-8", errors="ignore")
    nums = re.findall(r"(\d+\.\d+)%", dtxt)
    out.append(f"## {tag} {stem}")
    out.append(f"  草稿实测={dc} 润色实测={pc} 终稿实测={fc} 差异率实测={(1-sim)*100:.2f}%")
    out.append(f"  报告中出现的百分数: {nums[:12]}")
    # 报告是否含 stop-slop 五维 25/25
    out.append(f"  含 '25/25': {'25/25' in dtxt} | 含 '8 节' 或章节数: {len(re.findall(r'^## ', dtxt, re.M))}")
    out.append("")

(root / ".workbuddy/_report_audit_0922.txt").write_text("\n".join(out), encoding="utf-8")
print("OK")
