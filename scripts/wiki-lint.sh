#!/bin/bash
# Wiki Lint 脚本 - 检查知识库健康状态
# 每周运行一次

DOC_DIR="/root/.openclaw/workspace/document/小龙虾的文档"
INDEX_FILE="/root/.openclaw/workspace/document/index.md"
LOG_FILE="/root/.openclaw/workspace/document/log.md"
REPORT_FILE="/tmp/wiki-lint-report-$(date +%Y%m%d).txt"

echo "=== Wiki Lint Report - $(date +%Y-%m-%d) ===" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 1. 统计文档数量
DOC_COUNT=$(find "$DOC_DIR" -name "*.md" | wc -l)
echo "[1] 文档统计" >> "$REPORT_FILE"
echo "    当前文档数量: $DOC_COUNT" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 2. 检查 index.md 是否过时（对比实际文档）
echo "[2] index.md 同步检查" >> "$REPORT_FILE"
for doc in "$DOC_DIR"/*.md; do
    if [ -f "$doc" ]; then
        filename=$(basename "$doc" .md)
        if ! grep -q "$filename" "$INDEX_FILE" 2>/dev/null; then
            echo "    ⚠️  缺少索引: $filename" >> "$REPORT_FILE"
        fi
    fi
done
echo "    index.md 同步检查完成" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 3. 检查孤立文件（很久没更新的文档）
echo "[3] 文档时效检查" >> "$REPORT_FILE"
find "$DOC_DIR" -name "*.md" -mtime +30 -exec basename {} \; 2>/dev/null | while read f; do
    echo "    ⚠️  30天未更新: $f" >> "$REPORT_FILE"
done
echo "" >> "$REPORT_FILE"

# 4. 检查 log.md 最后更新时间
echo "[4] log.md 更新检查" >> "$REPORT_FILE"
if [ -f "$LOG_FILE" ]; then
    LAST_LOG=$(tail -20 "$LOG_FILE" | grep -E "^## \[" | head -1)
    echo "    最后记录: $LAST_LOG" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 5. 待办建议
echo "[5] 建议" >> "$REPORT_FILE"
echo "    - 检查是否有重复内容可以合并" >> "$REPORT_FILE"
echo "    - 考虑添加更多概念页连接相关文档" >> "$REPORT_FILE"
echo "    - 检查代码示例是否需要更新" >> "$REPORT_FILE"

cat "$REPORT_FILE"
rm -f "$REPORT_FILE"
