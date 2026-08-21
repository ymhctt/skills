#!/usr/bin/env python3
"""根据成本计算结果生成 HTML 可视化报告

风格参考：晶科能源海宁工厂 zData X 项目交付分析.html

Usage:
    python3 generate_html.py \
        --input result.json \
        --output report.html
"""

import json
import argparse
from datetime import datetime


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_html(data: dict, output_path: str):
    contract = data["contract"]
    orders = data["orders"]
    labor = data["labor"]
    budget = data["budget"]
    total_cost = data["total_cost"]
    gross_profit = data["gross_profit"]
    gross_margin = data["gross_margin"]
    sub_items = data.get("sub_items", [])
    time_records = data.get("time_records", [])

    total_amount = orders["total_amount"]
    total_outsource = orders["total_account_outsource"]
    total_labor = labor["total_cost"]
    total_hours = labor["total_hours"]
    budget_total = budget["total_budget"]
    order_details = orders["details"]
    person_costs = labor["person_costs"]

    # 获取合同名称：兼容 MES 原始字段名 (name)、camelCase (contractName)、snake_case (contract_name)
    raw_name = contract.get("contract_name") or contract.get("contractName") or contract.get("name", "")
    contract_name = raw_name or "未知合同"
    # 移除开头的年份前缀（如 "2025四川EI..." → "四川EI..."）
    import re
    contract_name = re.sub(r'^\d{4}[-_年\s]*', '', contract_name)
    contract_no = contract.get("contract_no") or contract.get("contractNo") or ""

    # Badge helper
    def badge(text: str, cls: str) -> str:
        return f'<span class="badge {cls}">{text}</span>'

    # ========== Order rows ==========
    order_rows = ""
    for o in order_details:
        diff_val = o["diff"]
        diff_cls = "green" if diff_val < 0 else ("orange" if diff_val < 30000 else "red")
        diff_sign = "+" if diff_val >= 0 else ""
        order_rows += f"""<tr>
            <td>{o['order_name']}</td>
            <td class="n">{o['amount']:,.0f}</td>
            <td class="n">{o['po_outsource']:,.0f}</td>
            <td class="n">{o['account_outsource']:,.0f}</td>
            <td>{badge(f'{diff_sign}{diff_val:,.0f}', diff_cls)}</td>
            <td class="n">{o['po_own']:,.0f}</td>
        </tr>"""

    if order_details:
        order_total_diff = orders['total_account_outsource'] - orders['total_po_outsource']
        diff_display = f"+{order_total_diff:,.0f}" if order_total_diff >= 0 else f"{order_total_diff:,.0f}"
        order_rows += f"""<tr style="font-weight:700">
            <td>合计</td>
            <td class="n">{orders['total_amount']:,.0f}</td>
            <td class="n">{orders['total_po_outsource']:,.0f}</td>
            <td class="n">{orders['total_account_outsource']:,.0f}</td>
            <td>{diff_display}</td>
            <td class="n">{orders['total_po_own']:,.0f}</td>
        </tr>"""

    # ========== Person rows ==========
    colors = ["r", "o", "b", "g", "p"]
    person_rows = ""
    for i, p in enumerate(person_costs):
        c = colors[i % len(colors)]
        ms = f"¥{p['monthly_salary']:,.0f}" if isinstance(p["monthly_salary"], (int, float)) else "—"
        person_rows += f"""<tr>
            <td>{p['name']}</td><td>{ms}</td><td>¥{p['hourly_rate']:.2f}</td>
            <td>{p['hours']:.0f}h</td><td class="n">¥{p['cost']:,.0f}</td>
            <td>{p['pct_of_labor']:.1f}%</td>
            <td><div class="mb"><div class="mbg"><div class="mbf {c}" style="width:{p['pct_of_labor']}%"></div></div></div></td>
        </tr>"""

    person_rows += f"""<tr style="font-weight:700">
        <td>合计</td><td>—</td><td>¥{labor['avg_hourly_rate']:.2f}</td>
        <td>{total_hours:.0f}h</td><td class="n">¥{total_labor:,.0f}</td><td>100%</td><td></td>
    </tr>"""

    # ========== Sub-item rows ==========
    sub_item_rows = ""
    for si in sub_items:
        comp = si["completion"]
        if comp > 100:
            comp_badge = badge(f'{comp:.1f}% 超计划', 'red')
        elif comp > 80:
            comp_badge = badge(f'{comp:.1f}%', 'orange')
        else:
            comp_badge = badge(f'{comp:.1f}%', 'green')
        sub_item_rows += f"""<tr>
            <td>{si['name']}</td>
            <td><span class="badge green">{si['type']}</span></td>
            <td class="n">{si['plan_hours']:.0f}h</td>
            <td class="n">{si['actual_hours']:.0f}h</td>
            <td>{comp_badge}</td>
            <td>{si['owner']}</td>
            <td>{si['start_time'][:10] if si.get('start_time') else ''} ~ {si['end_time'][:10] if si.get('end_time') else ''}</td>
        </tr>"""

    # ========== Time records detail & milestone extraction ==========
    record_rows = ""
    acc_name_map = {si["acc_id"]: si["name"] for si in sub_items}
    # Map acc_id -> sub_item type for maintenance-phase detection
    acc_type_map = {si["acc_id"]: si["type"] for si in sub_items}

    # 按时间升序排列报工
    sorted_records = sorted(time_records, key=lambda x: x.get("created_time", ""))

    # 关键里程碑阶段定义 — 主关键词 + 负向关键词（排除词）
    # 按真实 IT 项目生命周期排列
    milestone_phases = [
        {
            "phase": "项目启动",
            "primary_keywords": ["启动会", "kick-off", "kickoff", "开工仪式", "项目启动会"],
            "negative_keywords": ["准备", "环境", "调研"],
        },
        {
            "phase": "硬件上架",
            "primary_keywords": ["服务器上架", "机柜", "RAID", "BIOS", "BMC", "上架", "硬件安装"],
            "negative_keywords": [],
        },
        {
            "phase": "环境搭建",
            "primary_keywords": ["环境搭建", "系统安装", "网络配置", "RoCE", "IB网络", "IP配置",
                                 "系统初始化", "网络调试", "环境准备"],
            "negative_keywords": [],
        },
        {
            "phase": "软件部署",
            "primary_keywords": ["部署zdatax", "zdatax安装", "zdatax部署", "软件部署", "DM配置", "部署完成"],
            "negative_keywords": [],
        },
        {
            "phase": "性能测试",
            "primary_keywords": ["fio", "tpcc", "BenchmarkSQL", "压测", "性能测试", "性能优化",
                                 "网络测试", "NVME测试"],
            "negative_keywords": [],
        },
        {
            "phase": "故障排查",
            "primary_keywords": ["故障", "ORA-", "排查", "bug", "崩溃", "Bug修复", "bug修复"],
            "negative_keywords": [],
        },
        {
            "phase": "项目上线",
            "primary_keywords": ["上线", "投产", "正式上线", "割接", "go-live", "golive"],
            "negative_keywords": [],
        },
        {
            "phase": "保障运行",
            "primary_keywords": ["保障", "护航", "值守", "巡检"],
            "negative_keywords": [],
        },
        {
            "phase": "维保期",
            "primary_keywords": ["维保", "售后", "维护"],
            "negative_keywords": [],
            "require_maintenance_subitem": True,
        },
    ]

    def _is_maintenance_subitem(acc_id: str) -> bool:
        """判断该报工是否在维保/售后/维护类子项上"""
        si_type = acc_type_map.get(acc_id, "")
        return any(kw in si_type for kw in ["维保", "售后", "维护"])

    # 智能里程碑识别：按时间顺序遍历，每个阶段只取首次出现
    milestones = []
    phase_first_seen = {}

    for idx, r in enumerate(sorted_records):
        date_str = r.get("created_time", "")[:10] if r.get("created_time") else ""
        remark = r.get("remark", "") or ""
        acc_id = r.get("acc_id", "")

        for phase_info in milestone_phases:
            phase = phase_info["phase"]

            # 维保期特殊规则：只在维保类子项上匹配
            if phase_info.get("require_maintenance_subitem") and not _is_maintenance_subitem(acc_id):
                continue

            # 主关键词匹配（大小写不敏感）
            matched_kw = None
            for kw in phase_info["primary_keywords"]:
                if kw.lower() in remark.lower():
                    matched_kw = kw
                    break
            if not matched_kw:
                continue

            # 负向关键词排除
            if any(neg in remark for neg in phase_info.get("negative_keywords", [])):
                continue

            # 每个阶段只取第一次出现
            if phase not in phase_first_seen:
                phase_first_seen[phase] = {
                    "phase": phase,
                    "date": date_str,
                    "remark": remark[:120],
                    "hours": r.get("hours", 0),
                    "keyword": matched_kw,
                    "index": idx,
                }

    # 按项目阶段逻辑顺序输出里程碑（不按时间排序）
    phase_order = [
        "项目启动", "硬件上架", "环境搭建", "软件部署",
        "性能测试", "故障排查", "项目上线", "保障运行", "维保期",
    ]
    for phase_name in phase_order:
        if phase_name in phase_first_seen:
            milestones.append(phase_first_seen[phase_name])

    # ========== 重大风险复盘检测 ==========
    risk_keywords = [
        "不兼容", "bug", "Bug", "bug修复", "ORA-", "故障", "异常",
        "热插拔", "降速", "x16插槽", "raiser卡", "内存条", "三星",
        "不兼容列表", "白名单", "报警", "io抖动", "性能下降",
        "缺失", "依赖包", "无法访问", "交叉", "未使用网卡",
    ]
    risk_events = []
    risk_seen_phrases = set()

    for r in sorted_records:
        date_str = r.get("created_time", "")[:10] if r.get("created_time") else ""
        remark = r.get("remark", "") or ""
        remark_lower = remark.lower()

        for rk in risk_keywords:
            if rk.lower() in remark_lower:
                # 避免同一天同一类风险重复
                risk_key = f"{date_str}:{rk}"
                if risk_key not in risk_seen_phrases:
                    risk_seen_phrases.add(risk_key)
                    risk_events.append({
                        "date": date_str,
                        "keyword": rk,
                        "remark": remark[:150],
                        "hours": r.get("hours", 0),
                    })
                break

    # 按时间排序风险事件
    risk_events.sort(key=lambda x: x["date"])

    # 为报工明细表标记里程碑标签
    milestone_dates = set()
    for m in milestones:
        milestone_dates.add((m["date"], m["phase"]))

    for r in sorted_records:
        date_str = r.get("created_time", "")[:10] if r.get("created_time") else ""
        sub_name = acc_name_map.get(r["acc_id"], r["acc_id"])
        remark = r.get("remark", "") or ""
        # 标记里程碑行
        milestone_tag = ""
        for m in milestones:
            if m["date"] == date_str and m["keyword"] and m["keyword"] in remark:
                milestone_tag = f' <span class="milestone-badge">{m["phase"]}</span>'
                break

        html_remark = remark[:80]
        record_rows += f"""<tr>
            <td style="white-space:nowrap">{date_str}</td>
            <td style="white-space:nowrap">{r['name']}</td>
            <td class="n">{r['hours']:.0f}h</td>
            <td>{sub_name}</td>
            <td style="max-width:300px;font-size:12px;color:#94a3b8">{html_remark}{milestone_tag}</td>
        </tr>"""

    # ========== Build HTML ==========
    outsource_pct = total_outsource / total_amount * 100 if total_amount > 0 else 0
    labor_pct = total_labor / total_amount * 100 if total_amount > 0 else 0

    # Chart data
    timeline_labels = []
    timeline_data = []
    if time_records:
        # Group by date
        date_map = {}
        for r in time_records:
            d = r["created_time"][:10] if r.get("created_time") else ""
            if d:
                date_map[d] = date_map.get(d, 0) + r["hours"]
        sorted_dates = sorted(date_map.items())
        timeline_labels = [d for d, _ in sorted_dates]
        timeline_data = [h for _, h in sorted_dates]

    chart_timeline_labels = json.dumps(timeline_labels, ensure_ascii=False)
    chart_timeline_data = json.dumps(timeline_data)
    chart_cost_data = json.dumps([total_outsource, total_labor, gross_profit])
    chart_budget_used = json.dumps([total_labor, budget_total - total_labor])
    chart_profit_data = json.dumps([budget["dept_profit"], total_labor, budget["remaining_cost"]])
    chart_person_labels = json.dumps([p["name"] for p in person_costs], ensure_ascii=False)
    chart_person_data = json.dumps([p["cost"] for p in person_costs])

    order_labels = json.dumps([o["order_name"] for o in order_details], ensure_ascii=False) if order_details else '[]'
    order_amounts = json.dumps([o["amount"] for o in order_details]) if order_details else '[]'
    order_outsources = json.dumps([o["account_outsource"] for o in order_details]) if order_details else '[]'
    order_po_own = json.dumps([o["po_own"] for o in order_details]) if order_details else '[]'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{contract_name} · 交付分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
  :root {{
    --bg: #0f172a; --card: #1e293b; --border: #334155; --text: #f1f5f9;
    --muted: #94a3b8; --blue: #60a5fa; --purple: #c4b5fd; --green: #4ade80;
    --orange: #fbbf24; --red: #f87171; --cyan: #22d3ee;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg); color: var(--text); padding: 32px 20px; line-height: 1.7;
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; }}
  .hdr {{ text-align: center; margin-bottom: 36px; }}
  .hdr h1 {{ font-size: 22px; font-weight: 700; color: var(--text); }}
  .hdr h1 span {{ background: linear-gradient(135deg, var(--blue), var(--purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  .hdr p {{ color: var(--muted); font-size: 13px; margin-top: 4px; }}
  .kpi {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 28px; }}
  .kpi-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; text-align: center; }}
  .kpi-card .k {{ font-size: 12px; color: #94a3b8; margin-bottom: 2px; }}
  .kpi-card .v {{ font-size: 22px; font-weight: 700; margin: 6px 0; }}
  .kpi-card .s {{ font-size: 11px; color: #64748b; }}
  .flow {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 28px; }}
  .flow h2 {{ font-size: 15px; font-weight: 600; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
  .flow h2::before {{ content: ''; width: 4px; height: 16px; border-radius: 2px; background: var(--cyan); }}
  .flow-grid {{ display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 12px; align-items: center; }}
  .flow-box {{ text-align: center; padding: 14px 12px; border-radius: 10px; }}
  .flow-box.rev {{ background: rgba(34,211,238,.08); border: 1px solid rgba(34,211,238,.2); }}
  .flow-box.cost {{ background: rgba(248,113,113,.08); border: 1px solid rgba(248,113,113,.2); }}
  .flow-box.profit {{ background: rgba(74,222,128,.08); border: 1px solid rgba(74,222,128,.2); }}
  .flow-box .fl {{ font-size: 12px; color: var(--muted); margin-bottom: 4px; }}
  .flow-box .fv {{ font-size: 20px; font-weight: 700; }}
  .flow-box.rev .fv {{ color: var(--cyan); }}
  .flow-box.cost .fv {{ color: var(--red); }}
  .flow-box.profit .fv {{ color: var(--green); }}
  .flow-arrow {{ font-size: 24px; color: var(--muted); }}
  .flow-note {{ text-align: center; margin-top: 12px; font-size: 12px; color: var(--muted); }}
  .sec {{ margin-bottom: 28px; }}
  .sec h2 {{ font-size: 16px; font-weight: 600; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
  .sec h2::before {{ content: ''; width: 4px; height: 16px; border-radius: 2px; background: var(--blue); }}
  .sec h3 {{ font-size: 14px; font-weight: 600; margin: 14px 0 8px; color: var(--muted); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 12px; }}
  th, td {{ padding: 9px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ color: var(--muted); font-weight: 500; background: #0f172a; font-size: 12px; }}
  td {{ color: var(--text); }}
  td.n {{ font-family: 'SF Mono','Fira Code',monospace; color: var(--blue); font-weight: 600; }}
  tr:hover td {{ background: rgba(59,130,246,.04); }}
  .cp {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 14px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: center; }}
  .cp .chart {{ height: 180px; }}
  .cp .info {{ font-size: 13px; line-height: 1.8; }}
  .cp .info .hl {{ font-weight: 700; color: var(--blue); }}
  .cp.single {{ grid-template-columns: 1fr; }}
  .cp.single .chart {{ height: 170px; }}
  .mb {{ display: flex; align-items: center; gap: 8px; }}
  .mbg {{ flex: 1; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }}
  .mbf {{ height: 100%; border-radius: 3px; }}
  .r{{background:var(--red)}} .o{{background:var(--orange)}} .b{{background:var(--blue)}} .g{{background:var(--green)}} .p{{background:var(--purple)}}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
  .badge.green {{ background: rgba(74,222,128,.15); color: var(--green); }}
  .badge.orange {{ background: rgba(251,191,36,.15); color: var(--orange); }}
  .badge.red {{ background: rgba(248,113,113,.15); color: var(--red); }}
  .milestone-badge {{ display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 11px; font-weight: 700; background: rgba(96,165,250,.2); color: var(--blue); border: 1px solid rgba(96,165,250,.3); margin-left: 6px; }}
  .milestone-tl {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 28px; }}
  .milestone-tl h2 {{ font-size: 15px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
  .milestone-tl h2::before {{ content: ''; width: 4px; height: 16px; border-radius: 2px; background: var(--green); }}
  .ms-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }}
  .ms-card {{ position: relative; padding: 14px 12px; border-radius: 10px; background: rgba(96,165,250,.05); border: 1px solid rgba(96,165,250,.15); transition: all .2s; }}
  .ms-card:hover {{ background: rgba(96,165,250,.1); border-color: rgba(96,165,250,.3); }}
  .ms-card .ms-phase {{ font-size: 13px; font-weight: 700; color: var(--blue); margin-bottom: 6px; }}
  .ms-card .ms-date {{ font-size: 12px; color: var(--muted); font-family: 'SF Mono','Fira Code',monospace; }}
  .ms-card .ms-note {{ font-size: 11px; color: #64748b; margin-top: 4px; line-height: 1.4; }}
  .ms-card.risk {{ background: rgba(248,113,113,.08); border: 1px solid rgba(248,113,113,.3); }}
  .ms-card.risk:hover {{ background: rgba(248,113,113,.15); border-color: rgba(248,113,113,.5); }}
  .ms-card.risk .ms-phase {{ color: var(--red); }}
  .risk-badge {{ display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; background: rgba(248,113,113,.2); color: var(--red); border: 1px solid rgba(248,113,113,.4); margin-left: 6px; }}
  .ins .section {{ margin-bottom: 14px; }}
  .ins .section:last-child {{ margin-bottom: 0; }}
  .ins .section-title {{ font-size: 13px; font-weight: 700; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }}
  .ins .section-title::before {{ content: ''; width: 3px; height: 12px; border-radius: 2px; }}
  .ins .section-title.blue::before {{ background: var(--blue); }}
  .ins .section-title.orange::before {{ background: var(--orange); }}
  .ins .section-title.red::before {{ background: var(--red); }}
  .ins .section-title.green::before {{ background: var(--green); }}
  .ins .section-content {{ font-size: 12.5px; color: #cbd5e1; line-height: 1.8; }}
  .ins .section-content .highlight {{ color: var(--blue); font-weight: 600; }}
  .ins .section-content .warn {{ color: var(--orange); font-weight: 600; }}
  .ins .section-content .danger {{ color: var(--red); font-weight: 600; }}
  .ms-connector {{ display: none; }}
  .tl {{ position: relative; padding-left: 20px; }}
  .tl::before {{ content: ''; position: absolute; left: 6px; top: 4px; bottom: 4px; width: 2px; background: var(--border); }}
  .tl-item {{ position: relative; margin-bottom: 10px; font-size: 13px; }}
  .tl-item::before {{ content: ''; position: absolute; left: -17px; top: 6px; width: 8px; height: 8px; border-radius: 50%; background: var(--blue); border: 2px solid var(--card); }}
  .tl-item .d {{ color: var(--muted); font-size: 12px; }}
  .tl-item .t {{ color: var(--text); }}
  /* 报工明细表格优化 */
  .detail-table tbody tr {{ transition: background .15s; }}
  .detail-table tbody tr:hover {{ background: rgba(59,130,246,.06); }}
  .detail-date {{ white-space:nowrap; color: var(--muted); font-family: 'SF Mono','Fira Code',monospace; font-size: 12px; }}
  .name-badge {{ display: inline-flex; align-items: center; gap: 4px; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; background: rgba(96,165,250,.12); color: var(--blue); border: 1px solid rgba(96,165,250,.25); }}
  .hours-badge {{ display: inline-flex; align-items: center; justify-content: center; padding: 2px 10px; border-radius: 6px; font-size: 13px; font-weight: 700; background: rgba(96,165,250,.15); color: var(--blue); min-width: 40px; text-align: center; font-family: 'SF Mono','Fira Code',monospace; }}
  .sub-tag {{ display: inline-block; padding: 1px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; background: rgba(148,163,184,.08); color: #94a3b8; border: 1px solid rgba(148,163,184,.15); }}
  .remark-cell {{ font-size: 12.5px; color: #cbd5e1; line-height: 1.6; max-width: 400px; }}
  .ins {{ background: linear-gradient(135deg, var(--card), #0f172a); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }}
  .ins h3 {{ font-size: 14px; font-weight: 600; color: var(--orange); margin-bottom: 10px; }}
  .ins li {{ padding: 6px 0; border-bottom: 1px solid #1e293b; font-size: 13px; color: #cbd5e1; list-style: none; line-height: 1.7; }}
  .ins li:last-child {{ border: none; }}
  .ins li strong {{ color: var(--blue); }}
  .ins li.warn {{ color: var(--orange); }}
  blockquote {{ border-left: 3px solid var(--purple); padding: 10px 14px; margin: 10px 0; background: rgba(196,181,253,.05); border-radius: 0 8px 8px 0; font-size: 13px; color: var(--muted); }}
  @media(max-width:800px) {{
    .kpi {{ grid-template-columns: repeat(2,1fr); }}
    .cp {{ grid-template-columns: 1fr; }}
    .flow-grid {{ grid-template-columns: 1fr; gap: 8px; }}
    .flow-arrow {{ transform: rotate(90deg); text-align: center; }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <div class="hdr">
    <h1><span>{contract_name}</span> · 交付分析报告</h1>
    <p>合同编号 {contract_no} ｜ 数据截止 {data.get("generated_at", datetime.now().strftime("%Y-%m-%d"))}</p>
  </div>

  <!-- 收入→成本→利润 -->
  <div class="flow">
    <h2>项目收入与成本关系</h2>
    <div class="flow-grid">
      <div class="flow-box rev">
        <div class="fl">合同总金额（收入）</div>
        <div class="fv">¥{total_amount:,.0f}</div>
        <div class="s">合同总额</div>
      </div>
      <div class="flow-arrow">−</div>
      <div class="flow-box cost">
        <div class="fl">项目总成本</div>
        <div class="fv">¥{total_cost:,.0f}</div>
        <div class="s">外购 ¥{total_outsource:,.0f} + 人工 ¥{total_labor:,.0f}</div>
      </div>
      <div class="flow-arrow">=</div>
      <div class="flow-box profit">
        <div class="fl">项目毛利</div>
        <div class="fv">¥{gross_profit:,.0f}</div>
        <div class="s">毛利率 {gross_margin}%</div>
      </div>
    </div>
    <div class="flow-note">
      外购占合同额 {outsource_pct:.1f}%，人工占 {labor_pct:.1f}%，剩余 {gross_margin}% 为毛利。
    </div>
  </div>

  <!-- KPI -->
  <div class="kpi">
    <div class="kpi-card"><div class="k">合同总金额</div><div class="v" style="color:#22d3ee !important">¥{total_amount:,.0f}</div></div>
    <div class="kpi-card"><div class="k">外购成本</div><div class="v" style="color:#fbbf24 !important">¥{total_outsource:,.0f}</div><div class="s">占合同额 {outsource_pct:.1f}%</div></div>
    <div class="kpi-card"><div class="k">人工成本</div><div class="v" style="color:#60a5fa !important">¥{total_labor:,.0f}</div><div class="s">占合同额 {labor_pct:.1f}%</div></div>
    <div class="kpi-card"><div class="k">项目毛利</div><div class="v" style="color:#4ade80 !important">¥{gross_profit:,.0f}</div><div class="s">毛利率 {gross_margin}%</div></div>
  </div>"""

    # ========== Contract Info ==========
    company_name = contract.get("company_name", contract.get("companyName", ""))
    contract_manager = contract.get("contract_manager", contract.get("contractManager", ""))
    start_date = contract.get("start_date", contract.get("startDate", ""))
    end_date = contract.get("end_date", contract.get("endDate", ""))
    service_desc = contract.get("service_desc", contract.get("serviceDesc", ""))

    html += f"""
  <!-- 合同基本信息 -->
  <div class="sec">
    <h2>合同基本信息</h2>
    <table>
      <tr><th style="width:140px">合同编号</th><td>{contract_no}</td><th style="width:140px">合同名称</th><td>{contract_name}</td></tr>"""

    if company_name:
        html += f"""<tr><th>公司名称</th><td>{company_name}</td>"""
    if start_date and end_date:
        html += f"""<th>合同期间</th><td>{start_date[:10]} ~ {end_date[:10]}</td></tr>"""
    if contract_manager:
        html += f"""<tr><th>合同负责人</th><td>{contract_manager}</td>"""
    if service_desc:
        html += f"""<th>服务简述</th><td>{service_desc}</td></tr>"""

    html += """
    </table>
  </div>"""

    # ========== Sub-items ==========
    if sub_item_rows:
        html += f"""
  <!-- 合同子项 -->
  <div class="sec">
    <h2>合同子项</h2>
    <table>
      <thead><tr><th>子项名称</th><th>类型</th><th>计划工时</th><th>已用工时</th><th>完成度</th><th>负责人</th><th>期间</th></tr></thead>
      <tbody>{sub_item_rows}</tbody>
    </table>
  </div>"""

    # ========== Orders ==========
    if order_details:
        html += f"""
  <!-- 订单明细 -->
  <div class="sec">
    <h2>订单明细</h2>
    <table>
      <thead><tr><th>订单</th><th class="n">订单金额</th><th class="n">PO 外购</th><th class="n">核算外购</th><th>差异</th><th class="n">PO 自有</th></tr></thead>
      <tbody>{order_rows}</tbody>
    </table>
  </div>"""

    # ========== Timesheet summary ==========
    # Sub-item summary table
    sub_summary_rows = ""
    for si in sub_items:
        persons_str = "、".join(si["persons"])
        sub_summary_rows += f"""<tr>
            <td>{si['name']}</td>
            <td class="n">{si['actual_hours']:.0f}h</td>
            <td>{si['record_count']} 次</td>
            <td>{persons_str}</td>
        </tr>"""

    html += f"""
  <!-- 报工工时汇总 -->
  <div class="sec">
    <h2>报工工时汇总</h2>
    <table>
      <thead><tr><th>姓名</th><th>报工工时</th><th>报工次数</th><th style="width:40%">占比</th></tr></thead>
      <tbody>{person_rows}</tbody>
    </table>"""

    if sub_summary_rows:
        html += f"""
    <h3>按合同子项汇总</h3>
    <table>
      <thead><tr><th>合同子项</th><th>报工工时</th><th>报工次数</th><th>参与人员</th></tr></thead>
      <tbody>{sub_summary_rows}</tbody>
    </table>"""

    html += """
  </div>"""

    # ========== Milestone timeline ==========
    if milestones or risk_events:
        ms_cards = ""
        for m in milestones:
            ms_cards += f"""
        <div class="ms-card">
          <div class="ms-phase">{m['phase']}</div>
          <div class="ms-date">{m['date']}</div>
          <div class="ms-note">{m['remark'][:60]}</div>
        </div>"""
        # 添加重大风险复盘节点（标红）
        for re_item in risk_events:
            ms_cards += f"""
        <div class="ms-card risk">
          <div class="ms-phase"><span class="risk-badge">重大风险</span> {re_item['keyword']}</div>
          <div class="ms-date">{re_item['date']}</div>
          <div class="ms-note">{re_item['remark'][:80]}</div>
        </div>"""
        html += f"""
  <!-- 项目关键节点 -->
  <div class="milestone-tl">
    <h2>项目关键节点（蓝色为里程碑节点，红色为重大风险复盘）</h2>
    <div class="ms-grid">{ms_cards}
    </div>
  </div>"""

    # ========== Time records detail ==========
    if record_rows:
        display_count = min(len(time_records), 30)
        html += f"""
  <!-- 报工明细 -->
  <div class="sec">
    <h2>报工明细（共 {len(time_records)} 条，显示前 {display_count} 条）</h2>
    <table class="detail-table">
      <thead><tr><th style="width:100px">日期</th><th style="width:80px">执行人</th><th style="width:60px">工时</th><th style="width:140px">子项</th><th>工作内容</th></tr></thead>
      <tbody>"""
        for r in time_records[:display_count]:
            date_str = r["created_time"][:10] if r.get("created_time") else ""
            sub_name = acc_name_map.get(r["acc_id"], "")
            remark = r.get('remark', '') or ''
            # Mark milestone rows
            milestone_tag = ""
            for m in milestones:
                if m["date"] == date_str and m["phase"] in remark:
                    milestone_tag = f' <span class="milestone-badge">{m["phase"]}</span>'
                    break

            html_remark = remark[:100]
            html += f"""<tr>
                <td class="detail-date">{date_str}</td>
                <td><span class="name-badge">{r['name']}</span></td>
                <td style="text-align:center"><span class="hours-badge">{r['hours']:.0f}h</span></td>
                <td><span class="sub-tag">{sub_name}</span></td>
                <td class="remark-cell">{html_remark}{milestone_tag}</td>
            </tr>"""
        html += """
      </tbody>
    </table>
  </div>"""

    # ========== Cost analysis ==========
    top_person = person_costs[0] if person_costs else None
    top_person_note = f"{top_person['name']}成本消耗最高（{top_person['pct_of_labor']:.1f}%）" if top_person else ""

    html += f"""
  <!-- 成本分析 -->
  <div class="sec">
    <h2>项目成本分析</h2>

    <!-- 成本构成图 -->
    <div class="cp">
      <div class="chart"><canvas id="costPie"></canvas></div>
      <div class="info">
        <div>以 <span class="hl">合同总额 ¥{total_amount:,.0f}</span> 为基准看各项占比</div>
        <div><span class="hl">外购 {outsource_pct:.1f}%</span>（¥{total_outsource:,.0f}）</div>
        <div>人工 {labor_pct:.1f}%（¥{total_labor:,.0f}）</div>
        <div><span class="hl">毛利 {gross_margin}%</span>（¥{gross_profit:,.0f}）</div>
      </div>
    </div>

    <!-- 15%预算图 -->
    <div class="cp">
      <div class="chart"><canvas id="budgetDoughnut"></canvas></div>
      <div class="info">
        <div>交付+维保预算 = PO 自有 × 15% = <span class="hl">¥{budget_total:,.0f}</span></div>
        <div>已用 <span class="hl">{budget['labor_pct_of_budget']:.1f}%</span>（¥{total_labor:,.0f}），剩余 ¥{budget_total - total_labor:,.0f}</div>
        <div>剩余可用约 <span class="hl">{budget['remaining_hours']:.0f}h</span></div>
      </div>
    </div>

    <!-- 交付利润约束 -->
    <div class="cp">
      <div class="chart"><canvas id="profitPie"></canvas></div>
      <div class="info">
        <div>交付预算 ¥{budget_total:,.0f} 的 {budget['profit_rate']*100:.0f}% 利润线 = <span class="hl">¥{budget['dept_profit']:,.0f}</span></div>
        <div>即：交付部门 <strong>最多只能花 ¥{budget['max_allowable_cost']:,.0f}</strong> 在人工成本上</div>
        <div>已用 ¥{total_labor:,.0f}，仅占成本上限的 <span class="hl">{budget['labor_pct_of_max']:.1f}%</span></div>
        <div>剩余可用成本 ¥{budget['remaining_cost']:,.0f}，约 <span class="hl">{budget['remaining_hours']:.0f}h</span></div>
      </div>
    </div>

    <!-- 人员成本图 -->
    <div class="cp single">
      <div class="chart" style="height:150px"><canvas id="personBar"></canvas></div>
    </div>

    <!-- 人员成本表 -->
    <table>
      <thead><tr><th>姓名</th><th>月薪</th><th>时薪</th><th>报工工时</th><th class="n">人工成本</th><th>占人工</th><th style="width:30%">占比</th></tr></thead>
      <tbody>{person_rows}</tbody>
    </table>

    <blockquote>{top_person_note}</blockquote>
  </div>

  <!-- 交付+维保预算 -->
  <div class="sec">
    <h2>交付+维保预算</h2>
    <table>
      <thead><tr><th>项目</th><th>金额/数据</th></tr></thead>
      <tbody>
        <tr><td>PO 自有金额合计</td><td class="n">¥{orders['total_po_own']:,.2f}</td></tr>
        <tr><td>交付+维保总预算（自有 × 15%）</td><td class="n"><b>¥{budget_total:,.2f}</b></td></tr>
        <tr><td>已用人工成本</td><td class="n">¥{total_labor:,.2f}</td></tr>
        <tr><td>剩余可用预算</td><td class="n" style="color:var(--green)"><b>¥{budget_total - total_labor:,.2f}</b></td></tr>
        <tr><td>已用比例</td><td>{badge(f'{budget["labor_pct_of_budget"]:.1f}%', 'green' if budget['labor_pct_of_budget'] < 50 else ('orange' if budget['labor_pct_of_budget'] < 80 else 'red'))}</td></tr>
        <tr><td>剩余可用工时</td><td>约 {budget['remaining_hours']:.0f}h</td></tr>
      </tbody>
    </table>
  </div>

  <!-- 交付部门利润约束分析 -->
  <div class="sec">
    <h2>交付部门利润约束分析</h2>
    <blockquote>15%（¥{budget_total:,.0f}）为交付部门的费用包，交付部门需在费用包内保证 <strong style="color:var(--orange)">{budget['profit_rate']*100:.0f}% 利润率</strong></blockquote>

    <table>
      <thead><tr><th>指标</th><th>金额/数据</th><th>说明</th></tr></thead>
      <tbody>
        <tr><td>交付+维保总预算（PO 自有 × 15%）</td><td class="n">¥{budget_total:,.2f}</td><td>给到交付部门的费用包</td></tr>
        <tr><td>交付部门需保证利润率</td><td><b>{budget['profit_rate']*100:.0f}%</b></td><td>交付部门 KPI 要求</td></tr>
        <tr><td>交付部门利润</td><td class="n">¥{budget['dept_profit']:,.2f}</td><td>¥{budget_total:,.0f} × {budget['profit_rate']*100:.0f}%</td></tr>
        <tr><td>交付部门最大允许成本</td><td class="n"><b>¥{budget['max_allowable_cost']:,.2f}</b></td><td>¥{budget_total:,.0f} − 利润 ¥{budget['dept_profit']:,.0f}</td></tr>
        <tr><td>已用人工成本</td><td class="n">¥{total_labor:,.2f}</td><td>已报工 {total_hours:.0f}h</td></tr>
        <tr><td>已用占成本上限</td><td>{badge(f'{budget["labor_pct_of_max"]:.1f}%', 'green' if budget['labor_pct_of_max'] < 50 else ('orange' if budget['labor_pct_of_max'] < 80 else 'red'))}</td><td>¥{total_labor:,.0f} ÷ ¥{budget['max_allowable_cost']:,.0f}</td></tr>
        <tr><td>剩余可用成本</td><td class="n" style="color:var(--green)"><b>¥{budget['remaining_cost']:,.2f}</b></td><td>¥{budget['max_allowable_cost']:,.0f} − ¥{total_labor:,.0f}</td></tr>
        <tr><td>平均时薪</td><td>¥{labor['avg_hourly_rate']:.2f}/h</td><td>按加权平均</td></tr>
        <tr><td>剩余可用工时</td><td class="n">约 {budget['remaining_hours']:.0f}h</td><td>¥{budget['remaining_cost']:,.0f} ÷ ¥{labor['avg_hourly_rate']:.2f}</td></tr>
      </tbody>
    </table>
  </div>"""

    # ========== Order comparison ==========
    if order_details:
        # 计算每个订单的利润率用于标签
        order_margin_rates = []
        for o in order_details:
            if o["amount"] > 0:
                margin = o["amount"] - o["account_outsource"]
                rate = (margin / o["amount"]) * 100
                order_margin_rates.append(round(rate, 1))
            else:
                order_margin_rates.append(0)
        chart_order_rates = json.dumps(order_margin_rates)

        html += f"""
  <!-- 订单对比 -->
  <div class="sec">
    <h2>订单成本与利润对比</h2>
    <div class="cp single">
      <div class="chart" style="height:240px"><canvas id="orderBar"></canvas></div>
    </div>
    <table style="margin-top:14px">
      <thead><tr><th>订单</th><th class="n">订单金额</th><th class="n">核算外购</th><th class="n">利润空间</th><th>利润率</th></tr></thead>
      <tbody>"""
        for i, o in enumerate(order_details):
            profit_space = o["amount"] - o["account_outsource"]
            rate_cls = "green" if order_margin_rates[i] >= 30 else ("orange" if order_margin_rates[i] >= 15 else "red")
            html += f"""<tr>
                <td>{o['order_name']}</td>
                <td class="n">¥{o['amount']:,.0f}</td>
                <td class="n">¥{o['account_outsource']:,.0f}</td>
                <td class="n">¥{profit_space:,.0f}</td>
                <td>{badge(f'{order_margin_rates[i]:.1f}%', rate_cls)}</td>
            </tr>"""
        # 合计行
        total_profit = total_amount - total_outsource
        total_rate = (total_profit / total_amount * 100) if total_amount > 0 else 0
        total_cls = "green" if total_rate >= 30 else ("orange" if total_rate >= 15 else "red")
        html += f"""<tr style="font-weight:700">
            <td>合计</td>
            <td class="n">¥{total_amount:,.0f}</td>
            <td class="n">¥{total_outsource:,.0f}</td>
            <td class="n">¥{total_profit:,.0f}</td>
            <td>{badge(f'{total_rate:.1f}%', total_cls)}</td>
        </tr>"""
        html += """
      </tbody>
    </table>
  </div>"""

    # ========== Key findings ==========
    # Build comprehensive analysis — 基于报工内容真实分析
    plan_total_hours = sum(si["plan_hours"] for si in sub_items)
    over_budget_items = [si for si in sub_items if si["completion"] > 100]
    risk_event_count = len(risk_events)
    
    # 收集报工内容
    all_remarks = []
    for r in time_records:
        remark = r.get("remark", "").strip()
        if remark:
            all_remarks.append(remark)
    
    full_content = "\n".join(all_remarks) if all_remarks else ""
    
    # 关键词分类统计
    keyword_categories = {
        "软件安装/升级": ["安装", "部署", "升级", "版本", "zdata", "zData", "zCloud", "zDBM", "数据库", "Oracle", "MySQL", "PostgreSQL", "Redis", "软件", "RPM", "tar", "gz", "patch", "补丁"],
        "操作系统/环境": ["OS", "操作系统", "Redhat", "RHEL", "CentOS", "Ubuntu", "Linux", "内核", "kernel", "驱动", "系统", "环境配置", "配置", "ntp", "chrony", "DNS", "网络", "防火墙", "iptables", "selinux"],
        "硬件问题": ["NVMe", "硬盘", "内存", "内存条", "raiser", "riser", "热插拔", "硬件", "兼容", "服务器", "raid", "磁盘", "SSD", "HDD", "CPU", "网卡", "主板", "电源", "风扇"],
        "网络/存储": ["网络", "IP", "IP地址", "交换机", "路由器", "存储", "SAN", "NAS", "iSCSI", "光纤", "IB", "InfiniBand", "带宽", "延迟", "fio", "性能测试", "IO"],
        "故障处理": ["故障", "报错", "错误", "异常", "重启", "宕机", "崩溃", "修复", "排错", "debug", "排查", "问题", "处理", "恢复", "备份", "容灾", "DR", "HA"],
        "文档/沟通": ["文档", "报告", "方案", "确认", "沟通", "邮件", "会议", "记录", "说明", "清单"],
    }
    
    category_hits = {}
    if full_content:
        for cat, keywords in keyword_categories.items():
            count = 0
            hit_keywords = []
            for kw in keywords:
                if kw.lower() in full_content.lower():
                    count += full_content.lower().count(kw.lower())
                    hit_keywords.append(kw)
            if count > 0:
                category_hits[cat] = {"count": count, "keywords": hit_keywords}
    
    # 生成风险建议（基于实际报工内容）
    risk_suggestions = []
    if full_content:
        # 兼容性相关
        if "兼容" in full_content or "降级" in full_content or "适配" in full_content:
            compat_kws = [kw for kw in ["兼容", "降级", "适配", "bug"] if kw in full_content]
            compat_text = "、".join(compat_kws[:3])
            risk_suggestions.append(f'<span class="warn">兼容性风险</span>：报工中涉及{compat_text}相关问题（如操作系统版本适配），建议后续项目进场前完成环境兼容性清单确认。')
        # IB网络相关
        if any(kw in full_content for kw in ["IB", "InfiniBand", "ib网卡", "SR-IOV"]):
            ib_kws = [kw for kw in ["IB", "InfiniBand", "ib网卡", "SR-IOV"] if kw in full_content]
            ib_text = "、".join(ib_kws[:3])
            risk_suggestions.append(f'<span class="warn">网络部署</span>：涉及{ib_text}配置，属于技术难点，建议提前准备部署文档及排查手册。')
        # Oracle容灾
        if any(kw in full_content for kw in ["Oracle", "RAC", "DG", "容灾", "备份"]):
            db_kws = [kw for kw in ["Oracle", "RAC", "DG", "容灾", "备份"] if kw in full_content]
            db_text = "、".join(db_kws[:3])
            risk_suggestions.append(f'<span class="warn">数据库容灾</span>：涉及{db_text}部署，建议完成容灾演练验证并输出标准化文档。')
        # 文档相关
        if any(kw in full_content for kw in ["文档", "报告", "方案"]):
            risk_suggestions.append(f'<span class="highlight">知识沉淀</span>：报工中包含文档编写，建议将环境准备、部署步骤等内容整理为标准化交付手册。')
        # 项目跨度
        dates = [r.get("created_time", "")[:10] for r in time_records if r.get("created_time")]
        if dates:
            dates_sorted = sorted(dates)
            first_date = dates_sorted[0]
            last_date = dates_sorted[-1]
            if first_date != last_date:
                risk_suggestions.append(f'<span class="highlight">里程碑管理</span>：项目从 {first_date} 至 {last_date}，建议设置阶段性里程碑定期回顾。')
    
    # Build structured insights
    findings_html = ""
    
    # Section 1: 项目财务概览
    findings_html += f'<div class="section">'
    findings_html += f'<div class="section-title blue">项目财务概览</div>'
    findings_html += f'<div class="section-content">'
    findings_html += f'合同总金额 <span class="highlight">¥{total_amount:,.0f}</span>，'
    findings_html += f'项目总成本 <span class="highlight">¥{total_cost:,.0f}</span>（人工 ¥{total_labor:,.0f} + 外购 ¥{total_outsource:,.0f}），'
    findings_html += f'项目毛利 <span class="highlight">¥{gross_profit:,.0f}</span>，毛利率 <span class="highlight">{gross_margin}%</span>。'
    if gross_margin >= 30:
        findings_html += f' 整体盈利状况<span class="highlight">健康</span>。'
    findings_html += f'</div></div>'
    
    # Section 2: 交付成本与利润约束
    findings_html += f'<div class="section">'
    findings_html += f'<div class="section-title orange">交付成本与利润约束</div>'
    findings_html += f'<div class="section-content">'
    findings_html += f'交付+维保预算 = PO 自有 × 15% = <span class="highlight">¥{budget_total:,.0f}</span>。'
    findings_html += f'交付部门需在费用包内保证 <span class="highlight">{budget["profit_rate"]*100:.0f}% 利润率</span>，'
    findings_html += f'即最大允许成本 <span class="warn">¥{budget["max_allowable_cost"]:,.0f}</span>。'
    findings_html += f'已用人工 <span class="warn">¥{total_labor:,.0f}</span>（占成本上限 {budget["labor_pct_of_max"]:.1f}%），'
    findings_html += f'剩余可用成本 <span class="highlight">¥{budget["remaining_cost"]:,.0f}</span>（约 {budget["remaining_hours"]:.0f}h）。'
    if budget["labor_pct_of_max"] > 80:
        findings_html += f' <span class="danger">⚠ 成本已接近上限，需严格控制后续投入。</span>'
    elif budget["labor_pct_of_max"] > 50:
        findings_html += f' <span class="warn">成本使用适中，需关注后续维保阶段投入。</span>'
    else:
        findings_html += f' <span class="highlight">成本控制在合理范围内。</span>'
    findings_html += f'</div></div>'
    
    # Section 3: 工作内容深度分析（AI 驱动的项目执行分析）
    # 3.1 项目执行阶段识别
    if milestones:
        phases_executed = [m["phase"] for m in milestones]
        findings_html += f'<div class="section">'
        findings_html += f'<div class="section-title blue">项目执行阶段分析</div>'
        findings_html += f'<div class="section-content">'
        findings_html += f'项目共识别 <span class="highlight">{len(phases_executed)}</span> 个关键阶段：{" → ".join(phases_executed)}。'
        
        # 分析执行连续性
        all_phases = ["项目启动", "硬件上架", "环境搭建", "软件部署", "性能测试", "故障排查", "项目上线", "保障运行", "维保期"]
        missing_phases = [p for p in all_phases if p not in phases_executed]
        if missing_phases:
            findings_html += f'<br/>未识别到阶段：{"、".join(missing_phases)}（可能未在报工中体现或无需执行）。'
        
        # 分析故障排查情况
        if "故障排查" in phases_executed:
            fault_milestone = next((m for m in milestones if m["phase"] == "故障排查"), None)
            if fault_milestone:
                findings_html += f'<br/>项目执行期间经历<span class="warn">故障排查</span>阶段（{fault_milestone["date"]}），需关注技术风险对交付质量的影响。'
        
        findings_html += f'</div></div>'
    
    # 3.2 技术难点与挑战识别
    if risk_events or full_content:
        findings_html += f'<div class="section">'
        findings_html += f'<div class="section-title orange">技术难点与挑战识别</div>'
        findings_html += f'<div class="section-content">'
        
        technical_challenges = []
        # 基于风险事件
        if risk_events:
            challenge_types = set()
            for re_item in risk_events:
                kw = re_item["keyword"]
                if kw in ["不兼容", "Bug", "bug修复", "ORA-", "故障", "异常"]:
                    challenge_types.add("技术故障")
                elif kw in ["热插拔", "降速", "raiser卡", "内存条"]:
                    challenge_types.add("硬件兼容")
                elif kw in ["性能下降", "io抖动"]:
                    challenge_types.add("性能优化")
                elif kw in ["依赖包", "缺失", "无法访问"]:
                    challenge_types.add("环境依赖")
            
            if challenge_types:
                technical_challenges.append(f'项目实施期间识别 <span class="danger">{len(risk_events)}</span> 项技术风险，涉及：{"、".join(challenge_types)}。')
        
        # 基于报工内容分析技术复杂度
        if full_content:
            complexity_indicators = {
                "数据库集群": ["RAC", "DG", "集群", "主从", "双机"],
                "性能调优": ["TPCC", "fio", "压测", "性能测试", "基准测试", "BenchmarkSQL"],
                "网络配置": ["IB", "InfiniBand", "RoCE", "网卡", "IP地址", "交换机"],
                "系统迁移": ["迁移", "割接", "上线", "切换"],
                "容灾备份": ["备份", "容灾", "DR", "HA", "高可用"],
            }
            active_complexity = []
            for tech, keywords in complexity_indicators.items():
                if any(kw in full_content for kw in keywords):
                    active_complexity.append(tech)
            
            if active_complexity:
                technical_challenges.append(f'报工内容显示项目涉及 <span class="warn">{"、".join(active_complexity)}</span> 等技术领域，实施复杂度较高。')
        
        if technical_challenges:
            findings_html += "；".join(technical_challenges)
        else:
            findings_html += '报工内容显示项目执行过程相对平稳，未识别到重大技术挑战。'
        
        findings_html += f'</div></div>'
    
    # 3.3 资源效率评估
    if sub_items and person_costs:
        findings_html += f'<div class="section">'
        findings_html += f'<div class="section-title blue">资源效率评估</div>'
        findings_html += f'<div class="section-content">'
        
        # 工时利用率分析
        total_plan = sum(si["plan_hours"] for si in sub_items)
        total_actual = sum(si["actual_hours"] for si in sub_items)
        if total_plan > 0:
            efficiency = total_actual / total_plan * 100
            if efficiency > 100:
                findings_html += f'项目总工时利用率 <span class="danger">{efficiency:.0f}%</span>（计划 {total_plan:.0f}h，实际 {total_actual:.0f}h），实际投入超出计划，需关注工时评估准确性。'
            elif efficiency > 80:
                findings_html += f'项目总工时利用率 <span class="warn">{efficiency:.0f}%</span>（计划 {total_plan:.0f}h，实际 {total_actual:.0f}h），工时使用较为充分。'
            else:
                findings_html += f'项目总工时利用率 <span class="highlight">{efficiency:.0f}%</span>（计划 {total_plan:.0f}h，实际 {total_actual:.0f}h），部分子项仍有剩余工时。'
        
        # 人员投入集中度
        if person_costs:
            top_person = person_costs[0]
            if top_person["pct_of_labor"] > 50:
                findings_html += f'<br/>人员投入高度集中于 <span class="warn">{top_person["name"]}</span>（占人工成本 {top_person["pct_of_labor"]:.0f}%），存在单点依赖风险。'
            elif len(person_costs) >= 3:
                findings_html += f'<br/>团队共 <span class="highlight">{len(person_costs)}</span> 人参与报工，人员分布相对均衡，有利于降低单点风险。'
        
        findings_html += f'</div></div>'
    
    # 3.4 项目健康度评估
    health_score = 100
    health_issues = []
    
    # 超计划扣分
    over_items = [si for si in sub_items if si["completion"] > 100]
    if over_items:
        penalty = min(len(over_items) * 10, 30)
        health_score -= penalty
        health_issues.append(f'{len(over_items)} 个子项超计划工时')
    
    # 成本超标扣分
    if budget["labor_pct_of_max"] > 80:
        health_score -= 20
        health_issues.append('交付成本接近上限')
    elif budget["labor_pct_of_max"] > 60:
        health_score -= 10
        health_issues.append('交付成本使用过半')
    
    # 风险事件扣分
    if risk_events:
        penalty = min(len(risk_events) * 5, 20)
        health_score -= penalty
        health_issues.append(f'{len(risk_events)} 项技术风险')
    
    health_cls = "green" if health_score >= 80 else ("orange" if health_score >= 60 else "red")
    health_text = "健康" if health_score >= 80 else ("一般" if health_score >= 60 else "需关注")
    
    findings_html += f'<div class="section">'
    findings_html += f'<div class="section-title green">项目健康度评估</div>'
    findings_html += f'<div class="section-content">'
    findings_html += f'综合评估项目健康度为 <span class="{health_cls}">{health_score}分（{health_text}）</span>。'
    if health_issues:
        findings_html += f'<br/>扣分因素：{"；".join(health_issues)}。'
    else:
        findings_html += f' 项目执行情况良好，无明显风险项。'
    findings_html += f'</div></div>'
    
    # Section 4: 成本超支阶段分析（当项目超预算时）
    over_items = [si for si in sub_items if si["completion"] > 100]
    if over_items and budget["labor_pct_of_max"] > 100:
        findings_html += f'<div class="section">'
        findings_html += f'<div class="section-title red">成本超支阶段分析</div>'
        findings_html += f'<div class="section-content">'
        findings_html += f'项目人工成本已超预算上限（<span class="danger">{budget["labor_pct_of_max"]:.1f}%</span>），以下阶段报工超计划：'
        
        for si in over_items:
            excess_hours = si["actual_hours"] - si["plan_hours"]
            excess_pct = si["completion"] - 100
            findings_html += f'<br/><br/><span class="danger">▸ 子项「{si["name"]}」</span>'
            findings_html += f'<br/>  计划 {si["plan_hours"]:.0f}h，实际 {si["actual_hours"]:.0f}h，超 {excess_hours:.0f}h（+{excess_pct:.0f}%）'
            
            # 分析该子项的报工内容
            item_records = [r for r in time_records if r.get("acc_id") == si["acc_id"] or r.get("accId") == si["acc_id"]]
            if item_records:
                # 按人员统计该子项报工
                item_by_person = {}
                for r in item_records:
                    name = r.get("executor_name", r.get("executorName", "?"))
                    hours = r.get("task_time", r.get("taskTime", 0))
                    item_by_person[name] = item_by_person.get(name, 0) + hours
                
                person_breakdown = "；".join(f'{n}{h:.0f}h' for n, h in sorted(item_by_person.items(), key=lambda x: -x[1]))
                findings_html += f'<br/>  人员：{person_breakdown}'
                
                # 分析报工内容关键词
                item_remarks = [r.get("remark", r.get("content", "")).strip() for r in item_records]
                item_remarks = [r for r in item_remarks if r]
                if item_remarks:
                    item_full = "\n".join(item_remarks)
                    # 提取高频关键词
                    kw_count = {}
                    for kw in ["安装", "部署", "升级", "配置", "测试", "排查", "修复", "迁移", "调试", "兼容", "报错", "异常", "优化", "文档", "培训", "FIO", "TPCC", "RAC", "DG", "IB", "网络", "内存", "硬盘", "服务器", "许可", "lic"]:
                        cnt = item_full.count(kw)
                        if cnt > 0:
                            kw_count[kw] = cnt
                    top_kws = sorted(kw_count.items(), key=lambda x: -x[1])[:5]
                    if top_kws:
                        kw_summary = "、".join(f'{k}({v}次)' for k, v in top_kws)
                        findings_html += f'<br/>  主要工作：{kw_summary}'
            
            # 判断超支原因类型
            if excess_pct > 200:
                findings_html += f'<br/>  <span class="danger">⚠ 严重超支</span>：实际工时为计划的 {si["completion"]:.0f}%，需复盘是否因需求变更、技术难题或工时评估偏差导致。'
            elif excess_pct > 100:
                findings_html += f'<br/>  <span class="warn">⚠ 大幅超支</span>：实际工时为计划的 {si["completion"]:.0f}%，建议审查该阶段工作范围是否超出原计划。'
            else:
                findings_html += f'<br/>  <span class="warn">轻度超支</span>：实际工时为计划的 {si["completion"]:.0f}%，属可接受偏差范围。'
        
        findings_html += f'</div></div>'
    
    # Section 5: 建议与行动项（基于深度分析）
    findings_html += f'<div class="section">'
    findings_html += f'<div class="section-title green">建议与行动项</div>'
    findings_html += f'<div class="section-content">'
    findings_html += f'1. <span class="highlight">成本控制</span>：剩余可用成本约 ¥{budget["remaining_cost"]:,.0f}（{budget["remaining_hours"]:.0f}h），建议优先用于维保期客户响应，避免非必要投入。'
    
    # 基于超项的建议
    if over_items:
        for si in over_items:
            findings_html += f'<br/>2. <span class="warn">工时复盘</span>：子项「{si["name"]}」实际工时超计划 {si["completion"]-100:.0f}%，建议分析偏差原因并优化后续项目工时评估。'
    
    # 基于技术风险的改进
    if risk_events:
        findings_html += f'<br/>3. <span class="warn">经验沉淀</span>：项目期间识别 {len(risk_events)} 项技术风险，建议整理为《常见问题处理手册》供后续项目参考。'
    
    # 基于人员集中的建议
    if person_costs and person_costs[0]["pct_of_labor"] > 50:
        findings_html += f'<br/>4. <span class="highlight">团队建设</span>：{person_costs[0]["name"]}承担了 {person_costs[0]["pct_of_labor"]:.0f}% 的人工成本，建议培养备份人员降低单点依赖。'
    
    findings_html += f'</div></div>'
    
    html += f"""
  <!-- 关键发现 -->
  <div class="sec">
    <h2>关键发现与建议</h2>
    <div class="ins">
      {findings_html}
    </div>
  </div>

</div>

<script>
Chart.defaults.color='#94a3b8'; Chart.defaults.borderColor='#334155';
Chart.defaults.font={{family:'-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif',size:11}};
Chart.defaults.plugins.datalabels={{display:false}};

// 合同金额构成饼图
new Chart(document.getElementById('costPie'),{{type:'pie',data:{{labels:['外购成本','人工成本','毛利'],datasets:[{{data:{chart_cost_data},backgroundColor:['#f87171','#60a5fa','#4ade80'],borderWidth:0,hoverOffset:8}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom',labels:{{padding:10,boxWidth:12,font:{{size:11}},color:'#cbd5e1'}}}},tooltip:{{callbacks:{{label:c=>` ${{c.label}}: ¥${{c.raw.toLocaleString()}} (${{(c.raw/{total_amount}*100).toFixed(1)}}%)`}}}}}}}}}});

// 15% 预算半圆环
new Chart(document.getElementById('budgetDoughnut'),{{type:'doughnut',data:{{labels:['已用人工','剩余预算'],datasets:[{{data:{chart_budget_used},backgroundColor:['#fbbf24','#4ade80'],borderWidth:0,hoverOffset:8,circumference:180,rotation:270}}]}},options:{{responsive:true,maintainAspectRatio:false,cutout:'70%',plugins:{{legend:{{position:'bottom',labels:{{padding:10,boxWidth:12,font:{{size:11}},color:'#cbd5e1'}}}},tooltip:{{callbacks:{{label:c=>` ${{c.label}}: ¥${{c.raw.toLocaleString()}}`}}}}}}}}}});

// 交付利润约束
new Chart(document.getElementById('profitPie'),{{type:'pie',data:{{labels:['交付部门利润','已用人工','剩余可用成本'],datasets:[{{data:{chart_profit_data},backgroundColor:['#22d3ee','#fbbf24','#60a5fa'],borderWidth:0,hoverOffset:8}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom',labels:{{padding:10,boxWidth:12,font:{{size:11}},color:'#cbd5e1'}}}},tooltip:{{callbacks:{{label:c=>` ${{c.label}}: ¥${{c.raw.toLocaleString()}} (${{(c.raw/{budget_total}*100).toFixed(1)}}%)`}}}}}}}}}});

// 人员成本
new Chart(document.getElementById('personBar'),{{type:'bar',data:{{labels:{chart_person_labels},datasets:[{{label:'人工成本',data:{chart_person_data},backgroundColor:['rgba(248,113,113,.8)','rgba(251,191,36,.8)','rgba(96,165,250,.8)','rgba(74,222,128,.8)','rgba(196,181,253,.8)'],borderRadius:4,borderSkipped:false,barThickness:22}}]}},options:{{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>` ¥${{c.raw.toLocaleString()}}`}}}}}},scales:{{x:{{grid:{{color:'#334155'}},ticks:{{callback:v=>'¥'+(v/1000)+'k',font:{{size:10}},color:'#94a3b8'}}}},y:{{grid:{{display:false}},ticks:{{font:{{size:12}},color:'#cbd5e1'}}}}}}}}}});"""

    if timeline_data and timeline_labels:
        html += f"""

// 报工时间线
new Chart(document.getElementById('timelineBar'),{{type:'bar',data:{{labels:{chart_timeline_labels},datasets:[{{label:'报工工时',data:{chart_timeline_data},backgroundColor:'rgba(96,165,250,.65)',borderRadius:3,borderSkipped:false,barThickness:14}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>c.raw+'h'}}}}}},scales:{{x:{{grid:{{display:false}},ticks:{{font:{{size:9}},maxRotation:45,color:'#94a3b8'}}}},y:{{grid:{{color:'#334155'}},ticks:{{callback:v=>v+'h',font:{{size:10}},color:'#94a3b8'}}}}}}}}}});"""

    if order_details:
        html += f"""

// 订单对比 — 堆叠柱状图
var _orderLabels = {order_labels};
new Chart(document.getElementById('orderBar'),{{type:'bar',data:{{labels:_orderLabels,datasets:[
  {{label:'核算外购（成本）',data:{order_outsources},backgroundColor:'rgba(248,113,113,.85)',borderRadius:'4 4 0 0',borderSkipped:false,barPercentage:0.7}},
  {{label:'利润空间',data:{order_po_own},backgroundColor:'rgba(74,222,128,.85)',borderRadius:'4 4 0 0',borderSkipped:false,barPercentage:0.7}}
]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{
  legend:{{position:'top',labels:{{padding:14,usePointStyle:true,pointStyle:'rectRounded',font:{{size:12}},color:'#cbd5e1'}}}},
  tooltip:{{callbacks:{{
    title:function(items){{ return _orderLabels[items[0].dataIndex]; }},
    label:function(c){{
      if(c.datasetIndex===0) return ` 核算外购: ¥${{c.raw.toLocaleString()}}`;
      return ` 利润空间: ¥${{c.raw.toLocaleString()}}`;
    }},
    afterBody:function(items){{
      var rate={chart_order_rates}[items[0].dataIndex];
      return ` 利润率: ${{rate}}%`;
    }}
  }}}}
}},scales:{{
  x:{{stacked:true,grid:{{display:false}},ticks:{{font:{{size:12}},color:'#cbd5e1'}}}},
  y:{{stacked:true,grid:{{color:'#334155'}},ticks:{{callback:v=>'¥'+(v/10000)+'万',font:{{size:11}},color:'#94a3b8'}}}}
}}}}}});"""

    html += """
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML 报告已生成 → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成 HTML 可视化报告")
    parser.add_argument("--input", required=True, help="成本计算结果 JSON")
    parser.add_argument("--output", required=True, help="输出 HTML 路径")
    args = parser.parse_args()

    data = load_json(args.input)
    generate_html(data, args.output)
