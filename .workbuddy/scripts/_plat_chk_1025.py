# -*- coding: utf-8 -*-
"""2026-10-25 平台稿门禁自检：H2 数/最长段/锚文本三查/平台关键词/封面比例/简介字数"""
import sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(r"D:/Users/lorns/OneDrive/第二职业/产品经理独孤虾/互联网产品经理自媒体")
DATE = "2026-10-25"

DIRS = {
    "A": "国办发文减缓AI就业替代-第一级台阶的成本归属",
    "B": "南方区域电力市场正式运行-15分钟一次的电价定价",
    "C": "云南烟草工业负增长-产量涨增加值跌的账",
}
PLATS = ["知乎", "微信", "百家号", "CSDN", "头条"]
H2MIN = {"知乎": 4, "微信": 4, "百家号": 3, "CSDN": 4, "头条": 3}
RATIO = {"知乎": "16:9", "微信": "9:16", "百家号": "16:9", "CSDN": "16:9", "头条": "3:2"}
INTRO_MAX = {"知乎": 100, "微信": 120, "头条": 80, "百家号": 100, "CSDN": 100}
MARK = ["## 素材溯源", "## 标题决策说明", "## 质量自检报告", "## 封面图", "## 内容简介",
        "## 互动引导", "## SEO 关键词", "## 配图详情", "# 附属内容区域",
        "## 配图搜索替换指令", "## 参考来源", "## 润色说明", "## 发布建议"]


def cjk(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def run():
    issues = 0
    for k, name in DIRS.items():
        d = ROOT / "drafts" / DATE / name
        print("=" * 76)
        print(f"### {k} {name}")
        for pl in PLATS:
            hits = [p for p in d.glob("*.md") if p.name.startswith(pl)]
            if not hits:
                print(f"  [{pl}] 缺文件"); issues += 1; continue
            p = hits[0]
            t = p.read_text(encoding="utf-8", errors="ignore")
            # 正文区
            body = t
            if body.startswith("---"):
                e = body.find("\n---", 3)
                if e != -1:
                    body = body[e + 4:]
            for m in MARK:
                i = body.find(m)
                if i != -1:
                    body = body[:i]; break
            h2 = re.findall(r"^## (.+)$", body, re.M)
            paras = [x for x in re.split(r"\n\s*\n", body) if x.strip() and not x.strip().startswith("|")]
            longest = max((cjk(x) for x in paras), default=0)
            flags = []
            if len(h2) < H2MIN[pl]:
                flags.append(f"H2不足({len(h2)}<{H2MIN[pl]})")
            if longest > 300:
                flags.append(f"超长段({longest})")
            # 封面比例
            if f"**封面图提示词**" not in t:
                flags.append("缺封面图提示词")
            elif RATIO[pl] not in t.split("**封面图提示词**")[1][:600]:
                flags.append(f"封面比例非{RATIO[pl]}")
            # 简介
            m = re.search(r"\*\*内容简介\*\*：(.+)", t)
            if not m:
                flags.append("缺内容简介")
            else:
                n = cjk(m.group(1))
                if n > INTRO_MAX[pl]:
                    flags.append(f"简介{n}字>{INTRO_MAX[pl]}")
            # 锚文本三查
            # 锚文本核对区：正文到 [封面图提示词] 或 [配图1] 之前（与 check_anchor_quality 口径一致）
            ab = body
            for mk in ["[封面图提示词]", "[配图1]", "**封面图提示词**", "### [配图1]"]:
                i = ab.find(mk)
                if i != -1:
                    ab = ab[:i]
            anchors = re.findall(r"\*\*锚文本\*\*：(.+)", t)
            instr = t.split("## 配图搜索替换指令")[1] if "## 配图搜索替换指令" in t else ""
            for a in anchors:
                a = a.strip()
                c = ab.count(a)
                if c == 0:
                    flags.append(f"锚未命中「{a[:12]}」")
                elif c > 1:
                    flags.append(f"锚不唯一{c}「{a[:12]}」")
                if a not in instr:
                    flags.append(f"指令区缺锚「{a[:12]}」")
            # 平台专属
            if pl == "知乎":
                if "source_label" not in t: flags.append("缺source_label")
                if "source_url" in t and "去回答该问题" not in t: flags.append("缺Clickable Link")
            if pl == "微信" and not all(w in t for w in ["在看", "留言", "关注"]):
                flags.append("缺在看/留言/关注")
            if pl == "头条":
                if "关注" not in t: flags.append("缺关注引导")
                if "[封面图提示词]" not in t and "**封面图提示词**" not in t: flags.append("缺封面图提示词")
            if pl == "百家号":
                if "**核心" not in t and "核心答案" not in t: flags.append("缺核心答案")
                if "## SEO 关键词" not in t: flags.append("缺SEO关键词")
                else:
                    # SEO 必须在视觉之后
                    if t.find("## SEO 关键词") < t.find("## 视觉与配图"):
                        flags.append("SEO段在正文前")
            if pl == "CSDN" and not any(w in body for w in ["方法论", "步骤", "框架", "分析", "要点"]):
                flags.append("缺方法论/步骤/框架/分析/要点字面词")
            if flags:
                issues += len(flags)
                print(f"  [{pl}] ❌ {p.name}: " + " | ".join(flags))
            else:
                print(f"  [{pl}] ✅ {p.name}  H2={len(h2)} 最长段={longest} 锚={len(anchors)}")
    print(f"\nTOTAL_ISSUES={issues}")


if __name__ == "__main__":
    run()
