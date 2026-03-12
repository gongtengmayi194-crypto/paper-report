---
name: paper-report
description: >
  论文汇报稿生成（非论文阅读/教学解读）。忠实原文、少删减，仅摘要/引言/实验结论可压缩，其余高保真呈现。
  自动裁剪论文图表为 PNG 嵌入报告，保留公式与符号定义。
  触发词：论文汇报, 组会汇报, 读书会汇报, paper report, seminar report, 汇报稿, 论文报告。
  场景：学术组会/读书会，面向同行听众。
  与 paper-reader 的区别：paper-reader 是零基础教学化解读，paper-report 是忠实原文的同行汇报。
---

## Overview

生成忠实原文的 Markdown 论文汇报稿，用于学术组会/读书会汇报。

**核心原则**：
- 忠实原文结构与表述，不做教学化改写
- 仅 Abstract、Introduction、Experiment Conclusion 三处可压缩
- Method、核心实验、消融、局限等章节高保真呈现
- 图表使用实际裁剪的 PNG 图片嵌入（非文字占位符）
- 公式保留原始 LaTeX 与符号定义
- 报告开头必须放置从论文 PDF 首页面自动截取的标题截图
- 报告头部“发表”和“代码”字段必须可点击跳转（Markdown 超链接）
- 全文去除文献交叉引用标记（如 `[13]`、`[1,2]`），仅保留正文语义
- 支持导出单一 Markdown 文件（图片内嵌 base64，便于直接分发）

默认产物要求：最终交付文件必须为图片内嵌（base64）的单一 Markdown，不保留并行的非内嵌版本。

**输出**：`论文阅读 ｜ 年份 期刊 ｜ 英文题目.md`（单一 Markdown 文件，文件名与一级标题一致）

## Dependencies

复用 `paper-reader` skill 的脚本（路径：`~/.config/opencode/skills/paper-reader/scripts/`）：

```bash
pip install PyMuPDF>=1.23.0 pdfplumber>=0.10.0 Pillow
```

## Workflow

### Phase 1: 获取与解析论文

1. PDF → 直接使用；arXiv/Semantic Scholar/DOI → 通过 firecrawl 下载 PDF
2. 创建工作目录：`{paper-name}/`
3. 运行章节解析：
   ```bash
   python ~/.config/opencode/skills/paper-reader/scripts/pdf_to_sections.py <pdf_path> <output_dir>/
   ```
4. 读取 `<output_dir>/sections.json`，获取 title、authors、abstract、sections[]

### Phase 2: 提取标题截图、图表与公式（并行）

同时运行：
1. 标题截图裁剪（复用现有 `validate_fidelity.py`，不新增脚本）：
   ```bash
   python ~/.config/opencode/skills/paper-report/scripts/validate_fidelity.py extract-title <pdf_path> <output_dir>/images/title-screenshot.png
   ```
   → 将论文第一页标题区自动裁剪为 `<output_dir>/images/title-screenshot.png`

2. 图表裁剪：
   ```bash
   python ~/.config/opencode/skills/paper-reader/scripts/extract_figures.py <pdf_path> <output_dir>/images/
   ```
   → 读取 `<output_dir>/images/figure_map.json`，获取每张图/表的 id、kind、file、page、caption

3. 公式提取：
   ```bash
   python ~/.config/opencode/skills/paper-reader/scripts/extract_formulas.py <pdf_path> <output_dir>/
   ```
   → 读取 `<output_dir>/formulas.json`，获取公式的 LaTeX、位置、置信度

对 confidence="low" 且有 fallback_image 的公式，使用 `look_at` 工具视觉识别 LaTeX。

### Phase 3: 生成汇报稿

1. 读取 `references/fidelity-rules.md`（**必读**）
2. 读取 `references/compression-policy.md`（**必读**）
3. 读取 `references/report-template-faithful.md`（**必读**）
4. 按模板逐章节生成汇报稿：

**报告头部格式规则**（硬约束）：
- 一级标题格式：`论文阅读 | 年份 期刊 | 英文标题`
- 标题下方必须放置论文标题截图：`![论文标题截图](./images/title-screenshot.png)`
- 标题截图必须来自当前论文 PDF 的自动裁剪结果，不可复用其它论文截图
- “发表”字段必须使用超链接，显示文字不变但可点击跳转
- “代码”字段必须使用超链接，显示文字不变但可点击跳转
- 正文不得保留任何文献交叉引用编号（如 `[13]`、`[24,25]`）

**章节分类与处理策略**：

| 章节类型 | 处理策略 | 详见 |
|---------|---------|------|
| Abstract | 可压缩（≤50% 篇幅） | compression-policy.md |
| Introduction | 可压缩（保留问题定义与贡献声明） | compression-policy.md |
| Method / Approach | **高保真**（关键公式、图表、符号定义完整保留） | fidelity-rules.md |
| Experiments（设置与主结果） | **高保真**（实验配置、对比表、图表完整保留） | fidelity-rules.md |
| Ablation / Analysis | **高保真** | fidelity-rules.md |
| Experiment Conclusion | 可压缩（保留核心数值结论） | compression-policy.md |
| Limitations / Future Work | **高保真** | fidelity-rules.md |
| Related Work | **高保真**（除引言中已覆盖的部分） | fidelity-rules.md |

**图表嵌入规则**（硬约束）：
- **禁止**使用 `[Figure 1]`、`fig1`、`（见图1）` 等文字占位符代替图片
- **必须**使用 `figure_map.json` 中的实际裁剪图片路径
- 格式：`![Fig.X: caption](./images/figure_xxx.png)`
- 图表在对应章节**就地嵌入**，紧跟原文讨论位置
- 每张图/表下方附 1-2 句原文结论方向总结（非教学化批注）

**公式处理规则**：
- 保留原始 LaTeX，不改写数学含义
- 关键变量首次出现时给出符号定义表（简洁版，非教学化逐符号拆解）
- 公式编号与原文保持一致

5. 输出 `{paper-name}/论文阅读 ｜ 年份 期刊 ｜ 英文题目.md`（与一级标题一致）

### Phase 4: 质量校验

运行验证脚本：
```bash
python scripts/validate_fidelity.py <output_dir>/论文汇报稿.md <output_dir>/sections.json <output_dir>/images/figure_map.json
```

将 `<output_dir>/论文汇报稿.md` 替换为实际输出文件名：
`<output_dir>/论文阅读 ｜ 年份 期刊 ｜ 英文题目.md`

校验项：
- 删减范围是否越界（仅三处可压缩）
- 图表是否全部以 PNG 嵌入（无文字占位符）
- 关键术语是否前后一致
- 公式编号是否完整

如校验失败，根据报告修复后重新校验。

### Phase 5: 单文件内嵌导出（默认）

将报告中的本地图片链接内嵌为 base64，并直接覆盖最终输出文件：

```bash
python scripts/embed_images_single_md.py <input_md> <output_single_md>
```

示例：

```bash
python scripts/embed_images_single_md.py \
  "<output_dir>/论文阅读 ｜ 年份 期刊 ｜ 英文题目.md" \
  "<output_dir>/论文阅读 ｜ 年份 期刊 ｜ 英文题目.md"
```

若文档体积过大，建议在同一命令中开启压缩参数：

```bash
python scripts/embed_images_single_md.py \
  "<output_dir>/论文阅读 ｜ 年份 期刊 ｜ 英文题目.md" \
  "<output_dir>/论文阅读 ｜ 年份 期刊 ｜ 英文题目.md" \
  --compress --process-data-uri --max-width 1400 --jpeg-quality 80
```

## Output Structure

```
{paper-name}/
├── 论文阅读 ｜ 年份 期刊 ｜ 英文题目.md   # 最终汇报稿（与一级标题一致，图片已内嵌）
├── images/                 # 裁剪的图表 PNG
│   ├── figure_001.png
│   ├── figure_002.png
│   └── ...
├── figure_map.json         # 图表元数据
├── formulas.json           # 公式元数据
└── sections.json           # 章节结构
```

## Key Rules

- **MUST**: 图表使用实际裁剪的 PNG 图片嵌入，禁止文字占位符
- **MUST**: 报告开头标题截图必须由 `scripts/validate_fidelity.py extract-title` 从当前论文 PDF 自动生成
- **MUST**: Method 与核心实验章节不做任何删减
- **MUST**: 公式保留原始 LaTeX 与编号，关键变量附符号定义
- **MUST**: 术语首现采用"中文（English）"格式，后文保持一致
- **MUST**: 每个核心结论可追溯到原文章节/图表/公式
- **MUST**: 全文移除文献交叉引用标记（如 `[13]`、`[1,2,3]`）
- **MUST NOT**: 使用生活类比、大白话改写、"零基础"风格批注
- **MUST NOT**: 生成口语化讲稿或过度主观评价
- **MUST NOT**: 省略消融实验、局限性、误差分析等章节
- **MUST NOT**: 跳过图表/公式提取脚本，直接用文字描述

## Failure Handling

- **章节识别失败**：降级为基于页码块的顺序汇报，标注"章节识别不完整"
- **图表裁剪失败**：回退到 `look_at` 工具视觉识别论文页面中的图表，如仍失败则标注"图像未提取成功"并保留文字结论
- **公式解析失败**：回退为 formula_images/ 中的公式截图，附最小必要符号说明

## Resources

- **汇报稿模板**: `references/report-template-faithful.md`
- **保真规则**: `references/fidelity-rules.md`（术语、图表、公式、证据追溯）
- **压缩策略**: `references/compression-policy.md`（仅三处可压缩的执行规则）
- **验证脚本**: `scripts/validate_fidelity.py`（检查是否越权删减、图表是否嵌入）
- **标题截图提取**: `scripts/validate_fidelity.py extract-title`（自动裁剪首页标题区）
- **单文件导出**: `scripts/embed_images_single_md.py`（将图片转为 base64 内嵌）
- **外部脚本**（来自 paper-reader）:
  - `~/.config/opencode/skills/paper-reader/scripts/pdf_to_sections.py`
  - `~/.config/opencode/skills/paper-reader/scripts/extract_figures.py`
  - `~/.config/opencode/skills/paper-reader/scripts/extract_formulas.py`
