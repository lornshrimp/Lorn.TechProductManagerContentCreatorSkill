import json, yaml, os, io, sys
sys.stdout.reconfigure(encoding="utf-8")
base = r"d:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\research\车市价格带断裂-购车能力退出"
with open(os.path.join(base, "fields.yaml"), "r", encoding="utf-8") as f:
    y = yaml.safe_load(f)
fields = y.get("fields", {})
allnames = []
for cat, lst in fields.items():
    for fd in lst:
        allnames.append((cat, fd["name"]))
print("yaml 字段总数:", len(allnames))
print("分类:", list(fields.keys()))
for item in ["A1", "D6", "E5", "E6"]:
    p = os.path.join(base, "results", "item_%s.json" % item)
    if not os.path.exists(p):
        print(item, "文件不存在")
        continue
    try:
        d = json.load(open(p, "r", encoding="utf-8"))
    except Exception as e:
        print(item, "JSON 解析失败:", e)
        continue
    present = set()
    for cat, lst in fields.items():
        sec = d.get(cat, {})
        for fd in lst:
            if fd["name"] in sec:
                present.add((cat, fd["name"]))
    missing = [n for n in allnames if n not in present]
    print("%s: 覆盖 %d/%d; 缺失=%s; uncertain=%d" % (item, len(present), len(allnames), [m[1] for m in missing], len(d.get("uncertain", []))))
