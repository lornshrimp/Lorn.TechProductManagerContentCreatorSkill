# 品玩一周精选适配器

## 页面信息
- URL：`https://www.pingwest.com/`（首页，一周精选模块）
- 类型：品玩一周精选
- 状态：✅ 验证可用

## 数据特征

品玩首页有「一周精选」板块，展示本周编辑精选的 5 篇文章（排名 1-5），含标题、作者、评分摘要。内容质量高、编辑筛选含金量大。

## 操作步骤

1. 打开 `https://www.pingwest.com/` 首页
2. 等待页面加载完成
3. 使用 a11y 快照或 Playwright 提取「一周精选」区域

```javascript
// Playwright 提取代码
const weeklyPick = await page.evaluate(() => {
  const items = [];
  // 定位一周精选区域
  const pickSection = document.querySelector('[class*="pick"], [class*="hot"], [class*="weekly"], [class*="featured"]');
  if (pickSection) {
    const links = pickSection.querySelectorAll('a');
    links.forEach((a, i) => {
      const title = a.textContent?.trim();
      if (title && title.length > 6) {
        items.push({
          排名: i + 1,
          标题: title,
          链接: a.href
        });
      }
    });
  }
  return items.slice(0, 5);
});
```

## 提取字段
| 字段 | 说明 | 示例 |
|------|------|------|
| 排名 | 1-5 | 1 |
| 标题 | 文章标题 | AI 编程助手... |
| 作者 | 作者名 | xxx |
| 评分摘要 | 编辑推荐语 | 推荐理由... |

## 输出格式
```markdown
# 品玩一周精选 · {日期}

采集时间：{时间}

| 排名 | 标题 |
| --- | --- |
| 1 | xxx |
```

## 注意事项
- 无需登录
- 仅 5 条，条目最少但编辑精选含金量高
- 可以作为选题参考的辅助信号
- 适合科技领域的热点发现
