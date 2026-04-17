# 多节点拓扑识别与对比规则

本文件定义在单文件、双文件、多文件场景下，如何从原始巡检数据中识别节点角色与整体拓扑。

## 1. 总体原则
- 文件名可作为辅助，但不能作为唯一依据。
- 以文件中的配置、状态和复制/集群章节为准。
- 若不同证据冲突，应优先相信运行时状态和显式集群状态输出。
- 信息不足时输出“未知多节点巡检汇总”，不要强行判断。

## 2. 节点级字段优先抽取
每个文件至少抽取：
- hostname
- target_address
- instance_tag
- mysql_version
- server_id
- server_uuid
- read_only
- super_read_only
- replication_summary
- mgr_summary
- wsrep_summary

## 3. 单节点识别
满足以下条件时，可视为单节点：
- 未发现 `SHOW REPLICA STATUS` / `SHOW SLAVE STATUS` 证据
- 未发现 MGR 成员表
- 未发现 `wsrep_*` 集群状态
- 用户仅提供单个采集文件，且内容无复制/集群证据

输出重点：实例健康、性能、配置、安全、备份。

## 4. 主备 / 异步复制识别
满足以下任一组合时，优先判断为主备或异步复制：
- 某节点存在 `SHOW REPLICA STATUS` 或 `SHOW SLAVE STATUS`
- 节点配置中出现 `relay_log`、`relay_log_recovery`、`replica_parallel_workers`
- 某节点 `read_only=ON` / `super_read_only=ON`，另一个节点为 OFF

### 角色判断建议
- 同时存在 `SHOW REPLICA STATUS` 且线程正常的节点，优先标记为“从库/副本”
- `read_only=OFF` 且另一个节点为 ON 时，OFF 一侧通常为主库
- 如果多个节点都能看到复制信息，但方向不清晰，标记为“复制节点（角色待确认）”

### 主备场景必须输出
- 节点角色表
- 复制状态摘要
- 延迟与线程状态
- 只读状态差异
- 关键参数差异

## 5. MGR 识别
满足以下条件时，判断为 MGR：
- 出现 `Group Replication (MGR) 状态`
- 出现 `performance_schema.replication_group_members`
- 出现 `group_replication_*` 关键状态或参数

### MGR 核心关注点
- 成员总数
- ONLINE / OFFLINE / RECOVERING 状态
- PRIMARY 数量是否为 1（单主模式）
- `group_replication_single_primary_mode`
- `group_replication_consistency`
- `group_replication_exit_state_action`

### MGR 报告要求
- 输出集群成员表
- 标出 PRIMARY / SECONDARY
- 若存在非 ONLINE 成员，直接列为高风险

## 6. Galera / PXC 识别
满足以下条件时，判断为 Galera / PXC：
- 出现 `Galera/PXC 状态`
- 出现 `wsrep_cluster_size`
- 出现 `wsrep_cluster_status`
- 出现 `wsrep_ready` / `wsrep_connected`

### Galera / PXC 核心关注点
- `wsrep_cluster_size`
- `wsrep_cluster_status`
- `wsrep_ready`
- `wsrep_connected`
- `wsrep_flow_control_paused`
- `wsrep_local_recv_queue_avg`
- `wsrep_local_send_queue_avg`

### Galera / PXC 报告要求
- 输出节点状态汇总
- 识别是否 Primary 组件
- 如 flow control 或队列指标偏高，列为中高风险

## 7. 未知多节点场景
当用户给出多份文件，但无法可靠判断是主备、MGR 或 Galera/PXC 时：
- 先输出每节点概况
- 再输出跨节点共性问题
- 最后输出关键差异项
- 明确声明“拓扑判断依据不足，以下按多节点汇总处理”

## 8. 节点对比表建议字段
| 节点 | 角色 | 地址 | 版本 | server_id | read_only | 复制/集群状态 | 库容量 | 高风险项 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 9. 差异分析建议
多节点场景下，优先比较：
- 角色与只读状态
- 复制线程 / 集群成员状态
- 库容量与对象数量
- Buffer Pool 实际利用率
- Table Cache miss/overflow
- 慢查询与全表扫描风险
- 备份可见性
- 安全账号风险

## 10. 证据不足时的表达方式
推荐措辞：
- “根据现有采集结果初步判断”
- “当前证据显示该节点更可能为副本节点”
- “未采集到足够证据确认完整拓扑关系”
- “以下分析按多节点汇总视角展开”