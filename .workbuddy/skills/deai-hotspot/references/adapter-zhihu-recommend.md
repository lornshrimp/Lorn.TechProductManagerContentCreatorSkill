# 知乎推荐问题适配器

## 页面信息
- URL：`https://www.zhihu.com/creator/featured-question/recommend`
- 类型：知乎推荐问题
- 状态：✅ 验证可用（先访问检测，登录后可完整采集）

## 操作步骤

1. **直接打开** `https://www.zhihu.com/creator/featured-question/recommend`
2. **等待页面加载完成**（约 3 秒）
3. **检测是否被重定向到登录页**：检查页面 URL 是否包含 `/signin` 或页面标题是否包含「登录」
4. **如果检测到被重定向**：使用 `vscode_askQuestions` 询问用户是否已登录知乎
5. **注意**：如果已有其他知乎标签页已登录，应优先在已登录页面上导航到此 URL（登录态可能不跨子域名，需尝试）
6. **如果页面正常加载**：使用 Playwright `page.evaluate()` 从 DOM 中提取推荐问题列表

```javascript
// Playwright 提取代码（含链接）
return await page.evaluate(() => {
  const results = [];
  const links = document.querySelectorAll('a[href*="question"]');
  links.forEach(a => {
    const text = a.textContent?.trim();
    const href = a.href;
    if (text && text.length > 8 && text.includes('？')) {
      results.push({ 问题标题: text, 链接: href });
    }
  });
  // 按链接去重
  const seen = new Set();
  return results.filter(r => {
    if (seen.has(r.链接)) return false;
    seen.add(r.链接);
    return true;
  }).slice(0, 20);
});
```

## 提取字段
| 字段 | 说明 | 示例 |
| --- | --- | --- |
| 问题标题 | 推荐回答的问题 | AI时代更稀缺的是「提出好问题」还是「判断好答案」？ |
| 链接 | 问题页面 URL | `https://www.zhihu.com/question/xxx` |

## 输出格式

```markdown
# 知乎推荐问题 · {日期}

采集时间：{时间}

| 序号 | 问题标题 | 链接 |
| --- | --- | --- |
| 1 | xxx？ | [去回答](https://www.zhihu.com/question/xxx) |
```

## 注意事项

- **必须先在浏览器中登录知乎账号**

- 推荐问题返回的是平台根据用户兴趣推荐的待回答问题，**非热榜排名**
- a11y 快照（read_page）仅显示导航侧栏，主内容需使用 Playwright 从 DOM 提取
- 推荐问题的回答数、关注数等信息在 DOM 中不易结构化提取（多为动态渲染）
