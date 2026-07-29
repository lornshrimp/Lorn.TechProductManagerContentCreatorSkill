# 知微事见适配器

## 页面信息

- URL：`https://ef.zhiweidata.com/`（首页）
- 类型：知微事见 / 互联网大数据情报聚合平台
- 状态：✅ **强烈推荐**（数据丰富，无需登录，首页聚合 6 大模块）

## 数据特征总览

知微事见是一个互联网大数据情报平台，首页聚合了 **6 大模块**，都很有采集价值：

| 模块 | 说明 | 采集价值 |
| --- | --- | --- |
| **近期走势** | 按时间线展示当前最热事件，可切小时/天 | ⭐⭐⭐ 了解当前舆论焦点 |
| **事件榜** | 事件热度排名，含舆论场占比和热度值 | ⭐⭐⭐⭐⭐ 核心数据 |
| **热议事件** | 事件深度分析，含影响力指数和实时排名 | ⭐⭐⭐⭐ 深度参考 |
| **热搜榜（6平台）** | **6 个平台独立热搜**，需切换标签获取 | ⭐⭐⭐⭐⭐ 核心数据 |
| **事件专题** | 精选事件集合，含子话题影响力评分 | ⭐⭐⭐ 话题补充 |
| **热议词** | 热词标签云（首页未完全渲染，待验证） | ⭐⭐ 辅助参考 |

---

## 1. 热搜榜（Hot Search）⭐ 核心

### ⚠️ 重要变化：不再是聚合榜，而是 6 个独立平台标签

热搜榜实际包含 **6 个平台标签页**，点击切换后显示对应平台的热搜数据：

| 标签 | 对应平台 | 热度值特征 |
| --- | --- | --- |
| **微博** | 微博热搜 | 百万级（如 1,526,478），带标签"新" |
| **知乎** | 知乎热榜 | 百万级（如 7,020,000），问题形式 |
| **头条** | 今日头条热榜 | 无数值（首页显示为空白） |
| **B站** | B站热门 | 无数值（首页显示为 0） |
| **快手** | 快手热搜 | 千万级（如 13,469,000），带标签"新" |
| **百度** | 百度热搜 | 百万级（如 7,809,783） |

### 提取方法

需要**依次点击每个平台标签**，等待 DOM 更新后提取该平台数据。

```javascript
// 核心提取逻辑：依次点击 6 个标签页
async function extractAllPlatforms(page) {
  const platforms = ['微博', '知乎', '头条', 'B站', '快手', '百度'];
  const results = {};

  for (const platform of platforms) {
    // 1. 点击平台标签
    await page.evaluate((p) => {
      const spans = Array.from(document.querySelectorAll('span'));
      const tab = spans.find(s => s.textContent.trim() === p);
      if (tab) tab.click();
    }, platform);
    await page.waitForTimeout(800);

    // 2. 提取当前平台的文本数据
    const rawText = await page.evaluate(() => {
      const text = document.body.innerText;
      const match = text.match(/热搜榜[\s\S]*?(?=事件专题)/);
      return match ? match[0] : '';
    });

    results[platform] = rawText;
  }

  return results;
}
```

### 数据结构（按平台）

**微博** 每项结构：

```text
宗
宗馥莉18亿美元资产被冻结
1526478
新
```

**知乎** 每项结构（问题标题本身较长）：

```text
如
如何看待网传甘肃 656 分考生被福耀科技大学录取？
7020000
```

**头条** / **B站**：首页仅截取前 4 字+标题，无热度值

**快手** 每项结构（含标签"新"）：

```text
多
多省份预计有大暴雨
13469000
新
```

**百度** 每项结构：

```text
巨
巨浪击沉游轮游客漂流5小时 有人吓吐
7809783
```

### 解析函数

```javascript
function parsePlatformItems(rawText, platform) {
  const items = [];
  const lines = rawText.split('\n').map(l => l.trim()).filter(l => l);

  // 跳过标题行 "热搜榜" "查看更多" "微博知乎头条B站快手百度"
  const dataStart = lines.findIndex(l =>
    l === '微博' || l === '知乎' || l === '头条' || l === 'B站' || l === '快手' || l === '百度'
  );
  if (dataStart === -1) return items;

  // 从标签行之后开始解析
  const dataLines = lines.slice(dataStart + 1);

  let i = 0;
  while (i < dataLines.length) {
    // 每个条目 2-4 行：
    // 行1: 单字缩写（如"宗"）
    // 行2: 标题
    // 行3: 热度值（数字字符串）或空
    // 行4: 标签（"新"/"热"）可选
    if (i + 1 < dataLines.length && dataLines[i].length <= 2 && /[\u4e00-\u9fff]/.test(dataLines[i])) {
      const title = dataLines[i + 1];
      // 标题应该是中文句子（长度 > 4）
      if (title.length > 4) {
        let hotness = '';
        let tag = '';
        if (i + 2 < dataLines.length && /^\d[\d,]*$/.test(dataLines[i + 2])) {
          hotness = dataLines[i + 2];
          if (i + 3 < dataLines.length && /^(新|热|沸|爆)$/.test(dataLines[i + 3])) {
            tag = dataLines[i + 3];
            i += 2;
          }
          i += 2;
        } else {
          i += 1;
        }
        items.push({ title, hotness, tag });
      }
    }
    i++;
  }

  return items;
}
```

---

## 2. 事件榜（Event Ranking）

多平台事件热度排名，含**舆论场占比**和**事件热度值**。

首页显示 TOP 5，可通过"查看更多"跳转到 `/library` 查看完整列表。

### 事件榜提取代码

```javascript
const eventRank = await page.evaluate(() => {
  const text = document.body.innerText;
  const eventMatch = text.match(/事件榜\n([\s\S]*?)\n热议事件/);
  return eventMatch ? eventMatch[1] : '';
});
```

### 事件榜数据示例

```text
排名  事件名                            舆论场占比  事件热度  趋势
1     2026美加墨世界杯                  28%         5,614     --
2     2026世界人工智能大会开幕          25%         4,968     --
3     美国品牌怡颗莓检出致癌物          11%         2,209
4     月之暗面发布全球最大规模的开源模型Kimi K3  11%  2,126
5     2026"苏超"开赛                    5.1%       1,035
```

### 事件榜字段

| 字段 | 说明 | 示例 |
| --- | --- | --- |
| 排名 | 序号 | 1 |
| 事件名 | 热点事件名称 | 2026美加墨世界杯 |
| 舆论场占比 | 舆论关注度占比 | 28% |
| 事件热度 | 热度数值 | 5,614 |
| 趋势 | 趋势方向 | -- / ↑ / ↓ |

---

## 3. 近期走势（Timeline）

按时间线展示当前最热事件，可切换**小时/天**视图。首页默认显示当前时间点的事件列表，含时间戳和事件名。

### 近期走势数据示例

```text
2026-07-22 07:00
2026美加墨世界杯
2026世界人工智能大会开幕
美国品牌怡颗莓检出致癌物
月之暗面发布全球最大规模的开源模型Kimi K3
2026"苏超"开赛
港媒曝谢霆锋父亲谢贤去世
动画电影《八仙！》提档
高考试题外泄印度爆发大规模抗议
苹果AI国行版过审
11岁男孩被泳池排水口吸住溺亡
其他
```

### 近期走势提取代码

```javascript
const timeline = await page.evaluate(() => {
  const text = document.body.innerText;
  const timeMatch = text.match(/近期走势\n([\s\S]*?)\n事件榜/);
  return timeMatch ? timeMatch[1] : '';
});
```

---

## 4. 热议事件（Trending Events）

当前热议事件的深度分析，每条包含：

- **事件标题**（带链接到详细页）
- **事件描述**（一段话概述）
- **事件日期**和**分类标签**
- **事件热度**舆论场实时排名
- **事件影响力指数**（0-100 分，分为"一般/较大/重大/特大"四个等级）

### 热议事件数据示例

```text
超强台风"巴威"逼近！
2026-07-07 | 台风
2026年7月7日早5点，第9号台风"巴威"已稳定维持17级以上...
事件热度
舆论场实时排名 第11名
事件影响力指数
0                   95.3                  100
     一般   较大   重大    特大
```

### 热议事件提取代码

```javascript
const trendingEvents = await page.evaluate(() => {
  const text = document.body.innerText;
  const trendingMatch = text.match(/热议事件\n([\s\S]*?)\n热搜榜/);
  return trendingMatch ? trendingMatch[1] : '';
});
```

### 热议事件字段

| 字段 | 说明 | 示例 |
| --- | --- | --- |
| 事件标题 | 热点事件名 | 超强台风"巴威"逼近！ |
| 日期 | 事件日期 | 2026-07-07 |
| 分类 | 事件分类标签 | 台风 |
| 描述 | 事件概述（一段话） | 2026年7月7日早5点... |
| 实时排名 | 舆论场排名 | 第11名 |
| 影响力指数 | 0-100 评分 | 95.3（重大） |

---

## 5. 事件专题（Event Topics）

精选事件集合，按主题归类。每个专题下含多个子话题，子话题带有**影响力评分**。

### 事件专题数据示例

```text
2024年315晚会
  2024年央视315晚会播出          88.6
  央视3•15晚会曝光制造水军的"主板机"  73.6
  央视3•15晚会曝光不防火的防火玻璃    71.9
2023年汽车行业热门事件
企业双标事件
2023AI大模型盘点
```

### 事件专题提取代码

```javascript
const topics = await page.evaluate(() => {
  const text = document.body.innerText;
  const topicMatch = text.match(/事件专题\n([\s\S]*?)\n热议词/);
  return topicMatch ? topicMatch[1] : '';
});
```

---

## 完整采集流程

```javascript
async function collectZhiweiData(page) {
  await page.goto('https://ef.zhiweidata.com/');
  await page.waitForTimeout(3000);

  // 1. 采集事件榜
  const eventRank = await page.evaluate(() => {
    const text = document.body.innerText;
    const m = text.match(/事件榜\n([\s\S]*?)\n热议事件/);
    return m ? m[1] : '';
  });

  // 2. 采集近期走势
  const timeline = await page.evaluate(() => {
    const text = document.body.innerText;
    const m = text.match(/近期走势\n([\s\S]*?)\n事件榜/);
    return m ? m[1] : '';
  });

  // 3. 采集热议事件
  const trending = await page.evaluate(() => {
    const text = document.body.innerText;
    const m = text.match(/热议事件\n([\s\S]*?)\n热搜榜/);
    return m ? m[1] : '';
  });

  // 4. 采集事件专题
  const topics = await page.evaluate(() => {
    const text = document.body.innerText;
    const m = text.match(/事件专题\n([\s\S]*?)\n热议词/);
    return m ? m[1] : '';
  });

  // 5. 采集各平台热搜（依次点击 6 个标签）
  const platforms = ['微博', '知乎', '头条', 'B站', '快手', '百度'];
  const hotSearch = {};

  for (const platform of platforms) {
    await page.evaluate((p) => {
      const spans = Array.from(document.querySelectorAll('span'));
      const tab = spans.find(s => s.textContent.trim() === p);
      if (tab) tab.click();
    }, platform);
    await page.waitForTimeout(800);

    const raw = await page.evaluate(() => {
      const text = document.body.innerText;
      const m = text.match(/热搜榜[\s\S]*?(?=事件专题)/);
      return m ? m[0] : '';
    });

    hotSearch[platform] = raw;
  }

  return { eventRank, timeline, trending, hotSearch, topics };
}
```

---

## 输出格式

### 热搜榜（按平台输出）

```markdown
# 知微事见热搜榜 · 微博 · {日期}

| 排名 | 词条 | 热度 | 标签 |
| --- | --- | --- | --- |
| 1 | 宗馥莉18亿美元资产被冻结 | 1,526,478 | 新 |
| 2 | 阿根廷队仅3人祝贺西班牙夺冠 | 1,222,330 | 新 |
```

```markdown
# 知微事见热搜榜 · 知乎 · {日期}

| 排名 | 问题 | 热度 |
| --- | --- | --- |
| 1 | 如何看待网传甘肃 656 分考生被福耀科技大学录取？ | 7,020,000 |
| 2 | 网友发现很多 KTV 都没有 MV 了，全是奇怪的 AI 画面... | 4,730,000 |
```

### 事件榜

```markdown
# 知微事见事件榜 · {日期}

| 排名 | 事件名 | 舆论场占比 | 事件热度 |
| --- | --- | --- | --- |
| 1 | 2026美加墨世界杯 | 28% | 5,614 |
```

### 近期走势

```markdown
# 知微事见近期走势 · {日期}

| 时间 | 热点事件 |
| --- | --- |
| 2026-07-22 07:00 | 2026美加墨世界杯、2026世界人工智能大会开幕... |
```

### 热议事件

```markdown
# 知微事见热议事件 · {日期}

| 事件 | 日期 | 分类 | 实时排名 | 影响力指数 |
| --- | --- | --- | --- | --- |
| 超强台风"巴威"逼近！ | 2026-07-07 | 台风 | 第11名 | 95.3（重大） |
```

### 事件专题

```markdown
# 知微事见事件专题 · {日期}

| 专题 | 子话题 | 影响力评分 |
| --- | --- | --- |
| 2024年315晚会 | 2024年央视315晚会播出 | 88.6 |
| 2024年315晚会 | 央视3•15晚会曝光制造水军的"主板机" | 73.6 |
```

## 注意事项

- **无需登录**，页面可直接访问
- **热搜榜需点击 6 个平台标签**分别采集，不能一次性读取所有数据
- 每个标签页仅显示 TOP 5-6 条，首页无"加载更多"功能
- 热搜榜的"查看更多"链接跳转到事件库 `/library`，而非独立热搜页面
- 事件榜可通过"查看更多"跳转到 `/library` 查看更完整列表
- 头条和 B 站的热度值在首页未完整渲染（显示为 0 或空），如需完整热度值需点击该条目跳转
- 热议事件的事件影响力指数（0-100）提供了舆情分级的量化参考
- 知微事见本身是情报聚合平台，各模块数据可作为跨平台融合的交叉验证参考
