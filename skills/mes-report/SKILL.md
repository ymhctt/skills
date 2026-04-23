---
name: mes-report
description: 东西大区4部队报工统计。当用户说「生成报工统计」「生成本周报工」「输出报工」时使用此skill。
---

# MES 报工统计 Skill

## 执行命令

```bash
python3 /root/.openclaw/workspace/scripts/weekly_report.py auto
```

输出 JSON，含：
- `text`: 微信纯文本格式（可直接发送）
- `html_path`: HTML 报告文件路径（需作为附件发送）
- `from_date` / `to_date`: 统计日期范围

## 推送要求

每天9点定时任务必须同时发送：
1. **文本内容** → 直接粘贴到微信消息
2. **HTML文件** → 作为附件发送

## 定时任务
- cron ID: `4687754d-a8d5-4e5d-bdce-5bee9062b462`
- 每天 9:00 自动执行
