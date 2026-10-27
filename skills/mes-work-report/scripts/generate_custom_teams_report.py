#!/usr/bin/env python3
"""
自定义团队报工分析一键 CLI（mes_dongxi_weekly_report 技能扩展）

背景：analyze.py / generate_*.py 面向「东西大区四团队」硬编码团队 id 与文案。
本脚本支持任意团队组合（如 南北大区服务2/4/5部、电信行业服务部）的任意日期范围，
自动完成：采集 → 分析 → 未报工子项 → HTML 渲染，输出与季度报告同款 12 章节报告。

用法示例（南北·电信四团队，2026年8月）：
  python3 generate_custom_teams_report.py \\
    --teams "南北大区服务2部:25,南北大区服务4部:11,南北大区服务5部:22,电信行业服务部:7293" \\
    --from 2026-08-01 --to 2026-08-31 \\
    --label "南北·电信四团队" \\
    --sr-keywords "南北大区,电信行业服务部" \\
    --output /path/to/report.html

参数说明：
  --teams        团队列表 "显示名:teamId,..."（必填；teamId 可用 `mes dashboard team` 查询）
  --from/--to    统计起止日期 YYYY-MM-DD
  --label        报告标题/页脚团队简称（缺省自动从 --teams 生成）
  --sr-keywords  服务请求团队名称关键词（默认取 label；传 "东西大区" 保留官方语义）
  --sr-member    追加「处理人/提交人 ∈ 四团队名单」并集过滤（默认开启；SR.teamName 常挂在
                 部门/维保团队名下，仅关键词会漏数。--no-sr-member 关闭）
  --exclude      排除人员，逗号分隔（默认空）
  --skip-sr      跳过服务请求采集与章节
  --skip-unreported  跳过未报工子项采集（第十节显示"无"）
  --tmpdir       临时目录（默认 /tmp）
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime, timedelta

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)

import analyze as A  # noqa: E402

STANDARD_DAILY = 8.0

# ----------------------------------------------------------------------------
# 采集
# ----------------------------------------------------------------------------

def mes_json(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def collect_data(teams, d0, d1, tmpdir, skip_sr=False):
    """采集各团队 summary/list/article + 全局 SR → tmpdir/mes_*.json"""
    ok = True
    for team in teams:
        tid = team['id'].lstrip('t')          # 真实 team id（无 t 前缀）
        tkey = team['id']                     # 文件名用 t 前缀
        for kind, cmd in [
            ('summary', f'mes -o json statistics summary --from {d0} --to {d1} --team-id {tid}'),
            ('list', f'mes -o json statistics list --from {d0} --to {d1} --team-id {tid} --page-size 2000'),
            ('article', f'mes -o json article list --mode manage --team-id {tid} '
                        f'--start-time "{d0} 00:00:00" --end-time "{d1} 23:59:59" --page-size 100'),
        ]:
            path = os.path.join(tmpdir, f'mes_{kind}_{tkey}.json')
            data = mes_json(cmd)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            size = os.path.getsize(path)
            flag = 'OK ' if size > 200 else 'WARN'
            print(f'  [{flag}] {team["name"]} {kind}: {size}B')
            if size < 200:
                ok = False

    if not skip_sr:
        gsr = os.path.join(tmpdir, 'mes_service_requests.json')
        data = mes_json(f'mes -o json sr list --start-time "{d0} 00:00:00" '
                        f'--end-time "{d1} 23:59:59" --page-size 500')
        with open(gsr, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print(f'  [SR] 全局服务请求: {os.path.getsize(gsr)}B')
    return ok


# ----------------------------------------------------------------------------
# 分析（自定义团队 + 任意日期范围；复用 analyze.py 解析函数）
# ----------------------------------------------------------------------------

def analyze_teams(teams_config, date_list, exclude_str, tmpdir, sr_keywords, sr_member_ids):
    excluded = A.parse_excluded(exclude_str)
    date_strs = [d.strftime('%Y-%m-%d') for d in date_list]
    standard_total = len(date_list) * STANDARD_DAILY
    ws, we = date_strs[0], date_strs[-1]
    today_str = datetime.now().strftime('%Y-%m-%d')

    all_teams_data = {}
    for team in teams_config:
        tid, tname = team['id'], team['name']
        summary_raw = A.load_json(os.path.join(tmpdir, f'mes_summary_{tid}.json'))
        list_raw = A.load_json(os.path.join(tmpdir, f'mes_list_{tid}.json'))
        article_raw = A.load_json(os.path.join(tmpdir, f'mes_article_{tid}.json'))

        summary = A.parse_summary(summary_raw, excluded)
        person_day, approved_map, total_map, hours_map = A.parse_list(
            list_raw, excluded,
            date.fromisoformat(ws), date.fromisoformat(we))
        article_authors, article_list = A.parse_articles(article_raw, excluded)
        daily_work = A.parse_daily_work(list_raw, excluded,
                                        date.fromisoformat(ws), date.fromisoformat(we))

        # list 汇总工时覆盖 summary（summary 常不准确）
        for name in summary:
            actual = hours_map.get(name, 0)
            if actual > 0:
                old = summary[name]['totalHours']
                summary[name]['totalHours'] = round(actual, 1)
                if old > 0 and abs(old - actual) > 0.01:
                    scale = actual / old
                    for k in ('preHours', 'afterHours', 'internalHours', 'overHours'):
                        summary[name][k] = round(summary[name][k] * scale, 1)
            tot, appr = total_map.get(name, 0), approved_map.get(name, 0)
            summary[name]['reviewRate'] = round(appr / tot * 100, 1) if tot else 0.0
            summary[name]['totalRecords'] = tot
            summary[name]['approvedRecords'] = appr

        shortage_list = []
        for name in summary:
            pday = dict(person_day.get(name, {}))
            th = summary[name]['totalHours']
            info = A.analyze_shortage(pday, th, date_list, standard_total)
            if info['total_shortage'] > 0 or th < standard_total - 0.01:
                shortage_list.append({'name': name, **info, 'person_day': pday})
        shortage_list.sort(key=lambda x: x['total_shortage'], reverse=True)

        total_hours = sum(v['totalHours'] for v in summary.values())
        member_count = len(summary)
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
                'avg_hours': round(total_hours / member_count, 2) if member_count else 0,
                'total_articles': sum(article_authors.values()),
                'full_reporters': full_reporters,
                'compliance_rate': round(full_reporters / member_count * 100, 1) if member_count else 0,
                'total_ot': round(sum(v['overHours'] for v in summary.values()), 1),
                'total_pre': round(sum(v['preHours'] for v in summary.values()), 1),
                'total_after': round(sum(v['afterHours'] for v in summary.values()), 1),
                'total_internal': round(sum(v['internalHours'] for v in summary.values()), 1),
                'total_records': sum(v['totalRecords'] for v in summary.values()),
                'avg_opScore': round(sum(v['opScore'] for v in summary.values()) / member_count, 1)
                               if member_count else 0,
            },
        }

    # 项目报工排名（按 accName 聚合）
    for team in teams_config:
        tid = team['id']
        lf = os.path.join(tmpdir, f'mes_list_{tid}.json')
        project_hours = defaultdict(float)
        if os.path.exists(lf):
            try:
                with open(lf, encoding='utf-8') as f:
                    lr = json.load(f)
                for item in lr.get('list', []):
                    name = item.get('executorName', '') or ''
                    if not name or name in excluded:
                        continue
                    acc = item.get('accName', '') or ''
                    if acc:
                        project_hours[acc] += item.get('taskTime', 0) or 0
            except Exception:
                pass
        all_teams_data[tid]['project_ranking'] = sorted(project_hours.items(), key=lambda x: -x[1])

    # 服务请求（全局一次）
    service_requests = []
    if os.path.exists(os.path.join(tmpdir, 'mes_service_requests.json')):
        service_requests = A.parse_service_requests(tmpdir, ws, we, excluded,
                                                    team_keywords=sr_keywords,
                                                    member_team_ids=sr_member_ids)
    if all_teams_data:
        first_tid = list(all_teams_data.keys())[0]
        all_teams_data[first_tid]['service_requests'] = service_requests

    meta = {
        'mode': 'month',
        'date_start': ws,
        'date_end': we,
        'date_strs': date_strs,
        'standard_total': standard_total,
        'work_days': len(date_list),
        'excluded': list(excluded),
        'target_date': ws,
        'report_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
    return A.dedict(all_teams_data), meta


# ----------------------------------------------------------------------------
# 未报工子项（第十节）
# ----------------------------------------------------------------------------

def collect_unreported(teams, tmpdir, team_kw_list, exclude_keywords=('已结束',)):
    """按 team-id 拉名下合同 → 未结束 & serviceTeams 含团队关键词 → 0 报工子项
    返回: 扁平 unreported_items（generate_quarter_report.py 期望格式）
    """
    if not team_kw_list:
        return []
    contracts = {}
    for team in teams:
        real = team['id'].lstrip('t')
        page = 1
        while True:
            d = mes_json(f'mes -o json contract list --team-id {real} --page {page}')
            lst = d.get('list') or []
            if not lst:
                break
            for c in lst:
                contracts[c.get('id')] = c
            if not d.get('hasNextPage'):
                break
            page += 1
            if page > 100:
                break
    today = date.today().isoformat()
    items_out = []
    for cid, c in contracts.items():
        end = c.get('contractEndTime') or c.get('endTime') or ''
        if not end or end < today:
            continue
        teams_str = '|'.join((t.get('name') or '') for t in (c.get('serviceTeams') or []))
        if not any(k in teams_str for k in team_kw_list):
            continue
        d = mes_json(f'mes -o json contract list-items --contract-id {cid}')
        sub = (d.get('operateCallBackObj') or {}).get('list') or []
        for it in sub:
            if (it.get('actualHours', 0) or 0) == 0:
                items_out.append({
                    'contract_name': c.get('name', ''),
                    'manager': c.get('manager') or '未指定',
                    'start_time': c.get('contractStartTime'),
                    'end_time': end,
                    'item_name': it.get('itemName', ''),
                    'item_type': it.get('itemType', ''),
                    'actual_hours': 0,
                    'plan_hour': it.get('planHour', 0) or 0,
                    'remaining_task': it.get('remainingTask', 0) or 0,
                })
    return items_out


# ----------------------------------------------------------------------------
# 渲染（动态定制 generate_quarter_report.py 后执行）
# ----------------------------------------------------------------------------

def render_report(result, label, out_path, tmpdir):
    colors = {}
    for i, team in enumerate(result['teams_config']):
        palette = ['#2563eb', '#059669', '#d97706', '#7c3aed', '#db2777', '#0891b2']
        colors[team['id']] = palette[i % len(palette)]

    src = open(os.path.join(SKILL_DIR, 'generate_quarter_report.py'), encoding='utf-8').read()

    old_default_teams = "DEFAULT_TEAMS = [\n    {'id': 't2',  'name': '东西大区1部'},\n    {'id': 't3',  'name': '东西大区2部'},\n    {'id': 't23', 'name': '东西大区4部'},\n    {'id': 't19', 'name': '东西大区5部'},\n]"
    new_default_teams = 'DEFAULT_TEAMS = ' + json.dumps(result['teams_config'], ensure_ascii=False)
    if old_default_teams in src:
        src = src.replace(old_default_teams, new_default_teams)

    # 配色
    m = re.search(r"TEAM_COLORS = \{[^}]*\}", src)
    if m:
        src = src.replace(m.group(0), 'TEAM_COLORS = ' + json.dumps(colors))

    # 文案替换
    repl = [
        # <h1>
        ("🏢 东西大区四团队 · ", f"🏢 {label} · "),
        # 页脚（{mode_label} 须保留为字面量，供生成器运行时插值）
        ("东西大区 {mode_label} 报工分析系统", label + " {mode_label} 报工分析系统"),
        # 未报工说明
        ("<p style=\"font-size:13px;color:#6b7280;margin-bottom:16px\">东西大区维保项目支持团队下，共发现",
         f"<p style=\"font-size:13px;color:#6b7280;margin-bottom:16px\">{label}名下维保合同下，共发现"),
        # 周期自适应：≤7天=周报（按日分组），≤45天=月报，更长=季度（保持默认）
        ("<title>东西大区四团队报工分析", f"<title>{label}报工分析"),
    ]

    # 根据统计跨度自适应分组粒度与措辞
    try:
        _m = result['meta']
        span_days = (date.fromisoformat(_m['date_end']) - date.fromisoformat(_m['date_start'])).days + 1
    except Exception:
        span_days = 90
    if span_days <= 7:
        repl += [
            ("二、成员工时明细（按月汇总）", "二、成员工时明细（按日汇总）"),
            ("八-A、每人季度工作总结", "八-A、每人本周工作总结"),
            ("季度工作内容：", "本周工作内容："),
        ]
        # 按日分组（每列一天，标准 8h）—— 替换生成器的按月分组
        src = src.replace("month_groups = get_month_groups(date_strs)",
                          "month_groups = [(d[5:], [d]) for d in date_strs]")
    elif span_days <= 45:
        repl += [
            ("八-A、每人季度工作总结", "八-A、每人每月工作总结"),
            ("季度工作内容：", "本月工作内容："),
        ]
    for old, new in repl:
        if old in src:
            src = src.replace(old, new)

    gen_py = os.path.join(tmpdir, 'gen_custom_report.py')
    with open(gen_py, 'w', encoding='utf-8') as f:
        f.write(src)
    # 🆕 渲染器在 tmpdir 运行，需同步合同映射模块，否则「实施计划→合同」精确解析降级失效
    try:
        import shutil
        shutil.copy(os.path.join(SKILL_DIR, 'build_contract_item_map.py'),
                    os.path.join(tmpdir, 'build_contract_item_map.py'))
    except Exception:
        pass

    r = subprocess.run(
        [sys.executable, gen_py, '--input', os.path.join(tmpdir, 'mes_analysis_custom.json'),
         '--output', out_path],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(f'渲染失败: {r.stderr[-800:]}')
    print(r.stdout.strip())


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='自定义团队报工分析（一键生成 12 章节 HTML 报告）')
    ap.add_argument('--teams', required=True, help='"显示名:teamId,显示名:teamId,..."（teamId 用 `mes dashboard team` 查询）')
    ap.add_argument('--from', dest='d0', required=True, help='起始日期 YYYY-MM-DD')
    ap.add_argument('--to', dest='d1', required=True, help='结束日期 YYYY-MM-DD')
    ap.add_argument('--label', default='', help='标题/页脚团队简称（缺省自动生成）')
    ap.add_argument('--sr-keywords', default='', help='SR 团队名称关键词，逗号分隔（缺省=label）')
    ap.add_argument('--no-sr-member', action='store_true', help='关闭 SR「成员名单并集」过滤')
    ap.add_argument('--exclude', default='', help='排除人员，逗号分隔')
    ap.add_argument('--skip-sr', action='store_true', help='跳过服务请求')
    ap.add_argument('--skip-unreported', action='store_true', help='跳过未报工子项采集')
    ap.add_argument('--tmpdir', default='/tmp', help='临时目录（默认 /tmp）')
    ap.add_argument('--output', required=True, help='输出 HTML 路径')
    args = ap.parse_args()

    teams = []
    for seg in args.teams.split(','):
        seg = seg.strip()
        if not seg:
            continue
        if ':' in seg:
            name, tid = seg.rsplit(':', 1)
        else:  # 只给 id
            name, tid = f'团队{tid}', seg
        teams.append({'id': f't{tid.lstrip("t")}', 'name': name.strip()})
    if not teams:
        sys.exit('--teams 不能为空')

    d0 = date.fromisoformat(args.d0)
    d1 = date.fromisoformat(args.d1)
    if d1 < d0:
        sys.exit('--to 不能早于 --from')

    label = args.label or teams[0]['name'] + (f'等{len(teams)}团队' if len(teams) > 1 else '')
    sr_keywords = [k.strip() for k in args.sr_keywords.split(',') if k.strip()] if args.sr_keywords \
        else ([label] if not args.skip_sr else [])
    sr_member_ids = None if args.no_sr_member else [t['id'] for t in teams]

    # 工作日列表
    date_list = []
    d = d0
    while d <= d1:
        if d.weekday() < 5:
            date_list.append(d)
        d += timedelta(days=1)
    print(f'统计范围: {d0} ~ {d1}，工作日 {len(date_list)} 天，标准 {len(date_list)*STANDARD_DAILY:.0f}h/人')

    print('Step 1/4 采集数据…')
    if not collect_data(teams, d0.isoformat(), d1.isoformat(), args.tmpdir, skip_sr=args.skip_sr):
        print('⚠️ 部分采集异常，请检查 mes 登录状态后重试')

    print('Step 2/4 分析…')
    all_teams, meta = analyze_teams(teams, date_list, args.exclude, args.tmpdir,
                                    sr_keywords if not args.skip_sr else None,
                                    sr_member_ids if not args.skip_sr else None)
    result = A.build_result(all_teams, meta, teams)
    for t in result['teams'].values():
        st = t['stats']
        print(f"  {t['name']}: {st['member_count']}人 总{st['total_hours']}h 均{st['avg_hours']}h "
              f"满勤{st['full_reporters']}人 文档{st['total_articles']} 记录{st['total_records']}条")

    print('Step 3/4 未报工子项采集…')
    result['unreported_items'] = [] if args.skip_unreported else \
        collect_unreported(teams, args.tmpdir, sr_keywords or [label])
    print(f"  未报工子项: {len(result['unreported_items'])} 条")

    out_json = os.path.join(args.tmpdir, 'mes_analysis_custom.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print('Step 4/4 渲染 HTML…')
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    render_report(result, label, args.output, args.tmpdir)
    print(f'✅ 完成: {args.output}')


if __name__ == '__main__':
    main()
