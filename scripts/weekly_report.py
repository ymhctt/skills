#!/usr/bin/env python3
"""东西大区4部周报工统计 - 直接MES查询，输出结构化数据"""
import json, subprocess, sys
from collections import defaultdict
from datetime import datetime, timedelta

def get_week_range():
    today = datetime.now()
    # 本周一
    monday = today - timedelta(days=today.weekday())
    # 上周五
    friday = monday + timedelta(days=4)
    return monday.strftime("%Y-%m-%d"), friday.strftime("%Y-%m-%d")

def main():
    from_date, to_date = get_week_range()
    
    # 调用MES查询
    result = subprocess.run(
        ["mes", "-o", "json", "statistics", "list",
         "--from", from_date, "--to", to_date,
         "--team-id", "23", "--page-size", "200"],
        capture_output=True, text=True, timeout=30
    )
    
    if result.returncode != 0:
        print(f"MES查询失败: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    data = json.loads(result.stdout)
    records = data.get("list", [])
    
    members = ["石庆楠","杨明翰","罗海鸥","冯彦苇","李晴晴","聂大爽","薛瑞",
               "陈星","徐伟东","莫乾一","陈伟棠","张腾飞","杨丁娇","朱顶勋",
               "张懿骉","张磊-昆明","丁岩松","黄进","刘明民","李汶隆"]
    
    # 按人员分组
    grouped = defaultdict(lambda: {"total": 0, "days": defaultdict(float)})
    for r in records:
        name = r.get("executorName", "unknown")
        task_time = float(r.get("taskTime", 0) or 0)
        start = r.get("start", "")[:10] if r.get("start") else "unknown"
        grouped[name]["total"] += task_time
        grouped[name]["days"][start] += task_time
    
    # 输出结果
    total_all = sum(v["total"] for v in grouped.values())
    
    output = {
        "week": f"{from_date}~{to_date}",
        "total_hours": round(total_all, 1),
        "record_count": len(records),
        "member_count": len(grouped),
        "members": {}
    }
    
    weekdays = ["周一","周二","周三","周四","周五"]
    weekday_dates = []
    monday = datetime.strptime(from_date, "%Y-%m-%d")
    for i in range(5):
        weekday_dates.append((weekdays[i], (monday + timedelta(days=i)).strftime("%Y-%m-%d")))
    
    for name in members:
        info = grouped.get(name, {"total": 0, "days": {}})
        row = {"total": round(info["total"], 1)}
        for day_name, day_date in weekday_dates:
            row[day_name] = round(info["days"].get(day_date, 0), 1)
        output["members"][name] = row
    
    # 少于10字的条目
    short_items = []
    for r in records:
        remark = r.get("remark", "") or ""
        title = r.get("title", "") or ""
        content = remark if remark.strip() else title
        if 0 < len(content.strip()) < 10:
            short_items.append({
                "name": r.get("executorName", ""),
                "date": r.get("start", "")[:10],
                "content": content.strip(),
                "hours": r.get("taskTime", 0)
            })
    output["short_items"] = short_items
    
    # 未报工人员
    reported = set(grouped.keys())
    not_reported = [m for m in members if m not in reported]
    output["not_reported"] = not_reported
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
