# -*- coding: utf-8 -*-
import difflib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

M = {'A': '出口管制写的不是能力，是尺寸',
     'B': '存款的半径被砍回本地：定价权换了个维度',
     'C': '你的三分钟被谁定了价'}

P = {
"A": [("知乎", "从3.8亿买二手到全球七成，现在轮到我们写门槛"),
      ("微信", "参数贴线改：管制清单公开之后的第一个动作"),
      ("头条", "同一天里，盾构机被加进来，无人机被放出去"),
      ("百家号", "你把什么写成尺寸，行业就照着尺寸重排产品线"),
      ("CSDN", "吸口内径0.55米：一份国家安全公告里的数字")],
"B": [("知乎", "中小银行最赚钱的那条路，被地理条件关掉了"),
      ("微信", "存款的定价权，从谁出价高改成谁离得近"),
      ("头条", "多出来的那点利息差额，最后记在谁的账上"),
      ("百家号", "属地化不是新政策，只是把原则变成了五个字段"),
      ("CSDN", "整改的成本，先落在最没有议价能力的那一端")],
"C": [("知乎", "补贴退坡之后，被养出来的预期成了平台的负债"),
      ("微信", "金币不是福利，是平台给注意力开的欠条"),
      ("头条", "万播收益跌九成，这些都发生在金币下线之前"),
      ("百家号", "平台能定买入价，定不了卖出价，这就是全部算术"),
      ("CSDN", "125分钟不是产品力，是按分钟计价的结果")],
}

for k, arr in P.items():
    print(f"=== {k} 母稿：{M[k]}")
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            s = difflib.SequenceMatcher(None, arr[i][1], arr[j][1]).ratio()
            flag = " ❌" if s >= 0.85 else (" ⚠️" if s >= 0.72 else "")
            print(f"  {arr[i][0]}×{arr[j][0]} {s:.3f}{flag}")
    for pl, t in arr:
        s = difflib.SequenceMatcher(None, t, M[k]).ratio()
        print(f"  vs母稿 {pl} {s:.3f}{' ❌' if s >= 0.85 else ''}")
