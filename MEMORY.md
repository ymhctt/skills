# MEMORY.md - 长期记忆

> 这是你的核心记忆库。经过提炼的精华信息，会持续累积在这里。
> 每次会话结束后，把值得记住的内容写进来。

---

## 👤 关于用户

- **称呼**：爸爸
- **时区**：Asia/Shanghai (GMT+8)

---

## 📚 恩墨记录 - 知识库

| 项目 | 内容 |
|------|------|
| **名称** | 恩墨记录 |
| **GitHub仓库** | https://github.com/ymhctt/document.git |
| **本地路径** | /root/.openclaw/workspace/document/ |
| **远程方式** | SSH (git@github.com:ymhctt/document.git) |
| **每日同步** | 每天 7:00 自动 git pull |

### 知识库结构

```
document/  (恩墨记录)
├── 01-MySQL/
├── 02-PG-openGauss-MogDB/
├── 03-MongoDB/
├── 04-Linux-系统/
├── 05-中间件-Redis-ZK-Nginx/
├── 06-分布式数据库-大数据/
├── 07-Oracle-迁移/
├── 98-工具-脚本-杂项/
├── 99-未分类/
└── 小龙虾的文档/      ← 婷婷专属整理目录
    └── (深度整理的技术文档)
```

### 📝 收到链接后的处理流程

1. 收到爸爸发的文档链接
2. 阅读链接内容，提取关键信息
3. 整理成结构化文档
4. 放入对应分类目录（如 `小龙虾的文档/`）
5. **push 前必须先 pull**
6. git add → git commit → git push
7. 更新 `log.md`（记录 ingest 活动）

---

## ⏰ 定时任务

| 任务 | 时间 | 说明 | 通知方式 |
|------|------|------|----------|
| OpenClaw备份 | 每天 00:00 | 备份配置，保留5天 | 静默 |
| 每日Git同步 | 每天 7:00 | git pull 知识库 | 静默 |
| 每日早间简报 | 每天 7:20 | 天气+新闻推送给爸爸 | 正常通知 |
| 每小时Memory提炼 | 每小时 :00 | 提炼内容到 MEMORY.md | 静默 |
| 每周Memory归档 | 每周一 2:00 | 上周日记归档 | 静默 |
| **每日早间汇总** | 每天 8:00 | Git/Memory/备份状态汇总 | 正常通知 |

---

## 💡 重要决策记录

| 日期 | 决策内容 | 背景/原因 |
|------|----------|----------|
| 2026-04-08 | 建立备份任务 | 每天凌晨备份 OpenClaw 配置，清理日志，保留5天 |
| 2026-04-08 | 建立 Memory 提炼归档计划 | 规范长期记忆管理，避免信息流失 |
| 2026-04-09 | 建立知识库Git同步任务 | 每天7点自动同步 |
| 2026-04-10 | Git同步超时调优 | 每日Git同步超时从120s增至300s，避免云端拉取超时 |

---

## 🎯 学习与教训

- **教训**：每次 push 代码前必须先 pull，避免覆盖他人内容！
- **MySQL InnoDB 崩溃恢复 Bug**：已提交事务可能残留在 `active_tw_trxs` 中导致 Undo log 膨胀；官方修复在 MySQL 9.6.0（Bug #38132549）；日常运维禁止使用 `kill -9` 停止 MySQL ✅
- **xtrabackup ftWRL 参数**：
  - `--ftwrl-wait-threshold=300`：有超过300秒的SQL时，ftwrl锁等待1800秒后退出
  - `--kill-long-query-type=all --kill-long-queries-timeout=1800`：等待1800秒后kill阻塞查询
  - `--safe-slave-backup`：备份前停止slave SQL线程，避免临时表问题
- **MySQL 8.0.22 异步复制自动故障转移**：副本可自动重建到备用源的复制连接；需配置 `asynchronous_connection_failover_add_source()` UDF；建议将 `MASTER_RETRY_COUNT` 设为较小值以快速触发故障转移
- **binlog编号上限**：最大值为2147483647，达到后执行 `flush binary logs` 会导致MySQL进程崩溃退出（ERROR 1598）
- **Opening tables 问题**：table_open_cache 应 >= 并发连接数 × 平均每连接查询表数；高并发+多表JOIN易导致table_open_cache不足，大量线程卡在Opening tables
- **系统状态**：所有定时任务已配置完成，系统运行稳定 ✅

## 📋 待完成事项

- [ ] 完善 USER.md（爸爸姓名等个人信息待补充）
- [ ] 完善 IDENTITY.md（婷婷的头像尚未设置）

## 📢 通知规则

- 除 **7:20 天气新闻** 和 **8:00 汇总** 外，其他定时任务均**静默执行**，不主动打扰爸爸

---

## 🛡️ 安全规则（重要！）

| 场景 | 规则 |
|------|------|
| **安装 Skill 前** | 必须进行安全检查（使用 skill-vetter） |
| **发现问题** | 立即通知爸爸，拒绝安装 |
| **适用来源** | ClawdHub、GitHub、第三方链接等 |

---

_Last updated: 2026-04-14 13:03（每小时提炼完成）_
_2026-04-14 08:03 无新增内容；MEMORY.md 已最新 ✅
_Last check: 2026-04-14 06:03 无新增内容；2026-04-13.md 仅含归档记录；daily-learn/2026-04-13.md MySQL知识（binlog编号/半同步备库）均为已知信息；cron无活动；MEMORY.md 已最新 ✅
_2026-04-14 02:03 无新增内容；2026-04-13.md 仅含归档记录；daily-learn/ MySQL内容已收录；MEMORY.md 已最新 ✅
_2026-04-13 20:03 无新增内容；2026-04-13.md 仅含归档记录；daily-learn/ 内容已收录；cron/ stats/runs 无活动；MEMORY.md 已最新 ✅
_2026-04-13 19:03 每小时提炼完成，无新增内容 ✅
_2026-04-13 02:00 完成上周日记归档（04-08~04-12）至 archive/ ✅
