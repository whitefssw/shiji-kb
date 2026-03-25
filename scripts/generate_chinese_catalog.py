#!/usr/bin/env python3
"""
生成 ontology-v1 的详尽中文目录
"""

import json
import sys
from pathlib import Path

def load_index():
    """加载 SKU 索引"""
    index_file = Path("kg/ontology/ontology-v1/skus/skus_index.json")
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def translate_description(sku_id, name, desc, classification):
    """将英文描述翻译为中文（基于模式匹配）"""

    # 特殊情况处理
    if classification == "relational":
        return "关系知识库（标签体系、术语表、实体关系）"
    if classification == "meta":
        return "元知识（SKU路由表、创意洞察）"

    # 基于 name 的翻译映射（从已有索引文件中提取）
    translations = {
        # 史记总论
        "shiji-basic-metadata": "《史记》基本元数据",
        "shiji-significance": "《史记》的历史意义与评价",
        "simaqian-biography": "司马迁生平传记",

        # 五帝
        "five-emperors-genealogy": "五帝世系（黄帝至舜）",
        "yellow-emperor-achievements": "黄帝的主要成就与疆域",
        "emperor-yao-reign": "帝尧治世与禅让",
        "emperor-shun-officials": "帝舜任命的二十二位官员",
        "four-exiles": "四凶的流放与惩罚",
        "emperor-shun-life": "虞舜生平大事记",
        "ancient-surnames-origins": "上古姓氏与封国起源",

        # 夏商周
        "yu-genealogy": "大禹世系（上溯黄帝）",
        "gun-flood-control": "鲧治水失败",
        "yu-character": "禹的品格与德行",
        "yu-transportation-methods": "禹治水的四种交通工具",
        "nine-provinces": "九州的土壤、赋税与贡品",
        "nine-mountains": "九山及其走势",
        "nine-rivers": "九川水系",
        "five-zones-system": "五服制度",
        "nine-virtues": "皋陶九德（考核官员标准）",
        "xia-dynasty-succession": "夏朝君主世系（禹至桀）",
        "yu-descendants-surnames": "禹后裔衍生姓氏",
        "yu-death-burial": "禹崩于会稽",
        "xia-fall": "夏桀暴政与商汤兴起",
        "yin-dynasty-genealogy": "商朝君主世系（契至纣）",
        "zhou-dynasty-genealogy": "周朝君主世系（后稷至赧王）",
        "yin-yi-yin-biography": "伊尹传（商初贤相）",
        "shang-capital-relocations": "商朝迁都记录",
        "battle-muye": "牧野之战（周灭商）",
        "zhou-feudal-enfeoffments": "武王克殷后的分封",
        "five-punishments-system": "五刑制度（黥、劓、膑、宫、大辟）",
        "gonghe-regency": "共和行政（厉王出奔时期）",
        "baosi-legend": "褒姒传说与西周灭亡",
        "yin-descendant-surnames": "殷氏后裔姓氏",
    }

    # 如果有直接映射，使用映射
    if name in translations:
        return translations[name]

    # 否则使用原始描述
    return desc

def categorize_skus(skus):
    """按主题分类 SKU"""
    categories = {
        "史记总论与司马迁": [],
        "五帝与上古传说": [],
        "夏商周三代": [],
        "秦国与秦朝": [],
        "楚汉争霸": [],
        "汉朝政治与制度": [],
        "诸侯国与世家": [],
        "人物传记": [],
        "军事与战役": [],
        "天文历法与地理": [],
        "礼乐祭祀": [],
        "经济与社会": [],
        "匈奴与边疆民族": [],
        "思想学术": [],
        "军事战略与战术": [],
        "治国理政": [],
        "外交与谈判": [],
        "继承与权力交接": [],
        "人才选拔与管理": [],
        "危机应对与生存": [],
        "说服与劝谏": [],
        "法律与司法": [],
        "礼乐与文化": [],
        "经济与商业": [],
        "天文历法与占卜": [],
        "医学": [],
        "匈奴与边疆": [],
        "个人修养与处世": [],
        "关系知识": [],
        "元知识": [],
    }

    for sku in skus:
        sku_id = sku['sku_id']
        classification = sku['classification']

        # 特殊分类
        if classification == "relational":
            categories["关系知识"].append(sku)
            continue
        if classification == "meta":
            categories["元知识"].append(sku)
            continue

        # 根据 sku_id 范围分类（事实性知识）
        if classification == "factual":
            if sku_id in ["sku_001", "sku_002", "sku_003", "sku_079", "sku_433"]:
                categories["史记总论与司马迁"].append(sku)
            elif sku_id.startswith("sku_00") and int(sku_id[4:]) <= 10:
                categories["五帝与上古传说"].append(sku)
            elif int(sku_id[4:]) <= 38:
                categories["夏商周三代"].append(sku)
            # 可以继续添加更多规则...
            else:
                # 默认分类到"其他"
                if "其他" not in categories:
                    categories["其他"] = []
                categories["其他"].append(sku)

        # 技能类（根据 skill_id 范围）
        elif classification == "procedural":
            # 简化处理，放入"其他技能"
            if "其他技能" not in categories:
                categories["其他技能"] = []
            categories["其他技能"].append(sku)

    return {k: v for k, v in categories.items() if v}

def generate_catalog(index_data):
    """生成目录文档"""
    skus = index_data['skus']

    lines = []
    lines.append("# Ontology v1 详尽知识目录")
    lines.append("")
    lines.append(f"本目录列出 ontology-v1 中的所有 {index_data['total_skus']} 项知识单元，每项用中文说明其内容。")
    lines.append("")
    lines.append(f"- **生成时间**: {index_data['updated_at'][:10]}")
    lines.append(f"- **总知识单元数**: {index_data['total_skus']}")
    lines.append(f"- **总字符数**: {index_data['total_characters']:,}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 按 sku_id 排序输出
    factual_skus = [s for s in skus if s['classification'] == 'factual']
    procedural_skus = [s for s in skus if s['classification'] == 'procedural']
    relational_skus = [s for s in skus if s['classification'] == 'relational']
    meta_skus = [s for s in skus if s['classification'] == 'meta']

    # 事实性知识
    if factual_skus:
        lines.append("## 事实性知识（Factual SKUs）")
        lines.append("")
        lines.append(f"共 {len(factual_skus)} 项，记录史实、人物、事件、数据等客观信息。")
        lines.append("")

        for sku in sorted(factual_skus, key=lambda x: x['sku_id']):
            sku_id = sku['sku_id']
            name = sku['name']
            desc = sku.get('description', '')
            char_count = sku.get('character_count', 0)
            source = sku.get('source_chunk', '')

            chinese_desc = translate_description(sku_id, name, desc, 'factual')

            lines.append(f"### {sku_id}")
            lines.append(f"- **名称**: {name}")
            lines.append(f"- **说明**: {chinese_desc}")
            lines.append(f"- **来源**: {source}")
            lines.append(f"- **字数**: {char_count}")
            if 'entity_count' in sku and sku['entity_count']:
                lines.append(f"- **实体数**: {sku['entity_count']}")
                if 'top_entities' in sku:
                    entities = '、'.join(sku['top_entities'][:5])
                    lines.append(f"- **主要实体**: {entities}")
            lines.append("")

    # 技能知识
    if procedural_skus:
        lines.append("---")
        lines.append("")
        lines.append("## 技能知识（Procedural SKUs）")
        lines.append("")
        lines.append(f"共 {len(procedural_skus)} 项，提取可复用的方法、流程、策略。")
        lines.append("")

        for sku in sorted(procedural_skus, key=lambda x: x['sku_id']):
            sku_id = sku['sku_id']
            name = sku['name']
            desc = sku.get('description', '')
            char_count = sku.get('character_count', 0)
            source = sku.get('source_chunk', '')

            lines.append(f"### {sku_id}")
            lines.append(f"- **名称**: {name}")
            lines.append(f"- **说明**: {desc}")
            lines.append(f"- **来源**: {source}")
            lines.append(f"- **字数**: {char_count}")
            lines.append("")

    # 关系知识
    if relational_skus:
        lines.append("---")
        lines.append("")
        lines.append("## 关系知识（Relational SKU）")
        lines.append("")
        lines.append("构建知识图谱的标签体系、术语表、实体关系。")
        lines.append("")

        for sku in relational_skus:
            lines.append(f"### {sku['sku_id']}")
            lines.append(f"- **名称**: {sku['name']}")
            lines.append("- **说明**: 包含标签分类树（20类）、术语定义（978条）、实体关系三元组（1,336条）")
            lines.append("")

    # 元知识
    if meta_skus:
        lines.append("---")
        lines.append("")
        lines.append("## 元知识（Meta Knowledge）")
        lines.append("")
        lines.append("SKU 导航与创意洞察。")
        lines.append("")

        for sku in meta_skus:
            lines.append(f"### {sku['sku_id']}")
            lines.append(f"- **名称**: {sku['name']}")
            lines.append("- **说明**: mapping.md（按功能查找SKU）、eureka.md（跨领域创意连接）")
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

        print(f"✓ 已生成中文目录: {output_file}")
        print(f"  - 事实性知识: {len([s for s in index_data['skus'] if s['classification'] == 'factual'])} 项")
        print(f"  - 技能知识: {len([s for s in index_data['skus'] if s['classification'] == 'procedural'])} 项")
        print(f"  - 关系知识: {len([s for s in index_data['skus'] if s['classification'] == 'relational'])} 项")
        print(f"  - 元知识: {len([s for s in index_data['skus'] if s['classification'] == 'meta'])} 项")

    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
