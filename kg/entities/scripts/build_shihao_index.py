#!/usr/bin/env python3
"""
构建谥号索引

从实体索引中提取带谥号的人名，按谥号字分组，生成谥号索引页面。

输出：
- kg/entities/data/shihao_index.json
- docs/special/shihao.html
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional

# 常见谥号字（按拼音排序）
SHIHAO_CHARS = [
    # 美谥
    '文', '武', '成', '康', '昭', '穆', '宣', '懿', '献', '景', '惠', '襄',
    '烈', '显', '元', '章', '明', '睿', '庄', '定', '简', '靖', '威', '敬',
    '安', '桓', '僖', '孝', '平', '顷', '恭', '静', '德', '仁', '肃', '质',
    '贞', '节', '敏', '缪',
    # 平谥
    '怀', '悼', '哀', '闵', '思', '殇', '幽', '共', '愍', '夷',
    # 恶谥
    '厉', '炀', '灵', '荒', '隐'
]

# 谥法释义（来源：《谥法解》等）
SHIHAO_MEANINGS = {
    '文': '经纬天地曰文，道德博闻曰文，学勤好问曰文，慈惠爱民曰文',
    '武': '克定祸乱曰武，刑民克服曰武，夸志多穷曰武',
    '成': '安民立政曰成，制义克服曰成',
    '康': '安乐抚民曰康，令民安乐曰康',
    '昭': '容仪恭美曰昭，昭德有劳曰昭，圣闻周达曰昭',
    '穆': '布德执义曰穆，中情见貌曰穆',
    '宣': '善闻周达曰宣，圣善周闻曰宣',
    '懿': '温柔贤善曰懿，柔克有光曰懿',
    '献': '聪明睿智曰献，智质有圣曰献',
    '景': '布义行刚曰景，由义而济曰景',
    '惠': '爱民好与曰惠，柔质慈民曰惠',
    '襄': '辟地有德曰襄，因事有功曰襄',
    '烈': '有功安民曰烈，秉德尊业曰烈',
    '显': '行见中外曰显',
    '元': '始建国都曰元，主义行德曰元',
    '章': '温克令仪曰章，敬慎高亢曰章',
    '明': '照临四方曰明，谮诉不行曰明',
    '睿': '深思远虑曰睿',
    '庄': '屡征杀伐曰庄，武而不遂曰庄',
    '定': '安民法古曰定，纯行不爽曰定',
    '简': '平易不訾曰简，正直无邪曰简',
    '靖': '宽乐令终曰靖，柔德安众曰靖',
    '威': '猛以彊果曰威，猛以刚果曰威',
    '敬': '夙夜警戒曰敬，合善典法曰敬',
    '安': '好和不争曰安，宽容平和曰安',
    '桓': '辟土服远曰桓，克敬勤民曰桓',
    '僖': '小心畏忌曰僖，质渊受谏曰僖',
    '孝': '慈惠爱亲曰孝，秉德不回曰孝',
    '平': '治而无眚曰平，执事有制曰平',
    '顷': '甄心动惧曰顷',
    '恭': '尊贤敬让曰恭，执事坚固曰恭',
    '静': '宽乐令终曰静，恭己鲜言曰静',
    '德': '绥柔士民曰德，谏诤不威曰德',
    '仁': '慈民爱物曰仁，克己复礼曰仁',
    '怀': '慈仁短折曰怀',
    '悼': '年中早夭曰悼，恐惧从处曰悼',
    '哀': '早孤短折曰哀，恭仁短折曰哀',
    '闵': '在国逢难曰闵，使民折伤曰闵',
    '思': '道德纯一曰思，大省兆民曰思',
    '殇': '短折不成曰殇',
    '幽': '壅遏不通曰幽，蚤孤铺位曰幽',
    '共': '既过能改曰共',
    '厉': '杀戮无辜曰厉，暴慢无亲曰厉',
    '炀': '好内远礼曰炀，去礼远众曰炀',
    '灵': '乱而不损曰灵，死而志成曰灵',
    '荒': '好乐怠政曰荒，外内从乱曰荒',
    '隐': '隐拂不成曰隐，不显尸国曰隐',
    '肃': '刚德克就曰肃，执心决断曰肃',
    '质': '名实不爽曰质，温恭好礼曰质',
    '贞': '清白守节曰贞，大虑克就曰贞',
    '节': '好廉自克曰节，能固所守曰节',
    '敏': '速於事曰敏，应事有功曰敏',
    '缪': '名与实爽曰缪，伤人蔽贤曰缪',
    '愍': '在国逢难曰愍，使民折伤曰愍',
    '夷': '安心好静曰夷，克定祸乱曰夷',
}

# 爵位等级（按高低排序）
RANK_LEVELS = ['帝', '王', '公', '侯', '伯', '子', '男']

def extract_shihao_from_name(name: str, chapters: List[str] = None) -> Optional[tuple]:
    """
    从人名中提取谥号信息

    返回: (谥号字, 爵位, 前缀) 或 None
    例如: "秦献公" -> ('献', '公', '秦')
          "汉武帝" -> ('武', '帝', '汉')
    """
    # 排除列表：这些不是谥号（思想家、人名、封号等）
    EXCLUSIONS = [
        # 思想家（子）
        '庄子', '孟子', '荀子', '韩子', '墨子', '惠子', '老子',
        '孔子', '列子', '杨子', '公孙龙子', '慎子', '申子', '尹文子',
        '田子', '陈子', '吴子', '孙子', '鬼谷子', '商子', '邓子',
        '晏子', '管子', '伍子', '虞子', '陈平子', '张子',
        '张良子', '陈胜子', '项羽子', '范增子',
        # 人名（君）
        '文君',  # 卓文君
        # 封号（君）- 这些是地名+封号，不是谥号
        '成安君', '信平君', '武平君畔', '脩成君', '刚成君',
        # 封地侯（地名+侯）- 不是谥号
        '武安侯', '故安侯', '清安侯', '长平侯', '平津侯',
        '安定侯', '建成侯', '文成侯', '东武侯', '令武侯', '信武侯', '玄武侯',
    ]

    if name in EXCLUSIONS:
        return None

    # 匹配模式：[前缀][谥号字1-2个][爵位]
    # 前缀可选（0-3字），谥号字必需（1-2字），爵位必需（1字）
    common_states = ['周', '秦', '汉', '齐', '楚', '燕', '赵', '魏', '韩', '宋', '鲁', '卫', '陈', '蔡', '曹', '郑', '吴', '越', '晋']

    # 年表、本纪、世家章节 - 在这些章节中可以放宽前缀要求
    important_chapters = {
        # 年表（013-022）
        '013_三代世表', '014_十二诸侯年表', '015_六国年表',
        '016_秦楚之际月表', '017_汉兴以来诸侯王年表',
        '018_高祖功臣侯者年表', '019_惠景间侯者年表',
        '020_建元以来侯者年表', '021_建元已来王子侯者年表',
        '022_汉兴以来将相名臣年表',
        # 本纪（001-012）
        '001_五帝本纪', '002_夏本纪', '003_殷本纪', '004_周本纪', '005_秦本纪',
        '006_秦始皇本纪', '007_项羽本纪', '008_高祖本纪', '009_吕太后本纪',
        '010_孝文本纪', '011_孝景本纪', '012_孝武本纪',
        # 世家（031-060）
        '031_吴太伯世家', '032_齐太公世家', '033_鲁周公世家', '034_燕召公世家',
        '035_管蔡世家', '036_陈杞世家', '037_卫康叔世家', '038_宋微子世家',
        '039_晋世家', '040_楚世家', '041_越王句践世家', '042_郑世家',
        '043_赵世家', '044_魏世家', '045_韩世家', '046_田敬仲完世家',
        '047_孔子世家', '048_陈涉世家', '049_外戚世家', '050_楚元王世家',
        '051_荆燕世家', '052_齐悼惠王世家', '053_萧相国世家', '054_曹相国世家',
        '055_留侯世家', '056_陈丞相世家', '057_绛侯周勃世家', '058_梁孝王世家',
        '059_五宗世家', '060_三王世家'
    }

    # 检查是否主要出现在重要章节中
    in_important_chapters = False
    if chapters:
        in_important_chapters = any(ch in important_chapters for ch in chapters)

    for rank in RANK_LEVELS:
        # 先尝试匹配双字谥号
        pattern_double = f'^(.{{0,3}})([{"".join(SHIHAO_CHARS)}]{{2}})({rank})$'
        match = re.match(pattern_double, name)
        if match:
            prefix, shihao, rank_char = match.groups()
            # 验证两个字都是谥号字
            if shihao[0] in SHIHAO_CHARS and shihao[1] in SHIHAO_CHARS:
                # 验证爵位要求
                if rank in ['侯', '伯', '男']:
                    # 侯、伯、男：如果出现在重要章节中，允许没有前缀
                    if not in_important_chapters:
                        if not prefix or (len(prefix) == 1 and prefix not in common_states):
                            continue
                elif rank == '子':
                    # 子爵：前缀通常是姓氏，可以是单字。但完全没有前缀的要过滤
                    if not prefix and not in_important_chapters:
                        continue
                return (shihao, rank_char, prefix)

        # 再尝试匹配单字谥号
        pattern_single = f'^(.{{0,3}})([{"".join(SHIHAO_CHARS)}])({rank})$'
        match = re.match(pattern_single, name)
        if match:
            prefix, shihao, rank_char = match.groups()
            # 验证爵位要求
            if rank in ['侯', '伯', '男']:
                # 侯、伯、男：如果出现在重要章节中，允许没有前缀
                if not in_important_chapters:
                    if not prefix or (len(prefix) == 1 and prefix not in common_states):
                        continue
            elif rank == '子':
                # 子爵：前缀通常是姓氏，可以是单字。但完全没有前缀的要过滤
                # 只在重要章节中允许无前缀
                if not prefix and not in_important_chapters:
                    continue
            return (shihao, rank_char, prefix)

    return None

def load_entity_index(data_file: Path) -> Dict:
    """加载实体索引数据"""
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_person_lifespans(data_file: Path) -> Dict:
    """加载人物生卒年数据"""
    if not data_file.exists():
        return {}
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_shihao_index(entity_index: Dict, lifespans: Dict) -> Dict:
    """构建谥号索引"""

    shihao_index = defaultdict(lambda: {
        'meaning': '',
        'source': '《谥法解》',
        'ranks': defaultdict(list),
        'total': 0
    })

    # 遍历所有人名实体
    person_entities = entity_index.get('person', {})

    for person_name, person_data in person_entities.items():
        # 先提取章节信息
        refs = person_data.get('refs', [])
        chapters = sorted(set(ref[0] for ref in refs if ref))

        # 传入章节信息进行谥号提取
        result = extract_shihao_from_name(person_name, chapters)
        if not result:
            continue

        shihao_char, rank, prefix = result

        # 构建人物信息

        person_info = {
            'name': person_name,
            'prefix': prefix,
            'rank': rank,
            'chapters': chapters,
            'count': person_data.get('count', 0)
        }

        # 添加生卒年信息（如果有）
        lifespan = lifespans.get(person_name, {})
        if lifespan:
            if 'birth' in lifespan:
                person_info['birth'] = lifespan['birth']
            if 'death' in lifespan:
                person_info['death'] = lifespan['death']

        # 添加到索引
        shihao_index[shihao_char]['ranks'][rank].append(person_info)
        shihao_index[shihao_char]['total'] += 1

        # 添加谥法释义
        if shihao_char in SHIHAO_MEANINGS:
            shihao_index[shihao_char]['meaning'] = SHIHAO_MEANINGS[shihao_char]

    # 对每个谥号的每个等级按人名排序
    for shihao_char in shihao_index:
        for rank in shihao_index[shihao_char]['ranks']:
            shihao_index[shihao_char]['ranks'][rank].sort(
                key=lambda x: x['name']
            )

    return dict(shihao_index)

def generate_html(shihao_index: Dict, output_file: Path):
    """生成谥号索引HTML页面"""

    # 按谥号字拼音排序
    import pypinyin
    sorted_shihaos = sorted(
        shihao_index.items(),
        key=lambda x: pypinyin.lazy_pinyin(x[0])[0]
    )

    # 生成拼音导航
    pinyin_nav = {}
    for shihao_char, _ in sorted_shihaos:
        initial = pypinyin.lazy_pinyin(shihao_char)[0][0].upper()
        if initial not in pinyin_nav:
            pinyin_nav[initial] = []
        pinyin_nav[initial].append(shihao_char)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>谥号索引 - 史记知识库</title>
    <link rel="stylesheet" href="../css/shiji-styles.css">
    <link rel="stylesheet" href="../css/entity-index.css">
    <style>
        /* 谥号索引特定样式 */
        .shihao-entry {
            margin: 2.5em 0;
            padding: 0;
            border: 1px solid #e6e0c0;
            border-radius: 8px;
            background: #fffef8;
        }

        .shihao-header {
            padding: 1.5em;
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .shihao-header:hover {
            background: #f8f5e8;
        }

        .shihao-char {
            font-size: 2.2em;
            color: #8B0000;
            border-bottom: 3px solid #d4af37;
            padding-bottom: 0.3em;
            margin: 0;
            display: inline-block;
        }

        .shihao-toggle {
            font-size: 0.6em;
            color: #999;
            margin-left: 0.5em;
            transition: transform 0.3s;
        }

        .shihao-entry.collapsed .shihao-toggle {
            transform: rotate(-90deg);
        }

        .shihao-content {
            padding: 0 1.5em 1.5em 1.5em;
            display: none;
        }

        .shihao-entry:not(.collapsed) .shihao-content {
            display: block;
        }

        .shihao-meaning {
            margin: 1em 0 1.5em 0;
            padding: 1em;
            background: #f8f5e8;
            border-left: 4px solid #b8a86a;
            font-style: italic;
            color: #555;
            line-height: 1.8;
        }

        .rank-group {
            margin: 1.5em 0 1.5em 1em;
            padding-left: 1.2em;
            border-left: 3px solid #d0c8a0;
        }

        .rank-group h3 {
            color: #5a4a2a;
            font-size: 1.3em;
            margin-bottom: 0.8em;
        }

        .rank-count {
            font-size: 0.8em;
            color: #999;
            font-weight: normal;
            margin-left: 0.5em;
        }

        .person-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .person-item {
            margin: 1em 0;
            padding: 0.8em;
            background: #fdfdf8;
            border: 1px solid #f0ece0;
            border-radius: 4px;
        }

        .person-item:hover {
            background: #f8f5e8;
            border-color: #d4af37;
        }

        .person-name {
            font-weight: 700;
            font-size: 1.1em;
            color: #8B4513;
            text-decoration: none;
        }

        .person-name:hover {
            color: #8B0000;
        }

        .chapter-refs {
            font-size: 0.85em;
            color: #999;
            margin-left: 0.8em;
        }

        .person-meta {
            font-size: 0.9em;
            color: #666;
            margin-top: 0.5em;
            padding-left: 1em;
        }

        .meta-item {
            display: inline-block;
            margin-right: 1.5em;
        }

        .stats-summary {
            background: #f0f7ff;
            border: 1px solid #b8d4f1;
            border-radius: 6px;
            padding: 1.2em;
            margin: 2em 0;
        }

        .stats-summary h2 {
            margin-top: 0;
            color: #2c5aa0;
            border-bottom: none;
        }
    </style>
    <script>
        function toggleShihao(element) {
            element.classList.toggle('collapsed');
        }

        // 页面加载后默认全部折叠
        window.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.shihao-entry').forEach(function(entry) {
                entry.classList.add('collapsed');
            });
        });
    </script>
</head>
<body>
<nav class="chapter-nav">
    <a href="../index.html" class="nav-home">回到主页</a>
    <a href="special_index.html" class="nav-next">专项索引</a>
</nav>

<h1>谥号索引</h1>
<p>《史记》中出现的谥号及使用该谥号的君主、诸侯、大夫。谥号是对死者生前事迹的评价，分为美谥、平谥、恶谥三类。</p>
<p style="font-size: 0.9em; color: #666; margin-top: 0.5em;">
  <strong>说明：</strong>汉代皇帝谥号完整形式为"孝X"（如孝文帝、孝武帝），简称时常省略"孝"字（文帝、武帝）。本索引中"孝文"与"文"、"孝惠"与"惠"等为同一人的不同称呼方式，分别列出。
</p>

<div class="stats-summary">
    <h2>统计概览</h2>
    <ul>
        <li>谥号种类: <strong>""" + str(len(shihao_index)) + """</strong> 个（含单字、双字及简称形式）</li>
        <li>使用谥号人物: <strong>""" + str(sum(data['total'] for data in shihao_index.values())) + """</strong> 人</li>
        <li>谥法来源: 《谥法解》（《逸周书》）</li>
    </ul>
</div>

<!-- 拼音导航 -->
<div class="pinyin-nav">
"""

    for initial in sorted(pinyin_nav.keys()):
        count = len(pinyin_nav[initial])
        html += f'  <a href="#letter-{initial}" class="pinyin-letter">{initial}<span class="letter-count">{count}</span></a>\n'

    html += '</div>\n\n<div class="shihao-index">\n'

    # 生成谥号条目
    current_initial = None
    for shihao_char, data in sorted_shihaos:
        initial = pypinyin.lazy_pinyin(shihao_char)[0][0].upper()

        # 添加字母分节
        if initial != current_initial:
            if current_initial is not None:
                html += '</div>\n'
            html += f'<div class="letter-section" id="letter-{initial}">\n'
            html += f'  <h2 class="letter-heading">{initial}</h2>\n'
            current_initial = initial

        html += f'  <div class="shihao-entry" id="shihao-{shihao_char}">\n'
        html += f'    <div class="shihao-header" onclick="toggleShihao(this.parentElement)">\n'
        html += f'      <h2 class="shihao-char">{shihao_char}<span class="shihao-toggle">▼</span></h2>\n'
        html += f'      <span class="rank-count" style="font-size: 0.9em;">共{data["total"]}人</span>\n'
        html += f'    </div>\n'
        html += f'    <div class="shihao-content">\n'

        # 谥法释义
        if data['meaning']:
            html += f'      <div class="shihao-meaning">\n'
            html += f'        <strong>谥法</strong>：{data["meaning"]}\n'
            html += f'      </div>\n'

        # 按爵位等级排序
        sorted_ranks = sorted(
            data['ranks'].items(),
            key=lambda x: RANK_LEVELS.index(x[0]) if x[0] in RANK_LEVELS else 999
        )

        for rank, persons in sorted_ranks:
            html += f'    <div class="rank-group">\n'
            html += f'      <h3>{shihao_char}{rank}<span class="rank-count">({len(persons)}人)</span></h3>\n'
            html += f'      <ul class="person-list">\n'

            for person in persons:
                html += f'        <li class="person-item">\n'
                html += f'          <a href="../entities/person.html#entity-{person["name"]}" class="person-name">{person["name"]}</a>\n'

                # 章节引用
                if person['chapters']:
                    chapters_str = ', '.join(person['chapters'][:3])
                    if len(person['chapters']) > 3:
                        chapters_str += f' 等{len(person['chapters'])}章'
                    html += f'          <span class="chapter-refs">({chapters_str})</span>\n'

                # 元数据（生卒年）
                meta_items = []
                if 'birth' in person and 'death' in person:
                    birth_year = person['birth']
                    death_year = person['death']
                    if birth_year < 0:
                        birth_str = f"前{abs(birth_year)}"
                    else:
                        birth_str = str(birth_year)
                    if death_year < 0:
                        death_str = f"前{abs(death_year)}"
                    else:
                        death_str = str(death_year)
                    meta_items.append(f'生卒: {birth_str}–{death_str}年')
                elif 'death' in person:
                    death_year = person['death']
                    death_str = f"前{abs(death_year)}" if death_year < 0 else str(death_year)
                    meta_items.append(f'卒于: {death_str}年')

                if meta_items:
                    html += f'          <div class="person-meta">\n'
                    for item in meta_items:
                        html += f'            <span class="meta-item">{item}</span>\n'
                    html += f'          </div>\n'

                html += f'        </li>\n'

            html += f'      </ul>\n'
            html += f'    </div>\n'

        html += f'    </div>\n'  # Close shihao-content
        html += f'  </div>\n'  # Close shihao-entry

    html += """</div>
</div>

<nav class="chapter-nav">
    <a href="../index.html" class="nav-home">回到主页</a>
    <a href="special_index.html" class="nav-next">专项索引</a>
</nav>
</body>
</html>
"""

    # 保存文件
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ 已生成谥号索引: {output_file}")

def main():
    # 项目根目录
    root = Path(__file__).parent.parent.parent.parent

    # 输入文件
    entity_index_file = root / 'kg' / 'entities' / 'data' / 'entity_index.json'
    lifespans_file = root / 'kg' / 'entities' / 'data' / 'person_lifespans.json'

    # 输出文件
    output_json = root / 'kg' / 'entities' / 'data' / 'shihao_index.json'
    output_html = root / 'docs' / 'special' / 'shihao.html'

    print("正在构建谥号索引...")
    print(f"  加载实体索引: {entity_index_file}")

    # 加载数据
    entity_index = load_entity_index(entity_index_file)
    lifespans = load_person_lifespans(lifespans_file)

    # 构建索引
    print("  提取谥号信息...")
    shihao_index = build_shihao_index(entity_index, lifespans)

    print(f"\n统计结果:")
    print(f"  谥号种类: {len(shihao_index)} 个")
    print(f"  使用谥号人物: {sum(data['total'] for data in shihao_index.values())} 人")

    # 显示高频谥号 Top 10
    print(f"\n高频谥号 Top 10:")
    sorted_by_count = sorted(
        shihao_index.items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )
    for i, (char, data) in enumerate(sorted_by_count[:10], 1):
        ranks_str = ', '.join([f"{r}({len(ps)})" for r, ps in data['ranks'].items()])
        print(f"  {i}. {char} ({data['total']}人): {ranks_str}")

    # 保存JSON
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(shihao_index, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 已保存索引数据: {output_json}")

    # 生成HTML
    print("  生成HTML页面...")
    generate_html(shihao_index, output_html)

    print("\n✓ 谥号索引构建完成！")

if __name__ == '__main__':
    main()
