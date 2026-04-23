---
name: mes-report
description: 生成东西大区4部队报工统计文本，直接推送至微信。When user asks to generate/create/extract work-hour statistics report for their team, use this skill to query MES and output a formatted text report for WeChat delivery.
---

# MES 报工统计 Skill

## 使用方式

用户说「生成报工统计」「生成本周报工」「输出报工」时使用。

## 执行命令

```bash
python3 /root/.openclaw/workspace/scripts/weekly_report.py auto
```

输出为微信友好的纯文本格式，包含：
- 核心统计（总工时/人数/记录数）
- 每人每日明细（✅正常 / ❗不足 / 休）
- 短工时条目（<10字）
- 未报工人员
- 缺口分析

## 定时任务

- 每天 9:00 自动生成并推送微信
- cron ID: `b62d1735-e727-4ac5-b8d1-347c109bf4db`
