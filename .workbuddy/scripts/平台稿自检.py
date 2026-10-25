#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""平台稿自检 —— 补充 规范校验.py 未覆盖的维度。

覆盖：
  1) 封面图比例是否符合各 adapt skill 原文（知乎 16:9 / 微信 16:9 / 百家号 3:2 /
     CSDN 3:2 / 头条 3:2）
  2) [内容简介] 字数上限（知乎 100 / 微信 120 / 头条 80 / 百家号 100 / CSDN 100）
  3) 正文配图张数与锚文本三查（命中 / 唯一 / 同步）
  4) H2 数量门禁（知乎≥4 / 微信≥4 / 百家号≥3 / CSDN≥4 / 头条≥3 / 终稿≥4）
  5) 正文字数与保真比（复用 规范校验.py 的 count_body_chars 口径）

用法：
    python .workbuddy/scripts/平台稿自检.py --date 2026-09-14
    传路径时注意 Git Bash 会转换含中文/OneDrive 的参数：
    先 `cygpath -w <路径>` 再传，或在脚本内用正斜杠绝对路径。

注意：count_body_chars / extract_body_text 只接受 pathlib.Path 对象。
"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("gbjy", HERE / "规范校验.py")
_gbjy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gbjy)

count_body_chars = _gbjy.count_body_chars
extract_body_text = _gbjy.extract_body_text
text_similarity = _gbjy.text_similarity

# 各平台封面图比例（逐字取自 adapt skill 原文，2026-09-14 复核）
COVER_RATIO = {
    "zhihu": ("16:9", ["16:9"]),
    "wechat": ("16:9", ["16:9", "9:16", "1:1"]),   # skill 未固定，示例 16:9
    "baiduhao": ("3:2", ["3:2"]),
    "csdn": ("3:2", ["3:2"]),
    "toutiao": ("3:2", ["3:2"]),
}
# 文件名前缀 -> 平台键
PREFIX_PLATFORM = [
    ("知乎-", "zhihu"),
    ("微信-", "wechat"),
    ("百家号-", "baiduhao"),
    ("CSDN-", "csdn"),
    ("头条-", "toutiao"),
]
INTRO_MAX = {"zhihu": 100, "wechat": 120, "baiduhao": 100, "csdn": 100, "toutiao": 80}
H2_MIN = {"知乎-": 4, "微信-": 4, "百家号-": 3, "CSDN-": 4, "头条-": 3, "终稿-": 4}
# 保真比下限
FIDELITY_MIN = {"知乎-": 0.90, "微信-": 0.85, "百家号-": 0.70, "CSDN-": 0.70, "头条-": 0.70}


def read(p):
    return p.read_text(encoding="utf-8", errors="ignore")


def h2_count(text):
    body = text.split("## 素材溯源", 1)[0]
    return len(re.findall(r"^##\s+", body, flags=re.MULTILINE))


def cover_ratio_ok(text, key):
    want, allowed = COVER_RATIO[key]
    seg = text.split("[封面图提示词]", 1)
    if len(seg) < 2:
        return False, "缺 [封面图提示词]"
    tail = seg[1]
    # 只取封面提示词自身：截到 [内容简介] / ## 配图详情 等下一个标记，避免误扫正文配图提示词里的比例
    cut = len(tail)
    for mk in ("[内容简介]", "## 配图详情", "## 配图搜索替换指令", "\n## "):
        i = tail.find(mk)
        if i != -1:
            cut = min(cut, i)
    block = tail[:cut]
    found = [r for r in ("16:9", "9:16", "3:2", "1:1", "4:3") if r in block]
    if not found:
        return False, "封面提示词未见比例标注"
    bad = [r for r in found if r not in allowed]
    if bad:
        return False, f"封面比例 {bad} 不符合技能原文（应为 {want}）"
    return True, f"封面比例 {found}"


def intro_len(text):
    seg = text.split("[内容简介]", 1)
    if len(seg) < 2:
        return None
    tail = seg[1]
    # 截到下一个 ## 或 [ 标记
    cut = len(tail)
    for mk in ("## 配图详情", "## 配图搜索替换指令", "\n[", "\n## "):
        i = tail.find(mk)
        if i != -1:
            cut = min(cut, i)
    return len(re.sub(r"\s+", "", tail[:cut]))


def figure_blocks(text):
    """返回 [(序号, 锚文本)] —— 从 [配图N] 块中提取。"""
    out = []
    for m in re.finditer(r"###\s*\[配图(\d+)\](.*?)(?=###\s*\[配图|##\s*配图搜索替换指令|\Z)", text, re.S):
        blk = m.group(2)
        am = re.search(r"\*\*锚文本\*\*[:：]\s*(.+)", blk)
        out.append((m.group(1), am.group(1).strip() if am else None))
    return out


def check_dir(d):
    files = sorted(d.glob("*.md"))
    fin = next((f for f in files if f.name.startswith("终稿-")), None)
    fin_chars = count_body_chars(fin) if fin else 0
    print("=" * 74)
    print(f"{d.name}   终稿 {fin_chars} 字")
    for f in files:
        fb = count_body_chars(f)
        tag = ""
        for pre, _k in PREFIX_PLATFORM:
            if f.name.startswith(pre):
                ratio = fb / fin_chars if fin_chars else 0
                tag = f"  保真比 {ratio:.1%} (底线 {FIDELITY_MIN[pre]:.0%}) {'OK' if ratio >= FIDELITY_MIN[pre] else '!!! 不足'}"
        h2 = h2_count(read(f))
        h2min = None
        for pre, v in H2_MIN.items():
            if f.name.startswith(pre):
                h2min = v
        h2s = f"  H2 {h2}{('/<' + str(h2min) + ' !!!') if h2min and h2 < h2min else ''}"
        print(f"  {fb:>6}  {f.name}{tag}{h2s}")
        key = next((k for pre, k in PREFIX_PLATFORM if f.name.startswith(pre)), None)
        if key:
            ok, msg = cover_ratio_ok(read(f), key)
            if not ok:
                print(f"          !!! {msg}")
            il = intro_len(read(f))
            if il is None:
                print("          !!! 缺 [内容简介]")
            elif il > INTRO_MAX[key]:
                print(f"          !!! 内容简介 {il} 字 > 上限 {INTRO_MAX[key]}")
            anchors = figure_blocks(read(f))
            print(f"          配图 {len(anchors)} 张")
            bd = extract_body_text(f)
            for idx, a in anchors:
                if not a:
                    print(f"          !!! 配图{idx} 缺锚文本")
                    continue
                a2 = a.lstrip("# ").strip()
                cnt_exact = bd.count(re.sub(r"\s+", "", a2))
                if cnt_exact == 0:
                    print(f"          !!! 配图{idx} 锚文本未命中正文：「{a2}」")
                elif cnt_exact > 1:
                    print(f"          ?  配图{idx} 锚文本出现 {cnt_exact} 次：「{a2}」")
                cmd = read(f).split("## 配图搜索替换指令", 1)
                if len(cmd) < 2 or a2 not in cmd[1]:
                    print(f"          !!! 配图{idx} 指令区缺一字不差锚文本：「{a2}」")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    root = Path(a.root).resolve() / "drafts" / a.date
    if not root.exists():
        print(f"目录不存在: {root}")
        sys.exit(1)
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        check_dir(d)


if __name__ == "__main__":
    main()
