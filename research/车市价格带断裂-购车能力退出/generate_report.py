# -*- coding: utf-8 -*-
"""
research-report：汇总 results/*.json 为 report.md
- 按 fields.yaml 的 7 类结构覆盖全部 31 个叶子字段
- 跳过 uncertain 数组内字段、值为 None/空/含[不确定] 的字段
- 保留 "❌ 未获取" 以便报告显式呈现真实缺口
- 目录含锚点 + 摘要字段（核验状态）
输出：report.md + _报告摘要.txt（ASCII 摘要，规避 stdout 捕获失效）
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TOPIC_DIR = Path(__file__).resolve().parent
RESULTS = TOPIC_DIR / "results"
OUT_MD = TOPIC_DIR / "report.md"
OUT_SUM = TOPIC_DIR / "_报告摘要.txt"

# 目录顺序（按证据链分组）
GROUP_TITLES = {
    "A": "A 消费端（需求侧硬数据）",
    "B": "B 供给端（退出证据）",
    "C": "C 政策端（累退性证据）",
    "D": "D 就业收入端（先验指标）",
    "E": "E 对照与反证（防自证偏差）",
}

LABELS = {
    "indicator_name": "指标名称", "source_org": "来源机构", "publish_date": "发布时间",
    "statistical_caliber": "统计口径", "series_completeness": "序列完整性",
    "band_definition": "价格带定义", "breaks_flag": "口径断裂标记",
    "value": "数值", "yoy_change": "同比变化", "time_series": "时间序列",
    "net_change_abs": "净变动绝对量", "distribution_metric": "分布指标",
    "method_note": "测算方法", "known_limits": "已知局限",
    "counterfactual_baseline": "反事实基线",
    "cross_source": "对照来源", "divergence_point": "分歧点",
    "verification_status": "核验状态",
    "capacity_vs_willingness": "能力 vs 意愿", "leverage_ratio": "杠杆化程度",
    "regressivity_coef": "政策累退性系数", "tradeup_chain": "置换链条",
    "city_tier_split": "城市线级分解", "employment_form": "就业形态",
    "citable_number": "可直接引用数字", "writable_judgment": "可写判断",
    "redline_note": "红线提示",
    "criterion_map": "判据映射", "domain_link": "域衔接",
    "notebook_hook": "观点挂接点", "voice_hook": "原声挂接点",
}

CATEGORIES = [
    ("基本信息", ["indicator_name", "source_org", "publish_date", "statistical_caliber",
                  "series_completeness", "band_definition", "breaks_flag"]),
    ("数据", ["value", "yoy_change", "time_series", "net_change_abs", "distribution_metric"]),
    ("方法论", ["method_note", "known_limits", "counterfactual_baseline"]),
    ("交叉验证", ["cross_source", "divergence_point", "verification_status"]),
    ("支付能力判别", ["capacity_vs_willingness", "leverage_ratio", "regressivity_coef",
                      "tradeup_chain", "city_tier_split", "employment_form"]),
    ("写作可用性", ["citable_number", "writable_judgment", "redline_note"]),
    ("作者观点对齐", ["criterion_map", "domain_link", "notebook_hook", "voice_hook"]),
]
CATEGORY_KEYS = {
    "基本信息": ["基本信息", "basic_info"],
    "数据": ["数据", "data"],
    "方法论": ["方法论", "methodology"],
    "交叉验证": ["交叉验证", "cross_validation"],
    "支付能力判别": ["支付能力判别", "payment_capacity"],
    "写作可用性": ["写作可用性", "writing_usability"],
    "作者观点对齐": ["作者观点对齐", "author_alignment"],
}


def is_empty(v):
    if v is None:
        return True
    if isinstance(v, str):
        s = v.strip()
        if s == "" or "[不确定]" in s:
            return True
        return False
    if isinstance(v, (list, dict)):
        return len(v) == 0
    return False


def fmt(v):
    """复杂值格式化为可读单段文本（内部换行 -> <br>）"""
    if isinstance(v, str):
        return v.strip().replace("\r\n", "\n").replace("\n", " <br>")
    if isinstance(v, list):
        parts = []
        for it in v:
            if isinstance(it, dict):
                parts.append("；".join(f"{k}: {fmt(x)}" for k, x in it.items()))
            else:
                parts.append(str(it))
        return " ／ ".join(parts)
    if isinstance(v, dict):
        return "；".join(f"{k}: {fmt(x)}" for k, x in v.items())
    return str(v)


def find_cat(data, keys):
    for k in keys:
        if isinstance(data.get(k), dict):
            return data[k]
    return {}


def get_name(data, iid):
    for k in ("name", "title"):
        if isinstance(data.get(k), str) and data[k].strip():
            return data[k].strip()
    basic = find_cat(data, CATEGORY_KEYS["基本信息"])
    nm = basic.get("indicator_name")
    if isinstance(nm, str) and nm.strip():
        return nm.strip()
    return iid


def group_of(data, iid):
    g = data.get("group")
    if isinstance(g, str) and g.strip():
        return g.strip().upper()[0]
    return iid[0].upper()


def sort_key(iid):
    return (iid[:1], int("".join(ch for ch in iid[1:] if ch.isdigit()) or 0))


def main():
    files = sorted(RESULTS.glob("item_*.json"), key=lambda p: sort_key(p.stem.replace("item_", "")))
    items = []
    problems = []
    for f in files:
        raw = f.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except Exception as e:  # noqa
            problems.append(f"{f.name}: JSON解析失败 {e}")
            continue
        iid = data.get("id") or f.stem.replace("item_", "")
        items.append({"id": iid, "file": f.name, "data": data,
                      "name": get_name(data, iid), "group": group_of(data, iid),
                      "uncertain": data.get("uncertain", []) or []})

    # ---- 目录 ----
    lines = []
    lines.append(f"# {items and '中国车市价格带断裂与中低收入购车能力退出' or ''}")
    lines.append("")
    lines.append("> 副题：验证「车市销量下降 + 高价车销量上升 = 贫富分化加剧的先验信号」这一判断")
    lines.append("")
    lines.append(f"> 条目数：**{len(items)}** ｜ 字段框架：7 类 / 31 个叶子字段 ｜ 时间范围：2024-01-01 至今")
    lines.append("")
    lines.append("## 核心判别框架（作者四判据）")
    lines.append("")
    lines.append("1. **总量守恒检验**：总量守恒 + 低端萎缩 = 升级；总量大幅萎缩 + 降幅集中于底部 = 分化")
    lines.append("2. **先验指标 vs 后验指标**：预警型数据的价值在提前量，不用后验的尺子量先验的数据")
    lines.append("3. **分子分母拆解**：占比上升必须反算净变动绝对量，区分分子增长与分母萎缩")
    lines.append("4. **政策累退性检验**：同额补贴占车价比重的差异（补贴 / 车价比值）")
    lines.append("")
    lines.append("## 目录")
    lines.append("")
    cur_g = None
    for it in items:
        if it["group"] != cur_g:
            cur_g = it["group"]
            lines.append("")
            lines.append(f"**{GROUP_TITLES.get(cur_g, cur_g)}**")
            lines.append("")
        vs = find_cat(it["data"], CATEGORY_KEYS["交叉验证"]).get("verification_status", "")
        vs_short = ""
        if isinstance(vs, str):
            vs_short = vs.split("；")[0].split(";")[0].strip()[:18]
        flag = " ✅" if vs_short.startswith("✅") else (" ⚠️" if "⚠️" in vs_short else (" ❌" if "❌" in vs_short else ""))
        lines.append(f"- [{it['id']} · {it['name']}](#item-{it['id']}){flag}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ---- 详细内容 ----
    stat = {"ok": 0, "warn": 0, "bad": 0, "skip_fields": 0, "not_fetched": 0}
    for it in items:
        lines.append(f'<a id="item-{it["id"]}"></a>')
        lines.append("")
        lines.append(f'## {it["id"]} · {it["name"]}')
        lines.append("")
        lines.append(f'*分组：{GROUP_TITLES.get(it["group"], it["group"])}*')
        lines.append("")
        data = it["data"]
        unc = set(it["uncertain"])
        for cat, keys in CATEGORIES:
            catdata = find_cat(data, CATEGORY_KEYS[cat])
            if not catdata:
                continue
            rows = []
            for k in keys:
                if k in unc:
                    stat["skip_fields"] += 1
                    continue
                if k not in catdata:
                    continue
                v = catdata[k]
                if is_empty(v):
                    stat["skip_fields"] += 1
                    continue
                sv = fmt(v)
                if "❌" in sv:
                    stat["not_fetched"] += 1
                rows.append(f"- **{LABELS.get(k, k)}**：{sv}")
            if rows:
                lines.append(f"### {cat}")
                lines.append("")
                lines.extend(rows)
                lines.append("")
        # 其他信息（未在 fields.yaml 定义的额外字段，非 category）
        known = set(k for _, ks in CATEGORIES for k in ks)
        cat_names = set(k for ks in CATEGORY_KEYS.values() for k in ks)
        extras = []
        for k, v in data.items():
            if k in known or k in cat_names or k in ("id", "group", "priority", "uncertain",
                                                      "name", "title", "证据角色"):
                continue
            if isinstance(v, dict):
                continue
            if is_empty(v):
                continue
            extras.append(f"- **{k}**：{fmt(v)}")
        if extras:
            lines.append("### 其他信息")
            lines.append("")
            lines.extend(extras)
            lines.append("")
        if it["uncertain"]:
            lines.append("### 未获取 / 不确定项")
            lines.append("")
            for u in it["uncertain"]:
                lines.append(f"- {u}")
            lines.append("")
        # 状态统计
        vs = find_cat(data, CATEGORY_KEYS["交叉验证"]).get("verification_status", "")
        if isinstance(vs, str):
            if vs.strip().startswith("✅"):
                stat["ok"] += 1
            elif "⚠️" in vs:
                stat["warn"] += 1
            else:
                stat["bad"] += 1
        lines.append("---")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    summary = [
        f"OUT={OUT_MD}",
        f"ITEMS={len(items)}",
        f"VERIFY_OK={stat['ok']} WARN={stat['warn']} BAD={stat['bad']}",
        f"SKIP_FIELDS={stat['skip_fields']} NOT_FETCHED_ITEMS={stat['not_fetched']}",
        f"PROBLEMS={len(problems)}",
    ]
    OUT_SUM.write_text("\n".join(summary + problems), encoding="utf-8")
    sys.stdout.write("\n".join(summary) + "\n")


if __name__ == "__main__":
    main()
