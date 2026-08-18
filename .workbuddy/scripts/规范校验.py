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
# 2026-08-16 升级（deai-title 优化研究报告 P0）：
# ① 候选池数量门槛从 ≥5 提升至 ≥12（快讯评点体豁免 ≥8）——对齐 skill Step 3 "12-18 个"；
# ② 新增平台标题溯源检查：平台适配表首选/备选标题必须能在候选池中找到（相似度 ≥0.90），
#    禁止平台适配环节临时新造标题（抽查发现 CSDN 首选标题脱离候选池、绕过六维评分）。
TITLE_CHECKS = {
    "候选池": "必须含「候选池」章节（≥12 个候选；快讯评点体 ≥8）",
    "评分表": "必须含「评分表」或「六维评分」章节",
    "平台适配": "必须含「平台适配」章节（各平台首选标题）",
}

# 标题方案：候选池数量底线（2026-08-16 新增，对齐 skill Step 3 "12-18 个"）
TITLE_CANDIDATE_MIN = 12
TITLE_CANDIDATE_MIN_BREAKING_NEWS = 8   # 快讯评点体候选空间小，豁免底线
# 平台适配标题溯源：与候选池相似度低于该阈值视为"新造标题"（平台标题必须来自候选池 Top5）
TITLE_TRACE_SIMILARITY = 0.90
# deai-title v2.2 生效日期：该日期及之后的标题方案强制候选池数量/平台标题溯源检查
# （v2.2 前历史产出按旧规范执行——平台标题=候选池改写，溯源检查会大量误报，不强制）
TITLE_V22_EFFECTIVE_DATE = "2026-08-16"

# 平台标题字数合规区间（2026-08-16 新增，对应 deai-title v2.2 Step 5 平台字数表）：
# 平台适配后的标题字数必须落在平台区间内（超限在移动端截断=信息丢失）。
# 数据来源：2025-2026 各平台标题规范交叉验证（skill Step 5 已固化）。
# 注意：仅对"平台适配章节中的实际标题"做检查——v2.1 历史产出（推荐标题+理由列）兼容跳过。
PLATFORM_TITLE_LEN = {
    "知乎": (15, 35),
    "公众号": (15, 25),
    "微信": (15, 25),
    "头条": (18, 25),
    "小红书": (1, 20),
    "百家号": (20, 30),
    "视频号": (1, 15),
    "CSDN": (1, 60),
    "掘金": (1, 60),
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
    """配图锚文本质量门禁（2026-08-14 新增，2026-08-18 修订语义）。

    背景：2026-08-14 用户复核指出——平台稿配图锚文本不是段落首句，人工 Ctrl+F
    定位困难。当日核查 15 稿 24 锚点：9 处锚文本在正文完全搜不到（指向小标题/
    笔误），3 处出现在段落第二句（人工需先找到段再往下一句看）。

    门禁规则（每个 [配图N] 的锚文本必须）：
    ① 在正文区（配图区前）唯一出现（出现次数 == 1，避免多匹配）
    ② 位于"一眼可见"位置之一：所在段落首句（锚文本前是段落边界），或 markdown
       小标题行（## / ###，2026-08-18 修订：小标题作锚合法——同样 Ctrl+F 好定位，
       废止 08-14 "禁止小标题作锚" 旧规），或表格行（如 "| 计费项"）。三者之外的
       （藏在段落正文中间的一句/半句）判违规——人工定位难。
    ③ 配图搜索替换指令区包含该锚文本（「锚」格式）
    """
    issues = []
    try:
        c = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return issues
    # 提取所有锚文本（2026-08-18 修复：兼容「锚文本：xxx」与「锚文本定位：**xxx**」两种产出格式）
    # 历史 bug：仅按 "锚文本定位"+** 提取，而实际产出多为 「锚文本：xxx」，导致 anchors 为空 →
    # if not anchors: return issues → 静默跳过质量门禁（假阴性），锚文本非段首问题长期漏检。
    anchors = []
    for line in c.split("\n"):
        ls = line.strip()
        # 仅处理「锚文本：」/「锚文本:」前缀行（配图详情区）；排除配图搜索替换指令区
        # （含「在正文找到唯一锚文本」「插入 [配图」等）与「## 配图搜索替换指令」标题行
        if not ls.startswith("锚文本"):
            continue
        if "在正文找到唯一锚文本" in ls or "之后的段落后" in ls or "插入 [" in ls:
            continue
        val = re.sub(r"^锚文本\s*[:：]", "", ls).strip()
        a = val.strip('"').strip("'").strip("#").strip()
        if a and not a.startswith("[配图") and "锚文本" not in a:
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
        # 小标题作锚例外（2026-08-18 修订，废止"禁止小标题作锚"旧规）：
        # 锚文本若为 markdown 小标题行（## / ###）文本，同样一眼可见、Ctrl+F 好定位，视为合法。
        # 判定：取锚文本 pos 所在行，去除行首空白与 # 标记后，若锚文本构成该行主体则判为小标题作锚。
        is_heading = False
        ls = body.rfind("\n", 0, pos)
        le = body.find("\n", pos)
        anchor_line = body[ls + 1: le if le != -1 else len(body)]
        anchor_stripped = anchor_line.strip()
        if anchor_stripped.startswith("#"):
            hl_clean = anchor_stripped.lstrip("#").strip()
            a_clean = a.strip()
            if a_clean in hl_clean or hl_clean in a_clean:
                is_heading = True
        if not (is_start or is_table or is_heading):
            issues.append(f"  ❌ 配图锚文本藏在段落中间: 「{a}」——既不取该段第一句也算不上小标题，人工 Ctrl+F 定位难（应锚段落首句或小标题）")
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


def extract_title_candidates(path: Path) -> list:
    """从标题方案「候选池」章节提取候选标题列表（纯文本，去 markdown 标记）。

    兼容两种格式（deai-title 历史与现行输出均覆盖）：
    A. 表格格式：| # | 标题 | 类型 | → 取第二列
    B. 分节列表格式：
        ### 反直觉式（4 个）
        1. 标题一 [大纲种子]
        2. 标题二
    章节边界：下一个 H2（## 开头）为止；候选池内部的 ### 小节不算边界。"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    # 定位「候选池」章节（H2 级："## 三、标题候选池（共 N 个）" 等变体）。
    # 必须限定 ^#{2,4} 避免误匹配 H1 主标题（如"# 标题方案 · xxx候选池xxx"）。
    m = re.search(r"^#{2,4}\s*.*候选池.*$", text, re.MULTILINE)
    if not m:
        return []
    start = m.end()
    # 边界：下一个 H2（## 后不跟 #），避免 ### 小节标题截断内容
    nxt = re.search(r"^##(?!#)\s+", text[start:], re.MULTILINE)
    seg = text[start: start + nxt.start()] if nxt else text[start:]
    titles = []
    for line in seg.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("|"):
            # 跳过表格分隔行（|------|----------|）
            if re.fullmatch(r"\|[\s:\-|]+\|", line):
                continue
            # 表格行：取第二列（标题列）
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            first, second = cells[0], cells[1]
            # 跳过表头与分隔行
            if first in ("#", "序号", "排名", "编号") or re.fullmatch(r":?-+:?", first):
                continue
            if second in ("标题", "") or re.fullmatch(r":?-+:?", second):
                continue
            t = second
        else:
            # 分节列表格式：跳过小节标题（### xxx）与普通描述行
            if line.startswith("#"):
                continue
            if re.match(r"^[#>\-*]\s", line) or line.startswith((">", "```")):
                continue
            t = re.sub(r"^(\d+[\.、]|[-*])\s*", "", line)
            # 跳过非标题行（不含任何中文字符且不以数字开头的内容）
            if not re.search(r"[\u4e00-\u9fff]", t):
                continue
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)  # 去 markdown 链接保留文字
        # 去候选标注（[大纲种子] [知识库公式] 等）
        t = re.sub(r"\s*\[[^\]]*\]\s*$", "", t)
        t = t.strip().strip("*`").strip()
        if t and t not in titles:
            titles.append(t)
    return titles


def check_title_candidate_count(path: Path, min_count: int) -> list:
    """候选池数量门禁（2026-08-16 新增，对齐 skill Step 3 "12-18 个"）。

    背景：skill 要求生成 12-18 个候选，但旧校验只查"候选池章节存在"（TITLE_CHECKS 候选池项），
    抽查 2026-08-15 产出发现候选池仅 10 个仍通过校验——规范与校验脱节。
    修正：实测候选池标题数量，少于底线即 ❌（不依赖模型自查，代码硬校验）。
    注意：快讯评点体候选空间小，由调用方传 min_count=8。"""
    issues = []
    titles = extract_title_candidates(path)
    n = len(titles)
    if n < min_count:
        issues.append(
            f"  ❌ 标题候选池数量不足: 实测 {n} 个 < {min_count} 个"
            f"（deai-title Step 3 要求 12-18 个；快讯评点体 ≥8）——"
            f"候选池是六维评分的输入，数量不足会压缩 Top 选择空间，必须补齐")
    return issues


def check_platform_title_trace(path: Path) -> list:
    """平台适配标题溯源门禁（2026-08-16 新增，deai-title 优化研究报告 P0）。

    背景：抽查 2026-08-15「存储荒警报」标题方案发现——CSDN 首选标题
    「存储荒是真的吗？拆解涨价传导链」不在候选池 10 个标题中，是平台适配环节
    临时新造的，未经过六维评分。绕过评分的标题可能 AI 味超标/字数违规/与内容不符。

    门禁规则：平台适配章节表格中每个平台的标题列，必须能在候选池中找到。
    兼容两种表格格式：
    A. v2.2 规范格式：| 平台 | 首选标题 | 备选标题 |（两列标题都要检查）
    B. v2.1 实际格式：| 平台 | 推荐标题 | 理由 |（推荐标题检查，理由列不检查）
    标题单元格兼容 #N 编号引用（"#2 标题"、"Top 1 标题"、"#5"、"（同微信标题）"
    等历史写法）——先尝试定位候选池对应编号标题，定位成功即视为可溯源。
    """
    issues = []
    candidates = extract_title_candidates(path)
    if not candidates:
        return issues  # 候选池为空由 check_title_candidate_count 兜底
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^#{2,4}\s*.*平台适配.*$", text, re.MULTILINE)
    if not m:
        return issues  # 章节缺失由 check_section 兜底
    start = m.end()
    # 边界：下一个 H2（## 后不跟 #），避免 ### 小节标题截断
    nxt = re.search(r"^##(?!#)\s+", text[start:], re.MULTILINE)
    seg = text[start: start + nxt.start()] if nxt else text[start:]
    lines = [ln.strip() for ln in seg.split("\n") if ln.strip()]
    # 识别表头列含义：第二/三列表头名决定哪些列是标题列
    col_is_title = [False, False, False]
    for ln in lines:
        if not ln.startswith("|"):
            continue
        if re.fullmatch(r"\|[\s:\-|]+\|", ln):
            continue
        cells = [c.strip().strip("*`").strip() for c in ln.strip("|").split("|")]
        if len(cells) >= 3 and cells[0] in ("平台", "序号", "排名", "平台名称"):
            for idx, h in ((1, cells[1]), (2, cells[2] if len(cells) > 2 else "")):
                if h in ("首选标题", "备选标题", "标题", "推荐标题", "首选", "备选"):
                    col_is_title[idx] = True
            break
    # 若未识别到标准表头（历史异常格式），默认检查第 2 列（col 1）
    if not any(col_is_title):
        col_is_title[1] = True
    for ln in lines:
        if not ln.startswith("|"):
            continue
        if re.fullmatch(r"\|[\s:\-|]+\|", ln):
            continue
        cells = [c.strip().strip("*`").strip() for c in ln.strip("|").split("|")]
        if len(cells) < 3:
            continue
        platform = cells[0]
        if platform in ("平台", "序号", "排名", "平台名称") or not platform:
            continue
        for idx, cell in ((1, cells[1]), (2, cells[2] if len(cells) > 2 else "")):
            if not col_is_title[idx] or not cell:
                continue
            if cell in ("首选标题", "备选标题", "标题", "推荐标题", "首选", "备选"):
                continue
            t_clean = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell).strip()
            # 提取 #N / Top N / ① 编号引用 → 直接定位候选池对应编号
            num = None
            mm = re.match(r"^(?:#|Top\s*|top\s*|第)?\s*(\d{1,3})\s*[#、.．:：)]?", t_clean)
            if mm:
                num = int(mm.group(1))
            if num and 1 <= num <= len(candidates):
                continue  # 编号引用候选池对应标题，视为可溯源
            # 无编号：与候选池逐条比对（允许平台化微调，阈值 0.90）
            t_clean = t_clean.strip().strip('"\'“”‘’「」『』*`').strip()
            if not t_clean or t_clean in ("（同微信标题）", "同微信标题", "同头条标题"):
                continue
            best = 0.0
            for c in candidates:
                s = text_similarity(t_clean, c)
                if s > best:
                    best = s
            if best < TITLE_TRACE_SIMILARITY:
                issues.append(
                    f"  ❌ 平台适配标题未在候选池: {platform} 标题「{t_clean}」"
                    f"（与候选池最高相似度 {best:.0%} < {TITLE_TRACE_SIMILARITY:.0%}）"
                    f"——平台标题必须从候选池 Top5 中选取，禁止平台适配环节新造标题"
                    f"（新造标题未经过六维评分，AI 味/字数/内容一致性均无保障）")
    return issues


def check_platform_title_length(path: Path) -> list:
    """平台标题字数合规门禁（2026-08-16 新增，对应 deai-title v2.2 Step 5 平台字数表）。

    背景：skill 全局约束"每个标题 ≤30 字"一刀切，不适用于小红书（硬上限 20 字）
    与视频号（8-15 字）；平台适配后超限会在移动端截断，关键信息丢失。
    数据来源：2025-2026 各平台标题规范交叉验证（小红书 10-20/头条 18-25/公众号 15-25 等）。

    检查方式：平台适配表格中每个平台行的标题，中文字符数必须在 PLATFORM_TITLE_LEN
    对应区间内（平台名含"小红书"等关键词匹配；v2.1 的"推荐标题+理由"三列格式只查
    推荐标题列——理由列本来就是说明文字，不查）。"""
    issues = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^#{2,4}\s*.*平台适配.*$", text, re.MULTILINE)
    if not m:
        return issues  # 章节缺失由 check_section 兜底
    start = m.end()
    nxt = re.search(r"^##(?!#)\s+", text[start:], re.MULTILINE)
    seg = text[start: start + nxt.start()] if nxt else text[start:]
    lines = [ln.strip() for ln in seg.split("\n") if ln.strip()]
    col_is_title = [False, False, False]
    for ln in lines:
        if not ln.startswith("|") or re.fullmatch(r"\|[\s:\-|]+\|", ln):
            continue
        cells = [c.strip().strip("*`").strip() for c in ln.strip("|").split("|")]
        if len(cells) >= 2 and cells[0] in ("平台", "序号", "排名", "平台名称"):
            for idx, h in ((1, cells[1]), (2, cells[2] if len(cells) > 2 else "")):
                if h in ("首选标题", "备选标题", "标题", "推荐标题", "首选", "备选"):
                    col_is_title[idx] = True
            break
    if not any(col_is_title):
        col_is_title[1] = True
    for ln in lines:
        if not ln.startswith("|") or re.fullmatch(r"\|[\s:\-|]+\|", ln):
            continue
        cells = [c.strip().strip("*`").strip() for c in ln.strip("|").split("|")]
        if len(cells) < 2:
            continue
        platform = cells[0]
        if platform in ("平台", "序号", "排名", "平台名称") or not platform:
            continue
        # 定位平台对应字数区间（按关键词匹配：公众号/微信、小红书、视频号等）
        plen = None
        for pk, (lo, hi) in PLATFORM_TITLE_LEN.items():
            if pk in platform or platform in pk:
                plen = (lo, hi)
                break
        if not plen:
            continue  # 未识别平台（如"CSDN/掘金"含 CSDN 可识别；未知平台跳过）
        for idx, cell in ((1, cells[1]), (2, cells[2] if len(cells) > 2 else "")):
            if not col_is_title[idx] or not cell:
                continue
            if cell in ("首选标题", "备选标题", "标题", "推荐标题", "首选", "备选"):
                continue
            t_clean = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
            t_clean = t_clean.strip().strip("*`\"'“”‘’「」『』").strip()
            if not t_clean or t_clean.startswith("#") and re.match(r"^#?\d+", t_clean):
                continue  # #N 编号引用不是实际标题，跳过
            if t_clean in ("（同微信标题）", "同微信标题", "同头条标题"):
                continue
            n = len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", t_clean))
            lo, hi = plen
            if n > hi:
                issues.append(
                    f"  ❌ 平台标题超字数: {platform} 标题「{t_clean}」{n} 字"
                    f" > {hi} 字（{pk} 移动端展示上限）——超限会截断丢失信息，"
                    f"须按 deai-title Step 5 平台字数收缩规则压缩（删虚词/换语序/换更短候选）")
            elif n < lo:
                issues.append(
                    f"  ⚠️ 平台标题过短: {platform} 标题「{t_clean}」{n} 字"
                    f" < {lo} 字（{pk} 建议下限）——信息密度不足，降低点击动机")
    return issues


PLATFORM_TITLE_SIM = 0.85  # 平台标题两两相似度 ≥85% → 标题未差异化（2026-08-18 新增）


def check_platform_title_diversity(platform_files: list, final_file=None) -> list:
    """平台标题差异化门禁（2026-08-18 新增，教训固化）。

    背景：用户复核发现各平台版本文章标题高度雷同（母稿标题被多个平台整体复用），
    导致读者/算法判定为"同文多平台转载"，损害各平台原创权重与单位点击效率。
    根因：adapt 阶段回退到"排名第 1 标题"，且 deai-title 平台适配常共用同一候选。

    门禁：同一选题目录下各平台稿标题必须互不相同（相似度 < 阈值），且不得与母稿
    终稿标题完全相同（相似度 < 阈值）。差异化通过"换候选名次 + 平台化改造"实现，
    不得删改正文保真（各平台正文保真比例由 PLATFORM_MIN_RATIO 门禁另行校验）。
    """
    issues = []
    if not platform_files:
        return issues
    titles = {}  # filename -> title
    for pf in platform_files:
        pf_text = pf.read_text(encoding="utf-8", errors="ignore")
        try:
            fm, _ = parse_yaml_frontmatter(pf_text)
        except Exception:
            fm = {}
        title = (fm.get("title") or "").strip()
        # 优先取 frontmatter 之后第一个 H1（真实展示标题）；frontmatter title 若含
        # "平台前缀-..."（如"CSDN-xxx"）则不视为真实标题，回退取 H1。
        h1 = re.search(r"^#\s+(.+)$", pf_text, re.MULTILINE)
        h1_title = h1.group(1).strip() if h1 else ""
        if h1_title and (not title or title.startswith("CSDN-") or title.startswith("知乎-")
                         or title.startswith("微信-") or title.startswith("百家号-")
                         or title.startswith("头条-") or title.startswith("小红书-")
                         or title.startswith("视频号-")):
            title = h1_title
        titles[pf.name] = title

    named = {n: t for n, t in titles.items() if t}

    # 平台标题与母稿终稿标题判重（禁止整体复用母稿标题）
    if final_file is not None and final_file.exists():
        ftext = final_file.read_text(encoding="utf-8", errors="ignore")
        try:
            f_fm, _ = parse_yaml_frontmatter(ftext)
        except Exception:
            f_fm = {}
        final_title = (f_fm.get("title") or "").strip()
        if final_title:
            for name, t in named.items():
                s = text_similarity(t, final_title)
                if s >= PLATFORM_TITLE_SIM:
                    issues.append(
                        f"  ❌ 平台标题与母稿雷同（相似度 {s:.0%} ≥ {PLATFORM_TITLE_SIM:.0%}）："
                        f"{name} 标题「{t}」与终稿标题「{final_title}」一致——必须按平台类型"
                        f"差异化改造（知乎提问式 / 公众号\"我\"叙事 / 头条数字冲突 / 百家号搜索词 / CSDN方法论）")

    # 平台标题两两判重（禁止各平台整体复用同一标题）
    names = sorted(named)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            s = text_similarity(named[a], named[b])
            if s >= PLATFORM_TITLE_SIM:
                issues.append(
                    f"  ❌ 平台标题高度雷同（相似度 {s:.0%} ≥ {PLATFORM_TITLE_SIM:.0%}）："
                    f"{a}「{named[a]}」vs {b}「{named[b]}」——各平台必须依据平台特点选用"
                    f"差异化标题（不同候选名次 + 平台化改造），禁止整体复用同一标题")
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
                # 新检查生效门槛（2026-08-16）：候选池数量/平台标题溯源是 deai-title v2.2 规范，
                # 对 v2.2 之前的历史产出不强制（旧版允许平台标题=候选池改写，溯源必大量误报）。
                _tfm, _ = parse_yaml_frontmatter(title_f.read_text(encoding="utf-8", errors="ignore"))
                _tdate = (_tfm.get("date") or "").strip()
                _v22 = _tdate >= TITLE_V22_EFFECTIVE_DATE if _tdate else False
                if _v22:
                    # 候选池数量门禁（2026-08-16 新增）：对齐 skill Step 3 "12-18 个"；
                    # 快讯评点体候选空间小，底线降至 8。体裁从大纲 frontmatter 读取。
                    title_genre = "深度分析体"
                    if outline.exists():
                        _ot = outline.read_text(encoding="utf-8", errors="ignore")
                        _ofm, _ = parse_yaml_frontmatter(_ot)
                        title_genre = (_ofm.get("genre") or "深度分析体").strip() or "深度分析体"
                    tmin = TITLE_CANDIDATE_MIN_BREAKING_NEWS if title_genre == "快讯评点体" else TITLE_CANDIDATE_MIN
                    issues += check_title_candidate_count(title_f, tmin)
                    # 平台适配标题溯源门禁（2026-08-16 新增）：平台标题必须来自候选池 Top5，
                    # 禁止平台适配环节新造标题（绕过六维评分）。
                    issues += check_platform_title_trace(title_f)
                    # 平台标题字数合规门禁（2026-08-16 新增）：平台适配后标题须落在平台字数区间。
                    issues += check_platform_title_length(title_f)
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

            # 平台标题差异化门禁（2026-08-18 新增）：各平台稿标题须互不相同且不同于母稿标题
            dir_issues += check_platform_title_diversity(platform_files,
                                                          final_refs[0] if final_refs else None)

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
