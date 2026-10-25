# -*- coding: utf-8 -*-
"""统计对抗指标实测：草稿 vs 润色稿"""
import sys, io, runpy, re, statistics
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
CHECKER = BASE / ".workbuddy" / "scripts" / "规范校验.py"

buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
ns = runpy.run_path(str(CHECKER), run_name="_notmain_")
sys.stdout = old
extract_body_text = ns["extract_body_text"]

COLLOQUIAL = ["说白了", "结果呢", "其实", "倒是", "你说", "呢？", "吧", "嘛", "挺", "咋", "凭什么", "可就是", "够格", "凑一块", "这儿", "那边"]
CONNECT = ["然而", "此外", "因此", "值得注意的是", "综上所述", "与此同时", "首先", "其次", "最后", "并且", "综上", "总之", "由此可见"]
FORMULA = [r"不仅.{0,20}而且", r"不是.{0,15}而是", r"与其说.{0,15}不如说", r"从.{1,8}到.{1,8}，"]


def analyze(path):
    t = extract_body_text(path)
    cn = len(re.findall(r"[\u4e00-\u9fff]", t))
    sents = [s for s in re.split(r"[。！？]", t) if len(re.findall(r"[\u4e00-\u9fff]", s)) > 0]
    lens = [len(re.findall(r"[\u4e00-\u9fff]", s)) for s in sents]
    sd = statistics.pstdev(lens) if len(lens) > 1 else 0
    paras = [p for p in t.split("\n") if len(re.findall(r"[\u4e00-\u9fff]", p)) > 20]
    psent = [len([s for s in re.split(r"[。！？]", p) if re.findall(r"[\u4e00-\u9fff]", s)]) for p in paras]
    psd = statistics.pstdev(psent) if len(psent) > 1 else 0
    lowfreq = sum(t.count(w) for w in COLLOQUIAL)
    conn = sum(t.count(w) for w in CONNECT)
    formula = sum(len(re.findall(p, t)) for p in FORMULA)
    simile = len(re.findall(r"像.{0,12}一样", t))
    rhet = len(set(re.findall(r"(像|仿佛|如同|似的|好比|宛如|一样)", t)))
    return {
        "cn": cn,
        "sents": len(sents),
        "sent_len_sd": sd,
        "para_sd": psd,
        "lowfreq_per500": lowfreq / (cn / 500),
        "conn_per1000": conn / (cn / 1000),
        "formula": formula,
        "simile": simile,
        "rhet_kinds": rhet,
        "lowfreq_raw": lowfreq,
        "conn_raw": conn,
    }


a, b = Path(sys.argv[1]), Path(sys.argv[2])
ra, rb = analyze(a), analyze(b)
out = ["== 草稿 =="]
for k, v in ra.items():
    out.append(f"{k}: {v if not isinstance(v, float) else round(v, 2)}")
out.append("== 润色稿 ==")
for k, v in rb.items():
    out.append(f"{k}: {v if not isinstance(v, float) else round(v, 2)}")
txt = "\n".join(out)
(BASE / ".workbuddy" / "_c_stat.txt").write_text(txt, encoding="utf-8")
print(txt)
