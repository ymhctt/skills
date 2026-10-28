# HEARTBEAT.md

## 🚫 最高优先级规则（2026-10-28 爸爸明确要求）

**默认不发送任何内容。** heartbeat / cron systemEvent 触发时，回复 `NO_REPLY`，不要发状态播报。

### ❌ 绝对不要发这些
- "17:30 状态无变化：memory_refine ✅、cron 仍 7 个、MES 未登录"
- "静默处理。"
- "静默。"
- 任何形式的 cron 状态快照 / 故障计数 / day-N 里程碑播报
- "无变化" / "状态一致" / "已静默处理" 之类的话

### ✅ 只在以下情况才发消息
1. **需要爸爸动手做事**（如 `mes auth login`）
2. **出现新问题**（不是已有故障的重复播报）
3. **爸爸主动问**

### 🔑 判定口诀
> 状态没变 → `NO_REPLY`
> 老故障重复 → `NO_REPLY`
> 只有「需要你做事」或「新问题」才开口

---

## 背景说明（为什么会有这些规则）

2026-10-28 爸爸两次明确要求：
1. 「不用再发这种消息了」（指 cron 状态播报）
2. 「你又发了？？？」（指我口头答应但没改机制）

**根因**：`cron:memory_refine` 用 `--system-event` 触发，每小时往当前对话注入 systemEvent。
我误把「收到 event」当成「该输出内容」，于是照着旧 HEARTBEAT.md 的格式每次都生成状态报告。
旧 HEARTBEAT.md 堆了 273KB 的历史"静默处理"记录，本身就在示范错误输出格式。

**教训**：口头承诺不够，**必须改机制**：
- 本文件重写为规则式（而不是历史记录堆）
- 历史全文已备份到 `/tmp/HEARTBEAT.md.bak.20261028`
- 记忆/日志类工作照常写文件（daily / MEMORY.md / heartbeat-state.json），**只是不推送给爸爸**

---

## 静默任务的执行要求

收到下列 systemEvent 时：
- `cron:memory_refine`（每小时 :00）
- `cron:git_sync`（7:00）
- `cron:mes_update`（3:00）
- `cron:media_cleanup`（2:00）
- `cron:memory_archive`（周一 2:00）

**照常执行工作**（更新文件、跑脚本、记日志），然后回复 `NO_REPLY`。

**注意**：`cron:memory_archive` 历史上会 announce 推送归档摘要 —— 那是它的 announce 配置，保留；但 memory_refine / git_sync / mes_update / media_cleanup 是纯静默，不推送。

---

## ⚠️ 硬规则：`NO_REPLY` 必须是整条回复的唯一内容

**踩坑记录（2026-10-28 19:37 爸爸第三次投诉）**：

19:00 那次 memory_refine 的响应，我写成了：
```
NO_REPLY

**19:00 静默自检完成**（只读命令，未使用任何 push 通道）：
| 项目 | 状态 |
|---|---|
| 7 个 cron 任务 | 全部 enabled ✅ |
...
```
→ **`NO_REPLY` 指令失效，整条被当普通消息推送了** ❌

### 正确写法（只能二选一）
```bash
# 方式 A：完全静默 —— 整条回复就只有这四个字符，什么都别加
NO_REPLY
```

```bash
# 方式 B：需要说话时 —— 不要写 NO_REPLY，直接正常回复内容
（正常内容，不含 NO_REPLY）
```

### ❌ 绝对禁止
- `NO_REPLY` 后面跟任何解释、表格、说明
- 「先 NO_REPLY 然后补充说明」这种自我矛盾
- 觉得「NO_REPLY 后面再写点更保险」

### 🔑 判定流程（每次 systemEvent 触发时）
1. 判断是否需要开口（见顶部「只在以下情况才发消息」）
2. **需要开口** → 直接写正常内容，**不要出现 NO_REPLY**
3. **不需要开口** → 整条回复**只有** `NO_REPLY` 四个字符，**没有任何其他内容**
4. 想写文件/跑脚本 → 先做（用 exec/read/write 工具），最后才输出回复，且回复只有 `NO_REPLY`

⚠️ 工具调用和最终回复是两回事：可以先 exec 写日志，然后最终只回 `NO_REPLY`。
