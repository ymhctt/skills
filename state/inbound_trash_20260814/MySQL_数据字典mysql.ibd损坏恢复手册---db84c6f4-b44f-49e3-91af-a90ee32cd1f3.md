# MySQL 8.0 数据字典 (mysql.ibd) 损坏恢复手册

> **适用场景**：MySQL 8.0（Oracle 官方版）数据字典文件 `mysql.ibd` 损坏，导致实例无法启动、表结构元数据全部丢失的终极恢复流程。
>
> **前置条件**：已按《InnoDB 表空间损坏恢复手册》完成 undo 表空间和业务表损坏 .ibd 的移走处理，但 MySQL 仍然无法启动。
>
> **环境**：CentOS/RHEL 7、MySQL 8.0.19、InnoDB 引擎、独立表空间（innodb_file_per_table=ON）

---

## 一、故障现象

错误日志中出现 `mysql.ibd` 的页损坏报错：

```
[ERROR] [InnoDB] Database page corruption on disk or a failed read of page
[page id: space=4294967294, page number=828]. You may have to recover from a backup.
[page id: space=4294967294, page number=76].
[page id: space=4294967294, page number=14354].
```

关键标识：

```
space=4294967294  →  0xFFFFFFFE
```

这是 MySQL 8.0 数据字典 `mysql.ibd` 的**固定 space_id**，与普通业务表不同。

---

## 二、mysql.ibd 是什么

### 2.1 MySQL 8.0 数据字典架构

MySQL 8.0 引入了**事务性数据字典（Transactional Data Dictionary, DD）**，将之前分散在 `.frm`、`.par`、`.TRN`、`.TRG` 等文件中的表结构元数据，统一存入 InnoDB 表中，位于 `mysql.ibd` 表空间内。

| 对象 | 存储位置 | 内容 |
|------|----------|------|
| **mysql.ibd** | 数据目录根 | 数据字典表：表/列/索引/外键/视图/库定义/存储过程等 |
| ibdata1 | 数据目录根 | 系统表空间（doublewrite buffer、change buffer 等） |
| *.ibd | 各数据库目录 | 各业务表的独立表空间（含表数据 + SDI 元数据） |

### 2.2 mysql.ibd 损坏的严重性

| 维度 | 普通业务表 .ibd 损坏 | **mysql.ibd 损坏** |
|------|---------------------|-------------------|
| 影响范围 | 单张表数据丢失 | **所有表的元数据丢失** |
| MySQL 能否启动 | 可跳过该表 | **通常无法启动** |
| 表结构是否丢失 | 不丢失（DD 完好） | **全部丢失**（DD 坏了） |
| 恢复难度 | 中等 | **高** |

### 2.3 space_id 固定值

```
mysql.ibd 的 space_id = 4294967294 = 0xFFFFFFFE
```

这是 MySQL 8.0 源码中硬编码的值，不会变化。日志中看到 `space=4294967294` 即可确认是数据字典损坏。

---

## 三、恢复策略总览

```
有备份？
  ├── 有 → 直接还原备份（最快、最安全，强烈推荐）
  └── 无 → 走 ibd2sdi 恢复路线
              ↓
         第1步：先试 force_recovery=1（可能只坏部分页）
              ├── 启动成功 → mysqldump 导出 → 重建实例
              └── 启动失败
                    ↓
         第2步：移走 mysql.ibd，让 MySQL 重建空数据字典
              ↓
         第3步：用 ibd2sdi 从各 .ibd 文件提取表结构
              ↓
         第4步：执行 CREATE TABLE 重建表结构
              ↓
         第5步：IMPORT TABLESPACE 装回数据
              ↓
         第6步：mysqldump 全量导出 → 重建干净实例
```

---

## 四、详细恢复步骤

### 第 0 步：紧急备份（必做）

在进行任何操作前，先备份整个数据目录：

```bash
# 停掉 MySQL
pkill -9 mysqld
sleep 3

# 完整备份（cp -a 保留权限和属主）
cp -a /var/lib/mysql /var/lib/mysql.full.bak.$(date +%Y%m%d_%H%M%S)
```

> **这一步绝对不能跳过。** 后面移走文件的操作是不可逆的，出问题只能靠这个备份回滚。

### 第 1 步：先试 force_recovery=1

mysql.ibd 可能只是部分页损坏，1 档会跳过坏页继续运行：

```bash
# 编辑 my.cnf
# 将 innodb_force_recovery = 6 改为 innodb_force_recovery = 1
sed -i 's/innodb_force_recovery = 6/innodb_force_recovery = 1/' /etc/my.cnf

# 启动
mysqld_safe --user=mysql &
tail -f /var/log/mysqld/mysqld.log
```

**判断结果：**

| 结果 | 下一步 |
|------|--------|
| 启动成功，能连上 | 立即 mysqldump 导出，跳到第 6 步 |
| 仍然报 mysql.ibd 页损坏 | 继续第 2 步 |
| 报别的错误 | 根据日志判断，可能 ibdata1 也有问题 |

### 第 2 步：移走损坏的 mysql.ibd

```bash
# 确保 MySQL 已停止
pkill -9 mysqld
sleep 3

# 备份 + 移走损坏的 mysql.ibd
mkdir -p /var/lib/mysql/system-corrupt-backup
cp /var/lib/mysql/mysql.ibd /var/lib/mysql/system-corrupt-backup/
mv /var/lib/mysql/mysql.ibd /var/lib/mysql/system-corrupt-backup/

# 同时检查 ibdata1 是否也需要移走
ls -la /var/lib/mysql/ibdata*
# 如果 ibdata1 也有损坏报错，同样备份后移走
# cp /var/lib/mysql/ibdata1 /var/lib/mysql/system-corrupt-backup/
# mv /var/lib/mysql/ibdata1 /var/lib/mysql/system-corrupt-backup/

# my.cnf 保持 force_recovery=1（或注释掉）
# 启动
mysqld_safe --user=mysql &
tail -f /var/log/mysqld/mysqld.log
```

**预期结果：**

- MySQL 检测到 `mysql.ibd` 缺失，**自动重建一个空的数据字典**
- 系统表（mysql.user、information_schema 等）会自动建好
- **用户库和表全部消失** —— 这是正常的，下一步用 ibd2sdi 恢复

验证启动成功：

```bash
ps -ef | grep mysqld
mysql -uroot -e "SELECT 1"
mysql -uroot -e "SHOW DATABASES;"
# 应该只能看到系统库：mysql, sys, information_schema, performance_schema
```

### 第 3 步：用 ibd2sdi 提取表结构

#### 3.1 什么是 ibd2sdi

`ibd2sdi` 是 MySQL 8.0 自带的命令行工具，能**直接从 .ibd 文件中读取 SDI（Serialized Dictionary Information）**，不依赖数据字典。

SDI 是 MySQL 8.0 在每个独立表空间 .ibd 文件中嵌入的**序列化字典信息**，包含：
- 表名、列定义、列类型
- 索引定义
- 表选项（引擎、字符集等）

> **关键点**：即使 `mysql.ibd`（数据字典）完全损坏，只要各业务表的 `.ibd` 文件还在，就能从中提取出完整的表结构。

#### 3.2 确认 ibd2sdi 可用

```bash
# 查找 ibd2sdi 位置
which ibd2sdi
# 通常在 MySQL 安装目录的 bin/ 下
ls /app/mysql/bin/ibd2sdi
# 或
ls /usr/local/mysql/bin/ibd2sdi
```

#### 3.3 手动查看单个 .ibd 的 SDI

```bash
# 以 test 库的 t1 表为例
/app/mysql/bin/ibd2sdi /var/lib/mysql/test/t1.ibd | head -80
```

输出格式（JSON 数组）：

```json
[
  "ibd2sdi",                          ← 字符串，不是对象，解析时要跳过
  {
    "type": 1,                        ← 1 = 表对象
    "object": {
      "dd_object": {
        "name": "t1",
        "columns": [
          {
            "name": "id",
            "type": 3,               ← MySQL 类型码
            "column_type_utf8": "int",  ← 人类可读类型
            "is_nullable": false,
            "is_auto_increment": true,
            ...
          },
          ...
        ],
        "indexes": [
          {
            "name": "PRIMARY",
            "type": 1,               ← 1 = 主键
            "elements": [
              {"column_name": "id", ...},
              ...
            ]
          }
        ]
      }
    }
  },
  {
    "type": 2,                        ← 2 = 表空间对象
    ...
  }
]
```

#### 3.4 批量提取脚本

使用 `recover_dd.py` 脚本自动批量提取所有 .ibd 文件的表结构：

```bash
python3 recover_dd.py /var/lib/mysql \
  --ibd2sdi /app/mysql/bin/ibd2sdi \
  --output /tmp/recover_tables.sql
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `数据目录` | 第一个位置参数，MySQL 数据目录路径 |
| `--ibd2sdi` | ibd2sdi 二进制完整路径 |
| `--output` | 输出的 SQL 文件路径 |
| `--dump-json` | 同时输出原始 JSON（调试用） |
| `--only` | 只处理指定的 .ibd 文件 |

**脚本行为：**
- 自动跳过系统库（mysql、sys、performance_schema、information_schema）
- 自动跳过系统文件（ibdata、ib_logfile、undo）
- 从每个 .ibd 提取 SDI，重建 CREATE TABLE 语句
- 跳过隐藏系统列（DB_TRX_ID、DB_ROLL_PTR 等，`hidden=2`）
- 重建索引定义（PRIMARY KEY / UNIQUE KEY / KEY）
- 生成两个文件：
  - `recover_tables.sql` — 所有 CREATE TABLE 语句
  - `recover_tables_import.sh` — IMPORT TABLESPACE 自动化脚本

**调试模式（遇到问题时用）：**

```bash
python3 recover_dd.py /var/lib/mysql \
  --ibd2sdi /app/mysql/bin/ibd2sdi \
  --output /tmp/recover_tables.sql \
  --dump-json
```

会在 `raw_json/` 目录下生成每个 .ibd 的原始 JSON，可手动检查格式。

### 第 4 步：执行 CREATE TABLE 重建表结构

```bash
# 检查生成的 SQL 文件
cat /tmp/recover_tables.sql | head -50

# 执行建表
mysql -uroot < /tmp/recover_tables.sql

# 验证
mysql -uroot -e "SHOW DATABASES;"
mysql -uroot -e "SHOW TABLES FROM test;"
```

> **注意**：此时表结构已建好，但表是**空的**。数据在第 5 步装回来。

### 第 5 步：IMPORT TABLESPACE 装回数据

#### 5.1 原理

MySQL 的 `ALTER TABLE ... IMPORT TABLESPACE` 可以将外部的 .ibd 文件导入到已建好结构的空表中。流程是：

```
DISCARD TABLESPACE（丢弃当前空 .ibd）
      ↓
复制原始 .ibd 文件到表目录
      ↓
IMPORT TABLESPACE（加载 .ibd 数据）
```

#### 5.2 执行自动生成的脚本

```bash
# 检查脚本内容
cat /tmp/recover_tables_import.sh

# 执行
bash /tmp/recover_tables_import.sh
```

脚本对每张表执行：

```bash
mysql -uroot test -e "ALTER TABLE \`t1\` DISCARD TABLESPACE;"
cp /var/lib/mysql.bak/test/t1.ibd /var/lib/mysql/test/
chown mysql:mysql /var/lib/mysql/test/t1.ibd
mysql -uroot test -e "ALTER TABLE \`t1\` IMPORT TABLESPACE;"
```

#### 5.3 手动处理单张表（脚本失败时）

```bash
# 1. 丢弃当前空表空间
mysql -uroot test -e "ALTER TABLE t1 DISCARD TABLESPACE;"

# 2. 复制原始 .ibd 文件到表目录
#    注意：从备份目录复制，不要从当前数据目录（当前目录下的是刚 DISCARD 掉的）
cp /var/lib/mysql.full.bak.*/test/t1.ibd /var/lib/mysql/test/
chown mysql:mysql /var/lib/mysql/test/t1.ibd

# 3. 导入表空间
mysql -uroot test -e "ALTER TABLE t1 IMPORT TABLESPACE;"

# 4. 验证
mysql -uroot test -e "SELECT COUNT(*) FROM t1;"
```

#### 5.4 分区表的特殊处理

分区表的 .ibd 文件名格式为 `表名#p#分区名.ibd`（如 `server_logs#p#p2024q2.ibd`），IMPORT TABLESPACE 需要按分区逐个处理：

```bash
# 假设表 server_logs 有分区 p2024q2, p2024q3, p_future

# 对每个分区执行
mysql -uroot test -e "ALTER TABLE server_logs DISCARD PARTITION p2024q2 TABLESPACE;"
cp /var/lib/mysql.full.bak.*/test/server_logs#p#p2024q2.ibd /var/lib/mysql/test/
chown mysql:mysql "/var/lib/mysql/test/server_logs#p#p2024q2.ibd"
mysql -uroot test -e "ALTER TABLE server_logs IMPORT PARTITION p2024q2 TABLESPACE;"
```

> **注意**：自动生成的 `recover_tables_import.sh` 脚本可能不正确处理分区表。如果遇到分区表导入失败，需要手动按上述方式处理。

#### 5.5 IMPORT TABLESPACE 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `Tablespace is missing for 'test.t1'` | .ibd 文件没有放到正确位置 | 确认 .ibd 在 `/var/lib/mysql/库名/` 目录下 |
| `Schema mismatch (Table flags don't match)` | 建表时的行格式与原始不一致 | 加 `ROW_FORMAT=DYNAMIC` 重新建表 |
| `Space id in file ... is different` | .ibd 的 space_id 与新表不一致 | 新表 space_id 不同是正常的，IMPORT 会自动处理 |
| `corrupt page` | 原始 .ibd 本身有坏页 | 该表数据部分丢失，只能救回能读的页 |

### 第 6 步：全量导出 + 重建干净实例

所有表结构恢复、数据装回后，做一次完整导出，然后重建干净的实例：

```bash
# 1. 全量导出
mysqldump -uroot -p --all-databases \
  --single-transaction --routines --triggers --events \
  > /tmp/backup_final.sql

# 验证导出文件大小
ls -lh /tmp/backup_final.sql

# 2. 停库
mysqladmin -uroot -p shutdown

# 3. 备份旧数据目录
mv /var/lib/mysql /var/lib/mysql.recovered

# 4. 重新初始化
mysqld --initialize-insecure --user=mysql --datadir=/var/lib/mysql

# 5. my.cnf 注释掉 innodb_force_recovery（恢复正常模式）
#    将 innodb_force_recovery = 1 改为 # innodb_force_recovery = 1

# 6. 正常启动
mysqld_safe --user=mysql &

# 7. 导入数据
mysql -uroot < /tmp/backup_final.sql

# 8. 验证
mysql -uroot -e "SHOW DATABASES;"
mysql -uroot -e "SELECT COUNT(*) FROM test.t1;"
```

---

## 五、recover_dd.py 脚本说明

### 5.1 脚本核心逻辑

```
读取 .ibd → ibd2sdi 输出 JSON → 跳过首元素 "ibd2sdi" 字符串
  → 找 type=1 的表对象 → 解析 dd_object
  → 遍历 columns（跳过 hidden=2 的系统列）
  → 读取 column_type_utf8 获取列类型
  → 读取 is_nullable / is_auto_increment / default_value 获取列属性
  → 遍历 indexes 重建索引定义
  → 组装 CREATE TABLE 语句
  → 生成 IMPORT TABLESPACE 脚本
```

### 5.2 MySQL 类型码对照

当 `column_type_utf8` 字段缺失时，脚本用数字类型码做 fallback：

| 类型码 | 类型名 | 类型码 | 类型名 |
|--------|--------|--------|--------|
| 1 | tinyint | 16 | bit |
| 2 | smallint | 17 | timestamp2 |
| 3 | int | 18 | datetime2 |
| 4 | float | 19 | time2 |
| 5 | double | 20 | json |
| 7 | timestamp | 21 | newdecimal |
| 8 | bigint | 22 | enum |
| 9 | mediumint | 23 | set |
| 10 | date | 24 | tinyblob |
| 11 | time | 25 | mediumblob |
| 12 | datetime | 26 | longblob |
| 13 | year | 27 | blob |
| 15 | varchar | 28-29 | varbinary/binary |

### 5.3 Python 版本兼容性

脚本兼容 Python 3.6+。关键点：

```python
# ✅ 兼容 Python 3.6+ 的写法
result = subprocess.run(
    [ibd2sdi_bin, ibd_path],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    timeout=60
)
result.stdout = result.stdout.decode("utf-8", errors="replace")
result.stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""

# ❌ Python 3.7+ 才有的写法（Python 3.6 会报错）
# capture_output=True 是 3.7 新增参数
# text=True 也是 3.7+ 才有
result = subprocess.run(
    [ibd2sdi_bin, ibd_path],
    capture_output=True, text=True, timeout=60  # ← 3.6 报错
)
```

报错信息：

```
__init__() got an unexpected keyword argument 'capture_output'
```

### 5.4 脚本使用示例

```bash
# 基本用法
python3 recover_dd.py /var/lib/mysql \
  --ibd2sdi /app/mysql/bin/ibd2sdi \
  --output /tmp/recover_tables.sql

# 调试模式（输出原始 JSON）
python3 recover_dd.py /var/lib/mysql \
  --ibd2sdi /app/mysql/bin/ibd2sdi \
  --output /tmp/recover_tables.sql \
  --dump-json

# 只处理单个文件
python3 recover_dd.py /var/lib/mysql \
  --ibd2sdi /app/mysql/bin/ibd2sdi \
  --output /tmp/recover_t1.sql \
  --only /var/lib/mysql/test/t1.ibd
```

### 5.5 脚本输出文件

| 文件 | 内容 |
|------|------|
| `recover_tables.sql` | 所有表的 CREATE DATABASE + USE + CREATE TABLE 语句 |
| `recover_tables_import.sh` | 自动 IMPORT TABLESPACE 脚本 |
| `raw_json/库名.表名.json` | 原始 SDI JSON（仅 --dump-json 时） |

---

## 六、关键决策点

### 6.1 有备份 vs 无备份

| 情况 | 建议 |
|------|------|
| 有 XtraBackup 物理备份 | 直接还原，10 分钟搞定 |
| 有 mysqldump 逻辑备份 | 直接还原，导入即可 |
| 有 binlog | 还原最近备份后用 binlog 做 PITR |
| 有主从复制 | 提升从库为主库 |
| **什么都没有** | 走本文档的 ibd2sdi 恢复路线 |

### 6.2 force_recovery 档位选择

```
mysql.ibd 损坏后的档位策略：

  先试 1 档（可能只坏部分页，1 档跳过坏页）
    ├── 启动成功 → mysqldump 导出 → 重建实例
    └── 启动失败
          ↓
    移走 mysql.ibd（重建空 DD）
          ↓
    重新试 1 档或正常启动
    （此时 DD 是新的空的，不需要高档位了）
```

> **注意**：移走 mysql.ibd 后不需要 force_recovery=6。因为重建的空 DD 是干净的，正常启动即可。保留 1 档只是为了万一个别业务表也有坏页时能跳过。

### 6.3 什么情况下恢复会失败

| 情况 | 后果 |
|------|------|
| .ibd 文件的 SDI 页本身也损坏 | 该表结构无法提取，只能手动重建 |
| .ibd 文件被截断或部分丢失 | IMPORT TABLESPACE 可能失败，数据部分丢失 |
| ibdata1 也损坏 | 可能需要移走 ibdata1，影响更大 |
| 行格式不一致 | 需要手动指定 ROW_FORMAT 重新建表 |
| 分区表 | 脚本可能无法正确处理，需手动导入 |

---

## 七、磁盘健康检查

mysql.ibd 损坏几乎必然伴随底层磁盘问题：

```bash
# 检查磁盘空间
df -h

# 检查内核 I/O 错误日志
dmesg | grep -iE 'i/o|error|sd|xvd' | tail -50

# 检查硬盘 SMART 健康
smartctl -a /dev/sda

# 检查文件系统
mount | grep -E '/var/lib/mysql|/data'

# 如果是 LVM
lvs && vgs && pvs

# 检查 dmesg 中的具体 I/O 错误
dmesg -T | grep -i 'read error\|write error\|i/o error' | tail -20
```

---

## 八、预防措施

| 措施 | 优先级 | 说明 |
|------|--------|------|
| **定期 mysqldump 逻辑备份** | P0 | 每日至少一次，保留多份 |
| **Percona XtraBackup 物理备份** | P0 | 每周至少一次，恢复速度更快 |
| **binlog 保留策略** | P1 | 至少保留 7 天，支持 PITR |
| **主从复制** | P1 | 高可用场景必备 |
| **不要 kill -9 mysqld** | P1 | 使用 `mysqladmin shutdown` |
| **磁盘空间监控告警** | P1 | 使用率 > 80% 报警 |
| **UPS 不间断电源** | P2 | 防止异常掉电 |
| **RAID / 云盘多副本** | P2 | 底层存储冗余 |
| **sync_binlog=1** | P2 | 开启主从时确保刷盘 |
| **定期检查 MySQL 错误日志** | P2 | 及早发现 InnoDB warning |

---

## 九、故障处理时间线（本次案例）

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | undo_001 space_id 不匹配 | 确认 undo 表空间损坏 |
| 2 | 移走 undo_001/002 文件 | MySQL 进入 XA crash recovery |
| 3 | 业务表 space=33639 页损坏 | 用 od 扫描 .ibd 文件头定位 |
| 4 | 移走损坏的业务表 .ibd | MySQL 启动成功 |
| 5 | 发现 mysql.ibd 损坏 (space=0xFFFFFFFE) | 数据字典损坏，严重程度升级 |
| 6 | 移走 mysql.ibd，重建空 DD | MySQL 启动，但用户表全消失 |
| 7 | 用 ibd2sdi + recover_dd.py 提取表结构 | 从各 .ibd 的 SDI 重建 CREATE TABLE |
| 8 | 执行 CREATE TABLE + IMPORT TABLESPACE | 恢复表结构和数据 |
| 9 | mysqldump 全量导出 → 重建实例 | 得到干净的 MySQL 实例 |

---

## 十、附：命令速查

```bash
# ===== 查看 mysql.ibd 的 space_id =====
od -A n -t x1 -j 34 -N 4 /var/lib/mysql/mysql.ibd | tr -d ' \n'
# 应输出: fffffe 之类的值

# ===== 手动运行 ibd2sdi =====
/app/mysql/bin/ibd2sdi /var/lib/mysql/test/t1.ibd

# ===== recover_dd.py 脚本 =====
python3 recover_dd.py /var/lib/mysql \
  --ibd2sdi /app/mysql/bin/ibd2sdi \
  --output /tmp/recover_tables.sql

# ===== 单表 IMPORT TABLESPACE =====
mysql -uroot test -e "ALTER TABLE t1 DISCARD TABLESPACE;"
cp /var/lib/mysql.bak/test/t1.ibd /var/lib/mysql/test/
chown mysql:mysql /var/lib/mysql/test/t1.ibd
mysql -uroot test -e "ALTER TABLE t1 IMPORT TABLESPACE;"

# ===== 全量导出 =====
mysqldump -uroot -p --all-databases --single-transaction --routines --triggers --events > /tmp/backup.sql

# ===== 重新初始化数据目录 =====
mysqld --initialize-insecure --user=mysql --datadir=/var/lib/mysql

# ===== 验证表数据 =====
mysql -uroot -e "SELECT COUNT(*) FROM test.t1;"
```

---

*文档生成时间：2026-07-30*
*适用版本：MySQL 8.0.x（Oracle 官方版）*
*脚本：recover_dd.py（兼容 Python 3.6+）*
