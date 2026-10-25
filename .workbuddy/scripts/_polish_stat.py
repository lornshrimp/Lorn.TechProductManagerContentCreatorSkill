# -*- coding: utf-8 -*-
"""润色稿 vs 草稿：正文差异率、句长标准差、连接词密度、公式句、修辞统计。
用法: python _polish_stat.py <草稿路径> <润色稿路径>
"""
import re
import sys
import difflib
from pathlib import Path

MARKERS = ["## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 视觉与配图",
           "## 配图搜索替换指令", "## 参考来源", "## 润色说明", "## SEO 关键词"]


def body_of(p):
    t = Path(p).read_text(encoding="utf-8", errors="ignore")
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e != -1:
            t = t[e + 4:]
    t = re.sub(r"^#\s+.*$", "", t, flags=re.MULTILINE)
    cut = len(t)
    for m in MARKERS:
        i = t.find(m)
        if i != -1:
            cut = min(cut, i)
    return t[:cut]


def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def sents(t):
    t = re.sub(r"[#*>`\-\|\s]+", "", t)
    parts = [x for x in re.split(r"[。！？；\n]", t) if x.strip()]
    return [p for p in parts if cn(p) > 0]


def main():
    draft, polish = sys.argv[1], sys.argv[2]
    a, b = body_of(draft), body_of(polish)
    na, nb = cn(a), cn(b)
    ra = re.sub(r"\s+", "", a)
    rb = re.sub(r"\s+", "", b)
    sm = difflib.SequenceMatcher(None, ra, rb, autojunk=False)
    ratio = sm.ratio()
    diff_rate = (1 - ratio) * 100

    def stats(t, name):
        ss = sents(t)
        L = [cn(s) for s in ss]
        mean = sum(L) / max(len(L), 1)
        var = sum((x - mean) ** 2 for x in L) / max(len(L), 1)
        std = var ** 0.5
        paras = [p for p in t.split("\n\n") if cn(p) > 0]
        pL = [len([x for x in re.split(r"[。！？；]", p) if cn(x) > 0]) for p in paras]
        pm = sum(pL) / max(len(pL), 1)
        pstd = (sum((x - pm) ** 2 for x in pL) / max(len(pL), 1)) ** 0.5
        conn = sum(len(re.findall(k, t)) for k in ["然而", "此外", "因此", "同时", "并且", "更重要的是", "综上"])
        fml = sum(len(re.findall(k, t)) for k in [
            "不是[^。！？]{0,25}而是", "不只是[^。！？]{0,25}更是",
            "与其说[^。！？]{0,25}不如说", "不仅[^。！？]{0,25}而且"])
        xiang = len(re.findall(r"像[^。！？]{0,20}一样", t))
        q = len(re.findall(r"[？?]", t))
        return dict(name=name, chars=cn(t), sents=len(ss), mean=mean, std=std,
                    paras=len(paras), pstd=pstd, conn=conn,
                    conn_per_k=conn / max(cn(t) / 1000, 0.001), fml=fml, xiang=xiang, q=q)

    sa, sb = stats(a, "草稿"), stats(b, "润色稿")
    print(f"草稿正文 {na} 字 / 润色稿正文 {nb} 字  → 去字率 {(na-nb)/max(na,1)*100:.2f}%")
    print(f"相似度 {ratio:.4f}  差异率 {diff_rate:.2f}%")
    for s in (sa, sb):
        print(f"[{s['name']}] 句数 {s['sents']} 均长 {s['mean']:.1f} 标准差 {s['std']:.1f} | "
              f"段 {s['paras']} 段长标准差 {s['pstd']:.1f} | 连接词 {s['conn']} ({s['conn_per_k']:.2f}/千字) | "
              f"公式句 {s['fml']} | 像…一样 {s['xiang']} | 问号 {s['q']}")
    out = Path(__file__).resolve().parent / "_polish_stat_out.txt"
    out.write_text(f"{na}\t{nb}\t{diff_rate:.2f}\t{sa['std']:.1f}\t{sb['std']:.1f}\t"
                   f"{sa['conn_per_k']:.2f}\t{sb['conn_per_k']:.2f}\t{sa['fml']}\t{sb['fml']}\t"
                   f"{sa['xiang']}\t{sb['xiang']}\t{sa['pstd']:.1f}\t{sb['pstd']:.1f}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
