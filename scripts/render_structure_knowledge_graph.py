#!/usr/bin/env python3
"""
生成交互式知识图谱可视化（使用vis.js）
"""

import json
import re
from pathlib import Path

def load_annotated_text(chapter_file):
    """从原始标注文件中提取带标注的段落文本"""
    annotated_texts = {}

    with open(chapter_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配段落：[编号] 文本内容
    pattern = r'\[([0-9.]+)\]\s+([^\n\[]+(?:\n(?!\[)[^\n]+)*)'
    matches = re.findall(pattern, content)

    for anchor, text in matches:
        # 清理文本，去除多余空白
        text = text.strip()
        annotated_texts[anchor] = text

    return annotated_texts

def generate_paragraph_title(para):
    """为段落生成4-6字的标题"""
    anchor = para['anchor']
    summary = para['summary']
    section = para['section']

    # 预定义的标题映射
    title_map = {
        '1': '黄帝出身', '1.1': '征伐诸侯', '1.2': '擒蚩尤', '1.3': '为天子',
        '3': '治理天下', '4': '黄帝子嗣', '4.1': '嫘祖二子', '4.2': '黄帝崩',
        '5': '颛顼德行', '6': '颛顼崩',
        '7': '帝喾世系', '8': '帝喾德行', '9': '帝喾崩',
        '10': '帝尧德行', '11': '制定历法', '11.5': '闰月四时', '13.8': '尧选舜',
        '14': '舜摄政', '14.1': '巡狩礼制', '14.2': '刑法教化',
        '15': '惩四罪', '15.5': '天下服',
        '16': '尧崩', '16.1': '授舜天下', '16.2': '舜让辟',
        '17': '舜世系', '18': '父弟欲杀', '19': '舜事亲孝',
        '20': '尧妻二女', '20.1': '焚廪脱险', '20.2': '实井逃生', '20.3': '复事瞽叟',
        '21': '八恺八元', '22.6': '流四凶',
        '23': '舜入麓', '23.1': '举十贤', '23.2': '分职任能', '23.3': '三年考功',
        '24': '群臣成功', '25': '舜崩', '25.1': '舜让禹', '25.2': '不敢专',
        '26': '五帝世系', '27': '太史公曰'
    }

    if anchor in title_map:
        return title_map[anchor]

    # 默认：使用section前4字
    return section[:4]

def generate_html(json_path, output_path):
    """生成HTML页面"""

    # 读取JSON数据
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    paragraphs = data['paragraphs']
    relations = data['relations']

    # 加载原始标注文本
    chapter_file = Path('/home/baojie/work/shiji-kb/chapter_md/001_五帝本纪.tagged.md')
    annotated_texts = load_annotated_text(chapter_file)

    # 关系类型配置（添加2字简称）
    relation_config = {
        'temporal': {'color': '#999999', 'name': '时序关系', 'short_name': '时序', 'width': 5, 'dashes': False},  # 最粗
        'causal': {'color': '#e74c3c', 'name': '因果关系', 'short_name': '因果', 'width': 3, 'dashes': False},
        'genealogy': {'color': '#9b59b6', 'name': '世系关系', 'short_name': '世系', 'width': 4, 'dashes': False},
        'hierarchy': {'color': '#3498db', 'name': '总分关系', 'short_name': '总分', 'width': 2, 'dashes': [5, 5]},
        'parallel': {'color': '#2ecc71', 'name': '并列关系', 'short_name': '并列', 'width': 2, 'dashes': [10, 5]},
        'contrast': {'color': '#e67e22', 'name': '对比关系', 'short_name': '对比', 'width': 3, 'dashes': False},
        'meta': {'color': '#95a5a6', 'name': '元评论', 'short_name': '评论', 'width': 2, 'dashes': [2, 2]},
        'elaboration': {'color': '#1abc9c', 'name': '补充说明', 'short_name': '补充', 'width': 2, 'dashes': False}
    }

    # 节点颜色（按section）
    section_colors = {
        '黄帝': '#FFD700',
        '帝颛顼': '#87CEEB',
        '帝喾': '#98FB98',
        '帝尧': '#FFA07A',
        '帝舜': '#DDA0DD',
        '举贤任能': '#F0E68C',
        '五帝': '#E0E0E0',
        '太史公': '#D3D3D3'
    }

    # 构建节点数据（JSON格式）
    nodes = []
    for para in paragraphs:
        section_color = section_colors.get(para['section'], '#cccccc')

        # 生成段落标题
        para_title = generate_paragraph_title(para)

        # 根据段落字数计算节点大小（字数越多，节点越大）
        char_count = len(para['full_text'])
        # 基础大小 + 按字数缩放（每100字增加1单位）
        # 超大尺寸：基础从200开始，最大不超过300
        size = min(200 + (char_count / 100) * 8, 300)
        size = max(size, 150)  # 最小150

        # 构建纯文本tooltip（不使用HTML标签，使用换行）
        subsection_text = para.get('subsection', '')
        tooltip_parts = [
            f"[{para['anchor']}] {para_title}",
            f"章节: {para['section']}"
        ]
        if subsection_text:
            tooltip_parts.append(f"小节: {subsection_text}")
        tooltip_parts.append('')  # 空行
        tooltip_parts.append(para['summary'][:80] + ('...' if len(para['summary']) > 80 else ''))

        tooltip = '\\n'.join(tooltip_parts)

        # 编号显示在圆圈内，标题保存为自定义属性用于Canvas绘制
        nodes.append({
            'id': para['anchor'],
            'label': para['anchor'],  # 只显示编号在圆圈内
            'title': tooltip,  # 纯文本tooltip
            'group': para['section'],
            'color': section_color,
            'size': size,
            'font': {
                'size': 48,  # 编号字号（超大字号）
                'color': '#000',
                'face': 'Arial',
                'bold': True
            },
            'para_title': para_title,  # 保存标题用于Canvas绘制
            'full_text': annotated_texts.get(para['anchor'], para['full_text']),  # 优先使用带标注的文本
            'section_name': para['section'],  # 章节名
            'subsection_name': para.get('subsection', '')  # 小节名
        })

    # 构建边数据（JSON格式）
    edges = []
    edge_counter = 0  # 用于生成唯一ID
    for rel in relations:
        rel_type = rel['type']
        config = relation_config.get(rel_type, {'color': '#999', 'short_name': '关系', 'width': 1, 'dashes': False})

        # 使用计数器生成唯一ID，避免重复
        edge_counter += 1
        edge_id = f"edge_{edge_counter}"

        edge = {
            'id': edge_id,  # 唯一ID
            'from': rel['source'],
            'to': rel['target'],
            'color': config['color'],
            'width': config['width'],
            'title': rel.get('description', config['name']),  # tooltip显示详细描述
            'label': config['short_name'],  # 在边上显示2字关系名
            'arrows': 'to',
            'smooth': {'type': 'curvedCW', 'roundness': 0.2},
            'font': {
                'size': 9,
                'color': config['color'],
                'strokeWidth': 0,
                'align': 'top',  # 文字在边的上方，避免与箭头重叠
                'background': 'rgba(255,255,255,0.7)',  # 半透明白色背景
                'vadjust': -5  # 垂直向上偏移5像素
            },
            # 保存原始的from-to信息，用于后续的悬停效果
            'original_key': rel['source'] + '-' + rel['target']
        }

        if config['dashes']:
            edge['dashes'] = config['dashes']

        edges.append(edge)

    # 统计数据
    relation_stats = {}
    for rel in relations:
        rel_type = rel['type']
        if rel_type not in relation_stats:
            relation_stats[rel_type] = 0
        relation_stats[rel_type] += 1

    # 生成HTML
    # 先将nodes和edges转为JSON字符串
    nodes_json = json.dumps(nodes, ensure_ascii=False, indent=2)
    edges_json = json.dumps(edges, ensure_ascii=False, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>《史记·五帝本纪》段落关系知识图谱</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network@9.1.2/standalone/umd/vis-network.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;  /* 确保padding和border计入宽高 */
        }}

        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;  /* 防止页面滚动 */
        }}

        body {{
            font-family: "Songti SC", "SimSun", "Microsoft YaHei", sans-serif;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;  /* 垂直布局：header在上，container在下 */
        }}

        .header {{
            background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
            color: white;
            padding: 15px 20px;  /* 减小上下padding */
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            flex-shrink: 0;  /* header不会被压缩 */
        }}

        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 1.8em;  /* 稍微减小字号 */
        }}

        .header p {{
            margin: 3px 0;
            opacity: 0.9;
            font-size: 0.9em;
        }}

        .container {{
            display: flex;
            flex: 1;  /* 占据剩余所有空间 */
            position: relative;
            overflow: hidden;  /* 防止container内容超出 */
        }}

        .sidebar {{
            width: 300px;
            flex-shrink: 0;  /* 防止侧边栏被压缩 */
            background: white;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }}

        .sidebar h3 {{
            color: #8B4513;
            border-bottom: 2px solid #8B4513;
            padding-bottom: 10px;
            margin-top: 0;
        }}

        .stats-item {{
            margin: 10px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
            border-left: 3px solid #8B4513;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 0.9em;
        }}

        .legend-color {{
            width: 30px;
            height: 3px;
            margin-right: 10px;
        }}

        .legend-color.dashed {{
            background: repeating-linear-gradient(
                to right,
                currentColor 0px,
                currentColor 5px,
                transparent 5px,
                transparent 10px
            );
        }}

        .section-legend {{
            margin-top: 20px;
        }}

        .section-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 0.9em;
        }}

        .section-circle {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}

        #graph {{
            flex: 1;
            background: white;
            width: 100%;
            height: 100%;
            position: relative;  /* 让按钮相对于graph定位 */
        }}

        .controls {{
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 10000;  /* 高于vis按钮 */
        }}

        .btn {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #8B4513;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            padding: 0;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}

        .btn:hover {{
            background: #A0522D;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            transform: scale(1.05);
        }}

        .btn:active {{
            transform: scale(0.95);
        }}

        .filter-group {{
            margin: 15px 0;
        }}

        .filter-group label {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            cursor: pointer;
            font-size: 0.9em;
        }}

        .filter-group input[type="checkbox"] {{
            margin-right: 8px;
        }}

        .notice {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            margin: 15px 0;
            border-radius: 5px;
            font-size: 0.85em;
            color: #856404;
        }}

        /* 阅读卡片样式 */
        .reading-card {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            width: 600px;
            max-width: 90%;
            max-height: 80%;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            z-index: 10001;
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}

        .reading-card.show {{
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
        }}

        .card-header {{
            background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }}

        .card-anchor {{
            font-size: 1.5em;
            font-weight: bold;
            margin-right: 15px;
        }}

        .card-title {{
            flex: 1;
            font-size: 1.2em;
            font-weight: bold;
        }}

        .card-close {{
            background: none;
            border: none;
            color: white;
            font-size: 2em;
            cursor: pointer;
            padding: 0;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            transition: background 0.2s;
            line-height: 1;
        }}

        .card-close:hover {{
            background: rgba(255,255,255,0.2);
        }}

        .card-section {{
            padding: 15px 20px;
            background: #f9f9f9;
            border-bottom: 1px solid #ddd;
            font-size: 0.95em;
            color: #666;
            flex-shrink: 0;
        }}

        .card-content {{
            padding: 25px;
            font-size: 1.1em;
            line-height: 2;
            overflow-y: auto;
            flex: 1;
        }}

        .card-footer {{
            padding: 15px 20px;
            background: #f9f9f9;
            border-top: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }}

        .card-nav-btn {{
            background: #8B4513;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.95em;
            transition: all 0.2s;
        }}

        .card-nav-btn:hover {{
            background: #A0522D;
            transform: scale(1.05);
        }}

        .card-nav-btn:disabled {{
            background: #ccc;
            cursor: not-allowed;
            opacity: 0.5;
        }}

        .card-progress {{
            color: #666;
            font-size: 0.9em;
        }}

        /* 标注高亮样式 */
        .card-content .entity {{
            background: rgba(255, 215, 0, 0.3);
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 500;
        }}

        .card-content .entity-PERSON {{
            background: rgba(139, 69, 19, 0.15);
            color: #8B4513;
        }}

        .card-content .entity-PLACE {{
            background: rgba(52, 152, 219, 0.15);
            color: #2980b9;
        }}

        .card-content .entity-EVENT {{
            background: rgba(231, 76, 60, 0.15);
            color: #c0392b;
        }}

        /* 节点高亮动画 */
        @keyframes nodeHighlight {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.3); }}
        }}

        .node-highlight {{
            animation: nodeHighlight 0.6s ease-in-out;
        }}

    </style>
</head>
<body>
    <div class="header">
        <h1>《史记·五帝本纪》段落关系知识图谱</h1>
        <p>44个段落 × 101个关系 × 8种关系类型</p>
        <p style="font-size: 0.9em;">SKILL-02d: 段落语义关系建模</p>
    </div>

    <div class="container">
        <div class="sidebar">
            <h3>📊 统计数据</h3>
            <div class="stats-item">
                <strong>总段落数</strong>: {len(paragraphs)}个<br>
                <strong>总关系数</strong>: {len(relations)}个<br>
                <strong>大节数</strong>: 8个<br>
                <strong>关系类型</strong>: 8种
            </div>

            <h3>🎨 关系类型图例</h3>
'''

    # 添加关系图例
    for rel_type, config in relation_config.items():
        count = relation_stats.get(rel_type, 0)
        dashed_class = 'dashed' if config['dashes'] else ''
        html += f'''
            <div class="legend-item">
                <div class="legend-color {dashed_class}" style="color: {config['color']}; background: {config['color']}; width: 40px; height: {config['width']}px;"></div>
                <span>{config['name']} ({count})</span>
            </div>'''

    html += '''
            <h3>📖 章节图例</h3>
            <div class="section-legend">
'''

    # 添加章节图例
    for section, color in section_colors.items():
        html += f'''
                <div class="section-item">
                    <div class="section-circle" style="background: {color};"></div>
                    <span>{section}</span>
                </div>'''

    html += '''
            </div>

            <h3>🔍 关系筛选</h3>
            <div class="filter-group">
                <label>
                    <input type="checkbox" class="relation-filter" value="temporal" checked>
                    时序关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="causal" checked>
                    因果关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="genealogy" checked>
                    世系关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="hierarchy" checked>
                    总分关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="parallel" checked>
                    并列关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="contrast" checked>
                    对比关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="meta" checked>
                    元评论
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="elaboration" checked>
                    补充说明
                </label>
            </div>

            <div class="notice">
                <strong>💡 操作提示</strong><br>
                • 拖动节点改变位置<br>
                • 滚轮缩放视图<br>
                • 悬停节点查看详情<br>
                • <strong>双击节点跳转到原文</strong><br>
                • 使用筛选器控制显示的关系类型
            </div>
        </div>

        <div id="graph"></div>

        <div class="controls">
            <button class="btn" onclick="toggleAutoPlay()" title="自动播放" id="playBtn">▶</button>
            <button class="btn" onclick="cycleSpeed()" title="播放速度: 1x" id="speedBtn">1×</button>
            <button class="btn" onclick="zoomIn()" title="放大">+</button>
            <button class="btn" onclick="zoomOut()" title="缩小">−</button>
            <button class="btn" onclick="fitToView()" title="适应视图">⊙</button>
            <button class="btn" onclick="moveUp()" title="向上移动">↑</button>
            <button class="btn" onclick="moveDown()" title="向下移动">↓</button>
            <button class="btn" onclick="moveLeft()" title="向左移动">←</button>
            <button class="btn" onclick="moveRight()" title="向右移动">→</button>
            <button class="btn" onclick="resetLayout()" title="随机布局">⟲</button>
            <button class="btn" onclick="togglePhysics()" title="切换物理引擎">⚡</button>
        </div>

        <!-- 阅读卡片 -->
        <div id="readingCard" class="reading-card">
            <div class="card-header">
                <span class="card-anchor"></span>
                <span class="card-title"></span>
                <button class="card-close" onclick="closeReadingCard()">×</button>
            </div>
            <div class="card-section"></div>
            <div class="card-content"></div>
            <div class="card-footer">
                <button class="card-nav-btn" onclick="navigatePrevious()" id="prevBtn">← 上一段</button>
                <span class="card-progress"></span>
                <button class="card-nav-btn" onclick="navigateNext()" id="nextBtn">下一段 →</button>
            </div>
        </div>
    </div>

    <script>
        // 数据
        const nodesData = ''' + nodes_json + ''';
        const edgesData = ''' + edges_json + ''';

        // 创建数据集
        const nodes = new vis.DataSet(nodesData);
        const edges = new vis.DataSet(edgesData);

        // 网络配置
        const options = {
            nodes: {
                shape: 'circle',  // 使用circle而不是dot，可以在内部显示文字
                borderWidth: 2,
                borderWidthSelected: 4,
                shadow: true,
                font: {
                    size: 48,  // 超大全局字号
                    color: '#000',
                    face: 'Arial',
                    vadjust: 0,
                    strokeWidth: 0
                },
                scaling: {
                    label: {
                        enabled: false  // 禁用标签缩放，保持字体大小固定
                    }
                },
                labelHighlightBold: false
            },
            edges: {
                smooth: {
                    type: 'curvedCW',
                    roundness: 0.2
                },
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.5
                    }
                },
                shadow: true,
                font: {
                    size: 20,  // 边标签字号
                    color: '#333',
                    face: 'Arial',
                    background: 'rgba(255,255,255,0.8)',  // 白色半透明背景
                    strokeWidth: 0,
                    align: 'middle'
                }
            },
            physics: {
                enabled: true,
                barnesHut: {
                    gravitationalConstant: -8000,  // 增加排斥力，让节点更分散
                    centralGravity: 0.1,  // 减少中心引力
                    springLength: 200,  // 增加弹簧长度，让节点距离更远
                    springConstant: 0.02,
                    damping: 0.09,
                    avoidOverlap: 1  // 避免节点重叠
                },
                stabilization: {
                    enabled: true,
                    iterations: 500,
                    updateInterval: 25,
                    fit: true
                }
            },
            layout: {
                improvedLayout: true,
                randomSeed: undefined  // 每次随机初始化
            },
            interaction: {
                hover: true,
                tooltipDelay: 100,
                navigationButtons: false,  // 禁用vis.js自带的导航按钮，使用自定义按钮
                keyboard: true,
                zoomView: true,
                dragView: true
            }
        };

        // 创建网络
        const container = document.getElementById('graph');
        console.log('Container:', container);
        console.log('Nodes count:', nodesData.length);
        console.log('Edges count:', edgesData.length);

        const data = {
            nodes: nodes,
            edges: edges
        };
        const network = new vis.Network(container, data, options);

        console.log('Network created');
        console.log('Container size:', container.clientWidth, 'x', container.clientHeight);


        // 强制刷新canvas尺寸以填满容器
        window.addEventListener('resize', function() {
            network.redraw();
        });

        // 初始化时也刷新一次
        setTimeout(function() {
            network.redraw();
            network.fit();
        }, 100);

        // 自定义绘制：在节点下方绘制标题
        let debugOnce = false;
        network.on("afterDrawing", function(ctx) {
            const nodePositions = network.getPositions();

            nodesData.forEach(node => {
                if (node.para_title && nodePositions[node.id]) {
                    const canvasPos = nodePositions[node.id];
                    // 从原始数据获取size值
                    const nodeRadius = node.size || 45;

                    // 调试：只打印一次第一个节点的信息
                    if (!debugOnce && node.id === '1') {
                        console.log('Node 1 size:', nodeRadius);
                        console.log('Node 1 position:', canvasPos);
                        debugOnce = true;
                    }

                    // 设置字体和样式
                    ctx.font = 'bold 36px "Songti SC", "SimSun", "Microsoft YaHei", serif';
                    ctx.fillStyle = '#333';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';

                    // 在节点下方绘制标题（使用固定偏移量）
                    // 标题紧贴圆圈底部
                    const yOffset = 80;  // 调整偏移量以匹配超大圆圈
                    ctx.fillText(node.para_title, canvasPos.x, canvasPos.y + yOffset);
                }
            });
        });

        // 网络初始化完成后适应视图
        network.once('stabilized', function() {
            console.log('Network stabilized');
            fitToView();
        });

        // 鼠标悬停效果：根据距离调整节点和边的透明度
        let hoveredNodeId = null;

        network.on("hoverNode", function(params) {
            hoveredNodeId = params.node;
            updateNodesAndEdgesOpacity(hoveredNodeId);
        });

        network.on("blurNode", function(params) {
            hoveredNodeId = null;
            resetNodesAndEdgesOpacity();
        });

        // 计算图中两个节点之间的最短路径距离（BFS）
        function getShortestDistance(fromNode, toNode) {
            if (fromNode === toNode) return 0;

            const visited = new Set();
            const queue = [{node: fromNode, distance: 0}];
            visited.add(fromNode);

            while (queue.length > 0) {
                const {node, distance} = queue.shift();

                // 获取当前节点的所有邻居
                const connectedEdges = edgesData.filter(e => e.from === node || e.to === node);
                for (const edge of connectedEdges) {
                    const neighbor = edge.from === node ? edge.to : edge.from;
                    if (neighbor === toNode) {
                        return distance + 1;
                    }
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push({node: neighbor, distance: distance + 1});
                    }
                }
            }

            return Infinity; // 不连通
        }

        function updateNodesAndEdgesOpacity(hoveredId) {
            // 计算所有节点到悬停节点的距离
            const distances = {};
            let maxDistance = 0;

            nodesData.forEach(node => {
                const dist = getShortestDistance(hoveredId, node.id);
                distances[node.id] = dist;
                if (dist !== Infinity && dist > maxDistance) {
                    maxDistance = dist;
                }
            });

            // 更新节点透明度
            const updatedNodes = nodesData.map(node => {
                const dist = distances[node.id];
                let opacity = 1.0;

                if (dist === 0) {
                    opacity = 1.0; // 悬停节点自己
                } else if (dist === Infinity) {
                    opacity = 0.1; // 不连通的节点
                } else {
                    // 根据距离计算透明度：距离越远越淡
                    opacity = Math.max(0.15, 1.0 - (dist / (maxDistance + 1)) * 0.85);
                }

                return {
                    id: node.id,
                    opacity: opacity
                };
            });

            nodes.update(updatedNodes);

            // 更新边的透明度和宽度
            const updatedEdges = edgesData.map(edge => {
                const fromDist = distances[edge.from] || Infinity;
                const toDist = distances[edge.to] || Infinity;

                // 直接相关的边（距离为0-1之间）
                const isDirect = (fromDist === 0 && toDist === 1) || (fromDist === 1 && toDist === 0);

                let opacity, width;
                if (isDirect) {
                    opacity = 1.0;
                    width = edge.width * 2; // 加粗
                } else {
                    // 根据两端节点的最近距离计算透明度
                    const minDist = Math.min(fromDist, toDist);
                    if (minDist === Infinity) {
                        opacity = 0.05;
                    } else {
                        opacity = Math.max(0.1, 1.0 - (minDist / (maxDistance + 1)) * 0.9);
                    }
                    width = edge.width;
                }

                return {
                    id: edge.id,  // 使用边的唯一ID
                    opacity: opacity,
                    width: width
                };
            });

            edges.update(updatedEdges);
        }

        function resetNodesAndEdgesOpacity() {
            // 恢复所有节点
            const updatedNodes = nodesData.map(node => ({
                id: node.id,
                opacity: 1.0
            }));
            nodes.update(updatedNodes);

            // 恢复所有边
            const updatedEdges = edgesData.map(edge => ({
                id: edge.id,  // 使用边的唯一ID
                opacity: 1.0,
                width: edge.width
            }));
            edges.update(updatedEdges);
        }

        // 适应视图：尽可能放大填满容器
        // 缩放功能
        function zoomIn() {
            const scale = network.getScale();
            network.moveTo({
                scale: scale * 1.2,
                animation: {
                    duration: 300,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }

        function zoomOut() {
            const scale = network.getScale();
            network.moveTo({
                scale: scale / 1.2,
                animation: {
                    duration: 300,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }

        // 移动功能
        function moveUp() {
            const position = network.getViewPosition();
            network.moveTo({
                position: { x: position.x, y: position.y - 100 },
                animation: {
                    duration: 300,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }

        function moveDown() {
            const position = network.getViewPosition();
            network.moveTo({
                position: { x: position.x, y: position.y + 100 },
                animation: {
                    duration: 300,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }

        function moveLeft() {
            const position = network.getViewPosition();
            network.moveTo({
                position: { x: position.x - 100, y: position.y },
                animation: {
                    duration: 300,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }

        function moveRight() {
            const position = network.getViewPosition();
            network.moveTo({
                position: { x: position.x + 100, y: position.y },
                animation: {
                    duration: 300,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }

        // 适应视图
        function fitToView() {
            network.fit({
                animation: {
                    duration: 500,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }

        // 物理引擎开关
        let physicsEnabled = true;
        function togglePhysics() {
            physicsEnabled = !physicsEnabled;
            network.setOptions({ physics: { enabled: physicsEnabled } });

            // 更新按钮图标和提示（第11个按钮）
            const btn = document.querySelector('.controls button:nth-child(11)');
            if (btn) {
                btn.textContent = physicsEnabled ? '⚡' : '⏸';
                btn.title = physicsEnabled ? '关闭物理引擎' : '开启物理引擎';
                btn.style.background = physicsEnabled ? '#8B4513' : '#999';
            }

            console.log('物理引擎已' + (physicsEnabled ? '开启' : '关闭'));
        }

        // 随机生成新布局
        function resetLayout() {
            // 为每个节点生成随机位置
            const nodeIds = nodes.getIds();
            const updatedNodes = nodeIds.map(id => {
                return {
                    id: id,
                    x: Math.random() * 2000 - 1000,  // -1000 到 1000
                    y: Math.random() * 2000 - 1000
                };
            });

            // 更新节点位置
            nodes.update(updatedNodes);

            // 启用物理引擎让布局稳定下来
            network.setOptions({ physics: { enabled: true } });

            // 稳定后自动适应视图
            network.once('stabilizationIterationsDone', function() {
                fitToView();
            });
        }

        // 自动播放功能
        let autoPlayTimer = null;
        let currentPlayIndex = 0;
        let isPlaying = false;
        let sortedNodes = [];
        let playbackSpeed = 1; // 播放速度倍率：0.2, 0.5, 1, 2, 5
        const speedOptions = [0.2, 0.5, 1, 2, 5];

        // 处理标注高亮
        function highlightAnnotations(text) {
            // 匹配标注格式：〖@黄帝〗 或 〖@黄帝|轩辕氏〗（消歧）
            // 支持的标注类型：@ 人名、# 地名、! 事件、? 概念、& 族群、+ 动植物、= 地点、~ 国家、; 官职、_抽象概念、:动作、^仪式、•物品、⟦动作⟧
            return text.replace(/〖([@#!?&+=~;_:^•])([^〗|]+)(?:\\|[^〗]+)?〗|⟦([^⟧]+)⟧/g, (match, type, content, action) => {
                // 处理动作标记 ⟦◈动作⟧ 或 ⟦动作⟧
                if (action) {
                    // 去掉 ◈◉◇○● 等符号，只保留实际动词
                    const verb = action.replace(/^[◈◉◇○●]+/, '');
                    return `<span class="entity-EVENT">${verb}</span>`;
                }

                let className = 'entity';
                // 根据标注类型设置样式类
                if (type === '@') className = 'entity-PERSON';
                else if (type === '#' || type === '=') className = 'entity-PLACE';
                else if (type === '!' || type === ':' || type === '^') className = 'entity-EVENT';

                // 返回带高亮的文本（只显示实际名称，不显示消歧后缀）
                return `<span class="${className}">${content}</span>`;
            });
        }

        // 根据字数计算阅读时间（每分钟300字），应用速度倍率
        function calculateReadingTime(text) {
            const charCount = text.length;
            const readingSpeed = 300; // 每分钟300字
            const seconds = Math.max(3, Math.ceil((charCount / readingSpeed) * 60)); // 最少3秒
            return (seconds * 1000) / playbackSpeed; // 除以速度倍率（速度越快，时间越短）
        }

        // 切换播放速度
        function cycleSpeed() {
            const currentIndex = speedOptions.indexOf(playbackSpeed);
            const nextIndex = (currentIndex + 1) % speedOptions.length;
            playbackSpeed = speedOptions[nextIndex];

            // 更新按钮显示
            const speedBtn = document.getElementById('speedBtn');
            if (speedBtn) {
                if (playbackSpeed === 1) {
                    speedBtn.textContent = '1×';
                } else if (playbackSpeed < 1) {
                    speedBtn.textContent = `${playbackSpeed}×`;
                } else {
                    speedBtn.textContent = `${playbackSpeed}×`;
                }
                speedBtn.title = `播放速度: ${playbackSpeed}x`;
            }

            console.log('播放速度已切换到:', playbackSpeed + 'x');
        }

        function showReadingCard(nodeId) {
            const node = nodesData.find(n => n.id === nodeId);
            if (!node) return;

            // 初始化排序节点列表
            if (sortedNodes.length === 0) {
                sortedNodes = [...nodesData].sort((a, b) => {
                    return parseFloat(a.id) - parseFloat(b.id);
                });
            }

            const card = document.getElementById('readingCard');
            const anchor = card.querySelector('.card-anchor');
            const title = card.querySelector('.card-title');
            const section = card.querySelector('.card-section');
            const content = card.querySelector('.card-content');
            const progress = card.querySelector('.card-progress');
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');

            anchor.textContent = node.id;
            title.textContent = node.para_title;

            let sectionText = node.section_name;
            if (node.subsection_name) {
                sectionText += ' > ' + node.subsection_name;
            }
            section.textContent = sectionText;

            // 处理标注高亮
            content.innerHTML = highlightAnnotations(node.full_text);

            // 更新进度
            currentPlayIndex = sortedNodes.findIndex(n => n.id === nodeId);
            progress.textContent = `${currentPlayIndex + 1} / ${sortedNodes.length}`;

            // 更新按钮状态
            prevBtn.disabled = (currentPlayIndex === 0);
            nextBtn.disabled = (currentPlayIndex === sortedNodes.length - 1);

            // 显示卡片
            card.classList.add('show');

            // 聚焦到节点
            network.focus(nodeId, {
                scale: 1.5,
                animation: {
                    duration: 500,
                    easingFunction: 'easeInOutQuad'
                }
            });

            // 高亮节点（通过选中状态）
            network.selectNodes([nodeId]);
        }

        function closeReadingCard() {
            const card = document.getElementById('readingCard');
            card.classList.remove('show');
            network.unselectAll();
        }

        function toggleAutoPlay() {
            isPlaying = !isPlaying;
            const playBtn = document.getElementById('playBtn');

            if (isPlaying) {
                playBtn.textContent = '⏸';
                playBtn.title = '暂停播放';
                startAutoPlay();
            } else {
                playBtn.textContent = '▶';
                playBtn.title = '自动播放';
                stopAutoPlay();
            }
        }

        function startAutoPlay() {
            // 初始化排序节点列表
            if (sortedNodes.length === 0) {
                sortedNodes = [...nodesData].sort((a, b) => {
                    return parseFloat(a.id) - parseFloat(b.id);
                });
            }

            currentPlayIndex = 0;
            playNextNode();
        }

        function playNextNode() {
            if (!isPlaying || currentPlayIndex >= sortedNodes.length) {
                stopAutoPlay();
                return;
            }

            const node = sortedNodes[currentPlayIndex];
            showReadingCard(node.id);

            // 根据字数计算阅读时间
            const readingTime = calculateReadingTime(node.full_text);

            autoPlayTimer = setTimeout(() => {
                currentPlayIndex++;
                playNextNode();
            }, readingTime);
        }

        // 前后导航函数
        function navigatePrevious() {
            if (currentPlayIndex > 0) {
                currentPlayIndex--;
                const node = sortedNodes[currentPlayIndex];
                showReadingCard(node.id);
            }
        }

        function navigateNext() {
            if (currentPlayIndex < sortedNodes.length - 1) {
                currentPlayIndex++;
                const node = sortedNodes[currentPlayIndex];
                showReadingCard(node.id);
            }
        }

        function stopAutoPlay() {
            if (autoPlayTimer) {
                clearTimeout(autoPlayTimer);
                autoPlayTimer = null;
            }
            isPlaying = false;
            const playBtn = document.getElementById('playBtn');
            playBtn.textContent = '▶';
            playBtn.title = '自动播放';
            closeReadingCard();
        }

        // 关系筛选
        const relationTypeMap = new Map();
        const colorToType = {
            '#999999': 'temporal',
            '#e74c3c': 'causal',
            '#9b59b6': 'genealogy',
            '#3498db': 'hierarchy',
            '#2ecc71': 'parallel',
            '#e67e22': 'contrast',
            '#95a5a6': 'meta',
            '#1abc9c': 'elaboration'
        };

        edgesData.forEach((edge, index) => {
            relationTypeMap.set(edge.id, colorToType[edge.color] || 'unknown');
        });

        document.querySelectorAll('.relation-filter').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedTypes = Array.from(document.querySelectorAll('.relation-filter:checked'))
                    .map(cb => cb.value);

                const filteredEdges = edgesData.filter(edge => {
                    const edgeType = relationTypeMap.get(edge.id);
                    return checkedTypes.includes(edgeType);
                });

                edges.clear();
                edges.add(filteredEdges);
            });
        });

        // 节点单击事件
        network.on("selectNode", function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                console.log('Selected node:', nodeId);
            }
        });

        // 双击节点跳转到段落详情页
        network.on("doubleClick", function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                // 跳转到五帝本纪页面，带锚点
                const url = '../001_五帝本纪.html#para-' + nodeId;
                window.open(url, '_blank');
            }
        });

        // 稳定后适应视图
        network.once('stabilized', function() {
            network.fit();
        });
    </script>
</body>
</html>'''

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✅ 知识图谱HTML已生成: {output_path}')
    print(f'   节点数: {len(nodes)}')
    print(f'   边数: {len(edges)}')
    print(f'   关系类型: {len(relation_config)}种')

def main():
    json_path = Path('/home/baojie/work/shiji-kb/kg/structure/data/paragraph_relations_001_enhanced.json')
    output_path = Path('/home/baojie/work/shiji-kb/docs/special/structure.html')

    generate_html(json_path, output_path)

if __name__ == '__main__':
    main()
