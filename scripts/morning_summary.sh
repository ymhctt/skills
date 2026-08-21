#!/bin/bash
# 每日早间汇总脚本（7:20执行）
# 系统状态汇总推送
set -e

ACCOUNT="4dbdb065bbb4-im-bot"
TARGET="o9cq807ovdcJ6xWRU5uplq0N5vKA@im.wechat"
DATE=$(date +"%Y年%m月%d日 %A")
WDTOKY=$(python3 -c "
days={'Monday':'周一','Tuesday':'周二','Wednesday':'周三','Thursday':'周四','Friday':'周五','Saturday':'周六','Sunday':'周日'}
from datetime import datetime
print(days[datetime.now().strftime('%A')])
" 2>/dev/null)

# 1. 知识库Git同步状态
cd /root/.openclaw/workspace/document
GIT_PULL=$(git pull --ff-only 2>&1 || echo "failed")
if echo "$GIT_PULL" | grep -q "Already up to date"; then
    GIT_STATUS="✅ 已同步"
elif echo "$GIT_PULL" | grep -q "failed"; then
    GIT_STATUS="⚠️ 同步失败"
else
    GIT_STATUS="📥 已拉取更新"
fi

# 2. MES CLI版本
MES_VERSION=$(mes --version 2>/dev/null | head -1 || echo "未知")
MES_STATUS="✅ ${MES_VERSION}"

# 3. 磁盘空间
DISK=$(df -h / | tail -1 | awk '{print $5 "已用 / " $2 "总空间"}')
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    DISK_STATUS="⚠️ ${DISK}"
else
    DISK_STATUS="✅ ${DISK}"
fi

# 4. 内存使用
MEM_TOTAL=$(free -m | grep Mem | awk '{print $2}')
MEM_USED=$(free -m | grep Mem | awk '{print $3}')
MEM_PCT=$((MEM_USED * 100 / MEM_TOTAL))
if [ "$MEM_PCT" -gt 85 ]; then
    MEM_STATUS="⚠️ ${MEM_USED}MB / ${MEM_TOTAL}MB (${MEM_PCT}%)"
else
    MEM_STATUS="✅ ${MEM_USED}MB / ${MEM_TOTAL}MB (${MEM_PCT}%)"
fi

# 5. 最近一次cron运行状态
CRON_LOG="/root/.openclaw/workspace/memory/cron/runs.json"
if [ -f "$CRON_LOG" ]; then
    LAST_CRON=$(python3 -c "
import json, datetime
try:
    with open('${CRON_LOG}') as f:
        data = json.load(f)
    runs = data.get('runs', [])
    if runs:
        last = runs[-1]
        ts = last.get('start', '')
        job = last.get('job_id', 'unknown')[:8]
        status = last.get('status', '')
        emoji = '✅' if status == 'success' else '⚠️'
        print(f'{emoji} {job}... {status}')
except: print('无记录')
" 2>/dev/null || echo "无记录")
else
    LAST_CRON="无记录"
fi

# 6. inbound媒体清理状态
INBOUND_CLEAN=$(cat /root/.openclaw/workspace/memory/cron/jobs.json 2>/dev/null | python3 -c "
import json,sys
try:
    jobs = json.load(sys.stdin).get('jobs',[])
    for j in jobs:
        if 'media' in j.get('name','').lower() or 'clean' in j.get('name','').lower():
            print(j.get('last_run','从未'), j.get('status','unknown'))
            break
    else: print('未配置')
except: print('未配置')
" 2>/dev/null || echo "未配置")

# 7. uptime
UPTIME=$(uptime -p 2>/dev/null | sed 's/up /已运行 /' || echo "未知")

MSG="🌅 早间汇总 · ${DATE}（${WDTOKY}）

💻 系统状态
• 知识库：${GIT_STATUS}
• MES CLI：${MES_STATUS}
• 磁盘：${DISK_STATUS}
• 内存：${MEM_STATUS}
• 运行时间：${UPTIME}

📊 定时任务
• 最近运行：${LAST_CRON}
• 媒体清理：${INBOUND_CLEAN}

⏰ ${WDTOKY}愉快！"

echo "$MSG" | openclaw message send --channel openclaw-weixin --account "${ACCOUNT}" --target "${TARGET}" --message "$MSG" 2>&1
echo "[$(date)] 早间汇总发送完成"