# 网易新闻热点排行适配器

## 页面信息
- URL：`https://news.163.com/`（首页 HTML，热点排行模块）
- 类型：网易新闻热点排行
- 状态：✅ 验证可用

## 数据特征

网易新闻首页有「热点排行」模块，编号 1-10，每条附带**热度数值**（疑似浏览量/互动量），是目前少数自带热度数值的时政新闻热榜。

## 操作步骤

1. 打开 `https://news.163.com/` 首页
2. 等待页面加载完成
3. 使用 a11y 快照或 Playwright 提取「热点排行」区域

```javascript
// Playwright 提取代码
const hotRank = await page.evaluate(() => {
  const items = [];
  // 定位热点排行区域
  const rankSection = document.querySelector('[class*="rank"], [class*="hot"], [class*="top"]');
  if (rankSection) {
    const lis = rankSection.querySelectorAll('li, [class*="item"]');
    lis.forEach(li => {
      const link = li.querySelector('a');
      const text = link?.textContent?.trim();
      // 提取热度数值（如果有）
      const numSpan = li.querySelector('[class*="num"], span');
      const heat = numSpan?.textContent?.trim();
      if (text && text.length > 4) {
        items.push({
          标题: text,
          热度值: heat || '',
          链接: link?.href || ''
        });
      }
    });
  }
  return items.slice(0, 10);
});
```

## 提取字段
| 字段 | 说明 | 示例 |
|------|------|------|
| 排名 | 1-10 | 1 |
| 标题 | 新闻标题 | xxx |
| 热度值 | 热度数值 | 23025 |
| 链接 | 文章URL | https://... |

## 输出格式
```markdown
# 网易新闻热点排行 · {日期}

采集时间：{时间}

| 排名 | 标题 | 热度 |
| --- | --- | --- |
| 1 | xxx | 23,025 |
```

## 注意事项
- 无需登录
- 每条带热度数值，可直接用于融合榜单热度计算
- 仅 10 条，条目数较少
- 适合时事政治/社会热点领域
