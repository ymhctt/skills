#!/usr/bin/env python3
"""
东西大区报工分析 - 单团队/单人员深度分析 HTML 报告生成器
基于 dongxi_team4_q1_2026_report.html 深蓝色模板风格

用法：
  python3 generate_single_team_report.py --input /tmp/mes_analysis_result.json --output report.html
  python3 generate_single_team_report.py --input /tmp/mes_analysis_result.json --output report.html --person "张三"

特点：
  - 深蓝色主题（#1a237e / #283593），渐变 Header
  - 顶部导航栏
  - KPI 汇总卡片（6 个核心指标）
  - 人员能效排名表（金银铜徽章 + 色彩达标率）
  - 报工不足分析（橙色预警 + 绿色达标）
  - 项目成本消耗（卡片 + 条形图 + 人员明细）
  - 项目报工排名（表格 + TOP10 柱状图）
  - 文档编写统计
  - 报工质量分析（质量卡片 + 人员明细 + 预警）
  - 每人季度工作总结（月度工时条形图 + 参与项目 + 工作内容列表）
  - 综合评价

  --person 参数：只输出指定人员的工作总结，其他维度正常显示全团队
"""

import json
import argparse
import os
import sys
from datetime import date
from collections import defaultdict

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

# ==================== CSS ====================
CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,"PingFang SC","Microsoft YaHei","Helvetica Neue",sans-serif; background:#f0f2f5; color:#333; line-height:1.6; }

.container { max-width:1400px; margin:0 auto; padding:20px; }

/* 顶部标题 */
.header { background:linear-gradient(135deg,#1a237e,#283593); color:#fff; padding:30px 40px; border-radius:12px; margin-bottom:24px; box-shadow:0 4px 15px rgba(26,35,126,0.3); }
.header h1 { font-size:28px; margin-bottom:8px; }
.header .subtitle { font-size:14px; opacity:0.85; }
.header .meta-row { display:flex; gap:20px; margin-top:12px; flex-wrap:wrap; }
.header .meta-item { font-size:13px; background:rgba(255,255,255,0.15); padding:4px 12px; border-radius:20px; }

/* 卡片 */
.card { background:#fff; border-radius:10px; padding:24px; margin-bottom:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.card h2 { font-size:20px; color:#1a237e; margin-bottom:16px; padding-bottom:10px; border-bottom:2px solid #e8eaf6; display:flex; align-items:center; gap:8px; }
.card h3 { font-size:16px; color:#283593; margin:16px 0 12px; }

/* KPI 卡片 */
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:16px; margin-bottom:24px; }
.kpi { background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; padding:20px; border-radius:10px; text-align:center; box-shadow:0 3px 10px rgba(102,126,234,0.3); }
.kpi.green { background:linear-gradient(135deg,#11998e,#38ef7d); }
.kpi.orange { background:linear-gradient(135deg,#f093fb,#f5576c); }
.kpi.blue { background:linear-gradient(135deg,#4facfe,#00f2fe); }
.kpi .value { font-size:32px; font-weight:700; }
.kpi .label { font-size:13px; opacity:0.9; margin-top:4px; }

/* 表格 */
table { width:100%; border-collapse:collapse; font-size:13px; }
th { background:#f5f7ff; color:#1a237e; padding:10px 12px; text-align:left; font-weight:600; position:sticky; top:0; }
td { padding:8px 12px; border-bottom:1px solid #eee; }
tr:hover { background:#f8f9ff; }
.text-right { text-align:right; }
.text-center { text-align:center; }

/* 成员排名表 */
.rank-name { font-weight:600; color:#283593; }
.rank-highlight { background:#fff8e1 !important; }
.rank-warn { background:#ffebee !important; }

/* 报工不足 */
.shortage-section { background:#fff3e0; border-left:4px solid #ff9800; padding:16px; border-radius:0 8px 8px 0; margin:16px 0; }
.shortage-section h3 { color:#e65100; margin-top:0; }

/* 项目排名 */
.project-tag { display:inline-block; background:#e8eaf6; color:#283593; padding:3px 10px; border-radius:12px; font-size:12px; margin:3px; }
.project-hours { color:#1a237e; font-weight:600; }

/* 人员工作总结 */
.person-summary { background:#fafbff; border:1px solid #e8eaf6; border-radius:10px; padding:20px; margin-bottom:16px; }
.person-summary h4 { color:#1a237e; font-size:17px; margin-bottom:12px; display:flex; align-items:center; gap:8px; }
.summary-stats { display:flex; flex-wrap:wrap; gap:12px; margin-bottom:12px; }
.stat-item { font-size:13px; background:#eef; padding:4px 12px; border-radius:15px; }

/* 🆕 姓名后置「支持项目/合同」标签 */
.person-contracts { font-size:12px; margin:0 0 12px; padding:6px 10px; background:#eef2ff; border-left:3px solid #6366f1; border-radius:6px; }
.pc-label { color:#4338ca; font-weight:600; margin-right:4px; }
.pc-tag { display:inline-block; background:#e0e7ff; color:#3730a3; padding:2px 9px; border-radius:10px; font-size:11px; margin:2px 3px 2px 0; font-weight:500; }
.pc-tag b { font-weight:700; }
.pc-sub { color:#6366f1; font-weight:400; margin-left:2px; }
.pc-empty { color:#9ca3af; font-style:italic; }

.monthly-bar { display:flex; gap:12px; margin-bottom:12px; }
.month-block { flex:1; position:relative; background:#eef; border-radius:8px; padding:8px 12px; }
.month-label { font-size:12px; color:#666; }
.month-value { font-size:15px; font-weight:700; color:#1a237e; }
.month-bar { height:6px; border-radius:3px; margin-top:4px; transition:width 0.3s; }

.shortage-warning { background:#ffebee; color:#c62828; padding:8px 12px; border-radius:6px; font-size:13px; margin-bottom:10px; }
.full-badge { background:#e8f5e9; color:#2e7d32; padding:8px 12px; border-radius:6px; font-size:13px; margin-bottom:10px; display:inline-block; }

.project-list { font-size:13px; color:#444; margin-bottom:10px; }
.article-list { font-size:13px; color:#1565c0; margin-bottom:10px; }

.work-content { font-size:13px; color:#555; margin-bottom:6px; }
.work-ul { padding-left:20px; font-size:13px; color:#444; }
.work-ul li { margin-bottom:4px; padding-left:4px; }

/* 成本结构 */
.cost-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:12px; }
.cost-card { border:1px solid #e0e0e0; border-radius:8px; padding:16px; text-align:center; }
.cost-card .cost-value { font-size:24px; font-weight:700; margin:8px 0 4px; }
.cost-card .cost-label { font-size:12px; color:#888; }
.cost-card .cost-pct { font-size:13px; color:#666; }

/* 工时分布 */
.bar-chart { display:flex; flex-direction:column; gap:6px; }
.bar-row { display:flex; align-items:center; gap:10px; }
.bar-name { width:70px; font-size:13px; text-align:right; flex-shrink:0; }
.bar-track { flex:1; height:22px; background:#eee; border-radius:11px; overflow:hidden; }
.bar-fill { height:100%; border-radius:11px; display:flex; align-items:center; padding-left:8px; font-size:11px; color:#fff; font-weight:600; min-width:fit-content; transition:width 0.3s; }
.bar-value { width:60px; font-size:13px; text-align:right; flex-shrink:0; }

/* 文档列表 */
.doc-table td { font-size:13px; }

/* 导航 */
.nav-bar { background:#fff; padding:10px 20px; border-radius:8px; margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,0.06); display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
.nav-bar a { color:#283593; text-decoration:none; font-size:13px; padding:4px 12px; border-radius:15px; background:#e8eaf6; }
.nav-bar a:hover { background:#c5cae9; }

/* 综合评价 */
.eval-section { background:linear-gradient(135deg,#f5f7ff,#e8eaf6); border-radius:10px; padding:24px; }
.eval-section h2 { color:#1a237e; border-bottom:2px solid #c5cae9; }
.eval-item { margin-bottom:16px; }
.eval-item .eval-title { font-weight:600; color:#283593; margin-bottom:4px; }
.eval-item p { font-size:14px; color:#444; }

@media print {
    .container { padding:10px; }
    .card { box-shadow:none; border:1px solid #ddd; page-break-inside:avoid; }
    body { background:#fff; }
}
"""


# ==================== 辅助函数 ====================

def get_month_groups(date_strs):
    """将日期列表按月分组"""
    groups = defaultdict(list)
    month_names = {'01':'1月','02':'2月','03':'3月','04':'4月','05':'5月','06':'6月',
                   '07':'7月','08':'8月','09':'9月','10':'10月','11':'11月','12':'12月'}
    for d in date_strs:
        m = d[5:7]
        groups[month_names[m]].append(d)
    sorted_groups = []
    for i in range(1, 13):
        key = f'{i}月'
        if key in groups:
            sorted_groups.append((key, groups[key]))
    return sorted_groups


def rate_color(rate):
    """达标率颜色"""
    if rate >= 100: return '#27ae60'
    if rate >= 90: return '#2ecc71'
    if rate >= 70: return '#f39c12'
    return '#e74c3c'


def rank_badge(rank):
    """排名徽章"""
    if rank == 1: return '<span style="background:#FFD700;color:#333;padding:2px 8px;border-radius:10px;font-weight:bold">🥇</span>'
    if rank == 2: return '<span style="background:#C0C0C0;color:#333;padding:2px 8px;border-radius:10px;font-weight:bold">🥈</span>'
    if rank == 3: return '<span style="background:#CD7F32;color:#fff;padding:2px 8px;border-radius:10px;font-weight:bold">🥉</span>'
    return f'<span>{rank}</span>'


def rank_row_class(rank, total):
    """排名行样式"""
    if rank <= 3: return 'rank-highlight'
    if rank == total: return 'rank-warn'
    return ''


def load_list_data(list_file_path, excluded):
    """加载并解析原始 list JSON，返回清洗后的 items 列表"""
    try:
        with open(list_file_path, 'r') as f:
            list_raw = json.load(f)
    except:
        return []
    items = list_raw.get('list', [])
    # 检查是否有分页（total 字段大于已返回的条数）
    total = list_raw.get('total', 0)
    if total > len(items):
        import sys
        msg = "Warning: list JSON has %d records but only loaded %d. Use --page-size in MES CLI." % (total, len(items))
        print(msg)
    return items


def calc_person_day_from_list(items, excluded, date_start_str, date_end_str):
    """从原始 list JSON items 重新计算每人每天的工时分布（不依赖 analyze.py 的结果）"""
    person_day = defaultdict(lambda: defaultdict(float))
    for item in items:
        name = item.get('executorName', '') or ''
        if not name or name in excluded:
            continue
        start = item.get('start', '') or ''
        day = start[:10] if len(start) >= 10 else ''
        hours = item.get('taskTime', 0) or 0
        if day and date_start_str <= day <= date_end_str:
            person_day[name][day] += hours
    return dict(person_day)


def analyze_shortage_from_day(person_day_map, date_strs, standard_total, summary_map):
    """
    从 person_day 数据重新计算报工不足情况（修正版）
    
    关键逻辑：
    - 逐工作日检查：如果当天工时 < 8h，则记为不足
    - person_day 中没有记录的天 = 缺勤（0h）
    - total_hours 使用 summary 中的官方数据（更准确）
    """
    date_set = set(date_strs)
    shortage_list = []
    qualified_list = []

    for name, total_hours in summary_map.items():
        pday = person_day_map.get(name, {})
        shortage_days = []
        total_shortage = 0.0

        for d in date_strs:
            actual = pday.get(d, 0.0)
            if actual < STANDARD_DAILY - 0.01:
                gap = STANDARD_DAILY - actual
                shortage_days.append({'date': d, 'actual': round(actual, 2), 'shortage': round(gap, 2)})
                total_shortage += gap

        # 周末加班
        ws = date_strs[0] if date_strs else ''
        weekend_hours = sum(v for k, v in pday.items() if k not in date_set and k >= ws)

        shortage_days_count = len(shortage_days)

        if total_hours >= standard_total - 0.01:
            qualified_list.append({
                'name': name,
                'total_hours': total_hours,
                'weekend_hours': weekend_hours,
            })
        else:
            shortage_list.append({
                'name': name,
                'total_hours': total_hours,
                'total_shortage': round(total_shortage, 2),
                'shortage_days_count': shortage_days_count,
                'weekend_hours': weekend_hours,
                'person_day': pday,
            })

    shortage_list.sort(key=lambda x: x['total_shortage'], reverse=True)
    return shortage_list, qualified_list


def calc_project_ranking(items, excluded):
    """从原始 list JSON items 中提取项目报工排名"""
    project_hours = defaultdict(float)
    project_records = defaultdict(int)
    person_project = defaultdict(lambda: defaultdict(float))
    person_acc_meta = defaultdict(dict)  # 🆕 name -> accName -> (accId, companyName) 取工时最大记录

    for item in items:
        name = item.get('executorName', '') or ''
        if not name or name in excluded:
            continue
        acc_name = item.get('accName', '') or ''
        hours = item.get('taskTime', 0) or 0
        if acc_name:
            project_hours[acc_name] += hours
            project_records[acc_name] += 1
            person_project[name][acc_name] += hours
            _prev = person_acc_meta[name].get(acc_name)
            if _prev is None or hours > _prev[2]:
                person_acc_meta[name][acc_name] = (
                    str(item.get('accId') or ''),
                    (item.get('companyName') or '').strip(), hours)

    return (sorted(project_hours.items(), key=lambda x: -x[1]),
            dict(person_project), person_acc_meta)


def classify_work_category(remark):
    """根据报工内容关键词分类工作类型"""
    remark_lower = remark.lower()
    # 驻场
    if any(k in remark for k in ['驻场', '驻点', '现场服务', '现场支持']):
        return '驻场服务'
    # 故障/应急
    if any(k in remark for k in ['故障', '应急', '紧急', '救急', '恢复', '中断', '宕机', '异常']):
        return '故障处理'
    # 维保/巡检
    if any(k in remark for k in ['维保', '巡检', '巡', '维护', '保养', '健康检查', '例行', '季度巡']):
        return '维保巡检'
    # 安装/部署/实施
    if any(k in remark for k in ['安装', '部署', '实施', '上线', '迁移', '升级', '扩容', '配置']):
        return '安装部署'
    # 售前/POC
    if any(k in remark for k in ['售前', 'POC', '方案', '投标', '交流', '调研', '需求', '沟通']):
        return '售前支持'
    # 培训/文档
    if any(k in remark for k in ['培训', '文档', '手册', '知识库', '总结', '整理']):
        return '培训文档'
    # 优化/调优
    if any(k in remark for k in ['优化', '调优', '性能', '慢', 'SQL', '索引', '参数调整', '调整参数']):
        return '性能优化'
    # 备份/恢复/容灾
    if any(k in remark for k in ['备份', '恢复', '容灾', '演练', 'RAC', 'ADG', 'DG']):
        return '备份容灾'
    # 数据处理
    if any(k in remark for k in ['数据', '同步', '迁移', '导入', '导出', '清理', '归档']):
        return '数据管理'
    return '其他工作'


def calc_person_work(items, excluded, summary_map):
    """
    从原始 list JSON items 提取每人的详细工作信息
    
    返回:
      person_remarks: {name: [(remark, hours, category), ...]}
      person_monthly: {name: {'2026-01': hours, ...}}
      person_categories: {name: {category: {'hours': h, 'count': n, 'remarks': [...]}}}
    """
    person_remarks = defaultdict(list)
    person_monthly = defaultdict(lambda: defaultdict(float))
    person_categories = defaultdict(lambda: defaultdict(lambda: {'hours': 0.0, 'count': 0, 'remarks': []}))

    for item in items:
        name = item.get('executorName', '') or ''
        if not name or name in excluded:
            continue
        remark = (item.get('remark', '') or '').strip()
        hours = item.get('taskTime', 0) or 0
        start_str = (item.get('start', '') or '')[:7]

        if start_str:
            person_monthly[name][start_str] += hours

        if remark and len(remark) > 3:
            # 去重
            existing_texts = [r[0] for r in person_remarks[name]]
            if remark not in existing_texts:
                category = classify_work_category(remark)
                person_remarks[name].append((remark, hours, category))
                person_categories[name][category]['hours'] += hours
                person_categories[name][category]['count'] += 1
                if len(person_categories[name][category]['remarks']) < 5:
                    person_categories[name][category]['remarks'].append(remark)

    return dict(person_remarks), dict(person_monthly), dict(person_categories)


def calc_person_weekend(person_day_map, date_set, work_start):
    """计算每人周末加班工时"""
    person_weekend = defaultdict(float)
    for name, day_map in person_day_map.items():
        for d, h in day_map.items():
            if d >= work_start and d not in date_set:
                person_weekend[name] += h
    return dict(person_weekend)


def generate_person_summary_text(name, m, person_categories, person_project, rate, standard_total, article_list):
    """
    生成每人的智能工作总结文本
    
    分析维度：
    1. 核心工作领域（按工时排序的工作类型）
    2. 工作亮点（驻场/维保/故障处理等高频工作）
    3. 主要参与项目
    4. 待改进方面（工时不足/零工时天多等）
    5. 文档产出
    """
    parts = []

    categories = person_categories.get(name, {})
    projects = sorted(person_project.get(name, {}).items(), key=lambda x: -x[1])
    person_articles = [a['title'] for a in article_list if a['author'] == name]
    th = m['totalHours']

    # 1. 核心工作领域
    if categories:
        sorted_cats = sorted(categories.items(), key=lambda x: x[1]['hours'], reverse=True)
        cat_descriptions = []
        for cat, info in sorted_cats[:5]:
            h = info['hours']
            c = info['count']
            if cat == '驻场服务':
                cat_descriptions.append(f"长期驻场服务（{h:.0f}h/{c}次）")
            elif cat == '故障处理':
                cat_descriptions.append(f"应急故障处理（{h:.0f}h/{c}次）")
            elif cat == '维保巡检':
                cat_descriptions.append(f"维保巡检（{h:.0f}h/{c}次）")
            elif cat == '安装部署':
                cat_descriptions.append(f"安装部署实施（{h:.0f}h/{c}次）")
            elif cat == '售前支持':
                cat_descriptions.append(f"售前技术支持（{h:.0f}h/{c}次）")
            elif cat == '性能优化':
                cat_descriptions.append(f"性能优化调优（{h:.0f}h/{c}次）")
            elif cat == '培训文档':
                cat_descriptions.append(f"培训与文档编写（{h:.0f}h/{c}次）")
            elif cat == '备份容灾':
                cat_descriptions.append(f"备份恢复与容灾（{h:.0f}h/{c}次）")
            elif cat == '数据管理':
                cat_descriptions.append(f"数据管理与迁移（{h:.0f}h/{c}次）")
            else:
                cat_descriptions.append(f"其他日常（{h:.0f}h/{c}次）")
        parts.append(f"核心工作：{'、'.join(cat_descriptions[:4])}。")

    # 2. 工作亮点
    highlights = []
    if '故障处理' in categories:
        fc = categories['故障处理']
        highlights.append(f"响应{fc['count']}次应急故障处理，保障客户系统稳定运行")
    if '驻场服务' in categories:
        sc = categories['驻场服务']
        top_project = projects[0] if projects else None
        proj_name = top_project[0] if top_project else ''
        highlights.append(f"持续驻场{sc['count']}次（{sc['hours']:.0f}h），{('主要服务' + proj_name) if proj_name else '提供现场技术支持'}")
    if '维保巡检' in categories:
        mc = categories['维保巡检']
        highlights.append(f"完成{mc['count']}次维保巡检任务，确保系统健康运行")
    if '安装部署' in categories:
        ic = categories['安装部署']
        highlights.append(f"参与{ic['count']}次安装部署/升级扩容工作")
    if '售前支持' in categories:
        pc = categories['售前支持']
        highlights.append(f"提供{pc['count']}次售前技术支持，助力业务拓展")
    if person_articles:
        highlights.append(f"撰写{len(person_articles)}篇技术文档，积极进行知识沉淀")

    if highlights:
        parts.append(f"工作亮点：{'；'.join(highlights[:3])}。")

    # 3. 主要项目
    if projects:
        top_projs = projects[:3]
        proj_desc = '、'.join(f"{pn}（{ph:.0f}h）" for pn, ph in top_projs)
        parts.append(f"重点项目：{proj_desc}。")

    # 4. 待改进
    improvements = []
    if th < standard_total - 0.01:
        gap = standard_total - th
        improvements.append(f"季度工时{th:.0f}h，距标准{standard_total:.0f}h缺口{gap:.0f}h，建议加强日常报工规范性")
    if m['opScore'] < 80:
        improvements.append(f"操作标准分{m['opScore']}分，低于团队平均水平，需提升报工质量")
    review_r = m.get('reviewRate', 0)
    if review_r < 80:
        improvements.append(f"审批通过率{review_r:.1f}%，部分报工可能被退回，建议关注报工内容完整性")
    if m.get('docCount', 0) == 0:
        improvements.append("本季度无文档产出，建议及时总结技术经验")
    if improvements:
        parts.append(f"待改进：{'；'.join(improvements)}。")

    return '\n'.join(parts)


# ==================== 主报告生成 ====================

def generate_report(data, person_filter=None):
    meta = data['meta']
    all_teams = data['teams']
    teams_config = data.get('teams_config', [])

    date_strs = meta['date_strs']
    standard_total = meta['standard_total']
    work_days = meta['work_days']
    excluded = set(meta.get('excluded', []))
    date_set = set(date_strs)
    work_start = date_strs[0] if date_strs else ''
    report_time = meta.get('report_time', '')

    month_groups = get_month_groups(date_strs)
    month_standards = {name: len(dates) * STANDARD_DAILY for name, dates in month_groups}
    month_key_map = {}
    for mname, mdates in month_groups:
        if mdates:
            month_key_map[mname] = mdates[0][:7]

    # 取第一个（也是唯一一个）团队的数据
    tid = list(all_teams.keys())[0] if all_teams else None
    if not tid:
        return '<html><body><h1>无数据</h1></body></html>'
    td = all_teams[tid]
    tname = td['name']
    summary = td['summary']
    article_authors = td.get('article_authors', {})
    article_list = td.get('article_list', [])
    s = td['stats']

    # ---- 从原始 list JSON 重新计算所有数据（不依赖 analyze.py 的截断数据）----
    list_file = f'/tmp/mes_list_{tid}.json'
    items = load_list_data(list_file, excluded)
    if not items:
        return '<html><body><h1>原始 list 数据为空，请检查 MES CLI 采集时是否加了 --page-size 参数</h1></body></html>'

    # 重新计算 person_day（按完整日期范围）
    person_day = calc_person_day_from_list(items, excluded, meta['date_start'], meta['date_end'])

    # 重新计算报工不足（从 person_day 逐天检查）
    summary_map = {name: m['totalHours'] for name, m in summary.items()}
    shortage_members, qualified_members = analyze_shortage_from_day(
        person_day, date_strs, standard_total, summary_map)

    # 周末加班
    person_weekend = calc_person_weekend(person_day, date_set, work_start)

    # 计算排名
    members = sorted(summary.items(), key=lambda x: x[1]['totalHours'], reverse=True)
    member_count = len(members)

    # 项目排名
    project_ranking, person_project, person_acc_meta = calc_project_ranking(items, excluded)

    # 人员工作内容、月度工时、工作分类
    person_remarks, person_monthly, person_categories = calc_person_work(items, excluded, summary_map)

    # 综合评价用
    full_count = sum(1 for _, m in members if m['totalHours'] >= standard_total - 0.01)
    full_rate = round(full_count / member_count * 100, 1) if member_count > 0 else 0

    # ---- Header ----
    mode_label = '季度' if meta.get('mode') == 'quarter' else ('月度' if meta.get('mode') == 'month' else '周')
    title = f"📊 {tname} {meta['date_start']}~{meta['date_end']} 报工综合分析报告"
    if person_filter:
        title = f"📊 {tname} · {person_filter} {meta['date_start']}~{meta['date_end']} 报工综合分析报告"

    header_html = f"""
<div class="header">
    <h1>{title}</h1>
    <div class="subtitle">详细数据分析 · 人员工作总结 · 项目成本消耗 · 能效排名</div>
    <div class="meta-row">
        <span class="meta-item">📅 {meta['date_start']} ~ {meta['date_end']}</span>
        <span class="meta-item">👥 {member_count}人</span>
        <span class="meta-item">📋 {work_days}个工作日</span>
        <span class="meta-item">⏱️ 标准工时: {standard_total:.0f}h/人</span>
        <span class="meta-item">📝 {s['total_records']}条报工记录</span>
    </div>
</div>"""

    # ---- Nav ----
    nav_html = """
<div class="nav-bar">
    <a href="#kpi">核心指标</a>
    <a href="#ranking">能效排名</a>
    <a href="#shortage">报工不足</a>
    <a href="#cost">成本结构</a>
    <a href="#projects">项目排名</a>
    <a href="#docs">文档统计</a>
    <a href="#quality">报工质量</a>
    <a href="#summaries">人员工作总结</a>
    <a href="#eval">综合评价</a>
</div>"""

    # ---- KPI ----
    avg_hours = round(s['total_hours'] / member_count, 2) if member_count > 0 else 0
    total_project_hours = sum(ph for _, ph in project_ranking)

    kpi_html = f"""
<div class="kpi-grid" id="kpi">
    <div class="kpi"><div class="value">{s['total_hours']:,.1f}</div><div class="label">总工时 (h)</div></div>
    <div class="kpi green"><div class="value">{avg_hours}</div><div class="label">人均工时 (h)</div></div>
    <div class="kpi blue"><div class="value">{full_rate}%</div><div class="label">满勤率 ({full_count}/{member_count})</div></div>
    <div class="kpi orange"><div class="value">{s['total_records']}</div><div class="label">报工记录 (条)</div></div>
    <div class="kpi"><div class="value">{s['total_articles']}</div><div class="label">技术文档 (篇)</div></div>
    <div class="kpi green"><div class="value">{s['avg_opScore']:.1f}</div><div class="label">平均操作标准分</div></div>
</div>"""

    # ---- 1. 能效排名 ----
    ranking_html = f"""
<div class="card" id="ranking">
    <h2>🏆 人员能效排名</h2>
    <p style="color:#888;font-size:13px;margin-bottom:12px;">按总工时从高到低排列，达标率 = 实际工时/标准工时({standard_total:.0f}h)，绿色≥100%</p>
    <div style="overflow-x:auto;">
    <table>
        <tr>
            <th class="text-center">排名</th><th>姓名</th>
            <th class="text-right">总工时</th><th class="text-right">日均</th>
            <th class="text-right">达标率</th><th class="text-right">售前</th>
            <th class="text-right">售后</th><th class="text-right">加班</th><th class="text-right">内部</th>
            <th class="text-right">周末加班</th><th class="text-right">记录数</th>
            <th class="text-right">操作分</th><th class="text-right">文档</th>
        </tr>"""

    for rank, (name, m) in enumerate(members, 1):
        th = m['totalHours']
        daily = round(th / work_days, 2) if work_days > 0 else 0
        rate = round(th / standard_total * 100, 1) if standard_total > 0 else 0
        rc = rate_color(rate)
        weekend = person_weekend.get(name, 0)
        doc_count = m.get('docCount', 0)

        ranking_html += f"""
        <tr class="{rank_row_class(rank, member_count)}">
            <td class="text-center">{rank_badge(rank)}</td>
            <td class="rank-name">{name}</td>
            <td class="text-right"><b>{th:.1f}</b></td>
            <td class="text-right">{daily}</td>
            <td class="text-right"><span style="color:{rc};font-weight:600">{rate}%</span></td>
            <td class="text-right">{m['preHours']}</td>
            <td class="text-right">{m['afterHours']}</td>
            <td class="text-right">{m['overHours']}</td>
            <td class="text-right">{m['internalHours']}</td>
            <td class="text-right">{'<span style=color:#e74c3c>' if weekend > 0 else ''}{weekend:.1f}{'</span>' if weekend > 0 else ''}</td>
            <td class="text-right">{m['totalRecords']}</td>
            <td class="text-right"><span style="color:{rate_color(m['opScore'])}">{m['opScore']}</span></td>
            <td class="text-right">{doc_count}</td>
        </tr>"""

    ranking_html += "\n    </table>\n    </div>\n</div>"

    # ---- 2. 报工不足（使用自计算的 shortage_members/qualified_members）----
    shortage_html = f"""
<div class="card" id="shortage">
    <h2>⚠️ 报工不足分析</h2>
    <p style="color:#888;font-size:13px;margin-bottom:12px;">工作日未满8h的累计缺口，周末（周六日）工时计入加班；标准工时 = {work_days}天 × 8h = {standard_total}h</p>"""

    if shortage_members:
        shortage_html += f"""
    <div class="shortage-section">
        <h3>需关注人员（{len(shortage_members)}人存在工时缺口）</h3>
        <table>
            <tr><th>姓名</th><th class="text-right">实际工时</th><th class="text-right">标准工时</th><th class="text-right">缺口</th><th class="text-right">达标率</th><th class="text-right">缺勤天数</th><th class="text-right">周末加班</th></tr>"""
        for item in shortage_members:
            weekend = item['weekend_hours']
            rate = round(item['total_hours'] / standard_total * 100, 1) if standard_total > 0 else 0
            shortage_html += f"""
            <tr>
                <td>{item['name']}</td>
                <td class="text-right">{item['total_hours']:.1f}h</td>
                <td class="text-right">{standard_total}h</td>
                <td class="text-right" style="color:#c62828;font-weight:600">{item['total_shortage']:.1f}h</td>
                <td class="text-right"><span style="color:{rate_color(rate)}">{rate}%</span></td>
                <td class="text-right">{item['shortage_days_count']}天</td>
                <td class="text-right">{weekend:.1f}h</td>
            </tr>"""
        shortage_html += "\n        </table>\n    </div>"

    if qualified_members:
        shortage_html += f"""
    <h3 style="margin-top:16px;color:#2e7d32;">✅ 达标人员（{len(qualified_members)}人）</h3>
    <div style="display:flex;flex-wrap:wrap;gap:8px;">"""
        for item in qualified_members:
            shortage_html += f'<span class="project-tag" style="background:#e8f5e9;color:#2e7d32">{item["name"]} ({item["total_hours"]:.1f}h)</span>'
        shortage_html += "</div>"

    shortage_html += "\n</div>"

    # ---- 3. 成本结构 ----
    total_effective = s['total_pre'] + s['total_after'] + s['total_internal']
    after_pct = round(s['total_after'] / total_effective * 100, 1) if total_effective > 0 else 0
    pre_pct = round(s['total_pre'] / total_effective * 100, 1) if total_effective > 0 else 0
    int_pct = round(s['total_internal'] / total_effective * 100, 1) if total_effective > 0 else 0

    cost_html = f"""
<div class="card" id="cost">
    <h2>💰 项目成本消耗分析</h2>

    <div class="cost-grid" style="margin-bottom:20px;">
        <div class="cost-card">
            <div class="cost-label">售后工时</div>
            <div class="cost-value" style="color:#1565c0">{s['total_after']}h</div>
            <div class="cost-pct">{after_pct}%</div>
        </div>
        <div class="cost-card">
            <div class="cost-label">加班工时</div>
            <div class="cost-value" style="color:#e65100">{s['total_ot']}h</div>
        </div>
        <div class="cost-card">
            <div class="cost-label">内部工时</div>
            <div class="cost-value" style="color:#6a1b9a">{s['total_internal']}h</div>
            <div class="cost-pct">{int_pct}%</div>
        </div>
        <div class="cost-card">
            <div class="cost-label">售前工时</div>
            <div class="cost-value" style="color:#00897b">{s['total_pre']}h</div>
            <div class="cost-pct">{pre_pct}%</div>
        </div>
    </div>

    <h3>工时类型占比</h3>
    <div class="bar-chart">
        <div class="bar-row"><div class="bar-name">售后</div><div class="bar-track"><div class="bar-fill" style="width:{after_pct}%;background:#1565c0">{after_pct}%</div></div><div class="bar-value">{s['total_after']}h</div></div>
        <div class="bar-row"><div class="bar-name">加班</div><div class="bar-track"><div class="bar-fill" style="width:{min(round(s['total_ot']/total_effective*100,1),100)}%;background:#e65100">{round(s['total_ot']/total_effective*100,1) if total_effective>0 else 0}%</div></div><div class="bar-value">{s['total_ot']}h</div></div>
        <div class="bar-row"><div class="bar-name">内部</div><div class="bar-track"><div class="bar-fill" style="width:{int_pct}%;background:#6a1b9a">{int_pct}%</div></div><div class="bar-value">{s['total_internal']}h</div></div>
        <div class="bar-row"><div class="bar-name">售前</div><div class="bar-track"><div class="bar-fill" style="width:{pre_pct}%;background:#00897b">{pre_pct}%</div></div><div class="bar-value">{s['total_pre']}h</div></div>
    </div>

    <h3 style="margin-top:20px;">人员工时成本明细</h3>
    <div style="overflow-x:auto;">
    <table>
        <tr><th>姓名</th><th class="text-right">总工时</th><th class="text-right">售后</th><th class="text-right">加班</th><th class="text-right">内部</th><th class="text-right">售前</th><th class="text-right">售后占比</th></tr>"""
    for name, m in members:
        personal_effective = m['afterHours'] + m['internalHours'] + m['preHours']
        personal_after_pct = round(m['afterHours'] / personal_effective * 100, 1) if personal_effective > 0 else 100
        cost_html += f"""
        <tr>
            <td>{name}</td>
            <td class="text-right"><b>{m['totalHours']:.1f}</b></td>
            <td class="text-right">{m['afterHours']}</td>
            <td class="text-right">{m['overHours']}</td>
            <td class="text-right">{m['internalHours']}</td>
            <td class="text-right">{m['preHours']}</td>
            <td class="text-right">{personal_after_pct}%</td>
        </tr>"""
    cost_html += "\n    </table>\n    </div>\n</div>"

    # ---- 4. 项目排名 ----
    top_n = min(20, len(project_ranking))
    total_ph = sum(ph for _, ph in project_ranking) if project_ranking else 1
    max_ph = project_ranking[0][1] if project_ranking else 1

    projects_html = f"""
<div class="card" id="projects">
    <h2>🏗️ 项目报工排名</h2>
    <p style="color:#888;font-size:13px;margin-bottom:12px;">按项目累计工时从高到低排列（TOP {top_n}）</p>
    <div style="overflow-x:auto;">
    <table>
        <tr><th class="text-center">排名</th><th>项目名称</th><th class="text-right">累计工时</th><th class="text-right">占比</th></tr>"""
    for idx, (pname, phours) in enumerate(project_ranking[:top_n], 1):
        pct = round(phours / total_ph * 100, 1) if total_ph > 0 else 0
        projects_html += f"""
        <tr>
            <td class="text-center">{rank_badge(idx)}</td>
            <td>{pname}</td>
            <td class="text-right"><span class="project-hours">{phours:.1f}h</span></td>
            <td class="text-right">{pct}%</td>
        </tr>"""
    projects_html += "\n    </table>\n    </div>\n\n"

    # 项目工时分布可视化 TOP 10
    projects_html += """    <h3 style="margin-top:20px;">项目工时分布可视化</h3>
    <div class="bar-chart">\n"""
    for pname, phours in project_ranking[:10]:
        w = round(phours / max_ph * 100, 1) if max_ph > 0 else 0
        short = pname[:25] + ('...' if len(pname) > 25 else '')
        projects_html += f"""
        <div class="bar-row">
            <div class="bar-name" style="width:160px" title="{pname}">{short}</div>
            <div class="bar-track"><div class="bar-fill" style="width:{w}%;background:linear-gradient(90deg,#283593,#5c6bc0)">{phours:.1f}h</div></div>
        </div>"""
    projects_html += "\n    </div>\n</div>"

    # ---- 5. 文档统计 ----
    docs_html = f"""
<div class="card" id="docs">
    <h2>📄 文档编写统计</h2>
    <p style="color:#888;font-size:13px;margin-bottom:12px;">共发布 {s['total_articles']} 篇技术文档</p>
    <table class="doc-table">
        <tr><th>作者</th><th>文档数</th><th>文档列表</th></tr>"""
    if article_authors:
        for author, cnt in sorted(article_authors.items(), key=lambda x: -x[1]):
            titles = [a['title'] for a in article_list if a['author'] == author]
            titles_str = ', '.join(f'《{t}》' for t in titles)
            docs_html += f"""
        <tr>
            <td>{author}</td>
            <td class="text-center"><span style="background:#e8f5e9;color:#2e7d32;padding:2px 10px;border-radius:10px;font-weight:600">{cnt}</span></td>
            <td style="font-size:12px;">{titles_str}</td>
        </tr>"""
    else:
        docs_html += '<tr><td colspan="3" class="text-center" style="color:#999">本期无新增文档</td></tr>'
    docs_html += "\n    </table>\n</div>"

    # ---- 6. 报工质量 ----
    avg_review = round(s['total_records'] / member_count, 1) if member_count > 0 else 0

    quality_html = f"""
<div class="card" id="quality">
    <h2>✅ 报工质量分析</h2>

    <div class="cost-grid" style="margin-bottom:20px;">
        <div class="cost-card">
            <div class="cost-label">平均操作标准分</div>
            <div class="cost-value" style="color:{'#27ae60' if s['avg_opScore']>=80 else '#e74c3c'}">{s['avg_opScore']:.1f}</div>
        </div>
        <div class="cost-card">
            <div class="cost-label">平均审批通过率</div>
            <div class="cost-value" style="color:#1565c0">{avg_review}</div>
        </div>
        <div class="cost-card">
            <div class="cost-label">总报工记录</div>
            <div class="cost-value" style="color:#1565c0">{s['total_records']}</div>
        </div>
        <div class="cost-card">
            <div class="cost-label">人均记录数</div>
            <div class="cost-value" style="color:#6a1b9a">{avg_review}</div>
        </div>
    </div>

    <h3>人员质量明细</h3>
    <div style="overflow-x:auto;">
    <table>
        <tr><th>姓名</th><th class="text-right">操作标准分</th><th class="text-right">审批通过率</th><th class="text-right">记录数</th><th class="text-right">通过数</th><th class="text-right">知识库</th><th class="text-right">证书</th></tr>"""
    for name, m in members:
        score = m.get('opScore', 0)
        review_r = m.get('reviewRate', 0)
        quality_html += f"""
        <tr>
            <td>{name}</td>
            <td class="text-right"><span style="color:{rate_color(score)};font-weight:600">{score}</span></td>
            <td class="text-right"><span style="color:{rate_color(review_r)}">{review_r:.1f}%</span></td>
            <td class="text-right">{m['totalRecords']}</td>
            <td class="text-right">{m.get('approvedRecords', 0)}</td>
            <td class="text-right">{m.get('knowledgeCount', 0)}</td>
            <td class="text-right">{m.get('certCount', 0)}</td>
        </tr>"""
    quality_html += "\n    </table>\n    </div>\n</div>"

    # ---- 7. 人员工作总结 ----
    summary_persons = members if person_filter is None else [(n, m) for n, m in members if n == person_filter]

    summaries_html = f"""
<div class="card" id="summaries">
    <h2>📝 每人工作总结</h2>
    <p style="color:#888;font-size:13px;margin-bottom:16px;">基于 {meta['date_start']}~{meta['date_end']} 报工内容智能分析，包含核心工作领域、工作亮点、重点项目、待改进方向</p>"""

    for name, m in summary_persons:
        th = m['totalHours']
        rate = round(th / standard_total * 100, 1) if standard_total > 0 else 0
        weekend = person_weekend.get(name, 0)
        remarks_data = person_remarks.get(name, [])
        projects = sorted(person_project.get(name, {}).items(), key=lambda x: -x[1])[:8]
        monthly = person_monthly.get(name, {})

        # 月度工时条形图
        month_bars = ''
        for mname, mdates in month_groups:
            mkey = month_key_map.get(mname, '')
            mh = monthly.get(mkey, 0)
            std_m = month_standards.get(mname, 176)
            pct = min(round(mh / std_m * 100, 1), 100) if std_m > 0 else 0
            bar_color = '#27ae60' if pct >= 95 else ('#f39c12' if pct >= 80 else '#e74c3c')
            month_bars += f"""
        <div class="month-block">
            <span class="month-label">{mname}</span>
            <span class="month-value">{mh:.1f}h</span>
            <div class="month-bar" style="width:{pct}%;background:{bar_color}"></div>
        </div>"""

        # 工时缺口/达标
        if th >= standard_total - 0.01:
            status = f'<div class="full-badge">✅ 工时达标</div>'
        else:
            shortage_h = standard_total - th
            status = f'<div class="shortage-warning">⚠️ 工时缺口: {shortage_h:.1f}h（需关注日常报工完整性）</div>'

        # 项目标签
        proj_html = ''
        if projects:
            proj_html = '<div class="project-list"><b>参与项目:</b> '
            proj_html += ', '.join(f'{pn}({ph:.0f}h)' for pn, ph in projects)
            if len(projects) > 8:
                proj_html += f' 等{len(person_project.get(name, {}))}个项目'
            proj_html += '</div>'

        # 文档
        doc_html = ''
        person_articles = [a['title'] for a in article_list if a['author'] == name]
        if person_articles:
            doc_html = '<div class="article-list"><b>发布文档:</b> '
            doc_html += ', '.join(f'《{t}》' for t in person_articles)
            doc_html += '</div>'

        # 智能工作总结
        ai_summary_text = generate_person_summary_text(name, m, person_categories, person_project, rate, standard_total, article_list)
        ai_summary_html = ''
        if ai_summary_text:
            ai_summary_html = '<div style="margin-top:10px;padding:12px;background:#f5f7ff;border-radius:8px;border-left:3px solid #283593;font-size:13px;line-height:1.8;color:#374151">'
            for line in ai_summary_text.split('\n'):
                if line.strip():
                    ai_summary_html += f'<div>{line}</div>'
            ai_summary_html += '</div>'

        # 工作类型分布（可视化标签）
        categories = person_categories.get(name, {})
        cat_html = ''
        if categories:
            sorted_cats = sorted(categories.items(), key=lambda x: x[1]['hours'], reverse=True)
            cat_colors = {
                '驻场服务': '#1565c0', '故障处理': '#c62828', '维保巡检': '#2e7d32',
                '安装部署': '#e65100', '售前支持': '#6a1b9a', '培训文档': '#00838f',
                '性能优化': '#ad1457', '备份容灾': '#4527a0', '数据管理': '#00695c',
                '其他工作': '#546e7a',
            }
            cat_html = '<div style="margin-top:8px"><b style="font-size:12px;color:#374151">工作类型分布:</b></div><div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">'
            for cat, info in sorted_cats[:6]:
                bg = cat_colors.get(cat, '#78909c')
                cat_html += f'<span style="background:{bg};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;">{cat} {info["hours"]:.0f}h/{info["count"]}次</span>'
            cat_html += '</div>'

        # 🆕 姓名后置「合同名／实施计划」标签（accId 精确关联合同，按工时降序去重）
        _acc_meta = person_acc_meta.get(name, {})
        if projects:
            pc_html = '<div class="person-contracts"><span class="pc-label">支持项目/合同：</span>' + \
                      ''.join(pc_tag_html(pn, _acc_meta.get(pn)) for pn, _ in projects) + '</div>'
        else:
            pc_html = '<div class="person-contracts"><span class="pc-label">支持项目/合同：</span><span class="pc-empty">本期报工无关联项目</span></div>'

        summaries_html += f"""
<div class="person-summary" id="person-{name}">
    <h4>{name}</h4>
    {pc_html}
    <div class="summary-stats">
        <span class="stat-item">总工时 <b>{th:.1f}h</b></span>
        <span class="stat-item">达标率 <b style="color:{rate_color(rate)}">{rate}%</b></span>
        <span class="stat-item">售后 <b>{m['afterHours']}h</b></span>
        <span class="stat-item">加班 <b>{m['overHours']}h</b></span>
        <span class="stat-item">内部 <b>{m['internalHours']}h</b></span>
        <span class="stat-item">周末加班 <b>{weekend:.1f}h</b></span>
        <span class="stat-item">记录 <b>{m['totalRecords']}条</b></span>
        <span class="stat-item">操作分 <b style="color:{rate_color(m['opScore'])}">{m['opScore']}</b></span>
    </div>
    <div class="monthly-bar">{month_bars}</div>
    {status}
    {proj_html}
    {doc_html}
    {cat_html}
    {ai_summary_html}
</div>"""

    summaries_html += "\n</div>"

    # ---- 8. 综合评价 ----
    top_name = members[0][0] if members else ''
    top_hours = members[0][1]['totalHours'] if members else 0
    bottom_name = members[-1][0] if members else ''
    bottom_hours = members[-1][1]['totalHours'] if members else 0
    bottom_rate = round(bottom_hours / standard_total * 100, 1) if standard_total > 0 else 0

    eval_html = f"""
<div class="eval-section" id="eval">
    <h2>🏆 综合评价</h2>

    <div class="eval-item">
        <div class="eval-title">📊 整体概况</div>
        <p>{tname} {meta['date_start']}~{meta['date_end']} 共 {member_count} 人，总工时 {s['total_hours']:,.1f}h，人均 {avg_hours}h。满勤率 {full_rate}%（{full_count}/{member_count}人达标）。加班工时合计 {s['total_ot']}h，文档产出 {s['total_articles']} 篇。</p>
    </div>

    <div class="eval-item">
        <div class="eval-title">🥇 工时冠军</div>
        <p>{top_name} 以 {top_hours}h 工时排名第一，达标率 {round(top_hours/standard_total*100,1)}%。</p>
    </div>

    <div class="eval-item">
        <div class="eval-title">⏰ 加班关注</div>
        <p>加班最多的成员：{'、'.join(f'{n}({person_weekend.get(n,0):.0f}h)' for n, m in sorted(members, key=lambda x: -person_weekend.get(x[0],0))[:3])}。请核实加班是否合理分配。</p>
    </div>"""

    if shortage_members:
        eval_html += f"""
    <div class="eval-item">
        <div class="eval-title">⚠️ 工时关注</div>
        <p>{shortage_members[0]['name']} 存在最大工时缺口 {shortage_members[0]['total_shortage']:.1f}h（达标率 {round(shortage_members[0]['total_hours']/standard_total*100,1)}%，缺勤{shortage_members[0]['shortage_days_count']}天），建议关注报工习惯，确保工作日满 8h 记录。</p>
    </div>"""

    eval_html += f"""
    <div class="eval-item">
        <div class="eval-title">📌 管理建议</div>
        <p>1. 整体满勤率 {full_rate}%，{'表现优秀，继续保持。' if full_rate >= 80 else '部分人员未达标准工时，建议加强报工提醒。'}<br>
        2. 加班工时合计 {s['total_ot']}h，请关注加班合理性，避免过度疲劳。<br>
        3. 文档产出 {s['total_articles']} 篇，建议鼓励更多技术沉淀和知识共享。<br>
        4. 操作标准分整体良好（均分{s['avg_opScore']:.1f}），继续保持报工规范性。</p>
    </div>
</div>"""

    # ---- 页脚 ----
    footer_html = f"""
<div style="text-align:center;font-size:12px;color:#9ca3af;padding:20px">
    本报告由自动化任务生成 · {report_time} · 东西大区 {mode_label} 报工分析系统
</div>"""

    # ---- 组装 ----
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{tname} {meta['date_start']}~{meta['date_end']} 报工综合分析报告</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
{header_html}
{nav_html}
{kpi_html}
{ranking_html}
{shortage_html}
{cost_html}
{projects_html}
{docs_html}
{quality_html}
{summaries_html}
{eval_html}
{footer_html}
</div>
</body>
</html>"""

    return html


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成单团队/单人员深度分析 HTML 报告')
    parser.add_argument('--input', default='/tmp/mes_analysis_result.json', help='分析结果 JSON 文件路径')
    parser.add_argument('--output', required=True, help='输出的 HTML 文件路径')
    parser.add_argument('--person', default=None, help='指定单人员姓名（只输出该人员的工作总结）')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html = generate_report(data, person_filter=args.person)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)

    person_label = f'（{args.person}）' if args.person else ''
    print(f"HTML 报告已生成：{args.output}（{len(html)} 字符）{person_label}")
