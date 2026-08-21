"""
Magic 头扫描：通过文件签名在磁盘字节流中定位潜在文件。

支持常见文件类型：JPEG/PNG/GIF/PDF/ZIP/TAR/GZIP/ELF/文本等。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileSignature:
    name: str           # 友好名称
    magic: bytes        # 起始 magic bytes
    offset: int = 0     # 在文件中偏移
    footer: bytes | None = None  # 结束标记（用于定位文件大小）


# 常见文件 magic 签名
SIGNATURES: list[FileSignature] = [
    FileSignature("JPEG", b"\xFF\xD8\xFF"),
    FileSignature("PNG", b"\x89PNG\r\n\x1A\n"),
    FileSignature("GIF", b"GIF87a"),
    FileSignature("GIF", b"GIF89a"),
    FileSignature("PDF", b"%PDF-"),
    FileSignature("ZIP", b"PK\x03\x04"),
    FileSignature("ZIP_EMPTY", b"PK\x05\x06"),  # 空 ZIP
    FileSignature("GZIP", b"\x1F\x8B\x08"),
    FileSignature("TAR", b"ustar", offset=257),  # tar 头在 257 偏移
    FileSignature("ELF", b"\x7FELF"),
    FileSignature("BMP", b"BM"),
    FileSignature("WAV", b"RIFF"),
    FileSignature("OGG", b"OggS"),
    FileSignature("FLAC", b"fLaC"),
    FileSignature("SQLITE", b"SQLite format 3\x00"),
    FileSignature("CLASS", b"\xCA\xFE\xBA\xBE"),  # Java class
    FileSignature("XZ", b"\xFD7zXZ\x00"),
    FileSignature("7Z", b"7z\xBC\xAF\x27\x1C"),
    FileSignature("BZ2", b"BZh"),
]


def scan_magic(dev_path: str | Path, max_hits: int = 1000, min_block: int = 0) -> list[dict]:
    """扫描磁盘字节流，按文件 magic 找潜在文件。

    Returns: list of {offset, type, magic_hex}
    """
    hits = []
    with open(dev_path, "rb") as f:
        # 简化：按 4KB 块读，避免内存爆
        block_size = 4 * 1024 * 1024  # 4 MB chunks
        overlap = 1024  # 1 KB overlap 防止 magic 跨界

        offset = 0
        last_block = b""

        while True:
            chunk = f.read(block_size)
            if not chunk:
                break

            # 拼接 overlap
            data = last_block + chunk
            data_start = offset - len(last_block)

            for sig in SIGNATURES:
                pos = 0
                while True:
                    idx = data.find(sig.magic, pos)
                    if idx < 0:
                        break
                    # 跳过 boot sector / superblock 区域（前 1MB）
                    if data_start + idx < min_block:
                        pos = idx + 1
                        continue
                    hits.append({
                        "offset": data_start + idx,
                        "type": sig.name,
                        "magic_hex": sig.magic.hex(),
                        "file_offset": sig.offset,
                    })
                    if len(hits) >= max_hits:
                        return hits
                    pos = idx + 1

            last_block = data[-overlap:] if len(data) >= overlap else data
            offset += len(chunk)

    return hits


def group_consecutive_hits(hits: list[dict], max_gap: int = 4 * 1024 * 1024) -> list[list[dict]]:
    """把相邻的 magic 命中分组为"疑似文件区域"。

    例: 多个 JPEG SOI 标志相隔很近 → 可能是多张图连续存储。
    """
    if not hits:
        return []

    sorted_hits = sorted(hits, key=lambda h: h["offset"])
    groups = [[sorted_hits[0]]]

    for h in sorted_hits[1:]:
        prev = groups[-1][-1]
        if h["offset"] - prev["offset"] <= max_gap:
            groups[-1].append(h)
        else:
            groups.append([h])

    return groups


def extract_text_strings(dev_path: str | Path, min_len: int = 8, max_hits: int = 1000,
                          utf8_only: bool = False) -> list[dict]:
    """扫描磁盘中的可打印字符串（用于恢复纯文本文件）。"""
    import re
    hits = []
    if utf8_only:
        pat_utf8 = re.compile(rb"[\xE0-\xEF][\x80-\xBF]{2}|[\x20-\x7E]+")
        pat = None
    else:
        pat_utf8 = None
        pat = re.compile(rb"[\x20-\x7E]{%d,}" % min_len)

    with open(dev_path, "rb") as f:
        block_size = 4 * 1024 * 1024
        overlap = 4096
        last = b""
        offset = 0

        while True:
            chunk = f.read(block_size)
            if not chunk:
                break

            data = last + chunk
            data_start = offset - len(last)

            if utf8_only:
                for m in pat_utf8.finditer(data):
                    try:
                        s = m.group().decode("utf-8", errors="ignore")
                        if len(s) >= min_len:
                            hits.append({"offset": data_start + m.start(), "text": s[:200]})
                            if len(hits) >= max_hits:
                                return hits
                    except Exception:
                        continue
            else:
                for m in pat.finditer(data):
                    s = m.group().decode("latin-1", errors="ignore")
                    hits.append({"offset": data_start + m.start(), "text": s[:200]})
                    if len(hits) >= max_hits:
                        return hits

            last = data[-overlap:] if len(data) >= overlap else data
            offset += len(chunk)

    return hits
