"""
InnoDB IBD 文件解析模块

参考：
- MySQL 源码 storage/innobase/include/fil0fil.h
- MySQL 源码 storage/innobase/include/page0page.h
- https://dev.mysql.com/doc/internals/en/innodb-fil-header.html
- https://dev.mysql.com/doc/internals/en/innodb-page-overview.html
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


# InnoDB 常量
INNODB_PAGE_SIZE = 16 * 1024  # 默认 16KB
INNODB_COMPACT_ROW_FORMAT = "COMPACT"
INNODB_DYNAMIC_ROW_FORMAT = "DYNAMIC"
INNODB_COMPRESSED_ROW_FORMAT = "COMPRESSED"

# FIL Header 字段偏移（页面开头）
FIL_PAGE_OFFSET = 4            # 4-byte: page no within tablespace
FIL_PAGE_PREV = 8              # 4-byte: prev page
FIL_PAGE_NEXT = 12             # 4-byte: next page
FIL_PAGE_LSN = 16              # 8-byte: LSN
FIL_PAGE_TYPE = 24             # 2-byte: page type
FIL_PAGE_FILE_FLUSH_LSN = 26   # 8-byte
FIL_PAGE_ARCH_LOG_NO = 34      # 4-byte
FIL_PAGE_SPACE_ID = 34         # 4-byte (与上者重叠) — actually at offset 34 in MySQL 8

# 修正：FIL_PAGE_SPACE 在 offset 34，FIL_PAGE_ARCH_LOG_NO 在更早位置
# 实际结构（MySQL 8.0）:
#   0: FIL_PAGE_SPACE_OR_CHKSUM (4)  — page checksum
#   4: FIL_PAGE_OFFSET (4)           — page number
#   8: FIL_PAGE_PREV (4)             — prev page no
#  12: FIL_PAGE_NEXT (4)             — next page no
#  16: FIL_PAGE_LSN (8)              — LSN
#  24: FIL_PAGE_TYPE (2)             — page type
#  26: FIL_PAGE_FILE_FLUSH_LSN (8)
#  34: FIL_PAGE_SPACE_ID (4)         — tablespace id

# Page types
FIL_PAGE_TYPE_ALLOCATED = 0
FIL_PAGE_UNDO_LOG = 2
FIL_PAGE_INODE = 3
FIL_PAGE_IBUF_FREE_LIST = 4
FIL_PAGE_IBUF_BITMAP = 5
FIL_PAGE_SDI_BLOB = 17  # 补充 - 用于 zlib 压缩的 BLOB
FIL_PAGE_TYPE_SYS = 6
FIL_PAGE_TYPE_TRX_SYS = 7
FIL_PAGE_TYPE_FSP_HDR = 8
FIL_PAGE_TYPE_XDES = 9
FIL_PAGE_TYPE_BLOB = 10
FIL_PAGE_INDEX = 17855         # 0x45BF
FIL_PAGE_RTREE = 17854
FIL_PAGE_SDI = 17853           # MySQL 8.0 SDI page
FIL_PAGE_LOB_PAGE = 14         # COMPRESSED row format
FIL_PAGE_LOB_FIRST = 15
FIL_PAGE_ZLOB_FRAG = 17
FIL_PAGE_ZLOB_FRAG_ENTRY = 18
FIL_PAGE_TYPE_LEGACY_DBLWR = 19


# Page level (索引层) — 在 FIL_PAGE_FILE_FLUSH_LSN(8 字节) 之后，FIL_PAGE_SPACE_ID 之前
# 实际上 FIL_PAGE_FILE_FLUSH_LSN 是 8 字节(26-34), 接下来是 FIL_PAGE_ARCH_LOG_NO (4字节), 然后 FIL_PAGE_SPACE_ID
# level 实际上不在 FIL header 里，而在 PAGE header 起始 (offset 38 起)
# PAGE header: PAGE_N_DIR_SLOTS(2), PAGE_N_HEAP(2), PAGE_FREE(2), PAGE_GARBAGE(2), PAGE_LAST_INSERT(2), PAGE_DIRECTION(2), PAGE_N_DIRECTION(2), PAGE_N_RECS(2), PAGE_MAX_TRX_ID(8)
# 真正的 PAGE_LEVEL 在 offset = FIL_HEADER_SIZE + 36 = 38 + 36 = 74 (2 字节)
FIL_PAGE_LEVEL = 74

# Page directory 最后 8 字节
FIL_PAGE_END_LSN_OLD_CHKSUM = 8


@dataclass
class FilHeader:
    checksum: int
    page_no: int
    prev_page: int
    next_page: int
    lsn: int
    page_type: int
    flush_lsn: int
    space_id: int
    level: int = 0  # btree level (index pages only)

    @property
    def is_index(self) -> bool:
        return self.page_type == FIL_PAGE_INDEX

    @property
    def is_sdi(self) -> bool:
        return self.page_type == FIL_PAGE_SDI

    @property
    def page_type_name(self) -> str:
        names = {
            FIL_PAGE_TYPE_ALLOCATED: "ALLOCATED",
            FIL_PAGE_UNDO_LOG: "UNDO_LOG",
            FIL_PAGE_INODE: "INODE",
            FIL_PAGE_IBUF_FREE_LIST: "IBUF_FREE_LIST",
            FIL_PAGE_IBUF_BITMAP: "IBUF_BITMAP",
            FIL_PAGE_TYPE_SYS: "SYS",
            FIL_PAGE_TYPE_TRX_SYS: "TRX_SYS",
            FIL_PAGE_TYPE_FSP_HDR: "FSP_HDR",
            FIL_PAGE_TYPE_XDES: "XDES",
            FIL_PAGE_TYPE_BLOB: "BLOB",
            FIL_PAGE_INDEX: "INDEX",
            FIL_PAGE_RTREE: "RTREE",
            FIL_PAGE_SDI: "SDI",
            FIL_PAGE_LOB_PAGE: "LOB_PAGE",
            FIL_PAGE_LOB_FIRST: "LOB_FIRST",
            FIL_PAGE_ZLOB_FRAG: "ZLOB_FRAG",
            FIL_PAGE_ZLOB_FRAG_ENTRY: "ZLOB_FRAG_ENTRY",
        }
        return names.get(self.page_type, f"UNKNOWN(0x{self.page_type:04x})")


@dataclass
class PageRecord:
    """页面中的一条用户记录"""
    offset: int
    extra_bytes: int
    heap_no: int
    n_owned: int
    info_bits: int
    primary_key: bytes  # 原始字节（聚簇索引的 key）
    trx_id: int
    roll_ptr: int
    raw: bytes = b""


@dataclass
class IbdSummary:
    file_size: int
    page_size: int
    page_count: int
    space_id: int
    page_types: dict[str, int] = field(default_factory=dict)
    pages: list[FilHeader] = field(default_factory=list)

    @property
    def has_sdi(self) -> bool:
        return self.page_types.get("SDI", 0) > 0

    @property
    def index_page_count(self) -> int:
        return self.page_types.get("INDEX", 0)


def parse_fil_header(page: bytes, page_size: int = INNODB_PAGE_SIZE) -> FilHeader:
    """解析单个 InnoDB page 的 FIL Header（38 字节）"""
    if len(page) < 38:
        raise ValueError(f"page too small: {len(page)} bytes")

    checksum = struct.unpack_from("<I", page, 0)[0]
    page_no = struct.unpack_from("<I", page, 4)[0]
    prev_page = struct.unpack_from("<I", page, 8)[0]
    next_page = struct.unpack_from("<I", page, 12)[0]
    lsn = struct.unpack_from("<Q", page, 16)[0]
    page_type = struct.unpack_from("<H", page, 24)[0]
    flush_lsn = struct.unpack_from("<Q", page, 26)[0]
    space_id = struct.unpack_from("<I", page, 34)[0]
    level = 0
    if page_type == FIL_PAGE_INDEX:
        level = struct.unpack_from("<H", page, FIL_PAGE_LEVEL)[0]

    return FilHeader(
        checksum=checksum,
        page_no=page_no,
        prev_page=prev_page,
        next_page=next_page,
        lsn=lsn,
        page_type=page_type,
        flush_lsn=flush_lsn,
        space_id=space_id,
        level=level,
    )


def list_pages(ibd_path: str | Path, page_size: int = INNODB_PAGE_SIZE) -> IbdSummary:
    """扫描整个 .ibd 文件，返回所有页面摘要"""
    ibd_path = Path(ibd_path)
    file_size = ibd_path.stat().st_size
    page_count = file_size // page_size

    summary = IbdSummary(
        file_size=file_size,
        page_size=page_size,
        page_count=page_count,
        space_id=0,
        page_types={},
        pages=[],
    )

    with open(ibd_path, "rb") as f:
        for i in range(page_count):
            f.seek(i * page_size)
            page = f.read(page_size)
            if len(page) < page_size:
                break
            try:
                hdr = parse_fil_header(page, page_size)
            except Exception:
                continue

            if i == 0:
                summary.space_id = hdr.space_id

            type_name = hdr.page_type_name
            summary.page_types[type_name] = summary.page_types.get(type_name, 0) + 1
            summary.pages.append(hdr)

    return summary


def parse_page_directory(page: bytes, page_size: int = INNODB_PAGE_SIZE) -> list[int]:
    """解析 page directory，返回所有 slot 指向的相对偏移列表

    Page directory 在页面末尾，倒着读直到遇到 0xFFFF 哨兵。
    实际：最后 2 字节是 sentinel（0xFFFF），前面每 2 字节是一个 slot 指针。
    """
    slots: list[int] = []
    # 从末尾读
    pos = page_size - 2
    while pos >= 38:
        slot = struct.unpack_from("<H", page, pos)[0]
        if slot == 0xFFFF:
            break
        slots.append(slot)
        pos -= 2
    slots.reverse()
    return slots


def list_records(page: bytes, page_size: int = INNODB_PAGE_SIZE) -> list[PageRecord]:
    """列出 INDEX 页里的所有用户记录（简化版：只读 infimum+supremum 之间的数据）

    COMPACT 行格式 (从 infimum 起算)：
    - 2 字节变长字段长度列表
    - 1 字节 NULL bitmap
    - 5 字节 header (heap_no:13bit + n_owned:4bit + info_bits:3bit + status:3bit)  -- 非主键
       主键索引的 5 字节 header 不同: heap_no(13) + record_type(3) + n_owned(4) + ... (3字节delete_mark+min_rec_mark+...)
    - 变长字段长度
    - 非空列数据
    """
    records = []
    # infimum 在 offset 99 (99 + 5 字节 rec header = supremum)
    infimum_offset = 99
    if page_size != 16384:
        infimum_offset = page_size - 64 * 2  # 简化估算

    # 简化：直接从 infimum 开始顺序遍历
    pos = infimum_offset
    seen_heap_nos: set[int] = set()
    record_count = 0

    while pos < page_size - 6:
        # 读 5 字节 record header (主键索引)
        if pos + 5 > page_size:
            break

        # 解析 5 字节 header (从右往左)
        # Byte 4 (高字节): info_bits(3) + n_owned(4) + heap_no 高 1 位
        # Byte 3: heap_no 中 8 位
        # Byte 2: heap_no 低 4 位 + record_type(3) + delete_mark(1)
        # Byte 1, 0: next_record 偏移（有符号 16-bit）
        b4 = page[pos]
        b3 = page[pos + 1]
        b2 = page[pos + 2]
        next_record = struct.unpack_from("<h", page, pos + 3)[0]

        info_bits = (b4 >> 5) & 0x7
        n_owned = (b4 >> 1) & 0xF
        heap_no = ((b4 & 0x1) << 11) | (b3 << 3) | (b2 >> 5)
        record_type = (b2 >> 1) & 0x7  # 0=ordinary, 1=node_ptr, 2=infimum, 3=supremum

        if record_type == 2:  # infimum
            pos += 5 + (next_record if next_record else 8)
            continue
        if record_type == 3:  # supremum
            break

        # 跳过 node_ptr（索引非叶节点）
        if record_type == 1:
            pos = pos + 5 + next_record if next_record else pos + 5
            continue

        # 普通用户记录：跳过变长字段长度（这里只是占位）
        # 真正的实现需要 PAGE_HEAP_NO_USER_TRX_ID / ROLL_PTR 等偏移
        # 这里只读 header 和堆号
        records.append(PageRecord(
            offset=pos,
            extra_bytes=5,
            heap_no=heap_no,
            n_owned=n_owned,
            info_bits=info_bits,
            primary_key=b"",
            trx_id=0,
            roll_ptr=0,
            raw=page[pos:pos+5],
        ))

        record_count += 1
        if next_record == 0:
            break
        pos += next_record

        if record_count > 1000:  # 防止无限循环
            break

    return records


def extract_pages(
    ibd_path: str | Path,
    output_dir: str | Path,
    page_types: set[int] | None = None,
    page_indices: set[int] | None = None,
    page_size: int = INNODB_PAGE_SIZE,
) -> int:
    """从 .ibd 文件抽取符合条件的页面到 .page 文件"""
    ibd_path = Path(ibd_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted = 0
    with open(ibd_path, "rb") as f:
        page_count = ibd_path.stat().st_size // page_size
        for i in range(page_count):
            f.seek(i * page_size)
            page = f.read(page_size)
            if len(page) < page_size:
                break

            try:
                hdr = parse_fil_header(page, page_size)
            except Exception:
                continue

            match = False
            if page_indices is not None and i in page_indices:
                match = True
            elif page_types is not None and hdr.page_type in page_types:
                match = True

            if match:
                out_path = output_dir / f"page_{hdr.page_no:08d}_type{hdr.page_type:04x}.page"
                out_path.write_bytes(page)
                extracted += 1

    return extracted


def ibd_summary_report(ibd_path: str | Path, page_size: int = INNODB_PAGE_SIZE) -> str:
    """生成 .ibd 文件的摘要报告（人类可读）"""
    summary = list_pages(ibd_path, page_size)
    lines = []
    lines.append(f"📦 IBD 文件摘要")
    lines.append(f"  路径: {ibd_path}")
    lines.append(f"  大小: {summary.file_size:,} bytes ({summary.file_size / (1024*1024):.2f} MB)")
    lines.append(f"  页大小: {summary.page_size:,} bytes")
    lines.append(f"  页数量: {summary.page_count:,}")
    lines.append(f"  空间 ID: {summary.space_id}")
    lines.append("")
    lines.append(f"📊 页面类型分布:")
    for tname, cnt in sorted(summary.page_types.items(), key=lambda x: -x[1]):
        lines.append(f"  - {tname}: {cnt}")
    lines.append("")
    # 列出前 10 个 index page 的 btree level
    index_pages = [p for p in summary.pages if p.is_index]
    if index_pages:
        levels: dict[int, int] = {}
        for p in index_pages:
            levels[p.level] = levels.get(p.level, 0) + 1
        lines.append(f"🌲 INDEX 页 B+tree 层分布:")
        for lvl, cnt in sorted(levels.items()):
            lines.append(f"  - Level {lvl}: {cnt} pages")
    return "\n".join(lines)
