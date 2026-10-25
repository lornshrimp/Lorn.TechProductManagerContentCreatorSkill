# 知乎邀请问题适配器

## 页面信息
- URL：`https://www.zhihu.com/creator/featured-question/invited`
- 类型：知乎邀请问题
- 状态：✅ 验证可用（先访问检测，登录后可完整采集）

## 操作步骤

1. **直接打开** `https://www.zhihu.com/creator/featured-question/invited`
2. **等待页面加载完成**（约 5 秒）
3. **检测是否被重定向到登录页**：检查页面 URL 是否包含 `/signin` 或页面标题是否包含「登录」
4. **如果检测到被重定向**：使用 `vscode_askQuestions` 询问用户是否已登录知乎
5. **注意**：如果已有其他知乎标签页已登录，应优先在已登录页面上导航到此 URL（登录态可能不跨子域名，需尝试）
6. **如果页面正常加载**：使用 Playwright `page.evaluate()` 从 DOM 中提取邀请问题列表

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
| 问题标题 | 邀请回答的问题标题 | 如何看待Kimi K3模型价格翻5倍？ |
| 链接 | 问题页面 URL（用于回头答题） | `https://www.zhihu.com/question/xxx` |

## 输出格式

```markdown
# 知乎邀请问题 · {日期}

采集时间：{时间}

| 序号 | 问题标题 | 链接 |
| --- | --- | --- |
| 1 | xxx？ | [去回答](https://www.zhihu.com/question/xxx) |
```

## 注意事项

- **必须先在浏览器中登录知乎账号**
- 邀请问题是平台邀请当前用户回答的问题，**非热榜排名**，但可反映平台当前讨论方向
- a11y 快照仅显示导航侧栏，主内容需使用 Playwright DOM 提取
- 页面会混合展示"邀请回答"和"推荐问题"两个标签页的内容

## bsk 实测命令（2026-09-07 验证，优先使用）

```bash
bsk navigate --session <id> --wait-until load "https://www.zhihu.com/creator/featured-question/invited"
# 标题##链接 成对提取（同次 evaluate 内对齐，禁止手工拼链接）
bsk evaluate --session <id> "Array.from(document.querySelectorAll('a[href*=\\\"/question/\\\"]')).map(a=>(a.innerText||'').trim()+'##'+a.getAttribute('href')).filter(x=>x.split('##')[0].length>8).slice(0,20).join('\\n')"
```

## 落盘硬约束（规范校验门禁）

`hotspot/榜单/{日期}/知乎邀请问题.md` 必须含「链接」列（正文出现 `去回答` 或 `zhihu.com/question`），
否则 `规范校验.py` 判 ❌（规则：文件名含"知乎"且非"想法热榜/想法话题"即强制）。
**采集时就必须落链接，不要只存标题。**

## 断链补采流程（2026-09-14 实测，晨间采集漏链时用）

1. **feed 会轮换**：单轮 evaluate 通常只命中当日榜单的约 2/3，**至少 3 轮**（每轮 `navigate → wait-ms 4500 → evaluate`），取并集。
2. **余量走搜索页**（同 recommend 适配器）：
   ```bash
   bsk navigate --session <id> --wait-until load "https://www.zhihu.com/search?type=content&q=<urlencode(标题)>"
   bsk wait-ms 4000
   bsk evaluate --session <id> "Array.from(document.querySelectorAll('a[href*=\"/question/\"]')).map(a=>(a.innerText||'').trim()+'##'+a.getAttribute('href')).filter(x=>x.split('##')[0].length>4).slice(0,20).join('\n')"
   ```
   从返回结果里挑**标题逐字一致**的那条的 `/question/{id}`。
3. **核验**：补完后抽查 ≥5 条 `bsk navigate https://www.zhihu.com/question/{id}` + `evaluate "document.title"`，确认标题与榜单行一致。**禁止凭记忆拼 question id。**
4. 补齐后 `bsk session stop --all`。

> ⚠️ **前缀警告（2026-09-07 事故）**：**必须使用本文件第 4 行 URL 的 `/creator/featured-question/` 前缀**。曾因误用 `/creator/creative-inspiration/invited` 得到 404，被误判"页面已改版下线"——页面从未下线，是执行时换错了前缀。page 标题为「问题推荐 - 创作中心」，含板块分组（新问/「XX领域」今日热议/知乎热榜上榜/话题推荐），可按板块组织输出。
