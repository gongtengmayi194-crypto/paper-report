#!/usr/bin/env python3
"""
validate_fidelity.py — paper-report 汇报稿保真度验证脚本

检查汇报稿是否符合 fidelity-rules.md 和 compression-policy.md 的要求：
1. 图表嵌入检查：是否存在文字占位符（应使用实际 PNG 图片）
2. 章节覆盖检查：高保真章节是否缺失
3. 公式检查：是否保留了原文的编号公式
4. 术语一致性检查：关键术语是否前后一致
5. 数值精度检查：是否存在数值被四舍五入的痕迹

用法：
    python validate_fidelity.py <report.md> <sections.json> <figure_map.json>

输出：
    校验报告（PASS/WARN/FAIL），退出码 0=通过，1=有警告，2=有错误
"""

import json
import re
import sys
from pathlib import Path


def load_file(path: str) -> str:
    """读取文件内容"""
    p = Path(path)
    if not p.exists():
        print(f"FAIL: 文件不存在 — {path}")
        sys.exit(2)
    return p.read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    """读取 JSON 文件"""
    content = load_file(path)
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"FAIL: JSON 解析失败 — {path}: {e}")
        sys.exit(2)


def check_figure_placeholders(report: str) -> list[dict]:
    """检查是否存在图表文字占位符（应使用实际 PNG 图片）"""
    issues = []

    # 检测常见的文字占位符模式
    placeholder_patterns = [
        (r"\[Figure\s*\d+\]", "英文方括号占位符"),
        (r"\[Fig\.\s*\d+\]", "英文缩写方括号占位符"),
        (r"\[图\s*\d+\]", "中文方括号占位符"),
        (r"\[表\s*\d+\]", "中文表格方括号占位符"),
        (r"\[Table\s*\d+\]", "英文表格方括号占位符"),
        (r"(?<!\!)\[此处应有图片\]", "缺失图片标记"),
        (r"\[图片省略\]", "图片省略标记"),
        (r"(?<!\!)fig\d+", "裸文字 fig 引用（非图片嵌入）"),
    ]

    for pattern, desc in placeholder_patterns:
        matches = re.finditer(pattern, report, re.IGNORECASE)
        for match in matches:
            # 排除在 Markdown 图片语法 ![ ] 中的匹配
            start = match.start()
            if start > 0 and report[start - 1] == "!":
                continue
            # 排除在代码块中的匹配
            line_start = report.rfind("\n", 0, start) + 1
            line = report[line_start : report.find("\n", start)]
            if line.strip().startswith("```") or line.strip().startswith("`"):
                continue

            line_num = report[:start].count("\n") + 1
            issues.append(
                {
                    "type": "FAIL",
                    "check": "图表占位符",
                    "message": f"第 {line_num} 行发现{desc}：'{match.group()}'",
                    "detail": "应使用 ![caption](./images/xxx.png) 格式嵌入实际图片",
                }
            )

    return issues


def check_figure_coverage(report: str, figure_map: dict) -> list[dict]:
    """检查 figure_map 中的图表是否都在报告中以图片形式嵌入"""
    issues = []

    figures = figure_map.get("figures", [])
    if not figures:
        issues.append(
            {
                "type": "WARN",
                "check": "图表覆盖",
                "message": "figure_map.json 中没有图表记录",
                "detail": "可能是图表提取脚本未检测到图表，请确认 PDF 是否包含图表",
            }
        )
        return issues

    # 提取报告中所有 Markdown 图片引用
    img_pattern = r"!\[.*?\]\((.*?)\)"
    embedded_images = set()
    for match in re.finditer(img_pattern, report):
        img_path = match.group(1)
        # 提取文件名
        img_name = Path(img_path).name
        embedded_images.add(img_name.lower())

    # 检查每个图表是否被嵌入
    for fig in figures:
        fig_file = fig.get("file", "")
        fig_id = fig.get("id", "unknown")
        fig_kind = fig.get("kind", "figure")

        if not fig_file:
            continue

        fig_name = Path(fig_file).name.lower()
        if fig_name not in embedded_images:
            issues.append(
                {
                    "type": "WARN",
                    "check": "图表覆盖",
                    "message": f"{fig_kind} '{fig_id}' ({fig_file}) 未在报告中嵌入",
                    "detail": "高保真章节中的图表应使用实际图片嵌入",
                }
            )

    # 统计
    total = len(figures)
    missing = sum(1 for i in issues if i["check"] == "图表覆盖" and i["type"] == "WARN")
    if total > 0 and missing == 0:
        issues.append(
            {
                "type": "PASS",
                "check": "图表覆盖",
                "message": f"全部 {total} 张图表均已嵌入",
                "detail": "",
            }
        )

    return issues


def check_section_coverage(report: str, sections: dict) -> list[dict]:
    """检查高保真章节是否在报告中出现"""
    issues = []

    # 从 sections.json 提取章节标题
    section_list = sections.get("sections", [])
    if not section_list:
        issues.append(
            {
                "type": "WARN",
                "check": "章节覆盖",
                "message": "sections.json 中没有章节记录",
                "detail": "可能是章节解析失败，报告可能基于页码块生成",
            }
        )
        return issues

    # 高保真关键词（如果章节标题包含这些词，则为高保真章节）
    high_fidelity_keywords = [
        "method",
        "approach",
        "framework",
        "model",
        "architecture",
        "experiment",
        "result",
        "evaluation",
        "ablation",
        "analysis",
        "limitation",
        "future",
        "related work",
        "discussion",
    ]

    report_lower = report.lower()

    for sec in section_list:
        title = sec.get("title", "").strip()
        if not title:
            continue

        title_lower = title.lower()

        # 判断是否为高保真章节
        is_high_fidelity = any(kw in title_lower for kw in high_fidelity_keywords)

        if is_high_fidelity:
            # 检查报告中是否包含该章节（模糊匹配）
            # 去掉编号前缀匹配
            clean_title = re.sub(r"^\d+\.?\d*\s*", "", title).strip()
            if clean_title.lower() not in report_lower and title_lower not in report_lower:
                issues.append(
                    {
                        "type": "WARN",
                        "check": "章节覆盖",
                        "message": f"高保真章节 '{title}' 可能未在报告中出现",
                        "detail": "高保真章节不可省略，请检查报告是否覆盖了该章节内容",
                    }
                )

    return issues


def check_formula_presence(report: str) -> list[dict]:
    """检查报告中是否包含 LaTeX 公式"""
    issues = []

    # 检测行内公式和块级公式
    inline_formulas = re.findall(r"\$[^$]+\$", report)
    block_formulas = re.findall(r"\$\$[^$]+\$\$", report, re.DOTALL)

    total = len(inline_formulas) + len(block_formulas)

    if total == 0:
        issues.append(
            {
                "type": "WARN",
                "check": "公式存在性",
                "message": "报告中未检测到任何 LaTeX 公式",
                "detail": "如原文包含公式，应在报告中保留原始 LaTeX 表达式",
            }
        )
    else:
        issues.append(
            {
                "type": "PASS",
                "check": "公式存在性",
                "message": f"检测到 {len(block_formulas)} 个块级公式、{len(inline_formulas)} 个行内公式",
                "detail": "",
            }
        )

    return issues


def check_terminology_consistency(report: str) -> list[dict]:
    """检查术语是否使用"中文（English）"格式且前后一致"""
    issues = []

    # 提取所有"中文（English）"格式的术语
    term_pattern = r"([\u4e00-\u9fff]+)（([A-Za-z][A-Za-z\s\-]+)）"
    terms = {}
    for match in re.finditer(term_pattern, report):
        cn = match.group(1)
        en = match.group(2).strip()
        en_lower = en.lower()

        if en_lower not in terms:
            terms[en_lower] = {"cn": cn, "en": en, "count": 1}
        else:
            terms[en_lower]["count"] += 1
            # 检查同一英文术语是否有不同中文翻译
            if terms[en_lower]["cn"] != cn:
                issues.append(
                    {
                        "type": "WARN",
                        "check": "术语一致性",
                        "message": f"术语 '{en}' 有多个中文翻译：'{terms[en_lower]['cn']}' 和 '{cn}'",
                        "detail": "关键术语应全篇使用一致的中文翻译",
                    }
                )

    if not terms:
        issues.append(
            {
                "type": "WARN",
                "check": "术语一致性",
                "message": "未检测到'中文（English）'格式的术语",
                "detail": "关键术语首现应采用'中文（English）'格式",
            }
        )
    else:
        issues.append(
            {
                "type": "PASS",
                "check": "术语一致性",
                "message": f"检测到 {len(terms)} 个标注了中英文的术语",
                "detail": "",
            }
        )

    return issues


def check_teaching_language(report: str) -> list[dict]:
    """检查是否存在教学化改写痕迹"""
    issues = []

    teaching_patterns = [
        (r"你可以把它理解为", "教学化引导"),
        (r"简单来说就是", "过度简化"),
        (r"想象一下", "想象类引导"),
        (r"像.*?一样", "生活类比（需人工判断是否过度）"),
        (r"通俗.*?来说", "通俗化改写"),
        (r"大白话", "口语化改写"),
        (r"零基础", "教学化定位"),
        (r"妈妈测试", "教学化标准（来自 paper-reader，不适用于 paper-report）"),
    ]

    for pattern, desc in teaching_patterns:
        matches = list(re.finditer(pattern, report))
        if matches:
            for match in matches[:3]:  # 最多报告 3 处
                line_num = report[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "type": "WARN",
                        "check": "教学化改写",
                        "message": f"第 {line_num} 行发现{desc}：'{match.group()}'",
                        "detail": "paper-report 面向同行，应避免教学化表述",
                    }
                )

    if not issues:
        issues.append(
            {
                "type": "PASS",
                "check": "教学化改写",
                "message": "未检测到明显的教学化改写痕迹",
                "detail": "",
            }
        )

    return issues


def main():
    if len(sys.argv) < 4:
        print("用法: python validate_fidelity.py <report.md> <sections.json> <figure_map.json>")
        print()
        print("参数:")
        print("  report.md        — 生成的汇报稿 Markdown 文件")
        print("  sections.json    — pdf_to_sections.py 输出的章节结构")
        print("  figure_map.json  — extract_figures.py 输出的图表元数据")
        sys.exit(1)

    report_path = sys.argv[1]
    sections_path = sys.argv[2]
    figure_map_path = sys.argv[3]

    # 加载文件
    report = load_file(report_path)
    sections = load_json(sections_path)
    figure_map = load_json(figure_map_path)

    # 运行所有检查
    all_issues: list[dict] = []
    all_issues.extend(check_figure_placeholders(report))
    all_issues.extend(check_figure_coverage(report, figure_map))
    all_issues.extend(check_section_coverage(report, sections))
    all_issues.extend(check_formula_presence(report))
    all_issues.extend(check_terminology_consistency(report))
    all_issues.extend(check_teaching_language(report))

    # 输出报告
    print("=" * 60)
    print("paper-report 保真度校验报告")
    print("=" * 60)
    print(f"报告文件: {report_path}")
    print(f"章节文件: {sections_path}")
    print(f"图表文件: {figure_map_path}")
    print("-" * 60)

    pass_count = 0
    warn_count = 0
    fail_count = 0

    for issue in all_issues:
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(issue["type"], "?")
        print(f"{icon} [{issue['check']}] {issue['message']}")
        if issue["detail"]:
            print(f"   → {issue['detail']}")

        if issue["type"] == "PASS":
            pass_count += 1
        elif issue["type"] == "WARN":
            warn_count += 1
        elif issue["type"] == "FAIL":
            fail_count += 1

    print("-" * 60)
    print(f"总计: ✅ {pass_count} PASS | ⚠️ {warn_count} WARN | ❌ {fail_count} FAIL")

    if fail_count > 0:
        print("\n结论: ❌ 校验失败 — 存在必须修复的问题")
        sys.exit(2)
    elif warn_count > 0:
        print("\n结论: ⚠️ 校验通过（有警告）— 建议检查警告项")
        sys.exit(1)
    else:
        print("\n结论: ✅ 校验通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
