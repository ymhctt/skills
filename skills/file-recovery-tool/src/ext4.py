"""
ext4 文件系统解析模块

参考：
- https://ext4.wiki.kernel.org/index.php/Ext4_Disk_Layout
- include/uapi/linux/ext4_fs.h
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path


# ext4 常量
EXT4_MAGIC = 0xEF53
EXT4_SUPERBLOCK_OFFSET = 1024
EXT4_SUPERBLOCK_SIZE = 1024

# Inode 标志
EXT4_INODE_FLAG_EXTENTS = 0x80000  # i_flags bit: 文件使用 extent 映射
EXT4_INODE_FLAG_INLINE_DATA = 0x10000000  # 内联数据（小文件）

# 文件类型（i_mode 高位）
EXT4_FT_REG_FILE = 0o100000
EXT4_FT_DIR = 0o040000
EXT4_FT_SYMLINK = 0o120000


@dataclass
class Ext4Superblock:
    s_inodes_count: int
    s_blocks_count: int
    s_log_block_size: int
    s_blocks_per_group: int
    s_inodes_per_group: int
    s_magic: int
    s_inode_size: int
    s_feature_incompat: int
    s_feature_compat: int
    s_feature_ro_compat: int
    block_size: int = 0  # 派生

    @property
    def is_ext4(self) -> bool:
        return self.s_magic == EXT4_MAGIC

    @property
    def is_extents(self) -> bool:
        # EXT4_FEATURE_INCOMPAT_EXTENTS = 0x0040
        return bool(self.s_feature_incompat & 0x0040)


@dataclass
class Ext4Inode:
    i_mode: int
    i_size: int
    i_links_count: int
    i_blocks: int
    i_flags: int
    i_block: bytes  # 60 bytes (ext4: 15 * 4 byte extents or 12 direct + 3 indirect)
    i_ctime: int = 0
    i_dtime: int = 0
    inode_num: int = 0

    @property
    def is_extents(self) -> bool:
        return bool(self.i_flags & EXT4_INODE_FLAG_EXTENTS)

    @property
    def file_type(self) -> int:
        return self.i_mode & 0o170000

    @property
    def is_deleted(self) -> bool:
        # 已删除特征：links_count=0 且 dtime>0
        return self.i_links_count == 0 and self.i_dtime > 0

    @property
    def is_file(self) -> bool:
        return (self.i_mode & 0o170000) == EXT4_FT_REG_FILE

    @property
    def is_dir(self) -> bool:
        return (self.i_mode & 0o170000) == EXT4_FT_DIR


@dataclass
class Ext4GroupDesc:
    bg_block_bitmap: int
    bg_inode_bitmap: int
    bg_inode_table: int
    bg_free_blocks_count: int
    bg_free_inodes_count: int
    bg_used_dirs_count: int
    bg_flags: int


@dataclass
class DeletedFile:
    inode_num: int
    size: int
    mode: int
    is_extents: bool
    deletion_time: int
    raw_block: bytes  # 原始 i_block 数据（用于恢复）


def parse_superblock(dev_path: str | Path) -> Ext4Superblock:
    """读取并解析 ext4 超级块"""
    with open(dev_path, "rb") as f:
        f.seek(EXT4_SUPERBLOCK_OFFSET)
        data = f.read(EXT4_SUPERBLOCK_SIZE)

    # struct ext4_super_block {
    #   __le32 s_inodes_count;        // 0
    #   __le32 s_blocks_count;        // 4
    #   __le32 s_r_blocks_count;      // 8
    #   __le32 s_free_blocks_count;   // 12
    #   __le32 s_free_inodes_count;   // 16
    #   __le32 s_first_data_block;    // 20
    #   __le32 s_log_block_size;      // 24
    #   __le32 s_log_frag_size;       // 28
    #   ...
    #   __le32 s_blocks_per_group;    // 32
    #   __le32 s_frags_per_group;     // 36
    #   __le32 s_inodes_per_group;    // 40
    #   ...
    #   __le16 s_magic = 56;          // 56
    #   ...
    #   __le16 s_inode_size = 88;     // 88
    #   ...
    # }
    sb = Ext4Superblock(
        s_inodes_count=struct.unpack_from("<I", data, 0)[0],
        s_blocks_count=struct.unpack_from("<I", data, 4)[0],
        s_log_block_size=struct.unpack_from("<I", data, 24)[0],
        s_blocks_per_group=struct.unpack_from("<I", data, 32)[0],
        s_inodes_per_group=struct.unpack_from("<I", data, 40)[0],
        s_magic=struct.unpack_from("<H", data, 56)[0],
        s_inode_size=struct.unpack_from("<H", data, 88)[0],
        s_feature_incompat=struct.unpack_from("<I", data, 96)[0],
        s_feature_compat=struct.unpack_from("<I", data, 92)[0],
        s_feature_ro_compat=struct.unpack_from("<I", data, 100)[0],
    )
    sb.block_size = 1024 << sb.s_log_block_size
    return sb


def parse_block_group_desc(data: bytes) -> Ext4GroupDesc:
    """解析 32 字节块组描述符（适用于 block_size=1024）
    64 字节版本用于 block_size > 1024
    """
    if len(data) == 32:
        return Ext4GroupDesc(
            bg_block_bitmap=struct.unpack_from("<I", data, 0)[0],
            bg_inode_bitmap=struct.unpack_from("<I", data, 4)[0],
            bg_inode_table=struct.unpack_from("<I", data, 8)[0],
            bg_free_blocks_count=struct.unpack_from("<H", data, 12)[0],
            bg_free_inodes_count=struct.unpack_from("<H", data, 14)[0],
            bg_used_dirs_count=struct.unpack_from("<H", data, 16)[0],
            bg_flags=struct.unpack_from("<H", data, 18)[0],
        )
    elif len(data) == 64:
        return Ext4GroupDesc(
            bg_block_bitmap=struct.unpack_from("<I", data, 0)[0],
            bg_inode_bitmap=struct.unpack_from("<I", data, 4)[0],
            bg_inode_table=struct.unpack_from("<I", data, 8)[0],
            bg_free_blocks_count=struct.unpack_from("<H", data, 12)[0],
            bg_free_inodes_count=struct.unpack_from("<H", data, 14)[0],
            bg_used_dirs_count=struct.unpack_from("<H", data, 16)[0],
            bg_flags=struct.unpack_from("<H", data, 18)[0],
        )
    else:
        raise ValueError(f"unexpected bgdt size: {len(data)}")


def scan_inode_table(
    dev_path: str | Path,
    sb: Ext4Superblock,
    group_idx: int,
    bgdt_offset_bytes: int,
) -> list[DeletedFile]:
    """扫描指定块组的 inode 表，查找已删除文件"""
    deleted = []
    with open(dev_path, "rb") as f:
        f.seek(bgdt_offset_bytes + group_idx * 64)  # 64 字节/项
        bg_data = f.read(64)
        bg = parse_block_group_desc(bg_data)

        # 读 inode 表
        inode_table_offset = bg.bg_inode_table * sb.block_size
        f.seek(inode_table_offset)
        inode_table = f.read(sb.s_inodes_per_group * sb.s_inode_size)

        for i in range(sb.s_inodes_per_group):
            inode_offset = i * sb.s_inode_size
            raw = inode_table[inode_offset:inode_offset + sb.s_inode_size]
            if len(raw) < 156:
                continue

            # struct ext4_inode {
            #   __le16 i_mode;        // 0
            #   __le16 i_uid;         // 2
            #   __le32 i_size;        // 4
            #   __le32 i_atime;       // 8
            #   __le32 i_ctime;       // 12
            #   __le32 i_mtime;       // 16
            #   __le32 i_dtime;       // 20 (删除时间，0=未删)
            #   __le16 i_gid;         // 24
            #   __le16 i_links_count; // 26
            #   __le32 i_blocks;      // 28 (512字节块数)
            #   __le32 i_flags;       // 32
            #   ...
            #   __le32 i_block[60];   // 40
            # }
            i_mode = struct.unpack_from("<H", raw, 0)[0]
            i_size = struct.unpack_from("<I", raw, 4)[0]
            i_links_count = struct.unpack_from("<H", raw, 26)[0]
            i_flags = struct.unpack_from("<I", raw, 32)[0]
            i_dtime = struct.unpack_from("<I", raw, 20)[0]
            i_block_data = raw[40:100]

            # 跳过无效 inode
            if i_mode == 0:
                continue

            # 已删除特征：links_count=0 且 dtime>0
            if i_links_count == 0 and i_dtime > 0:
                # 只关心普通文件
                if (i_mode & 0o170000) != EXT4_FT_REG_FILE:
                    continue
                i_blocks_count = struct.unpack_from("<I", raw, 28)[0]
                deleted.append(DeletedFile(
                    inode_num=group_idx * sb.s_inodes_per_group + i + 1,
                    size=i_size,
                    mode=i_mode,
                    is_extents=bool(i_flags & EXT4_INODE_FLAG_EXTENTS),
                    deletion_time=i_dtime,
                    raw_block=i_block_data,
                ))

    return deleted


def scan_ext4(
    dev_path: str | Path,
    max_groups: int | None = None,
) -> tuple[Ext4Superblock, list[DeletedFile]]:
    """扫描整个 ext4 镜像，返回超级块 + 所有已删除文件列表"""
    sb = parse_superblock(dev_path)
    if not sb.is_ext4:
        raise ValueError(f"not an ext4 filesystem (magic=0x{sb.s_magic:04x})")

    # 计算块组数
    blocks_per_group = sb.s_blocks_per_group
    block_groups_count = (sb.s_blocks_count + blocks_per_group - 1) // blocks_per_group
    if max_groups is not None:
        block_groups_count = min(block_groups_count, max_groups)

    # bgdt 位置：块 2（如果 block_size=1024）或 块 1（block_size>1024）
    if sb.block_size == 1024:
        bgdt_offset = 2 * sb.block_size
    else:
        bgdt_offset = 1 * sb.block_size

    all_deleted = []
    for g in range(block_groups_count):
        try:
            deleted = scan_inode_table(dev_path, sb, g, bgdt_offset)
            all_deleted.extend(deleted)
        except Exception as e:
            # 单个组失败不中断
            continue
    return sb, all_deleted


@dataclass
class GhostInode:
    """幽灵 inode：i_block 里残留 extent header（可能是未完全清除的已删文件）"""
    inode_num: int
    eh_magic: int
    eh_entries: int
    eh_depth: int
    raw: bytes
    raw_size: int  # i_size 原始值（可能为0）


def scan_ghost_inodes(dev_path: str | Path, max_groups: int | None = None) -> list[GhostInode]:
    """扫描 inode 表中所有 i_block 残留 extent header 的 inode。

    场景：rm 后 extent header 通常会被 jbd2 journal 清为 0，
    但在一些场景（如未 sync、nojournal、崩溃后）会残留。
    """
    sb = parse_superblock(dev_path)
    if not sb.is_ext4:
        return []
    if not sb.is_extents:
        return []  # 仅 ext4 extents 格式

    blocks_per_group = sb.s_blocks_per_group
    block_groups_count = (sb.s_blocks_count + blocks_per_group - 1) // blocks_per_group
    if max_groups is not None:
        block_groups_count = min(block_groups_count, max_groups)

    if sb.block_size == 1024:
        bgdt_offset = 2 * sb.block_size
    else:
        bgdt_offset = 1 * sb.block_size

    ghosts: list[GhostInode] = []
    with open(dev_path, "rb") as f:
        for g in range(block_groups_count):
            try:
                f.seek(bgdt_offset + g * 64)
                bg = parse_block_group_desc(f.read(64))
                f.seek(bg.bg_inode_table * sb.block_size)
                table = f.read(sb.s_inodes_per_group * sb.s_inode_size)
            except Exception:
                continue

            for i in range(sb.s_inodes_per_group):
                raw = table[i * sb.s_inode_size:(i + 1) * sb.s_inode_size]
                if len(raw) < 100:
                    continue
                iblk = raw[40:100]
                eh_magic = struct.unpack_from("<H", iblk, 0)[0]
                eh_entries = struct.unpack_from("<H", iblk, 2)[0]
                eh_depth = struct.unpack_from("<H", iblk, 4)[0]

                if eh_magic == 0xF30A and (eh_entries > 0 or eh_depth > 0):
                    ino_num = g * sb.s_inodes_per_group + i + 1
                    i_size = struct.unpack_from("<I", raw, 4)[0]
                    ghosts.append(GhostInode(
                        inode_num=ino_num,
                        eh_magic=eh_magic,
                        eh_entries=eh_entries,
                        eh_depth=eh_depth,
                        raw=iblk,
                        raw_size=i_size,
                    ))

    return ghosts


def restore_ghost_inode(dev_path: str | Path, ghost: GhostInode, output_path: str | Path,
                         block_size_override: int | None = None) -> int:
    """从幽灵 inode 恢复文件数据，返回写入字节数"""
    sb = parse_superblock(dev_path)
    bs = block_size_override or sb.block_size

    if ghost.eh_depth == 0:
        # 叶子节点：直接读 extent 项
        offset = 12
        out = bytearray()
        for _ in range(ghost.eh_entries):
            if offset + 12 > len(ghost.raw):
                break
            ee_len = struct.unpack_from("<H", ghost.raw, offset + 4)[0]
            ee_hi = struct.unpack_from("<H", ghost.raw, offset + 6)[0]
            ee_lo = struct.unpack_from("<I", ghost.raw, offset + 8)[0]
            physical = (ee_hi << 32) | ee_lo

            with open(dev_path, "rb") as f:
                for b in range(ee_len):
                    f.seek(physical * bs + b * bs)
                    out.extend(f.read(bs))
            offset += 12
        written = len(out)
    elif ghost.eh_depth == 1:
        # 索引节点：递归读叶子
        offset = 12
        out = bytearray()
        with open(dev_path, "rb") as f:
            for _ in range(ghost.eh_entries):
                if offset + 12 > len(ghost.raw):
                    break
                ei_block = struct.unpack_from("<I", ghost.raw, offset)[0]
                ei_leaf_lo = struct.unpack_from("<I", ghost.raw, offset + 4)[0]
                ei_leaf_hi = struct.unpack_from("<H", ghost.raw, offset + 8)[0]
                leaf_phys = (ei_leaf_hi << 32) | ei_leaf_lo

                # 读叶子节点块
                f.seek(leaf_phys * bs)
                leaf_data = f.read(bs)
                leaf_magic = struct.unpack_from("<H", leaf_data, 0)[0]
                if leaf_magic != 0xF30A:
                    break
                leaf_entries = struct.unpack_from("<H", leaf_data, 2)[0]

                lo = 12
                for _ in range(leaf_entries):
                    if lo + 12 > bs:
                        break
                    ee_len = struct.unpack_from("<H", leaf_data, lo + 4)[0]
                    ee_hi = struct.unpack_from("<H", leaf_data, lo + 6)[0]
                    ee_lo = struct.unpack_from("<I", leaf_data, lo + 8)[0]
                    physical = (ee_hi << 32) | ee_lo

                    f.seek(physical * bs)
                    out.extend(f.read(ee_len * bs))
                    lo += 12
            offset += 12
        written = len(out)
    else:
        return 0

    with open(output_path, "wb") as f:
        f.write(out)
    return written


def get_orphan_inode_start(dev_path: str | Path) -> int:
    """读 s_last_orphan 超级块字段（最近 unlink 的 inode 起点）"""
    sb = parse_superblock(dev_path)
    with open(dev_path, "rb") as f:
        f.seek(EXT4_SUPERBLOCK_OFFSET + 84)
        return struct.unpack_from("<I", f.read(4), 0)[0]


def walk_orphan_list(dev_path: str | Path, start_ino: int, max_count: int = 100) -> list[int]:
    """沿 orphan inode 链追踪最近 unlink 的 inode 号列表。
    链中每个 inode 的 i_dtime 被复用为下一个 inode 号（链尾=0）。
    """
    sb = parse_superblock(dev_path)
    if start_ino == 0:
        return []

    # 找 inode 表位置
    with open(dev_path, "rb") as f:
        f.seek(1 * sb.block_size if sb.block_size != 1024 else 2 * sb.block_size)
        bg = parse_block_group_desc(f.read(64))

        orphans = []
        cur = start_ino
        visited = set()
        while cur and cur not in visited and len(orphans) < max_count:
            visited.add(cur)
            orphans.append(cur)
            # 读 inode
            ino_off = bg.bg_inode_table * sb.block_size + (cur - 1) * sb.s_inode_size
            f.seek(ino_off)
            raw = f.read(sb.s_inode_size)
            if len(raw) < sb.s_inode_size:
                break
            # 沿链：i_dtime 是下一个 inode 号（4 字节小端）
            next_ino = struct.unpack_from("<I", raw, 20)[0]
            if next_ino == cur or next_ino > sb.s_inodes_count:
                break
            cur = next_ino
    return orphans
