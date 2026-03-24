# 段落语义关系知识图谱说明文档

## 概述

本文档说明《史记》章节段落间语义关系的数据结构和使用方法。

## 数据文件

### `data/paragraph_relations_001_enhanced.json`

**完整版段落关系数据**，包含段落内容和语义关系。

**统计信息**（以 001_五帝本纪 为例）：
- 章节：001_五帝本纪
- 段落数：99
- 关系数：290
- 关系类型：8种

**数据结构**：

```json
{
  "chapter": "001_五帝本纪",
  "total_paragraphs": 99,
  "total_relations": 290,
  "relation_types": {
    "temporal": "时间顺序关系",
    "causal": "因果关系",
    "genealogy": "家族关系",
    "hierarchy": "层级关系",
    "parallel": "并列关系",
    "contrast": "对比关系",
    "meta": "元文本关系",
    "elaboration": "详细说明关系"
  },
  "paragraphs": [
    {
      "anchor": "1",
      "section": "黄帝世系",
      "subsection": "黄帝身世",
      "summary": "黄帝是少典之子，姓公孙，名轩辕",
      "full_text": "黄帝者，少典之子，姓公孙，名曰轩辕。",
      "char_count": 19
    }
  ],
  "relations": [
    {
      "source": "1",
      "target": "2",
      "type": "temporal",
      "subtype": "sequential",
      "description": "黄帝出生后的成长经历",
      "confidence": 0.9
    }
  ]
}
```

**字段说明**：

**paragraphs（段落）**：
- `anchor`: 段落编号（可以是整数或小数，如 1, 1.1, 1.2）
- `section`: 所属章节名称
- `subsection`: 所属小节名称（可选）
- `summary`: 段落内容摘要
- `full_text`: 段落完整文本
- `char_count`: 字符数统计

**relations（关系）**：
- `source`: 源段落编号
- `target`: 目标段落编号
- `type`: 关系类型（见下文）
- `subtype`: 关系子类型
- `description`: 关系描述
- `confidence`: 置信度（0-1）

### `data/paragraph_relations_001.json`

**基础版段落关系数据**，只包含结构化信息，不含完整文本。

适用于：
- 快速加载和分析
- 关系统计
- 结构可视化

## 关系类型体系

### 1. temporal（时间顺序关系）
- `sequential`: 顺序发生
- `concurrent`: 同时发生
- `before_after`: 先后关系

### 2. causal（因果关系）
- `cause_effect`: 直接因果
- `condition_result`: 条件结果
- `purpose_action`: 目的行动

### 3. genealogy（家族关系）
- `parent_child`: 父子关系
- `marriage`: 婚姻关系
- `sibling`: 兄弟姐妹关系
- `ancestry`: 祖先后代关系

### 4. hierarchy（层级关系）
- `ruler_subject`: 君臣关系
- `master_disciple`: 师徒关系
- `superior_subordinate`: 上下级关系

### 5. parallel（并列关系）
- `coordination`: 同级并列
- `enumeration`: 列举关系
- `comparison`: 比较关系

### 6. contrast（对比关系）
- `opposition`: 对立关系
- `difference`: 差异关系
- `conflict`: 冲突关系

### 7. meta（元文本关系）
- `citation`: 引用关系
- `commentary`: 评论关系
- `summary`: 总结关系

### 8. elaboration（详细说明关系）
- `detail`: 细节展开
- `example`: 举例说明
- `explanation`: 解释说明

## 数据生成脚本

### `scripts/extract_paragraph_structure.py`

**功能**：从标注文本中提取段落结构

**输入**：`chapter_md/*.tagged.md`（带语义标注的章节文件）

**输出**：`data/paragraph_relations_001.json`

**提取规则**：
- 匹配段落标记：`[编号] 段落内容`
- 支持多级编号：1, 1.1, 1.2, 1.2.1 等
- 提取章节和小节信息
- 识别列表项、对话、引文等特殊格式

**运行方法**：
```bash
python scripts/extract_paragraph_structure.py chapter_md/001_五帝本纪.tagged.md
```

### `scripts/analyze_paragraph_relations.py`

**功能**：分析段落间的语义关系

**输入**：`data/paragraph_relations_001.json`

**输出**：`data/paragraph_relations_001_enhanced.json`

**分析方法**：
- 基于段落摘要的语义分析
- 时间线索识别
- 因果关系推断
- 家族关系提取
- 层级关系识别

**运行方法**：
```bash
python scripts/analyze_paragraph_relations.py
```

### `scripts/render_structure_knowledge_graph.py`

**功能**：生成交互式知识图谱可视化

**输入**：
- `data/paragraph_relations_001_enhanced.json`（结构数据）
- `chapter_md/001_五帝本纪.tagged.md`（原文标注）

**输出**：`docs/special/structure.html`

**可视化特性**：
- vis.js 力导向图布局（Barnes-Hut 物理引擎）
- 节点大小根据段落长度动态调整（150-300px）
- 超大字体显示段落编号（48px）
- 边标签显示关系类型（20px）
- 11个圆形控制按钮：
  1. 播放/暂停自动播放
  2. 速度调节（0.2× ~ 5×）
  3. 缩放至适应
  4. 放大/缩小
  5. 切换物理引擎
  6. 重置视图
  7. 导出图片
  8. 前一段/后一段导航
- 阅读卡片功能：
  - 显示段落完整内容（带语义标注高亮）
  - 动态阅读时间（基于字数，300字/分钟）
  - 前后段落导航按钮
  - 进度指示器
  - 支持实体标注渲染：`〖@人名〗` `〖#地名〗` `〖!事件〗` 等
  - 支持动词标注渲染：`⟦◈动作⟧`

**运行方法**：
```bash
python scripts/render_structure_knowledge_graph.py
```

生成的 HTML 文件可以直接在浏览器中打开查看。

## 语义标注系统

段落文本使用以下标注格式：

### 实体标注
- `〖@人名〗` - 人物
- `〖#地名〗` 或 `〖=地点〗` - 地理位置
- `〖!事件〗` - 重要事件
- `〖?概念〗` - 抽象概念
- `〖&族群〗` - 族群/民族
- `〖+动植物〗` - 动植物
- `〖~国家〗` - 国家/政权
- `〖;官职〗` - 官职/职务
- `〖_抽象概念〗` - 抽象概念

### 动作标注
- `⟦动词⟧` - 基础动作
- `⟦◈动词⟧` - 核心动作
- `⟦◉动词⟧` - 重要动作
- `⟦◇动词⟧` - 次要动作

### 消歧标注
- `〖@显示名|规范名〗` - 当同一人物有多个名字时使用

**示例**：
```
〖@黄帝〗者，〖@少典〗之子，姓〖&公孙〗，名曰〖@轩辕|黄帝〗。
```

## 可视化效果

交互式知识图谱提供以下功能：

1. **全局视图**：显示所有段落及其关系
2. **自动播放**：按顺序逐段播放，带阅读卡片
3. **速度控制**：5档速度可选（0.2× 到 5×）
4. **导航功能**：点击节点或使用导航按钮浏览
5. **关系过滤**：点击边查看关系详情
6. **物理引擎**：可切换布局算法
7. **导出功能**：导出为PNG图片

## 数据更新流程

1. **提取段落结构**：
   ```bash
   python scripts/extract_paragraph_structure.py chapter_md/001_五帝本纪.tagged.md
   ```

2. **分析语义关系**：
   ```bash
   python scripts/analyze_paragraph_relations.py
   ```

3. **生成可视化**：
   ```bash
   python scripts/render_structure_knowledge_graph.py
   ```

4. **查看结果**：
   打开 `docs/special/structure.html` 在浏览器中查看

## 未来扩展方向

可以基于这套数据结构进行以下扩展：

1. **多章节对比**：比较不同章节的段落结构模式
2. **关系统计分析**：分析关系类型分布和密度
3. **段落聚类**：基于语义关系进行段落聚类
4. **时间线重建**：基于时间关系重建历史时间线
5. **人物关系网络**：提取人物关系子图
6. **文本生成**：基于结构生成章节摘要
7. **跨章节引用**：识别章节间的引用和互文关系
8. **自动关系发现**：使用AI模型自动识别更多关系类型

## 技术栈

- **数据格式**：JSON
- **可视化库**：vis.js (v9.1.2)
- **布局算法**：Barnes-Hut Physics Engine
- **前端技术**：HTML5 + CSS3 + JavaScript (ES6+)
- **后端脚本**：Python 3
- **文本处理**：正则表达式（用于解析和标注识别）

## 版本信息

- 初始版本：2026-03-24
- 当前数据版本：v1.0
- 章节覆盖：001_五帝本纪
- 最后更新：commit bbe1cf33

## 数据使用示例

### Python 读取段落关系数据

```python
import json

# 读取完整版数据
with open('kg/structure/data/paragraph_relations_001_enhanced.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"章节：{data['chapter']}")
print(f"段落数：{data['total_paragraphs']}")
print(f"关系数：{data['total_relations']}")

# 遍历所有段落
for para in data['paragraphs']:
    print(f"[{para['anchor']}] {para['summary']}")

# 查找特定段落的所有关系
def find_relations(anchor):
    relations = []
    for rel in data['relations']:
        if rel['source'] == anchor or rel['target'] == anchor:
            relations.append(rel)
    return relations

# 示例：查找段落 "1" 的所有关系
relations = find_relations("1")
for rel in relations:
    print(f"{rel['source']} --[{rel['type']}]--> {rel['target']}: {rel['description']}")
```

### JavaScript 在网页中使用

```javascript
// 使用 fetch API 加载数据
fetch('kg/structure/data/paragraph_relations_001_enhanced.json')
  .then(response => response.json())
  .then(data => {
    console.log(`加载了 ${data.total_paragraphs} 个段落`);
    console.log(`包含 ${data.total_relations} 个关系`);
    
    // 构建节点和边的数据结构（用于 vis.js）
    const nodes = data.paragraphs.map(p => ({
      id: p.anchor,
      label: p.anchor,
      title: p.summary
    }));
    
    const edges = data.relations.map(r => ({
      from: r.source,
      to: r.target,
      label: r.type,
      title: r.description
    }));
    
    // 使用 vis.js 渲染图谱
    // ...
  });
```

## 相关文档

- 项目主文档：[README.md](../../README.md)
- 标注规范：[CLAUDE.md](../../CLAUDE.md)
- 章节结构说明：[kg/structure/README.md](README.md)
- 实体标注系统：[doc/entities/](../../doc/entities/)
- 可视化示例：[docs/special/structure.html](../../docs/special/structure.html)

## 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: https://github.com/baojie/shiji-kb/issues
- 项目维护者：baojie
