# 项目长期记忆（MEMORY.md）

## deai-hotspot Skill 使用要点（2026-07-29 发现，2026-08-07 更新）
- 位置：`.github/skills/deai-hotspot/`（非标准 `.workbuddy/skills` 路径，Skill 工具无法直接调用，需手动 Read `SKILL.md` 与 `references/adapter-*.md`）。
- **采集通道（2026-08-07 最终版）**：**① BrowserSkill（腾讯开源，首选）**：`bsk.exe`（~/.local/bin）+ Edge 扩展，驱动用户真实浏览器，可读 JS 渲染+登录态页面（知乎/微博等）。命令：`bsk session start` → `bsk navigate --session <id> URL` → `bsk get-html/snapshot --session <id>`；`bsk doctor -v` 自检。② Python urllib 直连（SSR 源快速通道）。③ WebSearch（兜底）。不可用：agent-browser/browser-act（Chromium 下载超时/环境删除保护）、WebFetch（返空）。**deai-hotspot skill 已固化 bsk 优先流程（SKILL.md 章节 0 + references/adapter-bsk.md 手册，含各源命令与反爬绕过）**。
- **环境限制要点**：本环境对所有"删除/重命名/替换"操作强制走回收站且回收站不可用 → shell 写文件（curl -o、重定向）、npm 安装、应用日志滚动全部受限；**下载用 Python urllib 写 %TEMP%，交付文件用 Write 工具**。
- 输出规范：原始榜单 `hotspot/榜单/{日期}/{来源}.md`（含 YAML frontmatter），融合榜单 `hotspot/榜单/{日期}/融合榜单.md`（TOP20 + 各平台速览）。
- 不可用/降级源（应跳过并标注）：知乎想法话题、知乎想法热榜（接口失效❌）、百度指数（仅行业品牌榜⚠️）、头条/澎湃热榜模块改版（降级为搜索词+推荐流）。

## 双渠道热点核对法（2026-08-07 沉淀）
- 场景：用户另有第三方渠道采集同日榜单，需与 AI 渠道交叉核对。
- 步骤：① 读用户渠道全量文件（融合榜+各平台）作基准；② AI 渠道 WebSearch 重采；③ 平台级对照 + 标题模糊匹配（相似度>0.8 视为同一热点）；④ 输出三分类：**双渠道共识**（选题主依据）/ **AI 渠道独有补充** / **用户渠道独有**（多为快照口径差，非冲突）；⑤ 附平台一致性评级（如 B站 TOP5 双渠道完全一致=高置信）。
- 关键洞察：百度/网易/澎湃等平台抓取快照随时刻剧烈变化，融合时应以"跨平台重复出现"为权重；聚合站缓存（抖音/知乎）可能含数日前元素，引用需核对时间戳。
