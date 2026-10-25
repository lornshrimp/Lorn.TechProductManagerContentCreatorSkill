# -*- coding: utf-8 -*-
"""对单个选题目录跑 规范校验.py 的全部目录级门禁，快速闭环。
用法: python _m19_audit.py --date 2026-09-19 --topic "住建部房地产进入存量时代-现房销售改的是哪本账"
"""
import argparse, re, sys
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v", str(HERE / "规范校验.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

ROOT = HERE.parent.parent


def audit(date: str, topic: str):
    d = ROOT / "drafts" / date / topic
    if not d.exists():
        print(f"NOT_FOUND: {d}")
        return 1
    issues = []
    files = list(d.glob("*.md"))

    outline = d / "大纲.md"
    if outline.exists():
        issues += v.check_yaml_required(outline, v.REQUIRED_YAML_KEYS["drafts"])
        issues += v.check_section(outline, ["段落骨架", "标题策略"], "大纲必填章节")

    title_f = d / "标题方案.md"
    if title_f.exists():
        issues += v.check_yaml_required(title_f, ["type", "date", "topic", "model"])
        issues += v.check_section(title_f, ["候选池", "评分表", "平台适配"], "标题方案必填章节")
        _tfm, _ = v.parse_yaml_frontmatter(title_f.read_text(encoding="utf-8", errors="ignore"))
        _tdate = (_tfm.get("date") or "").strip()
        if _tdate and _tdate >= v.TITLE_V22_EFFECTIVE_DATE:
            title_genre = "深度分析体"
            if outline.exists():
                _ofm, _ = v.parse_yaml_frontmatter(outline.read_text(encoding="utf-8", errors="ignore"))
                title_genre = (_ofm.get("genre") or "深度分析体").strip() or "深度分析体"
            tmin = v.TITLE_CANDIDATE_MIN_BREAKING_NEWS if title_genre == "快讯评点体" else v.TITLE_CANDIDATE_MIN
            issues += v.check_title_candidate_count(title_f, tmin)
            issues += v.check_platform_title_trace(title_f)
            issues += v.check_platform_title_length(title_f)
            if _tdate >= v.TITLE_PUNCT_EFFECTIVE_DATE:
                issues += v.check_platform_title_punctuation(title_f)

    for df in list(d.glob("草稿-*.md")):
        issues += v.check_yaml_required(df, v.REQUIRED_yaml_KEYS["drafts"]) if hasattr(v, "REQUIRED_yaml_KEYS") else []
        issues += v.check_yaml_required(df, v.REQUIRED_YAML_KEYS["drafts"])
        issues += v.check_section(df, ["素材溯源", "质量自检"], "草稿必填章节")

    polish_files = list(d.glob("润色稿-*.md"))
    if not polish_files:
        issues.append("  ❌ 缺少「润色稿-*.md」")
    qaihua_files = list(d.glob("去AI化报告-*.md"))
    if not qaihua_files:
        issues.append("  ❌ 缺少「去AI化报告-*.md」")
    else:
        for qf in qaihua_files:
            _qtfm, _ = v.parse_yaml_frontmatter(qf.read_text(encoding="utf-8", errors="ignore"))
            _qdate = (_qtfm.get("date") or "").strip()
            if _qdate and _qdate >= v.QAIHUA_REPORT_EFFECTIVE:
                issues += v.check_qaihua_report(qf)

    if not list(d.glob("终稿-*.md")):
        issues.append("  ❌ 缺少「终稿-*.md」")
    if not list(d.glob("编辑终审签报-*.md")):
        issues.append("  ❌ 缺少「编辑终审签报-*.md」")
    if list(d.glob("终稿-*.md")) and not list(d.glob(f"{v.COMPLIANCE_CHECKFILE}-*.md")) \
            and not list(d.glob(f"{v.COMPLIANCE_CHECKFILE}.md")):
        issues.append("  ❌ 缺少「合规自检表」")

    genre = "深度分析体"
    if outline.exists():
        ofm, _ = v.parse_yaml_frontmatter(outline.read_text(encoding="utf-8", errors="ignore"))
        genre = (ofm.get("genre") or "深度分析体").strip() or "深度分析体"
    min_words = v.GENRE_MIN_WORDS.get(genre, 2500)
    for wf in (sorted(d.glob("草稿-*.md")) + sorted(d.glob("润色稿-*.md")) + sorted(d.glob("终稿-*.md"))):
        if wf.name.startswith("终稿-") and d.parent.name >= "2026-08-27":
            issues += v.check_body_structure(wf, "终稿-")
        n = v.count_body_chars(wf)
        if n < min_words:
            issues.append(f"  ❌ 正文字数不足: {wf.name} 实测 {n} < {min_words}")

    platform_files = [f for f in files if any(f.name.startswith(p) for p in v.PLATFORM_PREFIX)]
    final_refs = list(d.glob("终稿-*.md"))
    final_chars = v.count_body_chars(final_refs[0]) if final_refs else 0

    for pf in sorted(platform_files):
        pi = v.check_yaml_required(pf, v.PLATFORM_YAML_KEYS)
        if d.parent.name >= "2026-08-27":
            lbl = next((p for p in v.BODY_STRUCTURE_H2_MIN if pf.name.startswith(p)), "平台")
            pi += v.check_body_structure(pf, lbl)
        if final_refs:
            sim = v.text_similarity(v.extract_body_text(pf), v.extract_body_text(final_refs[0]))
            if sim >= v.COMPLIANCE_SIMILAR_TO_FINAL:
                pi.append(f"  ❌ 平台稿与终稿雷同 {sim:.0%}: {pf.name}")
        if final_chars > 0:
            pfx = next((p for p in v.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
            if pfx:
                pn = v.count_body_chars(pf)
                if pn < final_chars * v.PLATFORM_MIN_RATIO[pfx]:
                    pi.append(f"  ❌ 平台稿内容缩水: {pf.name} {pn} 字 ({pn*100//final_chars}%) "
                              f"< {int(v.PLATFORM_MIN_RATIO[pfx]*100)}%")
        if final_refs:
            pi += v.check_platform_coherence(pf, final_refs[0])
        for pfx, rules in v.PLATFORM_PREFIX.items():
            if pf.name.startswith(pfx):
                if pfx == "知乎-":
                    fm, _ = v.parse_yaml_frontmatter(pf.read_text(encoding="utf-8", errors="ignore"))
                    if not fm.get("source_label"):
                        pi.append("  ❌ 缺少 source_label")
                    pi += v.check_clickable_link(pf)
                else:
                    for keywords, rdesc in rules:
                        pi += v.check_content(pf, keywords, rdesc)
                break
        if not pf.name.startswith("头条-"):
            txt = pf.read_text(encoding="utf-8", errors="ignore")
            for vk, (vkw, vdesc) in v.PLATFORM_VISUAL_CHECKS.items():
                if not any(k in txt for k in vkw):
                    pi.append(f"  ❌ 视觉要素缺失: {vdesc}")
        if re.search(r"^#{1,3}\s*(读者互动|互动引导)\s*$",
                     pf.read_text(encoding="utf-8", errors="ignore"), re.MULTILINE):
            pi.append("  ❌ 互动引导另起小标题")
        if pf.name.startswith("头条-"):
            txt = pf.read_text(encoding="utf-8", errors="ignore")
            for vkw, vdesc in v.TOUTIAO_VISUAL_REQUIRED:
                if not any(k in txt for k in vkw):
                    pi.append(f"  ❌ 头条视觉要素缺失: {vdesc}")
            fk, fdesc = v.PLATFORM_VISUAL_CHECKS["figures"]
            if not any(k in txt for k in fk):
                pi.append(f"  ❌ 头条视觉要素缺失: {fdesc}")
        pi += v.check_anchor_quality(pf)
        issues += pi

    plat_texts = {pf.name: v.extract_body_text(pf) for pf in sorted(platform_files)}
    names = sorted(plat_texts)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            sim = v.text_similarity(plat_texts[names[i]], plat_texts[names[j]])
            if sim >= v.COMPLIANCE_SIMILAR_PLATFORMS:
                issues.append(f"  ❌ 平台版雷同 {sim:.0%}: {names[i]} vs {names[j]}")

    issues += v.check_platform_title_diversity(platform_files, final_refs[0] if final_refs else None)
    issues += v.check_figure_count_uniformity(platform_files)

    print(f"=== {topic} ===")
    if issues:
        print("\n".join(issues))
        print(f"ISSUES={len(issues)}  ERR={sum(1 for i in issues if '❌' in i)}  WARN={sum(1 for i in issues if '⚠' in i)}")
        return 1
    print("ALL_PASS")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--topic", required=True)
    a = ap.parse_args()
    sys.exit(audit(a.date, a.topic))
