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

**输出**：`论文汇报稿.md`（单一 Markdown 文件）

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

### Phase 2: 提取图表与公式（并行）

同时运行：
1. 图表裁剪：
   ```bash
   python ~/.config/opencode/skills/paper-reader/scripts/extract_figures.py <pdf_path> <output_dir>/images/
   ```
   → 读取 `<output_dir>/images/figure_map.json`，获取每张图/表的 id、kind、file、page、caption

2. 公式提取：
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

5. 输出 `{paper-name}/论文汇报稿.md`

### Phase 4: 质量校验

运行验证脚本：
```bash
python scripts/validate_fidelity.py <output_dir>/论文汇报稿.md <output_dir>/sections.json <output_dir>/images/figure_map.json
```

校验项：
- 删减范围是否越界（仅三处可压缩）
- 图表是否全部以 PNG 嵌入（无文字占位符）
- 关键术语是否前后一致
- 公式编号是否完整

如校验失败，根据报告修复后重新校验。

## Output Structure

```
{paper-name}/
├── 论文汇报稿.md          # 最终汇报稿
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
- **MUST**: Method 与核心实验章节不做任何删减
- **MUST**: 公式保留原始 LaTeX 与编号，关键变量附符号定义
- **MUST**: 术语首现采用"中文（English）"格式，后文保持一致
- **MUST**: 每个核心结论可追溯到原文章节/图表/公式
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
- **外部脚本**（来自 paper-reader）:
  - `~/.config/opencode/skills/paper-reader/scripts/pdf_to_sections.py`
  - `~/.config/opencode/skills/paper-reader/scripts/extract_figures.py`
  - `~/.config/opencode/skills/paper-reader/scripts/extract_formulas.py`
