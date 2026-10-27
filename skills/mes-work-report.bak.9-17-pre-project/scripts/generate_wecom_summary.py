#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""东西大区报工催办 Webhook 消息生成器

在生成 HTML 报告后调用，生成企业微信总结消息。
默认只生成消息内容并展示，不自动发送。用户确认后才发送。

用法：
    python3 generate_wecom_summary.py \
        --date-start 2026-05-18 \
        --date-end 2026-05-22 \
        --standard-hours 40.0 \
        --exclude "许文榕,杨明翰,周瑞斌" \
        --tmpdir /tmp
"""
import argparse, json, os, sys

TEAMS_CONFIG = {
    't2': {'name': '东西大区1部', 'id': 2},
    't3': {'name': '东西大区2部', 'id': 3},
    't23': {'name': '东西大区4部', 'id': 23},
    't19': {'name': '东西大区5部', 'id': 19},
}

TEAM_ORDER = ['东西大区1部', '东西大区2部', '东西大区4部', '东西大区5部']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date-start', required=True)
    parser.add_argument('--date-end', required=True)
    parser.add_argument('--standard-hours', type=float, default=40.0)
    parser.add_argument('--exclude', default='')
    parser.add_argument('--tmpdir', default='/tmp')
    parser.add_argument('--send', action='store_true',
        help='生成消息后直接发送到 webhook（默认不发送，只展示内容）')
    parser.add_argument('--webhook-key', default='',
        help='企业微信 webhook key，默认从环境变量 WECOM_WEBHOOK_KEY 读取')
    parser.add_argument('--output-payload', default='/tmp/wecom_webhook_payload.json',
        help='JSON payload 输出路径')
    args = parser.parse_args()

    excluded = set(x.strip() for x in args.exclude.split(',') if x.strip())
    date_range = f"{args.date_start}~{args.date_end}"

    # ========== 1. 提取东西大区全员名单 ==========
    all_dx_members = set()
    for tid in ['t2', 't3', 't23', 't19']:
        fpath = os.path.join(args.tmpdir, f'mes_summary_{tid}.json')
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        obj = data.get('operateCallBackObj')
        if isinstance(obj, list):
            for m in obj:
                name = m.get('userName', '')
                if name:
                    all_dx_members.add(name)

    # ========== 2. 报工不足人员 ==========
    low_hours = []
    for tid, cfg in TEAMS_CONFIG.items():
        tname = cfg['name']
        fpath = os.path.join(args.tmpdir, f'mes_summary_{tid}.json')
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for m in data.get('operateCallBackObj', []):
            name = m.get('userName', '')
            if name in excluded:
                continue
            total_h = float(m.get('totalTaskTime', 0) or 0)
            if total_h < args.standard_hours:
                gap = args.standard_hours - total_h
                low_hours.append({
                    'team': tname, 'name': name,
                    'total_h': total_h, 'gap': gap
                })
    low_hours.sort(key=lambda x: x['gap'], reverse=True)

    # ========== 3. 未报工项目 ==========
    no_work_items_summary = []
    nw_path = os.path.join(args.tmpdir, 'mes_no_work_items_v2.json')
    if os.path.exists(nw_path):
        with open(nw_path, 'r', encoding='utf-8') as f:
            nw = json.load(f)
        for entry in nw:
            contract = entry.get('contract', {})
            no_work_items_summary.append({
                'contract_name': contract.get('contract_name', '未知合同'),
                'manager': contract.get('manager', '未指定'),
                'count': len(entry.get('no_work_items', []))
            })
        no_work_items_summary.sort(key=lambda x: x['count'], reverse=True)

    # ========== 4. 未关闭服务请求（仅东西大区） ==========
    # 服务请求全量采集（所有团队共用一份）
    svc_path = None
    for tid in ['t2', 't3', 't23', 't19']:
        p = os.path.join(args.tmpdir, f'mes_service_{tid}.json')
        if os.path.exists(p):
            svc_path = p
            break

    open_requests = []
    exec_counts = {}
    if svc_path and os.path.exists(svc_path):
        with open(svc_path, 'r', encoding='utf-8') as f:
            svc_data = json.load(f)
        svc_list = svc_data.get('list', [])
        if not isinstance(svc_list, list):
            svc_list = []
        closed_keywords = ['已关闭', '关闭', '已解决', '已完成', '已结束']
        for s in svc_list:
            status = s.get('statusLabel', '') or ''
            if any(k in status for k in closed_keywords):
                continue
            exec_name = (s.get('executorEmployeeName') or s.get('executorName') or '').strip()
            if exec_name in all_dx_members:
                open_requests.append(s)
                exec_counts[exec_name] = exec_counts.get(exec_name, 0) + 1

    # ========== 5. 构建消息 ==========
    team_groups = {}
    for x in low_hours:
        team_groups.setdefault(x['team'], []).append(x)

    lines = []
    lines.append(f"# 东西大区报工催办 ({date_range})")
    lines.append("")
    lines.append(f"## 报工不足提醒（共 {len(low_hours)} 人）")
    lines.append("> 标准：工作日 40h/周，周六工时计入加班")
    lines.append("")

    for team in TEAM_ORDER:
        members = team_groups.get(team, [])
        if not members:
            continue
        lines.append(f"**{team}**（{len(members)}人不足）")
        for m in members:
            if m['gap'] >= 20:
                bar = "\U0001F534"
            elif m['gap'] >= 10:
                bar = "\U0001F7E0"
            else:
                bar = "\U0001F7E1"
            lines.append(f"{bar} {m['name']}：已报 **{m['total_h']}h**，缺 **{m['gap']:.1f}h**")
        lines.append("")

    # 未报工项目
    total_nw = sum(x['count'] for x in no_work_items_summary)
    lines.append(f"## 维保合同未报工子项（{len(no_work_items_summary)} 个合同 / {total_nw} 个子项）")
    lines.append("> 东西大区维保团队下，合同有效期内 actualHours=0 的子项")
    lines.append("")
    for x in no_work_items_summary[:10]:
        cname = x['contract_name']
        name_short = cname[:28] + '\u2026' if len(cname) > 28 else cname
        lines.append(f"- {name_short}（{x['manager']}）— **{x['count']}** 项未报工")
    if len(no_work_items_summary) > 10:
        lines.append(f"- \u2026另有 {len(no_work_items_summary) - 10} 个合同")
    lines.append("")

    # 服务请求（仅东西大区）
    lines.append(f"## 未关闭服务请求（共 {len(open_requests)} 条）")
    lines.append("> 本周内提交、当前仍处理中的请求（仅东西大区）")
    lines.append("")
    if exec_counts:
        lines.append("**处理人待办排行：**")
        for name, cnt in sorted(exec_counts.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"- {name}：**{cnt}** 条")
    else:
        lines.append("> 本周东西大区人员无未关闭服务请求")
    lines.append("")
    lines.append("> \u26A0\uFE0F 请各部门负责人督促相关人员**今日内完成报工填报**，并跟进未关闭服务请求处置进展。")

    msg = "\n".join(lines)

    payload = {
        "msgtype": "markdown",
        "markdown": {"content": msg}
    }

    with open(args.output_payload, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(msg)
    print(f"\n{'='*60}")
    print(f"字符数: {len(msg)}")
    print(f"报工不足: {len(low_hours)} 人")
    print(f"未报工合同: {len(no_work_items_summary)} 个 / {total_nw} 个子项")
    print(f"未关闭服务请求（东西大区）: {len(open_requests)} 条")
    print(f"\nJSON payload: {args.output_payload}")

    # ========== 6. 可选发送 ==========
    if args.send:
        webhook_key = args.webhook_key or os.environ.get('WECOM_WEBHOOK_KEY', '') or os.environ.get('WECOM_WEBHOOK_KEY', '')
        if not webhook_key:
            print("\n错误：未指定 webhook key，无法发送。")
            sys.exit(1)
        import subprocess
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', url,
             '-H', 'Content-Type: application/json',
             '-d', f'@{args.output_payload}'],
            capture_output=True, text=True
        )
        resp = result.stdout.strip()
        print(f"\n发送结果: {resp}")
        try:
            r = json.loads(resp)
            if r.get('errcode') == 0:
                print("发送成功！")
            else:
                print(f"发送失败: {r.get('errmsg', 'unknown')}")
        except:
            print(resp)

if __name__ == '__main__':
    main()
