# -*- coding: utf-8 -*-
"""差异率 / 保真比 / 两两相似度 实测（正文口径）"""
import io
import sys
import difflib
import importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
spec = importlib.util.spec_from_file_location("chk", ROOT / ".workbuddy/scripts/规范校验.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)


def body(p):
    return chk.extract_body_text(Path(p))


def sim(a, b):
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "diff":
        a, b = body(sys.argv[2]), body(sys.argv[3])
        r = sim(a, b)
        # 字符级差异率：1 - 相似度（近似"改动比例"）
        print(f"草稿 {len(a)} 字 → 润色 {len(b)} 字；相似度 {r:.4f}；差异率 {(1-r)*100:.2f}%")
    elif mode == "plat":
        final = sys.argv[2]
        fb = body(final)
        fn = chk.count_body_chars(Path(final))
        print(f"终稿 {fn} 字")
        rows = []
        for p in sys.argv[3:]:
            n = chk.count_body_chars(Path(p))
            b = body(p)
            rows.append((Path(p).name, n, n / fn * 100 if fn else 0, sim(b, fb) * 100))
        for nm, n, ratio, s in rows:
            flag = "OK" if ratio >= 70 else "LOW"
            print(f"  {nm}: {n} 字 / 保真 {ratio:.1f}% [{flag}] / 与终稿相似 {s:.2f}%")
        print("  两两相似度：")
        mx = 0
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                s = sim(body(sys.argv[3 + i]), body(sys.argv[3 + j])) * 100
                mx = max(mx, s)
                print(f"    {rows[i][0]} × {rows[j][0]} = {s:.2f}%")
        print(f"  最大两两相似度 = {mx:.2f}%")
