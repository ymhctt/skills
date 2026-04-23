---
name: mes-report
description: Generate comprehensive HTML work-hour statistics reports from MES data. Use when users ask to generate, create, or output a work-hour statistics report in HTML format, similar to the "东西大区四团队报工分析" format. Supports single team or multi-team reports with daily breakdown, project distribution, overtime analysis, and quality metrics.
---

# MES 报工统计报告生成 Skill

根据 MES CLI 数据，生成美观的 HTML 格式报工统计分析报告。

## 核心概念

- **输入**：团队ID、日期范围（默认本周）、是否包含多个团队
- **输出**：独立 HTML 文件，可直接在浏览器打开，支持微信直接推送
- **数据来源**：`mes statistics list` + `mes util list-members`

## 使用方式

### 触发条件
- 用户说「生成报工报告」「输出报工统计」「生成本周报工 HTML」
- 用户说「报工分析报告」「周报工统计表」
- 用户要求「按团队输出报工统计」

### 必需参数
- `team_ids`: 团队ID列表（可多个，如 `["23", "96"]`）
- `team_names`: 团队名称映射（如 `{"23": "东西大区4部", "96": "东西大区"}`）
- `from_date`: 开始日期（YYYY-MM-DD）
- `to_date`: 结束日期（YYYY-MM-DD）
- `output_path`: HTML 输出路径

### 可选参数
- `standard_hours`: 标准周工时（默认 40）
- `daily_standard`: 每日标准工时（默认 8）

## 执行流程

1. 验证 MES CLI 登录状态
2. 获取各团队成员列表
3. 查询日期范围内的所有报工记录
4. 按人员/日期/项目维度聚合
5. 计算指标：总工时、人均、满勤率、加班、缺口
6. 生成 HTML 报告
7. 输出文件路径

## HTML 报告结构

```html
<!-- 包含完整 CSS，无外部依赖 -->
<!-- 11 个主要板块 -->
<!-- 1. 核心指标对比（团队卡片） -->
<!-- 2. 工时明细（每日每人表格） -->
<!-- 3. 报工不足分析 -->
<!-- 4. 文档统计（如有 article 数据） -->
<!-- 5. 项目成本分布 -->
<!-- 6. 报工质量分析 -->
<!-- 7. 项目报工排名 -->
<!-- 8. 每人工作总结（备注摘要） -->
<!-- 9. 服务请求工时（如有） -->
<!-- 10. 综合评价 -->
<!-- 11. 未报工分析 -->
```

## 报告生成命令

```bash
python3 /root/.openclaw/workspace/skills/mes-report/skills/generate_report.py \
  --team-id 23 \
  --team-name "东西大区4部" \
  --from 2026-04-20 \
  --to 2026-04-24 \
  --output /tmp/report_20260420.html
```

### 多团队模式

```bash
python3 .../generate_report.py \
  --teams "23:东西大区4部,96:东西大区" \
  --from 2026-04-20 \
  --to 2026-04-24 \
  --output /tmp/report_multi.html
```

## 注意事项

- MES `type` 字段含义：0=标准工时, 1=实施/项目工时, 3=内部事项
- `overtimeType=0` 的条目为加班工时
- `serviceType=2` 的记录属于服务请求关联工时
- 报告默认保存到 `/tmp/`，文件名包含日期范围
