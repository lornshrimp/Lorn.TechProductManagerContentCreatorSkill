#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自媒体流水线产出物规范符合性校验脚本
====================================
用途：自动化任务（每日热点选题创作流水线）结束前自动扫描当日全部产出文件，
      核对各 skill 的 Output 规范必填项，输出校验报告。不合格项由执行代理回修后重跑本脚本。

设计原则：
- 不依赖模型记忆——规范以代码形式固化
- 只查"必填项"（技能中标注必须/强制的内容），不查建议项
- 输出结构化报告，供执行代理逐项修复

用法：
    python 规范校验.py --date 2026-08-08
    （缺省 --date 时使用今天）
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ============================================================
# 配置区：按 skill 规范固化的必填项（2026-08-08 汇总，随 skill 更新而更新）
# ============================================================

REQUIRED_YAML_KEYS = {
    # 各产出物的 frontmatter 必填字段
    "hotspot/榜单": ["title", "date", "source", "collectTime"],
    "hotspot/选题": ["type", "date", "model"],
    "research": ["type", "date", "topic", "depth", "model"],
    "drafts": ["type", "date", "topic", "model"],
}

# 知乎版（deai-adapt-zhihu）：source_label 必填；source_url 非空时必须含 Clickable Link 行
ZHIHU_REQUIRED = {
    "source_label": "frontmatter 必须含 source_label（邀请问题#N / 推荐问题#N / 热榜#N / 独立文章）",
    "clickable_rule": "source_url 非空时，frontmatter 之后正文之前必须有 [→ 去回答该问题](...) 行",
}

# 融合榜单（deai-hotspot）：必须含打卡表与 sources 对应
FUSION_CHECKS = {
    "采集打卡表": "必须含「采集打卡表」或「打卡表」章节，19 源逐源状态",
    "sources列表": "YAML sources 字段非空，且与打卡表 ✅ 源对应",
    "TOP20": "必须含「TOP 20」表格",
}

# 草稿（deai-write）：必须含素材溯源 + 质量自检
DRAFT_CHECKS = {
    "素材溯源": "必须含「素材溯源」或「素材溯源表」章节",
    "质量自检": "必须含「质量自检报告」或「自检报告」章节",
}

# 终稿（deai-review）：必须含编辑终审签报
REVIEW_CHECKS = {
    "终审签报": "同一目录必须存在「编辑终审签报-*.md」文件",
    "审核结论": "终稿 frontmatter 或签报中必须含审核结论（通过/微调发布/不通过）",
}

# 去AI化（deai-polish）：润色稿 + 去AI化报告成对
POLISH_CHECKS = {
    "润色稿": "目录必须存在「润色稿-*.md」",
    "去AI化报告": "目录必须存在「去AI化报告-*.md」",
}

# 大纲（deai-outline）：段落骨架
OUTLINE_CHECKS = {
    "段落骨架": "必须含「段落骨架」章节（每段含钩子类型/字数/情绪定位）",
    "标题策略": "必须含「标题策略」章节",
}

# 标题方案（deai-title）：候选池 + 评分表
TITLE_CHECKS = {
    "候选池": "必须含「候选池」章节（≥5 个候选）",
    "评分表": "必须含「评分表」或「六维评分」章节",
    "平台适配": "必须含「平台适配」章节（各平台首选标题）",
}

# 微信版（deai-adapt-wechat）：封面图提示词 + 内容简介（内容级关键词检查，2026-08-08 修复）
WECHAT_CHECKS = [
    (["封面图", "AI 提示词", "prompt"], "封面图 AI 提示词"),
    (["内容简介", "摘要"], "内容简介"),
    (["在看", "留言", "关注"], "点在看/留言/关注类互动引导"),
]

# 百家号版（deai-adapt-baiduhao）：SEO 关键词 + 开头直接给答案
BAIDUHAO_CHECKS = [
    (["关键词", "SEO", "搜索"], "SEO 关键词"),
    (["核心答案", "核心摘要", "**核心"], "开头直接给答案"),
]

# CSDN 版（deai-adapt-csdn）：结构化（H2/H3 或表格）+ 方法论
CSDN_CHECKS = [
    (["## ", "### ", "|"], "H2/H3 小标题或表格（结构化排版）"),
    (["方法论", "步骤", "框架", "分析", "要点"], "方法论/步骤/技术内容"),
]

# 头条版（deai-adapt-toutiao）：短段落 + 关注引导
TOUTIAO_CHECKS = [
    (["关注我", "关注"], "结尾关注引导"),
    (["\n", "。", "！"], "短段落结构（正文存在）"),
]

# 平台适配版文件名前缀 → 对应的校验规则
# 知乎版用 ZHIHU_REQUIRED（frontmatter source_label + clickable），其余用内容关键词规则
PLATFORM_PREFIX = {
    "知乎-": ZHIHU_REQUIRED,
    "微信-": WECHAT_CHECKS,
    "百家号-": BAIDUHAO_CHECKS,
    "CSDN-": CSDN_CHECKS,
    "头条-": TOUTIAO_CHECKS,
}

# 字数实测门禁（2026-08-08 新增）：按大纲 genre 映射体裁底线；草稿/润色稿/终稿正文字数不足即 ❌。
# 教训：此前"约 2300 字"为估算值，实测仅 1158-1661 字，导致不达标产出通过签报。字数必须实测，禁止估算。
GENRE_MIN_WORDS = {
    "深度分析体": 2500,
    "观点评论体": 1500,
    "清单体": 1500,
    "快讯评点体": 500,
    "故事体": 1500,
    "问题解决体": 800,
}

# 平台适配版 frontmatter 必填字段（deai-adapt-* 规范：title/date/platform/topic，无 type）
PLATFORM_YAML_KEYS = ["title", "date", "platform", "topic"]

# 平台稿内容保真门禁（2026-08-10 新增，教训固化）：
# 平台稿 = 终稿的平台化改写，不是摘要缩写。正文不得低于终稿字数的阈值比例。
# 教训：2026-08-10 平台稿实测仅为终稿的 17%-41%（知乎 26%/微信 21%/头条 25%），
# 等于把 2500 字深度内容压缩成 500-700 字摘要——根源是规范与脚本只查"关键词存在"不查内容量。
PLATFORM_MIN_RATIO = {
    "知乎-": 0.90,   # deai-adapt-zhihu：母稿信息不动、论证加厚，不得低于母稿
    "微信-": 0.85,   # 公众号深度主阵地，不做缩水
    "百家号-": 0.70,
    "CSDN-": 0.70,
    "头条-": 0.70,   # 短段落 ≠ 短内容
}

# 平台视觉要素门禁（2026-08-10 新增，教训固化）：
# 每个平台稿除完整正文外，必须产出三组视觉要素（对应各 adapt 技能封面图/配图章节：
# 知乎 7.5/7.6、微信 7.1-7.4、百家号 6.5/6.6、CSDN 8/9、头条 6.5/6.6）。
# 教训：2026-08-10 全部 15 个平台稿均无封面图提示词/内容简介/配图规划——
# 技能有定义但编排层未强制、校验层未检查，导致"有规范但产出被无视"。
# 检查方式：全文关键词（封面图提示词标记 / 内容简介标记 / 配图锚文本+提示词标记）。
PLATFORM_VISUAL_CHECKS = {
    "cover": (["[封面图提示词]", "封面图", "题图", "AI 提示词", "prompt"], "封面图 AI 提示词（必填）"),
    "summary": (["[内容简介]", "内容简介", "摘要"], "内容简介（必填）"),
    "figures": (["[配图1]", "[配图", "## 配图详情", "配图搜索替换指令", "插入位置", "锚文本"],
                "文中配图规划（≥1 张，含锚文本定位 + AI 提示词）"),
}

# 头条版封面图/内容简介检查（2026-08-10 新增：头条技能 6.5 明确封面图必填，
# 但 TOUTIAO_CHECKS 原先只查"关注我"——头条版封面提示词/内容简介曾被整体漏检）
TOUTIAO_VISUAL_REQUIRED = [
    (["[封面图提示词]", "封面图", "题图", "AI 提示词", "prompt"], "封面图 AI 提示词（头条技能 6.5 必填）"),
    (["[内容简介]", "内容简介", "摘要"], "内容简介（头条技能 6.5 摘要字段）"),
]

# 附属内容标记：统计正文时在此截断（草稿的素材溯源/质量自检、适配版的封面/配图/SEO 等）
BODY_TRUNCATE_MARKERS = [
    "## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 封面图",
    "## 内容简介", "## 互动引导", "## SEO 关键词", "## 配图详情",
    "# 附属内容区域", "## 配图搜索替换指令", "## 参考来源",
    "## 润色说明", "## 发布建议",
]


def parse_yaml_frontmatter(text: str) -> tuple:
    """解析 YAML frontmatter，返回 (dict, 正文起点)"""
    if not text.startswith("---"):
        return {}, 0
    end = text.find("\n---", 3)
    if end == -1:
        return {}, 0
    yaml_block = text[3:end]
    result = {}
    for line in yaml_block.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        result[key.strip()] = val.strip()
    return result, end + 4


def check_yaml_required(path: Path, expected_keys: list) -> list:
    """检查 frontmatter 必填字段"""
    issues = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    fm, _ = parse_yaml_frontmatter(text)
    for key in expected_keys:
        if key not in fm or not fm[key]:
            issues.append(f"  ❌ frontmatter 缺少必填字段: {key}")
    return issues


def check_section(path: Path, section_names: list, desc: str) -> list:
    """检查正文是否含指定章节标题"""
    issues = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for name in section_names:
        # 支持「## xxx」或「# xxx」标题
        if not re.search(rf"^#+\s*.*{re.escape(name)}.*$", text, re.MULTILINE):
            issues.append(f"  ❌ 缺少章节: {name}（{desc}）")
    return issues


def check_clickable_link(path: Path) -> list:
    """知乎版：source_url 非空时必须含 Clickable Link"""
    issues = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    fm, _ = parse_yaml_frontmatter(text)
    url = fm.get("source_url", "").strip()
    if url and "[→ 去回答该问题]" not in text:
        issues.append("  ❌ source_url 非空但缺少 Clickable Link 行: [→ 去回答该问题](url)")
    return issues


def count_body_chars(path: Path) -> int:
    """实测正文中文字符数：去掉 frontmatter、H1 标题与附属内容区（素材溯源/质量自检/封面/配图等）。
    字数必须实测（禁止估算）——2026-08-08 教训固化。"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    text = re.sub(r"^#\s+.*$", "", text, flags=re.MULTILINE)
    for marker in BODY_TRUNCATE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
            break
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def check_content(path: Path, keywords: list, desc: str) -> list:
    """全文关键词检查（平台版规范项）：命中任一关键词即通过。
    2026-08-08 修复：原用 check_section 按"标题行包含检查项名"匹配（如找名为'结构化'的标题），
    与实际产出格式不符导致误报；改为内容级关键词匹配。"""
    issues = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not any(kw in text for kw in keywords):
        issues.append(f"  ❌ 缺少内容: {desc}（需含关键词之一: {'/'.join(keywords)}）")
    return issues


def find_project_root() -> Path:
    """定位项目根目录：从脚本位置向上查找包含 hotspot/ 与 drafts/ 的目录。
    2026-08-08 修复：原 `Path(__file__).resolve().parent.parent` 解析到 .workbuddy 目录
    （scripts 的上一级），导致 hotspot/drafts 路径全部不存在 → 校验从未真正执行、
    长期输出假阳性"全部通过"。这是字数不达标漏过的根本原因之一。"""
    p = Path(__file__).resolve()
    for cand in [p, *p.parents]:
        if (cand / "hotspot").is_dir() and (cand / "drafts").is_dir():
            return cand
    return p.parents[2]  # 兜底：项目根


def main():
    parser = argparse.ArgumentParser(description="自媒体流水线产出物规范校验")
    parser.add_argument("--date", default="", help="日期 YYYY-MM-DD，缺省用今天")
    parser.add_argument("--root", default="", help="工作区根目录，缺省自动探测项目根")
    args = parser.parse_args()

    root = Path(args.root) if args.root else find_project_root()
    date = args.date or __import__("datetime").date.today().isoformat()

    report = []
    total_issues = 0

    # ---------- 1. 榜单与选题卡 ----------
    hotspot_dir = root / "hotspot" / "榜单" / date
    if hotspot_dir.exists():
        for f in sorted(hotspot_dir.glob("*.md")):
            name = f.name
            if name == "融合榜单.md":
                # 融合榜单 frontmatter 用 sources 列表（多行 "  - 来源名"），无单数 source 字段。
                # 2026-08-08 修复：parse_yaml_frontmatter 不支持 YAML 列表（"sources:" 后多行 "- " 被跳过），
                # 改为文本级校验 sources 列表，避免误报。
                issues = []
                text = f.read_text(encoding="utf-8", errors="ignore")
                fm, _ = parse_yaml_frontmatter(text)
                for key in ["title", "date", "collectTime"]:
                    if key not in fm or not fm[key]:
                        issues.append(f"  ❌ frontmatter 缺少必填字段: {key}")
                if not re.search(r"^sources:", text, re.MULTILINE) or not re.search(r"^  - ", text, re.MULTILINE):
                    issues.append("  ❌ YAML sources 列表为空（应含 'sources:' 及多行 '  - 来源名'）")
                issues += check_section(f, ["打卡表"], "19 源逐源状态")
                issues += check_section(f, ["TOP 20"], "跨平台热点表")
            else:
                issues = check_yaml_required(f, REQUIRED_YAML_KEYS["hotspot/榜单"])
                # 知乎类榜单必须含链接列
                if "知乎" in name and "想法热榜" not in name and "想法话题" not in name:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    if "去回答" not in text and "zhihu.com/question" not in text:
                        issues.append("  ❌ 知乎类榜单必须含「链接」列 [去回答](zhihu.com/question/...)")
            if issues:
                report.append(f"\n[榜单] {hotspot_dir.name}/{name}")
                report += issues
                total_issues += len(issues)

    topic_dir = root / "hotspot" / "选题"
    if topic_dir.exists():
        for f in sorted(topic_dir.glob(f"{date}-选题卡.md")):
            issues = check_yaml_required(f, REQUIRED_YAML_KEYS["hotspot/选题"])
            issues += check_section(f, ["评分总览"], "选题评分表")
            if issues:
                report.append(f"\n[选题卡] {f.name}")
                report += issues
                total_issues += len(issues)

    # ---------- 2. 研究报告 ----------
    research_dir = root / "research"
    if research_dir.exists():
        for d in sorted(research_dir.iterdir()):
            if d.is_dir():
                for f in sorted(d.glob("研究报告.md")):
                    issues = check_yaml_required(f, REQUIRED_YAML_KEYS["research"])
                    if issues:
                        report.append(f"\n[研究报告] {d.name}/研究报告.md")
                        report += issues
                        total_issues += len(issues)

    # ---------- 3. drafts 各选题目录 ----------
    drafts_dir = root / "drafts"
    if drafts_dir.exists():
        for d in sorted(drafts_dir.iterdir()):
            if not d.is_dir():
                continue
            files = list(d.glob("*.md"))
            if not files:
                continue
            dir_label = f"\n[选题目录] {d.name}"
            dir_issues = []

            # 大纲
            outline = d / "大纲.md"
            if outline.exists():
                issues = check_yaml_required(outline, REQUIRED_YAML_KEYS["drafts"])
                issues += check_section(outline, ["段落骨架", "标题策略"], "大纲必填章节")
                dir_issues += issues

            # 标题方案
            title_f = d / "标题方案.md"
            if title_f.exists():
                issues = check_yaml_required(title_f, ["type", "date", "topic", "model"])
                issues += check_section(title_f, ["候选池", "评分表", "平台适配"], "标题方案必填章节")
                dir_issues += issues

            # 草稿 + 润色稿 + 去AI化报告
            drafts = list(d.glob("草稿-*.md"))
            for df in drafts:
                issues = check_yaml_required(df, REQUIRED_YAML_KEYS["drafts"])
                issues += check_section(df, ["素材溯源", "质量自检"], "草稿必填章节")
                dir_issues += issues

            polish_files = list(d.glob("润色稿-*.md"))
            if not polish_files:
                dir_issues.append("  ❌ 缺少「润色稿-*.md」（deai-polish 必产出）")
            if not list(d.glob("去AI化报告-*.md")):
                dir_issues.append("  ❌ 缺少「去AI化报告-*.md」（deai-polish 必产出）")

            # 终稿 + 编辑终审签报
            if not list(d.glob("终稿-*.md")):
                dir_issues.append("  ❌ 缺少「终稿-*.md」（deai-review 必产出）")
            if not list(d.glob("编辑终审签报-*.md")):
                dir_issues.append("  ❌ 缺少「编辑终审签报-*.md」（deai-review 必产出）")

            # 字数实测门禁（2026-08-08 新增，硬性）：从大纲 frontmatter 读 genre → 体裁底线；
            # 草稿/润色稿/终稿正文中文字数不足即 ❌。禁止估算字数——估算通过 = 本轮事故根因。
            genre = "深度分析体"
            if outline.exists():
                ot = outline.read_text(encoding="utf-8", errors="ignore")
                ofm, _ = parse_yaml_frontmatter(ot)
                genre = (ofm.get("genre") or "深度分析体").strip() or "深度分析体"
            min_words = GENRE_MIN_WORDS.get(genre, 2500)
            for wf in (sorted(d.glob("草稿-*.md")) + sorted(d.glob("润色稿-*.md"))
                       + sorted(d.glob("终稿-*.md"))):
                n = count_body_chars(wf)
                if n < min_words:
                    dir_issues.append(
                        f"  ❌ 正文字数不足: {wf.name} 实测 {n} 字 < {min_words} 字"
                        f"（{genre} 底线，必须实测不得估算）")

            # 平台适配版
            platform_files = [f for f in files if any(f.name.startswith(p) for p in PLATFORM_PREFIX)]

            # 平台稿内容保真基准（2026-08-10 新增，教训固化）：以终稿字数为基准，
            # 平台稿正文低于阈值比例即 ❌（平台稿=改写非摘要）。终稿缺失则跳过该项（其余检查兜底）。
            final_refs = list(d.glob("终稿-*.md"))
            final_chars = count_body_chars(final_refs[0]) if final_refs else 0

            for pf in sorted(platform_files):
                issues = check_yaml_required(pf, PLATFORM_YAML_KEYS)

                # 内容保真门禁：平台稿字数 ≥ 终稿 × 阈值（2026-08-10 新增）
                # 教训：2026-08-10 平台稿实测仅为终稿 17%-41%，等于把深度文缩成摘要，
                # 且因关键词检查通过而漏网——必须用字数比例硬性拦截"摘要式平台稿"。
                if final_chars > 0:
                    pf_pfx = next((p for p in PLATFORM_MIN_RATIO if pf.name.startswith(p)), "")
                    if pf_pfx:
                        ratio_min = PLATFORM_MIN_RATIO[pf_pfx]
                        pn = count_body_chars(pf)
                        if pn < final_chars * ratio_min:
                            issues.append(
                                f"  ❌ 平台稿内容缩水: {pf.name} 实测 {pn} 字"
                                f"（终稿 {final_chars} 字的 {pn * 100 // final_chars}%）"
                                f" < 保真底线 {int(ratio_min * 100)}%（平台稿=终稿改写非摘要，"
                                f"核心论点/数据/金句必须全量保留）")

                for pfx, rules in PLATFORM_PREFIX.items():
                    if pf.name.startswith(pfx):
                        if pfx == "知乎-":
                            # 知乎版（deai-adapt-zhihu）：frontmatter 必含 source_label
                            # （邀请问题#N / 推荐问题#N / 热榜#N / 独立文章）；source_url 非空时
                            # frontmatter 之后正文之前必须有 [→ 去回答该问题](url) Clickable Link 行。
                            # 2026-08-08 修复：source_label 检查原被 clickable_rule 分支短路，
                            # 改为从 frontmatter 读取校验（check_section 只搜正文标题，无效）。
                            pf_text = pf.read_text(encoding="utf-8", errors="ignore")
                            fm, _ = parse_yaml_frontmatter(pf_text)
                            if not fm.get("source_label"):
                                issues.append("  ❌ frontmatter 缺少必填字段: source_label（邀请问题#N/推荐问题#N/热榜#N/独立文章）")
                            issues += check_clickable_link(pf)
                        else:
                            # 非知乎平台：内容级关键词检查（2026-08-08 修复，替代错误的标题行匹配）
                            for keywords, rdesc in rules:
                                issues += check_content(pf, keywords, rdesc)
                        break

                # 平台视觉要素门禁（2026-08-10 新增，教训固化）：
                # 每个平台稿必须产出封面图提示词 + 内容简介 + 文中配图规划（锚文本+提示词）。
                # 教训：2026-08-10 全部 15 个平台稿均无插图内容，因技能定义未被校验层拦截——
                # 新增三组必检项（封面/简介/配图），任一缺失即 ❌。
                # 头条版：封面/简介由 TOUTIAO_VISUAL_REQUIRED 专项检查（见下），此处跳过避免重复报。
                if not pf.name.startswith("头条-"):
                    for vk, (vkw, vdesc) in PLATFORM_VISUAL_CHECKS.items():
                        if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                            issues.append(f"  ❌ 平台视觉要素缺失: {vdesc}（适配技能封面图/配图章节必产）")

                # 头条版专项：封面图 + 内容简介（头条技能 6.5 必填项，原 TOUTIAO_CHECKS 漏检）
                if pf.name.startswith("头条-"):
                    for vkw, vdesc in TOUTIAO_VISUAL_REQUIRED:
                        if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in vkw):
                            issues.append(f"  ❌ 头条版视觉要素缺失: {vdesc}")
                    # 头条版配图检查（沿用通用 figures 规则）
                    fk, fdesc = PLATFORM_VISUAL_CHECKS["figures"]
                    if not any(k in pf.read_text(encoding="utf-8", errors="ignore") for k in fk):
                        issues.append(f"  ❌ 头条版视觉要素缺失: {fdesc}")
                dir_issues += issues

            if dir_issues:
                report.append(dir_label)
                report += dir_issues
                total_issues += len(dir_issues)

    # ---------- 输出 ----------
    print("=" * 60)
    print(f"自媒体流水线产出物规范校验报告 · {date}")
    print("=" * 60)
    if not report:
        print("\n✅ 全部通过：所有必填项均符合 skill Output 规范。")
        return 0
    print("\n".join(report))
    print(f"\n{'='*60}")
    print(f"共发现 {total_issues} 项问题，请逐项修复后重跑本脚本。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
