# -*- coding: utf-8 -*-
"""生成 2026-10-16 各源榜单 md"""
import os, io, sys, pathlib, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
T = os.environ.get("TEMP", ".")
OUT = r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单/2026-10-16"
D = "2026-10-16"
os.makedirs(OUT, exist_ok=True)
CT = "2026-10-16 07:35"
BSK = os.path.join(T, "bsk1016")


def w(name, body):
    pathlib.Path(os.path.join(OUT, name)).write_text(body, encoding="utf-8")
    print("WROTE", name, len(body))


def yaml(title, source):
    return "---\ntitle: %s · %s\ndate: %s\nsource: %s\ncollectTime: %s\n---\n\n" % (title, D, D, source, CT)


def tbl(headers, rows):
    s = "| " + " | ".join(headers) + " |\n|" + "|".join([":--:"] * len(headers)) + "|\n"
    for r in rows:
        s += "| " + " | ".join(str(x) for x in r) + " |\n"
    return s


def rd(name):
    return pathlib.Path(os.path.join(BSK, name)).read_text(encoding="utf-8", errors="replace")


J = json.load(open(os.path.join(T, "urllib1016.json"), encoding="utf-8"))

weibo = json.load(open(os.path.join(T, "weibo1016.json"), encoding="utf-8"))
w("微博热搜榜.md", yaml("微博热搜榜", "微博热搜榜") + "# 微博热搜榜 · %s\n\n" % D + tbl(["#", "话题"], [[i, t] for i, t in enumerate(weibo, 1)]))

baidu = J["百度热搜榜"]
w("百度热搜榜.md", yaml("百度热搜榜", "百度热搜榜") + "# 百度热搜榜 · %s\n\n" % D + tbl(["#", "热搜词"], [[i, t] for i, t in enumerate(baidu, 1)]))

rows = []
for i, t in enumerate(J["头条热榜"], 1):
    p = t.split("##"); nm = p[0]; hv = p[1] if len(p) > 1 else ""
    try:
        hv = "%.1f 万" % (int(hv) / 10000)
    except Exception:
        pass
    rows.append([i, nm, hv])
w("头条热榜.md", yaml("头条热榜", "头条热榜") + "# 头条热榜 · %s\n\n" % D + tbl(["#", "热点", "热度值"], rows))

it = json.load(open(os.path.join(T, "ithome1016.json"), encoding="utf-8"))
w("IT之家热榜.md", yaml("IT之家热榜", "IT之家热榜") + "# IT之家热榜 · %s\n\n" % D + tbl(["#", "标题"], [[i, t] for i, t in enumerate(it, 1)]))

ne = J["网易新闻热点排行"]
w("网易新闻热点排行.md", yaml("网易新闻热点排行", "网易新闻热点排行") + "# 网易新闻热点排行 · %s\n\n" % D + tbl(["#", "标题"], [[i, t] for i, t in enumerate(ne, 1)]))

tp = J["澎湃新闻热榜"]
w("澎湃新闻热榜.md", yaml("澎湃新闻热榜", "澎湃新闻热榜") + "# 澎湃新闻热榜 · %s\n\n" % D + tbl(["#", "标题"], [[i, t] for i, t in enumerate(tp, 1)]))

dy = [(a, b) for a, b in json.load(open(os.path.join(T, "douyin1016.json"), encoding="utf-8")) if a.strip("-# ")]
w("抖音热点.md", yaml("抖音热点", "抖音热点") + "# 抖音热点榜 · %s\n\n" % D + tbl(["#", "热点", "热度"], [[i, a, h] for i, (a, h) in enumerate(dy, 1)]))

hx = [l.strip() for l in rd("huxiu.txt").split("\n") if len(l.strip()) > 8 and "A new bsk" not in l]
seen = []
for t in hx:
    if t not in seen:
        seen.append(t)
w("虎嗅48h热文.md", yaml("虎嗅48h热文", "虎嗅48h热文") + "# 虎嗅 48h 热文 · %s\n\n" % D + tbl(["#", "标题"], [[i, t] for i, t in enumerate(seen, 1)]))

iqrows = ["GitHub新晋顶流REA：当大模型能逆向一切，软件行业还剩什么？", "CLAUDE.md 还是 AGENTS.md？Anthropic 的答案是：以后都不用", "Codex 和 Claude Code 都跑偏了，前 OpenAI 研究员称 Jev 出现前 AI 世界是个悲剧", "Claude 开始自己写程序管理 Agent 了：Anthropic 披露动态工作流架构", "Rails 之父 DHH 狂吹 Rust 快 150 倍，被开发者翻代码后群嘲", "单次RL后训练烧掉260万美元、每步37亿Token，小米披露MiMo-V2.6「规模化强化学习」路线", "模型开放之后，AI能力为什么仍难以复用？", "手机解锁先见 AI，不再先找 App：阶跃星辰首款智能体手机来了，定价 3999", "OpenAI 高管亲述：我们是怎么在一周内做出 Jev 竞品的", "Meta 新模型杀回AI第一梯队，Alexandr Wang 亲述 Muse 7个月翻身内幕"]
w("InfoQ中国热点.md", yaml("InfoQ中国热点", "InfoQ中国热点") + "# InfoQ 中国热点 · %s\n\n" % D + tbl(["#", "标题"], [[i, t] for i, t in enumerate(iqrows, 1)]))

pw = [l.strip() for l in rd("pingwest.txt").split("\n") if len(l.strip()) > 10 and "A new bsk" not in l]
seen = []
for t in pw:
    if t not in seen:
        seen.append(t)
w("品玩一周精选.md", yaml("品玩一周精选", "品玩一周精选") + "# 品玩一周精选 · %s\n\n" % D + tbl(["#", "标题"], [[i, t] for i, t in enumerate(seen, 1)]))

bl = [l.strip() for l in rd("bilibili.txt").split("\n") if len(l.strip()) > 6 and "A new bsk" not in l]
w("B站热门.md", yaml("B站热门", "B站热门") + "# B站热门榜 · %s\n\n" % D + tbl(["#", "标题"], [[i, t] for i, t in enumerate(bl[:40], 1)]))

zwrows = [["1", "康师傅扫码被拉黑危机（消费者扫码三十余瓶全提示未中奖，品牌承认风控误判）", "50.7", "社会"],
          ["2", "男孩被曝衣衫不整跟随母亲游荡（河南周口，家庭监护能力缺失）", "55.9", "社会"],
          ["3", "官方通报女子高铁开免提通话 1 小时（上铁南京客运段通报）", "72.4", "政务"],
          ["4", "伍浩被双开（中科院科技创新发展中心原党委副书记、主任）", "59.1", "企业"],
          ["5", "小鹏正式宣布开始对外卖技术（巴黎汽车峰会发布 XPENG AI ENGINEERING）", "57.2", "企业"],
          ["6", "超格向粉笔赔偿 450 万元（公考课程讲义侵权和解）", "61.6", "企业"],
          ["7", "150 余款 App 拒绝了豆包手机（《屏幕自动化操作声明协议》公示期结束）", "65.3", "企业"]]
w("知微事见.md", yaml("知微事见", "知微事见") + "# 知微事见 · %s\n\n" % D + tbl(["#", "事件", "影响力指数", "分类"], zwrows))

rows = []
for l in rd("zhihu_hot.txt").split("\n"):
    m = re.match(r"^(\d+)##(.*?)##(.*?)##(https://.*)$", l.strip())
    if m:
        rows.append([m.group(1), m.group(2), m.group(3), "[去回答](%s)" % m.group(4)])
w("知乎问题热榜.md", yaml("知乎问题热榜", "知乎问题热榜") + "# 知乎问题热榜 · %s\n\n" % D + tbl(["排名", "热度", "问题", "链接"], rows))

for fn, title in [("zhihu_recommend.txt", "知乎推荐问题"), ("zhihu_invited.txt", "知乎邀请问题")]:
    seen = []
    for l in rd(fn).split("\n"):
        if "##" in l and "zhihu.com/question" in l and "A new bsk" not in l:
            a, u = l.split("##")[0].strip(), l.split("##")[-1].strip()
            if a and u not in [x[1] for x in seen]:
                seen.append((a, u))
    w("%s.md" % title, yaml(title, title) + "# %s · %s\n\n" % (title, D) + tbl(["#", "问题", "链接"], [[i, a, "[去回答](%s)" % u] for i, (a, u) in enumerate(seen, 1)]))

zt = ["读书小分享（4824 人参与）", "每天读书分享（3471 人参与）", "零跑汽车（9.2 万人参与）", "真无线蓝牙耳机（6.2 万人参与）", "AI技术正冲击数学研究领域", "施工现场实拍（1008 人参与）", "捕捉春分限定风光", "游戏考考你", "创业避坑（2062 人参与）", "机器人拥抱AI", "身边的植物园（5501 人参与）", "新疆旅行（1235 人参与）"]
w("知乎想法话题.md", yaml("知乎想法话题", "知乎想法话题") + "# 知乎想法话题 · %s\n\n" % D + tbl(["#", "话题"], [[i, t] for i, t in enumerate(zt, 1)]))

w("知乎想法热榜.md", yaml("知乎想法热榜", "知乎想法热榜") + "# 知乎想法热榜 · %s\n\n> **状态：❌ 不可用**——`https://www.zhihu.com/pin/hot` 返回 HTTP 422 Unprocessable Entity，页面标题为空、body 仅返回 `Unprocessable Entity`。平台侧接口自 2026-09-17 起持续不可用（**连续第 27 日**），已降级采「知乎想法话题」替代。\n" % D)

w("百度指数.md", yaml("百度指数", "百度指数") + "# 百度指数 · %s\n\n> **状态：⚠️ 降级（仅首页推荐位）**——bsk 登录态 `index.baidu.com`；趋势/资讯指数面板显示「没有数据」（更新时段 12~16 时），行业排行子页需异步 RPC 签名接口。首页可见推荐词：肖战、尚公主、嫁金钗、丞磊、醉梦、AI引导数据革命。**连续多日降级。**\n" % D)

xhs = """# 小红书热榜/话题 · %s

> **状态：⚠️ 降级（WebSearch 兜底）**——`xiaohongshu.com/explore` 未登录态仅渲染登录页与页脚，适配器未建。

| # | 趋势 | 说明 |
|:--:|------|------|
| 1 | AI 女团「怀孕待产」营销翻车 | 小红书运营方账号仅 1045 粉，借真人偶像敏感话题制造噱头后被指营销，引发 AI 内容标识与真实性讨论 |
| 2 | Gleaning 秋收户外玩法 | 话题上线 2 周浏览量 1200 万+，笔记互动量增长 400%%+，户外赛道秋收美学 |
| 3 | 「中式辣感」新中式穿搭 | 近 60 天话题热度 8300 万+，笔记互动量暴涨 10 倍 |
| 4 | 螺蛳粉「鞋垫豆干」 | 广州高校圈「鞋垫悬案」出圈，形状误会引发二创 |
| 5 | 双 11「抄作业」退潮 | 大促玩法简化后，用户讨论从比价转向直接下单 |
""" % D
w("小红书热榜话题.md", yaml("小红书热榜话题", "小红书热榜/话题") + xhs)
print("ALL DONE")
