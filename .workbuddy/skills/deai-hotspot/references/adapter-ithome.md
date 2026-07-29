# IT之家热榜适配器

## 页面信息
- URL：`https://www.ithome.com/`（热榜嵌入首页 HTML）
- 类型：IT之家热榜（日榜 / 周榜 / 月榜）
- 状态：✅ 验证可用

## 数据特征

IT之家首页右侧嵌入「日榜 / 周榜 / 月榜」三标签排行榜，服务端渲染，每个标签12条。

## 操作步骤

1. 打开 `https://www.ithome.com/` 首页
2. 等待页面加载完成
3. 使用 a11y 快照或 Playwright 提取排行榜区域数据

```javascript
// Playwright 提取代码
const rankData = await page.evaluate(() => {
  // 定位排行榜容器（日榜/周榜/月榜）
  const rankSections = document.querySelectorAll('[class*="rank"] [class*="list"], [class*="hot"] [class*="ul"]');
  const results = { daily: [], weekly: [], monthly: [] };
  
  // 提取所有排行列表项
  const lists = document.querySelectorAll('ol, ul');
  lists.forEach(list => {
    const items = list.querySelectorAll('li');
    if (items.length >= 10) {
      const section = [];
      items.forEach((li, i) => {
        const link = li.querySelector('a');
        if (link) {
          section.push({
            排名: i + 1,
            标题: link.textContent?.trim(),
            链接: link.href
          });
        }
      });
      if (section.length > 0) results.daily = section;
    }
  });
  return results;
});
```

## 提取字段
| 字段 | 说明 | 示例 |
|------|------|------|
| 排名 | 1-12 | 1 |
| 标题 | 文章标题 | 我魂都吓没了：网友反馈收到1.5万亿美元AWS账单 |
| 链接 | 文章URL | https://www.ithome.com/0/xxx/xxx.htm |

## 输出格式
```markdown
# IT之家热榜 · {日期}

采集时间：{时间}

| 排名 | 标题 |
| --- | --- |
| 1 | xxx |
```

## 注意事项
- 无需登录，页面直接可访问
- 日榜/周榜/月榜三个标签切换，默认显示日榜
- 无独立热度数值，排名本身即热度排序
- 条目固定 12 条
- 适合 IT 数码领域的热点发现
