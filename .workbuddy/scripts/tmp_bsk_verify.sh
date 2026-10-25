#!/bin/bash
# 抖音重采 + 知乎链接核验
cd /tmp
bsk session start > /tmp/sess2.txt 2>&1
sleep 8
SID=$(grep -oE '^[a-z0-9]{4}$' /tmp/sess2.txt | head -1)
echo "SID=$SID"
mkdir -p /tmp/bsk_raw2

echo "=== 抖音热榜 evaluate ==="
bsk navigate --session $SID --wait-until load --timeout 30s "https://www.douyin.com/hot" > /dev/null 2>&1
sleep 3
bsk evaluate --session $SID 'Array.from(document.querySelectorAll("a")).map(a=>a.innerText.trim().replace(/\n+/g," | ")).filter(t=>t.length>10&&t.length<90).slice(0,50).join("\n")' > /tmp/bsk_raw2/douyin2.txt 2>&1

echo "=== 知乎链接核验（抽查5条） ==="
for qid in 2082478357984421508 2081827882993823882 2082497943508973001 2082571703062721521 2082440100701548705; do
  bsk navigate --session $SID --wait-until load --timeout 30s "https://www.zhihu.com/question/$qid" > /dev/null 2>&1
  echo -n "$qid => "
  bsk evaluate --session $SID 'document.title' 2>&1 | grep -v "new bsk version" | head -1
done

bsk session stop $SID > /dev/null 2>&1
echo "=== DONE ==="
