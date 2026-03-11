# 压缩策略（Compression Policy）

本文件定义 paper-report 汇报稿中**允许压缩**的三个章节的具体执行规则。

## 压缩白名单

**仅以下三个章节允许压缩**，其余所有章节为高保真（见 `fidelity-rules.md`）：

1. Abstract（摘要）
2. Introduction（引言）
3. Experiment Conclusion（实验结论性段落）

任何不在白名单内的章节，一个字都不能删。

---

## 1. Abstract 压缩规则

### 压缩幅度
- 目标篇幅：原文的 **40%-60%**

### 必须保留
- 核心问题/任务名称
- 方法名称（如有专有名词）
- 关键数值结果（如"在 X 数据集上达到 Y% 的准确率"）
- SOTA 声明（如有）

### 可以省略
- 研究领域背景铺垫（"近年来，X 领域受到广泛关注…"）
- 泛化性、应用前景等展望性表述
- 重复出现在 Introduction 中的内容

### 示例

**原文 Abstract**（120 词）：
> In recent years, multimodal learning has received significant attention... We propose MultiNet, a novel framework... Our method achieves 92.3% accuracy on MS-COCO and 88.7% on VQA v2.0, establishing new state-of-the-art results. Furthermore, we demonstrate broad applicability across various downstream tasks...

**压缩版**（约 50 词）：
> 本文提出 MultiNet，一种多模态学习框架（Multimodal Learning Framework）。在 MS-COCO 上达到 92.3% 准确率，VQA v2.0 上达到 88.7%，均为当前最优（SOTA）。

---

## 2. Introduction 压缩规则

### 压缩幅度
- 目标篇幅：原文的 **30%-50%**（Introduction 通常是最可压缩的章节）

### 必须保留
- **问题定义**：本文要解决什么问题
- **研究动机**：为什么现有方法不够好（核心痛点，1-2 句即可）
- **贡献声明**：本文的明确贡献点列表（通常在 Introduction 末尾）
- **方法概述**：方法的一句话描述（如有）

### 可以省略
- 详细的领域发展历史（如 Related Work 独立成章）
- 过渡性段落（"The rest of this paper is organized as follows…"）
- 修辞性开头（"The rapid advancement of deep learning…"）
- 与 Related Work 章节重复的文献回顾
- 详细的方法预览（Method 章节会完整展开）

### 处理建议
- 如 Introduction 包含对前人工作的详细讨论且 Related Work 为独立章节 → Introduction 中的文献回顾可大幅压缩
- 如 Introduction 包含问题的数学形式化定义 → 保留该定义（属于 Problem Definition 范畴）
- 贡献点列表**必须完整保留**，不可省略任何一条

---

## 3. Experiment Conclusion 压缩规则

### 适用范围
- Experiments 章节**末尾**的总结性段落（通常是最后 1-2 段）
- **不包括**：具体实验结果描述、消融实验分析、误差分析——这些属于高保真内容

### 压缩幅度
- 目标篇幅：原文的 **50%-70%**（压缩幅度最小，因为结论重要）

### 必须保留
- 核心数值结论（最佳方法名、关键提升幅度）
- 关键发现（如"X 组件贡献最大"、"在 Y 场景下优势最明显"）
- 与 SOTA 的对比结论

### 可以省略
- 对前面已详细展示的结果的重复性总结
- "实验充分验证了…" 等套话
- 泛化到其他场景的推测性讨论

---

## 边界情况处理

### Q: 某段落横跨"可压缩"和"高保真"内容怎么办？
A: 拆分处理。属于高保真的部分完整保留，属于可压缩的部分按规则压缩。

### Q: Conclusion 章节是否可压缩？
A: **否**。Conclusion 不在白名单内。但如果 Conclusion 中有明显重复 Introduction 的内容，可用 `[与引言重复，略]` 标注后省略该重复段落。

### Q: Discussion 章节是否可压缩？
A: **否**。Discussion 为高保真章节，通常包含重要的分析和洞察。

### Q: 压缩后发现信息丢失怎么办？
A: 宁可少压缩，不可丢信息。如果不确定某内容是否重要，**保留**。

---

## 压缩校验

生成汇报稿后，检查以下项目：

- [ ] 仅白名单内的三个章节发生了压缩？
- [ ] Abstract 保留了方法名和关键数值？
- [ ] Introduction 保留了完整的贡献声明列表？
- [ ] Experiment Conclusion 保留了核心数值结论？
- [ ] 压缩后的内容仍然准确（无因省略导致的歧义）？
- [ ] 未出现对 Method/Ablation/Limitations 的任何压缩？
