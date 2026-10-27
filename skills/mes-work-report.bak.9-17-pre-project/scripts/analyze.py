#!/usr/bin/env python3
"""
东西大区四团队报工数据分析脚本
用法：python3 analyze.py --mode week|month --date 2026-04-17 --exclude "张三,李四" --tmpdir /tmp
输出：/tmp/mes_analysis_result.json
"""

import json
import argparse
import os
import re
from collections import defaultdict
from datetime import date, timedelta, datetime

# ==================== 默认配置 ====================
DEFAULT_TEAMS = [
    {'id': 't2',  'name': '东西大区1部'},
    {'id': 't3',  'name': '东西大区2部'},
    {'id': 't23', 'name': '东西大区4部'},
    {'id': 't19', 'name': '东西大区5部'},
]

TEAM_COLORS = {'t2': '#3b82f6', 't3': '#10b981', 't23': '#f59e0b', 't19': '#ef4444'}

WEEKDAY_CN = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

STANDARD_DAILY = 8.0

def parse_excluded(exclude_str):
    """解析排除人员名单"""
    if not exclude_str:
        return set()
    return {n.strip() for n in exclude_str.replace('，', ',').split(',') if n.strip()}

def get_date_range(mode, target_date):
    """
    根据模式（week/month）和目标日期计算统计范围
    week: 取目标日期所在周的周一到周五
    month: 取目标日期所在月的第1天到最后一天
    """
    if mode == 'month':
        start = target_date.replace(day=1)
        # 计算该月所有工作日（周一到周五）
        dates = []
        d = start
        while d.month == target_date.month:
            if d.weekday() < 5:  # 周一到周五
                dates.append(d)
            d += timedelta(days=1)
        end = dates[-1] if dates else start
        standard_total = len(dates) * STANDARD_DAILY
        return start, end, dates, standard_total
    else:
        # week: 周一到周五
        weekday = target_date.weekday()
        monday = target_date - timedelta(days=weekday)
        friday = monday + timedelta(days=4)
        dates = [monday + timedelta(days=i) for i in range(5)]
        standard_total = 5 * STANDARD_DAILY
        return monday, friday, dates, standard_total

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ==================== 数据解析 ====================

def parse_summary(data, excluded):
    """解析 summary JSON（operateCallBackObj 列表，字段单位=小时）"""
    result = {}
    items = data.get('operateCallBackObj', [])
    if not isinstance(items, list):
        items = []
    for item in items:
        name = item.get('userName', '') or ''
        if not name or name in excluded:
            continue
        result[name] = {
            'totalHours':    item.get('totalTaskTime', 0) or 0,
            'preHours':      item.get('preTaskTime', 0) or 0,
            'afterHours':    item.get('afterTaskTime', 0) or 0,
            'internalHours': item.get('internalTaskTime', 0) or 0,
            'overHours':     item.get('overTaskTime', 0) or 0,
            'certCount':     item.get('certCount', 0) or 0,
            'docCount':      item.get('docCount', 0) or 0,
            'opScore':       item.get('operationStandardScore', 0) or 0,
            'groupType':     item.get('groupType', ''),
            'reviewRate':    0.0,
            'totalRecords':  0,
            'approvedRecords': 0,
        }
    return result

def parse_list(data, excluded, week_start, week_end):
    """解析 list JSON（顶层 list 字段，taskTime 单位=小时）"""
    person_day = defaultdict(lambda: defaultdict(float))
    approved_map = defaultdict(int)
    total_map = defaultdict(int)
    hours_map = defaultdict(float)  # 每个人的实际工时汇总

    items = data.get('list', [])
    ws = week_start.strftime('%Y-%m-%d')
    we = week_end.strftime('%Y-%m-%d')

    for item in items:
        name = item.get('executorName', '') or ''
        if not name or name in excluded:
            continue
        start = item.get('start', '') or ''
        hours = item.get('taskTime', 0) or 0
        day = start[:10] if len(start) >= 10 else ''
        if day and ws <= day <= we:
            person_day[name][day] += hours
            hours_map[name] += hours
        total_map[name] += 1
        review = item.get('reviewStatus', '')
        if str(review) in ('1', 'APPROVED', 'PASS', 'approved', 'pass'):
            approved_map[name] += 1

    return dict(person_day), dict(approved_map), dict(total_map), dict(hours_map)

def parse_articles(data, excluded):
    """解析 article JSON"""
    items = data.get('list', [])
    authors = defaultdict(int)
    articles = []
    for item in items:
        author = (item.get('account', '') or item.get('employeeName', '')
                  or item.get('creatorName', '') or '')
        if author and author not in excluded:
            authors[author] += 1
            articles.append({'author': author, 'title': (item.get('title') or '')[:60]})
    return dict(authors), articles

def parse_daily_work(data, excluded, week_start, week_end):
    """
    解析每人每天的报工内容明细
    返回: {name: {date: [{'remark': str, 'hours': float, 'accName': str, 'start': str, 'end': str}]}}
    """
    daily_work = defaultdict(lambda: defaultdict(list))
    
    items = data.get('list', [])
    ws = week_start.strftime('%Y-%m-%d')
    we = week_end.strftime('%Y-%m-%d')
    
    for item in items:
        name = item.get('executorName', '') or ''
        if not name or name in excluded:
            continue
        start = item.get('start', '') or ''
        day = start[:10] if len(start) >= 10 else ''
        if day and ws <= day <= we:
            remark = (item.get('remark', '') or '').strip()
            # 不过滤没有 remark 的记录，在显示时再过滤
            daily_work[name][day].append({
                'remark': remark,
                'hours': item.get('taskTime', 0) or 0,
                'accName': item.get('accName', '') or '',
                # 🆕 合同关联字段：accId == 合同子项 itemId，用于精确解析合同名
                'accId': str(item.get('accId', '') or ''),
                'companyName': item.get('companyName', '') or '',
                'start': start,
                'end': item.get('end', '') or '',
            })
    
    return dict(daily_work)

def parse_service_requests(tmpdir, date_start, date_end, excluded, team_keywords=None, member_team_ids=None):
    """
    解析服务请求数据（全局数据，默认按团队名称过滤东西大区）

    team_keywords:   团队名称关键词列表，默认 ['东西大区']
    member_team_ids: 团队成员白名单 team-id（如 ['t25','t11']，带 t 前缀）。
                     传入后启用「处理人/提交人 ∈ 成员名单」并集过滤 —— 用于自定义团队
                     SR 归属（SR.teamName 常挂在部门/维保团队名下，仅按关键词会漏数）

    返回: list of service request dicts（legacy 字段，供 generate_report.py）
    """
    import os

    # 团队名称关键词（默认东西大区）
    sr_keywords = team_keywords if team_keywords else ['东西大区']

    # 成员白名单（可选）：从各团队 summary 提取中文姓名
    member_names = set()
    if member_team_ids:
        for tid in member_team_ids:
            sf = os.path.join(tmpdir, f'mes_summary_{tid}.json')
            try:
                with open(sf, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                for o in (d.get('operateCallBackObj') or []):
                    n = (o.get('userName') or '')
                    if n:
                        member_names.add(n)
            except Exception:
                pass
    
    all_requests = []
    
    # 读取所有团队的服务请求文件（去重）
    seen_ids = set()
    
    # 优先读取全局服务请求文件（mes 0.5.3+ sr list 不支持 --team-id）
    global_sr = os.path.join(tmpdir, 'mes_service_requests.json')
    sr_files = []
    if os.path.exists(global_sr):
        sr_files.append(global_sr)
    else:
        for tid in ['t2', 't3', 't23', 't19']:
            sr_file = os.path.join(tmpdir, f'mes_service_{tid}.json')
            if os.path.exists(sr_file):
                sr_files.append(sr_file)
    
    for sr_file in sr_files:
        
        try:
            with open(sr_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            continue
        
        items = data.get('list', []) or data.get('data', {}).get('list', []) or []
        
        for item in items:
            sr_id = item.get('id')
            if sr_id in seen_ids:
                continue
            seen_ids.add(sr_id)
            
            # 归属过滤：团队名称关键词 OR（启用时）处理人/提交人 ∈ 成员白名单
            team_name = item.get('teamName', '') or ''
            sub_team_name = item.get('subTeamName', '') or ''
            handler_raw = item.get('executorEmployeeName', '') or item.get('executorName', '') or item.get('subExecutorName', '') or ''
            submitter = item.get('createdByName', '') or item.get('employeeName', '') or ''
            in_team_kw = any(kw in team_name for kw in sr_keywords) or any(kw in sub_team_name for kw in sr_keywords)
            in_members = bool(member_names) and (handler_raw in member_names or submitter in member_names)
            if not (in_team_kw or in_members):
                continue

            if submitter and submitter in excluded:
                continue
            
            # 状态码映射
            status_map = {0: '已提交', 1: '处理中', 2: '已关闭', 3: '已归档', 4: '待反馈', 5: '已恢复'}
            raw_status = item.get('status', None)
            status_text = status_map.get(raw_status, str(raw_status)) if isinstance(raw_status, int) else item.get('statusDesc', '') or '未知'
            
            # 从 typeLabel 中提取级别前缀（P0~P4等）
            type_label = item.get('typeLabel', '') or ''
            level = ''
            if type_label:
                # typeLabel 格式: "P4-咨询，业务暂未受影响"
                parts = type_label.split('-')
                if parts and parts[0].strip().upper().startswith('P'):
                    level = parts[0].strip().upper()
            
            # 处理人优先用中文名（executorEmployeeName），其次 executorName
            handler = item.get('executorEmployeeName', '') or item.get('executorName', '') or item.get('subExecutorName', '') or ''
            
            all_requests.append({
                'id': sr_id,
                'title': item.get('title', '') or '',
                'status': status_text,
                'level': level,
                'type_label': type_label,
                'submitter': submitter,
                'handler': handler,
                'company': item.get('companyName', '') or item.get('accName', '') or '',
                'submitTime': item.get('createdTime', '') or '',
                'team': team_name or sub_team_name,
                'description': (item.get('content', '') or '')[:200],
            })
    
    return all_requests

def analyze_shortage(person_day_map, total_hours, date_list, standard_total):
    """分析报工不足情况"""
    date_strs = [d.strftime('%Y-%m-%d') for d in date_list]
    date_set = set(date_strs)
    shortage_days = []
    total_shortage = 0.0
    for d in date_strs:
        actual = person_day_map.get(d, 0.0)
        if actual < STANDARD_DAILY - 0.01:
            shortage = STANDARD_DAILY - actual
            shortage_days.append({'date': d, 'actual': round(actual, 2), 'shortage': round(shortage, 2)})
            total_shortage += shortage
    ws = date_strs[0] if date_strs else ''
    weekend_hours = sum(v for k, v in person_day_map.items()
                        if k not in date_set and k >= ws)
    return {
        'shortage_days': shortage_days,
        'total_shortage': round(total_shortage, 2),
        'weekend_hours': round(weekend_hours, 2),
        'total_hours': round(total_hours, 2),
    }

def dedict(obj):
    """递归转换 defaultdict 为普通 dict"""
    if isinstance(obj, defaultdict):
        return {k: dedict(v) for k, v in obj.items()}
    if isinstance(obj, dict):
        return {k: dedict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [dedict(i) for i in obj]
    return obj

# ==================== 主流程 ====================

def run_analysis(mode, target_date_str, exclude_str, teams_config, tmpdir,
                 sr_keywords=None, sr_member_team_ids=None):
    """
    执行完整分析流程
    
    参数:
        mode: 'week' 或 'month'
        target_date_str: 目标日期 'YYYY-MM-DD'
        exclude_str: 排除人员，逗号分隔
        teams_config: 团队配置列表，每个元素 {'id': str, 'name': str}
        tmpdir: 临时文件目录
        sr_keywords: 服务请求团队名称关键词（默认 ['东西大区']）
        sr_member_team_ids: 服务请求成员白名单 team-id（可选，自定义团队用）
    
    返回:
        (all_teams_data, meta_info)
    """
    target_date = date.fromisoformat(target_date_str)
    excluded = parse_excluded(exclude_str)

    week_start, week_end, date_list, standard_total = get_date_range(mode, target_date)
    date_strs = [d.strftime('%Y-%m-%d') for d in date_list]

    all_teams_data = {}

    for team in teams_config:
        tid = team['id']
        tname = team['name']

        summary_file = os.path.join(tmpdir, f'mes_summary_{tid}.json')
        list_file = os.path.join(tmpdir, f'mes_list_{tid}.json')
        article_file = os.path.join(tmpdir, f'mes_article_{tid}.json')

        summary_raw = load_json(summary_file)
        list_raw = load_json(list_file)
        article_raw = load_json(article_file)

        summary = parse_summary(summary_raw, excluded)
        person_day, approved_map, total_map, hours_map = parse_list(list_raw, excluded, week_start, week_end)
        article_authors, article_list = parse_articles(article_raw, excluded)
        daily_work = parse_daily_work(list_raw, excluded, week_start, week_end)

        # ⚠️ 重要：summary 接口返回的工时经常不准确（只统计部分数据），
        # 必须用 list 接口实际报工记录汇总的工时来覆盖
        for name in summary:
            actual_hours = hours_map.get(name, 0)
            if actual_hours > 0:
                old_total = summary[name]['totalHours']
                summary[name]['totalHours'] = round(actual_hours, 1)
                
                # 如果 summary 的 totalHours 与 list 不一致，按比例缩放分类工时
                if old_total > 0 and abs(old_total - actual_hours) > 0.01:
                    scale = actual_hours / old_total
                    summary[name]['preHours'] = round(summary[name]['preHours'] * scale, 1)
                    summary[name]['afterHours'] = round(summary[name]['afterHours'] * scale, 1)
                    summary[name]['internalHours'] = round(summary[name]['internalHours'] * scale, 1)
                    summary[name]['overHours'] = round(summary[name]['overHours'] * scale, 1)
            
            tot = total_map.get(name, 0)
            appr = approved_map.get(name, 0)
            summary[name]['reviewRate'] = round(appr / tot * 100, 1) if tot > 0 else 0.0
            summary[name]['totalRecords'] = tot
            summary[name]['approvedRecords'] = appr

        shortage_list = []
        for name in summary:
            pday = dict(person_day.get(name, {}))
            th = summary[name]['totalHours']
            info = analyze_shortage(pday, th, date_list, standard_total)
            if info['total_shortage'] > 0 or th < standard_total - 0.01:
                shortage_list.append({'name': name, **info, 'person_day': pday})
        shortage_list.sort(key=lambda x: x['total_shortage'], reverse=True)

        total_hours = sum(v['totalHours'] for v in summary.values())
        member_count = len(summary)
        avg_hours = round(total_hours / member_count, 2) if member_count > 0 else 0
        total_articles = sum(article_authors.values())
        
        # 计算已过工作日（到今天为止的工作日数）
        from datetime import datetime as dt
        today_str = dt.now().strftime('%Y-%m-%d')
        passed_work_days = sum(1 for d in date_strs if d <= today_str)
        passed_standard = passed_work_days * STANDARD_DAILY
        
        full_reporters = sum(1 for v in summary.values() if v['totalHours'] >= passed_standard - 0.01)

        all_teams_data[tid] = {
            'name': tname,
            'summary': summary,
            'person_day': person_day,
            'daily_work': daily_work,
            'article_authors': article_authors,
            'article_list': article_list,
            'shortage_list': shortage_list,
            'stats': {
                'member_count': member_count,
                'total_hours': round(total_hours, 2),
                'avg_hours': avg_hours,
                'total_articles': total_articles,
                'full_reporters': full_reporters,
                'compliance_rate': round(full_reporters / member_count * 100, 1) if member_count > 0 else 0,
                'total_ot': round(sum(v['overHours'] for v in summary.values()), 1),
                'total_pre': round(sum(v['preHours'] for v in summary.values()), 1),
                'total_after': round(sum(v['afterHours'] for v in summary.values()), 1),
                'total_internal': round(sum(v['internalHours'] for v in summary.values()), 1),
                'total_records': sum(v['totalRecords'] for v in summary.values()),
                'avg_opScore': round(sum(v['opScore'] for v in summary.values()) / member_count, 1) if member_count > 0 else 0,
            }
        }

    # 解析服务请求（全局数据，只解析一次）
    service_requests = parse_service_requests(tmpdir, week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d'), excluded,
                                              team_keywords=sr_keywords, member_team_ids=sr_member_team_ids)
    
    # 解析项目报工排名（从 list 数据中提取）
    project_ranking = {}  # {tid: [(project_name, hours), ...]}
    for team in teams_config:
        tid = team['id']
        list_file = os.path.join(tmpdir, f'mes_list_{tid}.json')
        if os.path.exists(list_file):
            try:
                with open(list_file, 'r', encoding='utf-8') as f:
                    list_raw = json.load(f)
                project_hours = defaultdict(float)
                for item in list_raw.get('list', []):
                    name = item.get('executorName', '') or ''
                    if not name or name in excluded:
                        continue
                    acc_name = item.get('accName', '') or ''
                    hours = item.get('taskTime', 0) or 0
                    if acc_name:
                        project_hours[acc_name] += hours
                project_ranking[tid] = sorted(project_hours.items(), key=lambda x: -x[1])
            except:
                project_ranking[tid] = []
        else:
            project_ranking[tid] = []
    
    meta = {
        'mode': mode,
        'date_start': week_start.strftime('%Y-%m-%d'),
        'date_end': week_end.strftime('%Y-%m-%d'),
        'date_strs': date_strs,
        'standard_total': standard_total,
        'work_days': len(date_list),
        'excluded': list(excluded),
        'target_date': target_date_str,
        'report_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
    
    # 将服务请求和项目排名添加到第一个团队（全局数据）
    if all_teams_data:
        first_tid = list(all_teams_data.keys())[0]
        all_teams_data[first_tid]['service_requests'] = service_requests
    
    # 将项目排名添加到各团队
    for tid, ranking in project_ranking.items():
        if tid in all_teams_data:
            all_teams_data[tid]['project_ranking'] = ranking

    return dedict(all_teams_data), meta


def build_result(all_teams_data, meta, teams_config):
    """
    将分析结果组装为标准输出 JSON，SR 双写以同时兼容两个生成器：
      - generate_report.py（周/月报）        → teams[first]['service_requests']（legacy 字段 company/handler/submitTime）
      - generate_quarter_report.py（长周期） → result['service_requests']（字段 company_name/executor/created_time）
    修复：此前季度/长周期报告 SR 章节因读取顶层字段而恒为空。
    """
    result = {'meta': meta, 'teams': all_teams_data, 'teams_config': teams_config}
    if all_teams_data:
        first_tid = list(all_teams_data.keys())[0]
        legacy = all_teams_data[first_tid].get('service_requests', [])
        result['service_requests'] = [
            {
                'id': sr.get('id', ''),
                'title': sr.get('title', '') or '',
                'status': sr.get('status', '') or '',
                'level': sr.get('level', '') or '',
                'company_name': sr.get('company', '') or '',
                'executor': sr.get('handler', '') or '',
                'created_time': sr.get('submitTime', '') or '',
            }
            for sr in legacy
        ]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='东西大区四团队报工数据分析')
    parser.add_argument('--mode', choices=['week', 'month'], default='week', help='周报或月报')
    parser.add_argument('--date', default=date.today().isoformat(), help='目标日期 YYYY-MM-DD')
    parser.add_argument('--exclude', default='许文榕,杨明翰,周瑞斌', help='排除人员，逗号分隔')
    parser.add_argument('--tmpdir', default='/tmp', help='临时文件目录')
    parser.add_argument('--output', default='/tmp/mes_analysis_result.json', help='输出 JSON 路径')
    args = parser.parse_args()

    all_teams_data, meta = run_analysis(args.mode, args.date, args.exclude, DEFAULT_TEAMS, args.tmpdir)

    result = build_result(all_teams_data, meta, DEFAULT_TEAMS)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"分析完成，结果已保存至 {args.output}")
    print(f"模式: {meta['mode']}, 范围: {meta['date_start']} ~ {meta['date_end']}, 工作日: {meta['work_days']}天")
