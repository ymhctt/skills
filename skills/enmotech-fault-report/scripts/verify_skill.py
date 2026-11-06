#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_skill.py — Self-test for enmotech-fault-report skill

Re-runs the full end-to-end pipeline using the example content,
checks the generated docx, and reports a summary.

Usage:
    /usr/bin/python3 verify_skill.py
"""
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
EXAMPLE = SCRIPTS_DIR / "example_rac_eviction.json"
TEST_OUTPUT = "/tmp/enmotech_skill_verify_output.docx"

PASS = "  \033[32m✓\033[0m"
FAIL = "  \033[31m✗\033[0m"
INFO = "  →"


def run_build():
    """Run the build script with the example content."""
    cmd = [
        "/usr/bin/python3",
        str(SCRIPTS_DIR / "build_report.py"),
        "--content", str(EXAMPLE),
        "--output", TEST_OUTPUT,
    ]
    print(f"\n[1/3] Running build...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{FAIL} build failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    print(result.stdout)
    return TEST_OUTPUT


def verify_docx(docx_path: str):
    """Verify the generated docx file structure & content."""
    print(f"\n[2/3] Verifying docx content...")

    if not os.path.exists(docx_path):
        print(f"{FAIL} file not found: {docx_path}")
        sys.exit(1)

    with zipfile.ZipFile(docx_path, "r") as z:
        doc = z.read("word/document.xml").decode("utf-8")
        names = z.namelist()

    checks = []

    # 1. File integrity
    checks.append(("file size > 50KB", len(doc) > 50_000, f"{len(doc):,} bytes"))
    checks.append(("contains word/document.xml", "word/document.xml" in names, ""))
    checks.append(("contains word/styles.xml", "word/styles.xml" in names, ""))
    checks.append(("contains word/header1.xml", "word/header1.xml" in names, ""))
    checks.append(("contains word/footer1.xml", "word/footer1.xml" in names, ""))

    # 2. XML validity
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(doc)
        checks.append(("document.xml is valid XML", True, ""))
    except ET.ParseError as e:
        checks.append(("document.xml is valid XML", False, str(e)))

    # 3. Chapter structure
    h1_count = len(re.findall(r'<w:pStyle w:val="1"/>', doc))
    h2_count = len(re.findall(r'<w:pStyle w:val="2"/>', doc))
    a5_count = len(re.findall(r'<w:pStyle w:val="a5"/>', doc))
    checks.append(("5 H1 chapter headings", h1_count == 5, f"found {h1_count}"))
    checks.append(("3 H2 subsection headings (in 故障分析)", h2_count == 3, f"found {h2_count}"))
    checks.append(("≥30 body paragraphs (a5)", a5_count >= 30, f"found {a5_count}"))

    # 4. Title presence (cover)
    expected_title = "统一权限数据库RAC节点驱逐故障分析报告"
    title_in_t = len(re.findall(
        r'<w:t[^>]*>' + re.escape(expected_title) + r'</w:t>', doc
    ))
    checks.append(("title appears as <w:t> in cover (1x)", title_in_t >= 1, f"found {title_in_t}"))

    # 5. No double-titling
    # The cover is one <w:p> with one <w:t> containing only the title.
    # The 附件4 mention is a long paragraph where the title is part of a
    # longer text. So the check is: count <w:p> where the only <w:t> is the title.
    para_re = re.compile(
        r'<w:p(?:\s[^>]*)?>(?:(?!</w:p>).)*?</w:p>',
        re.DOTALL,
    )
    cover_only_count = 0
    for p in para_re.findall(doc):
        # Get all <w:t> texts in this paragraph
        ts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)
        # If this paragraph has only one <w:t> and it's the title → cover
        if len(ts) == 1 and ts[0] == expected_title:
            cover_only_count += 1
    checks.append(("cover title not duplicated", cover_only_count == 1,
                   f"cover-only paragraphs: {cover_only_count}"))

    # 6. Key analysis content preserved
    all_text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", doc))
    for keyword in ["CRS-1612", "ixgbe", "TX timeout", "miimon",
                    "rac45d1", "rac45d2", "bond1",
                    "故障现象", "故障根源", "故障处置",
                    "根本解决方案及建议", "其他", "附件"]:
        checks.append((f"keyword '{keyword}' present", keyword in all_text, ""))

    # 7. Footer attribution
    with zipfile.ZipFile(docx_path, "r") as z:
        footer = z.read("word/footer1.xml").decode("utf-8")
    checks.append(("footer has attribution '基于'",
                  "基于" in footer and "技能知识库深度分析" in footer, ""))

    # Print results
    print()
    all_pass = True
    for desc, ok, info in checks:
        marker = PASS if ok else FAIL
        line = f"{marker} {desc}"
        if info and not ok:
            line += f" ({info})"
        print(line)
        if not ok:
            all_pass = False

    # 8. Final summary
    green = "\033[32m"
    red = "\033[31m"
    endc = "\033[0m"
    status = f"{green}ALL PASS{endc}" if all_pass else f"{red}FAILURES{endc}"
    print(f"\n[3/3] Summary:")
    print(f"  File: {docx_path}")
    print(f"  Size: {os.path.getsize(docx_path):,} bytes")
    print(f"  Status: {status}")

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("  enmotech-fault-report skill self-test")
    print("=" * 60)
    out = run_build()
    verify_docx(out)
