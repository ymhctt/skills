#!/bin/bash
# 每天随机选取几个文档进行学习，生成学习笔记

DOC_DIR="/root/.openclaw/workspace/document"
LEARN_LOG="/root/.openclaw/workspace/memory/daily-learn/$(date +%Y-%m-%d).md"

mkdir -p "$(dirname $LEARN_LOG)"

echo "# 每日学习笔记 - $(date +%Y-%m-%d)" > "$LEARN_LOG"
echo "" >> "$LEARN_LOG"

# 随机选取3个markdown文档学习
find "$DOC_DIR" -type f -name "*.md" 2>/dev/null | shuf -n 3 | while read file; do
  echo "## 📄 $(basename "$file")" >> "$LEARN_LOG"
  echo "" >> "$LEARN_LOG"
  head -50 "$file" 2>/dev/null >> "$LEARN_LOG"
  echo "" >> "$LEARN_LOG"
  echo "---" >> "$LEARN_LOG"
  echo "" >> "$LEARN_LOG"
done

echo "✅ 学习完成！" >> "$LEARN_LOG"
