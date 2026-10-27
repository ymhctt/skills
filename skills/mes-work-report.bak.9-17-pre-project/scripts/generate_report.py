#!/usr/bin/env python3
"""
东西大区四团队报工分析 HTML 报告生成器
用法：python3 generate_report.py --input /tmp/mes_analysis_result.json --output /path/to/report.html
"""

import json
import argparse
import os
import sys
from datetime import date
from collections import Counter, OrderedDict

# 🆕 合同名解析：报工 accId == 合同子项 itemId，精确关联「实施计划 → 合同」
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from build_contract_item_map import load_map as _load_cmap, resolve_contract as _resolve_contract
    _CONTRACT_MAP = _load_cmap()
except Exception:
    _CONTRACT_MAP = None


def _truncate(s, n):
    s = (s or '').strip()
    return s if len(s) <= n else s[:n - 1] + '…'


def pc_tag_html(acc_name, acc_meta):
    """生成「合同名／实施计划」标签（内联样式版）；无合同映射时降级为仅实施计划名"""
    contract = ''
    if _CONTRACT_MAP and acc_meta:
        acc_id, company = acc_meta
        try:
            contract, _num, ok = _resolve_contract(_CONTRACT_MAP, acc_id, acc_name, company)
        except Exception:
            contract, ok = '', False
    full = f"{contract}／{acc_name}" if contract else acc_name
    if contract:
        if contract in acc_name or acc_name in contract:
            # 合同名与实施计划名互为包含时只显示更长者，避免标签冗余
            txt = f"<b style='font-weight:700'>{_truncate(max(contract, acc_name, key=len), 34)}</b>"
        else:
            txt = (f"<b style='font-weight:700'>{_truncate(contract, 26)}</b>"
                   f"<span style='color:#6366f1;font-weight:400;margin-left:2px'>／{_truncate(acc_name, 18)}</span>")
    else:
        txt = _truncate(acc_name, 30)
    return (f"<span title='{full}' style='display:inline-block;background:#e0e7ff;color:#3730a3;"
            f"padding:2px 9px;border-radius:10px;font-size:11px;margin:2px 3px 2px 0;font-weight:500'>{txt}</span>")

# ==================== 智能总结函数 ====================
def generate_person_summary(name, items, person_daily, member_stats, work_days, standard_total):
    """根据报工内容生成智能工作总结"""
    html = ''
    
    # 1. 按项目聚合
    project_map = OrderedDict()  # project_name -> {hours, remarks, dates}
    for item in items:
        proj = item.get('accName', '') or '内部事项'
        if proj not in project_map:
            project_map[proj] = {'hours': 0, 'remarks': [], 'dates': set()}
        project_map[proj]['hours'] += item.get('hours', 0)
        remark = item.get('remark', '').strip()
        if remark:
            # 拆分多行，每行作为独立任务点
            for line in remark.split('\n'):
                line = line.strip()
                if line:
                    # 去掉行首序号如 "1、" "2."
                    import re
                    line = re.sub(r'^\d+[、.．]\s*', '', line)
                    if line:
                        project_map[proj]['remarks'].append(line)
        project_map[proj]['dates'].add(item.get('start', '')[:10] or item.get('date', ''))
    
    total_hours = member_stats['totalHours']
    daily_avg = total_hours / work_days if work_days else 0
    
    # 判断报工质量
    if total_hours < standard_total * 0.6:
        quality_level = 'poor'
        quality_label = '报工不足'
        quality_color = '#dc2626'
        quality_bg = '#fee2e2'
    elif total_hours < standard_total * 0.8:
        quality_level = 'warning'
        quality_label = '需改善'
        quality_color = '#f59e0b'
        quality_bg = '#fef3c7'
    else:
        quality_level = 'good'
        quality_label = '达标'
        quality_color = '#10b981'
        quality_bg = '#d1fae5'
    
    # 2. 按工时排序项目
    sorted_projects = sorted(project_map.items(), key=lambda x: x[1]['hours'], reverse=True)
    
    # 3. 生成主要工作完成情况
    html += '<div style="margin-bottom:10px">'
    html += '<div style="font-size:13px;font-weight:600;color:#1e293b;margin-bottom:6px">📌 本周主要工作</div>'
    
    for proj, info in sorted_projects:
        pct = int(info['hours'] / total_hours * 100) if total_hours else 0
        proj_color = '#3b82f6' if pct >= 30 else '#6b7280'
        
        html += f'<div style="margin:6px 0;padding:8px;background:white;border-radius:6px;border:1px solid #e2e8f0">'
        html += f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
        html += f'<span style="font-size:13px;font-weight:600;color:{proj_color}">{proj}</span>'
        html += f'<span style="font-size:12px;color:#6b7280">{info["hours"]:.1f}h（{pct}%）</span>'
        html += f'</div>'
        
        # 进度条
        bar_color = '#3b82f6' if pct >= 30 else '#94a3b8'
        html += f'<div style="height:4px;background:#e2e8f0;border-radius:2px;margin-bottom:6px">'
        html += f'<div style="height:4px;width:{pct}%;background:{bar_color};border-radius:2px"></div></div>'
        
        # 任务明细（去重，最多5条）
        unique_tasks = list(dict.fromkeys(info['remarks']))[:5]
        for task in unique_tasks:
            # 判断任务状态（简单启发式）
            status_icon = '✅'
            status_text = ''
            task_lower = task.lower()
            if any(kw in task for kw in ['观察', '等待', '待', '催促', '联系', '请客户', 'oncall', 'on-call', '研发']):
                status_icon = '⏳'
            elif any(kw in task for kw in ['无法', '失败', '异常', '报错', '问题', 'bug', 'Bug']):
                status_icon = '⚠️'
            
            html += f'<div style="font-size:12px;color:#475569;margin:2px 0 2px 8px">{status_icon} {task}</div>'
        
        if len(info['remarks']) > 5:
            html += f'<div style="font-size:11px;color:#94a3b8;margin-top:2px">...等{len(info["remarks"])}项任务</div>'
        
        html += '</div>'
    
    html += '</div>'
    
    # 4. 下周工作计划（基于当前进展推断）
    ongoing_tasks = []
    blocked_tasks = []
    for proj, info in sorted_projects:
        for task in info['remarks']:
            task_lower = task.lower()
            if any(kw in task for kw in ['观察', '等待', '待', '催促', '预计', '还在', '进行中']):
                ongoing_tasks.append((proj, task))
            elif any(kw in task for kw in ['无法', '失败', '异常', '报错', 'bug', 'Bug', '请客户', 'oncall']):
                blocked_tasks.append((proj, task))
    
    if ongoing_tasks or blocked_tasks:
        html += '<div style="margin-bottom:10px">'
        html += '<div style="font-size:13px;font-weight:600;color:#1e293b;margin-bottom:6px">📋 后续工作计划</div>'
        
        if blocked_tasks:
            html += '<div style="font-size:12px;color:#dc2626;font-weight:500;margin-bottom:4px">🔴 阻塞项（需优先处理）</div>'
            for proj, task in blocked_tasks[:3]:
                html += f'<div style="font-size:12px;color:#475569;margin:2px 0 4px 12px">• [{proj}] {task}</div>'
        
        if ongoing_tasks:
            html += '<div style="font-size:12px;color:#f59e0b;font-weight:500;margin-bottom:4px">🟡 进行中（需跟进）</div>'
            for proj, task in ongoing_tasks[:3]:
                html += f'<div style="font-size:12px;color:#475569;margin:2px 0 4px 12px">• [{proj}] {task}</div>'
        
        html += '</div>'
    
    # 5. 综合评价
    # 饱和度
    if daily_avg >= 7:
        sat_score, sat_label = 5, '⭐⭐⭐⭐⭐'
    elif daily_avg >= 6:
        sat_score, sat_label = 4, '⭐⭐⭐⭐'
    elif daily_avg >= 4:
        sat_score, sat_label = 3, '⭐⭐⭐'
    elif daily_avg >= 2:
        sat_score, sat_label = 2, '⭐⭐'
    else:
        sat_score, sat_label = 1, '⭐'
    
    # 聚焦度（最高占比项目的集中度）
    max_proj_pct = sorted_projects[0][1]['hours'] / total_hours * 100 if sorted_projects and total_hours else 0
    if max_proj_pct >= 50:
        focus_score, focus_label = 5, '⭐⭐⭐⭐⭐'
    elif max_proj_pct >= 35:
        focus_score, focus_label = 4, '⭐⭐⭐⭐'
    elif max_proj_pct >= 25:
        focus_score, focus_label = 3, '⭐⭐⭐'
    else:
        focus_score, focus_label = 2, '⭐⭐'
    
    # 问题推动力
    issue_count = sum(1 for item in items if any(kw in item.get('remark', '') for kw in ['问题', '分析', '排查', '解决', '处理', 'oncall']))
    if issue_count >= 4:
        drive_score, drive_label = 5, '⭐⭐⭐⭐⭐'
    elif issue_count >= 2:
        drive_score, drive_label = 4, '⭐⭐⭐⭐'
    elif issue_count >= 1:
        drive_score, drive_label = 3, '⭐⭐⭐'
    else:
        drive_score, drive_label = 2, '⭐⭐'
    
    # 报工质量预警
    warning_html = ''
    if quality_level == 'poor':
        warning_html = f'<div style="margin-top:8px;padding:8px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;font-size:12px;color:#dc2626">⚠️ <b>报工预警：</b>本周仅报工 {total_hours:.1f}h，远低于标准 {standard_total:.0f}h，请加强报工规范。</div>'
    elif quality_level == 'warning':
        warning_html = f'<div style="margin-top:8px;padding:8px;background:#fffbeb;border:1px solid #fde68a;border-radius:6px;font-size:12px;color:#92400e">💡 <b>改善建议：</b>本周报工 {total_hours:.1f}h，未达标准 {standard_total:.0f}h，建议提高报工完整度。</div>'
    
    avg_score = (sat_score + focus_score + drive_score) / 3
    
    html += f'<div style="padding:10px;background:#fafafa;border-radius:8px;border:1px solid #e2e8f0">'
    html += f'<div style="font-size:13px;font-weight:600;color:#1e293b;margin-bottom:6px">💡 综合评价（均分 {avg_score:.1f}/5）</div>'
    html += f'<div style="display:flex;gap:16px;flex-wrap:wrap;font-size:12px">'
    html += f'<span>工作饱和度：{sat_label}（日均{daily_avg:.1f}h）</span>'
    html += f'<span>项目聚焦度：{focus_label}（核心项目{max_proj_pct:.0f}%）</span>'
    html += f'<span>问题推动力：{drive_label}（处理{issue_count}个问题）</span>'
    html += f'</div>'
    html += warning_html
    html += '</div>'
    
    return html


# ==================== 默认配置 ====================
STANDARD_DAILY = 8.0
TEAM_COLORS = {'t2': '#3b82f6', 't3': '#10b981', 't23': '#f59e0b', 't19': '#ef4444'}
DEFAULT_TEAMS = [
    {'id': 't2',  'name': '东西大区1部'},
    {'id': 't3',  'name': '东西大区2部'},
    {'id': 't23', 'name': '东西大区4部'},
    {'id': 't19', 'name': '东西大区5部'},
]

# ==================== HTML 辅助函数 ====================

def compliance_badge(rate):
    if rate >= 80:
        color, bg = '#065f46', '#d1fae5'
    elif rate >= 50:
        color, bg = '#92400e', '#fef3c7'
    else:
        color, bg = '#991b1b', '#fee2e2'
    return f'<span style="background:{bg};color:{color};padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{rate:.1f}%</span>'

def hours_badge(h):
    if h >= 40:
        color, bg = '#065f46', '#d1fae5'
    elif h >= 32:
        color, bg = '#92400e', '#fef3c7'
    else:
        color, bg = '#991b1b', '#fee2e2'
    return f'<span style="background:{bg};color:{color};padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{h:.1f}h</span>'

def day_cell(h):
    if h >= 8:
        bg, color = '#bbf7d0', '#065f46'
    elif h >= 4:
        bg, color = '#fef08a', '#713f12'
    elif h > 0:
        bg, color = '#fecaca', '#7f1d1d'
    else:
        bg, color = '#f3f4f6', '#9ca3af'
    return f'<td style="text-align:center;background:{bg};color:{color};font-weight:600;font-size:13px;padding:6px 4px">{h:.1f}</td>'

def fmt_date_label(d_str):
    """格式化日期标签: '04-13(周一)'"""
    dt = date.fromisoformat(d_str)
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return f'{d_str[5:]}({weekdays[dt.weekday()]})'

# ==================== 报告生成 ====================

def generate_report(data):
    """
    从分析结果 JSON 生成完整 HTML 报告字符串
    
    参数:
        data: 包含 meta, teams, teams_config 的字典
    """
    meta = data['meta']
    teams_config = data.get('teams_config', DEFAULT_TEAMS)
    all_teams = data['teams']

    date_strs = meta['date_strs']
    date_labels = [fmt_date_label(d) for d in date_strs]
    mode_label = '月度' if meta['mode'] == 'month' else '周'
    standard_total = meta['standard_total']
    work_days = meta['work_days']
    report_time = meta['report_time']

    # 计算综合排名
    team_ranks = sorted(all_teams.items(),
        key=lambda x: (x[1]['stats']['compliance_rate'], x[1]['stats']['avg_hours']), reverse=True)
    rank_map = {tid: i+1 for i, (tid, _) in enumerate(team_ranks)}

    TEAMS = teams_config

    # ---- CSS ----
    css = """
  * {box-sizing:border-box;margin:0;padding:0;}
  body {font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f4f8;color:#1f2937;}
  .container {max-width:1200px;margin:0 auto;padding:20px;}
  .header {background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);color:white;padding:32px;border-radius:16px;margin-bottom:24px;}
  .header h1 {font-size:24px;font-weight:700;margin-bottom:8px;}
  .header p {font-size:14px;opacity:0.85;}
  .section {background:white;border-radius:12px;padding:24px;margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);}
  .section-title {font-size:18px;font-weight:700;color:#1e3a5f;margin-bottom:18px;padding-bottom:10px;border-bottom:2px solid #e5e7eb;display:flex;align-items:center;gap:8px;}
  .section-title .icon {font-size:20px;}
  table {width:100%;border-collapse:collapse;font-size:13px;}
  th {background:#f8fafc;color:#374151;font-weight:600;padding:10px 12px;text-align:left;border-bottom:2px solid #e5e7eb;white-space:nowrap;}
  td {padding:8px 12px;border-bottom:1px solid #f3f4f6;}
  tr:hover td {background:#f8fafc;}
  .team-card {display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:20px;}
  @media(min-width:900px){.team-card{grid-template-columns:repeat(4,1fr);}}
  .card {background:#f8fafc;border-radius:10px;padding:16px;border-left:4px solid;}
  .metric {font-size:28px;font-weight:800;margin:4px 0;}
  .metric-label {font-size:12px;color:#6b7280;}
  .rank-badge {display:inline-block;width:28px;height:28px;border-radius:50%;text-align:center;line-height:28px;font-weight:700;font-size:14px;}
  .rank-1{background:#fbbf24;color:white;} .rank-2{background:#9ca3af;color:white;} .rank-3{background:#b45309;color:white;} .rank-4{background:#6b7280;color:white;}
  .shortage-item {padding:8px 12px;background:#fff7ed;border-left:3px solid #f59e0b;margin:4px 0;border-radius:4px;font-size:13px;}
  .shortage-detail {font-size:12px;color:#6b7280;margin-top:4px;}
  .tag {display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;margin:1px;}
  .tag-pre {background:#dbeafe;color:#1d4ed8;} .tag-after {background:#d1fae5;color:#065f46;} .tag-internal {background:#e0e7ff;color:#3730a3;} .tag-ot {background:#fce7f3;color:#9d174d;}
  .progress {background:#e5e7eb;border-radius:6px;height:10px;overflow:hidden;width:120px;display:inline-block;vertical-align:middle;}
  .progress-bar {height:100%;border-radius:6px;}
  .article-item {padding:8px 12px;background:#f0fdf4;border-left:3px solid #10b981;margin:4px 0;border-radius:4px;font-size:13px;}
  .warn {color:#b45309;font-size:12px;}
  .good {color:#065f46;font-size:12px;}
  .sub-title {font-size:15px;font-weight:600;color:#374151;margin:16px 0 10px;padding-left:8px;border-left:3px solid #3b82f6;}
  .grid2 {display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  @media(max-width:700px){.grid2{grid-template-columns:1fr;}}
"""

    # ---- Header ----
    header = f"""
<div class="header">
  <h1>🏢 东西大区四团队 · 本{mode_label}报工综合分析</h1>
  <p>统计周期：{meta['date_start']} — {meta['date_end']}（共{work_days}个工作日）&nbsp;&nbsp;|&nbsp;&nbsp;标准工时：{standard_total:.0f}h/人·{mode_label}</p>
</div>

<!-- 目录导航 -->
<div style="position:sticky;top:0;z-index:100;background:linear-gradient(135deg,#1e293b,#334155);padding:12px 24px;border-radius:12px;margin:16px 0 24px;box-shadow:0 4px 12px rgba(0,0,0,0.15)">
  <div style="font-size:13px;color:#94a3b8;margin-bottom:8px;font-weight:500">📑 报告目录</div>
  <div style="display:flex;flex-wrap:wrap;gap:8px">
    <a href="#section1" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px;transition:all 0.2s;hover:background:rgba(255,255,255,0.15)">📊 核心指标</a>
    <a href="#section2" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">📅 工时明细</a>
    <a href="#section3" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">⚠️ 报工不足</a>
    <a href="#section4" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">📝 文档统计</a>
    <a href="#section5" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">💰 项目成本</a>
    <a href="#section6" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">⭐ 报工质量</a>
    <a href="#section7" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">🏆 项目排名</a>
    <a href="#section8" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">👤 工作总结</a>
    <a href="#section9" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">🎫 服务请求</a>
    <a href="#section10" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">🎯 综合评价</a>
    <a href="#section11" style="color:#e2e8f0;text-decoration:none;padding:6px 14px;background:rgba(255,255,255,0.08);border-radius:8px;font-size:13px">⚠️ 未报工分析</a>
  </div>
</div>
"""

    # ---- 一、团队核心指标 ----
    s1 = """
  <div class="section" id="section1">
  <div class="section-title"><span class="icon">📊</span> 一、团队核心指标对比</div>
  <div class="team-card">
"""
    for tid, td in team_ranks:
        s = td['stats']
        color = TEAM_COLORS.get(tid, '#6b7280')
        rank = rank_map[tid]
        s1 += f"""
    <div class="card" style="border-color:{color}">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-size:15px;font-weight:700;color:{color}">{td['name']}</span>
        <span class="rank-badge rank-{rank}">{rank}</span>
      </div>
      <div class="metric" style="color:{color}">{s['avg_hours']}<small style="font-size:14px">h</small></div>
      <div class="metric-label">人均工时（共{s['member_count']}人）</div>
      <div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px">
        <div>总工时 <b>{s['total_hours']}h</b></div>
        <div>满勤率 {compliance_badge(s['compliance_rate'])}</div>
        <div>加班 <b>{s['total_ot']}h</b></div>
        <div>文档 <b>{s['total_articles']}</b> 篇</div>
      </div>
    </div>"""

    s1 += """
  </div>

  <table>
    <thead><tr>
      <th>团队</th><th>人数</th><th>总工时</th><th>人均工时</th><th>满勤人数</th><th>满勤率</th>
      <th>售前</th><th>售后</th><th>内部</th><th>加班</th><th>文档</th><th>操作标准均分</th>
    </tr></thead><tbody>"""

    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        s = all_teams[tid]['stats']
        s1 += f"""
    <tr>
      <td><b>{tname}</b></td>
      <td style="text-align:center">{s['member_count']}</td>
      <td><b>{s['total_hours']}h</b></td>
      <td>{hours_badge(s['avg_hours'])}</td>
      <td style="text-align:center">{s['full_reporters']}</td>
      <td>{compliance_badge(s['compliance_rate'])}</td>
      <td>{s['total_pre']}h</td>
      <td>{s['total_after']}h</td>
      <td>{s['total_internal']}h</td>
      <td>{'<span style="color:#ef4444;font-weight:600">' if s['total_ot']>0 else ''}{s['total_ot']}h{'</span>' if s['total_ot']>0 else ''}</td>
      <td style="text-align:center">{s['total_articles']}</td>
      <td style="text-align:center">{s['avg_opScore']:.1f}</td>
    </tr>"""
    s1 += "</tbody></table></div>"

    # ---- 二、成员工时明细 ----
    s2 = """
  <div class="section" id="section2">
  <div class="section-title"><span class="icon">👤</span> 二、成员工时明细 & 每日工时</div>
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        color = TEAM_COLORS.get(tid, '#6b7280')
        summary = all_teams[tid]['summary']
        person_day = all_teams[tid]['person_day']
        members = sorted(summary.items(), key=lambda x: x[1]['totalHours'], reverse=True)

        s2 += f'<div class="sub-title" style="border-color:{color}">{tname}</div>'
        s2 += """<table style="margin-bottom:12px">
    <thead><tr><th>姓名</th><th>总工时</th>"""
        for label in date_labels:
            s2 += f"<th style='text-align:center'>{label}</th>"
        s2 += "<th>售前</th><th>售后</th><th>内部</th><th>加班</th><th>记录数</th></tr></thead><tbody>"

        for name, m in members:
            pday = person_day.get(name, {})
            th = m['totalHours']
            s2 += f"<tr><td><b>{name}</b></td><td>{hours_badge(th)}</td>"
            for d in date_strs:
                s2 += day_cell(pday.get(d, 0.0))
            s2 += f"<td>{m['preHours']:.1f}h</td><td>{m['afterHours']:.1f}h</td><td>{m['internalHours']:.1f}h</td>"
            ot = m['overHours']
            s2 += f"<td>{'<span style=color:#ef4444;font-weight:600>' if ot>0 else ''}{ot:.1f}h{'</span>' if ot>0 else ''}</td>"
            s2 += f"<td style='text-align:center'>{m['totalRecords']}</td></tr>"
        s2 += "</tbody></table>"
    s2 += "</div>"

    # ---- 三、报工不足人员 ----
    s3 = f"""
  <div class="section" id="section3">
  <div class="section-title"><span class="icon">⚠️</span> 三、报工不足人员分析</div>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px">标准：工作日 {STANDARD_DAILY}h/天，共 {work_days} 个工作日 × {STANDARD_DAILY}h = {standard_total:.0f}h；以下人员存在工时缺口</p>
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        color = TEAM_COLORS.get(tid, '#6b7280')
        sl = all_teams[tid]['shortage_list']
        if not sl:
            s3 += f'<div class="sub-title" style="border-color:{color}">{tname} <span class="good">✓ 全员达标</span></div>'
            continue
        s3 += f'<div class="sub-title" style="border-color:{color}">{tname}（{len(sl)} 人未达标）</div>'
        s3 += '<table style="margin-bottom:12px"><thead><tr><th>姓名</th><th>合计缺口</th><th>总工时</th>'
        for label in date_labels:
            s3 += f"<th style='text-align:center'>{label}</th>"
        s3 += "</tr></thead><tbody>"
        for item in sl:
            pday = item['person_day']
            s3 += f"<tr><td><b>{item['name']}</b></td>"
            s3 += f"<td><span style='color:#ef4444;font-weight:700'>{item['total_shortage']:.1f}h</span></td>"
            s3 += f"<td>{item['total_hours']:.1f}h</td>"
            for d in date_strs:
                s3 += day_cell(pday.get(d, 0.0))
            s3 += "</tr>"
        s3 += "</tbody></table>"
    s3 += "</div>"

    # ---- 四、文档统计 ----
    total_arts = sum(all_teams[tid]['stats']['total_articles'] for tid in [t['id'] for t in TEAMS])
    s4 = f"""
  <div class="section" id="section4">
  <div class="section-title"><span class="icon">📝</span> 四、文档编写统计</div>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px">本{mode_label}四团队合计发布文档 <b>{total_arts}</b> 篇</p>
  <div class="grid2">
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        color = TEAM_COLORS.get(tid, '#6b7280')
        arts = all_teams[tid]['article_authors']
        art_list = all_teams[tid]['article_list']
        s4 += f'<div>'
        s4 += f'<div class="sub-title" style="border-color:{color}">{tname}（{sum(arts.values())} 篇）</div>'
        if arts:
            for author, cnt in sorted(arts.items(), key=lambda x: -x[1]):
                titles = [a['title'] for a in art_list if a['author'] == author]
                s4 += f'<div class="article-item"><b>{author}</b> — {cnt} 篇<br>'
                for t in titles:
                    s4 += f'<span style="font-size:12px;color:#374151">• {t}</span><br>'
                s4 += '</div>'
        else:
            s4 += '<div class="shortage-item" style="background:#f9fafb;border-color:#d1d5db">本' + mode_label + '无新增文档</div>'
        s4 += '</div>'
    s4 += '</div></div>'

    # ---- 五、项目成本消耗 ----
    s5 = """
  <div class="section" id="section5">
  <div class="section-title"><span class="icon">💰</span> 五、项目成本消耗分析（工时类型分布）</div>
  <table><thead><tr><th>团队</th><th>总有效工时</th><th>售前</th><th>售后</th><th>内部</th><th>加班</th><th>售后占比</th><th>工时结构</th></tr></thead><tbody>
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        s = all_teams[tid]['stats']
        total_all = s['total_pre'] + s['total_after'] + s['total_internal']
        after_pct = round(s['total_after'] / total_all * 100, 1) if total_all > 0 else 0
        pre_pct = round(s['total_pre'] / total_all * 100, 1) if total_all > 0 else 0
        int_pct = round(s['total_internal'] / total_all * 100, 1) if total_all > 0 else 0

        bar_html = ''
        if s['total_after'] > 0:
            bar_html += f'<span class="tag tag-after">售后{after_pct}%</span>'
        if s['total_pre'] > 0:
            bar_html += f'<span class="tag tag-pre">售前{pre_pct}%</span>'
        if s['total_internal'] > 0:
            bar_html += f'<span class="tag tag-internal">内部{int_pct}%</span>'
        if s['total_ot'] > 0:
            bar_html += f'<span class="tag tag-ot">加班</span>'

        s5 += f"""<tr>
      <td><b>{tname}</b></td>
      <td><b>{total_all:.1f}h</b></td>
      <td>{s['total_pre']}h</td>
      <td>{s['total_after']}h</td>
      <td>{s['total_internal']}h</td>
      <td>{'<b style=color:#ef4444>' if s['total_ot']>0 else ''}{s['total_ot']}h{'</b>' if s['total_ot']>0 else ''}</td>
      <td>
        <div class="progress"><div class="progress-bar" style="width:{after_pct}%;background:#10b981"></div></div>
        {after_pct}%
      </td>
      <td>{bar_html}</td>
    </tr>"""
    s5 += """</tbody></table>
  <div style="margin-top:14px;padding:12px;background:#f0fdf4;border-radius:8px;font-size:13px;color:#065f46">
    <b>说明：</b>售前工时=项目投标/前期调研；售后工时=实施交付/运维支持；内部工时=内部培训/行政事务；加班工时=非工作时间产生的工时。
  </div>
</div>"""

    # ---- 六、报工质量 ----
    s6 = """
  <div class="section" id="section6">
  <div class="section-title"><span class="icon">🔍</span> 六、报工质量分析</div>
  <table><thead><tr><th>团队</th><th>报工记录数</th><th>人均记录数</th><th>操作标准均分</th><th>零记录成员</th><th>质量评价</th></tr></thead><tbody>
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        s = all_teams[tid]['stats']
        summary = all_teams[tid]['summary']
        zero_rec = [n for n, v in summary.items() if v['totalRecords'] == 0]
        avg_rec = round(s['total_records'] / s['member_count'], 1) if s['member_count'] > 0 else 0
        score = s['avg_opScore']
        if score >= 60 and not zero_rec:
            quality = '<span style="color:#065f46;font-weight:600">✓ 良好</span>'
        elif zero_rec:
            quality = f'<span style="color:#dc2626;font-weight:600">⚠ {len(zero_rec)}人未报工</span>'
        else:
            quality = '<span style="color:#92400e;font-weight:600">△ 待提升</span>'
        zero_str = '、'.join(zero_rec) if zero_rec else '无'
        s6 += f"""<tr>
      <td><b>{tname}</b></td>
      <td style="text-align:center">{s['total_records']}</td>
      <td style="text-align:center">{avg_rec}</td>
      <td style="text-align:center">{score:.1f}</td>
      <td class="{'warn' if zero_rec else 'good'}">{zero_str}</td>
      <td>{quality}</td>
    </tr>"""
    s6 += "</tbody></table></div>"

    # ---- 七、项目报工排名（各团队TOP15） ----
    s7 = """
  <div class="section" id="section7">
  <div class="section-title"><span class="icon">📊</span> 七、项目报工排名（各团队TOP15）</div>
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        color = TEAM_COLORS.get(tid, '#6b7280')
        ranking = all_teams[tid].get('project_ranking', [])
        
        s7 += f'<div class="sub-title" style="border-color:{color}">{tname}</div>'
        
        if ranking:
            s7 += '<table style="margin-bottom:16px"><thead><tr><th style="width:50px">排名</th><th>项目/客户</th><th style="text-align:right;width:100px">工时</th><th style="width:200px">占比</th></tr></thead><tbody>'
            
            total_hours = sum(h for _, h in ranking)
            max_hours = ranking[0][1] if ranking else 1
            
            for idx, (pname, phours) in enumerate(ranking[:15], 1):
                pct = round(phours / total_hours * 100, 1) if total_hours > 0 else 0
                bar_w = round(phours / max_hours * 100, 1) if max_hours > 0 else 0
                
                medal = ['🥇','🥈','🥉'][idx-1] if idx <= 3 else f'{idx}'
                
                s7 += f'<tr>'
                s7 += f'<td style="text-align:center">{medal}</td>'
                s7 += f'<td><b>{pname[:60]}</b></td>'
                s7 += f'<td style="text-align:right;font-weight:600">{phours:.1f}h</td>'
                s7 += f'<td><div class="progress"><div class="progress-bar" style="width:{bar_w}%;background:{color}"></div></div> {pct}%</td>'
                s7 += '</tr>'
            
            s7 += '</tbody></table>'
        else:
            s7 += '<div style="padding:12px;color:#9ca3af;font-size:13px">本期无项目报工记录</div>'
    
    s7 += "</div>"

    # ---- 八、每人每天报工内容明细 & 工作总结 ----
    s8 = """
  <div class="section" id="section8">
  <div class="section-title"><span class="icon">📋</span> 八、每人每周工作总结</div>
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        color = TEAM_COLORS.get(tid, '#6b7280')
        summary = all_teams[tid]['summary']
        daily_work = all_teams[tid].get('daily_work', {})
        members = sorted(summary.items(), key=lambda x: x[1]['totalHours'], reverse=True)
        
        s8 += f'<div class="sub-title" style="border-color:{color}">{tname}</div>'
        
        for name, m in members:
            person_daily = daily_work.get(name, {})
            if not person_daily:
                continue
            
            # 收集所有有效记录
            all_items = []
            for day_items in person_daily.values():
                for item in day_items:
                    if item.get('remark', '').strip():
                        all_items.append(item)
            
            if not all_items:
                continue
            
            total_hours = m['totalHours']
            work_days = len(person_daily)
            daily_avg = total_hours / work_days if work_days else 0
            
            # 判断报工质量
            if total_hours < standard_total * 0.6:
                quality_level = 'poor'
                quality_label = '报工不足'
                quality_color = '#dc2626'
                quality_bg = '#fee2e2'
            elif total_hours < standard_total * 0.8:
                quality_level = 'warning'
                quality_label = '需改善'
                quality_color = '#f59e0b'
                quality_bg = '#fef3c7'
            else:
                quality_level = 'good'
                quality_label = '达标'
                quality_color = '#10b981'
                quality_bg = '#d1fae5'
            
            # 生成智能总结
            summary_html = generate_person_summary(name, all_items, person_daily, m, work_days, standard_total)
            
            s8 += f'<div style="margin:12px 0;padding:14px;background:#f8fafc;border-radius:8px;border-left:3px solid {color}">'
            s8 += f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
            s8 += f'<div style="font-size:14px;font-weight:600;color:{color}">{name}</div>'
            s8 += f'<div style="display:flex;gap:8px;align-items:center">'
            s8 += f'<span style="font-size:12px;color:#6b7280">{work_days}天 / {total_hours:.1f}h / 日均{daily_avg:.1f}h</span>'
            s8 += f'<span style="background:{quality_bg};color:{quality_color};padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600">{quality_label}</span>'
            s8 += f'</div></div>'

            # 🆕 姓名后置「合同名／实施计划」标签（accId 精确关联合同，按工时降序去重）
            # 注意：本函数后半段有局部 `from collections import Counter`，
            # 会把 Counter 变成函数局部变量，此处不可用，改用普通 dict 累加。
            proj_counter = {}
            proj_meta = {}  # accName -> (accId, companyName) 取工时最大记录
            for _day_items in person_daily.values():
                for _it in _day_items:
                    _acc = (_it.get('accName') or '').strip()
                    if _acc:
                        _h = _it.get('hours', 0) or 0
                        proj_counter[_acc] = proj_counter.get(_acc, 0) + _h
                        _prev = proj_meta.get(_acc)
                        if _prev is None or _h > _prev[2]:
                            proj_meta[_acc] = (str(_it.get('accId') or ''),
                                               (_it.get('companyName') or '').strip(), _h)
            top_projects = sorted(proj_counter.items(), key=lambda x: -x[1])[:8]
            if top_projects:
                pc_tags = ''.join(
                    pc_tag_html(p, proj_meta.get(p, ('', ''))[:2]) for p, _ in top_projects)
                s8 += (f'<div style="font-size:12px;margin:0 0 10px;padding:6px 10px;background:#eef2ff;'
                       f'border-left:3px solid #6366f1;border-radius:6px">'
                       f'<span style="color:#4338ca;font-weight:600;margin-right:4px">支持项目/合同：</span>{pc_tags}</div>')
            else:
                s8 += ('<div style="font-size:12px;margin:0 0 10px;padding:6px 10px;background:#eef2ff;'
                       f'border-left:3px solid #6366f1;border-radius:6px">'
                       f'<span style="color:#4338ca;font-weight:600;margin-right:4px">支持项目/合同：</span>'
                       f'<span style="color:#9ca3af;font-style:italic">本期报工无关联项目</span></div>')

            s8 += summary_html
            s8 += '</div>'
    
    s8 += "</div>"

    # ---- 九、服务请求列表 ----
    s9 = """
  <div class="section" id="section9">
  <div class="section-title"><span class="icon">🎫</span> 九、服务请求列表</div>
"""
    # 从第一个团队获取全局服务请求
    first_tid = TEAMS[0]['id']
    sr_list = all_teams[first_tid].get('service_requests', [])
    
    if sr_list:
        # 级别颜色映射
        level_colors = {
            'P0': ('#dc2626', '#fee2e2'),
            'P1': ('#ef4444', '#fee2e2'),
            'P2': ('#f59e0b', '#fef3c7'),
            'P3': ('#3b82f6', '#dbeafe'),
            'P4': ('#10b981', '#d1fae5'),
            'P5': ('#6b7280', '#f3f4f6'),
        }
        
        # ---- 9.1 统计摘要：按客户排名 + 按处理人排名 ----
        from collections import Counter
        company_counter = Counter()
        handler_counter = Counter()
        level_counter = Counter()
        
        for sr in sr_list:
            company = sr.get('company', '') or '未知客户'
            handler = sr.get('handler', '') or '未分配'
            level = sr.get('level', '') or '-'
            company_counter[company] += 1
            if handler and handler != '未分配':
                handler_counter[handler] += 1
            level_counter[level] += 1
        
        company_top = company_counter.most_common(10)
        handler_top = handler_counter.most_common(10)
        
        s9 += f'<p style="font-size:13px;color:#6b7280;margin-bottom:16px">本期东西大区共 <b>{len(sr_list)}</b> 个服务请求</p>'
        
        # 排名分析区域（两列布局）
        s9 += '<div style="display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap">'
        
        # 按客户排名
        s9 += '<div style="flex:1;min-width:280px;background:#f8fafc;border-radius:10px;padding:16px;border:1px solid #e2e8f0">'
        s9 += '<div style="font-size:14px;font-weight:700;color:#1e40af;margin-bottom:12px">📊 按客户排名（服务请求数）</div>'
        max_company_cnt = company_top[0][1] if company_top else 1
        for i, (comp, cnt) in enumerate(company_top, 1):
            bar_width = int(cnt / max_company_cnt * 100)
            rank_icon = ['🥇','🥈','🥉'][i-1] if i <= 3 else f'{i}.'
            s9 += f'<div style="margin:6px 0">'
            s9 += f'<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px">'
            s9 += f'<span><b>{rank_icon}</b> {comp}</span>'
            s9 += f'<span style="color:#1e40af;font-weight:600">{cnt} 单</span>'
            s9 += f'</div>'
            s9 += f'<div style="height:6px;background:#e2e8f0;border-radius:3px">'
            s9 += f'<div style="height:6px;width:{bar_width}%;background:#3b82f6;border-radius:3px"></div>'
            s9 += f'</div></div>'
        s9 += '</div>'
        
        # 按处理人排名
        s9 += '<div style="flex:1;min-width:280px;background:#f8fafc;border-radius:10px;padding:16px;border:1px solid #e2e8f0">'
        s9 += '<div style="font-size:14px;font-weight:700;color:#065f46;margin-bottom:12px">👤 按处理人排名（服务请求数）</div>'
        max_handler_cnt = handler_top[0][1] if handler_top else 1
        for i, (handler, cnt) in enumerate(handler_top, 1):
            bar_width = int(cnt / max_handler_cnt * 100)
            rank_icon = ['🥇','🥈','🥉'][i-1] if i <= 3 else f'{i}.'
            s9 += f'<div style="margin:6px 0">'
            s9 += f'<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px">'
            s9 += f'<span><b>{rank_icon}</b> {handler}</span>'
            s9 += f'<span style="color:#065f46;font-weight:600">{cnt} 单</span>'
            s9 += f'</div>'
            s9 += f'<div style="height:6px;background:#e2e8f0;border-radius:3px">'
            s9 += f'<div style="height:6px;width:{bar_width}%;background:#10b981;border-radius:3px"></div>'
            s9 += f'</div></div>'
        s9 += '</div>'
        
        s9 += '</div>'  # end flex row
        
        # 级别分布统计条
        if level_counter:
            s9 += '<div style="background:#fafafa;border-radius:8px;padding:12px 16px;margin-bottom:16px;border:1px solid #e2e8f0">'
            s9 += '<span style="font-size:13px;font-weight:600;color:#374151">服务等级分布：</span> '
            for lvl in ['P0','P1','P2','P3','P4','P5']:
                cnt = level_counter.get(lvl, 0)
                if cnt:
                    lc, lb = level_colors.get(lvl, ('#6b7280', '#f3f4f6'))
                    s9 += f'<span style="display:inline-block;margin:2px 4px;background:{lb};color:{lc};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600">{lvl} × {cnt}</span>'
            other_cnt = sum(v for k, v in level_counter.items() if k not in level_colors)
            if other_cnt:
                s9 += f'<span style="display:inline-block;margin:2px 4px;background:#f3f4f6;color:#6b7280;padding:3px 10px;border-radius:12px;font-size:12px">其他 × {other_cnt}</span>'
            s9 += '</div>'
        
        # ---- 9.2 明细列表 ----
        s9 += '<table><thead><tr><th>ID</th><th>级别</th><th>状态</th><th>标题</th><th>客户</th><th>提交人</th><th>处理人</th><th>提交时间</th><th>所属团队</th></tr></thead><tbody>'
        
        # 按级别优先（P0最高）再按提交时间排序
        level_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4, 'P5': 5, '-': 9}
        sr_list.sort(key=lambda x: (level_order.get(x.get('level', '-'), 9), x.get('submitTime', '')), reverse=False)
        sr_list.sort(key=lambda x: x.get('submitTime', ''), reverse=True)
        
        for sr in sr_list:
            status = sr.get('status', '未知')
            level = sr.get('level', '') or '-'
            type_label = sr.get('type_label', '') or level
            
            level_color, level_bg = level_colors.get(level, ('#6b7280', '#f3f4f6'))
            
            # 状态颜色
            status_color = '#065f46' if '关闭' in status or '归档' in status else ('#92400e' if '处理' in status or '待反馈' in status else '#6b7280')
            status_bg = '#d1fae5' if '关闭' in status or '归档' in status else ('#fef3c7' if '处理' in status or '待反馈' in status else '#f3f4f6')
            
            s9 += f'<tr>'
            s9 += f'<td style="font-size:12px;color:#6b7280">#{sr.get("id", "")}</td>'
            s9 += f'<td><span style="background:{level_bg};color:{level_color};padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600" title="{type_label}">{level}</span></td>'
            s9 += f'<td><span style="background:{status_bg};color:{status_color};padding:2px 8px;border-radius:10px;font-size:12px">{status}</span></td>'
            s9 += f'<td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{sr.get("title", "")}">{sr.get("title", "")[:60]}</td>'
            s9 += f'<td>{sr.get("company", "")}</td>'
            s9 += f'<td>{sr.get("submitter", "")}</td>'
            s9 += f'<td>{sr.get("handler", "")}</td>'
            s9 += f'<td style="font-size:12px;color:#6b7280">{sr.get("submitTime", "")[:16]}</td>'
            s9 += f'<td style="font-size:12px">{sr.get("team", "")}</td>'
            s9 += '</tr>'
        
        s9 += '</tbody></table>'
    else:
        s9 += '<div style="padding:20px;text-align:center;color:#9ca3af">本期东西大区无服务请求记录</div>'
    
    s9 += "</div>"

    # ---- 十、综合评价 ----
    s10 = """
  <div class="section" id="section10">
  <div class="section-title"><span class="icon">🏆</span> 十、综合评价</div>
"""
    rank_labels = ['🥇', '🥈', '🥉', '4️⃣']
    for rank, (tid, td) in enumerate(team_ranks, 1):
        s = td['stats']
        color = TEAM_COLORS.get(tid, '#6b7280')
        medal = rank_labels[rank - 1] if rank <= 4 else f'#{rank}'
        shortage_cnt = len(td['shortage_list'])

        if rank == 1:
            comment = f"人均工时最高（{s['avg_hours']}h），报工积极性强；文档产出 {s['total_articles']} 篇，知识沉淀领先。"
        elif rank == 2:
            comment = f"人均工时 {s['avg_hours']}h，满勤率 {s['compliance_rate']}%；加班 {s['total_ot']}h，投入度高，文档 {s['total_articles']} 篇。"
        elif rank == 3:
            comment = f"人均工时 {s['avg_hours']}h，满勤率 {s['compliance_rate']}%；加班 {s['total_ot']}h；{shortage_cnt} 人存在工时缺口，需督促。"
        else:
            comment = f"人均工时 {s['avg_hours']}h，整体工时偏低，{shortage_cnt} 人未达标准工时，建议加强报工管理。"

        s10 += f"""
    <div style="display:flex;align-items:flex-start;gap:16px;padding:14px;background:#f8fafc;border-radius:10px;margin-bottom:10px;border-left:4px solid {color}">
      <div style="font-size:32px;line-height:1">{medal}</div>
      <div style="flex:1">
        <div style="font-size:16px;font-weight:700;color:{color};margin-bottom:6px">{td['name']}</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px">
          <span style="font-size:13px">人数 <b>{s['member_count']}</b></span>
          <span style="font-size:13px">总工时 <b>{s['total_hours']}h</b></span>
          <span style="font-size:13px">人均 <b>{s['avg_hours']}h</b></span>
          <span style="font-size:13px">满勤率 {compliance_badge(s['compliance_rate'])}</span>
          <span style="font-size:13px">加班 <b>{s['total_ot']}h</b></span>
          <span style="font-size:13px">文档 <b>{s['total_articles']}</b>篇</span>
          <span style="font-size:13px">缺工时人员 <b style="color:#ef4444">{shortage_cnt}</b>人</span>
        </div>
        <div style="font-size:13px;color:#6b7280">{comment}</div>
      </div>
    </div>"""

    s10 += f"""
  <div style="margin-top:16px;padding:16px;background:#eff6ff;border-radius:10px;font-size:13px;line-height:1.8">
    <b style="color:#1d4ed8">📌 管理建议：</b><br>
    1. 本{mode_label}整体满勤率偏低，建议统一在截止日前完成报工填写。<br>
    2. 各团队均无月度质量评分（dashboard score 未生成），建议跟进打分流程。<br>
    3. 零文档产出的团队建议加强知识库建设要求，推动经验沉淀。<br>
    4. 操作标准分各团队差异较大，建议对零分或低分成员进行辅导，提升报工规范性。
  </div>
</div>"""

    # ---- 十一、项目未报工分析 ----
    s11 = """
  <div class="section" id="section11">
  <div class="section-title"><span class="icon">⚠️</span> 十一、项目未报工分析</div>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px">东西大区维保项目支持团队下，合同未结束但子项未产生报工的项目清单</p>
"""
    
    # 读取未报工数据（v2 格式，包含已报工子项信息）
    import os
    no_work_file = '/tmp/mes_no_work_items_v2.json'
    if os.path.exists(no_work_file):
        with open(no_work_file, 'r', encoding='utf-8') as f:
            no_work_data = json.load(f)
        
        if no_work_data:
            # 统计摘要
            total_contracts = len(no_work_data)
            total_no_work_items = sum(len(d['no_work_items']) for d in no_work_data)
            total_has_work_items = sum(len(d['has_work_items']) for d in no_work_data)
            total_remaining = sum(
                sum(i.get('remaining_task', 0) or 0 for i in d['no_work_items'])
                for d in no_work_data
            )
            
            s11 += f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px">'
            s11 += f'<div style="background:#fef2f2;padding:12px;border-radius:8px;text-align:center"><div style="font-size:24px;font-weight:700;color:#dc2626">{total_contracts}</div><div style="font-size:12px;color:#6b7280">有未报工子项的合同</div></div>'
            s11 += f'<div style="background:#fef2f2;padding:12px;border-radius:8px;text-align:center"><div style="font-size:24px;font-weight:700;color:#dc2626">{total_no_work_items}</div><div style="font-size:12px;color:#6b7280">未报工子项</div></div>'
            if total_has_work_items > 0:
                s11 += f'<div style="background:#f0fdf4;padding:12px;border-radius:8px;text-align:center"><div style="font-size:24px;font-weight:700;color:#16a34a">{total_has_work_items}</div><div style="font-size:12px;color:#6b7280">已报工子项（合同在交付）</div></div>'
            s11 += f'<div style="background:#fef2f2;padding:12px;border-radius:8px;text-align:center"><div style="font-size:24px;font-weight:700;color:#dc2626">{total_remaining:,}h</div><div style="font-size:12px;color:#6b7280">未报工剩余工时</div></div>'
            s11 += '</div>'
            
            # 按合同展示（按未报工子项数降序）
            sorted_contracts = sorted(no_work_data, 
                                     key=lambda x: len(x['no_work_items']), 
                                     reverse=True)
            
            for contract_data in sorted_contracts:
                contract = contract_data['contract']
                no_work_items = contract_data['no_work_items']
                has_work_items = contract_data['has_work_items']
                
                contract_name = contract['contract_name']
                manager = contract.get('manager', '未指定')
                start_time = contract.get('start_time', '')
                end_time = contract.get('end_time', '')
                contract_remaining = sum(i.get('remaining_task', 0) or 0 for i in no_work_items)
                contract_plan = sum(i.get('plan_hour', 0) or 0 for i in no_work_items)
                
                s11 += f'<div style="margin:12px 0;background:#f8fafc;border-radius:10px;border:1px solid #e2e8f0;overflow:hidden">'
                s11 += f'<div style="background:#f1f5f9;padding:12px 16px;border-bottom:1px solid #e2e8f0">'
                s11 += f'<div style="font-size:14px;font-weight:600;color:#1e293b;margin-bottom:6px">📄 {contract_name}</div>'
                s11 += f'<div style="display:flex;gap:16px;font-size:12px;color:#64748b;flex-wrap:wrap">'
                s11 += f'<span>👤 {manager}</span>'
                s11 += f'<span>📅 {start_time[:10]} ~ {end_time[:10]}</span>'
                s11 += f'<span>⏱️ 未报工计划 <b style="color:#1e40af">{contract_plan}h</b></span>'
                s11 += f'<span>⚠️ 剩余 <b style="color:#dc2626">{contract_remaining}h</b></span>'
                s11 += f'<span>📋 未报工子项 <b style="color:#dc2626">{len(no_work_items)}个</b></span>'
                if has_work_items:
                    s11 += f'<span>✅ 已报工子项 <b style="color:#16a34a">{len(has_work_items)}个</b></span>'
                s11 += f'</div>'
                
                # 如果有已报工子项，显示提示
                if has_work_items:
                    s11 += f'<div style="margin-top:8px;padding:6px 10px;background:#f0fdf4;border-radius:6px;font-size:11px;color:#15803d">'
                    s11 += f'💡 <b>合同在交付中</b>，以下子项已有报工：'
                    s11 += f'{"、".join(item["item_name"] for item in has_work_items)}'
                    s11 += f'</div>'
                
                s11 += f'</div>'
                
                # 未报工子项表格
                s11 += '<table style="width:100%;border-collapse:collapse;font-size:12px">'
                s11 += '<thead><tr style="background:#f8fafc">'
                s11 += '<th style="padding:8px 12px;text-align:left;border-bottom:1px solid #e2e8f0;color:#475569">子项名称</th>'
                s11 += '<th style="padding:8px 12px;text-align:left;border-bottom:1px solid #e2e8f0;color:#475569;width:120px">类型</th>'
                s11 += '<th style="padding:8px 12px;text-align:center;border-bottom:1px solid #e2e8f0;color:#475569;width:80px">计划工时</th>'
                s11 += '<th style="padding:8px 12px;text-align:center;border-bottom:1px solid #e2e8f0;color:#475569;width:80px">实际工时</th>'
                s11 += '<th style="padding:8px 12px;text-align:center;border-bottom:1px solid #e2e8f0;color:#475569;width:100px">剩余工时</th>'
                s11 += '</tr></thead><tbody>'
                
                for item in no_work_items:
                    item_name = item.get('item_name', '')
                    item_type = item.get('item_type', '')
                    plan = item.get('plan_hour', 0) or 0
                    actual = item.get('actual_hours', 0) or 0
                    remaining = item.get('remaining_task', 0) or 0
                    
                    bar_width = int(remaining / plan * 100) if plan > 0 else 0
                    
                    s11 += f'<tr style="border-bottom:1px solid #f1f5f9">'
                    s11 += f'<td style="padding:8px 12px"><b>{item_name}</b></td>'
                    s11 += f'<td style="padding:8px 12px"><span style="background:#fef3c7;color:#d97706;padding:2px 8px;border-radius:10px;font-size:11px">{item_type}</span></td>'
                    s11 += f'<td style="padding:8px 12px;text-align:center">{plan}h</td>'
                    s11 += f'<td style="padding:8px 12px;text-align:center"><span style="background:#fee2e2;color:#dc2626;padding:2px 8px;border-radius:10px;font-size:11px">{actual}h</span></td>'
                    s11 += f'<td style="padding:8px 12px;text-align:center">{remaining}h<div style="height:4px;background:#e2e8f0;border-radius:2px;margin-top:3px"><div style="height:4px;width:{bar_width}%;background:#ef4444;border-radius:2px"></div></div></td>'
                    s11 += '</tr>'
                
                s11 += '</tbody></table></div>'
        else:
            s11 += '<div style="padding:20px;text-align:center;color:#9ca3af">本期无未报工合同子项</div>'
    else:
        s11 += '<div style="padding:20px;text-align:center;color:#9ca3af">未报工数据文件不存在，请确认已执行 Step 2.5 查询</div>'
    
    s11 += "</div>"

    # ---- 页脚 ----
    footer = f"""
<div style="text-align:center;font-size:12px;color:#9ca3af;padding:20px">
  本报告由自动化任务生成 · {report_time} · 东西大区{mode_label}报工分析系统
</div>
"""

    # ---- 拼接完整 HTML ----
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>东西大区四团队报工分析 {meta['date_start']}~{meta['date_end']}</title>
<style>{css}</style>
</head>
<body>
<div class="container">
{header}
{s1}
{s2}
{s3}
{s4}
{s5}
{s6}
{s7}
{s8}
{s9}
{s10}
{s11}
{footer}
</div>
</body>
</html>"""

    return html


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成东西大区报工分析 HTML 报告')
    parser.add_argument('--input', default='/tmp/mes_analysis_result.json', help='分析结果 JSON 文件路径')
    parser.add_argument('--output', required=True, help='输出的 HTML 文件路径')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html = generate_report(data)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML 报告已生成：{args.output}（{len(html)} 字符）")
