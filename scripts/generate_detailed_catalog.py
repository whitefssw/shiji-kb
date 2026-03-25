#!/usr/bin/env python3
"""
生成 ontology-v1 的详尽中文目录（基于已有索引文件）
"""

import json
import re
from pathlib import Path

def load_index():
    """加载 SKU 索引"""
    index_file = Path("kg/ontology/ontology-v1/skus/skus_index.json")
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_facts_index():
    """从 facts_index.md 提取中文描述"""
    index_file = Path("kg/ontology/ontology-v1/facts_index.md")
    descriptions = {}

    with open(index_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 匹配格式： | [sku_001](path) | 描述 |
            match = re.search(r'\| \[(sku_\d+)\].*?\| (.*?) \|', line)
            if match:
                sku_id = match.group(1)
                desc = match.group(2).strip()
                # 去掉 markdown 链接
                desc = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', desc)
                descriptions[sku_id] = desc

    return descriptions

def load_skills_index():
    """从 skills_index.md 提取中文描述"""
    index_file = Path("kg/ontology/ontology-v1/skills_index.md")
    descriptions = {}

    with open(index_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 匹配格式： | [skill_001](path) | 名称 | 描述 |
            match = re.search(r'\| \[(skill_\d+)\].*?\| (.*?) \| (.*?) \|', line)
            if match:
                sku_id = match.group(1)
                name = match.group(2).strip()
                desc = match.group(3).strip()
                descriptions[sku_id] = f"{name}：{desc}"

    return descriptions

def parse_facts_index_by_category():
    """解析 facts_index.md 的分类结构"""
    index_file = Path("kg/ontology/ontology-v1/facts_index.md")
    categories = {}
    current_category = None

    with open(index_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 匹配二级标题：## 类别名（数量）
            match = re.match(r'^## (.+?)（(\d+)）', line)
            if match:
                current_category = match.group(1)
                categories[current_category] = []
                continue

            # 匹配 SKU 行
            if current_category:
                match = re.search(r'\[(sku_\d+)\]', line)
                if match:
                    sku_id = match.group(1)
                    # 提取描述（第二个 | 和第三个 | 之间）
                    parts = line.split('|')
                    if len(parts) >= 3:
                        desc = parts[2].strip()
                        # 去掉markdown链接
                        desc = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', desc)
                        categories[current_category].append({
                            'sku_id': sku_id,
                            'description': desc
                        })

    return categories

def parse_skills_index_by_category():
    """解析 skills_index.md 的分类结构"""
    index_file = Path("kg/ontology/ontology-v1/skills_index.md")
    categories = {}
    current_category = None

    with open(index_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 匹配二级标题：## 类别名（数量）
            match = re.match(r'^## (.+?)（(\d+)）', line)
            if match:
                current_category = match.group(1)
                categories[current_category] = []
                continue

            # 匹配 SKU 行
            if current_category:
                match = re.search(r'\[(skill_\d+)\]', line)
                if match:
                    sku_id = match.group(1)
                    # 提取名称和描述（第二、三列）
                    parts = line.split('|')
                    if len(parts) >= 4:
                        name = parts[2].strip()
                        desc = parts[3].strip()
                        # 去掉markdown链接
                        name = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', name)
                        categories[current_category].append({
                            'sku_id': sku_id,
                            'name': name,
                            'description': desc
                        })

    return categories

def generate_catalog(index_data):
    """生成详尽目录"""
    facts_categories = parse_facts_index_by_category()
    skills_categories = parse_skills_index_by_category()

    lines = []
    lines.append("# Ontology v1 详尽知识目录")
    lines.append("")
    lines.append(f"本目录列出 ontology-v1 中的所有 {index_data['total_skus']} 项知识单元，每项用中文说明其内容。")
    lines.append("")
    lines.append(f"- **生成时间**: 2026-03-25")
    lines.append(f"- **总知识单元数**: {index_data['total_skus']}")
    lines.append(f"- **事实性知识**: 434 项")
    lines.append(f"- **技能知识**: 241 项")
    lines.append(f"- **关系知识**: 1 项")
    lines.append(f"- **元知识**: 1 项")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 目录")
    lines.append("")
    lines.append("### 事实性知识")
    for cat in facts_categories.keys():
        lines.append(f"- [{cat}](#{cat.replace(' ', '-')})")
    lines.append("")
    lines.append("### 技能知识")
    for cat in skills_categories.keys():
        lines.append(f"- [{cat}](#{cat.replace(' ', '-')})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 事实性知识
    lines.append("# 事实性知识（Factual SKUs）")
    lines.append("")
    lines.append("共 434 项，记录史实、人物、事件、数据等客观信息。")
    lines.append("")

    for category, skus in facts_categories.items():
        lines.append(f"## {category}")
        lines.append("")
        lines.append(f"共 {len(skus)} 项")
        lines.append("")

        for item in skus:
            lines.append(f"### {item['sku_id']}")
            lines.append(f"{item['description']}")
            lines.append("")

    # 技能知识
    lines.append("---")
    lines.append("")
    lines.append("# 技能知识（Procedural SKUs）")
    lines.append("")
    lines.append("共 241 项，提取可复用的方法、流程、策略。")
    lines.append("")

    for category, skus in skills_categories.items():
        lines.append(f"## {category}")
        lines.append("")
        lines.append(f"共 {len(skus)} 项")
        lines.append("")

        for item in skus:
            lines.append(f"### {item['sku_id']}: {item['name']}")
            lines.append(f"{item['description']}")
            lines.append("")

    # 关系知识
    lines.append("---")
    lines.append("")
    lines.append("# 关系知识（Relational SKU）")
    lines.append("")
    lines.append("共 1 项，构建知识图谱的标签体系、术语表、实体关系。")
    lines.append("")
    lines.append("## relational-knowledge-base")
    lines.append("")
    lines.append("**内容**：")
    lines.append("- **标签体系**（label_tree.json）：20 个顶层分类，层级结构组织领域知识")
    lines.append("- **术语表**（glossary.json）：978 条术语定义，每条含标签与来源")
    lines.append("- **实体关系**（relationships.json）：1,336 条三元组（is-a、causes、related-to等12种关系）")
    lines.append("")

    # 元知识
    lines.append("---")
    lines.append("")
    lines.append("# 元知识（Meta Knowledge）")
    lines.append("")
    lines.append("共 1 项，SKU 导航与创意洞察。")
    lines.append("")
    lines.append("## meta-knowledge")
    lines.append("")
    lines.append("**内容**：")
    lines.append("- **mapping.md**：按功能特性查找相关 SKU（如「领导力」对应哪些历史案例）")
    lines.append("- **eureka.md**：跨领域创意连接与灵感（如「鸿门宴」与现代商业谈判）")
    lines.append("")

    # 统计信息
    lines.append("---")
    lines.append("")
    lines.append("# 统计信息")
    lines.append("")
    lines.append("## 事实性知识分类统计")
    lines.append("")
    lines.append("| 类别 | 数量 | 占比 |")
    lines.append("|------|------|------|")
    total_facts = sum(len(skus) for skus in facts_categories.values())
    for category, skus in facts_categories.items():
        count = len(skus)
        percentage = count / total_facts * 100 if total_facts > 0 else 0
        lines.append(f"| {category} | {count} | {percentage:.1f}% |")
    lines.append("")

    lines.append("## 技能知识分类统计")
    lines.append("")
    lines.append("| 类别 | 数量 | 占比 |")
    lines.append("|------|------|------|")
    total_skills = sum(len(skus) for skus in skills_categories.values())
    for category, skus in skills_categories.items():
        count = len(skus)
        percentage = count / total_skills * 100 if total_skills > 0 else 0
        lines.append(f"| {category} | {count} | {percentage:.1f}% |")
    lines.append("")

    return '\n'.join(lines)

def main():
    """主函数"""
    try:
        index_data = load_index()
        catalog = generate_catalog(index_data)

        # 输出到文件
        output_file = Path("kg/ontology/ontology-v1/CATALOG_CN.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(catalog)

        print(f"✓ 已生成详尽中文目录: {output_file}")
        print(f"  包含所有知识单元的中文说明")

    except Exception as e:
        import traceback
        print(f"✗ 错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
