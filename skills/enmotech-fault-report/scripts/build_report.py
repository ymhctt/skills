#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enmotech-fault-report builder
=============================

基于云和恩墨「故障处理报告模板」生成 Word (.docx) 故障分析报告。

输入方式（两种任选）：
  1. 命令行传 --content <json文件> 或 --content <python文件>
  2. Python API：from build_enmotech_report import build_report; build_report(...)

JSON 顶层结构（与 Enmotech 模板章节 1:1 对应）：
  {
    "title": "统一权限数据库RAC节点驱逐故障分析报告",     # 必填，封面主标题
    "background": [ "段落1...", "段落2..." ],                # 1. 背景概述
    "phenomenon": [ "段落1...", "code:日志片段", "段落2..." ],  # 2.1 故障现象
    "root_cause": [ "段落1...", ... ],                       # 2.2 故障根源
    "action": [ "段落1...", ... ],                           # 2.3 故障处置
    "solution": [ "段落1...", ... ],                         # 3. 根本解决方案及建议
    "other": [ "段落1...", ... ],                            # 4. 其他
    "attachments": [ "附件1：xxx", ... ],                    # 5. 附件
    "footer_source": "云和恩墨（北京）信息技术有限公司数据库技能知识库深度分析"  # 可选
  }

章节特殊语法（在段落字符串中识别）：
  - "code:..."  → 整段渲染为等宽代码块（Consolas/宋体 10pt）
  - "table:...|...|...\nrow2|..."  → 多行多列表格（首行为表头）
  - "h3:..."  → H3 小节标题（pStyle "3"）
  - "bold:..."  → 整段加粗
  - 普通文本 → pStyle "a5" 正文（首行缩进 480 dxa = 24pt）
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
#  XML helper builders (OOXML 1.0 compatible, MS Word 2010+)
# ═══════════════════════════════════════════════════════════════

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"


def _xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _base_ppr(style: str) -> str:
    """Common pPr base."""
    return f'<w:pPr><w:pStyle w:val="{style}"/>'


def p(text: str, style: str = "a5", bold: bool = False, indent_first: bool = True,
      line_spacing: int = 312) -> str:
    """Body paragraph. Default: 1.5x line spacing, first-line indent 480 dxa."""
    text_escaped = _xml_escape(text)
    rpr_parts = [
        '<w:rFonts w:asciiTheme="minorEastAsia" w:eastAsiaTheme="minorEastAsia" w:hAnsiTheme="minorEastAsia"/>'
    ]
    if bold:
        rpr_parts.append("<w:b/><w:bCs/>")
    rpr = "<w:rPr>" + "".join(rpr_parts) + "</w:rPr>"

    ppr_parts = [f'<w:pStyle w:val="{style}"/>',
                 f'<w:spacing w:line="{line_spacing}" w:lineRule="auto"/>']
    if indent_first and style == "a5":
        ppr_parts.append('<w:ind w:firstLine="480"/>')

    ppr_rpr = ('<w:rPr><w:rFonts w:asciiTheme="minorEastAsia" '
               'w:eastAsiaTheme="minorEastAsia" w:hAnsiTheme="minorEastAsia"/>')
    if bold:
        ppr_rpr += "<w:b/><w:bCs/>"
    ppr_rpr += "</w:rPr>"

    return (f"<w:p>{_base_ppr(style)}{''.join(ppr_parts)}{ppr_rpr}</w:pPr>"
            f"<w:r>{rpr}<w:t xml:space=\"preserve\">{text_escaped}</w:t></w:r></w:p>")


def h1(text: str, bookmark_id: int, bookmark_name: str) -> str:
    """H1 chapter heading (pStyle "1")."""
    text_escaped = _xml_escape(text)
    ppr = (
        '<w:pPr><w:pStyle w:val="1"/>'
        '<w:spacing w:line="312" w:lineRule="auto"/>'
        '<w:rPr>'
        '<w:rFonts w:ascii="宋体" w:hAnsi="宋体"/>'
        '<w:b/><w:bCs/>'
        '<w:sz w:val="36"/><w:szCs w:val="36"/>'
        '</w:rPr></w:pPr>'
    )
    rpr = (
        '<w:rPr>'
        '<w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>'
        '<w:b/><w:bCs/>'
        '<w:sz w:val="36"/><w:szCs w:val="36"/>'
        '</w:rPr>'
    )
    return (f'<w:p>{ppr}'
            f'<w:bookmarkStart w:id="{bookmark_id}" w:name="{bookmark_name}"/>'
            f'<w:r>{rpr}<w:t xml:space="preserve">{text_escaped}</w:t></w:r>'
            f'<w:bookmarkEnd w:id="{bookmark_id}"/></w:p>')


def h2(text: str, bookmark_id: int, bookmark_name: str) -> str:
    """H2 sub-section heading (pStyle "2")."""
    text_escaped = _xml_escape(text)
    ppr = (
        '<w:pPr><w:pStyle w:val="2"/>'
        '<w:spacing w:line="312" w:lineRule="auto"/>'
        '<w:rPr>'
        '<w:rFonts w:ascii="宋体" w:hAnsi="宋体"/>'
        '<w:b/><w:bCs/>'
        '<w:sz w:val="32"/><w:szCs w:val="32"/>'
        '</w:rPr></w:pPr>'
    )
    rpr = (
        '<w:rPr>'
        '<w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>'
        '<w:b/><w:bCs/>'
        '<w:sz w:val="32"/><w:szCs w:val="32"/>'
        '</w:rPr>'
    )
    return (f'<w:p>{ppr}'
            f'<w:bookmarkStart w:id="{bookmark_id}" w:name="{bookmark_name}"/>'
            f'<w:r>{rpr}<w:t xml:space="preserve">{text_escaped}</w:t></w:r>'
            f'<w:bookmarkEnd w:id="{bookmark_id}"/></w:p>')


def code_block(text: str) -> str:
    """Multi-line monospace block (Consolas 10pt)."""
    lines = _xml_escape(text).split("\n")
    paras = []
    for line in lines:
        line_xml = line.replace(" ", "&#160;")  # preserve leading spaces
        para = (
            '<w:p><w:pPr><w:spacing w:line="240" w:lineRule="auto"/>'
            '<w:ind w:left="480" w:firstLine="0"/>'
            '<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="宋体" w:hint="eastAsia"/>'
            '<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr></w:pPr>'
            '<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="宋体" w:hint="eastAsia"/>'
            '<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
            f'<w:t xml:space="preserve">{line_xml}</w:t></w:r></w:p>'
        )
        paras.append(para)
    return "\n".join(paras)


def table_row(cells, header: bool = False) -> str:
    """One table row. cells = list of cell text strings."""
    cells_xml = []
    for cell in cells:
        ct = _xml_escape(cell)
        shading = '<w:shd w:val="clear" w:color="auto" w:fill="4472C4"/>' if header else ""
        color = '<w:color w:val="FFFFFF"/>' if header else ""
        b = "<w:b/><w:bCs/>" if header else ""
        cell_xml = (
            f'<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/>{shading}'
            f'<w:tcBorders><w:top w:val="single" w:sz="4" w:color="BFBFBF"/>'
            f'<w:left w:val="single" w:sz="4" w:color="BFBFBF"/>'
            f'<w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/>'
            f'<w:right w:val="single" w:sz="4" w:color="BFBFBF"/></w:tcBorders>'
            f'</w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:line="240" w:lineRule="auto"/>'
            f'<w:rPr><w:rFonts w:asciiTheme="minorEastAsia" w:eastAsiaTheme="minorEastAsia" w:hAnsiTheme="minorEastAsia"/>'
            f'{b}<w:sz w:val="20"/><w:szCs w:val="20"/>{color}</w:rPr></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:asciiTheme="minorEastAsia" w:eastAsiaTheme="minorEastAsia" w:hAnsiTheme="minorEastAsia"/>'
            f'{b}<w:sz w:val="20"/><w:szCs w:val="20"/>{color}</w:rPr>'
            f'<w:t xml:space="preserve">{ct}</w:t></w:r></w:p></w:tc>'
        )
        cells_xml.append(cell_xml)
    return f'<w:tr>{"".join(cells_xml)}</w:tr>'


def table(rows, widths=None) -> str:
    """Full table. rows = list of lists. widths = list of dxa widths (optional)."""
    if widths:
        grid_cols = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
        grid = f'<w:tblGrid>{grid_cols}</w:tblGrid>'
        table_width = sum(widths)
    else:
        grid = ""
        table_width = 9000
    rows_xml = "".join(table_row(r, header=(i == 0)) for i, r in enumerate(rows))
    return (
        f'<w:tbl><w:tblPr><w:tblW w:w="{table_width}" w:type="dxa"/>'
        f'<w:jc w:val="left"/>'
        f'<w:tblBorders>'
        f'<w:top w:val="single" w:sz="4" w:color="BFBFBF"/>'
        f'<w:left w:val="single" w:sz="4" w:color="BFBFBF"/>'
        f'<w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/>'
        f'<w:right w:val="single" w:sz="4" w:color="BFBFBF"/>'
        f'<w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/>'
        f'<w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/>'
        f'</w:tblBorders>'
        f'<w:tblLayout w:type="fixed"/>'
        f'</w:tblPr>{grid}{rows_xml}</w:tbl>'
    )


# ═══════════════════════════════════════════════════════════════
#  Content parser
# ═══════════════════════════════════════════════════════════════

def render_paragraph(item) -> str:
    """Render a single content item (string or dict).

    String prefixes:
      "code:..."      → code block
      "table:..."     → table (multi-line, | delimiter, first row = header)
      "h3:..."        → H3 heading
      "bold:..."      → bold body paragraph
      other           → plain body paragraph
    """
    if isinstance(item, dict):
        # explicit type
        kind = item.get("type", "p")
        text = item.get("text", "")
        if kind == "code":
            return code_block(text)
        if kind == "table":
            rows = item.get("rows", [])
            widths = item.get("widths")
            return table(rows, widths=widths)
        if kind == "h3":
            # H3 uses pStyle "3" (we render as bold pStyle "a5" with smaller font)
            return p(text, style="a5", bold=True, indent_first=False)
        if kind == "bold":
            return p(text, bold=True)
        if kind == "p":
            return p(text, bold=item.get("bold", False))
    # string form
    if isinstance(item, str):
        if item.startswith("code:"):
            return code_block(item[5:].lstrip("\n"))
        if item.startswith("table:"):
            csv = item[6:].strip()
            rows = [r.split("|") for r in csv.split("\n") if r.strip()]
            return table(rows)
        if item.startswith("h3:"):
            return p(item[3:].strip(), bold=True, indent_first=False)
        if item.startswith("bold:"):
            return p(item[5:].strip(), bold=True)
    return p(str(item))


def render_chapter(items, h_func, h_args) -> str:
    """Render a chapter: heading + list of content items."""
    parts = [h_func(*h_args)]
    for it in items or []:
        parts.append(render_paragraph(it))
    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════
#  Build full body XML
# ═══════════════════════════════════════════════════════════════

# Bookmark IDs: 0=背景概述(template), 11-17=chapters
BOOKMARK_IDS = {
    "phenomenon": 12,
    "root_cause": 13,
    "action": 14,
    "solution": 15,
    "other": 16,
    "attachment": 17,
}


def build_body_xml(content: dict) -> str:
    """Build the full body XML (between 背景概述 H1 and _GoBack bookmark)."""
    parts = []

    # 1. 背景概述 (keep template's H1; we just add paragraphs)
    for item in content.get("background", []):
        parts.append(render_paragraph(item))

    # 2. 故障分析
    parts.append(h1("故障分析", bookmark_id=11, bookmark_name="_Toc_analysis"))
    parts.append(h2("故障现象", bookmark_id=BOOKMARK_IDS["phenomenon"],
                    bookmark_name="_Toc_phenomenon"))
    for item in content.get("phenomenon", []):
        parts.append(render_paragraph(item))
    parts.append(h2("故障根源", bookmark_id=BOOKMARK_IDS["root_cause"],
                    bookmark_name="_Toc_rootcause"))
    for item in content.get("root_cause", []):
        parts.append(render_paragraph(item))
    parts.append(h2("故障处置", bookmark_id=BOOKMARK_IDS["action"],
                    bookmark_name="_Toc_action"))
    for item in content.get("action", []):
        parts.append(render_paragraph(item))

    # 3. 根本解决方案及建议
    parts.append(h1("根本解决方案及建议", bookmark_id=BOOKMARK_IDS["solution"],
                    bookmark_name="_Toc_solution"))
    for item in content.get("solution", []):
        parts.append(render_paragraph(item))

    # 4. 其他
    parts.append(h1("其他", bookmark_id=BOOKMARK_IDS["other"],
                    bookmark_name="_Toc_other"))
    for item in content.get("other", []):
        parts.append(render_paragraph(item))

    # 5. 附件
    parts.append(h1("附件", bookmark_id=BOOKMARK_IDS["attachment"],
                    bookmark_name="_Toc_attachment"))
    for item in content.get("attachments", []):
        parts.append(render_paragraph(item))

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════
#  DOCX manipulation
# ═══════════════════════════════════════════════════════════════

# Cover title placeholder / suffix (the 2-run design that causes double-titling)
TITLE_PLACEHOLDER = "****"
TITLE_SUFFIX = "业务系统故障分析报告"

# Enmotech 故障处理报告模板结构标记：
#   封面标题: 占位符 **** + 固定后缀 "业务系统故障分析报告"（在两个 run 中）
#   正文结构: 5 个 H1 章节(pStyle="1"): 背景概述 / 故障分析 / 根本解决方案及建议 / 其他 / 附件
#             故障分析 下有 3 个 H2 (pStyle="2"): 故障现象 / 故障根源 / 故障处置
#   正文终点: 最后一个 H1 章节"附件"段结束 → _GoBack bookmark

# 章节关键词（用于识别 H1 段落）
H1_CHAPTERS = {
    "背景概述": {"key": "background", "h1_text": "背景概述"},
    "故障分析": {"key": "fault_analysis", "h1_text": "故障分析"},
    "根本解决方案及建议": {"key": "solution", "h1_text": "根本解决方案及建议"},
    "其他": {"key": "other", "h1_text": "其他"},
    "附件": {"key": "attachment", "h1_text": "附件"},
}
H2_CHAPTERS = ["故障现象", "故障根源", "故障处置"]


def unpack_docx(docx_path: str, dest_dir: str) -> None:
    """Unpack a .docx (ZIP) into dest_dir."""
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir)
    with zipfile.ZipFile(docx_path, "r") as z:
        z.extractall(dest_dir)


def repack_docx(src_dir: str, out_docx_path: str) -> None:
    """Repack a directory back into .docx (ZIP_DEFLATED compression)."""
    if os.path.exists(out_docx_path):
        os.remove(out_docx_path)
    src = Path(src_dir)
    with zipfile.ZipFile(out_docx_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in src.rglob("*"):
            if f.is_file():
                arcname = str(f.relative_to(src))
                z.write(f, arcname)

# H1 段落正则（一个完整 <w:p> 包含 pStyle="1"）
H1_PARA_RE = re.compile(
    r'<w:p [^>]*>(?:(?!</w:p>).)*?<w:pStyle w:val="1"/>(?:(?!</w:p>).)*?</w:p>',
    re.DOTALL,
)
GOBACK_MARKER = '<w:bookmarkStart w:id="8" w:name="_GoBack"/>'


def _h1_para_text(p_xml: str) -> str:
    """Concatenate all <w:t> texts within an H1 paragraph to identify chapter."""
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p_xml))


def fix_title_paragraph(doc_xml: str, new_title: str) -> str:
    """Surgically replace the 2-run title paragraph with a single-run clean title.

    The Enmotech template uses two adjacent <w:r> blocks for the cover title:
      <w:r>...<w:t>****</w:t></w:r>          ← placeholder
      <w:r>...<w:t>业务系统故障分析报告</w:t></w:r>   ← fixed suffix
    Replacing them naively causes double-titling. We replace the WHOLE
    <w:p>...</w:p> containing them with a single-run version.
    """
    pos = doc_xml.find(TITLE_PLACEHOLDER)
    if pos < 0:
        # No placeholder found — title may already be in a single run
        # (e.g. user re-ran the skill on a previously generated file)
        return doc_xml

    # Find the enclosing <w:p ...>...</w:p>
    para_start = doc_xml.rfind("<w:p ", 0, pos)
    if para_start < 0:
        para_start = doc_xml.rfind("<w:p>", 0, pos)
    para_end = doc_xml.find("</w:p>", pos) + len("</w:p>")

    # Build clean replacement: keep original pPr, single <w:r> with new title
    ppr_match = re.search(r"<w:pPr>.*?</w:pPr>", doc_xml[para_start:para_end], re.DOTALL)
    ppr_xml = ppr_match.group(0) if ppr_match else '<w:pPr><w:jc w:val="center"/></w:pPr>'

    new_para = (
        f'<w:p>{ppr_xml}'
        f'<w:r><w:rPr><w:rFonts w:ascii="宋体" w:eastAsiaTheme="minorEastAsia" w:hAnsi="宋体"/>'
        f'<w:b/><w:sz w:val="56"/><w:szCs w:val="56"/></w:rPr>'
        f'<w:t xml:space="preserve">{_xml_escape(new_title)}</w:t></w:r></w:p>'
    )
    return doc_xml[:para_start] + new_para + doc_xml[para_end:]


def replace_body_content(doc_xml: str, new_body_xml: str) -> str:
    """Replace the template's body content with new_body_xml.

    Strategy:
      1. Locate the REAL 背景概述 H1 paragraph (by text) — its end is the start of body
      2. Drop any stray leading empty H1 placeholder that precedes it
      3. Locate the _GoBack bookmark — its containing paragraph is the end
      4. Keep everything before 背景概述 H1 (cover, TOC) and after _GoBack paragraph (sectPr)

    Note: the Enmotech template ships with a stray empty leading H1 (carrying a
    <w:numPr>, no text) BEFORE the real 背景概述 H1. Anchoring on the first H1
    blindly would (a) delete the real 背景概述 heading and (b) leave the empty
    H1 as a blank chapter title. We anchor on the real 背景概述 H1 by text and
    drop the stray placeholder instead.
    """
    h1_iter = list(H1_PARA_RE.finditer(doc_xml))
    if not h1_iter:
        raise RuntimeError("No H1 paragraph found — template structure changed?")

    # Always anchor on the real 背景概述 H1, identified by its text.
    bg_h1 = None
    for m in h1_iter:
        if _h1_para_text(m.group(0)) == "背景概述":
            bg_h1 = m
            break
    if bg_h1 is None:
        # Fallback: treat the first H1 as 背景概述
        bg_h1 = h1_iter[0]

    # Replacement span starts at the (possibly stray) first H1 so the empty
    # leading placeholder is removed; the real 背景概述 H1 is kept.
    stray_start = h1_iter[0].start()

    # Find paragraph containing _GoBack
    gob_idx = doc_xml.find(GOBACK_MARKER)
    if gob_idx < 0:
        raise RuntimeError("_GoBack bookmark not found — template structure changed?")
    # Walk back to the enclosing <w:p>
    para_start = doc_xml.rfind("<w:p ", 0, gob_idx)
    if para_start < 0:
        para_start = doc_xml.rfind("<w:p>", 0, gob_idx)

    return (doc_xml[:stray_start]
            + bg_h1.group(0)
            + "\n" + new_body_xml + "\n"
            + doc_xml[para_start:])


def replace_footer_text(doc_xml: str, new_text: str) -> str:
    """No-op for now — footer source is in footer1.xml not document.xml.
    Use replace_footer_source() instead."""
    return doc_xml


def replace_footer_source(work_dir: str, new_source: str) -> None:
    """Append a small attribution line at the end of footer1.xml.

    The Enmotech template's footer only has the standard copyright notice
    "云和恩墨（北京）信息技术有限公司 版权所有，严禁翻印  X / Y".
    We append a right-aligned small line indicating the analysis source.
    """
    footer_path = os.path.join(work_dir, "word", "footer1.xml")
    if not os.path.exists(footer_path):
        return
    with open(footer_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Build a small attribution paragraph (right-aligned, 9pt grey)
    attribution = (
        f'<w:p><w:pPr><w:pStyle w:val="a8"/><w:jc w:val="right"/>'
        f'<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        f'<w:color w:val="808080"/><w:sz w:val="18"/></w:rPr></w:pPr>'
        f'<w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
        f'<w:color w:val="808080"/><w:sz w:val="18"/></w:rPr>'
        f'<w:t xml:space="preserve">基于{_xml_escape(new_source)}</w:t></w:r></w:p>'
    )
    # Insert before </w:ftr>
    new_content = content.replace("</w:ftr>", attribution + "</w:ftr>", 1)
    with open(footer_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[footer] appended attribution: 基于{new_source}")


# ═══════════════════════════════════════════════════════════════
#  Main build pipeline
# ═══════════════════════════════════════════════════════════════

def build_report(
    content: dict,
    output_path: str,
    template_path: str = None,
    work_dir: str = None,
) -> str:
    """Build the .docx report.

    Args:
        content: dict with keys title, background, phenomenon, root_cause,
                 action, solution, other, attachments, (optional) footer_source
        output_path: final .docx file path
        template_path: path to template .docx (defaults to bundled asset)
        work_dir: scratch directory (default: tempdir)

    Returns:
        absolute path to generated .docx
    """
    if template_path is None:
        skill_dir = Path(__file__).resolve().parent.parent
        template_path = str(skill_dir / "assets" / "enmotech_fault_report_template.docx")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    title = content.get("title", "").strip()
    if not title:
        raise ValueError("content['title'] is required")

    if work_dir is None:
        work_dir = tempfile.mkdtemp(prefix="enmotech_fault_")
    else:
        os.makedirs(work_dir, exist_ok=True)

    try:
        # 1. Unpack
        unpack_docx(template_path, work_dir)

        # 2. Edit document.xml
        doc_xml_path = os.path.join(work_dir, "word", "document.xml")
        with open(doc_xml_path, "r", encoding="utf-8") as f:
            doc_xml = f.read()

        # 2a. Fix title (single source of truth for the title text)
        doc_xml = fix_title_paragraph(doc_xml, title)

        # 2b. Replace body
        body_xml = build_body_xml(content)
        doc_xml = replace_body_content(doc_xml, body_xml)

        with open(doc_xml_path, "w", encoding="utf-8") as f:
            f.write(doc_xml)

        # 3. Footer (optional)
        if content.get("footer_source"):
            replace_footer_source(work_dir, content["footer_source"])

        # 4. Repack
        repack_docx(work_dir, output_path)

        # 5. Sanity check
        verify_output(output_path, expected_title=title)

        return os.path.abspath(output_path)
    finally:
        if work_dir and work_dir.startswith(tempfile.gettempdir()):
            shutil.rmtree(work_dir, ignore_errors=True)


def verify_output(docx_path: str, expected_title: str) -> None:
    """Verify the generated docx: XML valid, title appears once on cover, body intact."""
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(docx_path, "r") as z:
        doc = z.read("word/document.xml").decode("utf-8")

    # Count occurrences of the title text in <w:t> elements (any attribute pattern)
    title_occurrences = doc.count(expected_title)

    # The cover uses a single clean <w:t>...title...</w:t> run
    # Plus possibly a mention in 附件 or solution section
    cover_count = len(re.findall(
        r'<w:t[^>]*>' + re.escape(expected_title) + r'</w:t>', doc
    ))
    if cover_count == 0:
        raise RuntimeError(
            f"Title '{expected_title}' not found in any <w:t> in document.xml"
        )
    if cover_count > 2:
        print(f"[verify] WARNING: title appears as <w:t> text {cover_count} times. "
              f"Check for unintended cover duplication.")
    if title_occurrences > cover_count:
        # Title text also appears in other contexts (e.g. escaped &lt; or attribute)
        # This is OK
        pass

    # XML validity
    try:
        ET.fromstring(doc)
    except ET.ParseError as e:
        raise RuntimeError(f"document.xml is not valid XML: {e}")

    print(f"[verify] OK — title: {cover_count}x in <w:t>, "
          f"text occurrences: {title_occurrences}x, "
          f"XML valid, {len(doc):,} bytes")


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════

def load_content(source: str) -> dict:
    """Load content from JSON or .py file."""
    if not os.path.exists(source):
        raise FileNotFoundError(source)
    if source.endswith(".json"):
        with open(source, "r", encoding="utf-8") as f:
            return json.load(f)
    if source.endswith(".py"):
        # Import as a module
        import importlib.util
        spec = importlib.util.spec_from_file_location("user_content", source)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "CONTENT"):
            raise ValueError(f"{source} must define CONTENT = {...}")
        return mod.CONTENT
    raise ValueError(f"Unsupported content format: {source} (use .json or .py)")


def main():
    parser = argparse.ArgumentParser(
        description="基于云和恩墨故障处理报告模板生成 Word 故障分析报告"
    )
    parser.add_argument("--content", "-c", required=True,
                        help="内容数据源（.json 或 .py 文件）")
    parser.add_argument("--output", "-o", required=True,
                        help="输出 .docx 路径")
    parser.add_argument("--template", "-t", default=None,
                        help="模板路径（默认使用 skill 内置模板）")
    args = parser.parse_args()

    content = load_content(args.content)
    out = build_report(content, args.output, template_path=args.template)
    print(f"[OK] 报告已生成: {out}")


if __name__ == "__main__":
    main()
