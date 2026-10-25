# -*- coding: utf-8 -*-
"""校验某选题目录下全部平台稿（字数保真/H2/锚文本/连贯性/相似度矩阵/视觉要素/平台关键词/标题）"""
import sys, io, importlib.util, itertools, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def check_topic(topic, final_name):
    d = ROOT / "drafts/2026-10-14" / topic
    fin = d / final_name
    t = chk.count_body_chars(fin)
    print("=" * 70)
    print("TOPIC:", topic, "| 终稿字数:", t)
    pfs = sorted([f for f in d.glob("*.md") if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)])
    for pf in pfs:
        n = chk.count_body_chars(pf)
        label = next((p for p in chk.BODY_STRUCTURE_H2_MIN if pf.name.startswith(p)), "平台")
        pfx = next((p for p in chk.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
        ratio = chk.PLATFORM_MIN_RATIO.get(pfx, 0)
        sim = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(fin))
        iss = []
        iss += chk.check_yaml_required(pf, chk.PLATFORM_YAML_KEYS)
        iss += chk.check_body_structure(pf, label)
        if n < t * ratio:
            iss.append(f"  ❌ 保真不足 {n} < {int(t*ratio)} ({n*100//t}%)")
        if sim >= 0.99:
            iss.append(f"  ❌ 与终稿雷同 {sim:.2%}")
        iss += chk.check_platform_coherence(pf, fin)
        for vk, (vkw, vdesc) in chk.PLATFORM_VISUAL_CHECKS.items():
            if not pf.name.startswith("头条-"):
                if not any(k in pf.read_text(encoding="utf-8") for k in vkw):
                    iss.append(f"  ❌ 视觉缺失 {vdesc}")
        if pf.name.startswith("头条-"):
            for vkw, vdesc in chk.TOUTIAO_VISUAL_REQUIRED:
                if not any(k in pf.read_text(encoding="utf-8") for k in vkw):
                    iss.append(f"  ❌ 头条视觉缺失 {vdesc}")
        for pfx2, rules in chk.PLATFORM_PREFIX.items():
            if pf.name.startswith(pfx2):
                if pfx2 == "知乎-":
                    fm, _ = chk.parse_yaml_frontmatter(pf.read_text(encoding="utf-8"))
                    if not fm.get("source_label"):
                        iss.append("  ❌ 缺 source_label")
                    iss += chk.check_clickable_link(pf)
                else:
                    for keywords, rdesc in rules:
                        iss += chk.check_content(pf, keywords, rdesc)
                break
        if re.search(r"^#{1,3}\s*(读者互动|互动引导)\s*$", pf.read_text(encoding="utf-8"), re.MULTILINE):
            iss.append("  ❌ 互动引导另起小标题")
        iss += chk.check_anchor_quality(pf)
        status = "OK" if not iss else "ISSUES"
        print(f"[{pf.name[:26]:<26}] {n:>5}字 {n*100//t:>3}% sim{sim:.2f} {status}")
        for i in iss:
            print(i)
    # 两两
    names = [p.name for p in pfs]
    for a, b in itertools.combinations(names, 2):
        s = chk.text_similarity(chk.extract_body_text(d / a), chk.extract_body_text(d / b))
        if s >= 0.85:
            print(f"  ❌ 平台两两雷同 {a} vs {b}: {s:.2%}")
    print("  [配图同质化]", chk.check_figure_count_uniformity(pfs) or "OK")
    print("  [平台标题]", chk.check_platform_title_diversity(pfs, fin) or "OK")


check_topic("老干妈用AI一年54亿-拣椒工从600人减至48人",
            "终稿-54亿的营收-552个消失的岗位-老干妈这笔账怎么记.md")
check_topic("茶百道涉嫌操纵IPO被香港证监会停牌",
            "终稿-一只股票的需求可以是写出来的-茶百道停牌这件事.md")
check_topic("北京社保缴费基数下限7270元vs法定最低工资2540元",
            "终稿-两把尺子量同一个人-2540元的最低工资与7270元的社保基数.md")
