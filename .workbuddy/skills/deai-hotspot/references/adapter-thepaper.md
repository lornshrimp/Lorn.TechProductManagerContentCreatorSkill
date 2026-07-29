# 澎湃新闻热榜适配器

## 页面信息
- URL：`https://www.thepaper.cn/`（热榜嵌入首页 HTML）
- 类型：澎湃新闻热榜
- 状态：✅ 验证可用

## 数据特征

澎湃新闻首页中部有「热榜」模块，编号 1-20，静态 HTML 渲染，无需登录。

## 操作步骤

1. 打开 `https://www.thepaper.cn/` 首页
2. 等待页面加载完成
3. 使用 a11y 快照或 Playwright 提取「热榜」区域

```javascript
// Playwright 提取代码
const hotList = await page.evaluate(() => {
  const items = [];
  // 定位热榜容器
  const section = document.querySelector('[class*="rebang"], [class*="hot"], [class*="rank"]');
  if (section) {
    const links = section.querySelectorAll('a');
    links.forEach((a, i) => {
      const text = a.textContent?.trim();
      if (text && text.length > 4) {
        items.push({
          排名: i + 1,
          标题: text,
          链接: a.href
        });
      }
    });
  }
  // 降级方案：提取所有带编号（1. 2. 3.）模式的链接
  if (items.length === 0) {
    const allLinks = document.querySelectorAll('a[href*="newsDetail"]');
    allLinks.forEach((a, i) => {
      const text = a.textContent?.trim();
      if (text && text.length > 6) {
        items.push({
          排名: i + 1,
          标题: text,
          链接: a.href
        });
      }
    });
  }
  return items.slice(0, 20);
});
```

## 提取字段
| 字段 | 说明 | 示例 |
|------|------|------|
| 排名 | 1-20 | 1 |
| 标题 | 新闻标题 | 拜登宣布... |
| 链接 | 文章URL | https://www.thepaper.cn/newsDetail_forward_xxx |

## 输出格式
```markdown
# 澎湃新闻热榜 · {日期}

采集时间：{时间}

| 排名 | 标题 |
| --- | --- |
| 1 | xxx |
```

## 注意事项
- 无需登录
- 条目最多（20 条），是所有热榜源中条目数最多的
- 无独立热度数值，排名即热度排序
- 适合时事政治领域的热点发现
- 澎湃新闻的「热榜」和「推荐」两个模块靠近，注意区分
