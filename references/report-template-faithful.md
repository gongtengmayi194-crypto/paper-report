# {{paper_title}} — 论文汇报稿

> 📄 **论文信息**
> - **标题：** {{paper_title}}
> - **作者：** {{authors}}
> - **发表：** {{venue}} {{year}}
> - **链接：** [论文原文]({{paper_url}})
> - **汇报类型：** 结构保真汇报（仅 Abstract/Introduction/Experiment Conclusion 压缩）
> - **生成时间：** {{generated_date}}

---

## 📑 目录

<!-- INSTRUCTION: 根据 sections.json 中的实际章节自动生成目录，使用 Markdown 锚链接 -->
1. [论文基本信息](#论文基本信息)
2. [摘要（压缩版）](#摘要压缩版)
3. [引言（压缩版）](#引言压缩版)
4. [问题定义与任务设定](#问题定义与任务设定)
5. [方法](#方法)
6. [实验设置与主结果](#实验设置与主结果)
7. [消融与分析](#消融与分析)
8. [实验结论（压缩版）](#实验结论压缩版)
9. [局限与未来工作](#局限与未来工作)
10. [关键术语与符号索引](#关键术语与符号索引)

---

## 论文基本信息

- **研究领域：** {{research_field}}
- **核心贡献：**
  <!-- INSTRUCTION: 直接列出论文声明的贡献点，使用原文表述，不做改写。每条 1-2 句。 -->
  1. {{contribution_1}}
  2. {{contribution_2}}
  3. {{contribution_3}}

---

## 摘要（压缩版）

<!-- INSTRUCTION: 
  - 此章节为**可压缩**章节，篇幅可压缩至原文 50% 左右
  - 保留：核心问题、方法名称、关键数值结果
  - 可省略：背景铺垫、泛化性讨论
  - 术语使用"中文（English）"格式
-->

{{compressed_abstract}}

---

## 引言（压缩版）

<!-- INSTRUCTION:
  - 此章节为**可压缩**章节
  - 必须保留：问题定义、研究动机的核心论点、贡献声明
  - 可省略：详细的背景综述（如 Related Work 独立成章则此处可大幅压缩）
  - 可省略：过渡性段落、修辞性开头
-->

{{compressed_introduction}}

---

## 问题定义与任务设定

<!-- INSTRUCTION:
  - 此章节为**高保真**章节，不可删减
  - 完整保留：任务形式化定义、输入/输出规范、评价指标、关键假设与约束
  - 如原文有数学定义，保留原始 LaTeX 并附符号表
-->

- **任务定义：** {{task_definition}}
- **输入：** {{inputs}}
- **输出：** {{outputs}}
- **评价指标：** {{metrics}}
- **关键假设/约束：** {{assumptions}}

---

## 方法

<!-- INSTRUCTION:
  - 此章节为**高保真**章节，核心章节，不可删减
  - 按原文子章节结构组织，保留所有子标题
  - 关键公式：保留原始 LaTeX + 编号，附简洁符号定义表
  - 架构图/流程图：使用 figure_map.json 中的实际裁剪图片嵌入
  - 图片格式：![Fig.X: caption](./images/figure_xxx.png)
  - 禁止使用文字占位符代替图片
  - 每张图下方附 1-2 句结论方向总结
  - 关键设计决策：保留原文的设计理由（为什么选 A 而非 B）
-->

### {{method_subsection_title}}

{{method_subsection_content}}

<!-- INSTRUCTION: 图表嵌入示例 -->
![Fig.{{N}}: {{caption}}](./images/{{figure_file}})
> **图 {{N}} 要点：** {{figure_conclusion_summary}}

<!-- INSTRUCTION: 公式嵌入示例 -->
$${{formula_latex}}$$

| 符号 | 含义 |
|------|------|
| ${{sym}}$ | {{sym_definition}} |

<!-- INSTRUCTION: 为 Method 的每个子章节重复以上结构 -->

---

## 实验设置与主结果

<!-- INSTRUCTION:
  - 此章节为**高保真**章节，不可删减
  - 实验设置：完整保留数据集、基线方法、超参数、训练细节
  - 主结果表：使用裁剪的表格图片嵌入，或用 Markdown 表格复刻
  - 每张结果表/图后附 1-2 句原文结论方向总结
  - 数值结果：保留原文精度（如 76.3% 不可改为"约76%"）
-->

### 实验设置

{{experiment_setup}}

### 主结果

{{main_results}}

<!-- INSTRUCTION: 嵌入结果表格图片 -->
![Table {{N}}: {{caption}}](./images/{{table_file}})
> **表 {{N}} 要点：** {{table_conclusion_summary}}

---

## 消融与分析

<!-- INSTRUCTION:
  - 此章节为**高保真**章节，不可删减
  - 消融实验：每个变体说明去掉/修改了什么，保留数值结果
  - 分析实验：可视化结果、误差分析等完整保留
  - 图表：使用实际裁剪图片嵌入
-->

{{ablation_and_analysis}}

---

## 实验结论（压缩版）

<!-- INSTRUCTION:
  - 此章节为**可压缩**章节
  - 保留：核心数值结论（最佳方法、最大提升幅度、关键发现）
  - 可省略：重复性总结、泛化讨论
  - 关键数值必须精确保留
-->

{{compressed_experiment_conclusion}}

---

## 局限与未来工作

<!-- INSTRUCTION:
  - 此章节为**高保真**章节，不可删减
  - 完整保留作者声明的所有局限性
  - 完整保留作者提出的未来方向
  - 如原文无独立局限章节，从 Conclusion 中提取相关内容
-->

{{limitations_and_future_work}}

---

## 关键术语与符号索引

<!-- INSTRUCTION:
  - 汇总全文核心术语与数学符号
  - 格式：术语首列中文，括号内英文原文
  - 符号列出含义与首次出现位置
  - 此表用于快速查阅，不做教学化解释
-->

| 术语/符号 | 含义 | 首次出现 |
|-----------|------|----------|
| {{term_cn}}（{{term_en}}） | {{meaning}} | §{{section}} |

---

> 📝 本汇报稿由 paper-report 生成 | 类型：结构保真汇报
> 仅 Abstract / Introduction / Experiment Conclusion 三处做了有限压缩，其余章节忠实于原文。
