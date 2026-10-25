# -*- coding: utf-8 -*-
"""只跑 2026-10-24 当日目录的校验（秒级），复用 规范校验.py 的同名函数"""
import io, sys, re, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
P = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体"
spec = importlib.util.spec_from_file_location("chk", P + "/.workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

DATE = "2026-10-24"
root = Path(P)
total = 0

# 1 榜单
hd = root / "hotspot" / "榜单" / DATE
for f in sorted(hd.glob("*.md")):
    name = f.name
    if name == "融合榜单.md":
        issues = []
        text = f.read_text(encoding="utf-8", errors="ignore")
        fm, _ = chk.parse_yaml_frontmatter(text)
        for key in ["title", "date", "collectTime"]:
            if key not in fm or not fm[key]:
                issues.append(f"  ❌ frontmatter 缺少必填字段: {key}")
        if not re.search(r"^sources:", text, re.MULTILINE) or not re.search(r"^  - ", text, re.MULTILINE):
            issues.append("  ❌ YAML sources 列表为空")
        issues += chk.check_section(f, ["打卡表"], "19 源逐源状态")
        issues += chk.check_section(f, ["TOP 20"], "跨平台热点表")
    else:
        issues = chk.check_yaml_required(f, chk.REQUIRED_YAML_KEYS["hotspot/榜单"])
        if "知乎" in name and "想法热榜" not in name and "想法话题" not in name:
            text = f.read_text(encoding="utf-8", errors="ignore")
            if "去回答" not in text and "zhihu.com/question" not in text:
                issues.append("  ❌ 知乎类榜单必须含「链接」列")
    if issues:
        print(f"\n[榜单] {name}")
        for i in issues:
            print(i)
        total += len(issues)

# 2 选题卡
for f in sorted((root / "hotspot" / "选题").glob(f"{DATE}-选题卡.md")):
    issues = chk.check_yaml_required(f, chk.REQUIRED_YAML_KEYS["hotspot/选题"])
    issues += chk.check_section(f, ["评分总览"], "选题评分表")
    text = f.read_text(encoding="utf-8", errors="ignore")
    n_topics = len(re.findall(r"^###\s+选题[一二三四五六七八九十百]", text, re.MULTILINE))
    n_dedup = text.count("历史去重检测")
    if n_topics and n_dedup < n_topics:
        issues.append(f"  ❌ 选题详析须逐题标注「历史去重检测」（{n_topics} vs {n_dedup}）")
    issues += chk.check_notebook_refs(f, root / "notebook")
    if issues:
        print(f"\n[选题卡] {f.name}")
        for i in issues:
            print(i)
        total += len(issues)

# 3 今日研究报告
res = root / "research"
for d in sorted(res.iterdir()):
    if not d.is_dir():
        continue
    for f in sorted(d.glob("研究报告.md")):
        fm, _ = chk.parse_yaml_frontmatter(f.read_text(encoding="utf-8", errors="ignore"))
        if (fm.get("date") or "").strip() != DATE:
            continue
        issues = chk.check_yaml_required(f, chk.REQUIRED_YAML_KEYS["research"])
        issues += chk.check_pm_board(f, DATE)
        if issues:
            print(f"\n[研究报告] {d.name}")
            for i in issues:
                print(i)
            total += len(issues)

# 4 今日选题目录
td = root / "drafts" / DATE
for d in sorted([c for c in td.iterdir() if c.is_dir()]):
    files = list(d.glob("*.md"))
    if not files:
        continue
    dir_issues = []
    outline = d / "大纲.md"
    if outline.exists():
        issues = chk.check_yaml_required(outline, chk.REQUIRED_YAML_KEYS["drafts"])
        issues += chk.check_section(outline, ["段落骨架", "标题策略"], "大纲必填章节")
        issues += chk.check_notebook_refs(outline, root / "notebook")
        issues += chk.check_pm_mapping(outline)
        dir_issues += issues

    title_f = d / "标题方案.md"
    if title_f.exists():
        issues = chk.check_yaml_required(title_f, ["type", "date", "topic", "model"])
        issues += chk.check_section(title_f, ["候选池", "评分表", "平台适配"], "标题方案必填章节")
        _tfm, _ = chk.parse_yaml_frontmatter(title_f.read_text(encoding="utf-8", errors="ignore"))
        _tdate = (_tfm.get("date") or "").strip()
        if _tdate >= chk.TITLE_V22_EFFECTIVE_DATE:
            title_genre = "深度分析体"
            if outline.exists():
                _ofm, _ = chk.parse_yaml_frontmatter(outline.read_text(encoding="utf-8", errors="ignore"))
                title_genre = (_ofm.get("genre") or "深度分析体").strip() or "深度分析体"
            tmin = chk.TITLE_CANDIDATE_MIN_BREAKING_NEWS if title_genre == "快讯评点体" else chk.TITLE_CANDIDATE_MIN
            issues += chk.check_title_candidate_count(title_f, tmin)
            issues += chk.check_platform_title_trace(title_f)
            issues += chk.check_platform_title_length(title_f)
            issues += chk.check_platform_title_punctuation(title_f)
        dir_issues += issues

    for df in d.glob("草稿-*.md"):
        dir_issues += chk.check_yaml_required(df, chk.REQUIRED_YAML_KEYS["drafts"])
        dir_issues += chk.check_section(df, ["素材溯源", "质量自检"], "草稿必填章节")

    polish_files = list(d.glob("润色稿-*.md"))
    if not polish_files:
        dir_issues.append("  ❌ 缺少「润色稿-*.md」")
    for qf in d.glob("去AI化报告-*.md"):
        dir_issues += chk.check_qaihua_report(qf)
    if not list(d.glob("去AI化报告-*.md")):
        dir_issues.append("  ❌ 缺少「去AI化报告-*.md」")
    if not list(d.glob("终稿-*.md")):
        dir_issues.append("  ❌ 缺少「终稿-*.md」")
    if not list(d.glob("编辑终审签报-*.md")):
        dir_issues.append("  ❌ 缺少「编辑终审签报-*.md」")
    if list(d.glob("终稿-*.md")) and not list(d.glob("合规自检表-*.md")) and not list(d.glob("合规自检表.md")):
        dir_issues.append("  ❌ 缺少「合规自检表」")

    genre = "深度分析体"
    if outline.exists():
        _ofm, _ = chk.parse_yaml_frontmatter(outline.read_text(encoding="utf-8", errors="ignore"))
        genre = (_ofm.get("genre") or "深度分析体").strip() or "深度分析体"
    min_words = chk.GENRE_MIN_WORDS.get(genre, 2500)
    for wf in sorted(d.glob("草稿-*.md")) + sorted(d.glob("润色稿-*.md")) + sorted(d.glob("终稿-*.md")):
        if wf.name.startswith("终稿-"):
            dir_issues += chk.check_body_structure(wf, "终稿-")
        n = chk.count_body_chars(wf)
        if n < min_words:
            dir_issues.append(f"  ❌ 正文字数不足: {wf.name} 实测 {n} < {min_words}")

    platform_files = [f for f in files if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)]
    final_refs = list(d.glob("终稿-*.md"))
    final_chars = chk.count_body_chars(final_refs[0]) if final_refs else 0

    for pf in sorted(platform_files):
        issues = chk.check_yaml_required(pf, chk.PLATFORM_YAML_KEYS)
        pfx_label = next((p for p in chk.BODY_STRUCTURE_H2_MIN if pf.name.startswith(p)), "平台")
        issues += chk.check_body_structure(pf, pfx_label)
        if final_refs:
            sim = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(final_refs[0]))
            if sim >= chk.COMPLIANCE_SIMILAR_TO_FINAL:
                issues.append(f"  ❌ 与终稿高度雷同 {sim:.0%}: {pf.name}")
            pf_pfx = next((p for p in chk.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
            if pf_pfx:
                pn = chk.count_body_chars(pf)
                if pn < final_chars * chk.PLATFORM_MIN_RATIO[pf_pfx]:
                    issues.append(f"  ❌ 平台稿缩水: {pf.name} {pn} 字 = 终稿 {final_chars} 的 {pn*100//final_chars}%")
            issues += chk.check_platform_coherence(pf, final_refs[0])
        for pfx, rules in chk.PLATFORM_PREFIX.items():
            if pf.name.startswith(pfx):
                if pfx == "知乎-":
                    pfm, _ = chk.parse_yaml_frontmatter(pf.read_text(encoding="utf-8", errors="ignore"))
                    if not pfm.get("source_label"):
                        issues.append("  ❌ frontmatter 缺少 source_label")
                    issues += chk.check_clickable_link(pf)
                else:
                    for keywords, rdesc in rules:
                        issues += chk.check_content(pf, keywords, rdesc)
                break
        if not pf.name.startswith("头条-"):
            for vk, (vkw, vdesc) in chk.PLATFORM_VISUAL_CHECKS.items():
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    issues.append(f"  ❌ 平台视觉要素缺失: {vdesc}")
        if pf.name.startswith("头条-"):
            for vkw, vdesc in chk.TOUTIAO_VISUAL_REQUIRED:
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    issues.append(f"  ❌ 头条版视觉要素缺失: {vdesc}")
            fk, fdesc = chk.PLATFORM_VISUAL_CHECKS["figures"]
            if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in fk):
                issues.append(f"  ❌ 头条版视觉要素缺失: {fdesc}")
        if re.search(r"^#{1,3}\s*(读者互动|互动引导)\s*$", pf.read_text(encoding="utf-8", errors="ignore"), re.MULTILINE):
            issues.append("  ❌ 互动引导另起小标题")
        issues += chk.check_anchor_quality(pf)
        dir_issues += issues

    plat_texts = {pf.name: chk.extract_body_text(pf) for pf in sorted(platform_files)}
    names = sorted(plat_texts)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            s = chk.text_similarity(plat_texts[names[i]], plat_texts[names[j]])
            if s >= chk.COMPLIANCE_SIMILAR_PLATFORMS:
                dir_issues.append(f"  ❌ 平台版雷同 {s:.0%}: {names[i]} vs {names[j]}")
    dir_issues += chk.check_platform_title_diversity(platform_files, final_refs[0] if final_refs else None)
    dir_issues += chk.check_figure_count_uniformity(platform_files)

    if dir_issues:
        print(f"\n[选题目录] drafts/{DATE}/{d.name}")
        for i in dir_issues:
            print(i)
        total += len(dir_issues)

print("\n" + "=" * 60)
print(f"今日({DATE})问题数 = {total}")
