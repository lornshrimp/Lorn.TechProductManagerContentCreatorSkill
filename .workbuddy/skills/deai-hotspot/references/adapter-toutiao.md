# 今日头条热榜适配器

## 页面信息
- URL：`https://www.toutiao.com/?channel=hot&source=ch`（频道页，降级方案）
- 类型：头条热榜
- 状态：⚠️ **降级可用**（独立热榜页面已下线）

## 已知不可用的 URL（记录避免重复尝试）
- `https://www.toutiao.com/hot-event/` — 返回 404，已下线
- `https://www.toutiao.com/trending/` — 返回 404，已下线
- `https://www.toutiao.com/hot/` — 返回 404，已下线

## 操作步骤

### 方案 A：搜索栏热搜词（推荐）
1. 打开 `https://www.toutiao.com/?channel=hot&source=ch`
2. 在页面中找到搜索框下方的 **"热搜"区域**（region="热搜"），其中包含实时热搜词
3. 使用 a11y 快照或 Playwright 提取搜索栏中的热搜词列表

### 方案 B：频道页热门文章
1. 打开 `https://www.toutiao.com/?channel=hot&source=ch`
2. 等待页面加载后，使用 Playwright 提取文章标题列表
3. 标题即为当前热门话题

```javascript
// Playwright 提取热门文章标题
const articles = document.querySelectorAll('a[class*="title"], a[href*="article"]');
```

## 提取字段
| 字段 | 说明 | 示例 |
|------|------|------|
| 热搜词 | 搜索栏实时热搜关键词 | 2026年世界杯战况 |

## 输出格式
```markdown
# 头条热榜 · {日期}

## 热搜搜索词
| 序号 | 热搜词 |
| --- | --- |
| 1 | 2026年世界杯战况 |

## 热门文章
| 标题 | 来源 |
| --- | --- |
| xxx | 自媒体 |
```

## 注意事项
- 今日头条已下线独立热榜页面，当前仅有搜索栏热搜词和频道推荐流可用
- 热搜词无热度数值，仅能反映话题方向
- 如后续头条恢复独立热榜页面，需更新本适配器
