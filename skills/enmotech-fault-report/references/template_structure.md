# Enmotech 故障处理报告模板 - OOXML 内部结构详解

本文档解释云和恩墨「故障处理报告模板」`enmotech_fault_report_template.docx` 的内部结构。
供本 Skill 维护者深入理解模板和扩展时使用。

## 文件清单（OOXML Package Layout）

```
enmotech_fault_report_template.docx (ZIP)
├── [Content_Types].xml        ← 内容类型声明
├── _rels/.rels                ← 顶层关系
├── docProps/
│   ├── app.xml                ← 应用元数据
│   ├── core.xml               ← 核心属性（作者/标题/创建时间）
│   └── custom.xml             ← 自定义属性
└── word/
    ├── document.xml           ← 文档主体（核心）
    ├── styles.xml             ← 样式定义
    ├── numbering.xml          ← 编号定义
    ├── settings.xml           ← 文档设置
    ├── fontTable.xml          ← 字体表
    ├── webSettings.xml        ← Web 设置
    ├── header1.xml            ← 页眉（ENMOTECH logo + 公司名）
    ├── footer1.xml            ← 页脚（公司版权 + 页码）
    ├── _rels/document.xml.rels ← document 的关系
    ├── media/image1.png       ← 嵌入图片（页眉 logo）
    └── theme/theme1.xml       ← Office 主题
```

## 关键样式（pStyle 值）

| pStyle | 用途 | 字号/格式 |
|--------|------|----------|
| `1` | H1 章节标题 | 36 half-point = 18pt 宋体 加粗 |
| `2` | H2 子章节标题 | 32 half-point = 16pt 宋体 加粗 |
| `3` | H3 小节标题（备用） | 32 half-point = 16pt 宋体 加粗 |
| `10` | TOC 目录条目 | 28 half-point = 14pt |
| `a5` | 正文段落 | 默认 1.5 倍行距 + 首行缩进 480 dxa |
| `a8` | 页眉页脚 | 居中或居右 |

注：Word 用 half-point 存储字号，所以 `<w:sz w:val="36"/>` 表示 18pt 字号。

## 封面标题的两段式设计（重要陷阱）

模板封面标题用两个相邻 `<w:r>` 块渲染：

```xml
<w:p ...>
  <w:pPr><w:ind w:right="663"/><w:jc w:val="center"/>...</w:pPr>
  <w:r><w:rPr>...</w:rPr><w:t>****</w:t></w:r>          ← 占位符
  <w:r><w:rPr>...</w:rPr><w:t>业务系统故障分析报告</w:t></w:r>  ← 固定后缀
</w:p>
```

**陷阱**：用搜索替换分别替换这两个 `<w:t>` 都会把每段都替换成完整标题，导致首页显示两次。

**正确做法**（`fix_title_paragraph` 函数已实现）：
1. 找到包含 `****` 的整个 `<w:p>...</w:p>` 段落
2. 保留 `pPr`（段落属性）
3. 用单个 `<w:r>` 替换两个 run，新 `<w:t>` 包含完整标题

## H1 章节的多 run 渲染

模板的 H1 章节标题在 OOXML 中也是分多个 run（用于显示粗体+不同字体细节）：

```xml
<w:p ...><w:pPr><w:pStyle w:val="1"/>...</w:pPr>
  <w:r><w:rPr>宋体 18pt 加粗</w:rPr><w:t>故障</w:t></w:r>
  <w:r><w:rPr>宋体 18pt 加粗</w:rPr><w:t>分析</w:t></w:r>
</w:p>
```

`故障处置` H2 也类似：`故障` + `处置`。

**重要**：H1 段落的判定是「包含 `pStyle="1"` 的整段」，不依赖文本匹配。

## 模板章节顺序（5 H1 + 3 H2）

```
H1 #0  背景概述
   H1 段落 → N 个 a5 占位段落
H1 #1  故障分析
   H2 故障现象
   H2 故障根源
   H2 故障处置
H1 #2  根本解决方案及建议
H1 #3  其他
H1 #4  附件
   ↑ 最后 H1 = 附件
   ↑ 紧接 _GoBack bookmark → 段落结束
   ↑ 之后是 <w:sectPr>（节属性：页边距、纸张方向等）
```

## 目录（TOC）字段

模板的目录使用 TOC 字段：

```xml
<w:p>
  <w:pPr><w:pStyle w:val="TOC-Heading"/></w:pPr>
  <w:r><w:t>目录</w:t></w:r>
</w:p>
<w:p>
  <w:r><w:fldChar w:fldCharType="begin"/></w:r>
  <w:r><w:instrText xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText></w:r>
  <w:r><w:fldChar w:fldCharType="separate"/></w:r>
  <w:r><w:t>1. 故障概述  5</w:t></w:r>  ← 缓存文本（手动生成时静态）
  ...
  <w:r><w:fldChar w:fldCharType="end"/></w:r>
</w:p>
```

**注意**：模板里的 TOC 缓存文本是手动写好的（旧版本"1. 故障概述"），不是用 Word 自动生成的。

**打开 Word 后用户需要手动**：右键目录 → "更新域" / "Update Field"，TOC 才会同步到当前 H1 实际标题。

## 页脚（footer1.xml）

模板的页脚结构：

```xml
<w:ftr>
  <w:sdt>... 版权段落（多个 run 拼出 "云和恩墨（北京）信息技术有限公司 版权所有，严禁翻印  3 / 4"）...</w:sdt>
  <w:p>（空段落，撑出边距）</w:p>
</w:ftr>
```

**页脚的 PAGE / NUMPAGES 是域**，Word 打开时会自动计算并显示。

## 关键搜索锚点

| 用途 | 搜索文本 |
|------|----------|
| 找到封面标题位置 | `****` 或 `业务系统故障分析报告` |
| 找到第一个 H1 段 | 含 `pStyle="1"` 的 `<w:p>` |
| 找到正文结束位置 | `<w:bookmarkStart w:id="8" w:name="_GoBack"/>` |
| 找到 footer 位置 | `word/footer1.xml` 中的 `</w:ftr>` |
| 找到所有 H1 章节 | 5 个 `pStyle="1"` 段落（标题/背景/故障分析/根本解决方案/其他/附件） |

## 实际修改本模板的风险点

| 操作 | 风险 | 建议 |
|------|------|------|
| 修改 styles.xml 的 pStyle 定义 | 影响所有章节的视觉 | 改 styles.xml 后必须用 Word 打开验证 |
| 删除页眉的 image1.png | 页眉 logo 缺失 | 删除时同步删除 _rels 和 [Content_Types] 的引用 |
| 修改 footer1.xml 的 PAGE 域 | 页码显示错乱 | 用域编辑，不要替换为静态文本 |
| 替换 document.xml 的 H1 段 | 破坏书签锚点 | 替换时保留 `<w:bookmarkStart/End>` |
| 用 zip 重新打包时压缩级别 | 某些 Word 版本对压缩敏感 | 用 `zipfile.ZIP_DEFLATED` 标准级别 |

## 验证清单（修改后必做）

- [ ] document.xml 是合法 XML（`xml.etree.ElementTree.fromstring`）
- [ ] 所有 H1 段（5 个）pStyle="1" 且非空
- [ ] 故障分析章下 H2 段（3 个）pStyle="2" 且非空
- [ ] 封面标题文本恰好出现 1 次（cover）+ ≤ N 次（正文引用）
- [ ] Word 打开后页眉 logo 正常显示
- [ ] Word 打开后页脚页码正确
- [ ] Word 打开后目录可「更新域」同步
