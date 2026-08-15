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

合规检查（2026-08-11 新增，对应 deai-compliance Skill）：
- 平台稿与终稿高度雷同（≥99%，未做平台化改写）→ ❌
- 两个平台版之间高度雷同（≥85%，机器复制特征/非真人自动化创作风险）→ ❌
- 每日流水线选题目录必须含「合规自检表-*.md」（deai-compliance 必产出）→ ❌

用法：
    python 规范校验.py --date 2026-08-08
    （缺省 --date 时使用今天）
"""

import argparse
import difflib
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

# ============================================================
# 合规检查配置（2026-08-11 新增，对应 deai-compliance Skill）
# ============================================================
# 背景：微信 2025-03「非真人自动化创作行为」专项条款（限流/删除/封号）、
#      小红书 2025-02 AI 内容主动标识、知乎 2025-10 清朗行动、
#      《AI 生成合成内容标识办法》2025-09-01 强制施行。
#      平台稿必须"改写非复制"——与终稿雷同 = 未做平台化改写；平台间雷同 = 机器复制特征。
COMPLIANCE_SIMILAR_TO_FINAL = 0.99  # 平台稿与终稿相似度 ≥99% → 未改写，❌
COMPLIANCE_SIMILAR_PLATFORMS = 0.85  # 两平台版相似度 ≥85% → 机器复制特征，❌
# 合规自检表文件名模式（deai-compliance 必产出）
COMPLIANCE_CHECKFILE = "合规自检表"


def check_anchor_quality(path: Path) -> list:
    """配图锚文本质量门禁（2026-08-14 新增，教训固化）。

    背景：2026-08-14 用户复核指出——平台稿配图锚文本不是段落首句，人工 Ctrl+F
    定位困难。当日核查 15 稿 24 锚点：9 处锚文本在正文完全搜不到（指向小标题/
    笔误），3 处出现在段落第二句（人工需先找到段再往下一句看）。

    门禁规则（每个 [配图N] 的锚文本必须）：
    ① 在正文区（配图区前）唯一出现（出现次数 == 1，避免多匹配）
    ② 位于所在段落首句（锚文本前是段落边界或句末标点），或锚定表格行（表格场景
       无正文段可锚，允许锚表格单元格，如 "| 计费项"）
    ③ 配图搜索替换指令区包含该锚文本（「锚」格式）
    """
    issues = []
    try:
        c = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return issues
    # 提取所有锚文本
    anchors = []
    for line in c.split("\n"):
        if "锚文本定位" in line and "**" in line:
            parts = line.split("**")
            if len(parts) >= 3:
                a = parts[2].strip().strip("：: ").strip('"').strip("'")
                if a:
                    anchors.append(a)
    if not anchors:
        return issues  # 无配图锚文本时由 figures 存在性检查兜底
    # 正文区：frontmatter 后、配图区前
    body = c
    if body.startswith("---"):
        end = body.find("\n---", 3)
        body = body[end + 4:] if end != -1 else body
    for marker in ["[封面图提示词]", "[配图1]"]:
        idx = body.find(marker)
        if idx != -1:
            body = body[:idx]
            break
    for a in anchors:
        cnt = body.count(a)
        if cnt == 0:
            issues.append(f"  ❌ 配图锚文本未命中正文: 「{a}」——正文搜不到，人工无法定位（须取目标段落首句）")
            continue
        if cnt > 1:
            issues.append(f"  ❌ 配图锚文本不唯一: 「{a}」在正文出现 {cnt} 次——须取唯一短句")
            continue
        # 段首判定：锚文本必须精确位于段落首句——锚文本到最近段落边界之间
        # 只能是空白（\n）或段落起始，不能有其他正文文字。
        pos = body.find(a)
        seg = body[:pos]  # 锚文本之前全部内容
        # 找最近的一个段落分隔（\n\n）或文件开头
        seg_start = seg.rfind("\n\n")
        seg_tail = seg[seg_start + 2:] if seg_start != -1 else seg
        # seg_tail 是锚文本所在段落的段首前缀，应为空（锚在段首）或仅含零宽字符
        is_start = seg_tail.strip() == ""
        is_table = f"| {a}" in body or f"|{a}" in body  # 表格行例外
        if not (is_start or is_table):
            issues.append(f"  ❌ 配图锚文本非段落首句: 「{a}」——须取该段落第一句（人工 Ctrl+F 从段首定位）")
        # 指令区同步检查
        if f"「{a}」" not in c:
            issues.append(f"  ❌ 配图搜索替换指令缺锚: 「{a}」未出现在配图搜索替换指令区")
    return issues


def extract_body_text(path: Path) -> str:
    """提取正文纯文本（去 frontmatter/H1/附属区，去空白），用于相似度比对。
    2026-08-11 新增：平台稿改写度检查的比对基础。"""
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
    return re.sub(r"\s+", "", text)


def text_similarity(a: str, b: str) -> float:
    """两段文本相似度（0-1，基于 SequenceMatcher）。
    必须关闭 autojunk：SequenceMatcher 默认将出现频率 >1% 的字符视为 junk 不参与匹配，
    对高度重复的中文文本（如测试样例"这是正文内容"×N）会误判相似度为 0——
    这正是"校验脚本修改后必须用已知不达标样例验证"铁律要拦截的假阴性。"""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


def _raw_body(path: Path) -> str:
    """提取原始正文（保留段落结构）：去 frontmatter/H1/Clickable/附属区，不压缩空白。"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        text = text[end + 4:] if end != -1 else text
    text = re.sub(r"^#\s+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\[→.*$", "", text, flags=re.MULTILINE)
    cut = len(text)
    for marker in BODY_TRUNCATE_MARKERS + ["[封面图提示词]", "[内容简介]", "[配图"]:
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    return text[:cut]


def check_platform_coherence(path: Path, final_path: Path) -> list:
    """平台稿正文连贯性门禁（2026-08-13 新增，当日两轮修订至最终语义）。

    拦截"两篇文章拼一起"式的割裂产出——2026-08-13 实际发生并被人工复核拦截：
    平台稿补字时把终稿原文段落原样粘贴进平台稿，与已写内容重复、读起来前后割裂。
    ⚠️ 两个设计定论（来自用户复核 2026-08-13）：
    1. 割裂感的本质不是 `---` 分隔符（那是合法 markdown，任何平台稿都允许有多个），
       而是"前后段看起来就是两篇文章放一块儿了"；
    2. "保留母稿内容"本身不是问题——知乎 ≥90%/微信 ≥85% 保真是铁律，平台稿含大量
       与终稿逐字相同的段落属正常形态；知乎版同样不因"接近母稿"豁免。
       真正的问题只有一个：母稿原文段落被拼进来且与已写内容重复（同一论点说两遍），
       或集中堆砌成"第二篇文章"——这两者都会让读者感到割裂。
    ⚠️ 故本门禁只检测一个信号：**与前方正文的内容重复**（前文重复 = 第二篇在复述第一篇，
    最硬的割裂证据）。"母稿段的位置/长度/连续性"均不作为信号（微信 85% 保真下必然误报）。
    判定：
    ① 找出正文中与终稿段落逐字相似（相似度 ≥0.9 且 ≥60 字）的母稿逐字段；
    ② 任一母稿逐字段与其前方任一非母稿段相似度 ≥0.55（同一表述/同一数据出现两遍）→ ❌。
    正确做法：平台稿一次性写成完整连贯文章，保留母稿论点必须改写成平台风格并放在
    首次出现的位置；不得把母稿原文段落二次引入已论述过的内容。"""
    issues = []
    body = _raw_body(path)
    if not body.strip():
        return issues

    paras = [p.strip() for p in re.split(r"\n{2,}", body) if p.strip()]
    if len(paras) < 4:
        return issues

    def _norm(p: str) -> str:
        return re.sub(r"\s+", "", p)

    final_paras = [_norm(p) for p in re.split(r"\n{2,}", _raw_body(final_path))
                   if len(_norm(p)) >= 60]

    copied_idx = []
    for i, p in enumerate(paras):
        np = _norm(p)
        if len(np) < 60:
            continue
        if any(text_similarity(np, fp) >= 0.9 for fp in final_paras):
            copied_idx.append(i)

    if not copied_idx:
        return issues

    # 前文重复检测：母稿逐字段 vs 位置在前的非母稿段
    copied_set = set(copied_idx)
    dup = False
    dup_pair = None
    for ci in copied_idx:
        for j in range(ci):
            if j in copied_set:
                continue
            s = text_similarity(_norm(paras[ci]), _norm(paras[j]))
            if s >= 0.55:
                dup = True
                dup_pair = (j, ci, s)
                break
        if dup:
            break

    if dup:
        j, ci, s = dup_pair
        issues.append(
            f"  ❌ 平台稿正文连贯性: 正文第 {ci + 1} 段（与终稿逐字相同，≥60 字）与前方第 {j + 1} 段"
            f"内容重复（相似度 {s:.0%}）——同一论点出现两遍，读起来像两篇文章拼一起"
            f"（割裂感与 `---` 分隔符无关，任何平台稿都禁止重复引入母稿原文段，知乎版同样不豁免）；"
            f"保留母稿论点必须改写成平台风格并在首次出现处一次性讲完，删除重复段落")
    return issues


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
    # 目录结构（2026-08-12 起）：drafts/{日期}/{选题名}/；兼容历史遗留的 drafts/{选题名}/ 顶层目录。
    drafts_dir = root / "drafts"
    if drafts_dir.exists():
        topic_dirs = []
        for d in sorted(drafts_dir.iterdir()):
            if not d.is_dir():
                continue
            # 日期格式目录（YYYY-MM-DD）→ 其子目录为选题目录
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d.name):
                topic_dirs += [c for c in sorted(d.iterdir()) if c.is_dir()]
            else:
                topic_dirs.append(d)  # 历史遗留：顶层即选题目录
        for d in topic_dirs:
            files = list(d.glob("*.md"))
            if not files:
                continue
            dir_label = f"\n[选题目录] {d.relative_to(root)}"
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

            # 合规自检表（2026-08-11 新增，deai-compliance 必产出）：
            # 若目录已有终稿（=走完 review 的完整选题），必须有合规自检表才可进入发布。
            # 背景：微信"非真人自动化创作行为"条款与定时流水线冲突，发布前必须人工确认 + 合规自检。
            if list(d.glob("终稿-*.md")) and not list(d.glob(f"{COMPLIANCE_CHECKFILE}-*.md")) \
                    and not list(d.glob(f"{COMPLIANCE_CHECKFILE}.md")):
                dir_issues.append("  ❌ 缺少「合规自检表」（deai-compliance 必产出——"
                                  "发布前须确认 AI 参与度分级/发布节奏人性化/人工确认节点）")

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

                # 合规：平台稿与终稿相似度（2026-08-11 新增）
                # 背景：平台稿 = 终稿的平台化改写；若与终稿高度雷同（≥99%）说明未做平台化改写，
                # 且"多平台同文"是微信"非真人自动化创作行为"的高危特征。
                # 注意：知乎版允许接近母稿（论证加厚），此处阈值 0.99 只拦"一字不改的复制"。
                if final_refs:
                    sim = text_similarity(extract_body_text(pf), extract_body_text(final_refs[0]))
                    if sim >= COMPLIANCE_SIMILAR_TO_FINAL:
                        issues.append(
                            f"  ❌ 平台稿与终稿高度雷同（相似度 {sim:.0%} ≥ {COMPLIANCE_SIMILAR_TO_FINAL:.0%}）："
                            f"{pf.name} 疑似未做平台化改写——必须按平台特性调整结构/语气/标题/段落，"
                            f"禁止多平台同文复制（非真人自动化创作风险）")

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

                # 平台稿正文连贯性门禁（2026-08-13 新增，教训固化）：
                # 拦截"骨架+注入终稿段落硬凑字数"式写法（2026-08-13 发生并被人工复核拦截——
                # 补字用脚本把终稿段落原样粘贴到正文末尾，正文被 --- 割裂、内容重复风格断裂）。
                # 教训再固化：平台稿必须一次性写成完整连贯文章，补字必须在对应章节内平台化扩写，
                # 禁止"骨架+尾部堆砌"。注意：本检查放在字数保真门禁之后、平台专项检查之前。
                if final_refs:
                    issues += check_platform_coherence(pf, final_refs[0])

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
                # 配图锚文本质量门禁（2026-08-14 新增，教训固化）：
                # 锚文本必须是正文中唯一出现、且位于段落首句的短句（人工 Ctrl+F 可从段首
                # 定位），禁止锚定小标题/正文搜不到的文本；表格场景允许锚表格行。
                issues += check_anchor_quality(pf)
                dir_issues += issues

            # 合规：平台版两两相似度（2026-08-11 新增）
            # 背景：多平台版本应各自改写；若两平台版高度雷同（≥85%）说明是同文复制，
            # 机器批量发布特征明显（微信/知乎/小红书风控重点），必须各自改写差异化。
            plat_texts = {}
            for pf in sorted(platform_files):
                plat_texts[pf.name] = extract_body_text(pf)
            names = sorted(plat_texts)
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = names[i], names[j]
                    sim = text_similarity(plat_texts[a], plat_texts[b])
                    if sim >= COMPLIANCE_SIMILAR_PLATFORMS:
                        dir_issues.append(
                            f"  ❌ 平台版高度雷同（相似度 {sim:.0%} ≥ {COMPLIANCE_SIMILAR_PLATFORMS:.0%}）："
                            f"{a} vs {b}——两平台版必须差异化改写（结构/语气/案例/引导不同），"
                            f"禁止同文复制（非真人自动化创作风险）")

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
