#!/usr/bin/env python3
"""
MES 报工统计 HTML 报告生成器（12 章节完整版）
用法：
  python3 generate_report.py \
    --team-id 23 \
    --team-name "东西大区4部" \
    --from 2026-09-05 \
    --to 2026-09-08 \
    --data /tmp/full_report.json \
    --output /tmp/dongxi_11chapters.html
"""

import argparse
import json
import os
import sys
from datetime import datetime
from collections import defaultdict

# ─── 颜色主题 ────────────────────────────────────────────────
TEAM_COLORS = ["#f59e0b", "#10b981", "#3b82f6", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"]


# ─── 小工具 ──────────────────────────────────────────────────
def h(v, default=0):
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def safe(v, default="—"):
    return default if v is None else str(v)


def member_total(m: dict) -> float:
    return h(m.get("afterHours")) + h(m.get("internalHours")) + h(m.get("preHours"))


def shortage_level(std_total: float, total: float) -> str:
    diff = total - std_total
    if diff <= -10:
        return "🔴严重"
    if diff < 0:
        return "🟠偏少"
    return ""


def trend_label(std_total: float, total: float) -> str:
    diff = total - std_total
    if diff >= 8:
        return "⬆超额"
    if diff < 0:
        return "⬇不足"
    return "➡达标"


# ─── 章节渲染器 ─────────────────────────────────────────────
def render_overview(team: dict, work_days: int, std_per_day: float, std_total: float) -> str:
    """一、团队核心指标概览（8 卡片）"""
    members = team.get("members", [])
    unreported = team.get("unreportedMembers", [])
    total_hours = h(team.get("totalHours"))
    member_count = h(team.get("memberCount"))
    full_rate = h(team.get("fullRate"))
    overtime = h(team.get("overtimeHours"))
    avg_score = h(team.get("avgScore"))
    doc_count = h(team.get("docCount"))
    svc = team.get("serviceStats") or {}
    pending_svc = h(svc.get("pendingConsultCount")) + h(svc.get("pendingFaultCount"))
    pending_orders = h(svc.get("pendingPlanCount")) + h(svc.get("unClosedFaultCount"))

    cards = [
        ("👥 团队人数", f"{int(member_count)}", f"实报 {int(team.get('reportedMemberCount', 0))} 人", "#3b82f6"),
        ("⏱️ 总工时", f"{int(total_hours)}h", f"人均 {h(team.get('avgHours'))}h", "#10b981"),
        ("✅ 满勤率", f"{full_rate:.1f}%", f"{int(team.get('fullCount', 0))} 人达标", "#2ecc71"),
        ("🔥 加班工时", f"{int(overtime)}h", "周期内累计", "#f59e0b"),
        ("⭐ 平均评分", f"{avg_score:.1f}", "团队综合", "#8b5cf6"),
        ("📄 文档数", f"{int(doc_count)}", "本周期产出", "#0ea5e9"),
        ("🛎️ 服务请求", f"{int(pending_svc)}", "待处理 (咨询+故障)", "#ef4444"),
        ("📋 工单待办", f"{int(pending_orders)}", "未完结 (计划+故障)", "#ec4899"),
    ]
    card_html = ""
    for label, value, sub, color in cards:
        card_html += f"""
      <div class="card" style="border-left-color:{color}">
        <div class="metric-label">{label}</div>
        <div class="metric" style="color:{color}">{value}</div>
        <div class="metric-label">{sub}</div>
      </div>"""
    return f"""
  <div class="overview-grid">{card_html}
  </div>"""


def render_member_table(team: dict, work_dates: list, std_per_day: float, std_total: float) -> str:
    """二、成员工时明细排名表 + 每日工时热力图"""
    members = team.get("members", [])
    rows_html = ""
    for i, m in enumerate(sorted(members, key=lambda x: -member_total(x)), 1):
        name = safe(m.get("executorName"))
        city = safe(m.get("city"), "—")
        total = member_total(m)
        after = h(m.get("afterHours"))
        internal = h(m.get("internalHours"))
        overtime = h(m.get("overtimeHours"))
        pre = h(m.get("preHours"))
        report_count = m.get("reportCount", "—")
        score = m.get("score")
        score_str = f"{h(score):.1f}" if score is not None else "—"
        shortage = member_total(m) - std_total
        if shortage <= -10:
            badge = '<span class="badge badge-red">🔴严重</span>'
        elif shortage < 0:
            badge = '<span class="badge badge-orange">🟠偏少</span>'
        else:
            badge = ""
        # 每日工时单元格
        daily = m.get("daily") or {}
        daily_cells = ""
        for d in work_dates:
            dv = h(daily.get(d))
            # 配色
            if dv == 0:
                bg = "#2d2d2d"
                tc = "#9ca3af"
            elif dv < 4:
                bg = "#3d5a3d"
                tc = "white"
            elif dv < 8:
                bg = "#4a7a4a"
                tc = "white"
            elif dv == 8:
                bg = "#2ecc71"
                tc = "white"
            else:
                bg = "#e94560"
                tc = "white"
            daily_cells += f'<td style="background:{bg};color:{tc};text-align:center;font-size:11px">{dv:g}h</td>'

        rows_html += f"""
        <tr>
          <td><span class="rank-badge rank-{i if i<=3 else 4}">{i}</span></td>
          <td><b>{name}</b></td>
          <td>{city}</td>
          <td><b>{total:g}h</b></td>
          <td>{after:g}h</td>
          <td>{internal:g}h</td>
          <td>{overtime:g}h</td>
          <td>{pre:g}h</td>
          <td>{report_count}</td>
          <td>{score_str}</td>
          <td>{badge}</td>
        </tr>"""

    header_dates = "".join(f'<th>{d[5:]}</th>' for d in work_dates)
    return f"""
  <div class="sub-title" style="border-color:#3b82f6">📋 成员工时排名（按总工时降序）</div>
  <div style="overflow-x:auto">
  <table>
    <thead><tr>
      <th>#</th><th>姓名</th><th>城市</th><th>总工时</th><th>售后</th><th>内部</th>
      <th>加班</th><th>售前</th><th>报工条数</th><th>评分</th><th>不足</th>
    </tr></thead>
    <tbody>{rows_html}
    </tbody>
  </table>
  </div>

  <div class="sub-title" style="border-color:#10b981">🗓️ 每日工时热力图</div>
  <div style="overflow-x:auto">
  <table>
    <thead><tr><th>成员</th>{header_dates}<th>合计</th></tr></thead>
    <tbody>{''.join(_render_heatmap_row(m, work_dates) for m in members)}
    </tbody>
  </table>
  </div>"""


def _render_heatmap_row(m: dict, work_dates: list) -> str:
    name = safe(m.get("executorName"))
    daily = m.get("daily") or {}
    total = 0.0
    cells = ""
    for d in work_dates:
        dv = h(daily.get(d))
        total += dv
        if dv == 0:
            bg, tc = "#2d2d2d", "#9ca3af"
        elif dv < 4:
            bg, tc = "#3d5a3d", "white"
        elif dv < 8:
            bg, tc = "#4a7a4a", "white"
        elif dv == 8:
            bg, tc = "#2ecc71", "white"
        else:
            bg, tc = "#e94560", "white"
        cells += f'<td style="background:{bg};color:{tc};text-align:center;font-size:11px">{dv:g}h</td>'
    return f'<tr><td><b>{name}</b></td>{cells}<td><b>{total:g}h</b></td></tr>'


def render_shortage(team: dict, std_total: float) -> str:
    """三、报工不足人员分析"""
    members = team.get("members", [])
    shortlist = []
    for m in members:
        total = member_total(m)
        diff = total - std_total
        if diff < 0:
            shortlist.append((m, total, diff))
    shortlist.sort(key=lambda x: x[2])  # 最不足的在前

    if not shortlist:
        return '<div style="padding:20px;text-align:center;color:#10b981;font-size:16px">🎉 全员达标，无人报工不足！</div>'

    items_html = ""
    for m, total, diff in shortlist:
        level = shortage_level(std_total, total)
        items_html += f"""
        <div class="shortage-item">
          <b>{safe(m.get('executorName'))}</b> · {safe(m.get('city'), '—')} ·
          <span style="color:#dc2626">{total:g}h</span>（差 {abs(diff):g}h）
          {level}
          <div class="shortage-detail">售后 {h(m.get('afterHours')):g}h · 内部 {h(m.get('internalHours')):g}h · 加班 {h(m.get('overtimeHours')):g}h</div>
        </div>"""
    return items_html


def render_articles(articles: list) -> str:
    """四、文档编写统计"""
    if not articles:
        return '<div style="padding:20px;text-align:center;color:#6b7280">📄 本周期团队暂无文档产出</div>'
    rows = ""
    for a in articles[:30]:
        rows += f"""
        <tr>
          <td><a href="{safe(a.get('url'), '#')}" target="_blank" style="color:#3b82f6;text-decoration:none">{safe(a.get('title'))}</a></td>
          <td>{safe(a.get('authorName'))}</td>
          <td>{safe(a.get('teamName'))}</td>
          <td>{safe(a.get('createdTime'))}</td>
        </tr>"""
    return f"""
  <div style="overflow-x:auto">
  <table>
    <thead><tr><th>标题</th><th>作者</th><th>团队</th><th>创建时间</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  </div>"""


def render_hours_distribution(team: dict) -> str:
    """五、工时类型分布（售前/售后/内部 + 加班）"""
    pre = h(team.get("preHours"))
    after = h(team.get("afterHours"))
    internal = h(team.get("internalHours"))
    overtime = h(team.get("overtimeHours"))
    total = pre + after + internal
    if total == 0:
        return '<div style="padding:20px;text-align:center;color:#6b7280">无工时类型数据</div>'
    p_pre, p_after, p_internal = pre/total*100, after/total*100, internal/total*100
    bar_pre = f'<div class="bar-row"><span class="bar-label">售前</span><div class="bar"><div class="bar-fill" style="width:{p_pre:.1f}%;background:#0ea5e9">{pre:g}h ({p_pre:.1f}%)</div></div></div>'
    bar_after = f'<div class="bar-row"><span class="bar-label">售后</span><div class="bar"><div class="bar-fill" style="width:{p_after:.1f}%;background:#10b981">{after:g}h ({p_after:.1f}%)</div></div></div>'
    bar_internal = f'<div class="bar-row"><span class="bar-label">内部</span><div class="bar"><div class="bar-fill" style="width:{p_internal:.1f}%;background:#8b5cf6">{internal:g}h ({p_internal:.1f}%)</div></div></div>'
    cards = f"""
    <div class="overview-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="card" style="border-left-color:#0ea5e9"><div class="metric-label">售前工时</div><div class="metric" style="color:#0ea5e9">{pre:g}h</div><div class="metric-label">占比 {p_pre:.1f}%</div></div>
      <div class="card" style="border-left-color:#10b981"><div class="metric-label">售后工时</div><div class="metric" style="color:#10b981">{after:g}h</div><div class="metric-label">占比 {p_after:.1f}%</div></div>
      <div class="card" style="border-left-color:#8b5cf6"><div class="metric-label">内部工时</div><div class="metric" style="color:#8b5cf6">{internal:g}h</div><div class="metric-label">占比 {p_internal:.1f}%</div></div>
      <div class="card" style="border-left-color:#f59e0b"><div class="metric-label">加班工时</div><div class="metric" style="color:#f59e0b">{overtime:g}h</div><div class="metric-label">总工时外</div></div>
    </div>"""
    return cards + bar_pre + bar_after + bar_internal


def render_quality(team: dict, scores: list) -> str:
    """六、报工质量分析"""
    # 优先用 scores 列表，否则从 members.score 推
    score_data = scores if scores else [m.get("score") for m in team.get("members", []) if m.get("score") is not None]
    if not score_data:
        return '<div style="padding:20px;text-align:center;color:#6b7280">暂无评分数据</div>'

    buckets = {"优秀(>=95)": [], "良好(85-94)": [], "合格(70-84)": [], "待改进(<70)": []}
    members = team.get("members", [])
    for m in members:
        s = m.get("score")
        if s is None: continue
        s = float(s)
        if s >= 95: buckets["优秀(>=95)"].append(m)
        elif s >= 85: buckets["良好(85-94)"].append(m)
        elif s >= 70: buckets["合格(70-84)"].append(m)
        else: buckets["待改进(<70)"].append(m)

    badge_map = {
        "优秀(>=95)": ("badge-green", "🟢 优秀"),
        "良好(85-94)": ("badge-blue", "🔵 良好"),
        "合格(70-84)": ("badge-orange", "🟡 合格"),
        "待改进(<70)": ("badge-red", "🔴 待改进"),
    }
    cards = '<div class="overview-grid" style="grid-template-columns:repeat(4,1fr)">'
    for k, ms in buckets.items():
        bcls, blabel = badge_map[k]
        avg = sum(float(m.get("score", 0)) for m in ms) / len(ms) if ms else 0
        cards += f"""
        <div class="card" style="border-left-color:#6b7280">
          <div class="metric-label">{blabel}</div>
          <div class="metric">{len(ms)} 人</div>
          <div class="metric-label">均分 {avg:.1f}</div>
        </div>"""
    cards += "</div>"

    # 明细表
    rows = ""
    for m in sorted(members, key=lambda x: -(float(x.get("score") or 0))):
        s = m.get("score")
        if s is None: continue
        s = float(s)
        if s >= 95: bcls, blabel = "badge-green", "🟢 优秀"
        elif s >= 85: bcls, blabel = "badge-blue", "🔵 良好"
        elif s >= 70: bcls, blabel = "badge-orange", "🟡 合格"
        else: bcls, blabel = "badge-red", "🔴 待改进"
        rows += f'<tr><td><b>{safe(m.get("executorName"))}</b></td><td>{safe(m.get("city"), "—")}</td><td>{member_total(m):g}h</td><td><span class="badge {bcls}">{blabel}</span></td><td><b>{s:.1f}</b></td></tr>'

    return cards + f"""
    <div style="overflow-x:auto;margin-top:16px">
    <table>
      <thead><tr><th>姓名</th><th>城市</th><th>总工时</th><th>评级</th><th>评分</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    </div>"""


def render_top10(team: dict, std_total: float) -> str:
    """七、工时排名 TOP 10"""
    members = team.get("members", [])
    sorted_m = sorted(members, key=lambda x: -member_total(x))[:10]
    rows = ""
    for i, m in enumerate(sorted_m, 1):
        total = member_total(m)
        rows += f"""
        <tr>
          <td><span class="rank-badge rank-{i if i<=3 else 4}">{i}</span></td>
          <td><b>{safe(m.get('executorName'))}</b></td>
          <td>{safe(m.get('city'), '—')}</td>
          <td><b>{total:g}h</b></td>
          <td>{trend_label(std_total, total)}</td>
        </tr>"""
    return f"""
  <div style="overflow-x:auto">
  <table>
    <thead><tr><th>#</th><th>姓名</th><th>城市</th><th>总工时</th><th>趋势</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  </div>"""


def render_service_requests(service_requests: list) -> str:
    """八、服务请求列表"""
    if not service_requests:
        return '<div style="padding:20px;text-align:center;color:#6b7280">本周期无服务请求记录</div>'
    rows = ""
    for s in service_requests[:30]:
        status = s.get("status")
        if status is None: badge = '<span class="badge badge-blue">—</span>'
        elif "完成" in str(status) or "closed" in str(status).lower(): badge = '<span class="badge badge-green">✅ 已完成</span>'
        elif "进行" in str(status) or "process" in str(status).lower(): badge = '<span class="badge badge-orange">🟠 进行中</span>'
        else: badge = f'<span class="badge badge-blue">{status}</span>'
        rows += f"""
        <tr>
          <td>{safe(s.get('accId'))}</td>
          <td><b>{safe(s.get('accName'))}</b></td>
          <td>{safe(s.get('companyName'))}</td>
          <td>{safe(s.get('createdTime'))}</td>
          <td>{badge}</td>
        </tr>"""
    return f"""
  <div style="overflow-x:auto">
  <table>
    <thead><tr><th>单号</th><th>服务名</th><th>客户</th><th>创建时间</th><th>状态</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  </div>"""


def render_member_distribution(team: dict) -> str:
    """九、团队人员分布"""
    members = team.get("members", [])
    total = h(team.get("memberCount"))
    full = h(team.get("fullCount"))
    reported = h(team.get("reportedMemberCount"))
    no_full = reported - full
    cards = f"""
    <div class="overview-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="card" style="border-left-color:#3b82f6"><div class="metric-label">总人数</div><div class="metric" style="color:#3b82f6">{int(total)}</div><div class="metric-label">含未报工</div></div>
      <div class="card" style="border-left-color:#10b981"><div class="metric-label">已报工</div><div class="metric" style="color:#10b981">{int(reported)}</div><div class="metric-label">本周期</div></div>
      <div class="card" style="border-left-color:#2ecc71"><div class="metric-label">满勤</div><div class="metric" style="color:#2ecc71">{int(full)}</div><div class="metric-label">达标</div></div>
      <div class="card" style="border-left-color:#f59e0b"><div class="metric-label">不足</div><div class="metric" style="color:#f59e0b">{int(no_full)}</div><div class="metric-label">未满勤</div></div>
    </div>"""

    # 城市分布
    city_count = defaultdict(int)
    city_hours = defaultdict(float)
    for m in members:
        c = m.get("city") or "未知"
        city_count[c] += 1
        city_hours[c] += member_total(m)
    city_rows = ""
    for c, cnt in sorted(city_count.items(), key=lambda x: -x[1]):
        hrs = city_hours[c]
        city_rows += f'<tr><td><b>{c}</b></td><td>{cnt}</td><td>{hrs:g}h</td><td>{hrs/cnt if cnt else 0:.1f}h/人</td></tr>'
    return cards + f"""
    <div class="sub-title" style="border-color:#3b82f6">🌍 城市分布</div>
    <div style="overflow-x:auto">
    <table>
      <thead><tr><th>城市</th><th>人数</th><th>总工时</th><th>人均</th></tr></thead>
      <tbody>{city_rows}</tbody>
    </table>
    </div>"""


def render_evaluation(team: dict, std_total: float) -> str:
    """十、综合评价"""
    members = team.get("members", [])
    full_rate = h(team.get("fullRate"))
    total_hours = h(team.get("totalHours"))
    avg_hours = h(team.get("avgHours"))
    avg_score = h(team.get("avgScore"))
    full_count = h(team.get("fullCount"))
    shortlist = [m for m in members if member_total(m) < std_total]
    severe = [m for m in shortlist if member_total(m) - std_total <= -10]

    # 总体评价
    if full_rate >= 80:
        overall = f"🌟 团队表现优秀！满勤率达 {full_rate:.1f}%，整体战斗力强。"
    elif full_rate >= 60:
        overall = f"✅ 团队表现良好。满勤率 {full_rate:.1f}%，仍有提升空间。"
    elif full_rate >= 40:
        overall = f"⚠️ 团队表现一般。满勤率仅 {full_rate:.1f}%，需关注工时不足问题。"
    else:
        overall = f"🔴 团队表现欠佳。满勤率 {full_rate:.1f}%，需加强工时管理。"

    # 亮点
    highlights = []
    top = sorted(members, key=lambda x: -member_total(x))[:3]
    for m in top:
        highlights.append(f"工时之星：<b>{safe(m.get('executorName'))}</b> {member_total(m):g}h")
    if avg_score >= 90:
        highlights.append(f"高质量团队：平均评分 {avg_score:.1f}，工时质量有保障")
    if not highlights:
        highlights = ["暂无突出亮点"]

    # 待改进
    improvements = []
    if severe:
        names = "、".join(safe(m.get("executorName")) for m in severe[:3])
        improvements.append(f"<b>{len(severe)} 人</b>严重报工不足（差 ≥10h）：{names}")
    if full_rate < 60:
        improvements.append(f"满勤率仅 {full_rate:.1f}%，建议加强排班与日报提醒")
    if avg_hours < 7:
        improvements.append(f"人均工时 {avg_hours:.1f}h 偏低，建议排查工作饱和度")
    if not improvements:
        improvements = ["暂未发现明显问题"]

    items = ""
    for h_text in highlights:
        items += f'<li style="color:#10b981">✅ {h_text}</li>'
    for i_text in improvements:
        items += f'<li style="color:#f59e0b">⚠️ {i_text}</li>'
    return f"""
    <div style="padding:12px 16px;background:#f0fdf4;border-left:4px solid #10b981;border-radius:6px;margin-bottom:16px">
      <b>总体评价：</b>{overall}
    </div>
    <div style="padding:16px;background:#f8fafc;border-radius:6px">
      <b>📊 详细诊断：</b>
      <ul style="margin:8px 0 0 20px;line-height:2">{items}</ul>
    </div>"""


def render_unreported(team: dict) -> str:
    """十一、未报工分析"""
    unreported = team.get("unreportedMembers", [])
    if not unreported:
        return '<div style="padding:20px;text-align:center;color:#10b981;font-size:16px">🎉 全员报工，无遗漏！</div>'
    items = ""
    for m in unreported:
        items += f"""
        <div class="shortage-item" style="background:#fef2f2;border-left-color:#ef4444">
          <b>⚠️ {safe(m.get('executorName'))}</b> · {safe(m.get('city'), '—')} · 本周期未提交任何报工
          <div class="shortage-detail">请尽快补报工时</div>
        </div>"""
    return f'<div style="padding:4px">{items}</div>'


def render_appendix(data: dict, team: dict, work_days: int, std_per_day: float, std_total: float) -> str:
    """十二、附录与数据说明（数据来源 / 字段口径 / 报告生成参数）"""
    meta = data.get("meta", {})
    task_table = data.get("taskTable", [])
    tt = task_table[0] if task_table else {}
    return f"""
  <div class="overview-grid" style="grid-template-columns:repeat(2,1fr)">
    <div class="card" style="border-left-color:#3b82f6">
      <div class="metric-label">📅 报告周期</div>
      <div class="metric" style="color:#3b82f6;font-size:18px">{meta.get('fromDate','')} — {meta.get('toDate','')}</div>
      <div class="metric-label">工作日：{work_days} 天 · 标准总工时：{int(std_total)}h</div>
    </div>
    <div class="card" style="border-left-color:#8b5cf6">
      <div class="metric-label">👥 团队人员结构</div>
      <div class="metric" style="color:#8b5cf6;font-size:18px">{int(h(tt.get('totalMemberCount')))} 人</div>
      <div class="metric-label">专家 {int(h(tt.get('expertMemberCount')))} · 备份 {int(h(tt.get('backupMemberCount')))} · 无任务 {int(h(tt.get('noTaskMemberCount')))}</div>
    </div>
  </div>

  <div class="sub-title" style="border-color:#94a3b8">📊 任务级别分布</div>
  <div style="overflow-x:auto">
  <table>
    <thead><tr><th>任务级别</th><th>人数</th><th>说明</th></tr></thead>
    <tbody>
      <tr><td>L1 重点</td><td>{int(h(tt.get('levelOneTaskMemberCount')))}</td><td>重点项目保障</td></tr>
      <tr><td>L2</td><td>{int(h(tt.get('levelTwoTaskMemberCount')))}</td><td>次重点</td></tr>
      <tr><td>L3</td><td>{int(h(tt.get('levelThreeTaskMemberCount')))}</td><td>日常维护</td></tr>
      <tr><td>L4</td><td>{int(h(tt.get('levelFourTaskMemberCount')))}</td><td>低优先级</td></tr>
      <tr><td>L5</td><td>{int(h(tt.get('levelFiveTaskMemberCount')))}</td><td>后备</td></tr>
    </tbody>
  </table>
  </div>

  <div class="sub-title" style="border-color:#94a3b8">📋 数据来源与口径说明</div>
  <div style="background:#1e3a5f;padding:14px;border-radius:6px;font-size:13px;line-height:1.8">
    • <b>数据来源：</b>MES 平台 团队 ID = {int(h(team.get('teamId')))}（{safe(team.get('teamName'))}）<br>
    • <b>工时计算：</b>售后 + 售前 + 内部 + 加班（含 weekend）<br>
    • <b>满勤标准：</b>周期工时 ≥ {int(std_total)}h（每日 {std_per_day:g}h × {work_days} 天）<br>
    • <b>不足判定：</b>差 ≥ 10h → 🔴严重；0 < 差 < 10h → 🟠偏少<br>
    • <b>质量评级：</b>≥95 优秀 / 85-94 良好 / 70-84 合格 / &lt;70 待改进<br>
    • <b>报告生成：</b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · 婷婷自动推送
  </div>"""


def render_service_stats_card(svc: dict) -> str:
    """服务请求待办小卡片（嵌入综合评价）"""
    if not svc:
        return ""
    return f"""
    <div class="overview-grid" style="grid-template-columns:repeat(4,1fr);margin-top:12px">
      <div class="card" style="border-left-color:#3b82f6"><div class="metric-label">待咨询</div><div class="metric" style="color:#3b82f6">{int(h(svc.get('pendingConsultCount')))}</div></div>
      <div class="card" style="border-left-color:#ef4444"><div class="metric-label">待处理故障</div><div class="metric" style="color:#ef4444">{int(h(svc.get('pendingFaultCount')))}</div></div>
      <div class="card" style="border-left-color:#8b5cf6"><div class="metric-label">待计划</div><div class="metric" style="color:#8b5cf6">{int(h(svc.get('pendingPlanCount')))}</div></div>
      <div class="card" style="border-left-color:#f59e0b"><div class="metric-label">未完结故障</div><div class="metric" style="color:#f59e0b">{int(h(svc.get('unClosedFaultCount')))}</div></div>
    </div>"""


# ─── HTML 主体 ───────────────────────────────────────────────
def generate_html(
    title: str,
    period_str: str,
    std_per_day: float,
    work_days: int,
    data: dict,
) -> str:
    team = data.get("teams", [{}])[0] if data.get("teams") else {}
    work_dates = data.get("meta", {}).get("workDates", [])
    std_total = work_days * std_per_day
    articles = data.get("articles", [])
    scores = data.get("scores", [])
    service_requests = data.get("serviceRequests", [])
    service_stats = data.get("serviceStats", {}) or {}

    sec1 = render_overview(team, work_days, std_per_day, std_total)
    sec2 = render_member_table(team, work_dates, std_per_day, std_total)
    sec3 = render_shortage(team, std_total)
    sec4 = render_articles(articles)
    sec5 = render_hours_distribution(team)
    sec6 = render_quality(team, scores)
    sec7 = render_top10(team, std_total)
    sec8 = render_service_requests(service_requests)
    sec9 = render_member_distribution(team)
    sec10 = render_evaluation(team, std_total)
    sec11 = render_unreported(team)
    sec12 = render_appendix(data, team, work_days, std_per_day, std_total)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} {period_str}</title>
<style>
  * {{box-sizing:border-box;margin:0;padding:0;}}
  body {{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#0f0f23;color:#e5e7eb;}}
  .container {{max-width:1280px;margin:0 auto;padding:20px;}}
  .header {{background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);color:white;padding:32px;border-radius:16px;margin-bottom:24px;}}
  .header h1 {{font-size:26px;font-weight:700;margin-bottom:8px;}}
  .header p {{font-size:14px;opacity:0.9;}}
  .section {{background:#16213e;border-radius:12px;padding:24px;margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,0.3);}}
  .section-title {{font-size:19px;font-weight:700;color:#00d4ff;margin-bottom:18px;padding-bottom:10px;border-bottom:2px solid #1e3a5f;display:flex;align-items:center;gap:8px;}}
  .section-title .icon {{font-size:22px;}}
  .sub-title {{font-size:15px;font-weight:600;color:#94a3b8;margin:20px 0 10px;padding-left:10px;border-left:3px solid #00d4ff;}}
  table {{width:100%;border-collapse:collapse;font-size:13px;color:#e5e7eb;}}
  th {{background:#1e3a5f;color:#00d4ff;font-weight:600;padding:10px 12px;text-align:left;border-bottom:2px solid #2563eb;white-space:nowrap;}}
  td {{padding:8px 12px;border-bottom:1px solid #1e3a5f;}}
  tr:hover td {{background:#1e3a5f;}}
  .overview-grid {{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px;}}
  @media(max-width:900px){{.overview-grid{{grid-template-columns:repeat(2,1fr);}}}}
  .card {{background:#1e3a5f;border-radius:10px;padding:16px;border-left:4px solid;}}
  .metric {{font-size:26px;font-weight:800;margin:4px 0;color:#fff;}}
  .metric-label {{font-size:12px;color:#94a3b8;}}
  .rank-badge {{display:inline-block;width:26px;height:26px;border-radius:50%;text-align:center;line-height:26px;font-weight:700;font-size:12px;}}
  .rank-1{{background:#fbbf24;color:#1f2937;}} .rank-2{{background:#9ca3af;color:#1f2937;}} .rank-3{{background:#b45309;color:#fff;}} .rank-4{{background:#475569;color:#fff;}}
  .badge {{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;}}
  .badge-red{{background:#7f1d1d;color:#fecaca;}} .badge-orange{{background:#7c2d12;color:#fed7aa;}}
  .badge-green{{background:#064e3b;color:#bbf7d0;}} .badge-blue{{background:#1e3a8a;color:#bfdbfe;}}
  .shortage-item {{padding:10px 14px;background:#1e3a5f;border-left:3px solid #f59e0b;margin:6px 0;border-radius:4px;font-size:13px;}}
  .shortage-detail {{font-size:12px;color:#94a3b8;margin-top:4px;}}
  .bar-row {{display:flex;align-items:center;margin:8px 0;gap:10px;}}
  .bar-label {{width:60px;color:#94a3b8;font-size:13px;}}
  .bar {{flex:1;background:#1e3a5f;border-radius:8px;overflow:hidden;height:28px;}}
  .bar-fill {{height:100%;display:flex;align-items:center;padding:0 10px;color:white;font-size:12px;font-weight:600;}}
  a {{color:#00d4ff;}}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>🏢 {title} · 报工综合分析</h1>
  <p>统计周期：<b>{period_str}</b>（{work_days}个工作日）&nbsp;&nbsp;|&nbsp;&nbsp;标准工时：<b>{int(std_total)}h/人·周期</b></p>
  <p style="margin-top:6px;opacity:0.75;font-size:12px">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>

<!-- 1. 团队核心指标概览 -->
<div class="section">
  <div class="section-title"><span class="icon">📊</span> 一、团队核心指标概览</div>
  {sec1}
</div>

<!-- 2. 成员工时明细 + 热力图 -->
<div class="section">
  <div class="section-title"><span class="icon">📋</span> 二、成员工时明细 & 每日工时</div>
  {sec2}
</div>

<!-- 3. 报工不足分析 -->
<div class="section">
  <div class="section-title"><span class="icon">⚠️</span> 三、报工不足人员分析</div>
  {sec3}
</div>

<!-- 4. 文档编写统计 -->
<div class="section">
  <div class="section-title"><span class="icon">📄</span> 四、文档编写统计</div>
  {sec4}
</div>

<!-- 5. 工时类型分布 -->
<div class="section">
  <div class="section-title"><span class="icon">📊</span> 五、工时类型分布</div>
  {sec5}
</div>

<!-- 6. 报工质量分析 -->
<div class="section">
  <div class="section-title"><span class="icon">🎯</span> 六、报工质量分析</div>
  {sec6}
</div>

<!-- 7. 工时排名 TOP10 -->
<div class="section">
  <div class="section-title"><span class="icon">🏅</span> 七、工时排名 TOP 10</div>
  {sec7}
</div>

<!-- 8. 服务请求 -->
<div class="section">
  <div class="section-title"><span class="icon">🛠️</span> 八、服务请求列表</div>
  {sec8}
</div>

<!-- 9. 团队人员分布 -->
<div class="section">
  <div class="section-title"><span class="icon">👥</span> 九、团队人员分布</div>
  {sec9}
</div>

<!-- 10. 综合评价 -->
<div class="section">
  <div class="section-title"><span class="icon">🔍</span> 十、综合评价</div>
  {sec10}
  {render_service_stats_card(service_stats)}
</div>

<!-- 11. 未报工分析 -->
<div class="section">
  <div class="section-title"><span class="icon">✅</span> 十一、未报工分析</div>
  {sec11}
</div>

<!-- 12. 附录 -->
<div class="section">
  <div class="section-title"><span class="icon">📎</span> 十二、附录与数据说明</div>
  {sec12}
</div>

</div>
</body>
</html>"""


# ─── 主入口 ──────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="生成 MES 报工统计 HTML 报告（12 章节版）")
    parser.add_argument("--team-id", type=int, required=True, help="团队 ID")
    parser.add_argument("--team-name", required=True, help="团队名称")
    parser.add_argument("--from", dest="from_date", required=True, help="开始日期 YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", required=True, help="结束日期 YYYY-MM-DD")
    parser.add_argument("--data", required=True, help="fetch_data.py 输出的 JSON 路径")
    parser.add_argument("--work-days", type=int, help="工作日天数，不传则从 meta 读")
    parser.add_argument("--output", required=True, help="输出 HTML 文件路径")

    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    work_days = args.work_days or len(data.get("meta", {}).get("workDates", []))
    if work_days == 0:
        print("[WARN] meta.workDates 为空，按 0 处理")

    period_str = f"{args.from_date} — {args.to_date}"
    print(f"[INFO] 团队：{args.team_name}（id={args.team_id}），周期 {period_str}，{work_days} 个工作日")
    print(f"[INFO] 章节数：12 章节（团队核心 / 明细 / 不足 / 文档 / 类型 / 质量 / 排名 / 服务 / 分布 / 评价 / 未报工）")

    html = generate_html(
        title=args.team_name,
        period_str=period_str,
        std_per_day=8.0,
        work_days=work_days,
        data=data,
    )

    output_path = os.path.expanduser(args.output)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"[OK] 报告已生成：{output_path}（{size_kb:.1f} KB）")
    # 自检
    section_count = html.count('class="section-title"')
    print(f"[自检] section-title 数量 = {section_count}（要求 >= 12）")
    if section_count < 12:
        print(f"[ERROR] 章节数不足！预期 12，实际 {section_count}")
        sys.exit(1)


if __name__ == "__main__":
    main()
