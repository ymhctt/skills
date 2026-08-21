---
name: mes_project_skill
description: MES项目服务总结报告/项目进展分析报告生成技能。基于MES系统的报工数据、服务请求、合同子项等信息，自动生成专业的HTML报告和企业微信消息。当用户提到"项目报告"、"服务总结"、"进展分析"、"验收报告"、"汇报"、"项目状态"、"工时统计"、"报工"、"合同执行"等关键词时触发此技能。适用于项目验收、阶段性汇报、客户交付、项目进展跟踪、企业微信推送等场景。即使用户没有明确说"生成报告"，只要涉及MES项目数据的整理、分析或展示，都应使用此技能。
compatibility:
  tools:
    - mes-cli (MES命令行工具，用于查询服务请求、报工记录、合同数据)
    - curl (用于企业微信webhook推送)
---

# MES项目服务总结/进展分析技能

## 功能说明

基于MES系统数据自动生成专业的项目报告，支持两种模式：

## 配置

在技能目录下创建 `config.json` 文件，可配置以下选项：

```json
{
  "auto_send_webhook": false,
  "webhook_url": "",
  "email": {
    "enabled": false,
    "smtp_host": "smtp.example.com",
    "smtp_port": 465,
    "smtp_user": "",
    "smtp_pass": "",
    "from": "reports@example.com",
    "template": {
      "A": "email_template_a.html",
      "B": "email_template_b.html",
      "C": "template_data_report.html"
    },
    "contracts": {
      "东山精密": {
        "to": ["zhangsan@example.com", "lisi@example.com"],
        "cc": ["wangwu@example.com"],
        "template": {
          "A": "email_template_a_starbucks.html",
          "B": "email_template_b_starbucks.html"
        }
      },
      "华为技术": {
        "to": ["admin@huawei.com"],
        "cc": ["manager@huawei.com", "support@huawei.com"]
      }
    }
  }
}
```

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `auto_send_webhook` | boolean | false | 是否自动发送企业微信消息（跳过用户确认） |
| `webhook_url` | string | "" | 企业微信webhook地址（配置后无需每次询问） |
| `email.enabled` | boolean | false | 是否启用邮件发送功能 |
| `email.smtp_host` | string | "" | SMTP服务器地址 |
| `email.smtp_port` | number | 465 | SMTP端口（465为SSL，587为TLS） |
| `email.smtp_user` | string | "" | SMTP用户名 |
| `email.smtp_pass` | string | "" | SMTP密码 |
| `email.from` | string | "" | 发件人地址 |
| `email.template` | object | {"A": "email_template_a.html", "B": "email_template_b.html", "C": "template_data_report.html"} | 默认邮件模板文件名（位于 `assets/` 目录下），A=服务总结，B=进展分析，C=数据报告；合同未单独配置时使用这里的默认值 |
| `email.contracts` | object | {} | 按合同名称配置收件人、抄送人，以及可选的客户级模板覆盖 |

**邮件配置说明**：
- `email.contracts` 的 key 为合同名称（支持模糊匹配）
- `to` 为收件人列表，`cc` 为抄送人列表
- 可选 `template` 字段用于客户级模板覆盖，例如：
  - `template.A`：该客户的服务总结邮件模板
  - `template.B`：该客户的进展分析邮件模板
  - `template.C`：该客户的数据报告模板
- 模板选择优先级：`email.contracts[匹配合同].template.<模式>` → `email.template.<模式>`
- 匹配规则：合同名称包含配置的 key 即命中（如"东山精密数据库维保"会匹配"东山精密"）
- 未匹配到的合同不发送邮件（安全兜底）

**行为说明**：
- `auto_send_webhook: false`（默认）：生成报告后展示内容，等待用户确认并提供webhook URL
- `auto_send_webhook: true` + `webhook_url` 已配置：生成报告后自动发送，无需用户确认
- `auto_send_webhook: true` + `webhook_url` 为空：生成报告后询问用户webhook URL，确认后发送
- `email.enabled: true`：生成报告后自动发送邮件给配置的收件人

**模式A：服务总结报告**（适用于项目验收/阶段性汇报）
- 合同执行情况（合同子项、工时消耗）
- 服务人天分类分析（饼图+柱状图）
- 完整服务清单明细（真实报工数据）
- 交付文档清单
- 交付团队与工时分布
- 故障处理成果
- 交付价值总结

**模式B：项目进展分析**（适用于项目进行中/进度跟踪）
- 项目概览与KPI速览
- 执行团队与分工
- 服务请求明细与状态
- 报工详情与时间线
- 风险点分析（从报工remark中提取）
- 下一步建议

## 数据查询策略

### 核心原则

MES系统中，一个客户可能有多个合同，一个合同有多个子项。数据查询需要精确到合同子项级别，否则会混入其他项目的工时，导致报告数据失真。

### 查询流程

```bash
# Step 1: 获取目标合同的公司ID和合同ID
mes -o json contract list
# 搜索项目关键词，找到 companyId 和 contractId

# Step 2: 查询服务请求（按公司ID+时间范围）
mes -o json service request list --company-id {公司ID} --start-time "2026-01-01 00:00:00" --end-time "2026-12-31 23:59:59" --page-size 200 > /tmp/requests.json

# Step 3: 获取合同子项
mes -o json contract list-items --contract-id {合同ID} --page-size 50 > /tmp/contract_items.json

# Step 4: 按子项查询报工（每个子项单独查询，确保数据准确）
mes -o json statistics list --acc-id {子项ID1} --from 2026-01-01 --to 2026-12-31 --page-size 1000 > /tmp/work_1.json
mes -o json statistics list --acc-id {子项ID2} --from 2026-01-01 --to 2026-12-31 --page-size 1000 > /tmp/work_2.json

# Step 5: 合并去重（根据 id 字段），再按 executorName 统计工时
```

**为什么不能用 `--title` 搜索服务请求？**
标题关键词搜索会遗漏大量未包含关键词但实际关联该项目的工单。用 `--company-id` + 时间范围可以获取该客户在指定时间段内的所有服务请求。

**为什么报工必须用 `--acc-id` 查询？**
`--company-id` 会返回该客户所有项目的工时，混入无关数据。`--acc-id` 精确到合同子项，确保只统计目标项目的工时。

### 数据校验

生成报告前，需要校验以下关键字段：
- **executorName**：报工记录的执行人姓名，为空说明查询方式有误
- **accId**：每条报工必须属于目标合同子项
- **remark**：抽查备注内容，确认与目标项目相关
- **taskTime**：工时统计字段（单位：小时）
- **createdTime**：报工创建时间（用于时间线和报工详情的日期显示，注意不要用 `startTime`，该字段可能为空）

## 执行流程

### Step 1: 数据采集

按上述查询流程获取：
1. 服务请求数据（`/tmp/requests.json`）
2. 合同子项数据（`/tmp/contract_items.json`）
3. 报工记录数据（按子项查询后合并）

### Step 2: 数据分析

1. **按合同/子项分类**（accId/accName）
2. **按服务类型分类**（故障处理、巡检、安装部署等）
3. **统计真实工时消耗**（taskTime字段）
4. **提取报工内容**（remark字段）— 逐条阅读，提取关键里程碑
5. **阅读服务请求内容**（title、typeLabel、status）— 判断项目阶段
6. **按人员统计工时分布**
7. **交叉分析项目进展**：
   - 从报工 remark 中提取实际完成的工作
   - 从服务请求 title 和状态判断当前活跃任务
   - 结合合同子项完成率判断整体进度
   - 识别关键里程碑

### Step 3: 生成HTML报告

根据项目阶段选择模式，再按以下优先级确定邮件/报告模板：
- **模式A（服务总结）** → `assets/{email.contracts[匹配合同].template.A}`，未配置则回退 `assets/{email.template.A}`（默认 `email_template_a.html`）
- **模式B（进展分析）** → `assets/{email.contracts[匹配合同].template.B}`，未配置则回退 `assets/{email.template.B}`（默认 `email_template_b.html`）
- **模式C（数据报告）** → `assets/{email.contracts[匹配合同].template.C}`，未配置则回退 `assets/{email.template.C}`（默认 `template_data_report.html`）

### Step 4: 展示结果

生成报告后，同时展示以下两项内容（不自动发送）：
1. **HTML报告** — 使用 `preview_url` 打开报告文件
2. **企业微信消息内容** — 按标准格式输出完整markdown消息文本，供用户审阅

### Step 5: 消息推送

根据 `config.json` 配置决定推送行为：

**企业微信推送**：
- **auto_send_webhook: false**（默认）：展示消息内容，等待用户确认并提供webhook URL
- **auto_send_webhook: true** + webhook_url已配置：自动发送，无需用户确认
- **auto_send_webhook: true** + webhook_url为空：询问用户webhook URL，确认后发送

**邮件推送**（需配置 `email.enabled: true`）：
- 从 `email.contracts` 中查找匹配当前合同名称的配置
- 匹配规则：合同名称包含配置的 key（如"东山精密数据库维保"匹配"东山精密"）
- 找到匹配配置后，使用 SMTP 发送邮件给 `to` 收件人，抄送 `cc` 人员
- 未匹配到配置则跳过邮件发送
- 每个模式单独发送一封邮件，邮件正文即为 HTML 报告（非附件）
- 邮件主题：`【{合同名称}】服务总结报告 - {日期}` 或 `【{合同名称}】项目进展分析 - {日期}`
- 邮件正文：直接渲染完整 HTML 报告，MIME 类型为 `text/html`

## 企业微信消息格式

```
【{PROJECT_NAME} - 最新进展】（{YYYY-MM-DD}）

📋 项目概览
• 客户：{CLIENT_NAME}
• 目标：{PROJECT_GOAL}
• 启动时间：{START_DATE}
• 当前状态：<font color="{STATUS_COLOR}">{STATUS}</font>（截至 {STATUS_DATE}）

👥 执行团队
• {NAME}（{TEAM}）：{TASKS} | 报工{HOURS}h

📊 KPI速览
• 服务请求：{TICKET_COUNT}个（已关闭{CLOSED_COUNT}个）
• 总报工工时：{TOTAL_HOURS}h
• 客户对接人：{CONTACT}

⚠️ 核心风险点
🔴 高风险：{RISK_1}
🔴 高风险：{RISK_2}
🟡 中风险：{RISK_3}
🟡 中风险：{RISK_4}
🟡 中风险：{RISK_5}

🎯 下一步建议
• {STEP_1}
• {STEP_2}
• {STEP_3}
```

**状态颜色规则**：
- 🟢 `<font color="green">` — 项目正常推进/已上线/已完成
- 🔵 `<font color="info">` — 实施中/进行中（蓝色）
- 🟡 `<font color="warning">` — 存在风险但可控/延期预警（橙色）
- 🔴 `<font color="red">` — 严重阻塞/需要升级处理（红色）

**STATUS_DATE**：取最近一次报工或最近服务请求的日期（格式 YYYY-MM-DD），表示状态截止时间。

**发送命令示例**：

```bash
curl -s -X POST '{WEBHOOK_URL}' \
  -H 'Content-Type: application/json' \
  -d '{
  "msgtype": "markdown",
  "markdown": {
    "content": "【{PROJECT_NAME} - 最新进展】（{YYYY-MM-DD}）\n\n📋 项目概览\n• 客户：{CLIENT_NAME}\n• 目标：{PROJECT_GOAL}\n• 启动时间：{START_DATE}\n• 当前状态：<font color=\"{STATUS_COLOR}\">{STATUS}</font>（截至 {STATUS_DATE}）\n\n👥 执行团队\n• {NAME}（{TEAM}）：{TASKS} | 报工{HOURS}h\n\n📊 KPI速览\n• 服务请求：{TICKET_COUNT}个（已关闭{CLOSED_COUNT}个）\n• 总报工工时：{TOTAL_HOURS}h\n• 客户对接人：{CONTACT}\n\n⚠️ 核心风险点\n🔴 高风险：{RISK_1}\n🔴 高风险：{RISK_2}\n🟡 中风险：{RISK_3}\n🟡 中风险：{RISK_4}\n🟡 中风险：{RISK_5}\n\n🎯 下一步建议\n• {STEP_1}\n• {STEP_2}\n• {STEP_3}"
  }
}'
```

## 项目阶段参考（一体机项目标准流程）

项目进展必须基于实际报工内容和服务请求内容来判断，参照以下标准阶段：

| 阶段 | 典型工作内容 | 报工关键词 |
|---|---|---|
| **工勘调研** | 硬件盘点、确认架构类型、确认存储网络类型、软件物料确认 | "盘点"、"调研"、"确认"、"硬件"、"架构" |
| **项目启动会** | 项目启动会材料编写、与客户对齐项目交付标准交付内容、交付边界 | "启动会"、"对齐"、"交付标准" |
| **方案规划** | IP地址规划、网络拓扑设计、端口矩阵确认、服务器机柜、操作系统版本、一体机软件容量等规划设计 | "规划"、"拓扑"、"IP"、"方案" |
| **设备上架** | 服务器上架、布线、IB卡/RoCE卡安装、BIOS参数设置、RAID配置、BMC地址配置 | "上架"、"布线"、"IB卡"、"RoCE"、"BIOS"、"RAID"、"BMC" |
| **操作系统安装** | 存储交换机配置 | "操作系统"、"安装"、"存储交换机" |
| **管理平台部署** | 部署监控节点、创建机柜信息、纳管交换机 | "监控"、"纳管"、"管理平台" |
| **融合节点部署** | 部署融合节点、申请许可证、初始化存储集群 | "融合节点"、"许可证"、"存储集群"、"初始化" |
| **数据库安装** | 安装数据库软件、配置数据库实例 | "数据库"、"安装"、"实例"、"配置" |
| **性能测试** | IO性能测试、数据库性能测试、高可用测试 | "性能测试"、"FIO"、"TPMCC"、"高可用" |
| **归档提交** | 测试报告、一体机巡检、档案提交 | "测试报告"、"巡检"、"档案" |
| **正式上线** | 正式上线 | "上线"、"切换"、"割接" |
| **数据迁移** | 如有迁移服务则提前迁移方案、保障方案 | "迁移"、"切换上线"、"割接"、"同步" |
| **使用培训** | 使用培训 | "培训" |
| **项目验收** | 项目验收材料准备 | "验收"、"验收材料" |
| **维保服务** | 故障处理、巡检、性能优化、咨询支持 | "故障"、"巡检"、"优化"、"咨询"、"SPA" |

**进展判断示例**：
- 报工内容："数据库迁移完成，已切换上线" → 项目已进入**生产运行/维保阶段**
- 报工内容："SPA性能分析"（迁移场景） → **迁移上线后的性能验证**，非独立阶段
- 报工内容："服务器上架完成，开始安装操作系统" → **设备上架阶段**
- 服务请求全部已关闭且最近报工为"日常巡检" → **维保阶段**

## 报告模板

### 模式A模板（template_a.html）- 服务总结报告

适用于项目验收/阶段性总结：
1. 服务报告概述
2. 合同执行情况（合同子项+进度条）
3. 服务人天分类分析（Chart.js图表）
4. 交付文档清单
5. 服务清单明细（真实报工数据）
6. 交付团队与工时分布
7. 部分故障处理成果
8. 服务结论 - 交付价值总结

### 模式B模板（template_b.html）- 项目进展分析

适用于项目进行中/进度跟踪：
1. 项目概览
2. KPI速览卡片
3. 执行团队与分工
4. 服务请求明细
5. 报工详情
6. 实施进度时间线
7. 当前风险点（从remark提取）
8. 下一步建议

### 模式C模板（template_data_report.html）- 数据报告

适用于强调数据看板/汇总呈现的场景：
1. 服务报告概述
2. KPI速览
3. 合同执行情况
4. 数据分析图表
5. 服务清单明细
6. 团队工时分布
7. 结论摘要

### 多风格模板扩展约定

为支持 design 目录中的多种设计风格，浏览器版报告模板允许按“报告用途 × 风格”扩展，但必须遵守以下规则：

1. **只替换视觉，不改数据契约**
   - 必须保留现有 Mustache token / section 名称。
   - 不允许引入新的必填 token。
   - 生成侧应继续复用现有数据整理逻辑。

2. **保留章节语义与顺序**
   - 模式A：KPI → 合同执行 → 服务分析 → 交付文档/服务清单 → 团队 → 案例/结论。
   - 模式B：项目概览 → KPI → 团队 → 请求 → 时间线 → 风险 → 报工 → 建议。
   - 模式C：概览 → KPI → 合同执行 → 数据分析 → 服务清单 → 团队 → 结论。

3. **允许调整的内容**
   - 配色、字体、圆角、阴影、留白、栅格、卡片样式、表格样式。
   - Chart.js 图表的视觉样式。
   - 若某风格更适合静态表达，可将部分图表替换为进度条、统计卡或摘要表，但不能丢失原有信息。

4. **推荐命名规范**
   - `template_service_summary_<style>.html`
   - `template_progress_analysis_<style>.html`
   - `template_data_report_<style>.html`
   - 其中 `<style>` 建议使用：`anthropic`、`apple`、`claude`、`cursor`、`figma`、`notion`、`playstation`、`raycast`、`starbucks`、`xai`。

5. **模板选择约定**
   - `email.template.A`：模式A模板文件名
   - `email.template.B`：模式B模板文件名
   - `email.template.C`：模式C模板文件名
   - 默认值分别为 `template_a.html`、`template_b.html`、`template_data_report.html`

6. **邮件模板边界**
   - `email_template_a.html`、`email_template_b.html` 用于邮件兼容正文。
   - 多风格扩展默认只针对浏览器预览版 HTML，不自动扩展邮件兼容模板。

## 样式规范

采用暖色编辑主题（coral #cc785c / teal #5db8a6 / amber #e8a55a）：
- 奶油色画布背景（#faf9f5）
- Google Fonts：Cormorant Garamond（标题）、Inter（正文）、JetBrains Mono（代码）
- KPI汇总卡片
- Chart.js交互式图表（模式A）
- 响应式布局

## 文件清单

```
mes_project_skill/
├── SKILL.md                          # 技能说明文档
├── config.json                       # 配置文件（可选）
└── assets/
    ├── template.html                 # 模式A：服务总结报告（参考示例）
    ├── template_a.html               # 模式A：服务总结报告模板（默认）
    ├── template_progress.html        # 模式B：项目进展分析（参考示例）
    ├── template_b.html               # 模式B：项目进展分析模板（默认）
    ├── template_data_report.html     # 模式C：数据报告模板（默认）
    ├── template_service_summary_<style>.html
    ├── template_progress_analysis_<style>.html
    ├── template_data_report_<style>.html
    ├── email_template_a.html         # 邮件兼容：服务总结报告（默认）
    ├── email_template_b.html         # 邮件兼容：项目进展分析（默认）
    ├── email_template_a_starbucks.html
    └── email_template_b_starbucks.html
```
