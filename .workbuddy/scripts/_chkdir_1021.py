# -*- coding: utf-8 -*-
"""仅校验今日 drafts 目录（复用 规范校验.py 的全部门禁函数，秒级）"""
import io
import sys
import importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
DATE = "2026-10-21"
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

total = 0
for d in sorted((ROOT / "drafts" / DATE).iterdir()):
    if not d.is_dir():
        continue
    files = list(d.glob("*.md"))
    if not files:
        continue
    issues = []
    outline = d / "大纲.md"
    if outline.exists():
        issues += chk.check_yaml_required(outline, chk.REQUIRED_YAML_KEYS["drafts"])
        issues += chk.check_section(outline, ["段落骨架", "标题策略"], "大纲必填章节")
        issues += chk.check_notebook_refs(outline, ROOT / "notebook")
        issues += chk.check_pm_mapping(outline)

    tf = d / "标题方案.md"
    if tf.exists():
        issues += chk.check_yaml_required(tf, ["type", "date", "topic", "model"])
        issues += chk.check_section(tf, ["候选池", "评分表", "平台适配"], "标题方案必填章节")
        issues += chk.check_title_candidate_count(tf, chk.TITLE_CANDIDATE_MIN)
        issues += chk.check_platform_title_trace(tf)
        issues += chk.check_platform_title_length(tf)
        issues += chk.check_platform_title_punctuation(tf)

    for df in d.glob("草稿-*.md"):
        issues += chk.check_yaml_required(df, chk.REQUIRED_KEYS_YAML if hasattr(chk, "REQUIRED_KEYS_YAML") else chk.REQUIRED_YAML_KEYS["drafts"])
        issues += chk.check_section(df, ["素材溯源", "质量自检"], "草稿必填章节")

    if not list(d.glob("润色稿-*.md")):
        issues.append("  ❌ 缺少润色稿")
    for qf in d.glob("去AI化报告-*.md"):
        issues += chk.check_qaihua_report(qf)
    if not list(d.glob("终稿-*.md")):
        issues.append("  ❌ 缺少终稿")
    if not list(d.glob("编辑终审签报-*.md")):
        issues.append("  ❌ 缺少签报")
    if not list(d.glob("合规自检表-*.md")):
        issues.append("  ❌ 缺少合规自检表")

    genre = "深度分析体"
    if outline.exists():
        fm, _ = chk.parse_yaml_frontmatter(outline.read_text(encoding="utf-8", errors="ignore"))
        genre = (fm.get("genre") or genre).strip()
    min_words = chk.GENRE_MIN_WORDS.get(genre, 2500)
    for wf in sorted(d.glob("草稿-*.md")) + sorted(d.glob("润色稿-*.md")) + sorted(d.glob("终稿-*.md")):
        if wf.name.startswith("终稿-"):
            issues += chk.check_body_structure(wf, "终稿-")
        n = chk.count_body_chars(wf)
        if n < min_words:
            issues.append(f"  ❌ 字数不足 {wf.name} {n}<{min_words}")

    finals = list(d.glob("终稿-*.md"))
    final_chars = chk.count_body_chars(finals[0]) if finals else 0
    pf_list = [f for f in files if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)]
    for pf in sorted(pf_list):
        issues += chk.check_yaml_required(pf, chk.PLATFORM_YAML_KEYS)
        lab = next((p for p in chk.BODY_STRUCTURE_H2_MIN if pf.name.startswith(p)), "平台")
        issues += chk.check_body_structure(pf, lab)
        if finals:
            sim = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(finals[0]))
            if sim >= chk.COMPLIANCE_SIMILAR_TO_FINAL:
                issues.append(f"  ❌ 与终稿雷同 {pf.name} {sim:.0%}")
            pfx = next((p for p in chk.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
            if pfx:
                pn = chk.count_body_chars(pf)
                if pn < final_chars * chk.PLATFORM_MIN_RATIO[pfx]:
                    issues.append(f"  ❌ 保真不足 {pf.name} {pn}/{final_chars} = {pn*100//final_chars}%")
            issues += chk.check_platform_coherence(pf, finals[0])
        for pfx, rules in chk.PLATFORM_PREFIX.items():
            if pf.name.startswith(pfx):
                if pfx == "知乎-":
                    fm, _ = chk.parse_yaml_frontmatter(pf.read_text(encoding="utf-8", errors="ignore"))
                    if not fm.get("source_label"):
                        issues.append("  ❌ 知乎缺 source_label")
                    issues += chk.check_clickable_link(pf)
                else:
                    for kws, desc in rules:
                        issues += chk.check_content(pf, kws, desc)
                break
        if not pf.name.startswith("头条-"):
            for vk, (vkw, vdesc) in chk.PLATFORM_VISUAL_CHECKS.items():
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    issues.append(f"  ❌ 视觉要素缺失 {vdesc}")
        if chk.re.search(r"^#{1,3}\s*(读者互动|互动引导)\s*$", pf.read_text(encoding="utf-8", errors="ignore"), chk.re.MULTILINE):
            issues.append("  ❌ 互动引导另起小标题")
        if pf.name.startswith("头条-"):
            for vkw, vdesc in chk.TOUTIAO_VISUAL_REQUIRED:
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    issues.append(f"  ❌ 头条缺 {vdesc}")
        issues += chk.check_anchor_quality(pf)

    # 两两相似度
    texts = {f.name: chk.extract_body_text(f) for f in sorted(pf_list)}
    names = sorted(texts)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            s = chk.text_similarity(texts[names[i]], texts[names[j]])
            if s >= chk.COMPLIANCE_SIMILAR_PLATFORMS:
                issues.append(f"  ❌ 平台两两雷同 {names[i]} × {names[j]} = {s:.0%}")
    issues += chk.check_platform_title_diversity(pf_list, finals[0] if finals else None)
    issues += chk.check_figure_count_uniformity(pf_list)

    print(f"\n[{'✅' if not issues else '❌'}] {d.name}")
    for i in issues:
        print(i)
    total += len(issues)

print(f"\n今日问题合计：{total}")
