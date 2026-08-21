"""
XFS 文件系统解析模块 — 基于 Linux 内核 xfs_dsb_format.h 权威布局

字段偏移（v5 superblock，大端字节序）：
  0    sb_magicnum (4)
  4    sb_blocksize (4)
  8    sb_dblocks (8)
 16    sb_rblocks (8)
 24    sb_rextents (8)
 32    sb_uuid (16)
 48    sb_logstart (8)
 56    sb_rootino (8)
 64    sb_rbmino (8)
 72    sb_rsumino (8)
 80    sb_rextsize (4)
 84    sb_agblocks (4)
 88    sb_agcount (4)        ← 关键字段
 92    sb_rbmblocks (4)
 96    sb_logblocks (4)
100    sb_versionnum (2)
102    sb_sectsize (2)
104    sb_inodesize (2)
106    sb_inopblock (2)
108    sb_fname (12)
120-127  log/inprogress/imax_pct 等
128    sb_icount (8)
136    sb_ifree (8)
144    sb_fdblocks (8)
152    sb_frextents (8)
160    sb_uquotino (8)
168    sb_gquotino (8)
176    sb_qflags (2)
178    sb_flags (1)
179    sb_shared_vn (1)
180    sb_inoalignmt (4)
184    sb_unit (4)
188    sb_width (4)
192    sb_dirblklog (1)
193    sb_logsectlog (1)
194    sb_logsectsize (2)
196    sb_logsunit (4)
200    sb_features2 (4)
204    sb_bad_features2 (4)
# v5 only
208    sb_features_compat (4)
212    sb_features_ro_compat (4)
216    sb_features_incompat (4)
220    sb_features_log_incompat (4)
224    sb_crc (4)
228    sb_spino_align (4)
232    sb_pquotino (8)
240    sb_lsn (8)
248    sb_meta_uuid (16)
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path


XFS_SUPER_MAGIC = b"XFSB"  # 0x58465342
XFS_AGF_MAGIC = 0x41474600  # 'AGF' (大端: 0x58414746)
XFS_AGI_MAGIC = 0x41474900  # 'AGI' (大端: 0x58414749)
XFS_DINODE_MAGIC = 0x494E0000  # 'IN' (大端: 0x0000494E)

# 修正 magic 为纯 ASCII 大端值
XFS_AGF_MAGIC_BE = 0x58414746
XFS_AGI_MAGIC_BE = 0x58414749
XFS_DINODE_MAGIC_BE = 0x0000494E


@dataclass
class XfsSuperblock:
    sb_magicnum: bytes
    sb_blocksize: int
    sb_dblocks: int
    sb_rblocks: int
    sb_rextents: int
    sb_uuid: bytes
    sb_logstart: int
    sb_rootino: int
    sb_rbmino: int
    sb_rsumino: int
    sb_rextsize: int
    sb_agblocks: int
    sb_agcount: int
    sb_rbmblocks: int
    sb_logblocks: int
    sb_versionnum: int
    sb_sectsize: int
    sb_inodesize: int
    sb_inopblock: int
    sb_fname: str
    sb_icount: int
    sb_ifree: int
    sb_fdblocks: int
    sb_frextents: int
    sb_uquotino: int
    sb_gquotino: int
    sb_features2: int
    sb_features_compat: int
    sb_features_ro_compat: int
    sb_features_incompat: int
    sb_meta_uuid: bytes

    @property
    def is_xfs(self) -> bool:
        return self.sb_magicnum == XFS_SUPER_MAGIC

    @property
    def is_v5(self) -> bool:
        return (self.sb_versionnum & 0x000F) == 5

    @property
    def has_crc(self) -> bool:
        # XFS_SB_VERSION2_CRCBIT = 0x100
        return bool(self.sb_features2 & 0x100)


@dataclass
class XfsAgi:
    agi_magicnum: int
    agi_versionnum: int
    agi_length: int
    agi_count: int            # inode 总数 (inodes in this AG)
    agi_root: int             # inode btree 根块号 (AG 相对)
    agi_level: int
    agi_freecount: int
    agi_newino: int
    agi_dirino: int


@dataclass
class XfsInode:
    di_magic: int
    di_mode: int
    di_nlink: int
    di_uid: int
    di_gid: int
    di_size: int
    di_format: int
    inode_num: int = 0


@dataclass
class DeletedXfsFile:
    inode_num: int
    size: int
    mode: int
    format: int
    nlink: int
    di_magic: int


def parse_superblock(dev_path: str | Path) -> XfsSuperblock:
    """读取 XFS v5 超级块（offset=0，264 字节）"""
    with open(dev_path, "rb") as f:
        # v5 sb 是 264 字节，但要读到 metadata UUID 部分要 264+16=280
        data = f.read(280)

    return XfsSuperblock(
        sb_magicnum=data[0:4],
        sb_blocksize=struct.unpack_from(">I", data, 4)[0],
        sb_dblocks=struct.unpack_from(">Q", data, 8)[0],
        sb_rblocks=struct.unpack_from(">Q", data, 16)[0],
        sb_rextents=struct.unpack_from(">Q", data, 24)[0],
        sb_uuid=data[32:48],
        sb_logstart=struct.unpack_from(">Q", data, 48)[0],
        sb_rootino=struct.unpack_from(">Q", data, 56)[0],
        sb_rbmino=struct.unpack_from(">Q", data, 64)[0],
        sb_rsumino=struct.unpack_from(">Q", data, 72)[0],
        sb_rextsize=struct.unpack_from(">I", data, 80)[0],
        sb_agblocks=struct.unpack_from(">I", data, 84)[0],
        sb_agcount=struct.unpack_from(">I", data, 88)[0],
        sb_rbmblocks=struct.unpack_from(">I", data, 92)[0],
        sb_logblocks=struct.unpack_from(">I", data, 96)[0],
        sb_versionnum=struct.unpack_from(">H", data, 100)[0],
        sb_sectsize=struct.unpack_from(">H", data, 102)[0],
        sb_inodesize=struct.unpack_from(">H", data, 104)[0],
        sb_inopblock=struct.unpack_from(">H", data, 106)[0],
        sb_fname=data[108:120].rstrip(b"\x00").decode("ascii", errors="ignore"),
        sb_icount=struct.unpack_from(">Q", data, 128)[0],
        sb_ifree=struct.unpack_from(">Q", data, 136)[0],
        sb_fdblocks=struct.unpack_from(">Q", data, 144)[0],
        sb_frextents=struct.unpack_from(">Q", data, 152)[0],
        sb_uquotino=struct.unpack_from(">Q", data, 160)[0],
        sb_gquotino=struct.unpack_from(">Q", data, 168)[0],
        sb_features2=struct.unpack_from(">I", data, 200)[0],
        sb_features_compat=struct.unpack_from(">I", data, 208)[0],
        sb_features_ro_compat=struct.unpack_from(">I", data, 212)[0],
        sb_features_incompat=struct.unpack_from(">I", data, 216)[0],
        sb_meta_uuid=data[248:264],
    )


def parse_agi(data: bytes) -> XfsAgi:
    """解析 AGI（AG Inode B+tree 头）"""
    return XfsAgi(
        agi_magicnum=struct.unpack_from(">I", data, 0)[0],
        agi_versionnum=struct.unpack_from(">I", data, 4)[0],
        agi_length=struct.unpack_from(">I", data, 8)[0],
        agi_count=struct.unpack_from(">I", data, 12)[0],
        agi_root=struct.unpack_from(">Q", data, 16)[0],
        agi_level=struct.unpack_from(">Q", data, 24)[0],
        agi_freecount=struct.unpack_from(">Q", data, 32)[0],
        agi_newino=struct.unpack_from(">Q", data, 40)[0],
        agi_dirino=struct.unpack_from(">Q", data, 48)[0],
    )


def scan_xfs(
    dev_path: str | Path,
    max_ags: int | None = None,
    inode_scan_limit: int = 10000,
    scan_recent_only: bool = False,
) -> tuple[XfsSuperblock, list[DeletedXfsFile]]:
    """扫描 XFS 镜像中已删除 inode。

    策略：
    1. 解析超级块获取 AG 数
    2. 对每个 AG，定位 inode 区（每个 AG 有 sb_inopblock 个 inode/block）
    3. 线性扫 inode (1..agi_count)，找 nlink=0 的文件
    """
    sb = parse_superblock(dev_path)
    if not sb.is_xfs:
        raise ValueError(f"not an XFS filesystem (magic={sb.sb_magicnum})")

    ag_count = sb.sb_agcount
    if max_ags is not None:
        ag_count = min(ag_count, max_ags)

    if sb.sb_agblocks == 0 or sb.sb_blocksize == 0:
        return sb, []

    deleted: list[DeletedXfsFile] = []

    with open(dev_path, "rb") as f:
        for ag in range(ag_count):
            ag_start = ag * sb.sb_agblocks * sb.sb_blocksize

            # AGI 在 v5 superblock 块内的偏移 1024
            # 但 XFS v5 superblock 是第一个块 (块 0)
            f.seek(ag_start + 1024)  # AGI offset within superblock block
            probe = f.read(sb.sb_blocksize)
            agi = None
            agi_block = 0
            if len(probe) >= 56:
                m = struct.unpack_from(">I", probe, 0)[0]
                if m == XFS_AGI_MAGIC_BE:
                    try:
                        agi = parse_agi(probe)
                    except Exception:
                        agi = None

            if agi is None:
                # 试试从块 1 起扫
                for probe_blk in range(1, 8):
                    f.seek(ag_start + probe_blk * sb.sb_blocksize)
                    p2 = f.read(sb.sb_blocksize)
                    if len(p2) < 56: continue
                    m = struct.unpack_from(">I", p2, 0)[0]
                    if m == XFS_AGI_MAGIC_BE:
                        try:
                            agi = parse_agi(p2)
                            agi_block = probe_blk
                            break
                        except Exception:
                            continue

            if agi is None:
                continue

            # inode 区起点 = AGI 块号 + 1 (XFS 约定)
            inode_start_block = agi_block + 1
            # inode 区起始字节位置（AG 内）
            inode_start_byte = inode_start_block * sb.sb_blocksize

            # 扫 inode：每个 inode 大小 sb_inodesize，每块 sb_inopblock 个
            inodes_to_scan = agi.agi_count
            scan_n = min(inodes_to_scan, inode_scan_limit)

            for ino_off in range(scan_n):
                blk_off = ino_off // sb.sb_inopblock
                offset_in_blk = (ino_off % sb.sb_inopblock) * sb.sb_inodesize

                abs_byte = ag_start + inode_start_byte + blk_off * sb.sb_blocksize + offset_in_blk
                if abs_byte + sb.sb_inodesize > ag_start + sb.sb_agblocks * sb.sb_blocksize:
                    break

                f.seek(abs_byte)
                ino_data = f.read(sb.sb_inodesize)
                if len(ino_data) < sb.sb_inodesize:
                    continue

                di_magic = struct.unpack_from(">H", ino_data, 0)[0]
                if di_magic != 0x494E:  # "IN"
                    continue

                di_mode = struct.unpack_from(">H", ino_data, 2)[0]
                if di_mode == 0:
                    continue

                di_nlink = ino_data[6]
                di_size = struct.unpack_from(">Q", ino_data, 8)[0]
                di_format = ino_data[0x32] if len(ino_data) > 0x32 else 0

                # 只关心普通文件 + 已删除（nlink=0）
                if (di_mode & 0o170000) != 0o100000:
                    continue
                if di_nlink != 0:
                    continue

                ino_num = ag * inodes_to_scan + ino_off + 1
                deleted.append(DeletedXfsFile(
                    inode_num=ino_num,
                    size=di_size,
                    mode=di_mode,
                    format=di_format,
                    nlink=di_nlink,
                    di_magic=di_magic,
                ))

                if len(deleted) >= inode_scan_limit:
                    return sb, deleted

    return sb, deleted
