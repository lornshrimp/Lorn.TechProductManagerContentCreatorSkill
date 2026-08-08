---
name: adapter-bsk
title: bsk 浏览器采集手册（BrowserSkill · 真实 Edge/Chrome）
date: 2026-08-07
status: ✅ 可用（已验证）
source: bsk CLI v0.1.9 + BrowserSkill 扩展 0.1.5 + Edge 151
---

# bsk 浏览器采集手册

驱动用户真实浏览器（Edge/Chrome + BrowserSkill 扩展），可读 JS 渲染与登录态页面。本手册为 2026-08-07 全平台实测验证结果。

## 1. 前置条件与自检

```bash
bsk doctor -v          # 全部 ok 才可采集；extension connected >= 1 表示扩展已连接
bsk browsers           # 列出已连接浏览器（INSTANCE/浏览器版本/扩展版本）
bsk daemon start       # daemon 未运行时启动（偶尔扩展掉线，等 5-10s 重连）
```

环境要点（Windows + WorkBuddy）：
- bsk 装在 `~/.local/bin/bsk.exe`；命令用绝对路径或确保 PATH 生效。
- 不能用 `curl -o` 落盘（本环境拦截 rename）；**下载/落盘一律用 Python urllib + `open('wb')` 到 `%TEMP%`**，交付文件用 Write 工具。
- 若浏览器未登录目标平台（微博/知乎/抖音等），登录弹窗会遮挡内容——**请用户先在浏览器登录**，再重采。

## 2. 会话生命周期（强制）

```bash
bsk session start                      # 返回 4 位 session id（如 jnqg）
bsk navigate --session <id> --wait-until load <url>   # 注意：--session 是子命令级参数
bsk snapshot --session <id>            # aria 快照（可见文本 + @eN refs）
bsk session stop <id>                  # 任务结束必停（含出错路径）
```

## 3. 各源采集命令（实测验证）

### 知乎热榜（登录态，此前所有通道不可达）
```bash
bsk navigate --session <id> --wait-until load "https://www.zhihu.com/hot"
bsk snapshot --session <id> | grep -E 'link "'           # 问题标题
bsk snapshot --session <id> | grep '热度'                  # 热度值
```

### 微博热搜（需登录）
```bash
bsk navigate --session <id> --wait-until load --timeout 60s "https://s.weibo.com/top/summary"
bsk get-html --session <id> > /tmp/weibo.html             # 180KB 完整 HTML
# python 正则：<a href="[^"]*weibo[^"]*">词条</a> 提取全量词条
```

### 百度热搜（SSR，可直连亦可用 bsk 验证）
```bash
bsk navigate --session <id> "https://top.baidu.com/board?tab=realtime"
bsk snapshot --session <id> | grep -E 'link "'            # 词条；排名为数字 link
```

### B站排行榜（反爬绕过：用 /ranking，勿用 /v/popular/rank/all）
```bash
bsk navigate --session <id> "https://www.bilibili.com/ranking"   # /v/popular/rank/all 会被 CDP 拒绝
bsk snapshot --session <id> | grep -E 'link "'            # 视频标题（过滤导航元素）
# 注：api.bilibili.com/x/web-interface/ranking/v2 返回 -352（需 wbi 签名），不可直连
```

### 抖音热榜（需登录；登录态下用 evaluate 提取）
```bash
bsk navigate --session <id> --wait-until load "https://www.douyin.com/hot"
bsk snapshot --session <id> | grep -E 'link "|热度'       # 词条+热度（热榜为 JS 渲染）
bsk evaluate --session <id> "Array.from(document.querySelectorAll('a')).map(a=>a.innerText.trim()).filter(t=>t&&t.length>4&&t.length<45).slice(0,60).join('\n')"
# 热榜 API 可抓包：bsk network --session <id> --limit 50 | grep 'hot/search/list'（带 msToken/a_bogus 签名）
# 未登录会被登录弹窗遮挡（Esc 无效）——必须用户先登录
```

### 虎嗅 / InfoQ / 品玩 / 知微（2026-08-08 验证：bsk 均可采，勿直接降级）
- 虎嗅 `huxiu.com`：`bsk navigate` 后 `evaluate "document.body.innerText..."` 提取实时热文（含字节 AI 战略/梁文锋等）。urllib 直连会 WAF 拦截，但 bsk 正常。
- InfoQ `infoq.cn/hotlist?tag=day`：JS 渲染 + 懒加载，navigate 后**先 `window.scrollTo(0, document.body.scrollHeight)` 滚动触发**，再 evaluate 提取正文。urllib 直连返回空，bsk 正常。
- 品玩 `pingwest.com`：JS 渲染，navigate + 滚动后 evaluate 提取 `a[href*='pingwest.com/a/']` 链接与标题。urllib 直连返回空，bsk 正常。
- 知微 `ef.zhiweidata.com`：navigate 50s 内可加载完成（无需登录），evaluate 提取事件榜/近期走势/热议事件/影响力指数；热搜榜需依次点击 6 个平台标签。历史"渲染慢易超时"记录已过时。
- IT之家/澎湃/网易：SSR 源用 Python urllib 直采更快（澎湃/网易对 Agent Window 有 WAF/超时，bsk 可能 403/502）。

## 4. 反爬绕过经验（2026-08-07 验证，2026-08-08 补充）

| 源 | 问题 | 解法 |
| --- | --- | --- |
| B站 | `/v/popular/rank/all` CDP 拒绝 | 改 `/ranking` 路径 ✅ |
| 微博 | 登录墙重定向 passport | 用户登录后直采 s.weibo.com/top/summary ✅ |
| 抖音 | 未登录弹窗遮挡 | 用户登录 + evaluate 提取 ✅ |
| 澎湃/网易 | WAF（403/502） | bsk 不可行 → urllib 直采/WebSearch |
| 头条 | 热榜页 404（改版下线） | 降级：搜索词 + 热门文章 |
| 虎嗅/InfoQ/品玩 | urllib 直连返回空（WAF/JS 渲染/懒加载） | **bsk 可正常采集**（见 §3 各源命令）：虎嗅 evaluate 提取；InfoQ/品玩 滚动+evaluate（2026-08-08 实测 ✅）；WebSearch 仅作最后兜底 |
| 知微 | 历史记录"渲染慢易超时" | **bsk navigate 50s 内可加载**（无需登录），evaluate 提取事件榜/影响力指数（2026-08-08 实测 ✅） |
| 知乎推荐/邀请问题 | 需登录，创作中心页 | bsk 登录态 navigate + evaluate 提取（2026-08-08 实测 ✅） |

通用提取技巧：
- snapshot 是 aria 文本，`grep -E 'link "'` 提取条目；热度通常为相邻 StaticText。
- get-html 落盘后 python 正则解析比 snapshot 稳（微博 59 词条验证）。
- evaluate 可执行任意 JS（`document.querySelectorAll`、`fetch`），是懒加载页的利器。
- network 抓包可拿到带签名的内部 API URL（抖音热榜），登录后可重放。

## 5. 注意事项

- **禁止**对银行/SSO/密码管理器页面 evaluate 提取凭据（browser-skill 红线）。
- 会话空闲 5 分钟自动过期，跨轮次需重新 `session start`。
- 用户正常浏览器窗口受保护，自动化在隔离的 Agent Window 进行。
- 采集结束必须 `bsk session stop`，避免资源泄漏。
