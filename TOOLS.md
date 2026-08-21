# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## ⏰ 定时任务（微信推送）

| 任务 | 时间 | cron ID | 模式 |
|------|------|---------|------|
| 每日早间汇总(新) | 7:20 | 9fc7ca81-320b-4be7-ae2c-72631aab1629 | isolated+announce→**openclaw-weixin** |
| 每日早间简报(新) | 8:00 | f730b7b4-9439-46f0-8243-b17bbb7d3070 | isolated+announce→**openclaw-weixin** |
| 东西大区4部报工统计（11章节完整版） | 9:00 | a32216f6-35cb-4d15-81f3-cd93f4a7e197 | isolated+announce→**openclaw-weixin** |

## ⏰ 定时任务（静默）

| 任务 | 时间 | cron ID | 说明 |
|------|------|---------|------|
| 每小时Memory提炼 | 每小时 :00 | ea9ca7d6-fe43-407d-a5f3-68fa92600380 | isolated (静默) |

## ⏰ 定时任务（静默）

| 任务 | 时间 | cron ID | 说明 |
|------|------|---------|------|
| inbound媒体清理 | 每天 2:00 | ce65d49c-6f01-40b5-b33e-3b1153f4f706 | main session |
| MES CLI 自动更新 | 每天 3:00 | ad3dc4bb-b1aa-43aa-9a77-eb2b94839b7a | main session |
| Git 知识库同步 | 每天 7:00 | f193150b-c2c8-47b7-85e6-59ce1b57ed95 | main session |
| 每小时Memory提炼 | 每小时 :00 | 6da766bb-d17e-4f9c-9ce3-fc0ad8649e12 | main+system-event |
| 每周 Memory 归档 | 周一 2:00 | 2a2a6489-b7ec-42cd-a129-6e5635a2cdb9 | main session |

## 📝 Cron 模式说明

- **announce+isolated**：isolated session 执行完直接推送微信，不依赖主会话
  - 适用：需要推送微信、轻量任务（&lt;60秒）
  - 注意：isolated 有冷启动约60秒，轻量任务可忽略
- **main session**：在主会话中处理，可能被聊天延迟
  - 适用：后台静默任务

---

## 📝 memory 文件写入规范（2026-07-07 22:00 事故后固化）

⚠️ **关键提醒**：OpenClaw 的 `write` 工具**默认会覆盖整个文件**，不是 append 行为。

- ❌ **错误用法**：在 cron heartbeat 想追加一条 daily 记录，但用 `write` + 新内容 → 把整个 daily file 清空
- ✅ **正确做法**：
  1. **首选 `edit`**：定位最后一条 `## HH:MM heartbeat` 段落，在其后插入新段
  2. **必须 `write` 时**（比如整文件重建）：
     - 先 `read path=memory/YYYY-MM-DD.md` 拿到**完整当前内容**
     - 手动把新 heartbeat 拼接到末尾
     - 再 `write` 完整字符串
- shell 追加：`cat >> file << 'EOF' ... EOF` 安全（系统级 append）
- 事故案例：7/7 22:00 heartbeat 想追加 22:00 条目，用 `write` 写入只有 22:00+21:00 的内容，整个文件被覆盖，丢失 16:00 之前的 11 条 heartbeat；最终从 session context 重建

## 📊 报工统计报告标准（2026-04-24 确认）

每次生成报工统计报告（手动或 9:00 定时任务）都必须按此标准执行：

### 报告结构（12章节，全部必须有）
1. 📊 一、团队核心指标概览（人数/总工时/满勤率/加班/评分/文档/服务请求/待处理工单 8卡片）
2. 📋 二、成员工时明细（排名表格：# / 姓名 / 城市 / 总工时 / 售后 / 内部 / 加班 / 报工条数 / 评分 / 不足 / 状态）
3. 🗓️ 每日工时热力图（行=成员，列=工作日，色块：0h灰/1-4h浅绿/5-7h中绿/8h深绿/>8h红）
4. ⚠️ 三、报工不足人员分析（含"城市"列 + 🔴严重/🟠偏少 badge）
5. 📄 四、文档编写统计（标题/作者/团队/创建时间）
6. 📊 五、工时类型分布（售前/售后/内部占比条形图 + 卡片）
7. 🎯 六、报工质量分析（4档 badge + 明细表）
8. 🏅 七、工时排名 TOP 10（含趋势：⬆超额/➡达标/⬇不足）
9. 🛠️ 八、服务请求列表（含状态标签）
10. 👥 九、团队人员分布（总人数/满勤/不足/满勤率卡片）
11. 🔍 十、综合评价（总体评价 + 亮点 + 待改进）
12. ✅ 十一、未报工分析

### 执行流程
```bash
# Step 1: 拉取数据（含 extra）
cd /root/.openclaw/workspace/skills/mes-work-report/scripts
python3 fetch_data.py --team-id 23 --from $(date -d "-4 days" +%Y-%m-%d) --to $(date -d "-1 day" +%Y-%m-%d) --output /tmp/full_report.json --fetch-extra

# Step 2: 生成 11 章节 HTML
python3 /tmp/gen11.py

# Step 3: 发送微信
openclaw send --channel openclaw-weixin --to "o9cq807ovdcJ6xWRU5uplq0N5vKA@im.wechat" --file /tmp/dongxi_11chapters.html --caption "东西大区4部报工看板 MM/DD~MM/DD"
```

### 关键字段（full_report.json 对齐）
- 评分字段：`score`（不是 `operationStandardScore`）
- 人员姓名字段：`executorName`
- 城市字段：`city`
- 严重程度 badge：不足≥10h→🔴严重，0<不足<10h→🟠偏少

### 样式
- 暗色主题：`--bg:#0f0f23` / `--card:#16213e` / `--blue:#00d4ff` / `--green:#2ecc71`
- 热力图：h=0→#2d2d2d / h<4→#3d5a3d / h<8→#4a7a4a / h=8→#2ecc71 / h>8→#e94560

### ⚠️ 禁止简化
- 不能只输出 3 章，必须 11/12 章全部生成
- 不能跳过质量分析、服务请求、综合评价等章节
- 数据不完整时先补全数据，不接受缺章节的报告

---

## 🧹 inbound 媒体文件清理
