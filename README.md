# 🦐 产品经理独孤虾 · 自媒体内容生产工作流

> **写一个时代的观察者，不是写一个时代的复读机。**

基于 VS Code + GitHub Copilot 的自媒体内容全自动生产工作流。身份是"产品经理独孤虾"——20 年互联网产品人，写行业观察、产品方法论、职场经验和商业洞察。

## 项目概述

这不是一个"AI 自动写文章"的项目。这是一个**AI 辅助、人类主导**的半自动化内容生产工作流。它把自媒体的"选题→研究→写作→润色→审核→分发"全链路拆解为 10 个标准化 Skill，每个 Skill 负责一个明确的工序。

**核心理念**：
- **去 AI 化优先**：产出的文章必须读起来像人写的，不是 AI 生成的
- **事实驱动**：研究先行，用真实数据支撑观点
- **人设一致**：20 年 PM 经历是最大的差异化——AI 可以模仿语气，但模仿不了真实的履历和经历
- **爆款可预测**：情绪价值、信息差、社交货币是可量化评估的

## 快速开始

### 前提条件

- VS Code + GitHub Copilot（Chat 扩展）
- Python 3.10+（研究路径深度依赖）
- 浏览器（热点采集需要）

### 使用

在 VS Code 中打开项目，在 Copilot Chat 中调用 Skill：

```text
# 完整生产链路
@deai-hotspot                  # 1. 采集热点
@deai-topic                    # 2. 分析选题
@deai-research                 # 3. 深度研究
@deai-outline                  # 4. 生成大纲
@deai-title                    # 5. 设计标题
@deai-write                    # 6. 撰写全文
@deai-polish                   # 7. 去 AI 化润色
@deai-review                   # 8. 质量门禁
@deai-adapt-*                  # 9. 平台改写
@deai-publish                  # 10. 平台发布
```

## 项目结构

```
.
├── .github/
│   ├── copilot-instructions.md       # 全局指令
│   ├── instructions/                 # 人设基线
│   │   └── persona-product-manager-shrimp.instructions.md
│   └── skills/                       # 核心 Skill 集合
│       ├── deai-hotspot/             # 热点采集（18个平台）
│       ├── deai-topic/               # 选题分析（v2.3）
│       ├── deai-research/            # 深度研究（L1/L2/L3）
│       ├── deai-outline/             # 大纲生成（6种体裁）
│       ├── deai-title/               # 标题设计（v2.1）
│       ├── deai-write/               # 文章撰写（v2.1）
│       ├── deai-polish/              # 去AI化润色（4子技能）
│       ├── deai-review/              # 质量门禁+爆款预判
│       ├── deai-adapt-*/             # 多平台改写（知乎/公众号/头条等）
│       └── deai-publish/             # 平台分发
├── hotspot/                          # 热点数据
│   ├── 榜单/{日期}/{来源}.md         # 各平台原始榜单
│   └── 选题/{日期}-选题卡.md         # 选题分析卡
├── research/{选题名}/                # 研究报告
├── drafts/{日期}/{选题名}/            # 文章产物（草稿/润色稿/终稿/签报，按日期分层）
├── notebook/                         # 个人灵感笔记
├── my-articles/                      # 个人文章库
├── published/                        # 发布记录
└── resume.md                         # 个人简历
```

## 10 个核心 Skill

| # | Skill | 输入 | 输出 | 一句话职责 |
| :---: | :---: | :---: | :---: | :-----------: |
| 1 | **deai-hotspot** | 多平台 URL | 融合榜单 | 采集 18 个平台热点，跨来源去重排序 |
| 2 | **deai-topic** | 融合榜单 | 选题卡 | 四级分类 + 5 维评分 + 情绪驱动力 + 二创空间 |
| 3 | **deai-research** | 选题卡 | 研究报告 | 6 维标准研究 / 深度对比研究，信源评级 |
| 4 | **deai-outline** | 选题卡 + 报告 | 大纲 | 6 种体裁 + 金句植入 + 转发触发器 + 情绪曲线 |
| 5 | **deai-title** | 大纲 | 标题方案 | 7 种标题类型 + 6 维评分 + 情绪→标题映射 |
| 6 | **deai-write** | 大纲 + 报告 | 草稿 | 段落执行引擎 + 金句规则 + 情绪曲线兑现 |
| 7 | **deai-polish** | 草稿 | 润色稿 + 去AI化报告 | 4 子技能流水线去 AI 味 |
| 8 | **deai-review** | 润色稿 + 报告 | 终稿 + 编辑签报 | 质量门禁 + 爆款指数（打开/完读/转发/互动） |
| 9 | **deai-adapt-\*** | 终稿 | 平台改写版 | 知乎/公众号/头条/百家号/CSDN 等适配 |
| 10 | **deai-publish** | 改写版 | 发布记录 | 手动 / 半自动平台发布 |

### Skill 亮点

#### deai-topic（选题分析 v2.3）

- **四级话题分类**：S 级（政经引流）/ A 级（核心领域）/ B 级（交叉拓展）/ C 级（排除）
- **政经三条测试**：利益测试 / 连接测试 / 视角测试
- **情绪驱动力标签**：焦虑/愤怒/好奇/共鸣/希望/优越感 → 绑定标题和平台策略
- **话题生命周期**：萌芽/爆发/成熟/衰退 → 判断最佳写作时机
- **二创空间评估**：一个选题能写几篇文章？

#### deai-review（质量门禁 v2.2）

- **爆款指数四维评估**：打开力(20%) + 完读力(25%) + 转发力(30%) + 互动力(15%)
- **五级判定**：通过 / 微调发布 / 爆款优化(新增) / 需修改 / 驳回

#### deai-title（标题设计 v2.1）

- **情绪→标题公式映射**：选题卡的情绪标签直接决定标题策略
- **标题→开头兑现检查**：标题承诺的，正文开头 150 字必须兑现
- **6 种 AI 味模式检测**：生成时即刻过滤

## 去 AI 化体系

本项目最独特的部分是**去 AI 化体系**——确保 AI 辅助产出的文章读起来不像 AI 写的。这不是"写完后检查一遍"，而是贯穿全链路的内置约束：

| 工序 | 去 AI 化方式 |
| :----: | :------------ |
| deai-topic | 禁用 AI 味选题方向（"数字化赋能"类话题直接过滤） |
| deai-outline | 用个人风格指纹覆盖模板默认值 |
| deai-write | 三层质量体系（词汇 / 句式 / 人味儿）+ 人话转换表 |
| deai-polish | 4 子技能流水线：humanizer-zh → stop-slop → taste-skill → shuorenhua |
| deai-review | 6 种 AI 味残留模式检测 + 三条铁律终审 |

## 数据生产链路

```
deai-hotspot                              deai-topic
  ↓ 18 个平台热点采集                        ↓ 四级分类 + 5 维评分
deai-topic                                deai-research
  ↓ 输出选题卡                               ↓ 6 维研究 + 信源评级
deai-research                             deai-outline
  ↓ 输出研究报告                             ↓ 段落骨架 + 金句地图
deai-outline                              deai-write
  ↓ 输出大纲                                 ↓ 执行引擎 + 人话转换
deai-title                                deai-polish
  ↓ 输出标题方案                             ↓ 4 子技能流水线去AI味
deai-write                                deai-review
  ↓ 输出草稿                                 ↓ 质量门禁 + 爆款预判
deai-polish                               deai-adapt-*
  ↓ 输出润色稿 + 去AI化报告                   ↓ 多平台改写
deai-review                               deai-publish
  ↓ 输出终稿 + 编辑签报                       ↓ 发布 + 记录
deai-adapt-*
  ↓ 输出各平台版本
deai-publish
```

## 隐私说明

以下目录包含个人隐私数据，已加入 `.gitignore`，**不会提交到 GitHub**：

| 目录 | 内容 | 用途 |
| :----: | :---- | :----- |
| `notebook/` | 个人灵感笔记 | 行业观察、踩坑记录、类比吐槽 |
| `my-articles/` | 个人文章库 | 手动写的文章，提取风格指纹 |
| `resume.md` | 真实简历 | 公司名、项目名、数字成果 |
| `drafts/` | 文章稿 | 草稿/润色稿/终稿 |
| `published/` | 发布记录 | 账号信息和发布凭证 |

即使 Fork 或克隆，这些目录在你的副本中保持为空。

## 技术栈

| 组件 | 技术 |
| :---: | :------: |
| 编辑器 | VS Code |
| AI 助手 | GitHub Copilot（Chat + Agent） |
| 浏览器自动化 | Playwright |
| 深度研究 | Python + YAML + JSON |
| 版本控制 | Git + GitHub |

## 许可证

MIT License — 详见 [LICENSE](LICENSE)

---

> 关于"产品经理独孤虾"：20 年互联网从业者，曾就职于优酷、百度、苏宁、京东等公司。做过广告营销平台、AI 策略中台、增长产品。现在用 AI 辅助写作，但坚持"写自己真正想写的东西"。
