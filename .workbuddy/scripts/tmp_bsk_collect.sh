#!/bin/bash
# 2026-09-14 bsk 采集脚本
SID=ukju
OUT=/tmp/bsk_raw
mkdir -p $OUT
cd /tmp

echo "=== 1 知乎问题热榜 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.zhihu.com/hot" > $OUT/zhihu_hot_nav.txt 2>&1
bsk evaluate --session $SID 'Array.from(document.querySelectorAll(".HotItem")).slice(0,25).map(el=>{const r=el.querySelector(".HotItem-rank");const m=el.querySelector(".HotItem-metrics");const a=el.querySelector("a[href*=\"/question/\"]");const t=a?(a.innerText||"").trim().split("\n")[0]:"";const h=a?a.getAttribute("href"):"";return (r?r.innerText.trim():"?")+"##"+(m?m.innerText.trim().split("\n")[0]:"?")+"##"+t+"##"+h}).join("\n")' > $OUT/zhihu_hot.txt 2>&1

echo "=== 2 知乎推荐问题 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.zhihu.com/creator/featured-question/recommend" > /dev/null 2>&1
bsk evaluate --session $SID 'Array.from(document.querySelectorAll("div,li,section")).map(e=>e.innerText||"").filter(t=>t.length>20&&t.length<400).slice(0,20).join("\n---\n")' > $OUT/zhihu_recommend.txt 2>&1
bsk snapshot --session $SID > $OUT/zhihu_recommend_snap.txt 2>&1

echo "=== 3 知乎邀请问题 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.zhihu.com/creator/featured-question/invited" > /dev/null 2>&1
bsk evaluate --session $SID 'Array.from(document.querySelectorAll("div,li,section")).map(e=>e.innerText||"").filter(t=>t.length>20&&t.length<400).slice(0,20).join("\n---\n")' > $OUT/zhihu_invited.txt 2>&1
bsk snapshot --session $SID > $OUT/zhihu_invited_snap.txt 2>&1

echo "=== 4 知乎想法话题 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.zhihu.com/creator/creative-inspiration/idea-topics" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText' > $OUT/zhihu_idea.txt 2>&1

echo "=== 5 知乎想法热榜 ==="
bsk navigate --session $SID --wait-until load --timeout 40s "https://www.zhihu.com/pin/hot" > $OUT/zhihu_pin_nav.txt 2>&1
bsk evaluate --session $SID 'document.title+" | "+document.body.innerText.slice(0,600)' > $OUT/zhihu_pin.txt 2>&1

echo "=== 6 微博热搜 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://s.weibo.com/top/summary" > /dev/null 2>&1
bsk get-html --session $SID > $OUT/weibo.html 2>&1

echo "=== 7 抖音热点 ==="
bsk navigate --session $SID --wait-until load --timeout 30s "https://www.douyin.com/hot" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText.slice(0,3000)' > $OUT/douyin.txt 2>&1

echo "=== 8 B站热门 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.bilibili.com/ranking" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText.slice(0,3000)' > $OUT/bilibili.txt 2>&1

echo "=== 9 头条热榜 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.toutiao.com/?channel=hot" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText.slice(0,3000)' > $OUT/toutiao.txt 2>&1

echo "=== 10 虎嗅 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.huxiu.com/" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText.slice(0,4000)' > $OUT/huxiu.txt 2>&1

echo "=== 11 InfoQ ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.infoq.cn/hotlist?tag=day" > /dev/null 2>&1
bsk evaluate --session $SID 'window.scrollTo(0, document.body.scrollHeight); "scrolled"' > /dev/null 2>&1
sleep 3
bsk evaluate --session $SID 'document.body.innerText.slice(0,4000)' > $OUT/infoq.txt 2>&1

echo "=== 12 品玩 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.pingwest.com/" > /dev/null 2>&1
bsk evaluate --session $SID 'window.scrollTo(0, document.body.scrollHeight); "scrolled"' > /dev/null 2>&1
sleep 3
bsk evaluate --session $SID 'document.body.innerText.slice(0,4000)' > $OUT/pingwest.txt 2>&1

echo "=== 13 知微事见 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://ef.zhiweidata.com/library" > /dev/null 2>&1
sleep 6
bsk evaluate --session $SID 'document.body.innerText.slice(0,5000)' > $OUT/zhiwei.txt 2>&1

echo "=== 14 百度指数 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://index.baidu.com/v2/index.html#/" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText.slice(0,2000)' > $OUT/baiduindex.txt 2>&1

echo "=== 15 澎湃 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.thepaper.cn/" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText.slice(0,4000)' > $OUT/thepaper.txt 2>&1

echo "=== 16 网易 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://news.163.com/" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText.slice(0,4000)' > $OUT/163.txt 2>&1

echo "=== 17 IT之家 ==="
bsk navigate --session $SID --wait-until load --timeout 60s "https://www.ithome.com/" > /dev/null 2>&1
bsk evaluate --session $SID 'document.body.innerText.slice(0,4000)' > $OUT/ithome.txt 2>&1

echo "=== ALL DONE ==="
ls -la $OUT
