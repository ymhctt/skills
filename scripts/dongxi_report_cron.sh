#!/bin/bash
# 东西大区4部报工统计 - Cron 专用脚本（完整11章节版）
# 流程：fetch_data.py → JSON → Agent生成HTML
set -e

SKILL_DIR="/root/.openclaw/workspace/skills/mes-work-report/scripts"
OUTPUT_HTML="/tmp/dongxi_11chapters.html"
JSON_FILE="/tmp/full_report.json"

# 往前推6天确保覆盖完整工作周（周一到昨天）
# 周一往前推6天一定是周一，周日往前推6天是周二，所以一定能包含完整工作日
FROM_DATE=$(date -d "-6 days" +%Y-%m-%d)
TO_DATE=$(date -d "-1 day" +%Y-%m-%d)

echo "[Cron] 东西大区4部报工统计 $(date)"
echo "[Cron] 周期: $FROM_DATE ~ $TO_DATE"

# Step 1: 拉取数据到 JSON
cd "$SKILL_DIR"
python3 fetch_data.py \
    --team-id 23 \
    --from "$FROM_DATE" \
    --to "$TO_DATE" \
    --output "$JSON_FILE" \
    --fetch-extra

if [ ! -f "$JSON_FILE" ]; then
    echo "[ERROR] JSON 数据拉取失败"
    exit 1
fi
echo "[OK] JSON: $(wc -c < $JSON_FILE) bytes"

# Step 2: 生成完整11章节HTML
# 注意：此脚本输出 /tmp/dongxi_11chapters.html（路径写死在 gen_full_report.py 中）
python3 /tmp/gen_full_report.py

if [ -f "$OUTPUT_HTML" ]; then
    echo "[OK] HTML: $(wc -c < $OUTPUT_HTML) bytes"
else
    echo "[ERROR] HTML 生成失败"
    exit 1
fi
