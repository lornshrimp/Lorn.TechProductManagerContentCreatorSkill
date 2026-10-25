# -*- coding: utf-8 -*-
"""计算去AI化报告所需的统计指标（草稿 vs 润色稿）。"""
import importlib.util, re, statistics, sys
from pathlib import Path

ROOT = Path(r"D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体")
SPEC = ROOT / ".workbuddy" / "scripts" / "规范校验.py"
spec = importlib.util.spec_from_file_location("guifan", str(SPEC))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

DATE = sys.argv[1]
TOPIC = sys.argv[2]
D = ROOT / "drafts" / DATE / TOPIC

def body(p):
    return g.extract_body_text(p)

def cjk(s):
    return re.findall(r"[\u4e00-\u9fff]", s)

out = []
files = {p.name: p for p in D.iterdir() if p.is_file()}
def pick(kw):
    for n, p in files.items():
        if kw in n:
            return p
    return None

draft = pick("草稿-")
polish = pick("润色稿-")
final = pick("终稿-")

CONNECT = ["然而", "此外", "因此", "同时", "并且", "综上", "首先", "其次", "最后", "与此同时", "更重要的是", "值得注意的是", "总而言之", "由此可见"]
FORMULA = [r"不是.{0,30}?而是", r"不只是.{0,30}?更是", r"与其说.{0,30}?不如说", r"不仅.{0,30}?而且", r"从.{0,15}?到.{0,15}?，"]
RHET = ["像", "仿佛", "如同", "似的", "好比", "犹如"]
LIFT = ["标志着", "见证了", "凸显", "彰显", "奠定了坚实基础", "指明了方向", "提供了有力支撑", "具有重要意义", "蓬勃发展", "日益增长", "不断深入", "持续优化", "综上所述", "究其原因"]

for label, p in [("草稿", draft), ("润色稿", polish), ("终稿", final)]:
    if p is None:
        out.append(label + ": MISSING")
        continue
    t = body(p)
    n = len(cjk(t))
    sents = [s for s in re.split(r"[。！？\n]", t) if len(cjk(s)) >= 2]
    lens = [len(cjk(s)) for s in sents]
    paras = [x.strip() for x in re.split(r"\n{2,}", t) if x.strip()]
    plens = [len(cjk(x)) for x in paras]
    conn = sum(t.count(c) for c in CONNECT)
    form = sum(len(re.findall(f, t)) for f in FORMULA)
    rhet = {r: t.count(r) for r in RHET if t.count(r) > 0}
    lift = sum(t.count(x) for x in LIFT)
    bang = t.count("！") + t.count("？")
    out.append("### " + label + "  (" + p.name + ")")
    out.append("  正文字数 = %d" % n)
    out.append("  段落数 = %d，最长段 = %d 字" % (len(paras), max(plens) if plens else 0))
    out.append("  句数 = %d，平均句长 = %.1f，句长标准差 = %.1f" % (len(lens), statistics.mean(lens) if lens else 0, statistics.pstdev(lens) if len(lens) > 1 else 0))
    out.append("  连接词总数 = %d（%.2f/千字）" % (conn, conn * 1000.0 / n if n else 0))
    out.append("  公式句命中 = %d" % form)
    out.append("  修辞标记 = %s（共 %d 次 / %d 种）" % (rhet, sum(rhet.values()), len(rhet)))
    out.append("  抬升腔/假深度词 = %d" % lift)
    out.append("  问号+叹号 = %d" % bang)
    # 生硬连接词清单
    hits = [c for c in CONNECT if t.count(c)]
    out.append("  命中连接词 = " + ",".join(hits))

if draft and polish:
    a, b = body(draft), body(polish)
    na, nb = len(cjk(a)), len(cjk(b))
    out.append("")
    out.append("去字率 = (%d-%d)/%d = %.2f%%" % (na, nb, na, (na - nb) * 100.0 / na))
    sim = g.text_similarity(a, b)
    out.append("草稿/润色稿 difflib 相似度 = %.4f（差异率 %.2f%%）" % (sim, (1 - sim) * 100))

(ROOT / ".workbuddy" / ("_qaihua_" + DATE.replace("-", "") + ".txt")).write_text("\n".join(out), encoding="utf-8")
print("DONE")
