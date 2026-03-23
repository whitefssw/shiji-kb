#!/usr/bin/env python3
"""
构建语义关系（动词）索引

从标注的.tagged.md文件中提取动词标注（⟦TYPE⟧格式），
统计出现次数，并生成JSON索引数据。

输出：kg/entities/data/verb_index.json
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# 动词类型定义（基于 verb_taxonomy.md）
VERB_TYPES = {
    '◈': {'name': 'military', 'label': '军事', 'desc': '战争、军事行动相关'},
    '◉': {'name': 'penalty', 'label': '刑罚', 'desc': '刑罚执行、政治斗争'},
    '○': {'name': 'political', 'label': '政治', 'desc': '政治行为、外交活动'},
    '◇': {'name': 'economic', 'label': '经济', 'desc': '经济活动、贸易行为'},
}

def extract_verbs_from_file(file_path: Path) -> List[Tuple[str, str, str]]:
    """
    从单个文件中提取动词标注

    返回: [(type_symbol, verb, disambiguation), ...]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 正则匹配 ⟦TYPE⟧ 格式
    # 支持消歧语法: ⟦◈伐|征伐⟧ 或简单形式: ⟦◈伐⟧
    pattern = r'⟦([◈◉○◇])([^⟧|]+)(?:\|([^⟧]+))?⟧'

    verbs = []
    for match in re.finditer(pattern, content):
        type_symbol = match.group(1)
        verb = match.group(2)
        disambiguation = match.group(3) if match.group(3) else ''
        verbs.append((type_symbol, verb, disambiguation))

    return verbs

def build_verb_index(chapter_dir: Path) -> Dict:
    """
    构建完整的动词索引

    返回结构:
    {
        "types": {
            "military": {"label": "军事", "count": 123, "verbs": {...}},
            ...
        },
        "verbs": {
            "伐": {"count": 517, "type": "military", "occurrences": [...]},
            ...
        },
        "total_count": 12345,
        "total_verbs": 52
    }
    """
    verb_occurrences = defaultdict(lambda: {
        'count': 0,
        'type': '',
        'type_symbol': '',
        'chapters': defaultdict(int),
        'disambiguations': defaultdict(int)
    })

    type_counts = {info['name']: 0 for info in VERB_TYPES.values()}

    # 遍历所有.tagged.md文件
    for file_path in sorted(chapter_dir.glob('*.tagged.md')):
        chapter_name = file_path.stem.replace('.tagged', '')

        verbs = extract_verbs_from_file(file_path)

        for type_symbol, verb, disambiguation in verbs:
            if type_symbol not in VERB_TYPES:
                continue

            type_name = VERB_TYPES[type_symbol]['name']

            # 更新动词统计
            verb_data = verb_occurrences[verb]
            verb_data['count'] += 1
            verb_data['type'] = type_name
            verb_data['type_symbol'] = type_symbol
            verb_data['chapters'][chapter_name] += 1

            if disambiguation:
                verb_data['disambiguations'][disambiguation] += 1

            # 更新类型统计
            type_counts[type_name] += 1

    # 构建最终索引
    index = {
        'types': {},
        'verbs': {},
        'total_count': sum(type_counts.values()),
        'total_verbs': len(verb_occurrences)
    }

    # 添加类型信息
    for type_symbol, info in VERB_TYPES.items():
        type_name = info['name']
        index['types'][type_name] = {
            'label': info['label'],
            'desc': info['desc'],
            'symbol': type_symbol,
            'count': type_counts[type_name]
        }

    # 添加动词信息（按出现次数降序）
    for verb, data in sorted(verb_occurrences.items(),
                             key=lambda x: x[1]['count'],
                             reverse=True):
        index['verbs'][verb] = {
            'count': data['count'],
            'type': data['type'],
            'type_symbol': data['type_symbol'],
            'chapters': dict(data['chapters']),
            'disambiguations': dict(data['disambiguations']) if data['disambiguations'] else {}
        }

    return index

def main():
    # 项目根目录
    root = Path(__file__).parent.parent.parent.parent
    chapter_dir = root / 'chapter_md'
    output_file = root / 'kg' / 'entities' / 'data' / 'verb_index.json'

    print(f"正在扫描章节目录: {chapter_dir}")
    print(f"提取动词标注...")

    index = build_verb_index(chapter_dir)

    print(f"\n统计结果:")
    print(f"  总动词类型: {index['total_verbs']} 个")
    print(f"  总出现次数: {index['total_count']} 次")
    print(f"\n按类型统计:")
    for type_name, type_info in index['types'].items():
        print(f"  {type_info['label']} ({type_info['symbol']}): {type_info['count']} 次")

    print(f"\n高频动词 Top 10:")
    for i, (verb, data) in enumerate(list(index['verbs'].items())[:10], 1):
        type_label = index['types'][data['type']]['label']
        print(f"  {i}. {verb} ({type_label}): {data['count']} 次")

    # 保存JSON
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 已保存索引文件: {output_file}")

if __name__ == '__main__':
    main()
