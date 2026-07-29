# 项目长期记忆（MEMORY.md）

## deai-hotspot Skill 使用要点（2026-07-29 发现）
- 位置：`.github/skills/deai-hotspot/`（非标准 `.workbuddy/skills` 路径，Skill 工具无法直接调用，需手动 Read `SKILL.md` 与 `references/adapter-*.md`）。
- 本环境无 Playwright 浏览器，原 Skill 的浏览器自动化不可用。替代采集方案：
  - **SSR 静态源用 WebFetch**：百度热搜 `top.baidu.com/board?tab=realtime`、IT之家、澎湃、网易、InfoQ(`infoq.cn/hotlist?tag=day`)、虎嗅、品玩、知微事见 `ef.zhiweidata.com`、B站 `bilibili.com/v/popular/rank/all`。
  - **需登录 / JS 渲染源用 WebSearch + 聚合站**：微博、知乎（问题/推荐/邀请）、抖音、头条；参考 `uapis.cn/hotboard`、`rebang.today`、`neodrop.ai` 做跨榜验证。
- 输出规范：原始榜单 `hotspot/榜单/{日期}/{来源}.md`（含 YAML frontmatter），融合榜单 `hotspot/榜单/{日期}/融合榜单.md`（TOP20 + 各平台速览）。
- 不可用/降级源（应跳过并标注）：知乎想法话题、知乎想法热榜（接口失效❌）、百度指数（需登录⚠️）。
