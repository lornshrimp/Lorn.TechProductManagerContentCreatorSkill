---
name: deai-daily-pipeline
description: '每日自媒体内容生产流水线总编排。使用时：需要执行完整的"热点采集→选题→3选题×9步流水线→5平台适配"日常内容生产时。本技能是 deai-hotspot/topic/research/outline/title/write/polish/review/adapt-* 系列技能的总调度器，固化执行顺序、质量门禁与历史教训。自动化任务与手动触发均可调用本技能。'
user-invocable: true
---

# `deai-daily-pipeline` — 每日内容生产流水线（总编排）

## When to Use
- 每日定时内容生产（自动化任务入口）
- 手动触发完整流水线（`@deai-daily-pipeline`）
- 需要按标准流程产出融合榜单 + 选题卡 + 3 篇多平台文章时

## Input
- 今日日期（`{今日日期}`，格式 YYYY-MM-DD）
- 工作区根目录（本项目固定）

## Output
- `hotspot/榜单/{日期}/` 各平台原始榜单 + 融合榜单
- `hotspot/选题/{日期}-选题卡.md`
- `research/{选题名}/研究报告.md` × 3
- `drafts/{选题名}/` 每个选题 12 文件（大纲/标题方案/草稿/润色稿/去AI化报告/终稿/编辑终审签报 + 5 平台版本）
- 最终回复（含打卡表、校验结果、产出清单）

---

## ⚠️ 工作质量铁律（违反即视为本次任务不达标）

本流水线是定时自动化任务，**不允许因"时间紧/图省事/默认不重要"而跳过任何可执行步骤**。每步必须真实执行并留痕，宁可慢不可漏。

## ⚠️ Skill 严格执行三层机制（2026-08-08 确立，强制）

| 层 | 时机 | 动作 |
|:--:|------|------|
| **事前** | 每步执行前 | Read 对应 skill 的 `SKILL.md` **完整文件**（重点 Output 章节与必填字段），提炼必填项清单。禁止只看主体流程 |
| **事中** | 每步产出后 | 对照该 skill Output 规范逐项自检（frontmatter 字段/必填章节/必填行），不合格不进入下一步 |
| **事后** | 全部完成后 | 运行 `python .workbuddy/scripts/规范校验.py --date {今日日期}`，❌ 项回修后重跑至 ✅ |

> 校验脚本按技能规范固化全部必填项（frontmatter/必填章节/知乎 source_label+Clickable Link/榜单链接列/成对文件/打卡表）。**skill 规范更新时须同步更新脚本**。

---

## 历史教训（沉淀，禁止再犯）

1. **采集不得默认跳过**：19 源逐源打卡，无"没试就跳过"。
2. **通道硬约束**：bsk → urllib → WebSearch。路径 404/重定向/JS 渲染/懒加载/WAF **都不是降级理由**——先找替代入口（首页/频道页）或换 evaluate/滚动；适配器 ❌ 标注也须实测确认（可能过时，如知乎想法话题实测可用）。
3. **融合=发现流量，选题=筛选定位**，两环节职责分离。政经 S 级话题（利益/连接/视角三条测试通过）按 ×1.4 流量放大参与 TOP 排序，**禁止以"科技/产品定位"压制政经权重**；C 级娱乐/气象不得因"定位契合"前置。
4. **skill 执行须完整落实 Output 元数据规范**：知乎版 source_label/source_url/Clickable Link、知乎榜单「链接」列、草稿素材溯源+质量自检、润色稿与去AI化报告成对、终稿与签报成对。

---

## Procedure

### Step 0：初始化
1. 确认今日日期 `{今日日期}`
2. 创建目录：`hotspot/榜单/{日期}/`、`hotspot/选题/`、`research/`、`drafts/`
3. Read 本技能 Step 4-10 对应子技能时，遵循三层机制的事前要求

### Step 1：热点采集（deai-hotspot）
Read `.workbuddy/skills/deai-hotspot/SKILL.md` 完整规范 + `references/adapter-bsk.md` 手册，按「章节 0 采集通道优先级」执行：

**通道优先级**：① bsk 浏览器（`bsk doctor -v` → `bsk session start` → navigate/snapshot/get-html/evaluate → **必须 `bsk session stop`**）；② Python urllib 直连 SSR 源；③ WebSearch 兜底。

**19 源全量打卡**（每个源至少尝试一次）：
微博热搜榜、百度热搜榜、知乎问题热榜、知乎推荐问题、知乎邀请问题、头条热榜、B站热门、抖音热点、百度指数、知微事见、IT之家热榜、澎湃新闻热榜、网易新闻热点排行、InfoQ中国热点、虎嗅48h热文、品玩一周精选、知乎想法话题、知乎想法热榜。

**各源 bsk 实测采集要点（2026-08-08 验证）**：
- 知乎系（热榜/推荐/邀请/想法话题）：登录态 navigate + evaluate 提取
- 微博：登录态，get-html 落盘 `$TEMP` + Python 正则解析（Git Bash `/tmp` 与 Windows Python 不互通，用 `$TEMP` + cygpath）
- 抖音：navigate 超时但页面就绪，直接 evaluate 提取（含热度值）
- B站：用 `/ranking` 路径（`/v/popular/rank/all` 被 CDP 拒绝）
- 网易/澎湃/IT之家：rank/hotList 路径已改版 → **改采首页**（evaluate 提取）
- 头条：/hot 404 → 改采热点频道 `?channel=hot`
- 虎嗅/InfoQ/品玩：JS 渲染 → 滚动 + evaluate 提取
- 知微：navigate 50s 可加载，evaluate 提取事件榜+影响力指数

**输出规范**：
- 每个采集成功的源 → `hotspot/榜单/{日期}/{来源}.md`（YAML frontmatter: title/date/source/collectTime）
- **知乎类榜单必须含「链接」列**：`[去回答](https://www.zhihu.com/question/{id})`
- 融合榜单 → `hotspot/榜单/{日期}/融合榜单.md`：
  - YAML sources 与打卡表 ✅ 源一一对应
  - TOP20 含"级别"列（S 政经/A 科技/B 交叉/C 娱乐）
  - **S 级政经按 ×1.4 放大参与排序，禁止定位压制**
  - 含 19 源「采集打卡表」（✅/⚠️+原因/❌+原因）

### Step 2：选题（deai-topic）
Read `.workbuddy/skills/deai-topic/SKILL.md` 完整规范，产出 `hotspot/选题/{日期}-选题卡.md`：
- 五维评分模型 v2.5 + 优先级公式
- **必须优先纳入 S 级政经话题**（外贸/关税/新基建/供应链/政策，×1.4 后封顶 10 分，应占主选题多数）
- 选定排名前 3 为今日主选题 A、B、C（按最终分降序）

### Step 3-9：对主选题 A/B/C 逐一执行（3 轮完整流水线）

每轮对单一选题执行 7 个子步骤，产出落位 `drafts/{选题名}/`：

| 步 | 技能 | 产出文件（必含） |
|:--:|------|-----------------|
| 3 | deai-research | `research/{选题名}/研究报告.md`（frontmatter: type/date/topic/depth/model） |
| 4 | deai-outline | `drafts/{选题名}/大纲.md`（必含段落骨架/标题策略章节） |
| 5 | deai-title | `drafts/{选题名}/标题方案.md`（必含候选池/六维评分表/平台适配建议） |
| 6 | deai-write | `drafts/{选题名}/草稿-*.md`（必含素材溯源表+质量自检报告+标题决策说明） |
| 7 | deai-polish | `润色稿-*.md` + `去AI化报告-*.md`（成对） |
| 8 | deai-review | `终稿-*.md` + `编辑终审签报-*.md`（成对，不通过则回炉） |
| 9 | 5 平台适配 | 知乎/微信/百家号/CSDN/头条 5 版本 |

### Step 9 细化：5 平台适配 Output 规范（强制）

**知乎版（deai-adapt-zhihu）**：
- frontmatter 必含 `source_label`（邀请问题#N / 推荐问题#N / 热榜#N / 独立文章）+ `source_url`
- source_url 从当日知乎问题榜单提取（三来源：热榜/推荐/邀请；**无匹配才标"独立文章"且 source_url 留空**）
- source_url 非空时，正文前追加 Clickable Link 行：`[→ 去回答该问题](url)`

**微信版（deai-adapt-wechat）**：封面图 AI 提示词 + 内容简介 + 互动引导（在看/留言/关注）

**百家号版（deai-adapt-baiduhao）**：SEO 搜索关键词 + 开头直接给答案

**CSDN 版（deai-adapt-csdn）**：结构化排版（H2/H3/表格）+ 方法论/技术内容

**头条版（deai-adapt-toutiao）**：短段落（每段 ≤3 句）+ 结尾关注引导

### Step 10：规范校验门禁（强制，不可跳过）

```bash
python .workbuddy/scripts/规范校验.py --date {今日日期}
```

- ✅ 全部通过 → 进入 Step 11
- 存在 ❌ → 逐项回修后重跑，直到 ✅

**⚠️ 字数实测铁律（2026-08-08 教训固化，禁止再犯）**：
1. **字数必须实测，禁止估算**——草稿/润色稿/终稿产出后，必须在终端运行字数统计（正文中文字符数，排除 frontmatter/素材溯源/质量自检等附属区），禁止写"约 XX 字"。
2. **体裁底线硬性**：深度分析体 ≥2500、观点评论体 ≥1500、清单体 ≥1500、快讯评点体 ≥500、故事体 ≥1500、问题解决体 ≥800。不足即 ❌，**不得以"内容完整可接受"等理由放松标准放行**。
3. **脚本门禁已内置字数检查**：`规范校验.py` 会按大纲 genre 自动实测草稿/润色稿/终稿字数，不足即报 ❌——这是最后一道硬闸，任何估算或宽松判定都会被它拦截。

**⚠️ 校验脚本维护红线（2026-08-08 教训固化）**：规范校验.py 曾存在 4 处缺陷导致"全部通过"假阳性（root 路径解析错误→校验从未真正执行；source_label 被 clickable 分支短路；prefix 变量遮蔽；平台版章节用标题名匹配误报）。**校验脚本修改后必须用已知不达标样例验证其能报 ❌**，禁止只看"输出 ✅"就认为机制有效。

### Step 11：最终回复

列出：
1. 融合榜单路径
2. 选题卡路径
3. 采集打卡表（19 源全量）
4. 规范校验结果
5. 3 个主选题（A/B/C，注明级别与政经/科技类型）
6. 每个选题产出文件清单（含 5 平台版本路径）与一句话要点
7. 登录态缺失等降级原因（如有）

---

## Calling Examples

```text
@deai-daily-pipeline                   执行今日完整流水线
@deai-daily-pipeline --date 2026-08-08 指定日期执行
```

## Reference
- 子技能：deai-hotspot / deai-topic / deai-research / deai-outline / deai-title / deai-write / deai-polish / deai-review / deai-adapt-zhihu / deai-adapt-wechat / deai-adapt-baiduhao / deai-adapt-csdn / deai-adapt-toutiao
- 校验脚本：`.workbuddy/scripts/规范校验.py`
- bsk 手册：`.workbuddy/skills/deai-hotspot/references/adapter-bsk.md`
