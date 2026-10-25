# -*- coding: utf-8 -*-
from pathlib import Path

D = "2026-09-15"
CT = "2026-09-15 07:09"
BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单") / D

INFOQ = """两个 Token 就让 Kimi“变成”Claude？前 Google DeepMind 研究员意外撞上大模型的蒸馏疑云
为何前沿 AI 实验室要隐藏链式推理？
模型一模一样，Token 却相差 70 倍？三项实测揭开 AI 编程工具的成本黑洞
V4.1 Flash 全面超越，开发者为何还在喷 DeepSeek：缺的不是能力，是软件工程思维
DeepSeek 突然切模型，暴露了 AI 公司的“工程断层”
从沙箱到执行边界：蚂蚁 AI Agent 的大规模企业级实践｜QCon 上海
Google Mantis：一款旨在减少误报的基于智能代理的漏洞扫描框架
Neovim 加入 vim.async：告别回调地狱
AI 的新用法，被这群 Builder 带到了外滩大会开发者日
怒斥加密货币是旁氏骗局、放弃 80% 就业机会也不用 AI 写代码！Kotlin“J 神”：AI 会让工程师变成可替换的齿轮
当 AI 写出更多代码，企业为什么没有跑得更快？| JDD 大会现场观察
AI Coding 的下一步不是写得更快，而是可验收：蚂蚁数科 Harness 工程实践
破除人形崇拜！京东用“狼族”军团重做物理 AI
AI Coding 提速之后，如何补上稳定性“最后一公里”？快手柯南 AI 实践
Snowflake 落地中国两年：迈向智能体企业时代，关键在上下文
“数据比模型重要”成了共识，接下来拼什么？
AI 有了“工号”，数据平台长出了手：我在 Snowflake World Tour 看到的三个变化
“我们在拿生命做赌注”：造 AI 的人为何开始密集预警？
Figma 如何利用 AI 代理提升安全性
AMD 发布锐龙 AI Max PRO 400 系列，端侧智能体走向多模型协同"""

HUXIU = """再造“增长极”，广州这次要“复制”上海？
B站或许从没想过成为第二个谁
中国在AI领域优势可能构成国家安全风险？
Hyrox回应“失禁”事件
胖东来未来员工合同四年不续签
中国最有钱的几大公司，突然拼命借钱
大厂AI竞赛，从技术周期走进资本周期
阿里+腾讯，一个季度在AI上砸了1000亿
在市区50公里外读985，一抬头就是旷野
主动吃苦：选择学农的年轻人
迟到七年的折叠屏：苹果把首创权让给了三星，把定价权留给了自己
黄牛炒到9.9万？折叠屏的“大众普及”可能永远不会来
11年后，全网重审内娱名著《花少2》
新鲜零食火了，但钱还没敢进来
未来20年（2026–2045）中国房价走势分析报告（12000字长文）
内娱真的完了，连胡歌、宋佳都没戏拍了？
带外国人进中国工厂，一张票能卖到1.5万美元
911中，摩根士丹利2687名员工为何能逃生？
新CFO即将到岗，DeepSeek要做下一个豆包？
发展AI，要有重大变化？马斯克、奥尔特曼、阿莫代伊罕见达成一致，美股芯片股盘前大跌
“宠物月入1万5，我成了家里的‘啃狗族’”
花2万报AI培训班的年轻人，没有等到“包就业”
物企下半场：管得多，不如赚得到
《经济学人》说中国车企搬向全球，但这只是开始……
出海即盈利，7家车企净赚了400亿
万字长文深谈：把电车卖到全球第一之后，该轮到我们写电车全球标准了
不会追热点，天天都亏钱？散户学这招，账户能翻20倍？"""

PINGWEST = """图形学大佬、前微软全球研究合伙人童欣加盟，Meshy 下一步要做实时互动世界
实测最新版「豆包手机」助手：所有手机里的 AI 都该变成它这样
AI Costco，开始卖自有品牌了
OpenAI的担心反而是具身的正路？这家具身大脑公司已经先往前一步
因为这个功能，高德支棱起来了
「设备即环境」：这个北大系公司想告诉所有人，端侧模型才是未来
我们见了 B 站最会“整活”的 AI UP 主，拿到他们的创造心得
会翻译的耳机走进东南亚：3C卖家如何拓展智能音频新场景
一文看完苹果发布会：折叠iPhone又给所有手机上了一课（除了AI）
深度｜Seedance宇宙，和它的裂痕
AI越会写代码，Arm越要争取开发者
AI开始干活，Arm把CPU推回台前
百度搭子搭配小度，智能体既要办公也要“管家”
DEMO | 齐俊元重启 12 年前的 Today.ai：它可能是当下最主动的Personal AI
华为用两块屏幕，把移动设备带向了一个新方向"""


def write(name, source, body, extra=""):
    fm = f"---\ntitle: {source} · {D}\ndate: {D}\nsource: {source}\ncollectTime: {CT}\n---\n\n"
    (BASE / name).write_text(fm + body + ("\n" + extra if extra else ""), encoding="utf-8")
    print(name, "OK")


def tbl(lines, cols, note=None):
    head = "| 序号 | " + " | ".join(cols) + " |"
    sep = "|" + "---|" * (len(cols) + 1)
    rows = []
    for i, t in enumerate(lines, 1):
        vals = [str(i)] + [t] + ["—"] * (len(cols) - 1)
        rows.append("| " + " | ".join(vals) + " |")
    s = head + "\n" + sep + "\n" + "\n".join(rows)
    if note:
        s += "\n\n" + note
    return s


write("InfoQ中国热点.md", "InfoQ中国热点", tbl(INFOQ.strip().split("\n"), ["文章标题", "备注"], "> 采集方式：bsk 登录态 navigate `infoq.cn/hotlist?tag=day` + 滚动 + evaluate 提取（JS 渲染 + 懒加载，urllib 直连返回空）。已过滤作者/策划/译者行与摘要行，保留 20 条实质文章标题。"))
write("虎嗅48h热文.md", "虎嗅48h热文", tbl(HUXIU.strip().split("\n"), ["文章标题", "备注"], "> 采集方式：bsk 登录态 navigate `huxiu.com` + 滚动 1200px + evaluate 提取（urllib 直连被 WAF 拦截）。已剔除站内升级提示与纯摘要行。"))
write("品玩一周精选.md", "品玩一周精选", tbl(PINGWEST.strip().split("\n"), ["文章标题", "备注"], "> 采集方式：bsk 登录态 navigate `pingwest.com` + 滚动 + evaluate 提取 `a[href*='/a/']`（JS 渲染，urllib 直连返回空）。已按标题去重（原始 30 行 → 15 条唯一标题）。"))

PIN_BODY = """## 采集结果

**状态：❌ 接口不可用（422 Unprocessable Entity）**

- 目标 URL：`https://www.zhihu.com/pin/hot`
- 采集通道：bsk 登录态 navigate + evaluate `document.title`
- 返回结果：`||Unprocessable Entity`（HTTP 422，页面无任何可渲染内容）
- 判定依据：bsk 登录态下页面标题为空、正文为空，非"未登录"导致的重定向，而是服务端直接返回 422
- 历史对照：该接口自 2026-09-11 起连续 5 日（09-11/09-12/09-13/09-14/09-15）返回 422，属**平台侧功能下线**，非采集执行问题
- 降级处理：知乎系"想法"类内容改由 `知乎想法话题.md`（创作中心推荐话题，可正常采集）覆盖
"""

write("知乎想法热榜.md", "知乎想法热榜", PIN_BODY)
