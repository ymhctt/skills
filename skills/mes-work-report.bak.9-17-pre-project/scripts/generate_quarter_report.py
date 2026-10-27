#!/usr/bin/env python3
"""
东西大区四团队报工分析 - 季度/长周期 HTML 报告生成器
用法：python3 generate_quarter_report.py --input /tmp/mes_analysis_q1.json --output report.html
特点：支持长周期（季度），每日明细按月聚合显示
"""

import json
import argparse
import os
import sys
from collections import defaultdict
from datetime import date

# 🆕 合同名解析：报工 accId == 合同子项 itemId，精确关联「实施计划 → 合同」
# 缓存由 build_contract_item_map.py 构建（/tmp/mes_item_contract_map.json），无缓存时降级为仅显示实施计划名
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from build_contract_item_map import load_map as _load_cmap, resolve_contract as _resolve_contract
    _CONTRACT_MAP = _load_cmap()
except Exception:
    _CONTRACT_MAP = None


def _truncate(s, n):
    s = (s or '').strip()
    return s if len(s) <= n else s[:n - 1] + '…'


def pc_tag_html(acc_name, hours, acc_meta):
    """生成「合同名／实施计划」标签；无合同映射时降级为仅实施计划名"""
    contract = ''
    if _CONTRACT_MAP and acc_meta:
        acc_id, company = acc_meta[0], acc_meta[1]
        try:
            contract, _num, ok = _resolve_contract(_CONTRACT_MAP, acc_id, acc_name, company)
        except Exception:
            contract, ok = '', False
    full = f"{contract}／{acc_name}" if contract else acc_name
    if contract:
        if contract in acc_name or acc_name in contract:
            # 合同名与实施计划名互为包含时只显示更长者，避免标签冗余
            txt = f"<b>{_truncate(max(contract, acc_name, key=len), 34)}</b>"
        else:
            txt = f"<b>{_truncate(contract, 26)}</b><span class='pc-sub'>／{_truncate(acc_name, 18)}</span>"
    else:
        txt = _truncate(acc_name, 30)
    return f"<span class='pc-tag' title='{full}'>{txt}</span>"

STANDARD_DAILY = 8.0
TEAM_COLORS = {'t2': '#3b82f6', 't3': '#10b981', 't23': '#f59e0b', 't19': '#ef4444'}
DEFAULT_TEAMS = [
    {'id': 't2',  'name': '东西大区1部'},
    {'id': 't3',  'name': '东西大区2部'},
    {'id': 't23', 'name': '东西大区4部'},
    {'id': 't19', 'name': '东西大区5部'},
]

def compliance_badge(rate):
    if rate >= 80: color, bg = '#065f46', '#d1fae5'
    elif rate >= 50: color, bg = '#92400e', '#fef3c7'
    else: color, bg = '#991b1b', '#fee2e2'
    return f'<span style="background:{bg};color:{color};padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{rate:.1f}%</span>'

def hours_badge(h, std=None):
    if std and h >= std: color, bg = '#065f46', '#d1fae5'
    elif h >= std * 0.8 if std else h >= 400: color, bg = '#92400e', '#fef3c7'
    else: color, bg = '#991b1b', '#fee2e2'
    return f'<span style="background:{bg};color:{color};padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{h:.1f}h</span>'

def month_cell(h, month_std):
    """月度工时单元格"""
    ratio = h / month_std if month_std > 0 else 0
    if ratio >= 0.95: bg, color = '#bbf7d0', '#065f46'
    elif ratio >= 0.80: bg, color = '#fef08a', '#713f12'
    elif ratio > 0: bg, color = '#fecaca', '#7f1d1d'
    else: bg, color = '#f3f4f6', '#9ca3af'
    return f'<td style="text-align:center;background:{bg};color:{color};font-weight:600;font-size:13px;padding:6px 4px">{h:.1f}</td>'

def fmt_date_label(d_str):
    dt = date.fromisoformat(d_str)
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return f'{d_str[5:]}({weekdays[dt.weekday()]})'

def get_month_groups(date_strs):
    """将日期列表按月分组，返回 {月份名: [日期str列表]}"""
    groups = defaultdict(list)
    month_names = {'01': '1月', '02': '2月', '03': '3月', '04': '4月', '05': '5月', '06': '6月',
                   '07': '7月', '08': '8月', '09': '9月', '10': '10月', '11': '11月', '12': '12月'}
    for d in date_strs:
        m = d[5:7]
        groups[month_names[m]].append(d)
    # 按月份排序
    sorted_groups = []
    for i in range(1, 13):
        key = f'{i}月'
        if key in groups:
            sorted_groups.append((key, groups[key]))
    return sorted_groups

def calc_project_ranking(data, teams_config, tmpdir='/tmp'):
    """从 list 数据中提取项目报工排名（需要原始数据，此处从 person_day 无法获取项目名）"""
    # 从原始 list JSON 中提取
    project_hours = defaultdict(lambda: defaultdict(float))
    project_records = defaultdict(lambda: defaultdict(int))
    
    # 从 meta 中动态获取排除人员
    excluded = set(data.get('meta', {}).get('excluded', []))
    
    for team in teams_config:
        tid = team['id']
        try:
            with open(f'{tmpdir}/mes_list_{tid}.json', 'r') as f:
                list_raw = json.load(f)
        except:
            continue
        
        items = list_raw.get('list', [])
        for item in items:
            name = item.get('executorName', '') or ''
            if not name or name in excluded:
                continue
            acc_name = item.get('accName', '') or item.get('remark', '') or '未分类'
            hours = item.get('taskTime', 0) or 0
            project_hours[team['name']][acc_name] += hours
            project_records[team['name']][acc_name] += 1
    
    return dict(project_hours), dict(project_records)

def generate_report(data):
    meta = data['meta']
    teams_config = data.get('teams_config', DEFAULT_TEAMS)
    all_teams = data['teams']
    
    date_strs = meta['date_strs']
    mode_label = '季度' if meta.get('mode') == 'quarter' else ('月度' if meta['mode'] == 'month' else '周')
    standard_total = meta['standard_total']
    work_days = meta['work_days']
    report_time = meta['report_time']
    
    # 计算综合排名
    team_ranks = sorted(all_teams.items(),
        key=lambda x: (x[1]['stats']['compliance_rate'], x[1]['stats']['avg_hours']), reverse=True)
    rank_map = {tid: i+1 for i, (tid, _) in enumerate(team_ranks)}
    
    # 月度分组
    month_groups = get_month_groups(date_strs)
    # 每月标准工时
    month_standards = {name: len(dates) * STANDARD_DAILY for name, dates in month_groups}
    
    # 项目报工排名
    project_hours, project_records = calc_project_ranking(data, teams_config)
    
    TEAMS = teams_config
    
    # ---- CSS ----
    css = """
  * {box-sizing:border-box;margin:0;padding:0;}
  body {font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f4f8;color:#1f2937;}
  .container {max-width:1400px;margin:0 auto;padding:20px;}
  .header {background:linear-gradient(135deg,#1e3a5f 0%,#7c3aed 50%,#2563eb 100%);color:white;padding:36px;border-radius:16px;margin-bottom:24px;}
  .header h1 {font-size:26px;font-weight:700;margin-bottom:10px;}
  .header p {font-size:14px;opacity:0.9;line-height:1.6;}
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
  .project-row:nth-child(even) {background:#f8fafc;}
  .project-row td {font-size:13px;}
  .project-bar {display:inline-block;height:8px;border-radius:4px;vertical-align:middle;margin-right:6px;}
  .quality-row:hover td {background:#eff6ff !important;}
  .score-high {color:#065f46;font-weight:700;} .score-mid {color:#92400e;font-weight:600;} .score-low {color:#991b1b;font-weight:700;}
  .person-card {background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;padding:18px;margin-bottom:14px;}
  .person-card h4 {font-size:15px;color:#1e3a5f;margin-bottom:10px;}
  .person-stats {display:flex;flex-wrap:wrap;gap:10px;margin-bottom:10px;}
  .person-stat {font-size:12px;background:#e5e7eb;padding:3px 10px;border-radius:12px;}
  .monthly-bars {display:flex;gap:10px;margin-bottom:10px;}
  .month-col {flex:1;background:#f3f4f6;border-radius:8px;padding:8px 10px;text-align:center;}
  .month-col .m-label {font-size:11px;color:#6b7280;} .month-col .m-val {font-size:14px;font-weight:700;color:#1e3a5f;}
  .month-col .m-bar {height:5px;border-radius:3px;margin-top:4px;background:#d1d5db;}
  .month-col .m-bar-fill {height:100%;border-radius:3px;}
  .work-list {font-size:12px;color:#374151;padding-left:16px;}
  .work-list li {margin-bottom:3px;line-height:1.5;}
  .proj-tags {font-size:12px;margin-bottom:8px;}
  .proj-tag {display:inline-block;background:#dbeafe;color:#1d4ed8;padding:2px 8px;border-radius:10px;font-size:11px;margin:2px;}
  /* 🆕 每人姓名后置「支持项目/合同」标签 */
  .person-contracts {font-size:12px;margin:0 0 10px;padding:6px 10px;background:#eef2ff;border-left:3px solid #6366f1;border-radius:6px;}
  .pc-label {color:#4338ca;font-weight:600;margin-right:4px;}
  .pc-tag {display:inline-block;background:#e0e7ff;color:#3730a3;padding:2px 9px;border-radius:10px;font-size:11px;margin:2px 3px 2px 0;font-weight:500;}
  .pc-tag b {font-weight:700;}
  .pc-sub {color:#6366f1;font-weight:400;margin-left:2px;}
  .pc-empty {color:#9ca3af;font-style:italic;}
  .viz-bar-row {display:flex;align-items:center;gap:8px;margin-bottom:5px;}
  .viz-bar-name {width:200px;font-size:12px;text-align:right;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .viz-bar-track {flex:1;height:18px;background:#e5e7eb;border-radius:9px;overflow:hidden;}
  .viz-bar-fill {height:100%;border-radius:9px;display:flex;align-items:center;padding-left:8px;font-size:11px;color:#fff;font-weight:600;min-width:fit-content;}
  .viz-bar-val {width:70px;font-size:12px;text-align:right;flex-shrink:0;color:#374151;}
"""
    
    # ---- Header ----
    header = f"""
<div class="header">
  <h1>🏢 东西大区四团队 · {meta['date_start']}~{meta['date_end']} 报工综合分析报告</h1>
  <p>统计周期：{meta['date_start']} — {meta['date_end']}（共 <b>{work_days}</b> 个工作日）</p>
  <p>标准工时：{standard_total:.0f}h/人（工作日 {STANDARD_DAILY}h/天） &nbsp;&nbsp;|&nbsp;&nbsp; 周六周日工时视为加班</p>
</div>"""
    
    # ---- 汇总卡片 ----
    total_members = sum(all_teams[tid]['stats']['member_count'] for tid in [t['id'] for t in TEAMS])
    total_hours_all = sum(all_teams[tid]['stats']['total_hours'] for tid in [t['id'] for t in TEAMS])
    total_articles_all = sum(all_teams[tid]['stats']['total_articles'] for tid in [t['id'] for t in TEAMS])
    total_ot_all = sum(all_teams[tid]['stats']['total_ot'] for tid in [t['id'] for t in TEAMS])
    total_full = sum(all_teams[tid]['stats']['full_reporters'] for tid in [t['id'] for t in TEAMS])
    overall_avg = round(total_hours_all / total_members, 1) if total_members > 0 else 0
    overall_compliance = round(total_full / total_members * 100, 1) if total_members > 0 else 0
    
    summary_cards = f"""
<div class="section" style="padding:16px 24px;">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;text-align:center;">
    <div class="card" style="border-color:#3b82f6">
      <div class="metric" style="color:#3b82f6;font-size:22px">{total_members}</div>
      <div class="metric-label">总人数</div>
    </div>
    <div class="card" style="border-color:#10b981">
      <div class="metric" style="color:#10b981;font-size:22px">{total_hours_all:,}h</div>
      <div class="metric-label">总工时</div>
    </div>
    <div class="card" style="border-color:#f59e0b">
      <div class="metric" style="color:#f59e0b;font-size:22px">{overall_avg}h</div>
      <div class="metric-label">人均工时（标准{standard_total:.0f}h）</div>
    </div>
    <div class="card" style="border-color:#8b5cf6">
      <div class="metric" style="color:#8b5cf6;font-size:22px">{total_full}/{total_members}</div>
      <div class="metric-label">满勤人数（{overall_compliance}%）</div>
    </div>
    <div class="card" style="border-color:#ef4444">
      <div class="metric" style="color:#ef4444;font-size:22px">{total_ot_all}h</div>
      <div class="metric-label">加班工时</div>
    </div>
    <div class="card" style="border-color:#06b6d4">
      <div class="metric" style="color:#06b6d4;font-size:22px">{total_articles_all}</div>
      <div class="metric-label">文档数量</div>
    </div>
  </div>
</div>"""
    
    # ---- 一、团队核心指标对比 ----
    s1 = """
<div class="section">
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
      <div class="metric-label">人均工时（共{s['member_count']}人，标准{standard_total:.0f}h）</div>
      <div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px">
        <div>总工时 <b>{s['total_hours']:,}h</b></div>
        <div>满勤率 {compliance_badge(s['compliance_rate'])}</div>
        <div>加班 <b>{s['total_ot']}h</b></div>
        <div>文档 <b>{s['total_articles']}</b> 篇</div>
      </div>
    </div>"""
    
    s1 += """
  </div>
  <table>
    <thead><tr>
      <th>排名</th><th>团队</th><th>人数</th><th>总工时</th><th>人均工时</th><th>满勤人数</th><th>满勤率</th>
      <th>售前</th><th>售后</th><th>内部</th><th>加班</th><th>文档</th><th>操作标准均分</th>
    </tr></thead><tbody>"""
    
    for rank, (tid, td) in enumerate(team_ranks, 1):
        team = next(t for t in TEAMS if t['id'] == tid)
        s = all_teams[tid]['stats']
        medal = ['🥇','🥈','🥉','4️⃣'][rank-1] if rank <= 4 else f'#{rank}'
        s1 += f"""
    <tr>
      <td style="text-align:center;font-size:18px">{medal}</td>
      <td><b>{team['name']}</b></td>
      <td style="text-align:center">{s['member_count']}</td>
      <td><b>{s['total_hours']:,}h</b></td>
      <td>{hours_badge(s['avg_hours'], standard_total)}</td>
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
    
    # ---- 二、成员工时明细（按月聚合） ----
    s2 = """
<div class="section">
  <div class="section-title"><span class="icon">👤</span> 二、成员工时明细（按月汇总）</div>
  <p style="font-size:12px;color:#6b7280;margin-bottom:12px">热力色：🟢 ≥标准80%  🟡 ≥标准60%  🔴 &lt;标准60%  ⚪ 无记录</p>
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        color = TEAM_COLORS.get(tid, '#6b7280')
        summary = all_teams[tid]['summary']
        person_day = all_teams[tid]['person_day']
        members = sorted(summary.items(), key=lambda x: x[1]['totalHours'], reverse=True)
        
        s2 += f'<div class="sub-title" style="border-color:{color}">{tname}（{len(members)}人）</div>'
        s2 += f"""<table style="margin-bottom:16px">
    <thead><tr><th>姓名</th><th>总工时</th><th>达标率</th>"""
        for mname, mdates in month_groups:
            s2 += f"<th style='text-align:center'>{mname}<br><span style='font-size:10px;color:#9ca3af'>({len(mdates)}工作日/{month_standards[mname]:.0f}h)</span></th>"
        s2 += "<th>售前</th><th>售后</th><th>内部</th><th>加班</th><th>记录数</th></tr></thead><tbody>"
        
        for name, m in members:
            pday = person_day.get(name, {})
            th = m['totalHours']
            ratio = round(th / standard_total * 100, 1) if standard_total > 0 else 0
            
            # 按月计算
            month_hours = {}
            for mname, mdates in month_groups:
                month_hours[mname] = sum(pday.get(d, 0.0) for d in mdates)
            
            s2 += f"<tr><td><b>{name}</b></td><td>{hours_badge(th, standard_total)}</td>"
            s2 += f"<td style='text-align:center;font-size:12px;color:{'#065f46' if ratio>=95 else '#92400e' if ratio>=80 else '#991b1b'};font-weight:600'>{ratio}%</td>"
            for mname, mdates in month_groups:
                s2 += month_cell(month_hours[mname], month_standards[mname])
            s2 += f"<td>{m['preHours']}h</td><td>{m['afterHours']}h</td><td>{m['internalHours']}h</td>"
            ot = m['overHours']
            s2 += f"<td>{'<span style=color:#ef4444;font-weight:600>' if ot>0 else ''}{ot}h{'</span>' if ot>0 else ''}</td>"
            s2 += f"<td style='text-align:center'>{m['totalRecords']}</td></tr>"
        s2 += "</tbody></table>"
    s2 += "</div>"
    
    # ---- 三、报工不足人员 ----
    s3 = f"""
<div class="section">
  <div class="section-title"><span class="icon">⚠️</span> 三、报工不足人员分析</div>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px">标准：工作日 {STANDARD_DAILY}h/天，共 {work_days} 个工作日 × {STANDARD_DAILY}h = <b>{standard_total:.0f}h/人</b>；周六周日工时视为加班；以下人员存在工时缺口</p>
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
        s3 += '<table style="margin-bottom:12px"><thead><tr><th>姓名</th><th>总工时</th><th>缺口</th>'
        for mname, mdates in month_groups:
            s3 += f"<th style='text-align:center'>{mname}工时</th>"
        s3 += "</tr></thead><tbody>"
        for item in sl:
            pday = item['person_day']
            s3 += f"<tr><td><b>{item['name']}</b></td>"
            s3 += f"<td>{item['total_hours']:.1f}h</td>"
            s3 += f"<td><span style='color:#ef4444;font-weight:700'>-{item['total_shortage']:.1f}h</span></td>"
            for mname, mdates in month_groups:
                mh = sum(pday.get(d, 0.0) for d in mdates)
                s3 += month_cell(mh, month_standards[mname])
            s3 += "</tr>"
        s3 += "</tbody></table>"
    s3 += "</div>"
    
    # ---- 四、文档编写统计 ----
    total_arts = sum(all_teams[tid]['stats']['total_articles'] for tid in [t['id'] for t in TEAMS])
    s4 = f"""
<div class="section">
  <div class="section-title"><span class="icon">📝</span> 四、文档编写统计</div>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px">本期四团队合计发布文档 <b>{total_arts}</b> 篇</p>
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
            s4 += '<div class="shortage-item" style="background:#f9fafb;border-color:#d1d5db">本期无新增文档</div>'
        s4 += '</div>'
    s4 += '</div></div>'
    
    # ---- 五、项目成本消耗 ----
    s5 = """
<div class="section">
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
        if s['total_after'] > 0: bar_html += f'<span class="tag tag-after">售后{after_pct}%</span>'
        if s['total_pre'] > 0: bar_html += f'<span class="tag tag-pre">售前{pre_pct}%</span>'
        if s['total_internal'] > 0: bar_html += f'<span class="tag tag-internal">内部{int_pct}%</span>'
        if s['total_ot'] > 0: bar_html += f'<span class="tag tag-ot">加班{s["total_ot"]}h</span>'
        
        s5 += f"""<tr>
      <td><b>{tname}</b></td>
      <td><b>{total_all:,}h</b></td>
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
    
    # 合计行
    totals = {'pre': 0, 'after': 0, 'internal': 0, 'ot': 0}
    for team in TEAMS:
        s = all_teams[team['id']]['stats']
        totals['pre'] += s['total_pre']
        totals['after'] += s['total_after']
        totals['internal'] += s['total_internal']
        totals['ot'] += s['total_ot']
    grand = totals['pre'] + totals['after'] + totals['internal']
    grand_after_pct = round(totals['after'] / grand * 100, 1) if grand > 0 else 0
    s5 += f"""<tr style="background:#f0f4f8;font-weight:700">
      <td>合计</td><td>{grand:,}h</td><td>{totals['pre']}h</td><td>{totals['after']}h</td><td>{totals['internal']}h</td>
      <td>{totals['ot']}h</td>
      <td><div class="progress"><div class="progress-bar" style="width:{grand_after_pct}%;background:#10b981"></div></div> {grand_after_pct}%</td>
      <td></td>
    </tr>"""
    
    s5 += """</tbody></table>
  <div style="margin-top:14px;padding:12px;background:#f0fdf4;border-radius:8px;font-size:13px;color:#065f46">
    <b>说明：</b>售前工时=项目投标/前期调研；售后工时=实施交付/运维支持；内部工时=内部培训/行政事务；加班工时=非工作时间（含周末）产生的工时。
  </div>
</div>"""
    
    # ---- 六、报工质量分析 ----
    s6 = """
<div class="section">
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
    s6 += "</tbody></table>"
    
    # 人员质量明细
    s6 += '<div class="sub-title" style="margin-top:16px">人员质量明细</div>'
    s6 += '<table><thead><tr><th>姓名</th><th>所属团队</th><th style="text-align:right">操作标准分</th><th style="text-align:right">审批通过率</th><th style="text-align:right">记录数</th><th style="text-align:right">通过数</th><th style="text-align:right">知识库</th><th style="text-align:right">证书</th></tr></thead><tbody>'
    all_person_quality = []
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        summary = all_teams[tid]['summary']
        for name, m in summary.items():
            score = m.get('opScore', 0)
            review_rate = m.get('reviewRate', 0)
            records = m.get('totalRecords', 0)
            approved = m.get('approvedRecords', 0)
            knowledge = m.get('knowledgeCount', 0)
            cert = m.get('certCount', 0)
            score_cls = 'score-high' if score >= 80 else ('score-mid' if score >= 60 else 'score-low')
            review_cls = 'score-high' if review_rate >= 80 else ('score-mid' if review_rate >= 50 else 'score-low')
            s6 += f"""<tr class="quality-row">
        <td><b>{name}</b></td><td>{tname}</td>
        <td style="text-align:right" class="{score_cls}">{score}</td>
        <td style="text-align:right" class="{review_cls}">{review_rate:.1f}%</td>
        <td style="text-align:right">{records}</td>
        <td style="text-align:right">{approved}</td>
        <td style="text-align:right">{knowledge}</td>
        <td style="text-align:right">{cert}</td>
      </tr>"""
    s6 += '</tbody></table>'
    s6 += '</div>'
    
    # ---- 七、项目报工排名 ----
    s7 = """
<div class="section">
  <div class="section-title"><span class="icon">📋</span> 七、各团队项目报工排名（按工时排序 TOP 15）</div>
"""
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        color = TEAM_COLORS.get(tid, '#6b7280')
        ph = project_hours.get(tname, {})
        if not ph:
            s7 += f'<div class="sub-title" style="border-color:{color}">{tname} — 无数据</div>'
            continue
        sorted_projects = sorted(ph.items(), key=lambda x: -x[1])[:15]
        max_hours = sorted_projects[0][1] if sorted_projects else 1
        
        s7 += f'<div class="sub-title" style="border-color:{color}">{tname}（共 {len(ph)} 个项目）</div>'
        s7 += '<table style="margin-bottom:12px"><thead><tr><th style="width:40px">序号</th><th>项目/客户</th><th style="text-align:right">工时</th><th>占比</th></tr></thead><tbody>'
        
        total_team_ph = sum(ph.values())
        for idx, (pname, phours) in enumerate(sorted_projects, 1):
            pct = round(phours / total_team_ph * 100, 1) if total_team_ph > 0 else 0
            bar_w = round(phours / max_hours * 100, 1) if max_hours > 0 else 0
            s7 += f"""<tr class="project-row">
        <td style="text-align:center;color:#6b7280;font-size:12px">{idx}</td>
        <td><b>{pname[:50]}</b></td>
        <td style="text-align:right;font-weight:600">{phours:.1f}h</td>
        <td>
          <span class="project-bar" style="width:{bar_w * 0.5}px;background:{color}"></span>
          <span style="font-size:12px;color:#6b7280">{pct}%</span>
        </td>
      </tr>"""
        s7 += "</tbody></table>"
    
    # 跨团队项目汇总
    all_project_hours = defaultdict(float)
    for tname, ph in project_hours.items():
        for pname, phours in ph.items():
            all_project_hours[pname] += phours
    
    if all_project_hours:
        sorted_all = sorted(all_project_hours.items(), key=lambda x: -x[1])[:20]
        max_h = sorted_all[0][1] if sorted_all else 1
        total_all_ph = sum(all_project_hours.values())
        
        s7 += f'<div class="sub-title" style="border-color:#1e3a5f">🔗 四团队项目汇总 TOP 20（共 {len(all_project_hours)} 个项目）</div>'
        s7 += '<table style="margin-bottom:12px"><thead><tr><th style="width:40px">序号</th><th>项目/客户</th><th style="text-align:right">总工时</th><th>占比</th></tr></thead><tbody>'
        for idx, (pname, phours) in enumerate(sorted_all, 1):
            pct = round(phours / total_all_ph * 100, 1) if total_all_ph > 0 else 0
            bar_w = round(phours / max_h * 100, 1) if max_h > 0 else 0
            s7 += f"""<tr class="project-row">
        <td style="text-align:center;color:#6b7280;font-size:12px">{idx}</td>
        <td><b>{pname[:60]}</b></td>
        <td style="text-align:right;font-weight:700;font-size:14px">{phours:.1f}h</td>
        <td>
          <span class="project-bar" style="width:{bar_w * 0.5}px;background:linear-gradient(90deg,#3b82f6,#8b5cf6)"></span>
          <span style="font-size:12px;color:#6b7280">{pct}%</span>
        </td>
      </tr>"""
        s7 += "</tbody></table>"
    
    s7 += "</div>"
    
    # ---- 七-B、项目工时分布可视化 ----
    s7b = """
<div class="section">
  <div class="section-title"><span class="icon">📊</span> 七-B、项目工时分布可视化（四团队汇总 TOP 15）</div>
  <p style="font-size:12px;color:#6b7280;margin-bottom:14px">横条柱状图展示各项目累计工时分布，便于直观对比项目资源投入</p>
"""
    if all_project_hours:
        sorted_viz = sorted(all_project_hours.items(), key=lambda x: -x[1])[:15]
        max_viz = sorted_viz[0][1] if sorted_viz else 1
        total_viz = sum(all_project_hours.values())
        viz_colors = ['#3b82f6','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#6366f1','#14b8a6','#f97316','#a855f7','#22d3ee','#84cc16','#e11d48','#0ea5e9']
        for idx, (pname, phours) in enumerate(sorted_viz):
            pct = round(phours / total_viz * 100, 1)
            w = round(phours / max_viz * 100, 1)
            c = viz_colors[idx % len(viz_colors)]
            short_name = pname[:30] + ('...' if len(pname) > 30 else '')
            s7b += f"""
  <div class="viz-bar-row">
    <div class="viz-bar-name" title="{pname}">{short_name}</div>
    <div class="viz-bar-track"><div class="viz-bar-fill" style="width:{w}%;background:{c}">{phours:.1f}h</div></div>
    <div class="viz-bar-val">{pct}%</div>
  </div>"""
    s7b += "</div>"
    
    # ---- 八-A、每人季度工作总结 ----
    # 需要从原始 list JSON 中提取每人的 remark 生成工作内容摘要
    person_work_summaries = defaultdict(list)  # name -> list of remark strings
    person_project_map = defaultdict(lambda: defaultdict(float))  # name -> accName -> hours
    person_monthly_map = defaultdict(lambda: defaultdict(float))  # name -> month -> hours
    person_acc_meta = defaultdict(dict)  # 🆕 name -> accName -> (accId, companyName) 取工时最大记录
    
    excluded_set = set(meta.get('excluded', []))
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        try:
            with open(f'/tmp/mes_list_{tid}.json', 'r') as f:
                list_raw = json.load(f)
        except:
            continue
        items = list_raw.get('list', [])
        for item in items:
            name = item.get('executorName', '') or ''
            if not name or name in excluded_set:
                continue
            remark = (item.get('remark', '') or '').strip()
            if remark and len(remark) > 3:
                person_work_summaries[name].append(remark)
            acc_name = item.get('accName', '') or item.get('title', '') or ''
            if acc_name:
                _h = item.get('taskTime', 0) or 0
                person_project_map[name][acc_name] += _h
                _prev = person_acc_meta[name].get(acc_name)
                if _prev is None or _h > _prev[2]:
                    person_acc_meta[name][acc_name] = (
                        str(item.get('accId') or ''),
                        (item.get('companyName') or '').strip(), _h)
            start_str = (item.get('start', '') or '')[:7]
            if start_str:
                person_monthly_map[name][start_str] += item.get('taskTime', 0) or 0
    
    # 获取人员所属团队
    person_team_map = {}
    for team in TEAMS:
        tid = team['id']
        tname = team['name']
        summary = all_teams[tid]['summary']
        for name in summary:
            person_team_map[name] = tname
    
    s8a = """
<div class="section">
  <div class="section-title"><span class="icon">📝</span> 八-A、每人季度工作总结</div>
  <p style="font-size:12px;color:#6b7280;margin-bottom:16px">基于报工内容（remark）自动汇总，展示月度工时分布、参与项目、主要工作内容</p>
"""
    
    # 按工时排序所有人
    all_persons = []
    for team in TEAMS:
        tid = team['id']
        summary = all_teams[tid]['summary']
        for name, m in summary.items():
            all_persons.append((name, m))
    all_persons.sort(key=lambda x: x[1]['totalHours'], reverse=True)
    
    for name, m in all_persons:
        tname = person_team_map.get(name, '')
        color = '#6b7280'
        for team in TEAMS:
            if team['name'] == tname:
                color = TEAM_COLORS.get(team['id'], '#6b7280')
        
        th = m['totalHours']
        ratio = round(th / standard_total * 100, 1)
        remarks = list(dict.fromkeys(person_work_summaries.get(name, [])))[:20]
        projects = sorted(person_project_map.get(name, {}).items(), key=lambda x: -x[1])[:8]
        monthly = person_monthly_map.get(name, {})
        
        # 月度工时条形图
        # 建立 mname -> month_key 映射（"1月" -> "2026-01"）
        month_key_map = {}
        for mname, mdates in month_groups:
            if mdates:
                month_key_map[mname] = mdates[0][:7]  # 从日期推算月份key
        
        month_bars_html = ''
        for mname, mdates in month_groups:
            mkey = month_key_map.get(mname, '')
            mh = monthly.get(mkey, 0)
            std_m = month_standards.get(mname, 176)
            pct = min(round(mh / std_m * 100, 1), 100) if std_m > 0 else 0
            bar_color = '#10b981' if pct >= 95 else ('#f59e0b' if pct >= 80 else '#ef4444')
            month_bars_html += f"""
      <div class="month-col">
        <div class="m-label">{mname}</div>
        <div class="m-val">{mh:.1f}h</div>
        <div class="m-bar"><div class="m-bar-fill" style="width:{pct}%;background:{bar_color}"></div></div>
      </div>"""
        
        # 工时缺口/达标
        if th >= standard_total - 0.01:
            status_html = '<span style="background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600">✅ 达标</span>'
        else:
            shortage_h = standard_total - th
            status_html = f'<span style="background:#fee2e2;color:#991b1b;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600">⚠️ 缺口 {shortage_h:.1f}h</span>'
        
        # 项目标签
        proj_html = ''
        if projects:
            proj_html = '<div class="proj-tags"><b>参与项目：</b>'
            for pname, ph in projects:
                proj_html += f'<span class="proj-tag">{pname[:25]}({ph:.0f}h)</span>'
            proj_html += '</div>'
        
        # 工作内容
        work_html = ''
        if remarks:
            work_html = '<div style="margin-top:8px"><b style="font-size:12px;color:#374151">季度工作内容：</b></div><ul class="work-list">'
            for r in remarks[:12]:
                r_clean = r.replace('\n', '；').replace('\r', '').strip()
                if len(r_clean) > 100:
                    r_clean = r_clean[:97] + '...'
                work_html += f'<li>{r_clean}</li>'
            work_html += '</ul>'
        
        # 🆕 姓名后置「合同名／实施计划」标签（accId 精确关联合同，按工时降序去重）
        if projects:
            pc_tags = ''.join(
                pc_tag_html(pname, ph, person_acc_meta.get(name, {}).get(pname))
                for pname, ph in projects)
            pc_html = f'<div class="person-contracts"><span class="pc-label">支持项目/合同：</span>{pc_tags}</div>'
        else:
            pc_html = '<div class="person-contracts"><span class="pc-label">支持项目/合同：</span><span class="pc-empty">本期报工无关联项目</span></div>'

        s8a += f"""
  <div class="person-card">
    <h4 style="color:{color}">{name} <span style="font-size:12px;color:#6b7280;font-weight:400">{tname}</span></h4>
    {pc_html}
    <div class="person-stats">
      <span class="person-stat">总工时 <b>{th:.1f}h</b></span>
      <span class="person-stat">达标率 <b>{ratio}%</b></span>
      {status_html}
      <span class="person-stat">售后 {m['afterHours']}h</span>
      <span class="person-stat">加班 {m['overHours']}h</span>
      <span class="person-stat">内部 {m['internalHours']}h</span>
      <span class="person-stat">记录 {m['totalRecords']}条</span>
      <span class="person-stat">操作分 {m['opScore']}</span>
    </div>
    <div class="monthly-bars">{month_bars_html}</div>
    {proj_html}
    {work_html}
  </div>"""
    
    s8a += "</div>"

    # ---- 九、服务请求分析 ----
    sr_all = data.get('service_requests', [])
    if not sr_all:
        s9 = """
<div class="section">
  <div class="section-title"><span class="icon">🎫</span> 九、服务请求分析</div>
  <p style="font-size:13px;color:#6b7280">本期无服务请求数据。</p>
</div>"""
    else:
        # 按客户排名
        company_sr = defaultdict(int)
        for sr in sr_all:
            company_sr[sr['company_name']] += 1
        company_top = sorted(company_sr.items(), key=lambda x: -x[1])[:10]
        company_max = company_top[0][1] if company_top else 1

        # 按处理人排名
        person_sr = defaultdict(int)
        for sr in sr_all:
            person_sr[sr['executor']] += 1
        person_top = sorted(person_sr.items(), key=lambda x: -x[1])[:10]
        person_max = person_top[0][1] if person_top else 1

        # 服务等级分布
        level_sr = defaultdict(int)
        for sr in sr_all:
            lv = sr.get('level', '其他')
            level_sr[lv] += 1

        level_colors = {'P0': '#dc2626', 'P1': '#ef4444', 'P2': '#f97316', 'P3': '#eab308', 'P4': '#22c55e', 'P5': '#3b82f6'}

        s9 = f"""
<div class="section">
  <div class="section-title"><span class="icon">🎫</span> 九、服务请求分析</div>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px">本期共处理服务请求 <b>{len(sr_all)}</b> 条，涉及 <b>{len(company_sr)}</b> 个客户</p>
  <div class="grid2">
    <div>
      <div class="sub-title" style="border-color:#3b82f6">客户 TOP10（按请求数）</div>
      <table style="margin-bottom:12px"><thead><tr><th style="width:40px">序号</th><th>客户</th><th style="text-align:right">数量</th><th>占比</th></tr></thead><tbody>"""
        total_sr = len(sr_all)
        for idx, (cname, cnt) in enumerate(company_top, 1):
            pct = round(cnt / total_sr * 100, 1)
            bar_w = round(cnt / company_max * 100, 1)
            s9 += f"""<tr class="project-row">
        <td style="text-align:center;color:#6b7280;font-size:12px">{idx}</td>
        <td><b>{cname[:40]}</b></td>
        <td style="text-align:right;font-weight:600">{cnt}</td>
        <td>
          <span class="project-bar" style="width:{bar_w * 0.4}px;background:#3b82f6"></span>
          <span style="font-size:12px;color:#6b7280">{pct}%</span>
        </td>
      </tr>"""
        s9 += "</tbody></table></div>"

        # 处理人 TOP10
        s9 += """<div>
      <div class="sub-title" style="border-color:#10b981">处理人 TOP10（按处理量）</div>
      <table style="margin-bottom:12px"><thead><tr><th style="width:40px">序号</th><th>处理人</th><th style="text-align:right">数量</th><th>占比</th></tr></thead><tbody>"""
        for idx, (pname, cnt) in enumerate(person_top, 1):
            pct = round(cnt / total_sr * 100, 1)
            bar_w = round(cnt / person_max * 100, 1)
            s9 += f"""<tr class="project-row">
        <td style="text-align:center;color:#6b7280;font-size:12px">{idx}</td>
        <td><b>{pname}</b></td>
        <td style="text-align:right;font-weight:600">{cnt}</td>
        <td>
          <span class="project-bar" style="width:{bar_w * 0.4}px;background:#10b981"></span>
          <span style="font-size:12px;color:#6b7280">{pct}%</span>
        </td>
      </tr>"""
        s9 += "</tbody></table></div></div>"

        # 服务等级分布
        s9 += """<div class="sub-title" style="border-color:#8b5cf6">服务等级分布</div>
  <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px;">"""
        for lv in sorted(level_sr.keys()):
            cnt = level_sr[lv]
            c = level_colors.get(lv, '#6b7280')
            s9 += f'<span style="background:{c};color:white;padding:6px 16px;border-radius:16px;font-size:14px;font-weight:700">{lv} {cnt}条</span>'
        s9 += """</div>"""

        # 明细表格（TOP 50）
        s9 += """<div class="sub-title" style="border-color:#f59e0b">服务请求明细（TOP 50）</div>
  <table><thead><tr><th style="width:40px">序号</th><th>ID</th><th>标题</th><th>客户</th><th>服务等级</th><th>处理人</th><th>状态</th><th>创建时间</th></tr></thead><tbody>"""
        sr_sorted = sorted(sr_all, key=lambda x: x['created_time'], reverse=True)[:50]
        for idx, sr in enumerate(sr_sorted, 1):
            lv = sr.get('level', '')
            c = level_colors.get(lv, '#6b7280')
            s9 += f"""<tr class="project-row">
        <td style="text-align:center;color:#6b7280;font-size:12px">{idx}</td>
        <td style="font-size:12px">{sr.get('id', '')}</td>
        <td style="font-size:12px">{(sr.get('title', '') or '')[:50]}</td>
        <td style="font-size:12px">{(sr.get('company_name', '') or '')[:30]}</td>
        <td><span style="background:{c};color:white;padding:2px 8px;border-radius:8px;font-size:11px;font-weight:600">{lv}</span></td>
        <td style="font-size:12px">{sr.get('executor', '')}</td>
        <td style="font-size:12px">{sr.get('status', '')}</td>
        <td style="font-size:12px">{(sr.get('created_time', '') or '')[:10]}</td>
      </tr>"""
        s9 += "</tbody></table></div>"

    # ---- 十、项目未报工分析 ----
    unreported = data.get('unreported_items', [])
    if not unreported:
        s10 = """
<div class="section">
  <div class="section-title"><span class="icon">📭</span> 十、项目未报工分析</div>
  <p style="font-size:13px;color:#6b7280">未发现未报工合同子项。</p>
</div>"""
    else:
        # 按合同分组
        contract_groups = defaultdict(list)
        for item in unreported:
            contract_groups[item['contract_name']].append(item)

        s10 = f"""
<div class="section">
  <div class="section-title"><span class="icon">📭</span> 十、项目未报工分析</div>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px">东西大区维保项目支持团队下，共发现 <b>{len(unreported)}</b> 个合同子项存在 <b>actualHours=0</b>（未报工），涉及 <b>{len(contract_groups)}</b> 个合同</p>
"""
        for cname, items in sorted(contract_groups.items(), key=lambda x: -len(x[1])):
            first = items[0]
            s10 += f'<div class="sub-title" style="border-color:#f59e0b">{cname[:60]}（{len(items)}个未报工子项）</div>'
            s10 += f'<div style="font-size:12px;color:#6b7280;margin-bottom:8px">项目经理：{first["manager"]} | 合同时间：{(first["start_time"] or "")[:10]} ~ {(first["end_time"] or "")[:10]}</div>'
            s10 += '<table style="margin-bottom:12px"><thead><tr><th style="width:40px">序号</th><th>子项名称</th><th>子项类型</th><th style="text-align:right">计划工时</th><th style="text-align:right">剩余工时</th><th>状态</th></tr></thead><tbody>'
            for idx, item in enumerate(items, 1):
                status = '⚠️ 未报工' if item.get('remaining_task', 0) > 0 else '✅ 已完成'
                status_cls = 'warn' if item.get('remaining_task', 0) > 0 else 'good'
                s10 += f"""<tr class="project-row">
        <td style="text-align:center;color:#6b7280;font-size:12px">{idx}</td>
        <td><b>{(item['item_name'] or '')[:50]}</b></td>
        <td style="font-size:12px">{item.get('item_type', '')}</td>
        <td style="text-align:right;font-weight:600">{item.get('plan_hour', 0)}h</td>
        <td style="text-align:right;font-weight:600">{item.get('remaining_task', 0)}h</td>
        <td class="{status_cls}" style="font-size:12px">{status}</td>
      </tr>"""
            s10 += '</tbody></table>'
        s10 += """
  <div style="margin-top:14px;padding:12px;background:#fff7ed;border-radius:8px;font-size:13px;color:#92400e;border-left:4px solid #f59e0b">
    <b>说明：</b>以上合同子项 actualHours=0，表示在统计周期内未产生任何报工记录。请相关项目经理核实是否为漏报或实际未开展工作。
  </div>
</div>"""

    # ---- 十一、综合评价 ----
    s11 = """
<div class="section">
  <div class="section-title"><span class="icon">🏆</span> 十一、综合评价</div>
"""
    rank_labels = ['🥇', '🥈', '🥉', '4️⃣']
    for rank, (tid, td) in enumerate(team_ranks, 1):
        s = td['stats']
        color = TEAM_COLORS.get(tid, '#6b7280')
        medal = rank_labels[rank - 1] if rank <= 4 else f'#{rank}'
        shortage_cnt = len(td['shortage_list'])
        
        if rank == 1:
            comment = f"人均工时最高（{s['avg_hours']}h），满勤率{s['compliance_rate']}%；文档产出{s['total_articles']}篇。"
        elif rank == 2:
            comment = f"人均工时{s['avg_hours']}h，满勤率{s['compliance_rate']}%；加班{s['total_ot']}h，文档{s['total_articles']}篇。"
        elif rank == 3:
            comment = f"人均工时{s['avg_hours']}h，满勤率{s['compliance_rate']}%；{shortage_cnt}人存在工时缺口，需督促补报。"
        else:
            comment = f"人均工时{s['avg_hours']}h，整体偏低；{shortage_cnt}人未达标准工时，建议加强报工管理。"
        
        s11 += f"""
    <div style="display:flex;align-items:flex-start;gap:16px;padding:14px;background:#f8fafc;border-radius:10px;margin-bottom:10px;border-left:4px solid {color}">
      <div style="font-size:32px;line-height:1">{medal}</div>
      <div style="flex:1">
        <div style="font-size:16px;font-weight:700;color:{color};margin-bottom:6px">{td['name']}</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px">
          <span style="font-size:13px">人数 <b>{s['member_count']}</b></span>
          <span style="font-size:13px">总工时 <b>{s['total_hours']:,}h</b></span>
          <span style="font-size:13px">人均 <b>{s['avg_hours']}h</b></span>
          <span style="font-size:13px">满勤率 {compliance_badge(s['compliance_rate'])}</span>
          <span style="font-size:13px">加班 <b>{s['total_ot']}h</b></span>
          <span style="font-size:13px">文档 <b>{s['total_articles']}</b>篇</span>
          <span style="font-size:13px">缺工时 <b style="color:#ef4444">{shortage_cnt}</b>人</span>
        </div>
        <div style="font-size:13px;color:#6b7280">{comment}</div>
      </div>
    </div>"""
    
    s11 += f"""
  <div style="margin-top:16px;padding:16px;background:#eff6ff;border-radius:10px;font-size:13px;line-height:1.8">
    <b style="color:#1d4ed8">📌 管理建议：</b><br>
    1. 本{mode_label}整体满勤率仅 {overall_compliance}%，多数人员未达到标准 {standard_total:.0f}h，建议统一在截止日前完成报工。<br>
    2. 加班工时合计 {total_ot_all}h，部分人员周末报工较多，请核实是否为正常加班或工时分配不当。<br>
    3. 零文档产出的团队建议加强知识库建设要求，推动经验沉淀（文档总计仅 {total_articles_all} 篇）。<br>
    4. 操作标准分各团队差异较大，建议对零分或低分成员进行辅导，提升报工规范性。<br>
    5. 建议关注报工不足人员（见第三节），个别人员缺口超过 100h，需重点跟进。
  </div>
</div>"""
    
    # ---- 页脚 ----
    footer = f"""
<div style="text-align:center;font-size:12px;color:#9ca3af;padding:20px">
  本报告由自动化任务生成 · {report_time} · 东西大区 {mode_label} 报工分析系统
</div>
"""
    
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
{summary_cards}
{s1}
{s2}
{s3}
{s4}
{s5}
{s6}
{s7}
{s7b}
{s8a}
{s9}
{s10}
{s11}
{footer}
</div>
</body>
</html>"""
    
    return html


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成东西大区报工分析 HTML 报告（季度/长周期）')
    parser.add_argument('--input', default='/tmp/mes_analysis_q1_2026.json', help='分析结果 JSON 文件路径')
    parser.add_argument('--output', required=True, help='输出的 HTML 文件路径')
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    html = generate_report(data)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML 报告已生成：{args.output}（{len(html)} 字符）")
