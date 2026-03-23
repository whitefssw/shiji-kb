#!/usr/bin/env python3
"""
生成语义关系（动词）索引HTML页面

读取 verb_index.json，生成：
1. docs/entities/relations.html - 语义关系总索引（按类型）
2. docs/entities/relations-military.html - 军事动词详细索引
3. docs/entities/relations-penalty.html - 刑罚动词详细索引
4. docs/entities/relations-political.html - 政治动词详细索引
"""

import json
from pathlib import Path
from typing import Dict

def load_verb_index(data_file: Path) -> Dict:
    """加载动词索引数据"""
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_main_index(index: Dict, output_file: Path):
    """生成语义关系主索引页面"""

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>语义关系索引 - 史记知识库</title>
    <link rel="stylesheet" href="../css/shiji-styles.css">
    <link rel="stylesheet" href="../css/entity-index.css">
</head>
<body>
<nav class="chapter-nav">
    <a href="../index.html" class="nav-home">回到主页</a>
    <a href="index.html" class="nav-next">实体索引</a>
</nav>
<h1>语义关系索引</h1>
<p>史记全文语义关系索引，记录事件中的动作与关系。按关系类型分类，各类型按出现次数降序排列。点击类型名称进入详细索引页面。</p>

<div class="entity-type-grid">
"""

    # 类型卡片（按出现次数降序）
    sorted_types = sorted(index['types'].items(),
                         key=lambda x: x[1]['count'],
                         reverse=True)

    type_css_map = {
        'military': 'military',
        'penalty': 'penalty',
        'political': 'political',
        'economic': 'economic'
    }

    for type_name, type_info in sorted_types:
        if type_info['count'] == 0:
            continue

        css_class = type_css_map.get(type_name, 'default')
        verb_count = sum(1 for v in index['verbs'].values() if v['type'] == type_name)

        html += f"""  <a href="relations-{type_name}.html" class="entity-type-card">
    <span class="type-label {css_class}">{type_info['label']}</span>
    <span class="type-count">{verb_count} 个动作</span>
    <span class="type-total">{type_info['count']} 次出现</span>
  </a>
"""

    html += f"""</div>

<div class="stats-summary">
  <h2>总体统计</h2>
  <ul>
    <li>总动作类型: <strong>{index['total_verbs']}</strong> 个</li>
    <li>总出现次数: <strong>{index['total_count']}</strong> 次</li>
  </ul>
</div>

<nav class="chapter-nav">
    <a href="../index.html" class="nav-home">回到主页</a>
    <a href="index.html" class="nav-next">实体索引</a>
</nav>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ 已生成主索引: {output_file}")

def generate_type_index(type_name: str, type_info: Dict, verbs: Dict, output_file: Path):
    """生成单个类型的详细索引页面"""

    type_label = type_info['label']
    type_symbol = type_info['symbol']
    type_desc = type_info['desc']

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{type_label}动作索引 - 史记知识库</title>
    <link rel="stylesheet" href="../css/shiji-styles.css">
    <link rel="stylesheet" href="../css/entity-index.css">
</head>
<body>
<nav class="chapter-nav">
    <a href="../index.html" class="nav-home">回到主页</a>
    <a href="relations.html" class="nav-next">语义关系</a>
</nav>
<h1>{type_label}动作索引</h1>
<p class="index-stats">共 <strong>{len(verbs)}</strong> 个动作，<strong>{type_info['count']}</strong> 次出现</p>
<div class="entity-type-desc">
  <span class="type-label {type_name}">{type_label}</span>
  <span class="type-marker">⟦{type_symbol}⟧</span>
  <p>{type_desc}</p>
</div>

<div class="entity-filter">
    <input type="text" id="filter-input" placeholder="搜索{type_label}动作...">
</div>

<div class="entity-index">
"""

    # 按出现次数降序排列
    sorted_verbs = sorted(verbs.items(), key=lambda x: x[1]['count'], reverse=True)

    for verb, data in sorted_verbs:
        # 章节列表（按出现次数降序）
        chapters = sorted(data['chapters'].items(), key=lambda x: x[1], reverse=True)
        chapter_links = []
        for chapter, count in chapters:
            chapter_num = chapter.split('_')[0]
            chapter_title = chapter.split('_')[1] if '_' in chapter else chapter
            chapter_links.append(
                f'<a href="../chapters/{chapter}.html" class="chapter-ref">'
                f'{chapter_num}·{chapter_title} ({count})</a>'
            )

        # 消歧信息
        disambig_html = ''
        if data['disambiguations']:
            disambig_list = [f"{d}({c})" for d, c in
                           sorted(data['disambiguations'].items(),
                                  key=lambda x: x[1], reverse=True)]
            disambig_html = f'<div class="disambiguation">消歧: {", ".join(disambig_list)}</div>'

        html += f"""  <div class="entity-entry" id="verb-{verb}">
    <div class="entry-left">
      <span class="entity-name">{verb}</span>
      <span class="entity-count">{data['count']} 次</span>
    </div>
    <div class="entry-right">
      <div class="chapter-list">
        {' '.join(chapter_links)}
      </div>
      {disambig_html}
    </div>
  </div>
"""

    html += """</div>

<script>
// 搜索过滤功能
document.getElementById('filter-input').addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase();
    const entries = document.querySelectorAll('.entity-entry');
    entries.forEach(entry => {
        const name = entry.querySelector('.entity-name').textContent;
        entry.style.display = name.includes(query) ? '' : 'none';
    });
});
</script>

<nav class="chapter-nav">
    <a href="../index.html" class="nav-home">回到主页</a>
    <a href="relations.html" class="nav-next">语义关系</a>
</nav>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ 已生成 {type_label} 索引: {output_file}")

def main():
    # 项目根目录
    root = Path(__file__).parent.parent.parent.parent
    data_file = root / 'kg' / 'entities' / 'data' / 'verb_index.json'
    output_dir = root / 'docs' / 'entities'

    # 加载数据
    print(f"加载动词索引: {data_file}")
    index = load_verb_index(data_file)

    # 生成主索引
    generate_main_index(index, output_dir / 'relations.html')

    # 生成各类型详细索引
    for type_name, type_info in index['types'].items():
        if type_info['count'] == 0:
            continue

        # 筛选该类型的动词
        verbs = {v: data for v, data in index['verbs'].items()
                if data['type'] == type_name}

        output_file = output_dir / f'relations-{type_name}.html'
        generate_type_index(type_name, type_info, verbs, output_file)

    print(f"\n✓ 全部完成！共生成 {len([t for t in index['types'].values() if t['count'] > 0]) + 1} 个HTML文件")

if __name__ == '__main__':
    main()
