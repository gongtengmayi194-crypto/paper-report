# paper-report skill

`paper-report` 是一个面向学术组会/读书会场景的技能，用于生成高保真论文汇报稿（Markdown）。

## 目标

- 忠实原文结构和技术细节
- 仅允许压缩 `Abstract`、`Introduction`、`Experiment Conclusion`
- 图表必须使用实际裁剪 PNG 嵌入
- 保留原始 LaTeX 公式与关键符号定义
- 全文不保留文献交叉引用编号（如 `[13]`、`[1,2]`）
- 输出文件名与一级标题一致：`论文阅读 ｜ 年份 期刊 ｜ 英文题目.md`
- 默认导出为单文件分发版：`论文阅读 ｜ 年份 期刊 ｜ 英文题目.md`

## 目录结构

```text
.
├── SKILL.md
├── references/
│   ├── compression-policy.md
│   ├── fidelity-rules.md
│   └── report-template-faithful.md
└── scripts/
    ├── validate_fidelity.py
    └── embed_images_single_md.py
```

## 依赖

该 skill 复用 `paper-reader` 的脚本，建议先安装：

```bash
pip install PyMuPDF>=1.23.0 pdfplumber>=0.10.0 Pillow
```

## 使用流程

1. 使用 `pdf_to_sections.py` 解析章节
2. 使用 `extract_figures.py` 裁剪图表
3. 使用 `extract_formulas.py` 提取公式
4. 按 `references/` 规则生成 `论文阅读 ｜ 年份 期刊 ｜ 英文题目.md`
5. 运行 `scripts/validate_fidelity.py` 做保真度校验
6. 运行 `scripts/embed_images_single_md.py` 原位内嵌图片（输入输出同一路径）

## 校验命令

```bash
python scripts/validate_fidelity.py <report.md> <sections.json> <figure_map.json>
```

当输出为 `0 FAIL` 时即通过。

## 单文件导出命令

```bash
python scripts/embed_images_single_md.py "论文阅读 ｜ 年份 期刊 ｜ 英文题目.md" "论文阅读 ｜ 年份 期刊 ｜ 英文题目.md"
```

体积优化（对已内嵌 data URI 的文档再次压缩）：

```bash
python scripts/embed_images_single_md.py "论文阅读 ｜ 年份 期刊 ｜ 英文题目.md" "论文阅读 ｜ 年份 期刊 ｜ 英文题目.md" --compress --process-data-uri --max-width 1400 --jpeg-quality 80
```
