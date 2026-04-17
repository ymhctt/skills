---
name: mysql-inspection-report
description: Generate structured MySQL inspection reports from one or more mysql_check markdown data files. Use this whenever the user wants to turn raw MySQL巡检采集 .md files into a formal report, including single-instance reports, primary-replica comparisons, MGR summaries, or Galera/PXC cluster inspection summaries, even if they only say '整理巡检报告', '分析采集结果', or '输出汇报版 markdown'.
---

# MySQL Inspection Report

将 `mysql_check202604.sh`生成的原始巡检 `.md` 数据文件，整理为适合汇报、评审和跟踪整改的 Markdown 巡检报告。

## Inputs this skill expects
-1 个或多个原始巡检 Markdown 文件。
- 文件通常命名为 `mysql_check202604_<host>_<port>_<timestamp>.md`，但不要依赖文件名；始终以文件内容为准。
- 如果用户同时提供多个文件，先判断它们是：
 - 单节点独立巡检
 - 主备 / 异步复制
 - MGR
 - Galera / PXC
 - 无法确定拓扑的多节点集合

## Required workflow
1.读取所有输入巡检 `.md` 文件。
2.逐个文件按 Markdown结构手动解析，不依赖脚本：
 - 报告头部项目表
 - `##` 一级章节
 - `###` 二级章节
 -关键表格
 -关键结论 bullet
3.识别每个节点的核心标识：
 - 节点名 / hostname
 - 地址 /端口
 - 实例标识
 - MySQL版本
 - `server_id` / `server_uuid`
 - `read_only` / `super_read_only`
 -复制或集群角色
4. 根据 `references/topology-guidelines.md` 判断整体拓扑。
5. 根据 `references/data-mapping.md` 将原始章节映射到报告语义层。
6. 按 `references/report-template.md` 输出最终报告。
7. 报告必须是“分析结果 + 风险判断 + 整改建议”，不是对原始表格的逐段搬运。
8. 报告正文默认按14 个核心章节组织；若某章节因拓扑或采集范围不适用，可保留章节并明确写“本实例不适用”或“未采集到足够证据”。
9. 对错误日志与慢查询执行“时间窗口 + 噪声过滤”后再下结论（规则见下文）。

## Manual parsing guidance
在没有脚本的情况下，优先从以下位置抽取信息：
- 报告头：生成时间、实例标识、目标地址、MySQL版本
- `### 主机与内核`：节点名、OS
- `### 网络与磁盘`：IP、磁盘使用率、数据盘信息
- `### 配置快照`：关键参数
- `### 全局状态快照`：缓存、连接、慢查询等关键状态
- `### SHOW REPLICA STATUS` / `### Group Replication (MGR) 状态` / `### Galera/PXC 状态`：拓扑与角色判断
- `## 健康检查总结`：风险收敛

## Output requirements
- 最终输出格式必须为 Markdown。
- 使用正式、专业、适合 DBA / 运维汇报的中文风格。
- 输出必须为 **单一 Markdown 文件**（单文件交付）。
- 报告中 **禁止使用外部链接**（包括 `file:///`、相对路径链接、任何跳转到采集文件的链接）。
- 硬规则：输出中 **禁止出现任何 Markdown 链接语法** `](`。
-允许的唯一例外：目录 / 文内锚点链接 `](#...)`（仅用于本文件内跳转）。
- 所有关键证据必须在报告内直接呈现：以表格或代码块节选方式内嵌。
- 为避免报告过长，每类证据默认取 Top N / 最近 N（例如 Top20、最近50）；完整原始采集作为“输入材料”，不在报告中用链接引用。
- 报告必须包含以下14 个核心章节（可按拓扑标注不适用，但不要静默省略）：
1. 实例概览
2. 总体健康评分 / 风险摘要
3. 参数检查与调整建议
4. InnoDB 状态分析
5. 锁、事务与死锁分析
6. 错误日志分析
7. 慢查询与 TOP SQL 分析
8.连接与线程分析
9. 表与索引健康检查
10.复制健康检查
11.资源与容量风险分析
12. 安全与合规配置检查
13.采集完整性与结论可信度说明
14. 整改建议清单（按优先级排序）
- 必须给出结论，不要只给“建议可能关注”。
- 如果证据不足，明确写“信息不足 / 未采集到 / 无法确认”，不要编造。

## 时间窗口与噪声过滤（必须执行）
### 错误日志时间窗口
- 默认“当前风险”仅统计近30 天异常。
-30 天前异常归类为“历史事件”，可在附录保留，不计入当前高风险数量。
- 如用户明确要求全历史分析，可覆盖默认窗口，并在报告中声明。

### 慢 SQL过滤规则
- 慢日志优先于 `performance_schema` / `sys` 汇总。
- 当仅有 `P_S` / `sys` 时，过滤以下噪声：
 - 巡检脚本自查询（`SHOW VARIABLES`、`SHOW GLOBAL STATUS`、`information_schema` / `performance_schema` 元数据查询）。
 - 无业务语义的会话设置（`SET SESSION ...`）与通用提交语句（`COMMIT`）。
- 优先保留业务库（非系统库）且“高耗时 / 高扫描 / 高频”的 SQL 模板。

##证据内嵌规范（必须执行）
- 每个结论后至少跟随1份“可复核证据”，证据必须来自输入采集文件内容本身。
-证据呈现格式：
 - 表格：适用于固定结构（如 MGR 成员、`read_only` / `super_read_only`、账户列表、备份检查、关键参数）。
 -代码块：适用于日志片段（如 error log关键异常、复制 / 高可用关键异常）。
- 多节点场景：
 -先汇总表（节点对比、成员表、风险清单）。
 - 再按节点给“证据节选”，不要要求读者打开采集文件。

## Report writing rules
- 优先保留有决策价值的信息：复制状态、角色、延迟、容量、缓存利用率、慢查询风险、安全风险、备份有效性、无主键表、表缓存溢出、参数冲突。
- 报告正文建议每节按“结论 →关键指标 →发现的问题 →影响评估 → 优化建议 →证据来源”组织，保持先结论后证据。
- `实例概览` 必须说明实例 / 节点标识、版本、角色、采集时间范围、核心负载概况。
- `总体健康评分 / 风险摘要` 必须汇总高 / 中 /低风险数量，并给出最需要优先处理的3~5 项问题。
- `参数检查与调整建议` 必须同时写当前值、建议方向、判断依据、调整风险。
- `InnoDB 状态分析` 必须覆盖 Buffer Pool、Checkpoint / Redo、Purge / History List、刷写或等待异常。
- `锁、事务与死锁分析` 必须提炼长事务、大事务、锁等待、死锁、metadata lock、热点争用等结论。
- `错误日志分析` 必须分类说明错误类型、出现频次、时间分布、影响与建议。
- `慢查询与 TOP SQL 分析` 必须提炼总耗时 / 平均耗时 / 执行次数靠前的业务 SQL，并说明扫描、临时表、索引等风险。
- `连接与线程分析` 必须覆盖连接使用率、活跃线程、sleep连接、线程缓存、aborted连接等指标。
- `表与索引健康检查` 必须覆盖无主键表、重复 / 冗余索引、超大表、碎片、字符集 / 排序规则异常等结构问题。
- `复制健康检查`仅在主备、MGR、Galera / PXC 等场景重点展开；若为单实例需明确写“不适用”。
- `资源与容量风险分析` 必须结合 CPU / 内存 / 磁盘 / IO / 增长趋势判断主要瓶颈与扩容风险。
- `安全与合规配置检查` 必须覆盖账号权限、远程 root、日志与审计相关参数、`sql_mode`、`local_infile`、`secure_file_priv` 等风险项。
- `采集完整性与结论可信度说明` 必须明确缺失的数据项、单点快照限制、是否缺少 error log / slow log / `performance_schema`，以及哪些结论需要补采复核。
- `整改建议清单` 必须按优先级输出问题、影响范围、建议动作、证据来源，避免只给零散建议。
- 大表格只摘录最有价值的 Top N，不要把原始1000 行表格全部复制进正文。
- 对每个风险项尽量给出：现象、影响、证据、建议。
- 如果多个节点存在同类问题，汇总后再列出节点差异。
- 如果发现配置和值矛盾，优先相信“实际状态 / 状态变量 / 实例输出”，并指出“配置声明与实际生效值不一致”。

## Topology-specific guidance
### Single instance
重点写：实例健康、容量、性能、配置、安全、备份、可恢复性。

### Primary-replica / async replication
必须补充：
- 主从角色识别依据
-复制线程 / 延迟 / GTID / binlog 格式
- `read_only` / `super_read_only` 是否合理
- 主备配置差异与风险

### MGR
必须补充：
- 成员数量
- ONLINE / OFFLINE 状态
- PRIMARY 数量是否正常
- `group_replication`关键参数
- 一致性与退出策略风险

### Galera / PXC
必须补充：
- `wsrep_cluster_size`
- `wsrep_cluster_status`
- `wsrep_ready` / `wsrep_connected`
- flow control / recv queue / send queue 风险

### Unknown multi-node set
如果能确认是多节点但无法确定完整拓扑：
-先给出每节点摘要
- 再输出跨节点共性问题和差异项
- 明确说明拓扑判断不完整的原因

## Risk scoring guidance
默认按以下思路分级：
- 高风险：`root@'%'`、复制异常、备份失效、集群成员异常、明显安全或可恢复性问题
- 中风险：表缓存溢出、无主键表、高频全表扫描、重要参数不合理、error log 不可读
-低风险：可优化但暂未形成直接故障风险的项，如碎片、未使用索引、资源富余配置

## Important reminders
- 不要假设只有两节点。用户已明确需要支持单节点、双文件主备、多文件 MGR、Galera、PXC。
- 不要只依赖文件名推断角色；文件内容优先。
- 如果用户提供了参考报告文字版，应尽量对齐它的章节组织和表达风格。
- 若需要保留原始证据，将其放入“附录 /证据摘录”，正文保持精炼。
-这个 skill 不包含脚本，所有行为都应依靠当前文档和 reference 文档完成。

## Reference files
在开始前按需阅读：
- `references/report-template.md`
- `references/data-mapping.md`
- `references/topology-guidelines.md`
