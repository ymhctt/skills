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
| 每日早间简报 | 每天 7:20 | 天气+新闻 → announce微信推送 | 正常通知 |
| 每小时Memory提炼 | 每小时 :00 | 提炼内容到 MEMORY.md | 静默 |
| 每周Memory归档 | 每周一 2:00 | 上周日记归档 → announce微信推送 | 静默 |
| 每日早间汇总 | 每天 8:00 | Git/Memory/备份状态汇总 → announce微信 | 正常通知 |
| **东西大区4部报工统计（新skill）** | **每天 9:00** | **MES查询→HTML+摘要推送微信** | **正常通知** |
| 每日MES自动更新 | 每天 3:00 | mes update + skill git pull | 静默 |
| **inbound媒体清理** | 每天 2:00 | 清理1天前临时文件 | 静默 |

---

## 💡 重要决策记录

| 日期 | 决策内容 | 背景/原因 |
|------|----------|----------|
| 2026-04-08 | 建立备份任务 | 每天凌晨备份 OpenClaw 配置，清理日志，保留5天 |
| 2026-04-08 | 建立 Memory 提炼归档计划 | 规范长期记忆管理，避免信息流失 |
| 2026-04-09 | 建立知识库Git同步任务 | 每天7点自动同步 |
| 2026-04-10 | Git同步超时调优 | 每日Git同步超时从120s增至300s，避免云端拉取超时 |
| 2026-04-17 | Cron任务light-context优化 | 周报工/早间汇总/Git同步/MES更新四个任务启用 light-context（跳过workspace文件加载，加速冷启动）；早间汇总120s/周报工500s/Git同步180s/MES更新180s |
| 2026-04-21 | Cron任务isolated+announce模式确认 | **纠正**：60秒冷启动限制只影响 `--session main + --system-event` 路线；`--announce --session isolated` 配合可正常工作，因为不需要等 session 响应，直接投递；早间简报34秒内在60秒内完成，isolated 模式可以工作 |
| 2026-04-23 | 安装爸爸提供的mes-work-report skill | skill路径 ~/.openclaw/workspace/skills/mes-work-report/；含fetch_data.py(数据层)+generate_report.py(HTML生成)；cron改用新skill，ID 57c86329；新接口total 476.5h（旧script 412.5h，口径不同） |
| 2026-04-21 | 早间任务时间调整 | 7:20=早间汇总（详细），8:00=早间简报（天气新闻）；两个任务调整了 cron 时间并统一用 `--announce --session isolated` 模式 |
| 2026-04-21 | 修复早间简报 timeout | 早间简报原跑 isolated session，因冷启动+执行超过60秒导致 timeout；改为 `--announce --session isolated` 后任务轻量（34秒）可在60秒内完成 |
| 2026-04-19 | 周报工统计脚本化 | 创建 `scripts/weekly_report.py`，MES查询+数据整理一体化，2.3秒出完整结构化数据（652h/110条记录），绕过LLM冷启动问题 |

---

## 🎯 学习与教训

- **教训**：每次 push 代码前必须先 pull，避免覆盖他人内容！
- **2026-04-21 cron任务模式总结**（纠正2026-04-19的说法）：
  - `--session main + --system-event`：在主会话中处理，可并发但可能在聊天时被延迟
  - `--announce --session isolated`：**推荐**，isolated session 执行完直接推送微信，不依赖主会话，60秒冷启动对轻量任务（34秒）不构成问题
  - **推荐做法**：需要微信推送且任务轻量（&lt;60秒）→ `--announce --session isolated`；任务重或需要主会话处理 → `--session main + --system-event`
- **MES 周报工统计正确方法**（2026-04-17 修正）：
  - ✅ 正确：`mes -o json statistics list --from --to --team-id 23 --page-size 200`，按 `executorId` 分组汇总 `taskTime`
  - ❌ 错误：用 `statistics summary --group-type 0`（team-id 过滤有 Bug，返回数据不对）
  - ❌ 错误：按 `start` 日期分组（`start` 填错或留空会导致数据丢失）
  - ❌ 错误：用 `statistics list` 但默认 pageSize=50 不翻页（83条记录会截断）
  - 2026-04-17 第一次跑出 472h，第二次错误地修正为 319h，正确值是 472h（18人/83条记录）
  - teamId=23 是「东西大区4部」，共20人
- **MySQL InnoDB 崩溃恢复 Bug**：已提交事务可能残留在 `active_tw_trxs` 中导致 Undo log 膨胀；官方修复在 MySQL 9.6.0（Bug #38132549）；日常运维禁止使用 `kill -9` 停止 MySQL ✅
- **xtrabackup ftWRL 参数**：
  - `--ftwrl-wait-threshold=300`：有超过300秒的SQL时，ftwrl锁等待1800秒后退出
  - `--kill-long-query-type=all --kill-long-queries-timeout=1800`：等待1800秒后kill阻塞查询
  - `--safe-slave-backup`：备份前停止slave SQL线程，避免临时表问题
- **MySQL 8.0.22 异步复制自动故障转移**：副本可自动重建到备用源的复制连接；需配置 `asynchronous_connection_failover_add_source()` UDF；建议将 `MASTER_RETRY_COUNT` 设为较小值以快速触发故障转移
- **binlog编号上限**：最大值为2147483647，达到后执行 `flush binary logs` 会导致MySQL进程崩溃退出（ERROR 1598）
- **Opening tables 问题**：table_open_cache 应 >= 并发连接数 × 平均每连接查询表数；高并发+多表JOIN易导致table_open_cache不足，大量线程卡在Opening tables
- **MySQL binlog ROW 格式事务隔离级判断陷阱**（2026-04-19）：binlog 中出现 `/*!50718 SET TRANSACTION ISOLATION LEVEL READ COMMITTED*/` 并**不代表**实际隔离级是 RC；当 binlog 格式为 ROW 且源库隔离级为 RR 时，MySQL 会在 binlog 中插入此语句作为**优化手段**，让回放时使用 RC 隔离级来提高速度、降低锁开销、减少死锁；真正判断隔离级的方式是 `SELECT @@global.transaction_isolation;`，不能通过 binlog 解析来断定
- **MySQL 9.6 外键管理变革**：MySQL 9.6 起，外键约束和级联操作改由 SQL 引擎处理（原由 InnoDB 内部执行）；此举解决了级联操作对 SQL 层不可见、二进制日志缺失子表更改、CDC 复制不一致等问题；性能与原 InnoDB 方式几乎相同，完全向后兼容
- **MogDB 3.0.3→5.0.6 升级 whale 插件问题**：升级过程中若无法自动下载插件包，ptk 升级命令会失败；需预先下载对应版本的 whale 安装包，指定 `plugin_dir` 再升级；升级插件列表含 dblink/orafce/pg_bulkload/pg_prewarm/pg_repack/pg_trgm/postgis/wal2json/whale；选不同意则升级立即终止
- **MogHA 高可用软件**（云和恩墨自研，适用于 MogDB/openGauss）：lite 模式（轻量，2节点，需配置 ping_list 防脑裂，不修改复制关系）vs full 模式（最多1主8备，所有节点运行，修改 replconninfo）；故障切换秒级完成，支持 VIP 漂移；Python≥3.6，依赖 gsql/gs_ctl 免密（pg_hba.conf trust）
- **yum 基础命令**：`yum clean all` + `yum makecache` 清理缓存重建元数据；`yum search`、`yum list`、`yum list installed`、`yum list updates` 查询软件包
- **MySQL timeout 五种参数**：
  - `connect_timeout`（默认5s）：连接握手阶段超时，6次握手任意一次失败即断开
  - `wait_timeout`（默认28800s）：sleep线程存活超时，session级别；实际交互模式下也是它生效（非 interactive_timeout）
  - `interactive_timeout`：仅在连接初期将值赋给 wait_timeout，自己不起实际控制作用
  - `net_read_timeout`（默认30s）/ `net_write_timeout`（默认60s）：网络读写超时
- **MySQL 条件优化 `optimize_cond` 四步**：提取公共子条件(extract_common_cond) → 等值传播(build_equal_items) → 常数传播(propagate_cond_constants) → 零散条件去除(remove_eq_conds)；前提：where条件为析取式、存在公共子条件、完全一致形式、具幂等性
- **InnoDB 读写锁三种模式**：S（Shared）、SX（Shared-Exclusive）、X（Excluded）；SX锁优化场景：在 dict_index_t.lock 上加SX锁可避免阻塞 B+Tree 搜索操作（传统X锁会阻塞所有搜索）；基于原子操作+自旋锁实现，减少内核态同步开销
- **MySQL 8 窗口函数**：MySQL 8 支持窗口函数（RANK()、LAG()、NTILE() 等，以及 SUM()/AVG() 等聚合函数的窗口用法）；核心语法 `OVER([window_name] [partition_clause] [order_clause] [frame_clause])`；frame_clause 用于滑动窗口计算；可在 FROM 子句后用 `WINDOW` 子句定义命名窗口；注意：窗口函数不能用于 UPDATE/DELETE 中更新行，只能用于 SELECT/子查询选行
- **MySQL 8 自定义表空间路径**：`CREATE TABLESPACE ts_name ADD DATAFILE '/path/to/ts_name.ibd' ENGINE=INNODB`；`CREATE TABLE t (...) TABLESPACE=ts_name` 指定表所属表空间；`ALTER TABLE t TABLESPACE=ts_name` 迁移已有表；`AUTOEXTEND_SIZE` 控制表空间满时的自动扩容大小（8.0.13+）；`FILE_BLOCK_SIZE` 定义表空间数据文件块大小，存储压缩表时需与表的 `KEY_BLOCK_SIZE` 匹配；`ENCRYPTION` 控制静态加密；用于解决磁盘 IO 压力或容量瓶颈时将库表分散到不同磁盘
- **PostgreSQL 子事务（SAVEPOINT）**：子事务允许回滚事务中的部分工作；`SAVEPOINT name`（无需引号）创建命名保存点；`ROLLBACK TO SAVEPOINT name` 回滚到指定保存点，保留保存点之前的工作；子事务在主事务提交时自动提交；需注意子事务性能问题（Subtransaction overhead）
- **MySQL 8.0 SET PERSIST**：可将全局变量修改持久化到 `mysqld-auto.cnf`，重启后仍生效；`SET PERSIST max_connections=1000`（内存+文件），`SET PERSIST_ONLY`（仅文件）；启动时最后读取此文件；可通过 `performance_schema.persisted_variables` 查看
- **InnoDB Mutex 六种类型**（2026-04-21）：OSBasicMutex（OS事件，单次加锁尝试）| OSTrackMutex（继承自OSBasicMutex，支持max_spins次数重试）| TTASFutexMutex（Linux futex，CAS原子指令+TAS解锁）| TTASMutex（TAS原子指令，忙等待）| TTASEventMutex（TAS+ut_delay()睡眠延迟+最终等待）| PolicyMutex（携带持有者信息，用于Performance schema监控）；SX锁可避免阻塞B+Tree搜索，减少内核态同步开销
- **MySQL 单主MGR集群间异步复制 failover**（2026-04-21）：MySQL 8.0.22+ 支持异步连接故障转移；8.0.27起单主模式MGR作为备库时可自动维护备选主库列表；要求开启GTID+master_auto_position；复制用户需授权performance_schema.*权限；备库所有成员都需执行CHANGE MASTER；故障转移粒度为节点级，而非集群级
- **pt-archiver 数据归档工具要点**（2026-04-18）：源表必须有主键；默认迁移完会删源数据；未加 `--no-safe-auto-increment` 会漏最大ID记录（8.0前重启按最大值重置auto-increment）；归档中源数据变更可能导致不一致；可用 `--for-update/--share-lock` 锁定但影响业务；归档完不会自动 ANALYZE/OPTIMIZE
- **MySQL binlog 文件补充**（2026-04-18）：`crash_safe_index_file` 是 binlog 索引文件操作的崩溃恢复机制，先写临时文件再原子替换正式 index；`purge_index_file` 是 PURGE 日志时临时记录待删文件名，保证删除和索引更新原子性；binlog 编号上限 2147483647，超限 flush 会导致 MySQL 崩溃（ERROR 1598）
- **MySQL 通信包错误 `Aborted_clients`/`Aborted_connects`**（2026-04-22）：
  - `Aborted_connects`：登录失败（密码错误、权限不足、connect_timeout 超限）
  - `Aborted_clients`：连接成功但异常断开（未调用 `mysql_close()`、sleep 超 `wait_timeout`、程序中途终止）
  - 共同原因：max_allowed_packet 过小、Linux 以太网驱动 bug、线程库中断、TCP/IP 配置错误、硬件故障
  - 排查：`show status like 'Aborted%'` + `show variables like '%timeout'`
- **InnoDB redo log 机制**（2026-04-22）：
  - WAL 原则：数据页刷盘前，redo log 必须先落盘
  - LSN（Log Sequence Number）：unsigned long long，不断递增，标识 redo 中的位置
  - flush list：Buffer Pool 各 instance 维护，按 page 的 LSN 排序；做 checkpoint 时选最老（最小 LSN）page
  - ib_logfile[N]：循环顺序写，覆盖前需保证对应脏页已刷盘
  - innodb_log_files_in_group × innodb_log_file_size = 总 redo 大小
  - 危险线：未 checkpoint 日志超过文件总大小 76% 时，InnoDB 强制 preflush 脏页，导致大量线程 stall
  - log_sys：日志系统核心对象，控制日志拷贝、写入、checkpoint
- **系统状态**：所有定时任务已配置完成，系统运行稳定 ✅

## 🛠️ 周报工统计脚本

| 项目 | 内容 |
|------|------|
| **路径** | `~/.openclaw/workspace/scripts/weekly_report.py` |
| **功能** | MES查询 + 按人员/日期分组 + 少于10字条目 + 未报工人员 |
| **性能** | 2.3秒完成，110条记录，652总工时 |
| **使用方法** | `python3 /root/.openclaw/workspace/scripts/weekly_report.py` |
| **输出** | JSON格式，含 week/total_hours/members/short_items/not_reported |

---

## 📋 待完成事项

- [ ] 完善 USER.md（爸爸姓名等个人信息待补充）
| **贵阳出差** | 2026-04-22 爸爸在贵阳出差，预计返回后通知我 |
- [ ] 完善 IDENTITY.md（婷婷的头像尚未设置）

---

## 🛠️ MES CLI 与 Skill

| 项目 | 内容 |
|------|------|
| **CLI 下载** | https://oss-emcsprod-public.oss-cn-beijing.aliyuncs.com/tools/mes/ |
| **Skill 仓库** | https://github.com/enmotech/mes-cli-skills.git |
| **Skill 安装路径** | ~/.openclaw/workspace/skills/mes-cli-terminal/ |
| **当前版本** | 0.4.8 |
| **升级方式** | CLI：`mes update`；Skill：git pull 最新版仓库覆盖安装 |
| **自动更新** | 每天凌晨 3:00 自动执行更新任务（cron ID: ad3dc4bb-b1aa-43aa-9a77-eb2b94839b7a） |
| **每日周报工统计** | 每天早上 9:00 统计东西大区4部本周报工并推送（cron ID: f9ca9e48，main+system-event） |
| **inbound媒体清理** | 每天凌晨 2:00 清理临时文件（cron ID: ce65d49c-6f01-40b5-b33e-3b1153f4f706） |

---

## 🧹 inbound 媒体文件清理规则

| 项目 | 说明 |
|------|------|
| **规则** | 每天凌晨 2:00 自动清理 inbound 目录超过 1 天的临时文件 |
| **路径** | /root/.openclaw/media/inbound/ |
| **保留** | 1 天内的新文件 |
| **日志** | 清理结果写入 cleanup.log |
| **cron ID** | ce65d49c-6f01-40b5-b33e-3b1153f4f706 |
| **创建日期** | 2026-04-16 |

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

_Last updated: 2026-04-21 23:03 每小时提炼完成：新增 InnoDB Mutex 六种类型 + MGR集群间异步复制 failover 知识点 ✅

_Last updated: 2026-04-23 12:03 每小时提炼 ✅ 无新增内容；爸爸贵阳出差中_

_Last updated: 2026-04-23 21:15 爸爸强调：所有报工统计必须用 mes-work-report skill 生成！cron也用的是这个skill的generate_report.py_
