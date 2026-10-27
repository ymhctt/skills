---
name: mes_dongxi_weekly_report
description: 东西大区四团队报工周报/月报/季度报自动分析。当用户需要生成东西大区报工报告、东西大区周报、东西大区月报、东西大区季度报、Q1/Q2/Q3/Q4报工、四团队报工对比分析、项目报工排名、单团队报工分析、单人员报工分析时触发此技能。支持按周、按月或自定义日期范围统计，输出 HTML 可视化报告。单团队/单人员分析使用深蓝色主题模板。
---

# 东西大区四团队报工分析

## 目标

自动采集东西大区四个团队的报工数据，生成结构化的 HTML 可视化报告，包含核心指标对比、成员工时明细、报工不足分析、文档统计、项目成本消耗、报工质量（含人员质量明细）、项目报工排名（含工时分布可视化）、每人季度工作总结、服务请求分析、项目未报工分析和综合评价十一大维度。

## 触发词

- 东西大区报工、东西大区周报、东西大区月报、东西大区季度报
- 四团队报工分析、团队报工对比
- 单团队报工分析、单人员报工分析
- 生成本周报工报告、生成本月报工报告、生成季度报工报告
- Q1报工、Q2报工、Q3报工、Q4报工
- 项目报工排名、报工最多项目
- 项目未报工分析、未报工合同子项、合同子项报工情况
- 1部报工、2部报工、4部报工、5部报工
- XX报工分析（指定团队名或人员名）

## 固定配置

### 团队列表
| 团队 | MES team-id |
|------|-------------|
| 东西大区1部 | 2 |
| 东西大区2部 | 3 |
| 东西大区4部 | 23 |
| 东西大区5部 | 19 |

### 默认排除人员
许文榕、杨明翰、周瑞斌

### 工时标准
- 工作日 8h/天
- 周报：5 个工作日 × 8h = 40h/人·周
- 月报：当月实际工作日数 × 8h/人·月
- 季度报：当季所有工作日 × 8h（Q1约64天=512h，以实际日历为准）
- **周六周日工时视为加班**

## 执行流程

### Step 1：确定统计范围

根据用户请求确定模式和目标团队：

**⚠️ 严格执行规则：**
- 当用户要求分析**东西大区四团队**报工情况时，必须包含以下所有维度：
  1. 四团队核心指标对比
  2. 成员工时明细 & 每日工时
  3. 报工不足人员（工作日8h/天，周六周日视为加班）
  4. 文档编写数量
  5. 报工质量分析
  6. 报工内容工作总结
  7. 项目成本消耗
  8. 项目报工排名（各团队TOP15）
  9. 服务请求情况（按用户要求的时间范围）
  10. 🆕 **项目未报工分析**（东西大区维保项目支持团队下未产生报工的合同子项）
  11. 综合评价

**判断规则：**
- 如果用户指定了**单个团队**（如"服务2部报工分析"、"1部Q1报告"）或**单个人员**（如"吴伟龙的报工"），则标记为 `single_team=true`
- 如果用户指定了**多个团队**或**四团队对比**（如"东西大区报工"、"四团队对比"），则标记为 `single_team=false`

| 请求 | 模式 | 目标团队 | 报告模板 |
|------|------|----------|----------|
| "本周报工"、"周报" | `week` | 四团队(2,3,23,19) | generate_report.py |
| "本月报工"、"月报" | `month` | 四团队(2,3,23,19) | generate_report.py |
| "Q1"、"一季度"、"1-3月" | `quarter` | 四团队(2,3,23,19) | generate_quarter_report.py |
| "服务2部Q1"、"1部报工分析" | `quarter` | 单团队 | **generate_single_team_report.py** |
| "吴伟龙报工" | `quarter` | 单人员所在团队 | **generate_single_team_report.py** |
| 自定义范围（四团队） | `custom` | 四团队(2,3,23,19) | generate_quarter_report.py |
| 自定义范围（单团队） | `custom` | 单团队 | **generate_single_team_report.py** |

默认取**当前日期**。若未指定，周报取本周，月报取本月。

### Step 2：用 mes CLI 采集数据

**确定要采集的团队：**
- 四团队模式：对所有团队（team-id: 2, 3, 23, 19）执行以下命令
- 单团队/单人员模式：只对**目标团队**执行以下命令

对每个目标团队（team-id: {tid}）执行：

```bash
# ⚠️ 重要：团队 ID 必须带 "t" 前缀（t2/t3/t23/t19），与 analyze.py 中的 DEFAULT_TEAMS 一致
# 1. 团队摘要数据
mes -o json statistics summary --from {date_start} --to {date_end} --team-id {real_tid} > /tmp/mes_summary_t{real_tid}.json

# 2. 详细报工记录（⚠️ 必须加 --page-size，默认只返回100条，月度/季度数据量很大）
# ⚠️⚠️ 重要：月度数据用 --page-size 2000，季度数据用 --page-size 5000，否则可能超时或截断
mes -o json statistics list --from {date_start} --to {date_end} --team-id {real_tid} --page-size 2000 > /tmp/mes_list_t{real_tid}.json

# 3. 文章/文档数据（注意时间格式必须是 YYYY-MM-DD HH:mm:ss）
mes -o json article list --mode manage --team-id {real_tid} --start-time "{date_start} 00:00:00" --end-time "{date_end} 23:59:59" --page-size 100 > /tmp/mes_article_t{real_tid}.json

# 4. 服务请求数据（⚠️ mes 0.5.3 起命令改为 `sr list`，不支持 --team-id）
# ⚠️ 需全局查询后由 analyze.py 按团队名称过滤东西大区
mes -o json sr list --start-time "{date_start} 00:00:00" --end-time "{date_end} 23:59:59" --page-size 500 > /tmp/mes_service_requests.json
# ⚠️ analyze.py 读取 /tmp/mes_service_t{tid}.json，需将全局文件复制到各团队：
cp /tmp/mes_service_requests.json /tmp/mes_service_t2.json
cp /tmp/mes_service_requests.json /tmp/mes_service_t3.json
cp /tmp/mes_service_requests.json /tmp/mes_service_t23.json
cp /tmp/mes_service_requests.json /tmp/mes_service_t19.json
```

**示例：**
```bash
mes -o json statistics summary --from 2026-04-20 --to 2026-04-26 --team-id 2 > /tmp/mes_summary_t2.json
mes -o json statistics list --from 2026-04-20 --to 2026-04-26 --team-id 2 --page-size 2000 > /tmp/mes_list_t2.json
mes -o json article list --mode manage --team-id 2 --start-time "2026-04-20 00:00:00" --end-time "2026-04-26 23:59:59" --page-size 100 > /tmp/mes_article_t2.json
mes -o json sr list --start-time "2026-04-20 00:00:00" --end-time "2026-04-26 23:59:59" --page-size 500 > /tmp/mes_service_requests.json
cp /tmp/mes_service_requests.json /tmp/mes_service_t2.json
```

### Step 2.5：查询项目未报工合同子项（用于报告第十一节）

**目标**：找出"东西大区维保项目支持团队"下所有未结束合同中，`actualHours=0` 的合同子项。

```python
# 内联 Python 脚本执行（无需写文件）
import json, subprocess
from datetime import datetime
from collections import defaultdict

# 1. 拉取全部合同（⚠️ page-size 500 可能超时，需分页查询，page-size 默认15）
subprocess.run('mes -o json contract list --page 1 > /tmp/mes_all_contracts.json', shell=True)
with open('/tmp/mes_all_contracts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

today = datetime.now().strftime('%Y-%m-%d')

# 2. 筛选东西大区维保项目支持团队且合同未结束的
target_contracts = []
for item in data.get('list', []):
    service_teams = item.get('serviceTeams', [])
    if not isinstance(service_teams, list):
        continue
    has_target_team = any('东西大区维保' in t.get('name', '') for t in service_teams)
    if not has_target_team:
        continue
    end_time = item.get('contractEndTime', '') or item.get('endTime', '')
    if end_time and end_time > today:
        target_contracts.append({
            'contract_id': item.get('id'),
            'contract_name': item.get('name'),
            'manager': item.get('manager') or '未指定',
            'start_time': item.get('contractStartTime'),
            'end_time': end_time,
        })

# 3. 批量查询每个合同的子项，按 v2 格式分组（generate_report.py 读取 v2 格式）
results_v2 = []
for contract in target_contracts:
    cid = contract['contract_id']
    cmd = f'mes -o json contract list-items --contract-id {cid}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        resp = json.loads(result.stdout)
        items = resp.get('operateCallBackObj', {}).get('list', [])
        no_work_items = []
        has_work_items = []
        for ni in items:
            actual = ni.get('actualHours', 0) or 0
            entry = {
                'item_name': ni.get('itemName', ''),
                'item_type': ni.get('itemType', ''),
                'actual_hours': actual,
                'plan_hour': ni.get('planHour', 0) or 0,
                'remaining_task': ni.get('remainingTask', 0) or 0,
            }
            if actual == 0:
                no_work_items.append(entry)
            else:
                has_work_items.append(entry)
        # 只保留有未报工子项的合同
        if no_work_items:
            results_v2.append({
                'contract': contract,
                'no_work_items': no_work_items,
                'has_work_items': has_work_items,
            })
    except:
        pass

# 4. 保存 v2 格式（generate_report.py 读取 /tmp/mes_no_work_items_v2.json）
with open('/tmp/mes_no_work_items_v2.json', 'w', encoding='utf-8') as f:
    json.dump(results_v2, f, ensure_ascii=False, indent=2)

total_no_work = sum(len(d['no_work_items']) for d in results_v2)
print(f"涉及合同数: {len(results_v2)}, 未报工子项总数: {total_no_work}")
```

**分析逻辑说明：**

本节分析目标是：**找出"东西大区维保项目支持团队"下，合同未结束但子项实际报工为零的项目**，帮助管理层识别"有合同、无推进"的风险项目。

筛选规则（三层过滤）：
1. **团队过滤**：合同的 `serviceTeams` 字段中，至少有一个 team 的 `name` 包含"东西大区维保"
2. **时效过滤**：合同的结束时间（`contractEndTime` 或 `endTime`）> 今日，即合同仍在有效期内
3. **报工过滤**：合同子项的 `actualHours == 0`，即该子项未产生任何实际报工记录

输出格式（v2 格式，按合同分组）：
- `contract`：合同基础信息（合同名、项目经理、起止时间）
- `no_work_items`：该合同下未报工的子项列表
- `has_work_items`：该合同下已有报工的子项列表（用于提示"部分子项正常"）

报告呈现（generate_report.py 第十一节）：
- 汇总卡片：涉及合同数 / 未报工子项数 / 剩余工时合计
- 按合同分组展示，按未报工子项数降序排列
- 每个合同展示：合同名、项目经理、合同时间、计划工时、剩余工时、未报工子项数
- 若该合同同时存在已报工子项，用绿色角标提示"部分子项有报工"
- 子项明细表格：子项名称 / 类型 / 计划工时 / 实际工时(0h 红色标注) / 剩余工时进度条

**关键字段说明：**
- `serviceTeams`：合同的服务团队列表，需匹配 name 包含"东西大区维保"
- `actualHours`：实际报工工时，0 表示未报工
- `planHour`：计划工时
- `remainingTask`：剩余工时
- 结果保存至 `/tmp/mes_no_work_items_v2.json`（v2 按合同分组格式）供 generate_report.py 读取
- **⚠️ 注意**：generate_report.py 读取 `/tmp/mes_no_work_items_v2.json`（含 `contract`/`no_work_items`/`has_work_items` 三字段）；旧扁平格式 `mes_no_work_items.json` 已废弃，不可使用

**踩坑提醒：**
- `article list` 的 `--start-time` / `--end-time` **必须包含时分秒**，否则返回"参数非法"
- **`statistics list` 可能超时！** 月度数据必须用 `--page-size 2000`，季度用 `--page-size 5000`。如果 list 文件大小 <1KB（如 93字节），说明超时失败，需重新采集。验证方法：`wc -c /tmp/mes_list_t*.json`
- 如果 list 文件超过 100KB，用 Python 脚本解析而非 `read_file`
- `statistics summary` 返回的数据在 `operateCallBackObj` 字段（列表），不是 `data.list`
- `statistics list` 返回的数据在顶层 `list` 字段
- `article list` 返回的数据在顶层 `list` 字段
- 所有工时单位均为**小时**（不是分钟）
- **⚠️ mes 0.5.3+ 服务请求命令从 `service request list` 改为 `sr list`**，且 `sr list` 不支持 `--team-id` 参数，需全局查询后由 analyze.py 按团队名称过滤
- **⚠️ 未报工数据格式陷阱**：generate_report.py 读取 `/tmp/mes_no_work_items_v2.json`（v2 格式），绝对不能只生成旧扁平格式 `mes_no_work_items.json`，否则第十一节显示为空。v2 格式每条记录是 `{contract: {...}, no_work_items: [...], has_work_items: [...]}`，不是扁平列表
- **contract list-items 返回路径**：数据在 `resp['operateCallBackObj']['list']`，不是顶层 `list`。拿到的 `actualHours=0` 才是未报工子项
- **⚠️ contract list 分页陷阱**：`--page-size 500` 在 0.5.3 版本会超时，必须用默认 page-size（15条/页）+ 分页遍历（page=1,2,3...），结合 `hasNextPage` 判断是否继续
- **企业微信 Webhook 消息生成**：`generate_wecom_summary.py` 在报告生成后执行，读取 `/tmp/mes_summary_*.json`、`/tmp/mes_no_work_items_v2.json`、`/tmp/mes_service_requests.json`（或 `/tmp/mes_service_*.json`）生成 Markdown 格式催办消息。⚠️ **默认只展示不发送**，用户确认后加 `--send` 参数才推送

### Step 3：运行分析脚本

#### 周/月报模式（直接使用 analyze.py）

```bash
python3 {SKILL_DIR}/scripts/analyze.py \
  --mode {week|month} \
  --date {YYYY-MM-DD} \
  --exclude "许文榕,杨明翰,周瑞斌" \
  --tmpdir /tmp \
  --output /tmp/mes_analysis_result.json
```

#### 季度/自定义范围模式（需用桥接脚本）

季度或跨月范围时，`analyze.py` 的 `--mode` 不支持，需用 Python 脚本调用 `run_analysis` 函数并手动计算工作日：

```python
# 桥接脚本示例（直接内联执行，无需写文件）
import sys, json
sys.path.insert(0, '{SKILL_DIR}/scripts')
from analyze import *
from datetime import date, timedelta

start = date(2026, 1, 1)
end = date(2026, 3, 31)
dates = []
d = start
while d <= end:
    if d.weekday() < 5:
        dates.append(d)
    d += timedelta(days=1)

excluded = parse_excluded("许文榕,杨明翰,周瑞斌")
standard_total = len(dates) * STANDARD_DAILY

all_teams_data, meta = run_analysis('quarter', '2026-01-01', "许文榕,杨明翰,周瑞斌", DEFAULT_TEAMS, '/tmp')
# 覆盖 meta 为自定义范围
meta = {
    'mode': 'quarter',
    'date_start': '2026-01-01',
    'date_end': '2026-03-31',
    'date_strs': [d.strftime('%Y-%m-%d') for d in dates],
    'standard_total': standard_total,
    'work_days': len(dates),
    'excluded': list(excluded),
    'target_date': '2026-01-01',
    'report_time': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'),
}
result = {'meta': meta, 'teams': all_teams_data, 'teams_config': DEFAULT_TEAMS}
with open('/tmp/mes_analysis_result.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

**注意：** 季度模式下 `run_analysis` 内部会再次调用 `get_date_range('quarter', ...)`，但其按月逻辑只返回单月日期。**必须**在执行后用上面代码手动覆盖 `meta` 的 `date_strs` 和 `standard_total`。或者，也可以直接内联执行完整分析逻辑（参考 Q1 报告生成的桥接脚本）。

### Step 4：生成 HTML 报告

根据 `single_team` 判断使用哪个报告生成器：

#### ① 四团队周/月报 → generate_report.py

```bash
python3 {SKILL_DIR}/scripts/generate_report.py \
  --input /tmp/mes_analysis_result.json \
  --output {workspace}/dongxi_{mode}_report_{date}.html
```

#### ② 四团队季度/长周期 → generate_quarter_report.py

```bash
python3 {SKILL_DIR}/scripts/generate_quarter_report.py \
  --input /tmp/mes_analysis_result.json \
  --output {workspace}/dongxi_q{quarter}_{year}_report.html
```

#### ③ 单团队/单人员 → generate_single_team_report.py（深蓝色模板）

```bash
# 单团队全量报告
python3 {SKILL_DIR}/scripts/generate_single_team_report.py \
  --input /tmp/mes_analysis_result.json \
  --output {workspace}/dongxi_team{name}_q{quarter}_{year}_report.html

# 单人员报告（只输出该人员的工作总结，其他维度正常显示全团队）
python3 {SKILL_DIR}/scripts/generate_single_team_report.py \
  --input /tmp/mes_analysis_result.json \
  --output {workspace}/dongxi_{person}_q{quarter}_{year}_report.html \
  --person "吴伟龙"
```

**三个报告生成器的区别：**

| 特性 | generate_report.py | generate_quarter_report.py | generate_single_team_report.py |
|------|-------------------|---------------------------|-------------------------------|
| 适用范围 | 周报、单月报 | 季度、跨月、自定义范围 | **单团队、单人员** |
| 团队数 | 四团队对比 | 四团队对比 | **单团队**深度分析 |
| CSS主题 | 基础样式 | 增强样式（绿色系） | **深蓝色主题**（#1a237e / #283593） |
| 工时明细 | 按天展示 | **按月聚合**展示 | **按月聚合**展示 |
| 汇总卡片 | 无 | ✅ 顶部6指标汇总卡片 | ✅ 顶部6指标KPI卡片 |
| 项目报工排名 | ❌ | ✅ 各团队TOP15 + 汇总TOP20 | ✅ **TOP20 + TOP10柱状图** |
| 维度数 | 七大维度 | 十一大维度 | **十大维度** |
| 能效排名 | 按团队 | 按团队 | **按人员**（金银铜徽章） |
| 人员工作总结 | ❌ | ✅ 简要版 | ✅ **详细版**（月度条形图+项目+工作内容） |
| `--person` 参数 | ❌ | ❌ | ✅ **支持**过滤单人员 |
| 导航栏 | 无 | 无 | ✅ **顶部锚点导航** |

### Step 5：交付结果

1. 将 HTML 报告复制到工作区
2. 用 `preview_url` 预览报告
3. 用 `deliver_attachments` 交付报告文件

### Step 5.5：生成企业微信 Webhook 总结消息

**⚠️ 默认行为：只生成消息内容并展示给用户，不自动发送。必须用户明确确认"发送"后才调用 curl 发送到 webhook。**

HTML 报告生成后，调用 `generate_wecom_summary.py` 生成企业微信催办消息。该脚本会自动采集 `/tmp/mes_summary_*.json`、`/tmp/mes_no_work_items_v2.json`、`/tmp/mes_service_*.json` 中的数据，生成以下三块内容的 Markdown 消息：

1. **报工不足提醒** — 低于标准工时的团队成员，按缺口降序排列（🔴 ≥20h、🟠 ≥10h、🟡 <10h）
2. **维保合同未报工子项** — 东西大区维保项目下 actualHours=0 的子项，取前 10 个
3. **未关闭服务请求** — 仅统计东西大区四团队成员的未关闭请求，按处理人待办数排名

**执行命令（仅生成，不发送）：**

```bash
python3 {SKILL_DIR}/scripts/generate_wecom_summary.py \
  --date-start {date_start} \
  --date-end {date_end} \
  --standard-hours {standard_hours} \
  --exclude "许文榕,杨明翰,周瑞斌" \
  --tmpdir /tmp
```

**执行后：**
1. 向用户展示生成的消息内容预览
2. 告知用户："消息已生成，请确认是否发送到企业微信 Webhook。"
3. **仅当用户明确回复"发送"、"确认发送"、"发到群里"等肯定语时**，才执行发送：

```bash
python3 {SKILL_DIR}/scripts/generate_wecom_summary.py \
  --date-start {date_start} \
  --date-end {date_end} \
  --standard-hours {standard_hours} \
  --exclude "许文榕,杨明翰,周瑞斌" \
  --tmpdir /tmp \
  --send \
  --webhook-key {webhook_key}
```

**Webhook Key 配置：**
- 默认读取环境变量 `WECOM_WEBHOOK_KEY`
- 也可通过 `--webhook-key` 参数直接传入
- 当前已知的 Webhook Key：`b2195beb-977b-4e29-8ae5-454ef7e0fbed`

**⚠️ 安全规则：**
- 绝对不可在未获用户明确同意的情况下自动发送消息
- 用户说"看一下内容"、"生成就行"等只展示不发送
- 只有用户明确说"发送"、"发出去"、"确认发送"时才执行 `--send`

**未关闭服务请求过滤规则：**
- 仅统计东西大区四团队（team-id: 2/3/23/19）的成员
- 通过 `/tmp/mes_summary_*.json` 提取全员名单，过滤服务请求的 `executorEmployeeName`
- 关闭判定关键词：`['已关闭', '关闭', '已解决', '已完成', '已结束']`

### Step 6：清理临时文件

```bash
rm -f /tmp/mes_summary_t*.json /tmp/mes_list_t*.json /tmp/mes_article_t*.json /tmp/mes_service_t*.json /tmp/mes_all_contracts.json /tmp/mes_no_work_items_v2.json /tmp/mes_analysis_result*.json
```

## 报告包含维度（严格执行）

**⚠️ 重要：每次分析四团队报工情况时，以下维度必须全部包含，不可遗漏：**

1. **四团队核心指标对比** — 总工时、人均工时、满勤率、各工时类型、文档数（含排名徽章）
2. **成员工时明细 & 每日工时** — 按天工时热力矩阵 + 售前/售后/内部/加班分解
3. **报工不足人员分析** — 工时缺口明细，高亮标识，**工作日8h/天，周六周日工时视为加班**
4. **文档编写统计** — 各团队/成员文档产出数量与标题
5. **报工质量分析** — 团队级操作标准分、零记录成员预警 + **人员质量明细表**（每人操作标准分、审批通过率、记录数、通过数、知识库、证书）
6. **项目成本消耗** — 售前/售后/内部工时占比分析（含合计行）
7. **🆕 项目报工排名（各团队TOP15）** — 按工时降序，含进度条可视化
8. **🆕 每人每周工作总结** — 按项目聚合智能总结（完成/进行中/阻塞状态）+ 后续计划 + 三维度评价 + **姓名后置「支持项目/合同」标签**
9. **🆕 服务请求列表** — 东西大区服务请求，含：①按客户排名（TOP10进度条）②按处理人排名（TOP10进度条）③服务等级分布（P0~P5彩色标签）④明细表格
10. **🆕 项目未报工分析** — 东西大区维保项目支持团队下未产生报工的合同子项，按合同分组展示（合同名称/项目经理/合同时间/子项名称/计划工时/剩余工时）
11. **综合评价** — 团队排名 + 管理建议

## 脚本文件清单

```
scripts/
├── analyze.py                        # 通用数据分析脚本（周/月报）
├── build_contract_item_map.py        # 🆕 构建 报工accId(itemId)→合同 精确映射（缓存/tmp/mes_item_contract_map.json）
├── generate_report.py                # HTML报告生成器（周/月报，七大维度，四团队）
├── generate_quarter_report.py        # HTML报告生成器（季度/长周期，十大维度，四团队，绿色系）
├── generate_single_team_report.py    # HTML报告生成器（单团队/单人员，十大维度，深蓝色主题）
└── generate_wecom_summary.py         # 企业微信 Webhook 总结消息生成（催办通知，默认不发送）
```

## MES 数据结构参考

### statistics summary 返回格式
```json
{
  "operateCallBackObj": [
    {
      "userName": "张三",
      "totalTaskTime": 40,      // 总工时（小时）
      "preTaskTime": 0,          // 售前工时
      "afterTaskTime": 38,       // 售后工时
      "internalTaskTime": 2,     // 内部工时
      "overTaskTime": 0,         // 加班工时
      "certCount": 0,
      "docCount": 1,
      "operationStandardScore": 80,
      "groupType": ""
    }
  ]
}
```

### statistics list 返回格式
```json
{
  "list": [
    {
      "executorName": "张三",
      "taskTime": 8,              // 工时（小时）
      "start": "2026-04-13 09:00:00",
      "end": "2026-04-13 18:00:00",
      "remark": "XX项目实施",
      "accName": "XX客户",
      "reviewStatus": 0           // 0=待审核, 1=已审核
    }
  ]
}
```

### article list 返回格式
```json
{
  "total": 5,
  "list": [
    {
      "account": "张三",
      "title": "Oracle 故障排查手册"
    }
  ]
}
```

### service request list 返回格式
```json
{
  "list": [
    {
      "id": "SR20260422001",
      "title": "生产库频繁出现ORA-04031",
      "statusLabel": "处理中",
      "typeLabel": "P4-咨询，业务暂未受影响",   // 级别字段，取 "-" 前前缀即 P0~P5
      "companyName": "XX客户",
      "submitterName": "提交人",
      "executorEmployeeName": "吴伟龙",           // 处理人中文姓名（优先使用）
      "executorName": "wuweilong",                // 处理人英文账号（备用）
      "createdTime": "2026-04-22 10:30:00"
    }
  ]
}
```

**服务请求关键字段说明：**
- `typeLabel`：格式 `"P4-咨询，业务暂未受影响"`，取 `-` 前的前缀（P0~P5）作为 `level`
- `executorEmployeeName`：优先使用（中文姓名），若为空则 fallback 到 `executorName`
- 第九节包含三层结构：排名分析（客户/处理人 TOP10 进度条）+ 等级分布条 + 明细表格

### contract list 返回格式（Step 2.5 第一步）
```json
{
  "list": [
    {
      "id": 2304,
      "name": "2025年XX公司Oracle运维服务合同",
      "manager": "吴伟龙",
      "contractStartTime": "2025-01-01",
      "contractEndTime": "2026-12-31",
      "endTime": "2026-12-31",
      "serviceTeams": [
        { "id": 5, "name": "东西大区维保项目支持团队" }
      ]
    }
  ]
}
```

### contract list-items 返回格式（Step 2.5 第三步）
```bash
mes -o json contract list-items --contract-id {cid}
```
```json
{
  "operateCallBackObj": {
    "list": [
      {
        "itemName": "数据库日常巡检",
        "itemType": "运维服务",
        "actualHours": 0,       // 实际报工工时，0 = 未报工
        "planHour": 40,         // 计划工时
        "remainingTask": 40     // 剩余工时
      },
      {
        "itemName": "故障应急响应",
        "itemType": "应急支持",
        "actualHours": 16,
        "planHour": 80,
        "remainingTask": 64
      }
    ]
  }
}
```
**注意**：返回路径是 `resp['operateCallBackObj']['list']`，不是顶层 `list`。

---

## 自定义团队扩展（2026-09-03 新增）

### 适用场景
默认配置只覆盖「东西大区 1/2/4/5 部」（team-id 2/3/23/19）。当目标团队是**其他部门组合**时
（如 南北大区服务2/4/5部 + 电信行业服务部），用下方一键 CLI，无需手工改脚本。

### 一键 CLI：generate_custom_teams_report.py
```bash
python3 {SKILL_DIR}/scripts/generate_custom_teams_report.py \
  --teams "南北大区服务2部:25,南北大区服务4部:11,南北大区服务5部:22,电信行业服务部:7293" \
  --from 2026-08-01 --to 2026-08-31 \
  --label "南北·电信四团队" \
  --sr-keywords "南北大区,电信行业服务部" \
  --output /path/to/report.html
```
- `--teams`：`"显示名:teamId,..."`；teamId 用 `mes dashboard team`（**无 `team list` 命令**）
- 自动完成：采集 → 分析（复用 analyze.py）→ 未报工子项（按 team-id 拉合同）→ 动态定制渲染器 → HTML
- 报告与 generate_quarter_report.py 同款 12 章节；团队配色自动分配（蓝/绿/橙/紫…）
- `--sr-member` 默认开启：SR 归属 = 「teamName 含关键词」∪「处理人/提交人 ∈ 四团队名单」
  （解决 SR.teamName 常挂在部门/维保团队名下导致按关键词漏数的问题）
- `--skip-sr` / `--skip-unreported` 可跳过对应采集

### 已知团队 id（dashboard team 实测）
| 团队 | team-id |
|------|---------|
| 南北大区服务2部（南北大区2部） | 25 |
| 南北大区服务4部（南北大区4部） | 11 |
| 南北大区服务5部（南北大区5部） | 22 |
| 电信行业服务部 | 7293 |
| 东西大区1/2/4/5部 | 2 / 3 / 23 / 19 |

### analyze.py 扩展说明（向后兼容，默认行为不变）
- `parse_service_requests(tmpdir, start, end, excluded, team_keywords=None, member_team_ids=None)`
  - `team_keywords` 默认 `['东西大区']`；`member_team_ids` 传入后启用成员并集过滤
- `run_analysis(..., sr_keywords=None, sr_member_team_ids=None)` 透传上述两参数
- 新增 `build_result(all_teams_data, meta, teams_config)`：将 SR **双写**兼容两个生成器：
  - generate_report.py（周/月报）→ `teams[first]['service_requests']`（legacy 字段 company/handler/submitTime）
  - generate_quarter_report.py（季度/长周期）→ `result['service_requests']`（字段 company_name/executor/created_time）
  - **修复**：此前季度/长周期报告 SR 章节读取顶层而 analyze 只挂团队内 → 恒为空

### 数据一致性提醒（重要）
- `statistics list --page-size 2000` 服务端偶发**短暂异常窗口**（返回部分记录，文件明显变小，
  如 t25 正常 ~1.26MB / 异常 ~1.04MB，总工时差 ~100h）。复现验证：同一命令连跑 2 次，
  若两次一致即稳定。**生成正式报告前务必校验 list 文件大小与 total 条数**，异常时重采。

### 姓名后置「合同名／实施计划」标签（2026-09-06 新增）

**需求**：每人工作总结里，直接在姓名下方列出其报工所支持的 **合同名 + 实施计划名**，
一眼看出"这周他到底在给哪些合同干活"。

**⚠️ 关键数据事实（踩坑必读）**：
- 报工记录(statistics list)的 **`accName` = 实施计划/合同子项名**（如"3人驻场"、"人天服务"），**不是合同名**
- 报工 `title` 看似合同名，实测与合同库 **0 命中**，不可用作合同名
- **`accId` == 合同子项(`mes contract list-items`)的 `itemId`** → 可**精确关联**（实测 61/66 命中）
- 子项自带 `companyName`（= **合同名**）、`contractNum`（合同编号）、`itemName`（= accName）

**实现（三个生成器均已支持，样式统一靛蓝标签条）**：

1. 先构建映射缓存（约 1~2 分钟，388 合同并行拉子项）：
```bash
python3 {SKILL_DIR}/scripts/build_contract_item_map.py            # 有缓存直接用
python3 {SKILL_DIR}/scripts/build_contract_item_map.py --refresh  # 强制重建（合同有新增时）
```
   缓存 `/tmp/mes_item_contract_map.json`：`by_item_id`（accId 精确主路径）+ `by_item_name`（同名模糊兜底，
   多合同时按报工 `companyName` 消歧）

2. 生成器自动解析并渲染 `合同名／实施计划` 标签：
| 生成器 | 章节 | 数据源 |
|--------|------|--------|
| `generate_quarter_report.py` | 八-A 每人季度/本周/每月工作总结 | 原始 list 的 accId/accName/companyName |
| `generate_report.py` | 八、每人每周工作总结 | `person_daily`（analyze.py 已补 accId/companyName 字段） |
| `generate_single_team_report.py` | 7. 每人工作总结 | `calc_project_ranking` 返回的 person_acc_meta |

- 显示规则：合同名加粗在前、实施计划名淡色在后；**合同名与实施计划名互为包含时只显示更长者**（避免"德邦证券／德邦证券"式冗余）
- 无合同映射缓存时**静默降级**为仅显示实施计划名；无任何报工项目显示灰色斜体「本期报工无关联项目」
- 实测命中率 97~98%（未命中者多为合同库外的内部报工/非常规子项）
- CSS 类：`.person-contracts` / `.pc-label` / `.pc-tag` / `.pc-sub` / `.pc-empty`

**⚠️ 踩坑 1：`generate_report.py` 内不可直接用 `Counter`**
该函数后半段（第九节 9.1）有局部 `from collections import Counter`，会把 `Counter` 变成
**函数局部变量**，导致在其之前（第八节）调用 `Counter()` 抛
`UnboundLocalError: cannot access local variable 'Counter'`。
第八节需改用**普通 dict 累加**再 `sorted(..., key=lambda x: -x[1])[:8]`。

**⚠️ 踩坑 2：自定义 CLI 渲染器在 tmpdir 运行**
`generate_custom_teams_report.py` 把 generate_quarter_report.py 拷贝为 `/tmp/gen_custom_report.py` 执行，
导致渲染器相对导入 `build_contract_item_map` 失败并静默降级。render_report 已修复为**同步拷贝该模块到 tmpdir**。

### 周期自适应（2026-09-06 新增）
`generate_custom_teams_report.py` 按统计跨度自动适配分组粒度与措辞：
- **≤7 天（周报）**：第二节改为「按日汇总」（每日一列，标准 8h），第八节「每人本周工作总结」——避免跨月周报被拆成 2026-08/2026-09 两列
- **≤45 天（月报）**：维持按月分组，第八节「每人每月工作总结」
- **更长（季度）**：保持基础模板默认（按月分组 + 季度措辞）
