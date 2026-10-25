#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""对三份标题方案直接调用 规范校验.py 的标题函数，验证候选池数量/溯源/字数/标点"""
import sys, io, importlib.util
from pathlib import Path

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

buf = []
base = ROOT / "drafts/2026-09-26"
for sub in ["全国牛肉批发均价涨至一公斤71元-创两年新高",
            "Anthropic推演2030美国经济-钱继续流向有钱人",
            "央视曝光挂靠参保骗社保-灰色产业链如何运作"]:
    p = base / sub / "标题方案.md"
    buf.append("=" * 70)
    buf.append(f"【{sub}】")
    if not p.exists():
        buf.append("  ❌ 文件不存在")
        continue
    cands = chk.extract_title_candidates(p)
    buf.append(f"  候选池提取数：{len(cands)}（底线 {chk.TITLE_CANDIDATE_MIN}）")
    for i, c in enumerate(cands, 1):
        buf.append(f"    {i:2d}. {c}")
    buf.append(f"  章节检查：{chk.check_section(p, list(chk.TITLE_CHECKS.keys()), '标题方案')}")
    buf.append(f"  数量门禁：{chk.check_title_candidate_count(p, chk.TITLE_CANDIDATE_MIN)}")
    buf.append(f"  溯源门禁：{chk.check_platform_title_trace(p)}")
    buf.append(f"  字数门禁：{chk.check_platform_title_length(p)}")
    buf.append(f"  标点门禁：{chk.check_platform_title_punctuation(p)}")

Path(ROOT / ".workbuddy/scripts/_title_check_out.txt").write_text("\n".join(buf), encoding="utf-8")
print("done")
