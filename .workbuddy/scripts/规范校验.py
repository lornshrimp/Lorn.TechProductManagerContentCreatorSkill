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

# 微信版（deai-adapt-wechat）：封面图提示词 + 内容简介
WECHAT_CHECKS = {
    "封面图提示词": "必须含「封面图 AI 提示词」或「封面图」",
    "内容简介": "必须含「内容简介」",
    "引导": "必须含「点在看/留言/关注」类互动引导",
}

# 百家号版（deai-adapt-baiduhao）：SEO 关键词
BAIDUHAO_CHECKS = {
    "关键词": "必须含「关键词」或「搜索关键词」",
    "核心摘要": "必须含「核心摘要」或开头直接给答案",
}

# CSDN 版（deai-adapt-csdn）：方法论/结构化
CSDN_CHECKS = {
    "结构化": "必须含 H2/H3 小标题或表格（结构化排版）",
    "方法论/技术": "必须含方法论/步骤/技术内容，非纯叙事",
}

# 头条版（deai-adapt-toutiao）：短段落 + 关注引导
TOUTIAO_CHECKS = {
    "短段落": "正文段落平均 ≤3 句（头条规范）",
    "关注引导": "结尾必须含「关注我/关注」类引导",
}

# 平台适配版文件名前缀 → 对应的校验规则
PLATFORM_PREFIX = {
    "知乎-": ZHIHU_REQUIRED,
    "微信-": WECHAT_CHECKS,
    "百家号-": BAIDUHAO_CHECKS,
    "CSDN-": CSDN_CHECKS,
    "头条-": TOUTIAO_CHECKS,
}


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


def main():
    parser = argparse.ArgumentParser(description="自媒体流水线产出物规范校验")
    parser.add_argument("--date", default="", help="日期 YYYY-MM-DD，缺省用今天")
    parser.add_argument("--root", default="", help="工作区根目录，缺省用脚本上级目录")
    args = parser.parse_args()

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    date = args.date or __import__("datetime").date.today().isoformat()

    report = []
    total_issues = 0

    # ---------- 1. 榜单与选题卡 ----------
    hotspot_dir = root / "hotspot" / "榜单" / date
    if hotspot_dir.exists():
        for f in sorted(hotspot_dir.glob("*.md")):
            name = f.name
            issues = check_yaml_required(f, REQUIRED_YAML_KEYS["hotspot/榜单"])
            # 知乎类榜单必须含链接列
            if "知乎" in name and "想法热榜" not in name and "想法话题" not in name:
                text = f.read_text(encoding="utf-8", errors="ignore")
                if "去回答" not in text and "zhihu.com/question" not in text:
                    issues.append("  ❌ 知乎类榜单必须含「链接」列 [去回答](zhihu.com/question/...)")
            if name == "融合榜单.md":
                issues += check_section(f, ["打卡表"], "19 源逐源状态")
                issues += check_section(f, ["TOP 20"], "跨平台热点表")
                text = f.read_text(encoding="utf-8", errors="ignore")
                fm, _ = parse_yaml_frontmatter(text)
                if not fm.get("sources"):
                    issues.append("  ❌ YAML sources 列表为空")
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
            prefix = f"\n[选题目录] {d.name}"
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

            # 平台适配版
            platform_files = [f for f in files if any(f.name.startswith(p) for p in PLATFORM_PREFIX)]
            for pf in sorted(platform_files):
                issues = check_yaml_required(pf, REQUIRED_YAML_KEYS["drafts"])
                for prefix, rules in PLATFORM_PREFIX.items():
                    if pf.name.startswith(prefix):
                        if "clickable_rule" in rules:
                            issues += check_clickable_link(pf)
                        else:
                            for rname, rdesc in rules.items():
                                if rname == "clickable_rule":
                                    continue
                                issues += check_section(pf, [rname], rdesc)
                        break
                dir_issues += issues

            if dir_issues:
                report.append(prefix)
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
