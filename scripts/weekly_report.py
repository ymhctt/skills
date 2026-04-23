#!/usr/bin/env python3
"""东西大区4部每日报工统计 - 生成HTML文件+微信文本"""
import json, subprocess, sys
from collections import defaultdict
from datetime import datetime, timedelta

def get_auto_range():
    today = datetime.now()
    if today.weekday() == 0:
        last_friday = today - timedelta(days=3)
        monday = last_friday - timedelta(days=last_friday.weekday())
        return monday.strftime("%Y-%m-%d"), last_friday.strftime("%Y-%m-%d")
    else:
        from_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        to_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    return from_date, to_date

def query_mes(from_date, to_date):
    result = subprocess.run(
        ["mes", "-o", "json", "statistics", "list",
         "--from", from_date, "--to", to_date,
         "--team-id", "23", "--page-size", "500"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"MES查询失败: {result.stderr}")
    return json.loads(result.stdout).get("list", [])

def cell(h):
    """返回表格单元格html"""
    if h == 0:
        return "<td style='text-align:center;color:#9ca3af'>休</td>"
    elif h < 8:
        return f"<td style='text-align:center;color:#b45309;font-weight:600'>{h:.0f}❗</td>"
    else:
        return f"<td style='text-align:center;color:#065f46;font-weight:600'>{h:.0f}✅</td>"

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
    monday = datetime.strptime(from_date, "%Y-%m-%d")
    end_day = datetime.strptime(to_date, "%Y-%m-%d")
    days_count = (end_day - monday).days + 1
    names = ["周一","周二","周三","周四","周五","周六","周日"]
    weekday_dates = [(names[i], (monday + timedelta(days=i)).strftime("%Y-%m-%d")) for i in range(days_count)]
    weekday_names = [n for n, _ in weekday_dates]

    # Short items
    short_items = []
    for r in records:
        remark = (r.get("remark") or "").strip()
        title = (r.get("title") or "").strip()
        content = remark if remark else title
        if 0 < len(content) < 10:
            short_items.append({"name": r.get("executorName", ""), "date": (r.get("start") or "")[:10], "content": content, "hours": r.get("taskTime", 0)})

    # Not reported
    not_reported = [m for m in members if m not in grouped]

    # Build HTML table rows
    th_days = "".join([f"<th style='text-align:center'>{n}</th>" for n in weekday_names])
    rows_html = []
    for name in members:
        info = grouped.get(name, {"total": 0.0, "days": {}})
        cells = "".join([cell(info["days"].get(dd, 0)) for _, dd in weekday_dates])
        rows_html.append(f"<tr><td><b>{name}</b></td>{cells}<td style='font-weight:600'>{info['total']:.1f}h</td></tr>")

    # Shortage
    standard = days_count * 8.0
    shortage_items = [(n, grouped.get(n, {"total": 0.0})["total"]) for n in members]
    shortage_items = [(n, t, max(0.0, standard - t)) for n, t in shortage_items if max(0.0, standard - t) > 0.5]
    shortage_items.sort(key=lambda x: -x[2])
    if shortage_items:
        sh = "<br>".join([f"{n}: 缺口 <b>{s:.1f}h</b>（已报 {t:.1f}h）" for n, t, s in shortage_items])
        shortage_html = f"<div style='background:#fef3c7;padding:12px;border-radius:6px'>{sh}</div>"
    else:
        shortage_html = "<div style='color:#065f46'>✅ 无缺口</div>"

    # Special section
    special = []
    if short_items:
        items = "<br>".join([f"• {x['name']} | {x['date']} | [{x['content']}] | {x['hours']}h" for x in short_items])
        special.append(f"<b style='color:#b45309'>⚠️ 报工内容过短（&lt;10字）</b><br>{items}")
    else:
        special.append("<span style='color:#065f46'>✅ 报工内容：无过短条目</span>")
    if not_reported:
        special.append(f"<b style='color:#dc2626'>⚠️ 未报工（{len(not_reported)}人）</b>：{', '.join(not_reported)}")
    else:
        special.append("<span style='color:#065f46'>✅ 报工情况：全员已报工</span>")
    special_html = "<br><br>".join(special)

    # Chinese day suffix
    day_suffix = ["一","二","三","四","五","六","日"][days_count - 1]

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>东西大区4部 报工统计 {from_date}~{to_date}</title>
<style>
  body {{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f4f8;color:#1f2937;padding:20px;}}
  .card {{background:white;border-radius:12px;padding:24px;margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,0.06);}}
  .header {{background:linear-gradient(135deg,#1e3a5f,#2563eb);color:white;padding:24px;border-radius:12px;margin-bottom:16px;}}
  .header h1 {{font-size:20px;margin-bottom:6px;}}
  table {{width:100%;border-collapse:collapse;font-size:13px;}}
  th {{background:#f8fafc;color:#374151;font-weight:600;padding:8px 12px;text-align:left;border-bottom:2px solid #e5e7eb;}}
  td {{padding:8px 12px;border-bottom:1px solid #f3f4f6;}}
  .section-title {{font-size:16px;font-weight:700;color:#1e3a5f;margin:20px 0 12px;padding-bottom:8px;border-bottom:2px solid #e5e7eb;}}
  .footer {{text-align:center;color:#9ca3af;font-size:12px;padding:16px;}}
</style>
</head>
<body>
<div class="header">
  <h1>📊 东西大区4部 报工统计</h1>
  <p>周期：{from_date} ~ {to_date}（{days_count}天）&nbsp;|&nbsp;总工时：<b>{total_all:.1f}h</b>&nbsp;|&nbsp;{len(grouped)}/{len(members)}人已报工&nbsp;|&nbsp;{len(records)}条记录</p>
</div>

<div class="card">
  <div class="section-title">👤 每日工时明细</div>
  <table>
    <thead><tr><th>姓名</th>{th_days}<th>合计</th></tr></thead>
    <tbody>
{''.join(rows_html)}
    </tbody>
  </table>
</div>

<div class="card">
  <div class="section-title">⚠️ 缺口分析</div>
  {shortage_html}
</div>

<div class="card">
  <div class="section-title">📋 特殊条目</div>
  {special_html}
</div>

<div class="footer">自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</body>
</html>"""

    # Text format for WeChat
    text_lines = [f"📊 **东西大区4部 报工统计**"]
    text_lines.append(f"周期：{from_date} ~ {to_date}（周一~{day_suffix}）")
    text_lines.append(f"总工时：{total_all:.1f}h | 报工人数：{len(grouped)}/{len(members)} | 记录：{len(records)}条")
    text_lines.append("")
    text_lines.append("---")
    text_lines.append("**每日明细**")
    for name in members:
        info = grouped.get(name, {"total": 0.0, "days": {}})
        day_vals = []
        for _, dd in weekday_dates:
            h = info["days"].get(dd, 0)
            if h == 0: day_vals.append("休")
            elif h < 8: day_vals.append(f"{h:.0f}❗")
            else: day_vals.append(f"{h:.0f}✅")
        text_lines.append(f"{name:<8} | {' / '.join(day_vals)} | 合计 {info['total']:.1f}h")
    text_lines.append("")
    text_lines.append("---")
    if short_items:
        text_lines.append("⚠️ **报工内容过短（<10字）**")
        for x in short_items:
            text_lines.append(f"  {x['name']} | {x['date']} | [{x['content']}] | {x['hours']}h")
    else:
        text_lines.append("✅ 报工内容：无过短条目")
    if not_reported:
        text_lines.append(f"⚠️ **未报工人员（{len(not_reported)}人）**：{', '.join(not_reported)}")
    else:
        text_lines.append("✅ 报工情况：全员已报工")
    text_lines.append("")
    text_lines.append("---")
    text_lines.append("**缺口分析**")
    if shortage_items:
        for n, t, s in shortage_items:
            text_lines.append(f"  {n}: 缺口 {s:.1f}h（已报 {t:.1f}h）")
    else:
        text_lines.append("  无缺口 ✅")

    return {
        "html": html,
        "text": "\n".join(text_lines),
        "from_date": from_date,
        "to_date": to_date
    }

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "auto"
    if mode == "auto":
        from_date, to_date = get_auto_range()
    else:
        from_date, to_date = mode, mode

    records = query_mes(from_date, to_date)
    result = build_report(records, from_date, to_date)

    html_path = f"/tmp/report_{from_date.replace('-','')}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(result["html"])

    output = {
        "html_path": html_path,
        "text": result["text"],
        "from_date": from_date,
        "to_date": to_date
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
