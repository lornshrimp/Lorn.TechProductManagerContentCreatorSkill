# -*- coding: utf-8 -*-
"""为 B 题知乎/微信稿按信号增配第 2 张配图（打破全平台 1 张同质化）。"""
import re, pathlib, sys

sys.stdout.reconfigure(encoding="utf-8")
D = pathlib.Path(r"drafts/2026-09-15/广汽收购一汽合资股权-合资时代退出的定价权")


def head_body(text):
    i = text.find("[封面图提示词]")
    return text[:i] if i > 0 else text


JOBS = {
    "知乎-广汽买一汽的合资股权这到底是重组还是清算.md": {
        "anchor": "把这行字放回四十年，退出的主角早换了",
        "scene": '一条四十年时间轴横贯画面：左侧是 1994 年标注「50% 上限」的红色闸门，向右闸门逐级打开，2022 年处完全敞开；轴下方是两支交接的手，一支袖口写着一汽，一支写着广汽，中间一枚股权凭证。冷蓝灰主色，中段一处暖橙高光落在交接的凭证上。扁平矢量风格，画面顶部留白。',
        "prompt": "A 16:9 editorial timeline illustration spanning four decades: a red gate marked with an implied cap on the left gradually opening, fully open at the right end; below the axis two hands exchange an equity certificate, sleeves in cool slate and deep blue. Muted slate-blue palette with a single warm amber highlight on the certificate. Flat vector style, generous negative space at top. no text, no faces, no logos",
        "alt": "四十年股比放开与股权交接示意",
        "basis": '取点依据：该节承载全篇唯一的四十年政策时间轴（1994/2004/2018-2022 四个时间点），属「连续 2 个以上关键数据 + 抽象沿革需读者想象」双信号命中，故在该节配第 2 张。',
    },
    "微信-合资车的退场定价权这次落在谁手里.md": {
        "anchor": "四、产能三条退路，谁拿到处置权谁付钱",
        "scene": '三条并排的道路由同一点分岔：左侧通向一座关闭的厂房（大门上锁），中间通向正在改造的车间（吊臂与火花），右侧通向一条贴着双品牌标识的共用产线。三条路的起点处站着一个持笔的人影。冷灰蓝背景，三条路各有一处暖色光。竖版构图，顶部留白。',
        "prompt": "A 9:16 vertical editorial illustration of three roads diverging from one point: the left ends at a locked closed factory, the middle at a workshop under renovation with cranes and sparks, the right at a shared production line bearing faint dual-brand marks; a small figure holding a pen stands at the fork. Cool slate-grey background with warm accents on each road. Flat vector style, generous top negative space. no text, no faces, no logos",
        "alt": "产能关停改造代工三条退路示意",
        "basis": '取点依据：该节并列呈现关停/改造/代工三条成本路径，属「对比论证 + 抽象成本结构需读者想象」双信号命中，故在该节配第 2 张。',
    },
}

for fname, cfg in JOBS.items():
    p = D / fname
    t = p.read_text(encoding="utf-8")
    body = head_body(t)
    cnt = body.count(cfg["anchor"])
    print(fname[:6], "anchor count in body =", cnt)
    if cnt != 1:
        print("  SKIP: anchor not unique")
        continue

    blk = (
        "### [配图2]\n"
        "- **锚文本**：" + cfg["anchor"] + "\n"
        '- **插入位置**：在"' + cfg["anchor"] + '"（小标题）之后插入 [配图2]\n'
        "- **画面内容**：" + cfg["scene"] + "\n"
        "- **AI 提示词**：" + cfg["prompt"] + "\n"
        "- **alt 文本**：" + cfg["alt"] + "\n"
        "- " + cfg["basis"] + "\n"
    )

    m = re.search(r"(?m)^## 配图详情[ \t]*$", t)
    assert m, "no 配图详情"
    nxt = re.search(r"(?m)^## ", t[m.end():])
    end = m.end() + nxt.start()
    seg = t[m.end():end].rstrip("\n")
    t = t[:m.end()] + seg + "\n\n" + blk + "\n" + t[end:]

    m2 = re.search(r"(?m)^## 配图搜索替换指令[ \t]*$", t)
    nxt2 = re.search(r"(?m)^## ", t[m2.end():])
    end2 = m2.end() + nxt2.start() if nxt2 else len(t)
    seg2 = t[m2.end():end2].rstrip("\n")
    t = t[:m2.end()] + seg2 + "\n2. 在正文找到唯一锚文本「" + cfg["anchor"] + "」→ 在该小节之后插入配图2，并填写 alt 文本\n\n" + t[end2:]

    p.write_text(t, encoding="utf-8")
    print("  >>> inserted 配图2")
