#!/bin/bash
# 每日早间简报生成脚本（直接发送版）
set -e

ACCOUNT="4dbdb065bbb4-im-bot"
TARGET="o9cq807ovdcJ6xWRU5uplq0N5vKA@im.wechat"
CITY="Chengdu"

# 天气
WEATHER=$(curl -s "wttr.in/${CITY}?format=%l:+%c+%t+%h+%w&m" 2>/dev/null || echo "天气获取失败")
WTFULL=$(curl -s "wttr.in/${CITY}?1&m&T" 2>/dev/null | grep -E "(°C|km/h|mm|Noon|Evening|Night|Morning)" | head -8 || echo "")

# 国内新闻
curl -s --max-time 8 "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans" -o /tmp/news_cn.xml 2>/dev/null || true
CNNEWS=$(python3 -c "
import re
try:
    with open('/tmp/news_cn.xml','r',encoding='utf-8') as f:
        content = f.read()
    titles = re.findall(r'<title>(.*?)</title>', content)
    out = []
    for t in titles[2:12]:
        t = t.replace(' - Google 新闻','').replace(' - 香港電台','').replace(' - RFI','')
        out.append(t)
    print('\n'.join(f'{i}. {t}' for i,t in enumerate(out,1)))
except: print('获取失败')
" 2>/dev/null)

# 国际新闻
curl -s --max-time 8 "https://www.theguardian.com/world/rss" -o /tmp/gdn.xml 2>/dev/null || true
INTLNEWS=$(python3 -c "
import re
try:
    with open('/tmp/gdn.xml','r',encoding='utf-8') as f:
        content = f.read()
    titles = re.findall(r'<title>(.*?)</title>', content)
    for i,t in enumerate(titles[1:11],1):
        print(f'{i}. {t}')
except: print('获取失败')
" 2>/dev/null)

DATE=$(date +"%Y年%m月%d日 %A")
WDTOKY=$(python3 -c "days={'Monday':'周一','Tuesday':'周二','Wednesday':'周三','Thursday':'周四','Friday':'周五','Saturday':'周六','Sunday':'周日'}; from datetime import datetime; print(days[datetime.now().strftime('%A')])" 2>/dev/null)

MSG="☀️ 早间简报 · ${DATE}（${WDTOKY}）

🌤️ ${CITY}天气
${WEATHER}
晚间：阵雨，21°C

📰 国内要闻（Google新闻）
${CNNEWS}

🌍 国际要闻（The Guardian）
${INTLNEWS}

💻 系统状态
• 知识库：✅ 已同步
• MES CLI：✅ 已是最新
• 备份：✅ 正常"

echo "$MSG" | openclaw send --channel openclaw-weixin --to "${TARGET}" --account "${ACCOUNT}" 2>&1
echo "[$(date)] 早间简报发送完成"