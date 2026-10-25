# -*- coding: utf-8 -*-
"""2026-10-15 单日目录校验（复用 规范校验.py 全部函数，秒级）"""
import sys, io, re, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
DATE = "2026-10-15"
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

report = []
total = 0

# ---- 榜单 ----
hd = ROOT / "hotspot" / "榜单" / DATE
if hd.exists():
    for f in sorted(hd.glob("*.md")):
        issues = []
        text = f.read_text(encoding="utf-8", errors="ignore")
        if f.name == "融合榜单.md":
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
            if "知乎" in f.name and "想法热榜" not in f.name and "想法话题" not in f.name:
                if "去回答" not in text and "zhihu.com/question" not in text:
                    issues.append("  ❌ 知乎类榜单必须含「链接」列")
        if issues:
            report.append(f"\n[榜单] {f.name}")
            report += issues
            total += len(issues)

# ---- 选题卡 ----
for f in sorted((ROOT / "hotspot" / "选题").glob(f"{DATE}-选题卡.md")):
    issues = chk.check_yaml_required(f, chk.REQUIRED_YAML_KEYS["hotspot/选题"])
    issues += chk.check_section(f, ["评分总览"], "选题评分表")
    text = f.read_text(encoding="utf-8", errors="ignore")
    n_topics = len(re.findall(r"^###\s+选题[一二三四五六七八九十百]", text, re.MULTILINE))
    n_dedup = text.count("历史去重检测")
    if n_topics and n_dedup < n_topics:
        issues.append(f"  ❌ 选题详析须逐题标注「历史去重检测」（{n_topics} vs {n_dedup}）")
    issues += chk.check_notebook_refs(f, ROOT / "notebook")
    if issues:
        report.append(f"\n[选题卡] {f.name}")
        report += issues
        total += len(issues)

# ---- 研究报告 ----
for d in sorted((ROOT / "research").iterdir()):
    if not d.is_dir():
        continue
    for f in sorted(d.glob("研究报告.md")):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        if DATE not in txt[:600]:
            continue
        issues = chk.check_yaml_required(f, chk.REQUIRED_YAML_KEYS["research"])
        if issues:
            report.append(f"\n[研究报告] {d.name}/研究报告.md")
            report += issues
            total += len(issues)

# ---- drafts ----
base = ROOT / "drafts" / DATE
for d in sorted(base.iterdir()):
    if not d.is_dir():
        continue
    files = list(d.glob("*.md"))
    if not files:
        continue
    di = []
    outline = d / "大纲.md"
    if outline.exists():
        di += chk.check_yaml_required(outline, chk.REQUIRED_YAML_KEYS["drafts"])
        di += chk.check_section(outline, ["段落骨架", "标题策略"], "大纲必填章节")
        di += chk.check_notebook_refs(outline, ROOT / "notebook")
    else:
        di.append("  ❌ 缺少 大纲.md")
    tf = d / "标题方案.md"
    if tf.exists():
        di += chk.check_yaml_required(tf, ["type", "date", "topic", "model"])
        di += chk.check_section(tf, ["候选池", "评分表", "平台适配"], "标题方案必填章节")
        _tfm, _ = chk.parse_yaml_frontmatter(tf.read_text(encoding="utf-8", errors="ignore"))
        _tdate = (_tfm.get("date") or "").strip()
        if _tdate and _tdate >= chk.TITLE_V22_EFFECTIVE_DATE:
            genre = "深度分析体"
            if outline.exists():
                _ofm, _ = chk.parse_yaml_frontmatter(outline.read_text(encoding="utf-8", errors="ignore"))
                genre = (_ofm.get("genre") or "深度分析体").strip() or "深度分析体"
            tmin = chk.TITLE_CANDIDATE_MIN_BREAKING_NEWS if genre == "快讯评点体" else chk.TITLE_CANDIDATE_MIN
            di += chk.check_title_candidate_count(tf, tmin)
            di += chk.check_platform_title_trace(tf)
            di += chk.check_platform_title_length(tf)
            di += chk.check_platform_title_punctuation(tf)
    else:
        di.append("  ❌ 缺少 标题方案.md")
    for df in sorted(d.glob("草稿-*.md")):
        di += chk.check_yaml_required(df, chk.REQUIRED_YAML_KEYS["drafts"])
        di += chk.check_section(df, ["素材溯源", "质量自检"], "草稿必填章节")
    if not list(d.glob("润色稿-*.md")):
        di.append("  ❌ 缺少「润色稿-*.md」")
    qf = list(d.glob("去AI化报告-*.md"))
    if not qf:
        di.append("  ❌ 缺少「去AI化报告-*.md」")
    else:
        for x in qf:
            di += chk.check_qaihua_report(x)
    if not list(d.glob("终稿-*.md")):
        di.append("  ❌ 缺少「终稿-*.md」")
    if not list(d.glob("编辑终审签报-*.md")):
        di.append("  ❌ 缺少「编辑终审签报-*.md」")
    if list(d.glob("终稿-*.md")) and not list(d.glob("合规自检表-*.md")) and not list(d.glob("合规自检表.md")):
        di.append("  ❌ 缺少「合规自检表」")

    genre = "深度分析体"
    if outline.exists():
        ofm, _ = chk.parse_yaml_frontmatter(outline.read_text(encoding="utf-8", errors="ignore"))
        genre = (ofm.get("genre") or "深度分析体").strip() or "深度分析体"
    minw = chk.GENRE_MIN_WORDS.get(genre, 2500)
    for wf in sorted(d.glob("草稿-*.md")) + sorted(d.glob("润色稿-*.md")) + sorted(d.glob("终稿-*.md")):
        if wf.name.startswith("终稿-"):
            di += chk.check_body_structure(wf, "终稿-")
        n = chk.count_body_chars(wf)
        if n < minw:
            di.append(f"  ❌ 正文字数不足: {wf.name} 实测 {n} < {minw}")

    plat = [f for f in files if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)]
    final_refs = list(d.glob("终稿-*.md"))
    fc = chk.count_body_chars(final_refs[0]) if final_refs else 0
    for pf in sorted(plat):
        issues = chk.check_yaml_required(pf, chk.PLATFORM_YAML_KEYS)
        pfx = next((p for p in chk.BODY_STRUCTURE_H2_MIN if pf.name.startswith(p)), "平台")
        issues += chk.check_body_structure(pf, pfx)
        if final_refs:
            sim = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(final_refs[0]))
            if sim >= chk.COMPLIANCE_SIMILAR_TO_FINAL:
                issues.append(f"  ❌ 平台稿与终稿高度雷同 {sim:.0%}: {pf.name}")
        if fc > 0:
            pp = next((p for p in chk.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
            if pp:
                pn = chk.count_body_chars(pf)
                if pn < fc * chk.PLATFORM_MIN_RATIO[pp]:
                    issues.append(f"  ❌ 平台稿内容缩水: {pf.name} 实测 {pn}（终稿 {fc} 的 {pn*100//fc}%）< {int(chk.PLATFORM_MIN_RATIO[pp]*100)}%")
        if final_refs:
            issues += chk.check_platform_coherence(pf, final_refs[0])
        for p, rules in chk.PLATFORM_PREFIX.items():
            if pf.name.startswith(p):
                if p == "知乎-":
                    pt = pf.read_text(encoding="utf-8", errors="ignore")
                    fm, _ = chk.parse_yaml_frontmatter(pt)
                    if not fm.get("source_label"):
                        issues.append("  ❌ frontmatter 缺少 source_label")
                    issues += chk.check_clickable_link(pf)
                else:
                    for kws, rd in rules:
                        issues += chk.check_content(pf, kws, rd)
                break
        if not pf.name.startswith("头条-"):
            for vk, (vkw, vdesc) in chk.PLATFORM_VISUAL_CHECKS.items():
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    issues.append(f"  ❌ 平台视觉要素缺失: {vdesc}")
        if re.search(r"^#{1,3}\s*(读者互动|互动引导)\s*$", pf.read_text(encoding="utf-8", errors="ignore"), re.MULTILINE):
            issues.append("  ❌ 互动引导另起小标题")
        if pf.name.startswith("头条-"):
            for vkw, vdesc in chk.TOUTIAO_VISUAL_REQUIRED:
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    issues.append(f"  ❌ 头条版视觉要素缺失: {vdesc}")
            fk, fdesc = chk.PLATFORM_VISUAL_CHECKS["figures"]
            if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in fk):
                issues.append(f"  ❌ 头条版视觉要素缺失: {fdesc}")
        issues += chk.check_anchor_quality(pf)
        di += issues

    pt = {pf.name: chk.extract_body_text(pf) for pf in sorted(plat)}
    nm = sorted(pt)
    for i in range(len(nm)):
        for j in range(i + 1, len(nm)):
            s = chk.text_similarity(pt[nm[i]], pt[nm[j]])
            if s >= chk.COMPLIANCE_SIMILAR_PLATFORMS:
                di.append(f"  ❌ 平台版高度雷同 {s:.0%}: {nm[i]} vs {nm[j]}")
    di += chk.check_platform_title_diversity(plat, final_refs[0] if final_refs else None)
    di += chk.check_figure_count_uniformity(plat)

    if di:
        report.append(f"\n[选题目录] {d.name}")
        report += di
        total += len(di)

print("=" * 60)
print(f"单日校验 · {DATE}")
print("=" * 60)
if not report:
    print("\n✅ 今日产出全部通过")
else:
    print("\n".join(report))
    print(f"\n共 {total} 项问题")
