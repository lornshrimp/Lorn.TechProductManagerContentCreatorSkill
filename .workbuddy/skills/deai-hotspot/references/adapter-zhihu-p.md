# 知乎想法热榜适配器

## 页面信息
- URL：`https://www.zhihu.com/pin/hot`（已失效）
- 类型：知乎想法/帖子热榜
- 状态：❌ **不可用**（URL 返回 422）

## 已知不可用的 URL（记录避免重复尝试）
- `https://www.zhihu.com/pin/hot` — 返回 422 Unprocessable Entity
- `https://www.zhihu.com/pin/hot?page=1` — 返回 422 Unprocessable Entity

## 问题描述
该接口疑似已变更或需要特定鉴权（如 API Token）。当前无已知可用的浏览器页面或 API 接口能获取知乎想法热榜数据。

## 提取字段
该适配器当前**无法提取**任何字段。

## 替代方案
如果需求强烈，可考虑：
1. 逆向工程知乎移动端 API
2. 使用第三方聚合站
3. 放弃该来源（想法热榜在知乎整体流量中占比较小）
