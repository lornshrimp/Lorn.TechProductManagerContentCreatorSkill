import re, difflib
from pathlib import Path

titles = {
    "头条": "25 元外卖商家到手 6.08 元：这笔钱被拆成了三份",
    "知乎": "25 元的外卖里，那 18.92 元到底去哪了？",
    "微信": "消费者付了量，商家付了利，骑手付了时",
    "百家号": "平台说抽 6%，商家说抽 25%：差的这 19 个点去哪了",
    "CSDN": "一笔 25 元订单的四个科目：技术服务费、配送费、补贴分摊、推广费",
    "母稿": "25 元那本账：抽成不是平台与商家的两方账，是三方账",
    "头条备选": "平台说抽 6%，商家说抽 25%：这两个数为什么都对？",
    "知乎备选": "到手率低于 30%，这家店就在结构性退出",
    "微信备选": "抽成砍到零，这笔成本会消失吗？",
    "百家号备选": "美团抽成到底高不高？先把这张账单拆成四个科目",
    "CSDN备选": "美团抽成争议：一笔订单的四个科目与到手率三档",
}
print("=== 字数实测 [\\u4e00-\\u9fffA-Za-z0-9] ===")
for k, v in titles.items():
    n = len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", v))
    print(f"{k}: {n} 字  | {v}")

print()
print("=== 平台两两 + 母稿 相似度 ===")
plats = ["头条", "知乎", "微信", "百家号", "CSDN"]
mx = 0
for i in range(len(plats)):
    for j in range(i + 1, len(plats)):
        r = difflib.SequenceMatcher(None, titles[plats[i]], titles[plats[j]], autojunk=False).ratio()
        mx = max(mx, r)
        print(f"{plats[i]} vs {plats[j]}: {r:.4f} {'[OK]' if r < 0.85 else '[FAIL]'}")
for p in plats:
    r = difflib.SequenceMatcher(None, titles["母稿"], titles[p], autojunk=False).ratio()
    print(f"母稿 vs {p}: {r:.4f} {'[OK]' if r < 0.85 else '[FAIL]'}")
print(f"平台两两最大 = {mx:.4f}")

print()
print("=== 标点自检 ===")
for p in plats:
    t = re.sub(r"[\u4e00-\u9fffA-Za-z0-9\s]", "", titles[p])
    n = len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", titles[p]))
    print(f"{p}: {n} 字, 标点 = {t!r}")
