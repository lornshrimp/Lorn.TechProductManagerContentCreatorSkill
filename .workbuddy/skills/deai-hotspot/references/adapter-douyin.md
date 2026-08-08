# 抖音热点适配器

## 页面信息
- URL：`https://www.douyin.com/hot`
- 类型：抖音热点
- 状态：✅ **可用（bsk evaluate）**。2026-08-08 实测：navigate 会 RPC 超时（页面实际已就绪），**evaluate 可完整提取热榜主体含热度值**（18 条+）；a11y 快照截断的历史问题用 evaluate 绕开

## 操作步骤

### 方案 A：搜索引擎（推荐，稳定）
使用 vscode-websearch 搜索 "抖音热榜 2026" 获取结构化数据。

### 方案 B：Playwright 提取（需处理 DOM 结构）
```javascript
await page.goto('https://www.douyin.com/hot');
await page.waitForTimeout(3000);

// 方案 B1：查找 "抖音热榜" 标题所在的容器
const hotItems = await page.evaluate(() => {
  const headings = document.querySelectorAll('h1, h2');
  let hotSection = null;
  for (const h of headings) {
    if (h.textContent.includes('抖音热榜')) {
      hotSection = h.closest('div');
      break;
    }
  }
  if (!hotSection) return [];
  const items = hotSection.querySelectorAll('li, [class*="item"], [class*="card"]');
  return Array.from(items).map(li => li.textContent?.trim()).filter(Boolean);
});

// 方案 B2：提取所有可见文字中带排名模式的内容
const allText = await page.evaluate(() => document.body.innerText);
// 从 allText 中解析 "排名 话题名 播放量" 模式
```

## 提取字段
| 字段 | 说明 | 示例 |
|------|------|------|
| 话题名 | 热点话题 | 峨眉山会惩罚每一个嘴硬的人 |
| 播放量 | 热度数值 | 1133.9万 |

## 输出格式
```markdown
# 抖音热点 · {日期}

采集时间：{时间}

| 排名 | 话题名 | 播放量 | 趋势 |
| --- | --- | --- | --- |
| 1 | #xxx | 1133.9万 | 🔥 |
```

## 注意事项
- `read_page` a11y 快照可以看到 "抖音热榜" 标题，但**列表项的具体文字内容会被截断**
- 推荐优先使用 Playwright DOM 提取或搜索引擎方案获取数据
- 热度值单位为 K（千），如 11339.3K = 1133.9万
- **先尝试直接打开页面**，检测是否被重定向到登录页。抖音热榜页面即使未登录也能看到部分数据，登录后可看到更完整榜单
