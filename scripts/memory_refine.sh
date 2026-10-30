#!/bin/bash
# 每小时 Memory 提炼落盘脚本 —— 纯静默，不产生任何对话消息
#
# ⚠️ 2026-10-29 修复：此脚本曾作为 isolated command job 运行，
#    其 stdout 会被 OpenClaw 捕获并回灌到爸爸的微信对话（10/29 05:07~17:07 共 25 条）。
#    现在 cron 6da766bb 已改为 main + system-event（无 delivery），
#    且本脚本 **所有输出全部重定向到 /dev/null**，stdout 必须为空。
#
# 注意：不使用 sh -lc（会加载 /etc/profile.d/gateway.sh 触发语法错误），直接 shebang 执行
cd /root/.openclaw/workspace || exit 1
LOG="memory/$(date +%Y-%m-%d).md"
TS=$(date '+%H:%M')
COUNT=$(openclaw cron list --all 2>/dev/null | grep -cE '^[0-9a-f]{8}-')

{
  echo ""
  echo "## $TS heartbeat（cron:memory_refine 6da766bb · main session 静默模式）"
  echo ""
  echo "- cron 健康度：${COUNT} 个 job"
  echo "- 本节点仅落盘，不推送（爸爸 2026-10-28 / 10-29 连续要求：禁止状态播报）"
} >> "$LOG" 2>/dev/null

# 🔒 关键：stdout/stderr 必须完全为空，否则会被回灌成对话消息推给爸爸
exit 0
