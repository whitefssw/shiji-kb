#!/usr/bin/env python3
"""
将 person_xingshi.md 转换为 person_xingshi.json

这个脚本解析 Markdown 表格格式的姓氏推理数据，转换为 JSON 格式。

Usage:
    python kg/entities/scripts/convert_xingshi_md_to_json.py

Input:  kg/entities/data/person_xingshi.md
Output: kg/entities/data/person_xingshi.json
"""

import re
import json
from pathlib import Path
from collections import defaultdict


def parse_evidence(evidence_str):
    """解析证据字符串为列表"""
    if not evidence_str or evidence_str.strip() == "":
        return []
    # 分割多个证据，用 ; 或 | 分隔
    parts = re.split(r'[;|]', evidence_str)
    return [p.strip() for p in parts if p.strip()]


def parse_chapter_refs(evidence_list):
    """从证据中提取章节编号"""
    chapters = set()
    for ev in evidence_list:
        # 匹配 001: 这样的格式
        match = re.match(r'(\d{3}):', ev)
        if match:
            chapters.add(match.group(1))
    return sorted(list(chapters))


def infer_rule_from_round(round_name):
    """根据轮次名称推断规则编号"""
    if "Round 1" in round_name or "直接记载" in round_name:
        return "R1"
    elif "Round 2" in round_name or "邦国" in round_name:
        return "R2"
    elif "Round 3" in round_name:
        return "R3"
    elif "Round 4" in round_name:
        return "R4"
    elif "Round 5" in round_name:
        return "R5"
    elif "Round 6" in round_name and "6b" not in round_name and "6c" not in round_name:
        return "R6"
    elif "6b" in round_name:
        return "R6b"
    elif "6c" in round_name:
        return "R6c"
    elif "重要人物" in round_name or "补充" in round_name:
        return "R_supplement"
    else:
        return "R_unknown"


def parse_markdown_table(md_file):
    """解析 Markdown 文件中的所有表格"""
    persons = {}
    stats = defaultdict(int)

    content = md_file.read_text(encoding='utf-8')
    lines = content.split('\n')

    current_round = None
    in_table = False
    headers = []

    for i, line in enumerate(lines):
        # 检测章节标题（轮次）
        if line.startswith('##'):
            current_round = line.strip('# ').strip()
            in_table = False
            continue

        # 检测表格头
        if '|' in line and not in_table:
            # 检查是否是表头
            if i + 1 < len(lines) and '---' in lines[i + 1]:
                headers = [h.strip() for h in line.split('|')[1:-1]]  # 去掉首尾空元素
                in_table = True
                continue

        # 解析表格行
        if in_table and '|' in line and '---' not in line:
            cells = [c.strip() for c in line.split('|')[1:-1]]

            if len(cells) < len(headers) or not cells[0]:  # 空行或不完整行
                continue

            # 构建数据字典
            row_data = dict(zip(headers, cells))

            person_name = row_data.get('人名', '').strip()
            if not person_name:
                continue

            # 提取字段
            xing = row_data.get('姓', '').strip()
            shi = row_data.get('氏', '').strip()
            ming = row_data.get('名', '').strip()
            zi = row_data.get('字', '').strip()
            confidence = row_data.get('置信度', '').strip().lower()
            evidence_str = row_data.get('证据', '').strip()

            # 解析证据
            evidence = parse_evidence(evidence_str)
            source_chapter = parse_chapter_refs(evidence)

            # 推断规则
            rule = infer_rule_from_round(current_round) if current_round else "R_unknown"

            # 判断时期
            period = "pre-qin"  # 默认先秦
            if row_data.get('时代'):
                period = row_data['时代'].strip()

            # 构建 person 条目
            person_entry = {
                "xing": xing if xing else None,
                "shi": shi if shi else None,
                "ming": ming if ming else None,
                "zi": zi if zi else None,
                "period": period,
                "confidence": confidence if confidence in ['exact', 'high', 'medium', 'low'] else 'medium',
                "evidence": evidence,
                "rule": rule,
                "source_chapter": source_chapter
            }

            # 清理 None 值（可选，保留更清晰）
            # person_entry = {k: v for k, v in person_entry.items() if v is not None}

            # 添加到结果
            if person_name not in persons:
                persons[person_name] = person_entry
                stats[rule] += 1
            else:
                # 如果重复，保留置信度更高的
                existing_conf = ['exact', 'high', 'medium', 'low'].index(persons[person_name]['confidence'])
                new_conf = ['exact', 'high', 'medium', 'low'].index(person_entry['confidence'])
                if new_conf < existing_conf:  # 索引越小置信度越高
                    persons[person_name] = person_entry
                    stats[rule] += 1

    return persons, stats


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent.parent
    md_file = project_root / "kg" / "entities" / "data" / "person_xingshi.md"
    json_file = project_root / "kg" / "entities" / "data" / "person_xingshi.json"

    if not md_file.exists():
        print(f"❌ 源文件不存在: {md_file}")
        return

    print("=" * 60)
    print("开始转换 person_xingshi.md → person_xingshi.json")
    print("=" * 60)

    # 解析 Markdown
    print(f"📖 读取: {md_file.name}")
    persons, stats = parse_markdown_table(md_file)

    print(f"✓ 解析完成: {len(persons)} 人")
    print()

    # 统计信息
    print("规则分布:")
    for rule in sorted(stats.keys()):
        print(f"  {rule}: {stats[rule]}")
    print()

    total = len(persons)
    print(f"总计: {total} 人")
    print()

    # 构建输出 JSON
    output = {
        "_doc": "史记人物姓氏推理表。先秦人物区分姓（血缘）与氏（分家）。秦后人物仅记姓。",
        "_version": "v2.0",
        "_stats": {
            **stats,
            "total": total
        },
        "persons": persons
    }

    # 写入 JSON
    print(f"💾 写入: {json_file.name}")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    file_size = json_file.stat().st_size
    print(f"✓ 文件大小: {file_size:,} 字节 ({file_size / 1024:.1f} KB)")
    print()

    # 验证
    print("验证数据...")
    with open(json_file, 'r', encoding='utf-8') as f:
        verify = json.load(f)

    print(f"✓ JSON格式正确")
    print(f"✓ 包含 {len(verify['persons'])} 人")

    # 统计置信度分布
    conf_dist = defaultdict(int)
    for p in verify['persons'].values():
        conf_dist[p.get('confidence', 'unknown')] += 1

    print()
    print("置信度分布:")
    for conf in ['exact', 'high', 'medium', 'low', 'unknown']:
        if conf in conf_dist:
            print(f"  {conf}: {conf_dist[conf]}")

    print("=" * 60)
    print("✓ 转换完成！")
    print("=" * 60)
    print()
    print(f"输出文件: {json_file.relative_to(project_root)}")
    print()
    print("下一步:")
    print("  1. 检查生成的 JSON 文件")
    print("  2. 运行: python scripts/publish_xingshi_data.py")
    print("  3. 提交更新: git add kg/entities/data/person_xingshi.json")


if __name__ == "__main__":
    main()
