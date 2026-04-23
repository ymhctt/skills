#!/usr/bin/env python3
"""东西大区4部每日报工统计 - 微信文本格式"""
import json, subprocess, sys
from collections import defaultdict
from datetime import datetime, timedelta

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

def query_mes(from_date: str, to_date: str):
    result = subprocess.run(
        ["mes", "-o", "json", "statistics", "list",
         "--from", from_date, "--to", to_date,
         "--team-id", "23", "--page-size", "500"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"MES查询失败: {result.stderr}")
    return json.loads(result.stdout).get("list", [])

def build_report(records, from_date, to_date):
    members = ["石庆楠","杨明翰","罗海鸥","冯彦苇","李晴晴","聂大爽","薛瑞",
               "陈星","徐伟东","莫乾一","陈伟棠","张腾飞","杨丁娇","朱顶勋",
               "张懿骉","张磊-昆明","丁岩松","黄进","刘明民","李汶隆"]

    grouped = defaultdict(lambda: {"total": 0.0, "days": defaultdict(float)})
    for r in records:
        name = r.get("executorName", "unknown")
        task_time = float(r.get("taskTime", 0) or 0)
        start = (r.get("start", "") or "")[:10]
        if start:
            grouped[name]["total"] += task_time
            grouped[name]["days"][start] += task_time

    total_all = sum(v["total"] for v in grouped.values())

    # 推断统计天数
    monday = datetime.strptime(from_date, "%Y-%m-%d")
    days_count = (datetime.strptime(to_date, "%Y-%m-%d") - monday).days + 1
    weekday_names = ["周一","周二","周三","周四","周五","周六","周日"]
    weekday_dates = [(weekday_names[i], (monday + timedelta(days=i)).strftime("%Y-%m-%d")) for i in range(days_count)]

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

    # 未报工
    not_reported = [m for m in members if m not in grouped]

    # === 生成微信文本 ===
    lines = []
    lines.append("📊 **东西大区4部 报工统计**")
    lines.append(f"周期：{from_date} ~ {to_date}（周一~{['一','二','三','四','五','六','日'][days_count-1]}）")
    lines.append(f"总工时：{total_all:.1f}h | 报工人数：{len(grouped)}/{len(members)} | 记录：{len(records)}条")
    lines.append("")
    lines.append("---")
    lines.append("**每日明细**")

    for name in members:
        info = grouped.get(name, {"total": 0.0, "days": {}})
        total = info["total"]
        day_vals = []
        for day_name, day_date in weekday_dates:
            h = info["days"].get(day_date, 0)
            if h == 0:
                day_vals.append("休")
            elif h < 8:
                day_vals.append(f"{h:.0f}❗")
            else:
                day_vals.append(f"{h:.0f}✅")
        lines.append(f"{name:<8} | {' / '.join(day_vals)} | 合计 {total:.1f}h")

    lines.append("")
    lines.append("---")

    if short_items:
        lines.append("⚠️ **报工内容过短（<10字）**")
        for item in short_items:
            lines.append(f"  {item['name']} | {item['date']} | [{item['content']}] | {item['hours']}h")
    else:
        lines.append("✅ 报工内容：无过短条目")

    if not_reported:
        lines.append(f"⚠️ **未报工人员（{len(not_reported)}人）**：{', '.join(not_reported)}")
    else:
        lines.append("✅ 报工情况：全员已报工")

    # 缺口分析
    standard = days_count * 8.0
    lines.append("")
    lines.append("---")
    lines.append("**缺口分析**")
    has_shortage = False
    for name in members:
        info = grouped.get(name, {"total": 0.0})
        shortage = max(0.0, standard - info["total"])
        if shortage > 0.5:
            lines.append(f"  {name}: 缺口 {shortage:.1f}h（已报 {info['total']:.1f}h）")
            has_shortage = True
    if not has_shortage:
        lines.append("  无缺口 ✅")

    return '\n'.join(lines)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "auto"

    if mode == "auto":
        from_date, to_date = get_auto_range()
    else:
        from_date, to_date = mode, mode

    records = query_mes(from_date, to_date)
    report = build_report(records, from_date, to_date)
    print(report)

if __name__ == "__main__":
    main()
