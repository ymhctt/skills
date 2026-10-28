#!/bin/bash
# 每小时 Memory 提炼落盘脚本 —— 纯静默，不产生任何对话消息
# 由 cron 6da766bb (isolated command job) 每小时调用
# 注意：不使用 sh -lc（会加载 /etc/profile.d/gateway.sh 触发语法错误），直接 shebang 执行
cd /root/.openclaw/workspace || exit 1
LOG="memory/$(date +%Y-%m-%d).md"
TS=$(date '+%H:%M')
COUNT=$(openclaw cron list --all 2>/dev/null | grep -cE '^[0-9a-f]{8}-')

{
  echo ""
  echo "## $TS heartbeat（cron:memory_refine 6da766bb · isolated 静默模式）"
  echo ""
  echo "- cron 健康度：${COUNT} 个 job"
  echo "- 本节点仅落盘，不推送（爸爸 2026-10-28 连续要求：禁止状态播报）"
  echo "- 产出：MEMORY.md / daily-learn 提炼在主会话中按需执行"
} >> "$LOG" 2>/dev/null

exit 0
