# InfoQ 中国热点适配器

## 页面信息
- URL：`https://www.infoq.cn/hotlist?tag=day`（热点列表页，支持时间切换）
- 类型：InfoQ 中国热点
- 状态：✅ 验证可用

## 数据特征

InfoQ 中国有**独立热点页面**，支持按 7 天 / 1 月 / 3 月切换，每条带**阅读量数值**，是唯一有专用热榜 URL + 时间筛选 + 热度数值的 IT 技术平台。

## 操作步骤

1. 打开 `https://www.infoq.cn/hotlist?tag=day`（7 天热点）
2. 或者 `https://www.infoq.cn/hotlist?tag=month`（1 月热点）
3. 或者 `https://www.infoq.cn/hotlist?tag=quarter`（3 月热点）
4. 等待页面加载完成
5. 使用 Playwright 提取文章列表

```javascript
// Playwright 提取代码
const hotList = await page.evaluate(() => {
  const items = [];
  const articles = document.querySelectorAll('[class*="article"], [class*="card"], [class*="item"]');
  articles.forEach(article => {
    const titleEl = article.querySelector('[class*="title"], h2, h3, a');
    const heatEl = article.querySelector('[class*="heat"], [class*="view"], [class*="num"]');
    const title = titleEl?.textContent?.trim();
    const heat = heatEl?.textContent?.trim();
    if (title && title.length > 4) {
      items.push({
        标题: title,
        阅读量: heat?.replace(/[^0-9]/g, '') || '',
        链接: titleEl?.href || ''
      });
    }
  });
  return items.slice(0, 20);
});
```

## 提取字段
| 字段 | 说明 | 示例 |
|------|------|------|
| 标题 | 文章标题 | 如何用K8s实现... |
| 阅读量 | 热度数值 | 8360 |
| 时间范围 | 7天/1月/3月 | day |
| 链接 | 文章URL | https://www.infoq.cn/article/xxx |

## 输出格式
```markdown
# InfoQ 中国热点 · {日期}

采集时间：{时间}
时间范围：7 天

| 排名 | 标题 | 阅读量 |
| --- | --- | --- |
| 1 | xxx | 8,360 |
```

## 注意事项
- 浏览热榜不登录可见，部分详细内容需登录
- 推荐默认使用 `?tag=day`（7 天热点），数据量适中
- 带阅读量数值，可直接用于融合榜单
- 适合 IT 技术、企业级开发领域的热点发现
