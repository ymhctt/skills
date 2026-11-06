---
name: enmotech-fault-report
description: 基于云和恩墨「故障处理报告模板」生成 Word (.docx) 故障分析报告。当用户需要根据已有的故障分析结果，按照恩墨标准格式输出
  Word 故障处理报告时使用本 Skill。输入为结构化内容（JSON 或 Python dict），输出为符合恩墨模板格式的 .docx
  文件。自动处理模板的封面标题、章节结构、页脚署名等细节，避免常见错误（首页标题重复、章节错位、页脚乱码等）。触发关键词：恩墨故障报告、云和恩墨报告、故障分析报告
  Word、故障分析报告 docx、生成故障处理报告、按模板生成故障报告、Enmotech 报告、Enmotech fault report。
allowed-tools: null
agent_created: true
---

# enmotech-fault-report

根据已完成的故障分析结果，按云和恩墨「故障处理报告」标准模板生成 Word 格式报告。

## 适用场景

- 客户要求按恩墨模板输出故障处理报告
- 已有 oracle_analyze / awr-word-report / db-inspection-report 等其他 Skill 生成的故障分析结论，需要 Word 版交付物
- 其他任何需要按"背景概述 / 故障分析 / 根本解决方案及建议 / 其他 / 附件"5 章结构输出故障分析报告的场景

## 模板说明

- 模板文件：`assets/enmotech_fault_report_template.docx`（已内置）
- 模板结构（不可修改）：
  - **封面**：标题 + 编制人 / 审批人 / 日期 + ENMOTECH logo + 公司版权
  - **目录**：自动生成的 TOC 字段（Word 打开后右键「更新域」同步）
  - **正文 5 章**（H1）：
    1. 背景概述
    2. 故障分析
       - 2.1 故障现象（H2）
       - 2.2 故障根源（H2）
       - 2.3 故障处置（H2）
    3. 根本解决方案及建议
    4. 其他
    5. 附件
  - **页脚**：云和恩墨公司版权 + 页码（X / Y）

## 工作流程

### 步骤 1：确认输入内容

需要从对话历史、相关 Skill 输出或用户提供的内容中提取/组装结构化数据。**核心字段**：

```json
{
  "title": "报告封面主标题（必填）",
  "background": ["背景概述段1", "段2", ...],
  "phenomenon": ["故障现象段1", "code:日志片段", "段2", ...],
  "root_cause": ["故障根源段1", "段2", ...],
  "action": ["故障处置段1", "段2", ...],
  "solution": ["根本解决建议段1", "bold:【P0 高】xxx", "段2", ...],
  "other": ["其他建议段1", "段2", ...],
  "attachments": ["附件1：xxx", "附件2：xxx", ...],
  "footer_source": "可选：页脚署名归口文字"
}
```

**段落内的特殊前缀语法**（在字符串中识别）：
| 前缀 | 效果 | 示例 |
|------|------|------|
| `code:` | 整段渲染为等宽代码块（10pt Consolas） | `"code:ORA-00600 [1234]\nORA-07445..."` |
| `table:` | 多行多列表格，首行为表头 | `"table:列1\|列2\n值1\|值2"` |
| `h3:` | H3 小节标题（加粗体 a5） | `"h3:子标题"` |
| `bold:` | 加粗正文 | `"bold:【P0 高】紧急事项"` |
| 普通文本 | a5 正文（首行缩进 24pt） | `"这是普通段落..."` |

也可以用 dict 形式表达（更显式）：
```python
{"type": "code", "text": "日志片段..."}
{"type": "table", "rows": [["列1","列2"],["v1","v2"]], "widths": [3000, 5000]}
{"type": "h3", "text": "子标题"}
{"type": "p", "text": "...", "bold": true}
```

### 步骤 2：写出内容文件

将内容保存为 `.json` 或 `.py` 文件，**放在工作目录**（如 `WorkBuddy/<workspace>/` 下）。

**方式 A：JSON 文件**（最简单）
```json
{
  "title": "XX 系统 RAC 节点驱逐故障分析报告",
  "background": ["...", "..."],
  ...
}
```

**方式 B：Python 文件**（适合需要表达复杂结构如表格 dict 时）
```python
CONTENT = {
    "title": "...",
    "background": ["...", "..."],
    "phenomenon": [
        "故障时段 alert 日志：",
        {"type": "code", "text": "ORA-00600: ..."},
        {"type": "table", "rows": [["时间", "事件"], ["18:01:25", "TX timeout"]]},
        "关键异常分析..."
    ],
    ...
}
```

### 步骤 3：执行生成

```bash
# 默认使用内置模板
/usr/bin/python3 /vol1/dsh/lihua/.agents/skills/enmotech-fault-report/scripts/build_report.py \
  --content /path/to/content.json \
  --output /path/to/output_report.docx

# 使用自定义模板（必须是同款 Enmotech 模板变体）
/usr/bin/python3 /vol1/dsh/lihua/.agents/skills/enmotech-fault-report/scripts/build_report.py \
  --content /path/to/content.py \
  --output /path/to/output_report.docx \
  --template /path/to/custom_template.docx
```

生成后脚本会自动验证：
- 标题在封面只出现 1 次（不会重复）
- 5 个 H1 章节完整
- 3 个 H2 子章节完整（在故障分析章下）
- document.xml 是合法 XML

### 步骤 4：交付报告

用 `present_files` 把生成的 .docx 交给用户。**附带简明摘要**：
- 报告标题
- 包含的章节（1. 背景概述 / 2. 故障分析 / 3. 根本解决方案 / 4. 其他 / 5. 附件）
- 主要发现（≤ 5 条）
- 建议优先行动项（≤ 5 条）

## Python API（高级用法）

```python
import sys
sys.path.insert(0, "/vol1/dsh/lihua/.agents/skills/enmotech-fault-report/scripts")
from build_report import build_report

build_report(
    content={
        "title": "...",
        "background": [...],
        ...
    },
    output_path="/path/to/output.docx",
    # template_path="/path/to/template.docx",  # 可选，默认用内置
)
```

## 内置最佳实践（已自动处理）

1. **首页标题不重复**：模板原设计是「占位符 **** + 固定后缀」两段式，本 Skill 自动合并为单个 run，避免双标题 BUG
2. **章节结构匹配模板**：5 个 H1 章节 + 3 个 H2 子章节严格按模板顺序
3. **代码块保留等宽字体**：用 Consolas + 宋体回退，保留原始缩进
4. **表格自适应列宽**：默认等宽分布，可指定 width（dxa 单位）
5. **页脚智能添加归属**：`footer_source` 字段会作为 9pt 灰色小字追加到页脚末尾
6. **XML 格式校验**：打包前会用 ElementTree 验证 document.xml 合法

## 常见错误与规避

| 错误 | 原因 | 规避 |
|------|------|------|
| 首页标题重复两次 | 模板两段式 title 被分别替换 | 脚本已自动用单 run 替换整段 |
| 章节错位 | 模板 H1 标题被分多个 run | 脚本按 `pStyle="1"` 整体段落识别 |
| 目录显示旧标题 | TOC 字段缓存 | 用户打开 Word 后右键「更新域」即可 |
| 修改了模板章节名 | 用户要求"标题不可修改" | Skill 严格保留模板原章节名，仅替换正文内容 |
| 嵌入图片 | 当前 Skill 不支持图片 | 把图片放在 附件 章节以"附件N：xxx.png"形式引用 |

## 扩展点

- **不同模板变体**：用 `--template` 参数指定其他 Enmotech 模板（巡检简版/详版等），但需要先确认该模板是否使用相同的 pStyle 体系
- **多模板支持**：可复制 `build_report.py` 适配其他 pStyle 体系（如 pStyle "10" 的 TOC 模式）
- **HTML 报告联动**：可与 oracle_analyze / awr-word-report 的 HTML 输出联动，把 HTML 内容转写为 docx 内容

## 注意事项

- 模板的所有 XML 样式（styles.xml）、关系（_rels/）、页眉页脚（header1.xml/footer1.xml）都从内置模板继承，**不要修改**
- 报告的 Word 兼容性目标：MS Word 2010+ / WPS / LibreOffice（基于 pStyle 标准）
- 中文段落使用宋体（东亚 fallback 微软雅黑），代码块使用 Consolas
- 输出 docx 默认约 60-100 KB（视正文长度）

## 参考资源

- `references/template_structure.md` — Enmotech 模板的 OOXML 内部结构详解
- `assets/enmotech_fault_report_template.docx` — 内置模板（二进制）
- `scripts/build_report.py` — 主生成脚本
- `scripts/example_rac_eviction.json` — 完整示例（2026-06-30 RAC 节点驱逐故障分析报告）
