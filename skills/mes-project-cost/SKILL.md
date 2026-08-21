---
name: mes-project-cost
description: MES 项目交付成本分析自动化技能。根据合同名称和金额，自动从 MES 拉取合同、订单、报工数据，结合人员成本配置，生成 Markdown 分析报告和 HTML 可视化报告。
---

# MES 项目交付成本分析技能

## 触发条件

当用户提供以下信息时启用：
- 合同名称 + 合同金额
- 要求分析项目成本、报工情况、交付预算
- 提到"项目成本分析"、"交付报告"、"合同成本"

## 用户只需提供

```
合同名称：<name> 或 合同编号：<no>
合同金额：<amount>（可选，MES 中有则不需要提供）
利润率：<rate>（可选，默认 50%）
人员配置：使用默认配置文件 或 指定新的 JSON
```

## 完整流程

### Phase 1: 数据获取

使用 `mes` CLI 拉取数据（所有命令用 `mes -o json` 输出 JSON 格式）：

#### Step 1.1 — 查询合同信息

```bash
mes -o json contract list --search <关键词> --page-size 50
```

**注意**：`contract list --search` 对中文关键词过滤效果差。如果搜不到：
1. 先用宽泛关键词（如年份）搜索
2. 在返回的列表中人工筛选匹配的合同

从结果中提取：
- `contractId` 或 `id`: 合同 ID（整数，后续查询用）
- `contractNo`: 合同编号
- `contractName`: 合同名称
- `companyName` / `companyId`: 客户公司名称和 ID
- `contractManager`: 合同负责人
- `serviceDesc`: 服务简述
- 合同期间

#### Step 1.2 — 查询合同详情

```bash
mes -o json contract view <合同ID>
```

获取财务信息：订单金额、PO外购、核算外购、PO自有等。

#### Step 1.3 — 查询合同子项（关键！）

```bash
mes -o json contract list-items --contract-id <合同ID>
```

从结果提取所有子项 ID（`itemId`）。**必须获取全部子项**，不可遗漏。

每个子项包含：
- `itemId`: 子项 ID（后续报工查询用）
- `itemName`: 子项名称
- `itemType`: 子项类型（如"部署-zDataX"、"维保-zDataX"）
- `planHour`: 计划工时
- `actualHours`: 已用工时
- `ownerName`: 负责人
- `startTime` / `endTime`: 期间

#### Step 1.4 — 查询报工记录（按每个子项逐一查询）

**⚠️ 关键：MES 报工关联的是合同子项 (acc-id)，不是公司 ID。** 必须对每个子项单独查询。

```bash
# 对每个子项 ID 执行：
mes -o json statistics list --acc-id <子项ID> --from <开始日期> --to <结束日期> --page-size 200
```

**关键字段**：
- `executorName`: 报工人员姓名
- `executorId`: 报工人员 ID
- `taskTime`: 报工工时（小时数）
- `createdTime`: 报工创建时间
- `accId`: 合同子项 ID
- `remark`: 报工内容描述

**合并所有子项的报工记录** 到一个数组中，用于后续计算。

#### Step 1.5 — 查询实施计划

```bash
mes -o json plan list --company-id <公司ID> --page-size 200
```

#### Step 1.6 — 查询订单信息

从合同详情中提取订单列表，或单独查询：
- `order_name`: 订单名称
- `order_amount`: 订单金额
- `po_outsource`: PO外购金额
- `account_outsource`: 核算外购金额
- `po_own`: PO自有金额

### Phase 2: 准备数据文件

> **⚠️ 铁律：所有临时文件 MUST 直接从 MES CLI 输出写入，绝不可手动构造、编辑或复制粘贴修改其中任何字段（尤其是 executorName、accId 等关键字段）。上一条合同的残留数据绝不可带入当前合同。**

将所有数据写入临时文件，供计算脚本使用：

```bash
# 1. 合同信息（直接从 mes 输出写入，不可手动编辑）
# 写入 /tmp/mes_contract.json

# 2. 合同子项（MES 原始 JSON，不可修改）
# 写入 /tmp/mes_sub_items.json

# 3. 订单明细（数组格式，从 MES 获取）
# 写入 /tmp/mes_orders.json

# 4. 报工记录（所有子项合并后的数组，直接来自 MES API）
# ⚠️ 每条记录的 executorName 必须与 MES 原始返回完全一致
# 写入 /tmp/mes_time_records.json
```

**重要**：
- 报工记录必须包含所有子项的数据，且每条记录必须有 `accId` 字段
- **禁止**手动创建或修改报工记录中的 `executorName` 字段
- **禁止**复用上一个合同的临时文件数据
- 写入前用 Python 验证：`python3 -c "import json; d=json.load(open('/tmp/mes_time_records.json')); print(set(r.get('executorName','?') for r in d))"`

### Phase 3: 人员成本配置

#### Step 3.1 — 读取全局人员成本配置

```
全局配置路径: <skill_dir>/configs/staff.json
```

从报工记录中提取所有唯一 `executorName`，在 `staff.json` 中按姓名精确匹配月薪。

**如果报工人员不在配置中**：
1. 向用户询问该人员的月薪和角色
2. 追加到 `staff.json` 中供后续项目复用

**时薪自动计算**：`月薪 ÷ (21.75 × 8) = 月薪 ÷ 174`

### Phase 4: 成本计算

```bash
python3 <skill_dir>/references/scripts/calc_cost.py \
  --contract /tmp/mes_contract.json \
  --sub-items /tmp/mes_sub_items.json \
  --orders /tmp/mes_orders.json \
  --time-records /tmp/mes_time_records.json \
  --staff <skill_dir>/configs/staff.json \
  --profit-rate 0.5 \
  --output /tmp/mes_cost_result.json
```

计算逻辑：
- 人员成本 = 时薪 × 报工工时
- 外购成本 = 核算外购合计
- 总成本 = 外购 + 人工
- 毛利 = 合同总额 - 总成本
- 毛利率 = 毛利 / 合同总额
- 交付预算 = PO 自有金额 × 15%
- 交付利润 = 预算 × 利润率（默认 50%）
- 最大允许成本 = 预算 - 交付利润

### Phase 5: 报告生成

#### Step 5.1 — 生成 HTML 可视化报告

```bash
python3 <skill_dir>/references/scripts/generate_html.py \
  --input /tmp/mes_cost_result.json \
  --output "<workspace>/<合同名称> 交付分析.html"
```

报告包含以下章节（参照晶科能源模板）：
1. Header — 项目名称、合同编号、数据截止日期
2. 收入→成本→利润流程图
3. KPI 卡片（合同总额、外购、人工、毛利）
4. 合同基本信息表
5. 合同子项表（含完成度）
6. 订单明细表（含外购差异分析）
7. 报工工时汇总表（按人员 + 按子项）
8. 报工明细表（逐条列出）
9. 成本分析（饼图 + 说明）
10. 15% 预算使用率（半圆环图）
11. 交付利润约束分析（饼图 + 详细表格）
12. 交付+维保预算表
13. 人员成本柱状图 + 成本表
14. 报工时间线图
15. 订单对比图
16. 关键发现与建议

#### Step 5.2 — 预览

使用 `preview_url` 工具预览 HTML 报告。

### Phase 6: 清理

删除所有临时文件：
```bash
rm -f /tmp/mes_contract.json /tmp/mes_sub_items.json /tmp/mes_orders.json \
      /tmp/mes_time_records.json /tmp/mes_cost_result.json
```

## 关键规则

1. **不写死数据** — 所有数据从 MES 动态拉取
2. **人员配置全局共享** — `configs/staff.json` 按姓名匹配所有项目，维护一份即可
3. **按子项查报工** — MES 报工关联的是 acc-id，不是 company-id。必须逐一查询每个子项
4. **多子项聚合** — 合同可能有多个子项（如部署+维保），必须全部查询并合并
5. **最小输入** — 用户只需提供合同名称和金额即可开始
6. **自动匹配** — 从报工记录自动提取人员，匹配已有配置
7. **利润率可调** — 默认 50%，可在输入时指定
8. **验证报工完整性** — 生成报告后，核对报工人员是否与 MES 实际一致

## 常见陷阱

### 陷阱 1：只查一个子项，遗漏其他子项报工

**症状**：报工工时偏少，某些人员（如熊群）的维保报工被遗漏。

**原因**：合同有多个子项（如部署子项 + 维保子项），但只查询了第一个子项。

**修复**：先 `contract list-items` 获取所有子项 ID，对每个子项执行 `statistics list --acc-id`。

### 陷阱 2：人员姓名匹配错误

**症状**：报工人员显示为"许文榕"，但实际执行人是"熊群"。

**原因**：从报工 JSON 提取姓名时用了错误的字段名，或 MES 字段名不一致。

**修复**：MES 报工 API 使用 `executorName` 字段（不是 `executor` 或 `executor_name`）。calc_cost.py 中的 `get_field` 函数已处理多字段名兼容。

### 陷阱 3：contract list --search 中文搜索失败

**症状**：搜索"天门医院"返回不相关合同。

**原因**：MES `contract list --search` 对中文关键词过滤效果差。

**修复**：用宽泛关键词（如年份"2025"）搜索，然后在返回列表中人工筛选。

### 陷阱 4：f-string 三元运算符

**症状**：Python f-string 中写 `{x if cond else y}` 会报 SyntaxError。

**修复**：在 f-string 外预计算变量。

## 文件结构

```
~/.workbuddy/skills/mes-project-cost/
├── SKILL.md                          # 本文件（流程定义）
├── configs/                          # 全局共享人员成本配置
│   └── staff.json                    # 所有项目共用一份，按姓名匹配
└── references/
    ├── config-template.md            # 人员成本配置模板（说明格式）
    └── scripts/
        ├── calc_cost.py              # 成本计算引擎
        └── generate_html.py          # HTML 报告生成器
```

## 示例交互

**用户输入**：
> 分析 2026 晶科能源海宁工厂 zData X 项目，合同金额 3,038,128

**技能执行**：
1. 从 MES 查询合同信息 → 获取合同编号、客户、负责人等
2. 查询所有合同子项 → 获取每个子项的 acc-id
3. 对每个子项查询报工 → 合并所有报工记录
4. 匹配人员配置 → 读取 `configs/staff.json`，按姓名匹配月薪（新人则询问并追加）
5. 运行 `calc_cost.py` → 计算成本
6. 运行 `generate_html.py` → 生成 HTML 可视化报告
7. 预览 HTML，交付结果
