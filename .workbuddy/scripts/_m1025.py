# -*- coding: utf-8 -*-
"""2026-10-25 度量工具：字数/差异率/保真比/两两相似度/锚文本三查"""
import sys, io, re, difflib
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
DATE = "2026-10-25"

BODY_TRUNCATE_MARKERS = [
    "## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 封面图",
    "## 内容简介", "## 互动引导", "## SEO 关键词", "## 配图详情",
    "# 附属内容区域", "## 配图搜索替换指令", "## 参考来源",
    "## 润色说明", "## 发布建议",
]


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    text = re.sub(r"^#\s+.*$", "", text, flags=re.MULTILINE)
    for marker in BODY_TRUNCATE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
            break
    return text


def cjk(path: Path) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", body(path)))


def norm(path: Path) -> str:
    return re.sub(r"\s+", "", body(path))


def sim(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


DIRS = {
    "A": "国办发文减缓AI就业替代-第一级台阶的成本归属",
    "B": "南方区域电力市场正式运行-15分钟一次的电价定价",
    "C": "云南烟草工业负增长-产量涨增加值跌的账",
}
PLATS = ["知乎", "微信", "百家号", "CSDN", "头条"]
RATIO = {"知乎": 0.90, "微信": 0.85, "百家号": 0.70, "CSDN": 0.70, "头条": 0.70}


def find(d: Path, kw: str):
    hits = [p for p in d.glob("*.md") if kw in p.name]
    return hits[0] if hits else None


def run():
    for k, name in DIRS.items():
        d = ROOT / "drafts" / DATE / name
        if not d.exists():
            print(f"!! 缺目录 {name}")
            continue
        print("=" * 78)
        print(f"### {k} {name}")
        draft = find(d, "草稿")
        polish = find(d, "润色稿")
        final = find(d, "终稿")
        for tag, p in [("草稿", draft), ("润色稿", polish), ("终稿", final)]:
            if p:
                print(f"  {tag}: {cjk(p)} 字  ({p.name})")
            else:
                print(f"  {tag}: 缺失")
        if draft and polish:
            a, b = norm(draft), norm(polish)
            dr = 1 - sim(a, b)
            print(f"  草稿→润色稿 差异率: {dr*100:.2f}%  (块 {len(list(difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()))})(需 ≥5%)")
        if final:
            fc = cjk(final)
            plats = {}
            for pl in PLATS:
                p = find(d, pl)
                if not p:
                    print(f"  [{pl}] 缺文件")
                    continue
                c = cjk(p)
                r = c / fc if fc else 0
                flag = "OK" if r >= RATIO[pl] else "❌不足"
                print(f"  [{pl}] {c} 字  保真 {r*100:.1f}%  (底线 {RATIO[pl]*100:.0f}%) {flag}  需≥{int(fc*RATIO[pl])+1}")
                plats[pl] = norm(p)
            mx = 0
            pair = ""
            ks = list(plats)
            for i in range(len(ks)):
                for j in range(i + 1, len(ks)):
                    s = sim(plats[ks[i]], plats[ks[j]])
                    if s > mx:
                        mx, pair = s, f"{ks[i]}×{ks[j]}"
            if mx:
                print(f"  平台两两最高: {mx*100:.2f}%  ({pair})  (<85%)")
            fn = norm(final)
            mx2, mp = 0, ""
            for pl in ks:
                s = sim(plats[pl], fn)
                if s > mx2:
                    mx2, mp = s, pl
            if mx2:
                print(f"  平台vs终稿最高: {mx2*100:.2f}%  ({mp})  (<99%)")


if __name__ == "__main__":
    run()
