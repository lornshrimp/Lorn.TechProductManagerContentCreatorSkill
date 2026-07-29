---
name: deai-hotspot
description: '从多个平台采集热点话题（微博、百度、知乎问题热榜、知乎推荐问题、知乎邀请问题、知乎想法话题、头条、B站、抖音、百度指数、知微事见、IT之家、澎湃新闻、网易新闻、InfoQ中国、虎嗅、品玩）。使用时：需要获取今日热点榜单作为选题依据。跨来源去重、热度归一化，输出融合排名。'
user-invocable: true
---

# `deai-hotspot` — 热点采集

## When to Use
- 需要了解当前各平台的热点话题
- 为选题分析提供数据基础

## Input
- 用户指定来源类型（默认全量采集所有平台）

## Output
- `hotspot/榜单/{日期}/{来源}.md`（各来源原始榜单，按日期分目录存放）
- `hotspot/榜单/{日期}/融合榜单.md`（跨平台聚合后的 TOP 榜单）

## Procedure

### 1. 确定采集来源
用户可指定，默认全量。支持来源：

| 来源 | 适配器文件 |
|------|-----------|
| 微博热搜榜 | `./references/adapter-weibo.md` |
| 百度热搜榜 | `./references/adapter-baidu.md` |
| 知乎问题热榜 | `./references/adapter-zhihu-q.md` |
| 知乎推荐问题 | `./references/adapter-zhihu-recommend.md` |
| 知乎邀请问题 | `./references/adapter-zhihu-invited.md` |
| 知乎想法话题 | `./references/adapter-zhihu-idea.md` |
| 知乎想法热榜 | `./references/adapter-zhihu-p.md` |
| 头条热榜 | `./references/adapter-toutiao.md` |
| B站热门 | `./references/adapter-bilibili.md` |
| 抖音热点 | `./references/adapter-douyin.md` |
| 百度指数 | `./references/adapter-baidu-index.md` |
| **知微事见** | `./references/adapter-zhiwei.md` |
| **IT之家热榜** | `./references/adapter-ithome.md` |
| **澎湃新闻热榜** | `./references/adapter-thepaper.md` |
| **网易新闻热点排行** | `./references/adapter-163news.md` |
| **InfoQ中国热点** | `./references/adapter-infoq.md` |
| **虎嗅48h热文** | `./references/adapter-huxiu.md` |
| **品玩一周精选** | `./references/adapter-pingwest.md` |

### 2. 按来源采集
对每个来源，按对应适配器说明访问页面、提取字段、标准化输出。

**知乎来源特别要求**：知乎问题热榜、推荐问题、邀请问题的输出表中必须包含「链接」列，格式为 `[去回答](https://www.zhihu.com/question/{id})`，方便后续回到对应问题页面答题。

#### 登录处理规则
某些来源可能需要登录才能完整访问（如微博、知乎、抖音等）。**规则：先尝试访问，检测到被重定向到登录页才询问，不预设"需登录"。**

具体流程：

1. **直接尝试访问页面**，打开目标 URL
2. **检测是否被重定向到登录页**：
   - 等待页面加载（约 3 秒）
   - 检查页面 URL 是否包含 `/signin`、`/login`、`/passport` 等关键词
   - 检查页面标题是否包含「登录」「注册」「Sign in」等关键词
   - 检查页面主体是否包含明显的登录表单（如用户名/密码输入框）
3. **判断结果**：
   - **未被重定向，页面正常加载** → 继续采集
   - **被重定向到登录页** → 暂停该来源采集，使用 `vscode_askQuestions` 询问用户是否已登录该平台
4. 如果用户确认已登录，刷新页面继续采集
5. 如果用户未登录，告知用户需要先登录并提供登录 URL，等待用户登录确认后刷新重试
6. **如果同一来源在同一个会话中再次被访问且发现仍处于登录状态**（之前已验证过），应直接使用当前已登录的页面继续采集，不再重复询问

注意：
- 很多平台的登录态保存在 cookie 中，新的浏览器页面可能继承已有登录态，**必须真实验证是否被重定向**，不能假设
- 有 `status: ❌ **不可用**` 标记的适配器（如知乎想法话题、知乎想法热榜）属于已知无法提取的接口，即使登录也无法采集，应直接跳过并标注原因

### 3. 执行融合

```text
① 读取 `hotspot/榜单/{日期}/` 目录下当日所有 `{来源}.md` 文件
② 对标题做模糊相似度匹配（>0.80 视为同一热点）
③ 合并热度值（不同来源量纲归一化后加权平均）
④ 按融合热度排序，去重后输出 TOP 20
⑤ 标注"覆盖来源数"（如"微博+知乎"双平台上榜）
```

### 4. 输出文件

每个输出文件**必须包含 YAML frontmatter**，格式为 `---` 包裹的键值对，放在文件最顶部。

**单个来源文件的 YAML 规范：**

```yaml
---
title: 微博热搜榜 · 2026-07-20     # 榜单标题
date: 2026-07-20                   # 采集日期
source: 微博热搜榜                  # 来源平台名称
collectTime: 2026-07-20 09:50      # 具体采集时间
---
```

**融合榜单的 YAML 规范：**

```yaml
---
title: 融合热点榜单 · 2026-07-20
date: 2026-07-20
collectTime: 2026-07-20 09:50
sources:                          # 所有参与融合的来源列表
  - 微博热搜榜
  - 百度热搜榜
  - 知乎问题热榜
---
```

输出原始榜单（各来源独立文件）和融合榜单（聚合文件），按日期组织在子目录下：

```
hotspot/榜单/
├── {日期}/               ← 按采集日期分组
│   ├── 融合榜单.md       ← 当日跨平台融合 TOP 榜单
│   ├── 微博热搜榜.md     ← 各来源原始榜单
│   ├── 百度热搜榜.md
│   ├── 知乎问题热榜.md
│   └── ...
├── {另一日期}/
│   └── ...
```

融合榜单格式（**H1 省略，由 YAML `title` 替代**）：

```markdown
---
title: 融合热点榜单 · {日期}
date: {日期}
collectTime: {时间}
sources:
  - 微博热搜榜
  - 百度热搜榜
  - 知乎问题热榜
  - 头条热榜
---

## TOP 20 跨平台热点

| 排名 | 热点标题 | 融合热度 | 覆盖来源 | 时效性 | 最佳切入点 |
|------|----------|----------|----------|--------|-----------|
| 1 | xxx | 92.5 | 微博+百度+知乎 | 2h内 | 深度分析 |

## 各平台独立 TOP 10 速览
### 微博热搜榜
...(简略引用)

### 知乎问题热榜
...(简略引用)
```

## Calling Examples
```text
@deai-hotspot                   全量采集所有来源
@deai-hotspot 只采知乎问题热榜  仅采集知乎
@deai-hotspot 采微博和百度      指定来源
```
