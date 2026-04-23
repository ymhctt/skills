#!/usr/bin/env python3
"""东西大区4部每日报工统计 + HTML报告生成"""
import json, subprocess, sys, os
from collections import defaultdict
from datetime import datetime, timedelta

REPORT_HTML = "/tmp/daily_report.html"

def get_week_range():
    today = datetime.now()
    if today.weekday() == 0:
        monday = today - timedelta(days=7)
    else:
        monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday.strftime("%Y-%m-%d"), friday.strftime("%Y-%m-%d")

def get_auto_range():
    """自动日期范围：周一~周四显示本周到昨天，周五显示上周完整周"""
    today = datetime.now()
    if today.weekday() == 0:
        last_friday = today - timedelta(days=3)
        monday = last_friday - timedelta(days=last_friday.weekday())
        from_date = monday.strftime("%Y-%m-%d")
        to_date = last_friday.strftime("%Y-%m-%d")
    else:
        from_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        to_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    return from_date, to_date

def generate_html_report(team_id: str, team_name: str, from_date: str, to_date: str, output_path: str):
    """调用 HTML 报告生成器"""
    cmd = [
        "python3",
        "/root/.openclaw/workspace/skills/mes-report/skills/generate_report.py",
        "--team-id", team_id,
        "--team-name", team_name,
        "--from", from_date,
        "--to", to_date,
        "--output", output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"报告生成失败: {result.stderr}")
    return output_path

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "auto"

    if mode == "auto":
        from_date, to_date = get_auto_range()
    elif mode == "week":
        from_date, to_date = get_week_range()
    else:
        from_date, to_date = mode, mode  # 接受 YYYY-MM-DD,YYYY-MM-DD 格式

    # 生成 HTML 报告
    html_path = REPORT_HTML
    print(f"正在生成报告: {from_date} ~ {to_date}", file=sys.stderr)
    generate_html_report("23", "东西大区4部", from_date, to_date, html_path)
    print(f"HTML报告: {html_path}", file=sys.stderr)

    # 查询 JSON 数据（用于文本推送）
    result = subprocess.run(
        ["mes", "-o", "json", "statistics", "list",
         "--from", from_date, "--to", to_date,
         "--team-id", "23", "--page-size", "500"],
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
        start = (r.get("start", "") or "")[:10]
        if start and start != "unknown":
            grouped[name]["total"] += task_time
            grouped[name]["days"][start] += task_time

    total_all = sum(v["total"] for v in grouped.values())

    # 构建输出
    weekdays = ["周一","周二","周三","周四","周五"]
    monday_dt = datetime.strptime(from_date, "%Y-%m-%d")
    weekday_dates = [(weekdays[i], (monday_dt + timedelta(days=i)).strftime("%Y-%m-%d")) for i in range(5)]

    output = {
        "week": f"{from_date}~{to_date}",
        "total_hours": round(total_all, 1),
        "record_count": len(records),
        "member_count": len(grouped),
        "html_report": html_path,
        "members": {}
    }

    for name in members:
        info = grouped.get(name, {"total": 0, "days": {}})
        row = {"total": round(info["total"], 1)}
        for day_name, day_date in weekday_dates:
            row[day_name] = round(info["days"].get(day_date, 0), 1)
        output["members"][name] = row

    # 短工时条目
    short_items = []
    for r in records:
        remark = (r.get("remark") or "").strip()
        title = (r.get("title") or "").strip()
        content = remark if remark else title
        if 0 < len(content) < 10:
            short_items.append({
                "name": r.get("executorName", ""),
                "date": (r.get("start") or "")[:10],
                "content": content,
                "hours": r.get("taskTime", 0)
            })
    output["short_items"] = short_items

    # 未报工
    reported = set(grouped.keys())
    not_reported = [m for m in members if m not in reported]
    output["not_reported"] = not_reported

    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
