# MySQL 8.0 InnoDB 表空间损坏恢复手册

> **适用场景**：MySQL 8.0（Oracle 官方版）因 undo 表空间损坏 + 业务表数据页损坏导致无法启动的完整恢复流程。
>
> **环境**：CentOS/RHEL 7、MySQL 8.0.19、InnoDB 引擎、独立表空间（innodb_file_per_table=ON）

---

## 一、故障现象

MySQL 启动失败，错误日志中出现以下关键报错：

```
# 阶段一：undo 表空间损坏
Space ID in fsp header is 131128, but in the page header it is 4294946832
FATAL: Tablespace id is 4294946832 in the data dictionary but in file ./undo_001 it is 4294967295!
Assertion failure: ut0ut.cc:536 thread ...

# 阶段二：业务表数据页损坏（移走 undo 文件后出现）
[ERROR] [InnoDB] Database page corruption on disk or a failed read of page
[page id: space=33639, page number=18837]. You may have to recover from a backup.

# 附加：业务表 .ibd 文件缺失
[Warning] Tablespace 127292, name './autocamel_ynd/lta_bf',
file './autocamel_ynd/lta_bf.ibd' is missing!
```

---

## 二、根因分析

### 2.1 undo 表空间损坏

- `undo_001` 文件头中的 space_id 为 `4294967295`（即 `0xFFFFFFFF`，未初始化的全 F 值）
- 数据字典记录的 space_id 为 `4294946832`，两者不匹配
- **文件头在校验阶段就触发 assertion，早于崩溃恢复的回滚阶段**

常见诱因：
- 磁盘空间写满
- `kill -9` 强杀 MySQL 进程
- 服务器异常掉电
- 底层磁盘/文件系统 I/O 异常

### 2.2 业务表数据页损坏

- undo 问题解决后，InnoDB 崩溃恢复继续进行
- 读取某业务表（tablespace id=33639）的第 18837 页时发现页损坏
- `innodb_force_recovery=6` 默认对页损坏执行 assert 崩溃，无法继续启动

### 2.3 为什么关 binlog 无效

| 机制 | 所属层 | 作用 | 崩溃恢复顺序 |
|------|--------|------|-------------|
| **undo log** | InnoDB 引擎层 | 回滚未提交事务 | 第 2 步（必须执行） |
| **redo log** | InnoDB 引擎层 | 重做已提交未落盘事务 | 第 1 步（必须执行） |
| **binlog** | MySQL Server 层 | 主从复制、PITR | 第 3 步（最后执行） |

undo 回滚是 InnoDB 引擎层行为，binlog 是 Server 层行为，两者独立。**关闭 binlog 只跳过第 3 步，不影响第 2 步的 undo 回滚。**

### 2.4 为什么 innodb_corrupt_table_action 不可用

| 发行版 | 是否支持 innodb_corrupt_table_action |
|--------|--------------------------------------|
| MariaDB | ✅ 原生支持（XtraDB 引擎） |
| Percona Server for MySQL | ✅ 支持（8.0.12-1 起） |
| **Oracle MySQL 8.0** | ❌ **不支持** |

Oracle MySQL 8.0 没有此参数，在 my.cnf 中添加会导致 `unknown variable` 启动失败。

---

## 三、恢复流程

### 总览

```
undo 损坏 → 移走 undo 文件
                ↓
         force_recovery=6 启动
                ↓
         业务表页损坏 → 定位 .ibd → 移走 .ibd
                ↓
         启动成功 → mysqldump 导出 → 重建实例
```

### 第 1 步：移走损坏的 undo 表空间文件

```bash
# 进入数据目录
cd /home/data/mysql-8.0.19-el7-x86_64/data

# 创建备份目录
mkdir -p /home/data/undo-corrupt-backup

# 备份 + 移走 undo 文件（不要删除，移走即可）
cp undo_001 /home/data/undo-corrupt-backup/undo_001.bak
cp undo_002 /home/data/undo-corrupt-backup/undo_002.bak 2>/dev/null

mv undo_001 /home/data/undo-corrupt-backup/undo_001.moved
mv undo_002 /home/data/undo-corrupt-backup/undo_002.moved 2>/dev/null
```

> **原理**：MySQL 8.0 会自动重建缺失的 undo 表空间。移走损坏文件后，启动时 MySQL 创建全新的空 undo 文件。

### 第 2 步：配置 my.cnf 强制恢复

```ini
[mysqld]
innodb_force_recovery = 6
```

`innodb_force_recovery` 各档位说明：

| 档位 | 行为 | 风险 |
|------|------|------|
| 1 | 检测到坏页也继续运行，SELECT 跳过坏页 | 低 |
| 2 | 阻止主线程和清除线程运行 | 低 |
| 3 | 崩溃恢复后不执行回滚 | 中 |
| 4 | 插入缓冲不合并，不计算统计信息 | 高 |
| 5 | 启动时不查看 undo log，将未完成事务视为已提交 | 高 |
| **6** | **不做崩溃恢复（无 redo 重做、无 undo 回滚）** | **最高** |

> **注意**：6 档跳过整个崩溃恢复，实例进入只读不一致状态。仅用于抢救数据，不可长期运行。

### 第 3 步：首次启动尝试

```bash
# 确认 MySQL 完全停止
pkill -9 mysqld
sleep 3

# 启动
mysqld_safe --user=mysql &
tail -f /home/data/mysql-8.0.19-el7-x86_64/log/mysqld.log
```

**预期结果**：undo 问题解决（日志出现 `XA crash recovery finished successfully`），但可能暴露新的业务表页损坏错误。

### 第 4 步：定位损坏的业务表 .ibd 文件

如果日志出现 `Database page corruption ... space=XXXXX`，需要找到对应的 .ibd 文件。

#### 4.1 计算目标 space_id 的十六进制值

```bash
# 以 space=33639 为例
python3 -c "print(format(33639, '08x'))"
# 输出: 00008367
```

或手动计算：33639 = 0x8367 → 大端序 4 字节 = `00008367`

#### 4.2 扫描所有 .ibd 文件的 FIL_PAGE_SPACE_ID

InnoDB .ibd 文件页头结构：

```
偏移 0     (4字节)  保留
偏移 4     (4字节)  页号 (FIL_PAGE_OFFSET)
偏移 8     (4字节)  前一页指针
偏移 12    (4字节)  后一页指针
偏移 16    (8字节)  LSN
偏移 24    (2字节)  页类型
偏移 26    (8字节)  文件 flush LSN
偏移 34    (4字节)  ★ space_id (FIL_PAGE_SPACE_ID)
```

**方法 A：使用 xxd（需安装 vim-common）**

```bash
# 安装 xxd
yum install -y vim-common

# 扫描所有 .ibd，查找 space_id=33639(0x8367)
for f in $(find /home/data/mysql-8.0.19-el7-x86_64/data -name '*.ibd' -type f); do
  sid=$(xxd -s 34 -l 4 -p "$f" 2>/dev/null)
  if [ "$sid" = "00008367" ]; then
    echo "★ FOUND: $f"
  fi
done
```

`xxd` 参数说明：

| 参数 | 含义 |
|------|------|
| `-s 34` | 从第 34 字节开始读（skip） |
| `-l 4` | 只读 4 字节（length） |
| `-p` | 纯十六进制输出（plain），无地址和 ASCII |

**方法 B：使用 od（系统自带，无需安装）**

```bash
for f in $(find /home/data/mysql-8.0.19-el7-x86_64/data -name '*.ibd' -type f); do
  sid=$(od -A n -t x1 -j 34 -N 4 "$f" 2>/dev/null | tr -d ' \n')
  if [ "$sid" = "00008367" ]; then
    echo "★ FOUND: $f"
  fi
done
```

`od` 参数说明：

| 参数 | 含义 |
|------|------|
| `-A n` | 不显示地址列 |
| `-t x1` | 以单字节十六进制输出 |
| `-j 34` | 跳过前 34 字节 |
| `-N 4` | 只读 4 字节 |
| `tr -d ' \n'` | 去掉空格和换行 |

**方法 C：列出所有 .ibd 的 space_id（排查全貌）**

```bash
for f in $(find /home/data/mysql-8.0.19-el7-x86_64/data -name '*.ibd' -type f); do
  printf "%s  %s\n" "$(od -A n -t x1 -j 34 -N 4 "$f" 2>/dev/null | tr -d ' \n')" "$f"
done | sort
```

### 第 5 步：移走损坏的业务表 .ibd 文件

```bash
# 备份 + 移走（与 undo 相同的处理方式）
mkdir -p /home/data/ibd-corrupt-backup

# 替换为实际找到的文件路径
CORRUPT_IBD="<第4步找到的文件路径>"

cp "$CORRUPT_IBD" /home/data/ibd-corrupt-backup/
mv "$CORRUPT_IBD" /home/data/ibd-corrupt-backup/

# 重启 MySQL
pkill -9 mysqld; sleep 3
mysqld_safe --user=mysql &
tail -f /home/data/mysql-8.0.19-el7-x86_64/log/mysqld.log
```

> **原理**：MySQL 会 warning 该表空间缺失，但不影响启动。损坏的表数据将丢失，其他表正常。

### 第 6 步：启动成功后立即导出数据

```bash
# 全量导出，跳过损坏的表和缺失的表
mysqldump -uroot -p --all-databases \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  --ignore-table=<损坏的库>.<损坏的表> \
  --ignore-table=autocamel_ynd.lta_bf \
  > /home/data/backup_all_$(date +%Y%m%d_%H%M%S).sql
```

> **注意**：
> - 如果某张表导出报错，加 `--ignore-table=库名.表名` 跳过，先保住能救的数据
> - force_recovery=6 模式下数据库为只读，mysqldump 可以正常读取
> - 导出文件务必确认大小合理后再进行下一步

### 第 7 步：重建干净的实例

```bash
# 1. 停库
mysqladmin -uroot -p shutdown

# 2. 备份旧数据目录（不要删除）
mv /home/data/mysql-8.0.19-el7-x86_64/data /home/data/mysql-8.0.19-el7-x86_64/data.corrupt

# 3. 重新初始化数据目录
mysqld --initialize-insecure --user=mysql \
  --datadir=/home/data/mysql-8.0.19-el7-x86_64/data

# 4. my.cnf 注释掉 innodb_force_recovery（恢复正常模式）
#    将 innodb_force_recovery = 6 改为 # innodb_force_recovery = 6

# 5. 正常启动
mysqld_safe --user=mysql &

# 6. 导入数据
mysql -uroot < /home/data/backup_all_XXXX_XXXXXX.sql

# 7. 验证数据完整性
mysql -uroot -p -e "SHOW DATABASES;"
mysql -uroot -p -e "SELECT COUNT(*) FROM <关键业务表>;"
```

### 第 8 步：处理丢失的表

移走的损坏表数据已丢失，需根据业务情况恢复：

| 表类型 | 恢复方式 |
|--------|----------|
| 配置/字典表 | 手动重新插入 |
| 业务数据表 | 从上游系统/缓存/日志重放 |
| 日志类表 | 可接受丢失，重建空表 |
| 核心业务表无备份 | 需专业数据恢复工具（如 Percona undrop-for-innodb） |

---

## 四、关键参数速查

### innodb_force_recovery 档位选择策略

```
能正常启动？
  ├── 是 → 不需要 force_recovery
  └── 否 → 试 1 档
              ├── 起来了 → 导出数据（1档会跳过坏页）
              └── 起不来 → 试 2 → 3 → 4 → 5 → 6
                              └── 6 档仍失败 → 移走损坏文件后再试
```

### undo vs redo vs binlog 对比

| 维度 | undo log | redo log | binlog |
|------|----------|----------|--------|
| 所属层 | InnoDB 引擎 | InnoDB 引擎 | MySQL Server |
| 记录内容 | 修改前的旧值（before image） | 修改后的新值（after image） | 已提交的 SQL/行变更 |
| 用途 | 回滚、MVCC | 崩溃恢复重做 | 主从复制、PITR |
| 崩溃恢复 | 第 2 步执行 | 第 1 步执行 | 第 3 步执行 |
| 关闭影响 | 不可关闭 | 不可关闭 | 可关闭，仅影响复制 |

---

## 五、磁盘健康检查

页损坏通常伴随底层 I/O 异常，务必排查：

```bash
# 检查磁盘空间
df -h

# 检查内核 I/O 错误日志
dmesg | grep -iE 'i/o|error|sd|xvd' | tail -50

# 检查硬盘 SMART 健康
smartctl -a /dev/sda

# 检查文件系统
mount | grep data    # 确认不是 tmpfs/nfs 等不稳定存储
xfs_db -c frag /dev/sda1   # XFS 文件系统碎片检查
```

---

## 六、预防措施

| 措施 | 说明 |
|------|------|
| **定期备份** | mysqldump 逻辑备份 + Percona XtraBackup 物理备份，至少每日一次 |
| **不要 kill -9** | 使用 `mysqladmin shutdown` 优雅关闭 |
| **监控磁盘空间** | 设置告警，磁盘使用率 > 80% 时通知 |
| **UPS 不间断电源** | 防止异常掉电导致文件损坏 |
| **sync_binlog=1** | 开启主从复制时确保 binlog 同步刷盘 |
| **innodb_flush_log_at_trx_commit=1** | 保持默认值，确保 redo log 每事务刷盘 |
| **RAID / 云盘多副本** | 底层存储冗余，防单盘故障 |
| **监控 MySQL 错误日志** | 定期检查 `mysqld.log` 中的 InnoDB warning |

---

## 七、故障处理时间线（本次案例）

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | 发现 undo_001 space_id 不匹配 | 确认 undo 表空间损坏 |
| 2 | 确认 force_recovery=6 无法跳过 | 文件头校验早于回滚阶段 |
| 3 | 移走 undo_001/002 文件 | MySQL 进入 XA crash recovery |
| 4 | 发现业务表 space=33639 页损坏 | force_recovery=6 默认 assert 崩溃 |
| 5 | 确认 innodb_corrupt_table_action 不可用 | Oracle MySQL 8.0 无此参数 |
| 6 | 用 od/xxd 扫描 .ibd 文件头 FIL_PAGE_SPACE_ID | 定位到 space=33639 的 .ibd 文件 |
| 7 | 移走损坏的 .ibd 文件 | **MySQL 启动成功** |
| 8 | mysqldump 导出数据 | 待执行 |
| 9 | 重建实例 + 导入 | 待执行 |

---

## 八、附：常用命令速查

```bash
# 查看 MySQL 错误日志
tail -100f /home/data/mysql-8.0.19-el7-x86_64/log/mysqld.log

# 优雅停库
mysqladmin -uroot -p shutdown

# 强制停库（最后手段）
pkill -9 mysqld

# 查看当前 force_recovery 档位
mysql -uroot -p -e "SHOW VARIABLES LIKE 'innodb_force_recovery'"

# 查看所有表空间
mysql -uroot -p -e "SELECT SPACE, NAME, SPACE_TYPE FROM INFORMATION_SCHEMA.INNODB_TABLESPACES ORDER BY SPACE"

# 全量导出
mysqldump -uroot -p --all-databases --single-transaction --routines --triggers --events > backup.sql

# 重新初始化数据目录
mysqld --initialize-insecure --user=mysql --datadir=/path/to/data

# 查看 .ibd 文件的 space_id
od -A n -t x1 -j 34 -N 4 table.ibd | tr -d ' \n'
```

---

*文档生成时间：2026-07-30*
*适用版本：MySQL 8.0.x（Oracle 官方版）*
