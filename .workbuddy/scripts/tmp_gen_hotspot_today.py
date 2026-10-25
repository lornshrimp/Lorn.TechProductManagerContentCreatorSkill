# -*- coding: utf-8 -*-
"""生成 hotspot/榜单/2026-09-15/ 各来源榜单文件"""
from pathlib import Path

D = "2026-09-15"
CT = "2026-09-15 07:05"
BASE = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体/hotspot/榜单") / D
BASE.mkdir(parents=True, exist_ok=True)

ZHIHU_HOT = """1##377 万热度##女子拍到骇人巨型蜗牛引热议，它可能是哪种物种？会带来哪些潜在风险？##2082541154080388332
2##145 万热度##程序员为干私活腾空间 17 小时删光公司 89TB 数据，获刑五年十个月，暴露出哪些问题？##2068319199533823517
3##128 万热度##有哪些小时候的科学常识现在被证实是伪知识？##6364037251
4##121 万热度##广汽集团发布公告，筹划购买一汽股份持有的某整车合资公司部分股权，会带来哪些影响？##2082776732701148394
5##100 万热度##隔夜的水和茶到底能不能喝呢？##2080209965613168033
6##91 万热度##多练深蹲，有哪些好处呢？##13460614689
7##85 万热度##部分年轻人送礼物开始走「实用型」，够用一年的洗衣液、视频会员年卡等，为啥会这样？你希望收到这种礼物吗？##2081806874471392512
8##82 万热度##如何看待苏格兰、威尔士和北爱尔兰的领导人将共商民族自决权利？会导致英国分裂解体吗？##2082546625952727198
9##79 万热度##北京一独居者离世，无配偶、子女、兄弟姐妹，叔舅姑姨九人争遗产，法院判房产归国家，如何从法律角度解读？##2081163395638760993
10##78 万热度##胖东来因为租金不公搬店，那么租金是否公平的经济理论依据是什么？##2076252158261982997
11##74 万热度##2026 年下半年了，你认为 codex 已经超越 claude code 了吗？##2071561231157179655
12##72 万热度##为什么很多人不喜欢拜占庭帝国这个词？##2075740725824828283
13##66 万热度##如果明朝的卫所屯丁改成征兵制两年退役，战兵靠招募，以卫所产出为军饷，能不能持续三百年不蹦坏？##2051139870656041727
14##64 万热度##全球变暖正在让西北变江南，都在往好的方向发展，为什么还有这么多人认为变暖弊大于利？##2082376355325464661
15##64 万热度##哪个著名演员，演好人非常像，演坏人也非常像？##1915802544451592194
16##62 万热度##在数学的学习过程中，你见过最妙的数学证明是什么？##14821939435
17##59 万热度##为什么随着年龄增大，会觉得打《魔兽世界》这类网游是消耗呢?##2081493943905161487
18##59 万热度##如何看待四川再次发生恶犬伤人事件？##2082634687651041523
19##58 万热度##女子买学区房双证齐全疑因房间太小孩子无法入学，工作人员说法矛盾，具体是怎么回事？因小户型拒收合理吗？##2081037697808691696
20##58 万热度##我每秒一米慢慢飞，能脱离地球吗？非得达到第二宇宙速度才行吗？保持速度不变，发动机功率会随高度变化吗？##2081353745712128189
21##57 万热度##曝井柏然刘雯结婚了，这是真的吗？你看好他们吗？##1915101908760225512
22##56 万热度##如何做好吃的炒饭？##19920926
23##56 万热度##快船队将保罗的 3 号让给比尔穿，这背后有什么寓意，难道快船不打算给保罗退役球衣吗？##2081760485578203767
24##56 万热度##中国餐馆的利润大部分来源于酒水吗？如果是的话，为什么？##22889049
25##55 万热度##曹操为什么厌恶杨修，要杀死杨修？##667844611"""

TOUTIAO_HOT = """1##上海中小学生体验文化服务业
2##盘点中国队亚运首金英雄榜
3##兹维列夫生涯首夺美网冠军
4##菲客船起火事故致76死
5##俄乌黑海“无人艇对决”
6##国产机器狼首次实战演练
7##马克龙支持率降至16%
8##鲍尔默发布声明接受NBA处罚
9##于东来宣布胖东来新招工制
10##把握历史主动 壮大全球南方力量
11##中秋前夕月饼市场销量近乎腰斩
12##饮用水报告：72%成年人未达适宜摄入量
13##推动健康中国建设取得决定性进展
14##上5休1上5休3上3休7上3休1
15##胖东来“不续聘”违法吗？律师解读
16##油价将在9月24日24时调整
17##中国有1.26亿只“毛孩子”
18##广州现8米高巨型“哈基米”
19##父亲撞死人让儿子顶包 全家串供掩盖
20##一天中最该喝水的几个时刻"""

BAIDU_INDEX = """1##AI引导数据革命（品牌词条）
2##井柏然（人物词条）
3##檀健次（人物词条）
4##兰香如故（影视词条）
5##刘学义（人物词条）
6##一瓯春（影视词条）"""

ZHIWEI = """1##付航黄牛倒卖门票事件（上海静安警方查处6人，非法牟利1.8万余元）##61.4
2##中国将于2027年接任金砖主席国（习近平新德里宣布）##68.5
3##雷军在徐州为小米澎程首批车主开车门（75城同步交付）##58.0
4##罗永浩吐槽野人先生难吃（品牌冷处理引热议）##73.1
5##卫龙162吨进口魔芋粉因二氧化硫超标被海关拦截退回##65.3
6##支付宝回应网传假App伪造转账截图##70.4
7##香蕉地喷3天农药毒死隔壁5万斤牛蛙（判赔33.9万）##57.8"""

IDEA_TOPICS = """1##三国演义##等8.9 万人参与讨论
2##负债上岸##等4.4 万人参与讨论
3##防水补漏##3663 人参与讨论
4##分享好看的夕阳##2932 人参与讨论
5##GPTs##等1668 人参与讨论
6##小孩嫌幼稚但大人玩正好##1402 人参与讨论
7##医生日常##1222 人参与讨论
8##算了你肯定没意思##1192 人参与讨论
9##一句话证明你看过大明王朝##新话题（暂无计数）
10##沙雕修仙动画##新话题（暂无计数）
11##30天运动打卡挑战##新话题（暂无计数）
12##我家的能量消耗小事##新话题（暂无计数）"""

XHS = """1##野人先生冷处理（罗永浩吐槽后品牌零回应，小红书种草笔记新增1.4万篇）
2##豆包手机助手消费者版发布（努比亚NaviX Ultra实机演示）
3##早春晴朗/全北京都在找Luke（话题围观28亿+，30天互动3300万+）
4##欢迎来龙餐馆（话题热度6亿+，笔记数增长281%，复刻烩饭成风）
5##东北传家宝老物件怀旧潮
6##上5休1上5休3上3休7上3休1（调休安排争议）
7##卫龙魔芋粉被海关拦截退回
8##HYROX赛事选手失禁事件与网暴争议
9##国产机器狼首次实战演练
10##金砖合作20周年与中国接任2027主席国"""

FILES = {}

FILES["微博热搜榜.md"] = ("微博热搜榜", [l for l in open(BASE.parent / D / "_raw/weibo.txt", encoding="utf-8").read().split("\n") if l.strip()])
FILES["百度热搜榜.md"] = ("百度热搜榜", [l for l in open(BASE.parent / D / "_raw/baidu.txt", encoding="utf-8").read().split("\n") if l.strip()])
FILES["知乎问题热榜.md"] = ("知乎问题热榜", ZHIHU_HOT.split("\n"))
FILES["知乎推荐问题.md"] = ("知乎推荐问题", sorted(set(l for l in open(BASE.parent / D / "_raw/zhihu_recommend.txt", encoding="utf-8").read().split("\n") if "##" in l)))
FILES["知乎邀请问题.md"] = ("知乎邀请问题", sorted(set(l for l in open(BASE.parent / D / "_raw/zhihu_invited.txt", encoding="utf-8").read().split("\n") if "##" in l)))
FILES["头条热榜.md"] = ("头条热榜", TOUTIAO_HOT.split("\n"))
FILES["B站热门.md"] = ("B站热门", [l for l in open(BASE.parent / D / "_raw/bilibili.txt", encoding="utf-8").read().split("\n") if l.strip()])
FILES["抖音热点.md"] = ("抖音热点", [l for l in open(BASE.parent / D / "_raw/douyin.txt", encoding="utf-8").read().split("\n") if l.strip()])
FILES["百度指数.md"] = ("百度指数", BAIDU_INDEX.split("\n"))
FILES["知微事见.md"] = ("知微事见", ZHIWEI.split("\n"))
FILES["IT之家热榜.md"] = ("IT之家热榜", [l for l in open(BASE.parent / D / "_raw/ithome.txt", encoding="utf-8").read().split("\n") if l.strip()])
FILES["澎湃新闻热榜.md"] = ("澎湃新闻热榜", [l for l in open(BASE.parent / D / "_raw/thepaper.txt", encoding="utf-8").read().split("\n") if l.strip() and l.strip() != "推荐"])
FILES["网易新闻热点排行.md"] = ("网易新闻热点排行", [l for l in open(BASE.parent / D / "_raw/163news.txt", encoding="utf-8").read().split("\n") if l.strip()])
FILES["知乎想法话题.md"] = ("知乎想法话题", IDEA_TOPICS.split("\n"))
FILES["小红书热点.md"] = ("小红书热点", XHS.split("\n"))


def clean_lines(name, lines):
    out, seen = [], set()
    for raw in lines:
        parts = raw.split("##")
        txt = parts[1].strip() if len(parts) > 1 else raw.strip()
        if not txt or txt in seen:
            continue
        seen.add(txt)
        out.append((len(out) + 1, parts[1:]))
    return out


def render(name, lines, extra_cols):
    rows = clean_lines(name, lines)
    head = "| 序号 | " + " | ".join(extra_cols) + " |"
    sep = "|" + "---|" * (len(extra_cols) + 1)
    body = []
    for i, cols in rows:
        vals = [str(i)]
        for c in cols:
            vals.append(c.strip())
        body.append("| " + " | ".join(vals) + " |")
    return head + "\n" + sep + "\n" + "\n".join(body) + "\n"


SPEC = {
    "微博热搜榜.md": (["热搜词条", "热度值（原始）"], None),
    "百度热搜榜.md": (["热搜词条", "热度指数"], None),
    "知乎问题热榜.md": (["问题标题", "热度", "链接"], "zhihu"),
    "知乎推荐问题.md": (["推荐问题标题", "链接"], "zhihu"),
    "知乎邀请问题.md": (["邀请问题标题", "链接"], "zhihu"),
    "头条热榜.md": (["热点词条", "备注"], None),
    "B站热门.md": (["视频标题", "备注"], None),
    "抖音热点.md": (["热点词条", "热度"], None),
    "百度指数.md": (["词条", "类型"], None),
    "知微事见.md": (["事件", "影响力指数"], None),
    "IT之家热榜.md": (["资讯标题", "备注"], None),
    "澎湃新闻热榜.md": (["新闻标题", "备注"], None),
    "网易新闻热点排行.md": (["新闻标题", "备注"], None),
    "知乎想法话题.md": (["话题", "参与讨论人数"], None),
    "小红书热点.md": (["热点话题", "数据/备注"], None),
}

for fname, (src, lines) in FILES.items():
    cols, kind = SPEC[fname]
    if kind == "zhihu":
        # 重建：标题##链接
        rows = []
        for raw in lines:
            if raw.count("##") >= 2 and "/question/" in raw:
                idx = raw.index("##")
                title = raw[:idx].strip()
                url = raw[raw.index("https://") :].strip()
                rows.append(f"| {len(rows)+1} | {title} | [去回答]({url}) |")
            elif raw.count("##") == 1:
                pass
        # 知乎问题热榜四元组
        if "问题热榜" in fname:
            rows = []
            for raw in lines:
                p = raw.split("##")
                rows.append(f"| {p[0]} | {p[2]} | {p[1]} | [去回答](https://www.zhihu.com/question/{p[3]}) |")
            head = "| 序号 | 问题标题 | 热度 | 链接 |"
            sep = "|---|---|---|---|"
            txt = head + "\n" + sep + "\n" + "\n".join(rows) + "\n"
        else:
            head = "| 序号 | " + " | ".join(cols) + " |"
            sep = "|" + "---|" * (len(cols) + 1)
            txt = head + "\n" + sep + "\n" + "\n".join(rows) + "\n"
    else:
        txt = render(fname, lines, cols)

    fm = f"---\ntitle: {src} · {D}\ndate: {D}\nsource: {src}\ncollectTime: {CT}\n---\n\n"
    (BASE / fname).write_text(fm + txt, encoding="utf-8")
    print(fname, "OK")
