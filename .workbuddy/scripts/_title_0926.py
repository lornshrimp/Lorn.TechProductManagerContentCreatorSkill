#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""标题实测 v2：候选池数量 / 平台首选+备选字数 / 标点 / 溯源 / 两两相似度 / 与终稿相似度"""
import re, difflib, itertools

PLATFORM_LEN = {"知乎": (15, 35), "微信": (15, 25), "头条": (18, 25),
                "百家号": (20, 30), "CSDN": (1, 60)}
SIM = 0.85
TITLE_TRACE_SIM = 0.90
PUNCT = "，。、：；？！…—－·《》〈〉「」『』（）〔〕【】“”‘’\"'-–~!?,:;()[]"
QWORDS = (r"(吗|呢)[\s）」』”\"'）)]*$",
          r"^(为什么|怎么|如何|为何|凭什么|难道|谁能|什么是)",
          r"(是什么|怎么办|怎么算|怎么念|怎么读|怎么选|怎么分|归谁|给谁|是谁|去哪|在哪"
          r"|哪里|哪些|多少|多久|多大|为什么|何时|有没有|了没)[\s）」』”\"'）)]*$")


def n_chars(t):
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", t))


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def punct_check(t):
    n = n_chars(t)
    has = any(c in PUNCT for c in t)
    msg = []
    if not has and n >= 16:
        msg.append("❌零标点且>=16字")
    elif not has and n >= 12:
        msg.append("⚠️零标点12-15字")
    if not ("？" in t or "?" in t):
        for pat in QWORDS:
            if re.search(pat, t):
                msg.append("⚠️设问缺问号")
                break
    return msg


TOPICS = {
    "A-牛肉CPI": {
        "final": "牛肉创两年新高，CPI 只有 0.8%：两个数为什么都是真的",
        "cands": [
            "牛肉创两年新高，CPI 只有 0.8%：两个数为什么都是真的",           # 1
            "牛价创两年新高，为什么 CPI 只有 0.8%？",                       # 2
            "一公斤 71 元的牛肉，是怎么被平均成 0.8% 的？",                  # 3
            "牛肉涨 8.4%，猪肉跌 11.8%：一篮子里的三个方向",                 # 4
            "从 71 元批发价到你的菜篮子，中间隔着三把尺子",                  # 5
            "CPI 量的是平均价，你的钱包量的是自己那只篮子",                   # 6
            "牛肉创两年新高，CPI 却只有 0.8%：物价的账记在谁那一端",          # 7
            "牛少了才贵，不是人多了才贵",                                   # 8
            "一篮子商品里，凭什么让跌的猪肉代表涨的牛肉？",                  # 9
            "牛肉价格创新高，CPI 只有 0.8%：四个观察指标",                  # 10
            "牛肉批发价 71 元创新高：CPI 与菜市场的差在哪？",                # 11
            "平均数的好处是永远正确，坏处是永远不落在你身上",                # 12
            "牛肉 71 元一公斤的账：三把尺子与两个观察指标",                   # 13
            "涨价的和跌价的装进同一只篮子，出来就是一个看不出问题的平均数",    # 14
            "批发价 71 元的牛肉，零售端涨了多少？",                         # 15
            "牛肉与 CPI 的价差：三把尺子、两个观察指标与一个自检法",          # 16
        ],
        "plat": {"知乎": [2, 3], "微信": [6, 12], "头条": [4, 7],
                 "百家号": [10, 13], "CSDN": [13, 16]},
    },
    "B-Anthropic": {
        "final": "Anthropic 自己算出了「钱继续流向有钱人」：AI 的账，不在能力表上，在分配那一栏",
        "cands": [
            "Anthropic 自己算出了「钱继续流向有钱人」：AI 的账，不在能力表上，在分配那一栏",  # 1
            "Anthropic 推演 2030：为什么钱还会继续流向有钱人？",             # 2
            "GDP 涨 32.4%，工资降 11.5%：同一份报告里的两个数",              # 3
            "60% 到 45.2%：一份 AI 经济推演里的劳动份额",                   # 4
            "问题不在生产力，在分配",                                      # 5
            "AI 会提升生产力没有争议，有争议的是提升的那部分归谁？",          # 6
            "效率红利不是没产生，是没往这边流",                             # 7
            "AI 越强工资未必越涨，这份推演来自一家卖算力的公司",              # 8
            "劳动份额从 60% 掉到 45.2%：这张表的重点在分配",               # 9
            "推理成本降了 280 倍，折旧却涨了 56%：AI 的两本账",              # 10
            "钱没有消失，是换了账户",                                      # 11
            "7200 亿美元资本开支与一栏分配数据：AI 的账记在哪一侧",           # 12
            "一家卖算力的公司，为什么算出钱流向有钱人？",                    # 13
            "AI 提效的收益归谁：三个可以自己问的问题",                       # 14
            "报告说并非预测，但它算出的那条分配曲线值得看",                  # 15
            "GDP 涨了三成，切给你的那一份为什么没变",                       # 16
        ],
        "plat": {"知乎": [2, 13], "微信": [8, 6], "头条": [3, 4],
                 "百家号": [9, 12], "CSDN": [10, 14]},
    },
    "C-挂靠参保": {
        "final": "1875 元买一份假劳动关系：挂靠参保打不掉，是因为它的那一头连着需求",
        "cands": [
            "1875 元买一份假劳动关系：挂靠参保打不掉，是因为它的那一头连着需求",  # 1
            "挂靠参保被曝光，为什么这条链条年年打击却年年还在？",              # 2
            "有正规渠道可走的人，为什么会去买一份假劳动关系？",              # 3
            "1875 元一个月：一份明码标价的挂靠参保账单",                    # 4
            "两类需求、两条治理解法：挂靠参保为什么不能只打中介",             # 5
            "渠道存在不等于渠道可用",                                      # 6
            "资质名单上有名字，工地上没有这个人",                           # 7
            "本来该单位交的钱，怎么折进了个人每月的账单",                    # 8
            "1000 元代办费撬 5 万元失业金：这门生意的收益端",                # 9
            "正规的门对一部分人关得太紧，灰色才在门口等着",                  # 10
            "社保挂靠、灵活就业与参保门槛：三个可以自己观察的指标",           # 11
            "打掉中介只是第一刀，第二刀要砍在需求上",                       # 12
            "挂靠参保的账：1875 元买什么，谁在收，谁在付",                  # 13
            "社保没有捷径，但正规的路得让人走得通",                        # 14
            "挂靠参保为什么打不掉：两类需求与两条解法",                     # 15
            "让弱者不用靠运气活着",                                       # 16
        ],
        "plat": {"知乎": [2, 15], "微信": [8, 10], "头条": [4, 9],
                 "百家号": [5, 3], "CSDN": [11, 13]},
    },
}

out = []
for name, d in TOPICS.items():
    out.append("=" * 78)
    out.append(f"【{name}】候选池 {len(d['cands'])} 个  (底线 12)")
    fin = d["final"]
    out.append(f"终稿标题：{n_chars(fin)} 字 | {fin}")
    out.append("-" * 78)
    out.append("候选池逐条（字数 | 标点检查 | 与终稿相似度）：")
    for i, t in enumerate(d["cands"], 1):
        s = sim(t, fin)
        pf = " <== 与终稿超阈" if s >= SIM else ""
        pm = (" " + "/".join(punct_check(t))) if punct_check(t) else ""
        out.append(f"  {i:2d}. {n_chars(t):3d}字 sim{fin and s:.4f}{pf}{pm} | {t}")
    out.append("-" * 78)
    out.append("平台首选 / 备选（字数区间 + 标点 + 溯源 + 与终稿）：")
    chosen = {}
    bad = 0
    for p in ["知乎", "微信", "头条", "百家号", "CSDN"]:
        lo, hi = PLATFORM_LEN[p]
        row = []
        for k, idx in enumerate(d["plat"][p]):
            t = d["cands"][idx - 1]
            n = n_chars(t)
            okN = "OK" if lo <= n <= hi else "FAIL"
            if okN == "FAIL":
                bad += 1
            trace = "溯源OK" if sim(t, d["cands"][idx - 1]) >= TITLE_TRACE_SIM else "溯源FAIL"
            sfin = sim(t, fin)
            flag = " <==与终稿超阈" if sfin >= SIM else ""
            if sfin >= SIM:
                bad += 1
            pm = (" " + "/".join(punct_check(t))) if punct_check(t) else ""
            row.append(f"    {'首选' if k == 0 else '备选'} #{idx:2d} {n:3d}字[{lo}-{hi}]{okN} {trace} "
                       f"sim终稿{sfin:.4f}{flag}{pm} | {t}")
            if k == 0:
                chosen[p] = t
        out.append(f"  {p}:")
        out.extend(row)
    out.append("-" * 78)
    out.append("平台首选两两相似度（须 <0.85）：")
    over = 0
    for a, b in itertools.combinations(sorted(chosen), 2):
        s = sim(chosen[a], chosen[b])
        f = " <== OVER" if s >= SIM else ""
        if s >= SIM:
            over += 1
        out.append(f"    {a} vs {b}: {s:.4f}{f}")
    out.append(f"    超阈对数：{over}")
    out.append(f"  【小结】字数/溯源/终稿违规数：{bad}，两两超阈：{over}")

txt = "\n".join(out)
open(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/.workbuddy/scripts/_title_0926_out.txt",
     "w", encoding="utf-8").write(txt)
print("done")
