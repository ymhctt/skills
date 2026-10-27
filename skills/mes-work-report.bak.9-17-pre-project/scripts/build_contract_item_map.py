#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建「报工 → 合同」精确映射，供报告「每人工作总结」展示 **合同名 + 实施计划**。

核心发现（2026-09-06 实测）
--------------------------
报工记录(statistics list)的 `accId` == 合同子项(`mes contract list-items`)的 `itemId`，
可做**精确关联**（实测命中率 61/66 ≈ 92%）；且子项自带：
  - companyName  = **合同名**（如 "2026年S2E云和恩墨二线支持框架合同"）
  - contractNum  = 合同编号（如 "00032689"）
  - itemName     = 实施计划名（即报工里的 accName）

字段澄清（重要踩坑）：
  - 报工 accName = 实施计划/合同子项名（用户口径）
  - 报工 title   ≠ 合同名（与合同库 0 命中，勿用）
  - 合同名只能靠 accId→itemId 精确关联，或 itemName 模糊匹配兜底

产出缓存
--------
  /tmp/mes_item_contract_map.json
  {
    "by_item_id":   {"<itemId=accId>": {"contract": "...", "contract_num": "...", "item": "..."}},
    "by_item_name": {"<itemName>": [{"contract": "...", "contract_num": "..."}, ...]},
    "contract_count": 388, "item_count": 824, "built_at": "..."
  }

同名子项挂多个合同时（如通用「人天服务」），by_item_name 值为列表，仅作兜底；
主路径 by_item_id 精确无歧义。

用法
----
  python3 build_contract_item_map.py                  # 有缓存直接用，无则构建
  python3 build_contract_item_map.py --refresh        # 强制重建
  python3 build_contract_item_map.py --workers 10     # 并发数（默认 8）
"""

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_CACHE = '/tmp/mes_item_contract_map.json'


def mes_json(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout) if r.stdout else {}
    except Exception:
        return {}


def fetch_all_contracts():
    """分页拉取全部合同 → {id: name}"""
    contracts = {}
    page = 1
    total = None
    while page <= 60:
        d = mes_json(f'mes -o json contract list --page {page}')
        lst = d.get('list') or []
        if not lst:
            break
        for c in lst:
            cid = c.get('id')
            if cid is not None:
                contracts[str(cid)] = (c.get('name') or '').strip()
        if total is None:
            total = d.get('total')
        if total and len(contracts) >= total:
            break
        page += 1
    return contracts


def fetch_items(cid):
    """拉取单个合同的子项 → [(itemId, itemName, contractNum)]"""
    d = mes_json(f'mes -o json contract list-items --contract-id {cid}')
    out = []
    for it in (d.get('operateCallBackObj') or {}).get('list') or []:
        iid = str(it.get('itemId') or '')
        nm = (it.get('itemName') or '').strip()
        if iid and nm:
            out.append((iid, nm, (it.get('contractNum') or '').strip()))
    return cid, out


def build(workers=8):
    contracts = fetch_all_contracts()
    if not contracts:
        raise RuntimeError('未拉到任何合同，请检查 mes 登录状态')

    by_item_id = {}
    by_item_name = {}
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(fetch_items, cid) for cid in contracts]
        for fut in as_completed(futs):
            cid, rows = fut.result()
            done += 1
            if done % 50 == 0:
                print(f'  ...已处理 {done}/{len(contracts)} 个合同', file=sys.stderr)
            cname = contracts[cid]
            for iid, nm, cnum in rows:
                # itemId 全局唯一，后者不覆盖前者
                by_item_id.setdefault(iid, {
                    'contract': cname, 'contract_num': cnum, 'item': nm})
                by_item_name.setdefault(nm, [])
                entry = {'contract': cname, 'contract_num': cnum}
                if entry not in by_item_name[nm]:
                    by_item_name[nm].append(entry)

    return {
        'by_item_id': by_item_id,
        'by_item_name': by_item_name,
        'contract_count': len(contracts),
        'item_count': len(by_item_id),
        'built_at': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'),
    }


# ---------------------------------------------------------------------------
# 解析 API（供生成器调用）
# ---------------------------------------------------------------------------

def load_map(path=DEFAULT_CACHE):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def resolve_contract(cmap, acc_id='', item_name='', company_name=''):
    """
    解析报工 → 合同名。返回 (合同名, 合同编号, 是否命中)。

    主路径：acc_id 精确匹配 itemId（无歧义）。
    兜底：item_name 模糊匹配；同名多合同时优先「合同名含客户名」者。
    """
    if not cmap:
        return '', '', False
    # 1) 精确：accId == itemId
    if acc_id:
        e = (cmap.get('by_item_id') or {}).get(str(acc_id))
        if e:
            return e['contract'], e.get('contract_num', ''), True
    # 2) 兜底：子项名模糊匹配
    nm = (item_name or '').strip()
    if nm:
        cands = (cmap.get('by_item_name') or {}).get(nm) or []
        if len(cands) == 1:
            return cands[0]['contract'], cands[0].get('contract_num', ''), True
        if cands:
            comp = (company_name or '').strip()
            if comp:
                key = (comp.replace('股份有限公司', '').replace('有限责任公司', '')
                           .replace('有限公司', '').replace('集团', ''))
                for c in cands:
                    if comp in c['contract'] or (key and key in c['contract']):
                        return c['contract'], c.get('contract_num', ''), True
            return cands[0]['contract'], cands[0].get('contract_num', ''), True
    return '', '', False


def main():
    ap = argparse.ArgumentParser(description='构建 报工accId(itemId) → 合同 精确映射')
    ap.add_argument('--output', default=DEFAULT_CACHE, help=f'缓存路径（默认 {DEFAULT_CACHE}）')
    ap.add_argument('--refresh', action='store_true', help='强制重建（忽略已有缓存）')
    ap.add_argument('--workers', type=int, default=8, help='并发数（默认 8）')
    args = ap.parse_args()

    if not args.refresh and os.path.exists(args.output):
        m = load_map(args.output)
        if m:
            print(f"使用已有缓存 {args.output}（合同 {m.get('contract_count')} 个，"
                  f"子项 {m.get('item_count')} 个，构建于 {m.get('built_at')}）"
                  f"；加 --refresh 可强制重建")
            return

    print(f'开始构建合同子项映射（并发 {args.workers}）…', file=sys.stderr)
    data = build(workers=args.workers)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已写入 {args.output}：合同 {data['contract_count']} 个，"
          f"子项 {data['item_count']} 个")


if __name__ == '__main__':
    main()
