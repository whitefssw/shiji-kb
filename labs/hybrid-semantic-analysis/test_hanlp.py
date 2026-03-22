#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HanLP实体标注测试

使用HanLP进行实体识别,作为LTP的替代方案
"""

import sys
import json
import re
import argparse
import time
from pathlib import Path

def test_hanlp_available():
    """测试HanLP是否可用"""
    try:
        import hanlp
        return True
    except ImportError:
        return False

def extract_entities_with_hanlp(text, model_name='MSRA_NER_BERT_BASE_ZH'):
    """使用HanLP提取实体"""
    import hanlp

    # 加载NER模型
    try:
        # 可选的预训练模型:
        # - hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH (MSRA数据集)
        # - hanlp.pretrained.ner.CONLL03_NER_BERT_BASE_UNCASED_EN (英文)
        recognizer = hanlp.load(getattr(hanlp.pretrained.ner, model_name))
    except Exception as e:
        print(f"模型加载失败: {e}")
        print(f"尝试下载模型...")
        recognizer = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH)

    # 识别实体
    # HanLP返回格式: [[[entity_text, entity_type, start, end], ...]]
    result = recognizer(text)

    entities = []
    tagged_text = text

    # HanLP的实体类型映射
    type_mapping = {
        'PER': 'PERSON',     # 人名
        'PERSON': 'PERSON',
        'LOC': 'PLACE',      # 地名
        'LOCATION': 'PLACE',
        'ORG': 'ORG',        # 组织
        'ORGANIZATION': 'ORG',
        'GPE': 'PLACE',      # 地缘政治实体
    }

    # 收集实体并生成标注
    entity_spans = []
    for entity_info in result:
        if isinstance(entity_info, (list, tuple)) and len(entity_info) >= 2:
            entity_text = entity_info[0]
            entity_type = entity_info[1]

            mapped_type = type_mapping.get(entity_type, entity_type)

            entities.append({
                'text': entity_text,
                'type': mapped_type
            })

            # 记录实体位置(用于标注)
            entity_spans.append((entity_text, mapped_type))

    # 生成标注文本
    # 从后往前替换,避免位置偏移
    for entity_text, entity_type in reversed(entity_spans):
        # 只标注第一次出现
        pattern = re.escape(entity_text)
        if re.search(f'(?<!〗){pattern}(?!〖)', tagged_text):
            tagged_text = re.sub(
                f'(?<!〗){pattern}(?!〖)',
                f'〖{entity_type} {entity_text}〗',
                tagged_text,
                count=1
            )

    return tagged_text, entities

def count_entities(text):
    """统计标注实体数"""
    pattern = r'〖([A-Z_]+)\s+([^〗]+)〗'
    matches = re.findall(pattern, text)

    entity_types = {}
    for entity_type, _ in matches:
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

    return len(matches), entity_types

def extract_entity_texts(text):
    """提取实体文本集合"""
    pattern = r'〖[A-Z_]+\s+([^|〗]+)(?:\|[^〗]+)?〗'
    return set(re.findall(pattern, text))

def evaluate(predicted_text, ground_truth_text):
    """评估标注结果"""
    pred_entities = extract_entity_texts(predicted_text)
    gt_entities = extract_entity_texts(ground_truth_text)

    correct = len(pred_entities & gt_entities)
    recall = correct / len(gt_entities) if gt_entities else 0
    precision = correct / len(pred_entities) if pred_entities else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    pred_count, pred_types = count_entities(predicted_text)
    gt_count, gt_types = count_entities(ground_truth_text)

    return {
        'recall': recall,
        'precision': precision,
        'f1': f1,
        'predicted_count': pred_count,
        'ground_truth_count': gt_count,
        'correct_count': correct,
        'predicted_types': pred_types,
        'ground_truth_types': gt_types,
    }

def main():
    parser = argparse.ArgumentParser(description='HanLP实体标注测试')
    parser.add_argument('--data', type=str, default='short',
                       choices=['short', 'medium', 'long'],
                       help='测试数据集: short(138字), medium(631字), long(3000字)')
    parser.add_argument('--model', type=str, default='MSRA_NER_BERT_BASE_ZH',
                       help='HanLP预训练模型名称')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='结果输出目录')

    args = parser.parse_args()

    # 数据文件映射
    data_files = {
        'short': {
            'corpus': 'data/test_corpus.txt',
            'ground_truth': 'data/ground_truth.tagged.md',
            'description': '短文本(138字)'
        },
        'medium': {
            'corpus': 'data/test_corpus_long.txt',
            'ground_truth': None,
            'description': '中文本(631字)'
        },
        'long': {
            'corpus': 'data/test_corpus_chapter.txt',
            'ground_truth': None,
            'description': '长文本(3000字)'
        }
    }

    data_config = data_files[args.data]

    # 检查HanLP是否可用
    if not test_hanlp_available():
        print("=" * 80)
        print("错误: HanLP不可用")
        print("=" * 80)
        print("\n请安装HanLP:")
        print("  pip install hanlp")
        print("\n详见: NLP_TOOLS_COMPARISON.md")
        return 1

    # 加载HanLP
    print("=" * 80)
    print(f"HanLP实体标注测试 - {data_config['description']}")
    print("=" * 80)

    print("\n加载HanLP模型...")
    print(f"模型: {args.model}")

    try:
        import hanlp
        print("✓ HanLP导入成功")
    except Exception as e:
        print(f"✗ HanLP导入失败: {e}")
        return 1

    # 读取测试数据
    corpus_file = Path(__file__).parent / data_config['corpus']
    if not corpus_file.exists():
        print(f"\n错误: 测试数据不存在 - {corpus_file}")
        return 1

    with open(corpus_file, encoding='utf-8') as f:
        text = f.read().strip()

    ground_truth = None
    if data_config['ground_truth']:
        gt_file = Path(__file__).parent / data_config['ground_truth']
        if gt_file.exists():
            with open(gt_file, encoding='utf-8') as f:
                ground_truth = f.read()

    print(f"\n原文长度: {len(text)} 字")
    print(f"原文预览: {text[:100]}...")

    # 运行HanLP标注
    print("\n正在标注...")
    start_time = time.time()

    try:
        tagged_text, entities = extract_entities_with_hanlp(text, args.model)
        elapsed = time.time() - start_time
        print(f"✓ 标注完成 ({elapsed:.2f}秒)")
    except Exception as e:
        print(f"✗ 标注失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 显示结果
    print("\n" + "=" * 80)
    print("标注结果")
    print("=" * 80)
    print(tagged_text)

    # 统计
    entity_count, entity_types = count_entities(tagged_text)

    print("\n" + "=" * 80)
    print("统计信息")
    print("=" * 80)
    print(f"\n识别实体数: {entity_count}")
    print(f"\n实体类型分布:")
    for etype, count in sorted(entity_types.items()):
        print(f"  {etype}: {count}")

    # 评估(如果有ground truth)
    if ground_truth:
        print("\n" + "=" * 80)
        print("性能评估")
        print("=" * 80)

        eval_result = evaluate(tagged_text, ground_truth)

        print(f"\n召回率 (Recall):    {eval_result['recall']*100:.1f}%")
        print(f"精确率 (Precision): {eval_result['precision']*100:.1f}%")
        print(f"F1分数:             {eval_result['f1']*100:.1f}%")

        print(f"\n实体统计:")
        print(f"  预测: {eval_result['predicted_count']} 个")
        print(f"  标准: {eval_result['ground_truth_count']} 个")
        print(f"  正确: {eval_result['correct_count']} 个")

        print(f"\n实体类型对比:")
        print(f"  {'类型':<10} {'预测':<10} {'标准':<10}")
        print(f"  {'-'*30}")
        all_types = set(eval_result['predicted_types'].keys()) | set(eval_result['ground_truth_types'].keys())
        for entity_type in sorted(all_types):
            pred = eval_result['predicted_types'].get(entity_type, 0)
            gt = eval_result['ground_truth_types'].get(entity_type, 0)
            print(f"  {entity_type:<10} {pred:<10} {gt:<10}")

    # 保存结果
    output_dir = Path(__file__).parent / args.output_dir
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"hanlp_{args.data}_result.tagged.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(tagged_text)

    metadata = {
        'method': 'hanlp',
        'model': args.model,
        'data_size': args.data,
        'text_length': len(text),
        'time_seconds': elapsed,
        'entity_count': entity_count,
        'entity_types': entity_types,
    }

    if ground_truth:
        metadata.update({
            'recall': eval_result['recall'],
            'precision': eval_result['precision'],
            'f1': eval_result['f1'],
        })

    metadata_file = output_dir / f"hanlp_{args.data}_result.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("结果已保存")
    print("=" * 80)
    print(f"标注文本: {output_file}")
    print(f"元数据:   {metadata_file}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
