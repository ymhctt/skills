#!/usr/bin/env python3
"""东西大区4部报工统计 - cron调用入口，自动判断日期"""
import subprocess, sys, json
from datetime import datetime, timedelta

def get_auto_range():
    today = datetime.now()
    if today.weekday() == 0:  # 周一
        last_friday = today - timedelta(days=3)
        monday = last_friday - timedelta(days=last_friday.weekday())
        return monday.strftime("%Y-%m-%d"), last_friday.strftime("%Y-%m-%d"), (last_friday - monday).days + 1
    else:
        monday = today - timedelta(days=today.weekday())
        yesterday = today - timedelta(days=1)
        return monday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"), (yesterday - monday).days + 1

from_date, to_date, work_days = get_auto_range()
print(f"[INFO] 报告周期: {from_date} ~ {to_date} ({work_days}个工作日)", file=sys.stderr)

# 生成 HTML 报告
result = subprocess.run([
    "python3",
    "/root/.openclaw/workspace/skills/mes-work-report/scripts/generate_report.py",
    "--team-id", "23",
    "--team-name", "东西大区4部",
    "--from", from_date,
    "--to", to_date,
    "--work-days", str(work_days),
    "--title", "东西大区4部报工统计",
    "--output", "/tmp/dongxi_report.html"
], capture_output=True, text=True, timeout=300)

if result.returncode != 0:
    print(f"[ERROR] {result.stderr}", file=sys.stderr)
    sys.exit(1)

print(result.stdout, file=sys.stderr)

# 读取 JSON 数据生成摘要
data_result = subprocess.run([
    "python3",
    "/root/.openclaw/workspace/skills/mes-work-report/scripts/fetch_data.py",
    "--team-id", "23",
    "--team-name", "东西大区4部",
    "--from", from_date,
    "--to", to_date,
    "--output", "/tmp/dongxi_report_data.json"
], capture_output=True, text=True, timeout=120)

summary = ""
if data_result.returncode == 0:
    try:
        d = json.load(open("/tmp/dongxi_report_data.json"))
        t = d["teams"][0]
        summary = (f"📊 {t['teamName']} | {t['totalHours']}h | "
                   f"{t['reportedMemberCount']}/{t['memberCount']}人已报 | "
                   f"满勤率{t['fullRate']}% | 不达标{len([m for m in t['members'] if m['shortage']>0])}人")
    except:
        summary = "报告已生成"

print(f"[OK] HTML: /tmp/dongxi_report.html")
print(f"摘要: {summary}")
