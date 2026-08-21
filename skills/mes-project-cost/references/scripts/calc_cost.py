#!/usr/bin/env python3
"""MES 项目成本计算引擎

从 MES 导出的 JSON 数据和人员配置文件中计算项目成本。

Usage:
    python3 calc_cost.py \
        --contract contract.json \
        --sub-items sub_items.json \
        --orders orders.json \
        --time-records time_records.json \
        --staff staff.json \
        --profit-rate 0.5 \
        --output result.json

注意：
- time_records.json 应该是所有合同子项报工记录的合并数组
- 每条报工必须包含 accId 字段（合同子项 ID）
"""

import json
import argparse
from datetime import datetime

HOURS_PER_MONTH = 21.75 * 8  # 174


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_hourly_rate(monthly: float) -> float:
    return round(monthly / HOURS_PER_MONTH, 2)


def get_field(obj: dict, *keys, default=None):
    """按优先级从多个可能的字段名中获取值"""
    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]
    return default


def main():
    parser = argparse.ArgumentParser(description="MES 项目成本计算")
    parser.add_argument("--contract", required=True, help="合同信息 JSON")
    parser.add_argument("--sub-items", required=False, help="合同子项 JSON（可选）")
    parser.add_argument("--orders", required=True, help="订单明细 JSON")
    parser.add_argument("--time-records", required=True, help="报工记录 JSON（所有子项合并）")
    parser.add_argument("--staff", required=True, help="人员成本配置 JSON")
    parser.add_argument("--profit-rate", type=float, default=0.5, help="交付部门利润率 (默认 0.5)")
    parser.add_argument("--output", required=True, help="输出结果 JSON 路径")
    args = parser.parse_args()

    # Load data
    contract = load_json(args.contract)
    time_records = load_json(args.time_records)
    staff_config = load_json(args.staff)

    # Load sub-items if available
    sub_items = {}
    if args.sub_items:
        raw = load_json(args.sub_items)
        # Handle nested MES response structure
        if isinstance(raw, list):
            items_list = raw
        else:
            items_list = raw.get("operateCallBackObj", {}).get("list", [])
            if not items_list:
                items_list = raw.get("list", [])
        for item in items_list:
            item_id = item.get("itemId", item.get("acc_id", ""))
            sub_items[item_id] = {
                "name": item.get("itemName", item.get("name", "")),
                "type": item.get("itemType", item.get("type", "")),
                "plan_hours": float(item.get("planHour", item.get("plan_hours", 0))),
                "actual_hours": float(item.get("actualHours", item.get("actual_hours", 0))),
                "owner": item.get("ownerName", item.get("owner", "")),
                "start_time": item.get("startTime", item.get("start_time", "")),
                "end_time": item.get("endTime", item.get("end_time", "")),
            }

    # Build staff lookup: name -> {monthly_salary, hourly_rate, role}
    staff_map = {}
    for s in staff_config["staff"]:
        name = s["name"]
        monthly = s["monthly_salary"]
        staff_map[name] = {
            "monthly_salary": monthly,
            "hourly_rate": compute_hourly_rate(monthly),
            "role": s.get("role", ""),
        }

    # Aggregate time records by person AND by sub-item
    person_data = {}  # name -> {hours, count, records[]}
    sub_item_data = {}  # accId -> {hours, count, persons: set()}
    all_records = []  # normalized records for detail table

    for r in time_records:
        # Extract fields with multiple possible names (MES API naming)
        name = get_field(r, "executorName", "name", "executor_name", "executor", "执行人", default="未知")
        hours = float(get_field(r, "taskTime", "hours", "task_time", "工时", default=0))
        acc_id = get_field(r, "accId", "acc_id", "contractAccId", default="")
        created_time = get_field(r, "createdTime", "created_time", "date", "日期", "happenTime", default="")
        remark = get_field(r, "remark", "content", "内容", "description", default="")
        team_name = get_field(r, "teamName", "team_name", default="")

        # Person aggregation
        if name not in person_data:
            person_data[name] = {"hours": 0, "count": 0, "records": []}
        person_data[name]["hours"] += hours
        person_data[name]["count"] += 1
        person_data[name]["records"].append({
            "acc_id": acc_id,
            "hours": hours,
            "created_time": created_time,
            "remark": remark,
        })

        # Sub-item aggregation
        if acc_id:
            if acc_id not in sub_item_data:
                sub_item_data[acc_id] = {"hours": 0, "count": 0, "persons": set()}
            sub_item_data[acc_id]["hours"] += hours
            sub_item_data[acc_id]["count"] += 1
            sub_item_data[acc_id]["persons"].add(name)

        all_records.append({
            "name": name,
            "hours": hours,
            "acc_id": acc_id,
            "created_time": created_time,
            "remark": remark,
            "team_name": team_name,
        })

    # Calculate per-person cost
    total_hours = 0
    total_labor_cost = 0
    person_costs = []

    for name, data in sorted(person_data.items(), key=lambda x: x[1]["hours"], reverse=True):
        hours = data["hours"]
        total_hours += hours
        info = staff_map.get(name, None)
        if info:
            hourly = info["hourly_rate"]
            cost = round(hourly * hours, 2)
        else:
            # Use weighted average rate of configured staff
            configured = list(staff_map.values())
            if configured:
                avg_rate = sum(v["hourly_rate"] for v in configured) / len(configured)
            else:
                avg_rate = 115.80
            hourly = round(avg_rate, 2)
            cost = round(hourly * hours, 2)

        total_labor_cost += cost
        person_costs.append({
            "name": name,
            "monthly_salary": info["monthly_salary"] if info else "N/A",
            "hourly_rate": hourly,
            "hours": hours,
            "count": data["count"],
            "cost": cost,
            "role": info["role"] if info else "未知",
            "pct_of_labor": 0,  # calculated later
        })

    # Calculate percentages
    for pc in person_costs:
        pc["pct_of_labor"] = round(pc["cost"] / total_labor_cost * 100, 1) if total_labor_cost > 0 else 0

    total_labor_cost = round(total_labor_cost, 2)

    # Aggregate orders
    orders_raw = load_json(args.orders) if args.orders else []
    # Handle wrapped structure: {"details": [...]} or {"total_amount": ..., "details": [...]}
    if isinstance(orders_raw, dict):
        orders_data = orders_raw.get("details", orders_raw.get("orders", []))
        if not isinstance(orders_data, list):
            orders_data = [orders_raw]  # single order dict
    elif isinstance(orders_raw, list):
        orders_data = orders_raw
    else:
        orders_data = []
    order_total_amount = 0
    order_total_po_outsource = 0
    order_total_account_outsource = 0
    order_total_po_own = 0
    order_details = []

    for o in orders_data:
        amount = float(get_field(o, "amount", "order_amount", "订单金额", default=0))
        po_out = float(get_field(o, "po_outsource", "PO外购金额", "PO外购", default=0))
        acc_out = float(get_field(o, "account_outsource", "核算外购金额", "核算外购", default=0))
        po_own = float(get_field(o, "po_own", "PO自有金额", "PO自有", default=0))
        diff = round(acc_out - po_out, 2)

        order_total_amount += amount
        order_total_po_outsource += po_out
        order_total_account_outsource += acc_out
        order_total_po_own += po_own

        order_details.append({
            "order_name": get_field(o, "order_name", "订单名称", default="订单"),
            "amount": amount,
            "po_outsource": po_out,
            "account_outsource": acc_out,
            "po_own": po_own,
            "diff": diff,
        })

    order_total_amount = round(order_total_amount, 2)
    order_total_po_outsource = round(order_total_po_outsource, 2)
    order_total_account_outsource = round(order_total_account_outsource, 2)
    order_total_po_own = round(order_total_po_own, 2)

    # Total cost
    total_cost = round(total_labor_cost + order_total_account_outsource, 2)
    gross_profit = round(order_total_amount - total_cost, 2)
    gross_margin = round(gross_profit / order_total_amount * 100, 1) if order_total_amount > 0 else 0

    # Budget analysis
    budget_total = round(order_total_po_own * 0.15, 2)
    profit_rate = args.profit_rate
    dept_profit = round(budget_total * profit_rate, 2)
    max_allowable_cost = round(budget_total - dept_profit, 2)
    remaining_cost = round(max_allowable_cost - total_labor_cost, 2)
    remaining_hours = round(remaining_cost / (total_labor_cost / total_hours), 0) if total_labor_cost > 0 else 0
    labor_pct_of_max = round(total_labor_cost / max_allowable_cost * 100, 1) if max_allowable_cost > 0 else 0
    labor_pct_of_budget = round(total_labor_cost / budget_total * 100, 1) if budget_total > 0 else 0

    # Build sub-item summary
    sub_item_summary = []
    for acc_id, info in sub_item_data.items():
        sub_info = sub_items.get(acc_id, {})
        plan_h = sub_info.get("plan_hours", 0)
        actual_h = info["hours"]
        completion = round(actual_h / plan_h * 100, 1) if plan_h > 0 else 0
        sub_item_summary.append({
            "acc_id": acc_id,
            "name": sub_info.get("name", acc_id),
            "type": sub_info.get("type", ""),
            "plan_hours": plan_h,
            "actual_hours": actual_h,
            "completion": completion,
            "owner": sub_info.get("owner", ""),
            "start_time": sub_info.get("start_time", ""),
            "end_time": sub_info.get("end_time", ""),
            "record_count": info["count"],
            "persons": sorted(info["persons"]),
        })

    # Sort records by date descending
    all_records.sort(key=lambda x: x["created_time"], reverse=True)

    # Result
    result = {
        "contract": contract,
        "sub_items": sub_item_summary,
        "orders": {
            "total_amount": order_total_amount,
            "total_po_outsource": order_total_po_outsource,
            "total_account_outsource": order_total_account_outsource,
            "total_po_own": order_total_po_own,
            "details": order_details,
        },
        "labor": {
            "total_hours": total_hours,
            "total_count": sum(p["count"] for p in person_costs),
            "total_cost": total_labor_cost,
            "avg_hourly_rate": round(total_labor_cost / total_hours, 2) if total_hours > 0 else 0,
            "person_costs": person_costs,
        },
        "time_records": all_records,
        "total_cost": total_cost,
        "gross_profit": gross_profit,
        "gross_margin": gross_margin,
        "budget": {
            "total_budget": budget_total,
            "profit_rate": profit_rate,
            "dept_profit": dept_profit,
            "max_allowable_cost": max_allowable_cost,
            "labor_used": total_labor_cost,
            "labor_pct_of_max": labor_pct_of_max,
            "labor_pct_of_budget": labor_pct_of_budget,
            "remaining_cost": remaining_cost,
            "remaining_hours": remaining_hours,
        },
        "generated_at": datetime.now().strftime("%Y-%m-%d"),
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"成本计算完成 → {args.output}")
    print(f"  合同总额: ¥{order_total_amount:,.2f}")
    print(f"  外购成本: ¥{order_total_account_outsource:,.2f}")
    print(f"  人工成本: ¥{total_labor_cost:,.2f}")
    print(f"  项目总成本: ¥{total_cost:,.2f}")
    print(f"  毛利: ¥{gross_profit:,.2f} ({gross_margin}%)")
    print(f"  交付预算: ¥{budget_total:,.2f}")
    print(f"  最大允许成本: ¥{max_allowable_cost:,.2f}")
    print(f"  已用: ¥{total_labor_cost:,.2f} ({labor_pct_of_max}%)")
    print(f"  剩余可用: {remaining_hours:.0f}h")
    if sub_item_summary:
        print(f"  合同子项: {len(sub_item_summary)} 个")
        for si in sub_item_summary:
            print(f"    - {si['name']}: {si['actual_hours']}h (计划 {si['plan_hours']}h)")


if __name__ == "__main__":
    main()
