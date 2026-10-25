#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$PATH"
export BSK_AUTO_START=0
O="$TEMP/bsk1024"
mkdir -p "$O"
SID=$(bsk session start 2>&1 | grep -oE '[a-z0-9]{4,}' | tail -1)
echo "SESSION=$SID" | tee "$O/_sid.txt"

shot() { # name url js
  local n="$1" u="$2" js="$3"
  bsk navigate --session "$SID" --wait-until load --timeout 60s "$u" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 5500 >/dev/null 2>&1
  bsk evaluate --session "$SID" "$js" > "$O/$n.txt" 2>&1
  echo "[$n] bytes=$(wc -c < "$O/$n.txt" 2>/dev/null)"
}

# 1 知乎问题热榜（四元组）
shot zhihu_hot "https://www.zhihu.com/hot" "Array.from(document.querySelectorAll('.HotItem')).slice(0,30).map(el=>{const r=el.querySelector('.HotItem-rank');const m=el.querySelector('.HotItem-metrics');const a=el.querySelector('a[href*=\\\"/question/\\\"]');const t=a?(a.innerText||'').trim().split('\n')[0]:'';const h=a?a.getAttribute('href'):'';return (r?r.innerText.trim():'?')+'##'+(m?m.innerText.trim().split('\n')[0]:'?')+'##'+t+'##'+h}).join('\n')"

# 2 知乎推荐问题 4 轮
: > "$O/zhihu_recommend.txt"
for i in 1 2 3 4; do
  bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.zhihu.com/creator/featured-question/recommend" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 4500 >/dev/null 2>&1
  bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a[href*=\\\"/question/\\\"]')).map(a=>(a.innerText||'').trim()+'##'+a.getAttribute('href')).filter(x=>x.split('##')[0].length>8).slice(0,25).join('\n')" >> "$O/zhihu_recommend.txt" 2>&1
  echo "" >> "$O/zhihu_recommend.txt"
  bsk evaluate --session "$SID" "window.scrollTo(0,document.body.scrollHeight)" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 2000 >/dev/null 2>&1
done
echo "[zhihu_recommend] bytes=$(wc -c < "$O/zhihu_recommend.txt")"

# 3 知乎邀请问题 3 轮
: > "$O/zhihu_invited.txt"
for i in 1 2 3; do
  bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.zhihu.com/creator/featured-question/invited" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 4500 >/dev/null 2>&1
  bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a[href*=\\\"/question/\\\"]')).map(a=>(a.innerText||'').trim()+'##'+a.getAttribute('href')).filter(x=>x.split('##')[0].length>8).slice(0,25).join('\n')" >> "$O/zhihu_invited.txt" 2>&1
  echo "" >> "$O/zhihu_invited.txt"
done
echo "[zhihu_invited] bytes=$(wc -c < "$O/zhihu_invited.txt")"

# 4 知乎想法话题
shot zhihu_idea "https://www.zhihu.com/creator/creative-inspiration/idea-topics" "document.body.innerText.slice(0,6000)"

# 5 知乎想法热榜
shot zhihu_pin "https://www.zhihu.com/pin/hot" "document.title+'##'+location.href+'##'+document.body.innerText.slice(0,600)"

# 6 微博热搜
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://s.weibo.com/top/summary" >/dev/null 2>&1
bsk wait-ms --session "$SID" 5000 >/dev/null 2>&1
bsk evaluate --session "$SID" "document.title+'###'+location.href" > "$O/weibo_meta.txt" 2>&1
bsk get-html --session "$SID" > "$O/weibo.html" 2>&1
echo "[weibo] html=$(wc -c < "$O/weibo.html")"

# 7 B站排行榜
shot bilibili "https://www.bilibili.com/ranking" "Array.from(document.querySelectorAll('a[href*=\\\"/video/\\\"]')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>6&&t.length<80).slice(0,40).join('\n')"

# 8 抖音热点（bsk 备用通道）
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://www.douyin.com/hot" >/dev/null 2>&1
bsk wait-ms --session "$SID" 9000 >/dev/null 2>&1
bsk evaluate --session "$SID" "document.body.innerText.slice(0,6000)" > "$O/douyin.txt" 2>&1
echo "[douyin] bytes=$(wc -c < "$O/douyin.txt")"

# 9 知微事见（4 轮滚动）
: > "$O/zhiwei.txt"
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://ef.zhiweidata.com/library" >/dev/null 2>&1
bsk wait-ms --session "$SID" 10000 >/dev/null 2>&1
for i in 1 2 3 4; do
  bsk evaluate --session "$SID" "document.body.innerText" >> "$O/zhiwei.txt" 2>&1
  echo "$(printf '\n=====SCROLL=====\n')" >> "$O/zhiwei.txt"
  bsk evaluate --session "$SID" "window.scrollTo(0,document.body.scrollHeight)" >/dev/null 2>&1
  bsk wait-ms --session "$SID" 3500 >/dev/null 2>&1
done
echo "[zhiwei] bytes=$(wc -c < "$O/zhiwei.txt")"

# 10 虎嗅
shot huxiu "https://www.huxiu.com/" "Array.from(document.querySelectorAll('a[href*=\\\"/article/\\\"]')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>8&&t.length<60).slice(0,30).join('\n')"

# 11 InfoQ（首页「热点」编辑精选）
bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.infoq.cn/" >/dev/null 2>&1
bsk wait-ms --session "$SID" 5000 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,600)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 2500 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>10&&t.length<80).slice(0,50).join('\n')" > "$O/infoq2.txt" 2>&1
echo "[infoq2] bytes=$(wc -c < "$O/infoq2.txt")"

# 12 品玩
bsk navigate --session "$SID" --wait-until load --timeout 60s "https://www.pingwest.com/" >/dev/null 2>&1
bsk wait-ms --session "$SID" 4000 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,document.body.scrollHeight)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 2500 >/dev/null 2>&1
bsk evaluate --session "$SID" "Array.from(document.querySelectorAll('a[href*=\\\"/a/\\\"]')).map(a=>(a.innerText||'').trim()).filter(t=>t.length>8&&t.length<60).slice(0,30).join('\n')" > "$O/pingwest.txt" 2>&1
echo "[pingwest] bytes=$(wc -c < "$O/pingwest.txt")"

# 13 百度指数
shot baidu_index "https://index.baidu.com/v2/index.html#/" "document.title+'###'+document.body.innerText.slice(0,1500)"

# 14 澎湃（bsk 渲染补量）
bsk navigate --session "$SID" --wait-until load --timeout 90s "https://www.thepaper.cn/" >/dev/null 2>&1
bsk wait-ms --session "$SID" 5500 >/dev/null 2>&1
bsk evaluate --session "$SID" "window.scrollTo(0,1200)" >/dev/null 2>&1
bsk wait-ms --session "$SID" 2500 >/dev/null 2>&1
bsk evaluate --session "$SID" "document.body.innerText.slice(0,8000)" > "$O/thepaper2.txt" 2>&1
echo "[thepaper2] bytes=$(wc -c < "$O/thepaper2.txt")"

# 15 小红书（登录态探测）
shot xhs "https://www.xiaohongshu.com/explore" "document.title+'###'+document.body.innerText.slice(0,2000)"

echo "ALL_DONE SESSION=$SID"
