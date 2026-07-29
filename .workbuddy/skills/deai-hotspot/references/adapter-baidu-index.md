# 百度指数适配器

## 页面信息
- URL：`https://index.baidu.com/v2/index.html#/`（首页） / `https://index.baidu.com/v2/rank/index.html#/industryrank`（行业排行）
- 类型：百度指数/搜索趋势
- 状态：⚠️ **降级可用**（需登录，数据为非标结构）

## 数据特征

百度指数是百度提供的搜索大数据分析平台，主要提供以下数据类型：

### 1. 搜索指数趋势（需登录）
- 搜索关键词，获取该词的搜索指数、资讯指数等趋势图表
- **非热榜结构**，需要先有目标关键词

### 2. 行业排行（部分可见）
- 访问 `https://index.baidu.com/v2/rank/index.html#/industryrank`
- 提供汽车、手机等行业的品牌指数/品牌搜索指数/品牌资讯指数/品牌互动指数排名
- 支持日榜/周榜切换
- a11y 快照可看到分类标题和选项卡，但**具体列表项为 JS 渲染，需使用 Playwright 提取**

```javascript
// Playwright 提取行业排行（如汽车行业品牌指数日榜）
const rankData = await page.evaluate(() => {
  // 查找行业排行容器
  const sections = document.querySelectorAll('[class*="rank"] [class*="list"], [class*="industry"]');
  return Array.from(sections).map(el => el.textContent?.trim()).filter(Boolean);
});
```

### 3. 最新动态（不须登录）
- 访问 `https://index.baidu.com/v2/topic/index.html#/topic/all`
- 展示百度指数官方发布的行业分析报告和热点解读文章
- 过滤器：全部/专题/公告/行业/热点
- **可提取文章标题列表**

## 提取字段
| 字段 | 说明 | 来源 |
|------|------|------|
| 品牌/关键词 | 排行中的品牌名或搜索关键词 | 行业排行 |
| 指数值 | 搜索指数/品牌指数数值 | 行业排行 |
| 排名 | 当前排名 | 行业排行 |

## 输出格式
```markdown
# 百度指数行业排行 · {日期}

采集时间：{时间}

| 排名 | 品牌 | 指数 |
| --- | --- | --- |
| 1 | xxx | 12,500 |
```

## 注意事项
- 百度指数**需要登录百度账号**才能进行关键词搜索和查看完整排行
- 行业排行仅覆盖汽车、手机等特定行业，**非全网通用热榜**
- 建议将百度指数作为**辅助验证工具**（验证某个话题的搜索热度趋势），而非独立热榜来源
- 页面有较多 JavaScript 动态渲染，建议优先使用 Playwright 而非 a11y 快照
