"""
XFS 真实恢复：从 inode fork data 重建文件内容。

XFS inode fork 位置：
- di_mode 偏移 = 2 (大端)
- di_format 偏移 = 0x32 (大端, 1 字节)
- di_forkoff 偏移 = 0x33 (大端, 1 字节) — 区分 data fork / attr fork 的字节偏移
- data fork 起始 = 100 (v3 inode) 或 96 (v2 inode)

fork 内容取决于 di_format：
- LOCAL (1): 小文件内联 (≤2KB)
- EXTENTS (2): 数组形式的 extent
- BTREE (3): B+tree 形式
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass
class XfsExtent:
    """xfs_bmbt_rec（48 位逻辑块号版本）"""
    startoff: int      # 逻辑块号
    startblock: int    # 物理块号
    blockcount: int    # 块数
    flag: int          # 0=normal, 1=unwritten


def parse_xfs_bmbt_rec(data: bytes, rec_format: int = 0) -> XfsExtent:
    """解析 xfs_bmbt_rec。

    rec_format=0（v4 文件系统，inode ≥256 字节）：
      struct xfs_bmbt_rec {
        __be64 l0;        // startoff (63 位) + startblock 高 21 位
        __be64 l1;        // startblock 低 43 位 + blockcount (21 位) + flag (1 位)
      }
    rec_format=1（v5 文件系统默认，物理块 53 位）：
      struct xfs_bmbt_rec {
        __be64 l0;        // startoff (64 位)
        __be64 l1;        // startblock (54 位) + blockcount (21 位) + flag (1 位)
      }
    """
    if rec_format == 0:
        l0 = struct.unpack_from(">Q", data, 0)[0]
        l1 = struct.unpack_from(">Q", data, 8)[0]
        startoff = l0 >> 9  # 63 位
        startblock = ((l0 & 0x1FF) << 43) | (l1 >> 21)  # 21 + 43 = 64 位
        blockcount = (l1 >> 1) & 0x1FFFFF  # 21 位
        flag = l1 & 0x1
    else:
        l0 = struct.unpack_from(">Q", data, 0)[0]
        l1 = struct.unpack_from(">Q", data, 8)[0]
        startoff = l0
        startblock = l1 >> 10  # 54 位
        blockcount = (l1 >> 1) & 0x7FFFFF  # 21 位
        flag = l1 & 0x1

    return XfsExtent(
        startoff=startoff,
        startblock=startblock,
        blockcount=blockcount,
        flag=flag,
    )


@dataclass
class XfsBmbtKey:
    """btree 节点 key（lblock:64 位 + forkoff:8 位 = 72 位）"""
    lblock: int
    forkoff: int


def parse_xfs_bmbt_key(data: bytes, rec_format: int = 0) -> XfsBmbtKey:
    """btree 节点 key：前 8 字节是 lblock（逻辑块号），后 1 字节是 forkoff"""
    if rec_format == 0:
        # v4：lblock 63 位 + forkoff 8 位
        l0 = struct.unpack_from(">Q", data, 0)[0]
        return XfsBmbtKey(lblock=l0 >> 9, forkoff=l0 & 0xFF)
    else:
        # v5：lblock 64 位 + forkoff 8 位
        lblock = struct.unpack_from(">Q", data, 0)[0]
        forkoff = data[8]
        return XfsBmbtKey(lblock=lblock, forkoff=forkoff)


def restore_xfs_inode_extents(
    dev_path: str | Path,
    block_size: int,
    inode_offset_in_ag: int,
    inode_data: bytes,
    output_path: str | Path,
    rec_format: int = 0,
) -> int:
    """从 XFS inode 的 fork data 恢复文件内容。

    inode_data: 单个 inode 的原始字节（v3 = 256 字节）
    """
    # 数据 fork 起始 = inode_size - forkoff (data 部分)
    # 简化：v3 inode (256 字节) data fork 从 offset 100 起
    data_fork_offset = 100
    if len(inode_data) < data_fork_offset + 16:
        return 0

    di_format = inode_data[0x32]
    out = bytearray()

    with open(dev_path, "rb") as f:
        if di_format == 1:  # LOCAL — 小文件内联
            # data 在 fork 后
            # inline data 长度由 di_size 决定
            di_size = struct.unpack_from(">Q", inode_data, 8)[0]
            inline_data = inode_data[data_fork_offset:data_fork_offset + di_size]
            out.extend(inline_data)

        elif di_format == 2:  # EXTENTS — 直接数组
            # bmbt_rec 每个 16 字节
            di_size = struct.unpack_from(">Q", inode_data, 8)[0]
            n_extents = di_size // (block_size // 2)  # 简化估算
            # 实际：bmbt_keypoint 在 first_rec 前是 0 entries / 1 key
            # 实际：v4 fs header = 4 keys (16 bytes) + n_extents * 16 bytes
            # 简化：尝试读 entries
            offset = data_fork_offset
            # 跳过可能的 keypoint
            for entry_idx in range(40):  # 最多 40 个 extent
                if offset + 16 > len(inode_data):
                    break
                # 判断是 key 还是 rec（rec 的 blockcount 不会 > 0xFFFFF）
                # 简化：直接尝试解析为 extent
                ext = parse_xfs_bmbt_rec(inode_data[offset:offset + 16], rec_format)
                if ext.flag > 1 or ext.blockcount > 0xFFFFF:
                    # 可能是 key
                    offset += 16
                    continue
                if ext.blockcount == 0:
                    offset += 16
                    continue
                # 物理块 = startblock (相对 AG)
                physical_block = ext.startblock
                f.seek(physical_block * block_size)
                try:
                    data = f.read(ext.blockcount * block_size)
                    out.extend(data)
                except Exception:
                    break
                offset += 16

        elif di_format == 3:  # BTREE
            # btree 头: magic(4) + level(2) + numrecs(2) + ...
            # struct xfs_btree_hdr {
            #   __be32 bb_magic;
            #   __be16 bb_level;
            #   __be16 bb_numrecs;
            #   __be64 bb_leftsib;
            #   __be64 bb_rightsib;
            # }
            # 后续是 keys[] + pointers[] + recs[]
            # key = 9 字节, pointer = 8 字节, rec = 16 字节
            # 每个 block 容纳 maxrecs = (block_size - hdr_size - 1) / (key + rec)
            hdr_off = data_fork_offset
            magic = struct.unpack_from(">I", inode_data, hdr_off)[0]
            if magic != 0x424D4233:  # "BMB3" = btree magic
                return 0
            level = struct.unpack_from(">H", inode_data, hdr_off + 4)[0]
            numrecs = struct.unpack_from(">H", inode_data, hdr_off + 6)[0]
            leftsib = struct.unpack_from(">Q", inode_data, hdr_off + 8)[0]
            rightsib = struct.unpack_from(">Q", inode_data, hdr_off + 16)[0]

            # 简化：仅当 level=0（叶节点）时遍历 recs
            if level != 0:
                # 需要递归读 btree 内部节点，简化不处理
                return 0

            # level=0：keys 起始 hdr+24，每 key=9 字节
            # recs 在所有 keys 后开始
            keys_start = hdr_off + 24
            for i in range(numrecs):
                rec_off = keys_start + (numrecs + 1) * 9 + i * 16
                if rec_off + 16 > len(inode_data):
                    break
                ext = parse_xfs_bmbt_rec(inode_data[rec_off:rec_off + 16], rec_format)
                if ext.blockcount > 0:
                    physical_block = ext.startblock
                    f.seek(physical_block * block_size)
                    out.extend(f.read(ext.blockcount * block_size))

    written = len(out)
    if written > 0:
        Path(output_path).write_bytes(out)
    return written
