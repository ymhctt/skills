#!/usr/bin/env python3
"""
MES 报工统计分析报告生成器
生成美观的 HTML 格式报工报告，支持单团队和多团队
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any


def run_mes(args: List[str], timeout: int = 30) -> Dict:
    """执行 mes 命令并返回 JSON 结果"""
    cmd = ["mes", "-o", "json"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"MES 命令失败: {' '.join(args)}\n{result.stderr}")
    return json.loads(result.stdout)


def get_records(team_id: str, from_date: str, to_date: str) -> List[Dict]:
    """获取指定团队和日期范围的报工记录"""
    data = run_mes([
        "statistics", "list",
        "--from", from_date,
        "--to", to_date,
        "--team-id", team_id,
        "--page-size", "500"
    ])
    return data.get("list", [])


def get_team_members(team_id: str) -> Dict[str, int]:
    """获取团队成员 ID->Name 映射"""
    data = run_mes(["util", "list-members", "--team-id", team_id])
    members = data.get("list", data) if isinstance(data, dict) else data
    return {str(m.get("userId", "")): m.get("employeeName") or m.get("name", "") or "未知" for m in members}


def get_week_dates(from_date: str, to_date: str) -> List[tuple]:
    """返回 (weekday_name, date_str) 列表"""
    d = datetime.strptime(from_date, "%Y-%m-%d")
    end = datetime.strptime(to_date, "%Y-%m-%d")
    names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    dates = []
    while d <= end:
        dates.append((names[d.weekday()], d.strftime("%Y-%m-%d")))
        d += timedelta(days=1)
    return dates


def build_member_stats(records: List[Dict], dates: List[tuple], standard_hours: float = 8.0):
    """构建每人的统计数据"""
    # 按人分组
    person_data = defaultdict(lambda: {
        "total": 0.0,
        "days": defaultdict(float),
        "type_0": 0.0,   # 标准工时
        "type_1": 0.0,   # 项目/实施工时
        "type_3": 0.0,   # 内部事项
        "overtime": 0.0, # 加班
        "records": 0,     # 记录条数
        "projects": defaultdict(float),  # 项目工时分布
        "remarks": [],    # 备注摘要
    })

    for r in records:
        name = r.get("executorName", "未知")
        task_time = float(r.get("taskTime", 0) or 0)
        date_key = (r.get("start", "") or "")[:10]
        rec_type = r.get("type", 0)
        ot = r.get("overtimeType")
        remark = (r.get("remark") or "").strip()
        title = (r.get("title") or "").strip()

        pd = person_data[name]
        pd["total"] += task_time
        pd["days"][date_key] += task_time
        pd["records"] += 1

        # 工时类型
        if rec_type == 0:
            pd["type_0"] += task_time
        elif rec_type == 1:
            pd["type_1"] += task_time
        elif rec_type == 3:
            pd["type_3"] += task_time

        # 加班
        if ot == 0:
            pd["overtime"] += task_time

        # 项目归类
        project = r.get("accName") or r.get("companyName") or "其他"
        pd["projects"][project] += task_time

        # 备注（有内容且非短内容）
        if remark and len(remark) >= 5:
            pd["remarks"].append({
                "date": date_key,
                "hours": task_time,
                "text": remark[:100]
            })

    # 计算缺口
    total_days = len(dates)
    expected = total_days * standard_hours
    for name, pd in person_data.items():
        pd["shortage"] = max(0, expected - pd["total"])
        pd["full_days"] = sum(1 for v in pd["days"].values() if v >= standard_hours - 0.1)

    return person_data


def day_color(hours: float, standard: float = 8.0) -> str:
    """根据工时返回单元格背景色"""
    if hours == 0:
        return "#f3f4f6"  # 灰色-无工时
    elif hours < standard:
        ratio = hours / standard
        if ratio < 0.25:
            return "#fecaca"  # 红色-严重不足
        else:
            return "#fef08a"  # 黄色-不足
    else:
        return "#bbf7d0"  # 绿色-正常


def day_text_color(hours: float) -> str:
    if hours == 0:
        return "#9ca3af"
    elif hours < 8:
        return "#713f12"
    else:
        return "#065f46"


def shortage_color(短缺: float) -> str:
    if 短缺 >= 32:
        return "#991b1b"
    elif 短缺 >= 16:
        return "#b45309"
    else:
        return "#374151"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  * {{box-sizing:border-box;margin:0;padding:0;}}
  body {{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f4f8;color:#1f2937;}}
  .container {{max-width:1200px;margin:0 auto;padding:20px;}}
  .header {{background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);color:white;padding:32px;border-radius:16px;margin-bottom:24px;}}
  .header h1 {{font-size:24px;font-weight:700;margin-bottom:8px;}}
  .header p {{font-size:14px;opacity:0.85;}}
  .section {{background:white;border-radius:12px;padding:24px;margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);}}
  .section-title {{font-size:18px;font-weight:700;color:#1e3a5f;margin-bottom:18px;padding-bottom:10px;border-bottom:2px solid #e5e7eb;display:flex;align-items:center;gap:8px;}}
  .section-title .icon {{font-size:20px;}}
  table {{width:100%;border-collapse:collapse;font-size:13px;}}
  th {{background:#f8fafc;color:#374151;font-weight:600;padding:10px 12px;text-align:left;border-bottom:2px solid #e5e7eb;white-space:nowrap;}}
  td {{padding:8px 12px;border-bottom:1px solid #f3f4f6;}}
  tr:hover td {{background:#f8fafc;}}
  .team-card {{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-bottom:20px;}}
  .card {{background:#f8fafc;border-radius:10px;padding:16px;border-left:4px solid;}}
  .metric {{font-size:28px;font-weight:800;margin:4px 0;}}
  .metric-label {{font-size:12px;color:#6b7280;}}
  .rank-badge {{display:inline-block;width:28px;height:28px;border-radius:50%;text-align:center;line-height:28px;font-weight:700;font-size:14px;}}
  .shortage-item {{padding:8px 12px;background:#fff7ed;border-left:3px solid #f59e0b;margin:4px 0;border-radius:4px;font-size:13px;}}
  .tag {{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;margin:1px;}}
  .tag-pre {{background:#dbeafe;color:#1d4ed8;}} .tag-after {{background:#d1fae5;color:#065f46;}} .tag-internal {{background:#e0e7ff;color:#3730a3;}} .tag-ot {{background:#fce7f3;color:#9d174d;}}
  .progress {{background:#e5e7eb;border-radius:6px;height:10px;overflow:hidden;width:120px;display:inline-block;vertical-align:middle;}}
  .progress-bar {{height:100%;border-radius:6px;}}
  .warn {{color:#b45309;font-size:12px;}}
  .good {{color:#065f46;font-size:12px;}}
  .sub-title {{font-size:15px;font-weight:600;color:#374151;margin:16px 0 10px;padding-left:8px;border-left:3px solid #3b82f6;}}
  .grid2 {{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
  @media(max-width:700px){{.grid2{{grid-template-columns:1fr;}}}}
  .no-data {{padding:16px;text-align:center;color:#9ca3af;font-size:14px;}}
  .footer {{text-align:center;color:#9ca3af;font-size:12px;padding:16px;}}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>📊 {title}</h1>
  <p>统计周期：{from_date} — {to_date}（{total_days}天）&nbsp;&nbsp;|&nbsp;&nbsp;标准工时：{standard_hours}h/人·天</p>
</div>

{body}

<div class="footer">
  <p>由 MES 报工统计报告生成器 自动生成 &nbsp;|&nbsp; {generated_at}</p>
</div>
</div>
</body>
</html>"""


def generate_html(
    team_records: Dict[str, List[Dict]],
    team_names: Dict[str, str],
    dates: List[tuple],
    from_date: str,
    to_date: str,
    standard_hours: float = 8.0
) -> str:
    """生成完整 HTML 报告"""

    total_days = len(dates)
    weekday_names = [d[0] for d in dates]
    date_strs = [d[1] for d in dates]

    # 构建每团队统计
    team_stats = {}
    all_persons = set()

    for team_id, records in team_records.items():
        team_name = team_names.get(team_id, team_id)
        members = get_team_members(team_id)
        all_persons.update(members.values())

        # 按姓名分组
        person_data = build_member_stats(records, dates, standard_hours)

        # 团队汇总
        total_h = sum(p["total"] for p in person_data.values())
        full_days_count = sum(1 for p in person_data.values() if p["full_days"] == total_days)
        avg_h = total_h / len(person_data) if person_data else 0
        total_ot = sum(p["overtime"] for p in person_data.values())
        total_short = sum(p["shortage"] for p in person_data.values())

        team_stats[team_id] = {
            "name": team_name,
            "members": person_data,
            "member_count": len(person_data),
            "total_hours": total_h,
            "avg_hours": avg_h,
            "full_days_count": full_days_count,
            "full_days_rate": full_days_count / len(person_data) if person_data else 0,
            "overtime": total_ot,
            "shortage": total_short,
            "type_0": sum(p["type_0"] for p in person_data.values()),
            "type_1": sum(p["type_1"] for p in person_data.values()),
            "type_3": sum(p["type_3"] for p in person_data.values()),
        }

    # ===== 1. 核心指标对比 =====
    section1 = """
  <div class="section">
  <div class="section-title"><span class="icon">📊</span> 一、团队核心指标对比</div>
  <div class="team-card">
"""
    # 颜色映射
    colors = ["#f59e0b", "#10b981", "#ef4444", "#3b82f6", "#8b5cf6", "#ec4899"]
    for i, (team_id, stats) in enumerate(team_stats.items()):
        c = colors[i % len(colors)]
        section1 += f"""
    <div class="card" style="border-color:{c}">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-size:15px;font-weight:700;color:{c}">{stats['name']}</span>
        <span class="rank-badge" style="background:{c};color:white">{i+1}</span>
      </div>
      <div class="metric" style="color:{c}">{stats['avg_hours']:.1f}<small style="font-size:14px">h</small></div>
      <div class="metric-label">人均工时（共{stats['member_count']}人）</div>
      <div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px">
        <div>总工时 <b>{stats['total_hours']:.1f}h</b></div>
        <div>满勤率 <span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{stats['full_days_rate']*100:.1f}%</span></div>
        <div>加班 <b>{stats['overtime']:.1f}h</b></div>
        <div>缺口 <b>{stats['shortage']:.1f}h</b></div>
      </div>
    </div>
"""

    section1 += "  </div>\n"

    # 汇总表
    section1 += """
  <table>
    <thead><tr>
      <th>团队</th><th>人数</th><th>总工时</th><th>人均工时</th><th>满勤人数</th><th>满勤率</th>
      <th>标准工时</th><th>项目工时</th><th>内部</th><th>加班</th>
    </tr></thead><tbody>
"""
    for i, (team_id, stats) in enumerate(team_stats.items()):
        c = colors[i % len(colors)]
        section1 += f"""    <tr>
      <td><b>{stats['name']}</b></td>
      <td style="text-align:center">{stats['member_count']}</td>
      <td><b>{stats['total_hours']:.1f}h</b></td>
      <td><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{stats['avg_hours']:.1f}h</span></td>
      <td style="text-align:center">{stats['full_days_count']}</td>
      <td><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{stats['full_days_rate']*100:.1f}%</span></td>
      <td>{stats['type_0']:.1f}h</td>
      <td>{stats['type_1']:.1f}h</td>
      <td>{stats['type_3']:.1f}h</td>
      <td style="color:#ef4444;font-weight:600">{stats['overtime']:.1f}h</td>
    </tr>
"""
    section1 += "  </tbody></table></div>\n"

    # ===== 2. 工时明细 =====
    section2 = """
  <div class="section">
  <div class="section-title"><span class="icon">👤</span> 二、成员工时明细</div>
"""
    for i, (team_id, stats) in enumerate(team_stats.items()):
        c = colors[i % len(colors)]
        section2 += f'<div class="sub-title" style="border-color:{c}">{stats["name"]}（{stats["member_count"]}人）</div>\n'
        section2 += "<table style='margin-bottom:16px'>\n"
        section2 += "<thead><tr><th>姓名</th><th>总工时</th>"
        for dn in weekday_names:
            section2 += f"<th style='text-align:center'>{dn}</th>"
        section2 += "<th>标准</th><th>项目</th><th>内部</th><th>加班</th><th>缺口</th><th>记录数</th></tr></thead><tbody>\n"

        # 按总工时排序
        sorted_members = sorted(stats["members"].items(), key=lambda x: -x[1]["total"])
        for name, pd in sorted_members:
            section2 += f"<tr><td><b>{name}</b></td>"
            section2 += f"<td><span style='background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600'>{pd['total']:.1f}h</span></td>"
            for dn, dd in dates:
                h = pd["days"].get(dd, 0)
                bg = day_color(h, standard_hours)
                tc = day_text_color(h)
                section2 += f"<td style='text-align:center;background:{bg};color:{tc};font-weight:600;font-size:13px;padding:6px 4px'>{h:.1f}</td>"
            section2 += f"<td>{pd['type_0']:.1f}h</td>"
            section2 += f"<td>{pd['type_1']:.1f}h</td>"
            section2 += f"<td>{pd['type_3']:.1f}h</td>"
            ot = pd['overtime']
            section2 += f"<td style='color:#ef4444;font-weight:600'>{ot:.1f}h</td>"
            sh = pd['shortage']
            sc = shortage_color(sh)
            section2 += f"<td style='color:{sc};font-weight:600'>{sh:.1f}h</td>"
            section2 += f"<td style='text-align:center'>{pd['records']}</td></tr>\n"

        section2 += "</tbody></table>\n"

    section2 += "</div>\n"

    # ===== 3. 报工不足人员分析 =====
    section3 = """
  <div class="section">
  <div class="section-title"><span class="icon">⚠️</span> 三、报工不足人员分析</div>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px">标准：""" + f"{standard_hours}h/天 × {total_days}天 = {standard_hours * total_days}h；以下人员未达标准</p>\n"

    for i, (team_id, stats) in enumerate(team_stats.items()):
        c = colors[i % len(colors)]
        short_members = [(n, p) for n, p in stats["members"].items() if p["shortage"] > 0.1]
        short_members.sort(key=lambda x: -x[1]["shortage"])
        section3 += f'<div class="sub-title" style="border-color:{c}">{stats["name"]}（{len(short_members)}人未达标）</div>\n'
        if not short_members:
            section3 += '<div class="no-data">✅ 全部达标</div>\n'
        else:
            section3 += "<table style='margin-bottom:12px'><thead><tr><th>姓名</th><th>缺口</th><th>总工时</th>"
            for dn in weekday_names:
                section3 += f"<th style='text-align:center'>{dn}</th>"
            section3 += "</tr></thead><tbody>\n"
            for name, pd in short_members:
                section3 += f"<tr><td><b>{name}</b></td>"
                section3 += f"<td><span style='color:#ef4444;font-weight:700'>{pd['shortage']:.1f}h</span></td>"
                section3 += f"<td>{pd['total']:.1f}h</td>"
                for dn, dd in dates:
                    h = pd["days"].get(dd, 0)
                    bg = day_color(h, standard_hours)
                    tc = day_text_color(h)
                    section3 += f"<td style='text-align:center;background:{bg};color:{tc};font-weight:600;font-size:13px;padding:6px 4px'>{h:.1f}</td>"
                section3 += "</tr>\n"
            section3 += "</tbody></table>\n"

    section3 += "</div>\n"

    # ===== 4. 项目工时分布 =====
    section4 = """
  <div class="section">
  <div class="section-title"><span class="icon">💰</span> 四、项目工时分布</div>
"""
    for i, (team_id, stats) in enumerate(team_stats.items()):
        c = colors[i % len(colors)]
        section4 += f'<div class="sub-title" style="border-color:{c}">{stats["name"]}</div>\n'

        # 聚合所有人员的项目
        all_projects = defaultdict(float)
        for pd in stats["members"].values():
            for proj, hrs in pd["projects"].items():
                all_projects[proj] += hrs

        if not all_projects:
            section4 += '<div class="no-data">暂无数据</div>\n'
        else:
            sorted_projs = sorted(all_projects.items(), key=lambda x: -x[1])[:15]
            max_h = sorted_projs[0][1] if sorted_projs else 1
            section4 += "<table><thead><tr><th style='width:50px'>#</th><th>项目/客户</th><th style='text-align:right;width:80px'>工时</th><th style='width:180px'>占比</th></tr></thead><tbody>\n"
            for rank, (proj, hrs) in enumerate(sorted_projs, 1):
                pct = hrs / max_h * 100
                bar_width = hrs / max_h * 100
                emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else str(rank)
                section4 += f"<tr><td style='text-align:center'>{emoji}</td>"
                section4 += f"<td><b>{proj}</b></td>"
                section4 += f"<td style='text-align:right;font-weight:600'>{hrs:.1f}h</td>"
                section4 += f"<td><div class='progress'><div class='progress-bar' style='width:{bar_width:.1f}%;background:{c}'></div></div> {pct:.1f}%</td></tr>\n"
            section4 += "</tbody></table>\n"

    section4 += "</div>\n"

    # ===== 5. 加班条目 =====
    section5 = """
  <div class="section">
  <div class="section-title"><span class="icon">⏰</span> 五、加班工时明细</div>
"""
    for i, (team_id, stats) in enumerate(team_stats.items()):
        c = colors[i % len(colors)]
        ot_members = [(n, p) for n, p in stats["members"].items() if p["overtime"] > 0.1]
        ot_members.sort(key=lambda x: -x[1]["overtime"])
        section5 += f'<div class="sub-title" style="border-color:{c}">{stats["name"]}（{len(ot_members)}人有加班）</div>\n'
        if not ot_members:
            section5 += '<div class="no-data">✅ 无加班记录</div>\n'
        else:
            section5 += "<table><thead><tr><th>姓名</th><th>总加班</th><th>说明</th></tr></thead><tbody>\n"
            for name, pd in ot_members:
                section5 += f"<tr><td><b>{name}</b></td>"
                section5 += f"<td><span style='color:#ef4444;font-weight:700'>{pd['overtime']:.1f}h</span></td>"
                # 取第一条加班备注
                ot_remarks = [f"{rem['date']} {rem['hours']}h: {rem['text'][:40]}" for rem in pd["remarks"] if rem["hours"] > 0]
                note = ot_remarks[0] if ot_remarks else "-"
                section5 += f"<td style='color:#6b7280;font-size:12px'>{note}</td></tr>\n"
            section5 += "</tbody></table>\n"

    section5 += "</div>\n"

    # ===== 6. 报工质量（记录条数） =====
    section6 = """
  <div class="section">
  <div class="section-title"><span class="icon">⭐</span> 六、报工质量分析</div>
  <table>
    <thead><tr><th>团队</th><th>总记录数</th><th>人均记录</th><th>零记录人员</th><th>质量评价</th></tr></thead><tbody>
"""
    for i, (team_id, stats) in enumerate(team_stats.items()):
        total_records = sum(p["records"] for p in stats["members"].values())
        avg_records = total_records / stats["member_count"] if stats["member_count"] else 0
        zero_records = [n for n, p in stats["members"].items() if p["records"] == 0]
        if zero_records:
            quality = f"<span style='color:#dc2626;font-weight:600'>⚠️ {', '.join(zero_records)}</span>"
        else:
            quality = f"<span style='color:#065f46'>✅ 全部有记录</span>"
        section6 += f"""    <tr>
      <td><b>{stats['name']}</b></td>
      <td style="text-align:center">{total_records}</td>
      <td style="text-align:center">{avg_records:.1f}</td>
      <td>{', '.join(zero_records) if zero_records else '无'}</td>
      <td>{quality}</td>
    </tr>
"""
    section6 += "  </tbody></table></div>\n"

    # ===== 7. 每人备注摘要 =====
    section7 = """
  <div class="section">
  <div class="section-title"><span class="icon">📋</span> 七、每人工作摘要（备注节选）</div>
"""
    for i, (team_id, stats) in enumerate(team_stats.items()):
        c = colors[i % len(colors)]
        members_with_notes = {n: p for n, p in stats["members"].items() if p["remarks"]}
        if not members_with_notes:
            section7 += f'<div class="sub-title" style="border-color:{c}">{stats["name"]}</div>\n'
            section7 += '<div class="no-data">暂无备注</div>\n'
            continue

        section7 += f'<div class="sub-title" style="border-color:{c}">{stats["name"]}</div>\n'
        for name, pd in sorted(members_with_notes.items(), key=lambda x: -x[1]["total"]):
            section7 += f"<div class='shortage-item' style='border-color:{c};background:#f8fafc'><b>{name}</b>（合计{pd['total']:.1f}h，共{len(pd['remarks'])}条备注）</div>\n"
            for rem in pd["remarks"][:3]:  # 最多3条
                section7 += f"<div style='padding:4px 12px;font-size:12px;color:#6b7280'>{rem['date']} {rem['hours']}h: {rem['text'][:80]}</div>\n"

    section7 += "</div>\n"

    body = section1 + section2 + section3 + section4 + section5 + section6 + section7

    title = f"报工统计分析 {from_date}~{to_date}"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = HTML_TEMPLATE.format(
        title=title,
        from_date=from_date,
        to_date=to_date,
        total_days=total_days,
        standard_hours=standard_hours,
        generated_at=generated_at,
        body=body
    )

    return html


def main():
    parser = argparse.ArgumentParser(description="MES 报工统计 HTML 报告生成器")
    parser.add_argument("--team-id", help="单个团队 ID（与 --teams 互斥）")
    parser.add_argument("--team-name", help="团队名称（与 --teams 互斥）")
    parser.add_argument("--teams", help="多团队格式：id:name,id:name（如 23:东西大区4部,96:东西大区）")
    parser.add_argument("--from", dest="from_date", required=True, help="开始日期 YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", required=True, help="结束日期 YYYY-MM-DD")
    parser.add_argument("--output", required=True, help="HTML 输出路径")
    parser.add_argument("--standard-hours", type=float, default=8.0, help="每日标准工时（默认8）")
    args = parser.parse_args()

    # 智能日期范围
    today = datetime.now()
    if args.from_date == "auto":
        # 自动判断：周一到周四查本周，周五查上周
        if today.weekday() == 0:  # 周一
            # 看上周五是否有数据，如果有则显示上周
            last_friday = today - timedelta(days=3)
            args.from_date = (last_friday - timedelta(days=last_friday.weekday())).strftime("%Y-%m-%d")
            args.to_date = last_friday.strftime("%Y-%m-%d")
        else:
            args.from_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            args.to_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 解析团队
    team_ids = []
    team_names = {}
    if args.teams:
        for entry in args.teams.split(","):
            tid, tname = entry.split(":", 1)
            team_ids.append(tid.strip())
            team_names[tid.strip()] = tname.strip()
    elif args.team_id and args.team_name:
        team_ids = [args.team_id]
        team_names = {args.team_id: args.team_name}
    else:
        print("错误：必须指定 --team-id + --team-name 或 --teams", file=sys.stderr)
        sys.exit(1)

    dates = get_week_dates(args.from_date, args.to_date)

    # 获取各团队记录
    team_records = {}
    for team_id in team_ids:
        print(f"正在查询团队 {team_names.get(team_id, team_id)} ({team_id})...", file=sys.stderr)
        try:
            records = get_records(team_id, args.from_date, args.to_date)
            team_records[team_id] = records
            print(f"  获取到 {len(records)} 条记录", file=sys.stderr)
        except Exception as e:
            print(f"  查询失败: {e}", file=sys.stderr)
            team_records[team_id] = []

    # 生成 HTML
    html = generate_html(
        team_records, team_names, dates,
        args.from_date, args.to_date,
        standard_hours=args.standard_hours
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"报告已生成: {args.output}", file=sys.stderr)
    print(f"包含 {len(team_ids)} 个团队，日期范围 {args.from_date} ~ {args.to_date}", file=sys.stderr)


if __name__ == "__main__":
    main()
