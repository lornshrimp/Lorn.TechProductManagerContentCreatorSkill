# -*- coding: utf-8 -*-
"""对 2026-10-14 三题的 大纲/标题方案 跑校验脚本函数"""
import sys, io, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

TOPICS = [
    "老干妈用AI一年54亿-拣椒工从600人减至48人",
    "茶百道涉嫌操纵IPO被香港证监会停牌",
    "北京社保缴费基数下限7270元vs法定最低工资2540元",
]
nb = ROOT / "notebook"
for t in TOPICS:
    d = ROOT / "drafts/2026-10-14" / t
    print("=" * 60)
    print("TOPIC:", t)
    ol = d / "大纲.md"
    if ol.exists():
        iss = chk.check_yaml_required(ol, chk.REQUIRED_YAML_KEYS["drafts"])
        iss += chk.check_section(ol, ["段落骨架", "标题策略"], "大纲必填章节")
        iss += chk.check_notebook_refs(ol, nb)
        print("[大纲]", "OK" if not iss else "")
        for i in iss:
            print(i)
    tf = d / "标题方案.md"
    if tf.exists():
        iss = chk.check_yaml_required(tf, ["type", "date", "topic", "model"])
        iss += chk.check_section(tf, ["候选池", "评分表", "平台适配"], "标题方案必填章节")
        iss += chk.check_title_candidate_count(tf, 12)
        iss += chk.check_platform_title_trace(tf)
        iss += chk.check_platform_title_length(tf)
        iss += chk.check_platform_title_punctuation(tf)
        print("[标题方案]", "OK" if not iss else "")
        for i in iss:
            print(i)
        print("候选池数量:", len(chk.extract_title_candidates(tf)))
