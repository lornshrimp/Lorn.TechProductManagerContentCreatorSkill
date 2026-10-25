# -*- coding: utf-8 -*-
"""2026-10-08 局部校验：复用 规范校验.py 的函数，只跑今日目录（快）"""
import sys, io, re, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
SPEC = importlib.util.spec_from_file_location("chk", str(ROOT / ".workbuddy" / "scripts" / "规范校验.py"))
chk = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chk)

DATE = "2026-10-08"
issues_all = []

# 榜单
hs = ROOT / "hotspot" / "榜单" / DATE
for f in sorted(hs.glob("*.md")):
    if f.name == "融合榜单.md":
        t = f.read_text(encoding="utf-8", errors="ignore")
        fm, _ = chk.parse_yaml_frontmatter(t)
        iss = [f"缺少 {k}" for k in ["title", "date", "collectTime"] if not fm.get(k)]
        if not re.search(r"^sources:", t, re.MULTILINE) or not re.search(r"^  - ", t, re.MULTILINE):
            iss.append("sources 列表为空")
        iss += chk.check_section(f, ["打卡表"], "")
        iss += chk.check_section(f, ["TOP 20"], "")
    else:
        iss = chk.check_yaml_required(f, chk.REQUIRED_YAML_KEYS["hotspot/榜单"])
        if "知乎" in f.name and "想法热榜" not in f.name and "想法话题" not in f.name:
            t = f.read_text(encoding="utf-8", errors="ignore")
            if "去回答" not in t and "zhihu.com/question" not in t:
                iss.append("知乎榜单缺链接列")
    if iss:
        issues_all.append(f"[榜单] {f.name}: {iss}")

# 选题卡
tf = ROOT / "hotspot" / "选题" / f"{DATE}-选题卡.md"
if tf.exists():
    iss = chk.check_yaml_required(tf, chk.REQUIRED_YAML_KEYS["hotspot/选题"])
    iss += chk.check_section(tf, ["评分总览"], "")
    t = tf.read_text(encoding="utf-8", errors="ignore")
    n_topics = len(re.findall(r"^###\s+选题[一二三四五六七八九十百]", t, re.MULTILINE))
    n_dedup = t.count("历史去重检测")
    if n_topics and n_dedup < n_topics:
        iss.append(f"历史去重检测 {n_dedup} < {n_topics}")
    iss += chk.check_notebook_refs(tf, ROOT / "notebook")
    if iss:
        issues_all.append(f"[选题卡]: {iss}")

# 研究报告
for d in sorted((ROOT / "research").iterdir()):
    if d.is_dir():
        for f in sorted(d.glob("研究报告.md")):
            t = f.read_text(encoding="utf-8", errors="ignore")
            fm, _ = chk.parse_yaml_frontmatter(t)
            if fm.get("date") == DATE:
                iss = chk.check_yaml_required(f, chk.REQUIRED_YAML_KEYS["research"])
                if iss:
                    issues_all.append(f"[研究报告] {d.name}: {iss}")

# drafts 今日
dd = ROOT / "drafts" / DATE
for d in sorted(dd.iterdir()):
    if not d.is_dir():
        continue
    dir_issues = []
    files = list(d.glob("*.md"))
    outline = d / "大纲.md"
    genre = "深度分析体"
    if outline.exists():
        ot = outline.read_text(encoding="utf-8", errors="ignore")
        ofm, _ = chk.parse_yaml_frontmatter(ot)
        genre = (ofm.get("genre") or "深度分析体").strip() or "深度分析体"
        dir_issues += chk.check_yaml_required(outline, chk.REQUIRED_YAML_KEYS["drafts"])
        dir_issues += chk.check_section(outline, ["段落骨架", "标题策略"], "")
        dir_issues += chk.check_notebook_refs(outline, ROOT / "notebook")
    title_f = d / "标题方案.md"
    if title_f.exists():
        dir_issues += chk.check_yaml_required(title_f, ["type", "date", "topic", "model"])
        dir_issues += chk.check_section(title_f, ["候选池", "评分表", "平台适配"], "")
        tmin = chk.TITLE_CANDIDATE_MIN_BREAKING_NEWS if genre == "快讯评点体" else chk.TITLE_CANDIDATE_MIN
        dir_issues += chk.check_title_candidate_count(title_f, tmin)
        dir_issues += chk.check_platform_title_trace(title_f)
        dir_issues += chk.check_platform_title_length(title_f)
        dir_issues += chk.check_platform_title_punctuation(title_f)
    for df in sorted(d.glob("草稿-*.md")):
        dir_issues += chk.check_yaml_required(df, chk.REQUIRED_YAML_KEYS["drafts"])
        dir_issues += chk.check_section(df, ["素材溯源", "质量自检"], "")
    polish = list(d.glob("润色稿-*.md"))
    if not polish:
        dir_issues.append("缺润色稿")
    qf_list = list(d.glob("去AI化报告-*.md"))
    if not qf_list:
        dir_issues.append("缺去AI化报告")
    else:
        for qf in qf_list:
            dir_issues += chk.check_qaihua_report(qf)
    if not list(d.glob("终稿-*.md")):
        dir_issues.append("缺终稿")
    if not list(d.glob("编辑终审签报-*.md")):
        dir_issues.append("缺签报")
    if list(d.glob("终稿-*.md")) and not list(d.glob("合规自检表*")):
        dir_issues.append("缺合规自检表")
    min_words = chk.GENRE_MIN_WORDS.get(genre, 2500)
    for wf in sorted(d.glob("草稿-*.md")) + sorted(d.glob("润色稿-*.md")) + sorted(d.glob("终稿-*.md")):
        if wf.name.startswith("终稿-"):
            dir_issues += chk.check_body_structure(wf, "终稿-")
        n = chk.count_body_chars(wf)
        if n < min_words:
            dir_issues.append(f"字数不足 {wf.name}: {n} < {min_words}")
    platform_files = [f for f in files if any(f.name.startswith(p) for p in chk.PLATFORM_PREFIX)]
    final_refs = list(d.glob("终稿-*.md"))
    final_chars = chk.count_body_chars(final_refs[0]) if final_refs else 0
    print(f"### {d.name}  终稿={final_chars}字  平台稿={len(platform_files)}")
    for pf in sorted(platform_files):
        iss = chk.check_yaml_required(pf, chk.PLATFORM_YAML_KEYS)
        pfx_label = next((p for p in chk.BODY_STRUCTURE_H2_MIN if pf.name.startswith(p)), "平台")
        iss += chk.check_body_structure(pf, pfx_label)
        if final_refs:
            sim = chk.text_similarity(chk.extract_body_text(pf), chk.extract_body_text(final_refs[0]))
            if sim >= chk.COMPLIANCE_SIMILAR_TO_FINAL:
                iss.append(f"与终稿雷同 {sim:.2%}")
        pn = chk.count_body_chars(pf)
        pf_pfx = next((p for p in chk.PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
        if final_chars and pf_pfx:
            rmin = chk.PLATFORM_MIN_RATIO[pf_pfx]
            if pn < final_chars * rmin:
                iss.append(f"内容缩水 {pn}/{final_chars}={pn*100//final_chars}% < {int(rmin*100)}%")
        if final_refs:
            iss += chk.check_platform_coherence(pf, final_refs[0])
        for pfx, rules in chk.PLATFORM_PREFIX.items():
            if pf.name.startswith(pfx):
                if pfx == "知乎-":
                    fm2, _ = chk.parse_yaml_frontmatter(pf.read_text(encoding="utf-8", errors="ignore"))
                    if not fm2.get("source_label"):
                        iss.append("缺 source_label")
                    iss += chk.check_clickable_link(pf)
                else:
                    for kws, rdesc in rules:
                        iss += chk.check_content(pf, kws, rdesc)
                break
        if not pf.name.startswith("头条-"):
            for vk, (vkw, vdesc) in chk.PLATFORM_VISUAL_CHECKS.items():
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    iss.append(f"缺视觉要素 {vdesc}")
        if re.search(r"^#{1,3}\s*(读者互动|互动引导)\s*$", pf.read_text(encoding="utf-8", errors="ignore"), re.MULTILINE):
            iss.append("互动引导另起小标题")
        if pf.name.startswith("头条-"):
            for vkw, vdesc in chk.TOUTIAO_VISUAL_REQUIRED:
                if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                    iss.append(f"头条缺视觉要素 {vdesc}")
            fk, fdesc = chk.PLATFORM_VISUAL_CHECKS["figures"]
            if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in fk):
                iss.append(f"头条缺 {fdesc}")
        iss += chk.check_anchor_quality(pf)
        nfig = len(set(re.findall(r"\[配图\s*(\d+)\]", pf.read_text(encoding="utf-8", errors="ignore"))))
        print(f"   {pf.name[:28]:30s} {pn:5d}字  ratio={pn*100//final_chars if final_chars else 0}%  fig={nfig}")
        dir_issues += iss
    plat_texts = {pf.name: chk.extract_body_text(pf) for pf in sorted(platform_files)}
    names = sorted(plat_texts)
    mx = 0.0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            s = chk.text_similarity(plat_texts[names[i]], plat_texts[names[j]])
            if s > mx:
                mx = s
    if mx >= chk.COMPLIANCE_SIMILAR_PLATFORMS:
        dir_issues.append(f"平台两两最高 {mx:.2%} >= 85%")
    print(f"   平台两两最高相似度 {mx:.2%}")
    dir_issues += chk.check_platform_title_diversity(platform_files, final_refs[0] if final_refs else None)
    dir_issues += chk.check_figure_count_uniformity(platform_files)
    if dir_issues:
        issues_all.append(f"[选题目录] {d.name}:\n    " + "\n    ".join(dir_issues))

print("\n" + "=" * 60)
if not issues_all:
    print("今日目录：0 问题 ✅")
else:
    print(f"今日目录问题 {len(issues_all)} 组：")
    for x in issues_all:
        print(x)
