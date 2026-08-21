# 每日学习笔记 - 2026-05-29

## 📄 PostgreSQL DROP COLUMN 后 attisdropped 仍占用 1600 列槽位.md

> 来源：微信文章 - 德哥 digoal  
> 整理时间：2026-05-29

---

## ⚠️ 核心问题

PG 中 `ALTER TABLE ... DROP COLUMN` 只是把 `pg_attribute` 行标记为 `attisdropped = true`，**不会删除目录记录**。即使 `VACUUM FULL` 也只重写数据文件把旧值变成 NULL，**不会移除 catalog 中的 dropped column 元数据**。

这导致经常加删列的表会提前耗尽单表最大 1600 列的上限。

---

## 📐 三个关键机制

### 1. DROP COLUMN 本身只做"软删除"

- 源码 `src/backend/catalog/heap.c:RemoveAttributeById()` 把 `attisdropped` 置为 `true`，`atttypid` 置为 `InvalidOid`
- 把列名改成内部名字（如 `........pg.dropped.<attnum>........`）
- **不删除 `pg_attribute` 记录，不更新 `pg_class.relnatts`**

### 2. ADD COLUMN 分配新 attnum，不复用 dropped 槽位

- `src/backend/commands/tablecmds.c:7456`：`newattnum = relform->relnatts + 1`
- 新增列后才更新 `relnatts`，超过 `MaxHeapAttributeNumber`(1600) 就报错
- dropped column 的 `attnum` 永远不会被后续 `ADD COLUMN` 复用

### 3. VACUUM FULL 只回收数据，不清理 catalog

- VACUUM FULL 重写数据文件，把 dropped column 的旧值重构成 NULL（回收旧值空间）
- 但 `pg_attribute` 中的 dropped column 记录**仍然存在**
- 新 tuple 的 `null bitmap` 仍按包含 dropped column 的 `natts` 计算位数

---

## 📊 null bitmap 也受影响

```c
// src/include/access/htup_details.h:581
BITMAPLEN(NATTS) = (NATTS + 7) / 8
```

每多一个 dropped column，`natts` 就多 1，`null bitmap` 就多消耗 `(dropped数 + 7)/8` 字节。

---

## 🔬 验证 SQL

```sql
CREATE TABLE t_drop_vf (a int, b text, c int);
INSERT INTO t_drop_vf VALUES (1, repeat('x', 1000), 3);

ALTER TABLE t_drop_vf DROP COLUMN b;
VACUUM FULL t_drop_vf;

-- 查看 pg_attribute，dropped column 仍在
SELECT attnum, attname, attisdropped, atttypid
FROM pg_attribute
WHERE attrelid = 't_drop_vf'::regclass
  AND attnum > 0
ORDER BY attnum;

-- relnatts 仍包含 dropped column
SELECT relnatts FROM pg_class WHERE oid = 't_drop_vf'::regclass;
```

---

## 🛠️ 真正解决问题的办法

当表接近 1600 列上限且有大量 dropped column 时，`VACUUM FULL` **不够**，需要逻辑重建：

```sql
-- 只导出有效列建新表
CREATE TABLE t_new AS
SELECT live_col1, live_col2, live_col3
FROM t_old;
```

生产环境还需补充：主键、唯一约束、外键、索引、默认值、生成列、权限、注释、触发器、分区、依赖对象、统计信息。

---

## 📝 记忆要点

- **DROP COLUMN ≠ 删除目录记录**，`attisdropped = true` 只是标记
- **VACUUM FULL ≠ 清理 dropped column**，只回收数据空间
- **1600 列上限是真实限制**，包括 dropped column
- 经常加删列的表要提前规划重建，不能靠 VACUUM FULL 解决
- **彻底清理需要逻辑重建表**（CREATE TABLE ... AS）

---

## 🔗 相关文件

- 源码：`src/backend/catalog/heap.c` / `src/backend/commands/tablecmds.c` / `src/backend/access/heap/heapam_handler.c`
- 文档：`doc/src/sgml/limits.sgml` / `doc/src/sgml/ref/alter_table.sgml`