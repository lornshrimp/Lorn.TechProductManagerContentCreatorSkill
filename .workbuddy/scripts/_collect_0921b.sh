#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
D="$TEMP/collect"
mkdir -p "$D"

S=$(bsk session start 2>/dev/null < /dev/null | grep -E '^[a-z]{4}$' | head -1)
echo "SESSION=$S"
if [ -z "$S" ]; then S=$(bsk session start 2>/dev/null < /dev/null | tail -1); echo "SESSION2=$S"; fi

n() { bsk navigate --session $S --wait-until load --timeout 40s "$1" > "$D/$2.nav.txt" 2>&1 < /dev/null; }
ev() { bsk evaluate --session $S "$1" > "$D/$2.txt" 2>&1 < /dev/null; }

n "https://www.infoq.cn/hotlist?tag=day" infoq
ev 'window.scrollTo(0,document.body.scrollHeight)' infoq_scroll
sleep 2
ev 'document.body.innerText.slice(0,4000)' infoq

n "https://www.huxiu.com/" huxiu
ev 'window.scrollTo(0,document.body.scrollHeight)' huxiu_scroll
sleep 2
ev 'document.body.innerText.slice(0,6000)' huxiu

n "https://www.pingwest.com/" pingwest
ev 'window.scrollTo(0,document.body.scrollHeight)' pingwest_scroll
sleep 2
ev 'document.body.innerText.slice(0,5000)' pingwest

bsk session stop $S < /dev/null > /dev/null 2>&1
echo "DONE_BATCH2 session=$S"
