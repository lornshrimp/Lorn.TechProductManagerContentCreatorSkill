# 虎嗅 48 小时热文适配器

## 页面信息
- URL：`https://www.huxiu.com/`（首页，48 小时热文模块）
- 类型：虎嗅 48 小时热文
- 状态：✅ 验证可用

## 数据特征

虎嗅首页有「48 小时热文」模块，可切换「周」视图，展示当前热门商业科技文章。按热度排序显示，每条含标题、作者、评论数、发表时间。

## 操作步骤

1. 打开 `https://www.huxiu.com/` 首页
2. 等待页面加载完成
3. 使用 a11y 快照或 Playwright 提取「48 小时热文」区域

```javascript
// Playwright 提取代码
const hotArticles = await page.evaluate(() => {
  const items = [];
  // 定位 48 小时热文区域
  const hotSection = document.querySelector('[class*="hot"], [class*="rank"], [class*="trending"]');
  if (hotSection) {
    const articles = hotSection.querySelectorAll('a, [class*="article"], [class*="item"]');
    articles.forEach(a => {
      const title = a.textContent?.trim();
      if (title && title.length > 6 && title.length < 100) {
        items.push({
          标题: title,
          链接: a.href || ''
        });
      }
    });
  }
  return items.slice(0, 15);
});
```

## 提取字段
| 字段 | 说明 | 示例 |
|------|------|------|
| 标题 | 文章标题 | 字节跳动为何... |
| 作者 | 作者名 | 虎嗅 |
| 评论数 | 评论数 | 23 |
| 时间 | 发表时间 | 2 小时前 |

## 输出格式
```markdown
# 虎嗅 48 小时热文 · {日期}

采集时间：{时间}

| 排名 | 标题 | 评论数 | 时间 |
| --- | --- | --- | --- |
| 1 | xxx | 23 | 2 小时前 |
```

## 注意事项
- 无需登录
- 热文区域显示顺序即热度排序，但无明确排名数字
- 可切换「48 小时 / 周」两个时间范围
- 无独立热度值，评论数可作热度参考
- 适合科技商业领域的热点发现
