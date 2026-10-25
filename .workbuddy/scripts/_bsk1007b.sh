#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$PATH"
export BSK_AUTO_START=0
O="$TEMP/bsk1007"
SID=$(bsk session start 2>&1 | grep -oE '[a-z0-9]{4,}' | tail -1)
echo "SESSION=$SID" | tee "$O/_sid2.txt"

# 抖音热点重试
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://www.douyin.com/hot" >/dev/null 2>&1
bsk wait-ms --session "$SID" 9000 >/dev/null 2>&1
bsk evaluate --session "$SID" "document.body.innerText.slice(0,6000)" > "$O/douyin2.txt" 2>&1
echo "[douyin2] bytes=$(wc -c < "$O/douyin2.txt")"

# 知微事见 滚动加载更多
bsk navigate --session "$SID" --wait-until load --timeout 60s "https://ef.zhiweidata.com/library" >/dev/null 2>&1
bsk wait-ms --session "$SID" 9000 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,1400)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 3000 >/dev/null 2>&1
bsk evaluate --session "$SID" "document.body.innerText.slice(1400,9000)" > "$O/zhiwei2.txt" 2>&1
echo "[zhiwei2] bytes=$(wc -c < "$O/zhiwei2.txt")"

# 抖音二次重试（重新导航）
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://www.douyin.com/hot" >/dev/null 2>&1
bsk wait-ms --session "$SID" 10000 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('[data-e2e],a,div')).map(e=>(e.innerText||'').trim()).filter(t=>t&&t.length>6&&t.length<40).slice(0,60).join('\n')" > "$O/douyin3.txt" 2>&1
echo "[douyin3] bytes=$(wc -c < "$O/douyin3.txt")"

echo "ALL_DONE SESSION=$SID"
