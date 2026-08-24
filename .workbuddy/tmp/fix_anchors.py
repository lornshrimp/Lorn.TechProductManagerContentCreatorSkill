# -*- coding: utf-8 -*-
"""修复今日 15 份平台稿的锚文本问题（2026-08-23 校验回修）：
规则（对齐 规范校验.py check_anchor_quality）：
1. 锚从「锚文本：xxx」行提取，提取时剥首尾引号/#（不剥 **）
2. 锚须在正文唯一 + 位于段首（段首前缀为空，含 ** 加粗前缀则锚必须含 **）或小标题行/表格行
3. 指令区须含「锚」（中文方括号包裹）"""
import re, os, glob

roots = [
    r'D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-08-23\白菜蘸甲醛事件-农食流通监管真空',
    r'D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-08-23\A00级小车销量腰斩-国民神车为何卖不动',
    r'D:\Users\lorns\OneDrive\第二职业\产品经理独孤虾\互联网产品经理自媒体\drafts\2026-08-23\世界人形机器人运动会-从破纪录到商用临界点',
]

def norm_anchor(a):
    # 与校验脚本一致：剥首尾引号/#（不剥 **）
    return a.strip('"').strip("'").strip('#').strip()

def extract_body(c):
    body = c
    if body.startswith('---'):
        end = body.find('\n---', 3)
        body = body[end + 4:] if end != -1 else body
    for marker in ['[封面图提示词]', '[配图1]']:
        idx = body.find(marker)
        if idx != -1:
            body = body[:idx]
            break
    return body

def fix_file(path):
    c = open(path, encoding='utf-8').read()
    lines = c.split('\n')
    body_full = extract_body(c)
    changed = False
    # 逐行处理「锚文本：」行
    for i, line in enumerate(lines):
        ls = line.strip()
        if not ls.startswith('锚文本'):
            continue
        if '在正文找到唯一锚文本' in ls or '之后的段落后' in ls or '插入 [' in ls:
            continue
        val = re.sub(r'^锚文本\s*[:：]', '', ls).strip()
        a0 = norm_anchor(val)
        if not a0 or a0.startswith('[配图') or '锚文本' in a0:
            continue
        # 在正文中定位 a0
        pos = body_full.find(a0)
        if pos == -1:
            # 尝试去掉 ** 前缀后查找
            a_plain = a0.replace('**', '')
            pos2 = body_full.find(a_plain)
            if pos2 != -1:
                # 检查 a_plain 是否段首（前面无正文）
                seg = body_full[:pos2]
                seg_start = seg.rfind('\n\n')
                seg_tail = seg[seg_start + 2:] if seg_start != -1 else seg
                if seg_tail.strip() == '' or seg_tail.strip() == '**':
                    new_anchor = ('**' if seg_tail.strip() == '**' else '') + a_plain
                    if body_full.count(new_anchor) == 1:
                        a0 = new_anchor
            if pos == -1 and a0 == a_plain:
                pass
        # 重新定位（若 a0 更新）
        pos = body_full.find(a0)
        if pos == -1:
            print('  [MISS]', os.path.basename(path), a0[:25])
            continue
        # 段首判定
        seg = body_full[:pos]
        seg_start = seg.rfind('\n\n')
        seg_tail = seg[seg_start + 2:] if seg_start != -1 else seg
        is_start = seg_tail.strip() == ''
        is_table = ('| ' + a0) in body_full or ('|' + a0) in body_full
        # 小标题判定
        is_heading = False
        nl = body_full.rfind('\n', 0, pos)
        ne = body_full.find('\n', pos)
        aline = body_full[nl + 1: ne if ne != -1 else len(body_full)]
        if aline.strip().startswith('#'):
            hj = aline.strip().lstrip('#').strip()
            if a0.strip() in hj or hj in a0.strip():
                is_heading = True
        # 段首前缀为 ** 而 a0 不带 ** → 补 **
        if seg_tail.strip() == '**' and not a0.startswith('**'):
            new_anchor = '**' + a0
            if body_full.count(new_anchor) == 1:
                a0 = new_anchor
                is_start = True
        # 若仍非段首/表格/小标题 → 尝试用本段段首句
        if not (is_start or is_table or is_heading):
            # 取锚所在段落文本
            pep = body_full.find('\n\n', pos)
            if pep == -1:
                pep = len(body_full)
            para = body_full[seg_start + 2: pep]
            # 段首句：从行首（或 ** 后）到第一个句尾标点
            cand = para.strip()
            m = re.match(r'^(\*\*)?(.{4,40}?)(?=[。？?!！])', cand)
            if m:
                maybe = (m.group(1) or '') + m.group(2) + cand[cand.find(m.group(2)) + len(m.group(2)):][:0]
                head = (m.group(1) or '') + m.group(2)
                # 加回标点
                rest = cand[len(head):]
                if rest and rest[0] in '。？?!！':
                    head = head + rest[0]
                if body_full.count(head) == 1:
                    a0 = head
                    is_start = True
                else:
                    print('  [CANDFAIL]', os.path.basename(path), a0[:20], '->', head[:20])
            else:
                print('  [CANDNONE]', os.path.basename(path), a0[:25])
        # 更新锚文本行
        new_line = '锚文本：%s' % a0
        lines[i] = new_line if not val.startswith('**') else new_line
        # 更新指令区表格中对应旧锚行（旧值 val 或剥后值）
        old_variants = [val, norm_anchor(val)]
        changed = True
        # 便于后续指令区更新：记录 (old_val, new_a0)
        pending.append((path, val, a0))

    c = '\n'.join(lines)
    return c, body_full, pending

pending = []  # 全局收集用
# 由于上面 per-file 逻辑需要 pending，简化：一次处理一个文件
def process(path):
    global pending
    pending = []
    fixed, body_full, pend = fix_file_impl(path)
    # 更新指令区：把所有旧锚出现（旧值）替换为「新锚」
    c = fixed
    for oldv, newa in pend:
        # 指令区格式：| xx |（旧）→ | 「newa」 |
        # 全文替换旧锚裸出现（在表格行中）为「newa」
        if oldv != newa:
            c = c.replace('| ' + oldv + ' |', '| 「' + newa + '」 |')
            c = c.replace('|' + oldv + '|', '|「' + newa + '」|')
        else:
            # 已是正确锚，仅需加「」
            c = c.replace('| ' + oldv + ' |', '| 「' + newa + '」 |')
            c = c.replace('|' + oldv + '|', '|「' + newa + '」|')
    open(path, 'w', encoding='utf-8').write(c)
    # 校验一遍
    import subprocess
    # 报告
    print('processed', os.path.basename(path), 'pend=', len(pend))

def fix_file_impl(path):
    c = open(path, encoding='utf-8').read()
    lines = c.split('\n')
    body_full = extract_body(c)
    pending = []
    for i, line in enumerate(lines):
        ls = line.strip()
        if not ls.startswith('锚文本'):
            continue
        if '在正文找到唯一锚文本' in ls or '之后的段落后' in ls or '插入 [' in ls:
            continue
        val = re.sub(r'^锚文本\s*[:：]', '', ls).strip()
        a0 = norm_anchor(val)
        if not a0 or a0.startswith('[配图') or '锚文本' in a0:
            continue
        pos = body_full.find(a0)
        if pos == -1:
            a_plain = a0.replace('**', '')
            pos2 = body_full.find(a_plain)
            if pos2 != -1:
                seg = body_full[:pos2]
                seg_start = seg.rfind('\n\n')
                seg_tail = seg[seg_start + 2:] if seg_start != -1 else seg
                if seg_tail.strip() in ('', '**'):
                    new_anchor = ('**' if seg_tail.strip() == '**' else '') + a_plain
                    if body_full.count(new_anchor) == 1:
                        a0 = new_anchor
                        pos = body_full.find(a0)
        if pos == -1:
            print('  [MISS]', os.path.basename(path), a0[:25])
            continue
        seg = body_full[:pos]
        seg_start = seg.rfind('\n\n')
        seg_tail = seg[seg_start + 2:] if seg_start != -1 else seg
        is_start = seg_tail.strip() == ''
        is_table = ('| ' + a0) in body_full or ('|' + a0) in body_full
        is_heading = False
        nl = body_full.rfind('\n', 0, pos)
        ne = body_full.find('\n', pos)
        aline = body_full[nl + 1: ne if ne != -1 else len(body_full)]
        if aline.strip().startswith('#'):
            hj = aline.strip().lstrip('#').strip()
            if a0.strip() in hj or hj in a0.strip():
                is_heading = True
        if seg_tail.strip() == '**' and not a0.startswith('**'):
            new_anchor = '**' + a0
            if body_full.count(new_anchor) == 1:
                a0 = new_anchor
                is_start = True
        if not (is_start or is_table or is_heading):
            pep = body_full.find('\n\n', pos)
            if pep == -1:
                pep = len(body_full)
            para = body_full[seg_start + 2: pep]
            cand = para.strip()
            m = re.match(r'^(\*\*)?(.{4,40}?)(?=[。？?!！])', cand)
            if m:
                head = (m.group(1) or '') + m.group(2)
                rest = cand[len(head):]
                if rest and rest[0] in '。？?!！':
                    head = head + rest[0]
                if body_full.count(head) == 1:
                    a0 = head
                    is_start = True
                else:
                    print('  [CANDFAIL]', os.path.basename(path), '->', head[:20])
            else:
                print('  [CANDNONE]', os.path.basename(path), cand[:20])
        lines[i] = '锚文本：%s' % a0
        pending.append((val, a0))
    return '\n'.join(lines), body_full, pending

for root in roots:
    for fp in glob.glob(os.path.join(root, '*.md')):
        bn = os.path.basename(fp)
        if not bn[0:2] in ('知乎', '微信', '头条', '百家', 'CSDN'):
            continue
        process(fp)
print('ALL DONE')