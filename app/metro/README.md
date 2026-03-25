# 史记地铁图

《史记》130篇历史事件的交互式时间线可视化，采用地铁线路图的设计风格。

## 功能特性

- **130条线路**：对应《史记》130篇（本纪、世家、列传等）
- **3197个站点**：历史事件节点
- **时间轴对齐**：公元前2700年至公元220年，每50年一个刻度
- **换乘站**：标识跨章节的关联事件（cross_ref）
- **交互功能**：
  - 平移、缩放查看（鼠标拖拽、滚轮缩放）
  - 搜索事件、人物、地点
  - 点击事件查看详情（原文引用、段落链接）
  - 筛选显示特定线路（侧边栏勾选）
  - 固定时间刻度（顶部和底部）

## 在线访问

- 🌐 GitHub Pages: https://baojie.github.io/shiji-kb/app/metro/
- 📖 项目主页: https://github.com/baojie/shiji-kb

## 本地运行

### 快速启动

```bash
# 启动本地服务器（默认端口1046）
./start.sh

# 或指定端口
./start.sh 8080

# 然后访问
open http://localhost:8080
```

### 系统要求

- Python 3 / Python 2 / Node.js (npx) 任一即可
- 现代浏览器（Chrome 90+, Firefox 88+, Safari 14+）

## 部署

### 方式1: Netlify Drop（最简单）

```bash
# 创建部署包
./create_deploy_package.sh

# 访问 https://app.netlify.com/drop
# 拖拽 shiji-metro.zip 文件
```

### 方式2: GitHub Pages

```bash
# 部署到 docs/app/metro
./deploy_to_docs.sh

# 提交到仓库
git add docs/app/metro
git commit -m "部署史记地铁图"
git push
```

### 方式3: 手动部署

需要部署的文件：
- `index.html`
- `metro.css`
- `metro.js`
- `data/metro_map_data.json` (4MB)

## 技术栈

- **前端**：纯JavaScript（无框架依赖）
- **绘图**：SVG + Canvas
- **数据**：JSON (4.2MB)
- **设计**：参考上海地铁图

### 技术亮点

1. **固定时间刻度**：HTML覆盖层 + CSS `position: fixed`
2. **地铁风格曲线**：SVG 贝塞尔曲线（S曲线过渡）
3. **换乘站光晕**：动态半径限制（最大9px）
4. **性能优化**：
   - 虚拟滚动（仅渲染可见区域的年份标签）
   - viewBox 动态更新
   - 标签聚类显示

## 数据结构

### 线路 (lines)

```json
{
  "id": "005",
  "name": "秦本纪",
  "label": "秦",
  "color": "#f39c12",
  "group": "本纪",
  "stations": [...]
}
```

### 站点 (stations)

```json
{
  "id": "005-007",
  "name": "秦仲伐戎战死",
  "type": "战争",
  "year": -822,
  "x_pos": -822,
  "people": ["秦仲"],
  "locations": ["西戎"],
  "dynasties": ["周", "秦"],
  "description": "...",
  "quote": "...",
  "para_pos": "[7]",
  "chapter": "005",
  "chapter_name": "秦本纪"
}
```

### 换乘 (transfers)

```json
{
  "type": "cross_ref",
  "events": ["005-007", "043-012"],
  "shared_people": ["秦仲"]
}
```

## 数据来源

所有历史事件和时间线数据来自《史记》原文，经过：
1. 结构化提取（段落 → 事件）
2. 时间推理（基于干支、帝号、谥号等）
3. 实体链接（人物、地点、朝代）
4. 关系挖掘（跨章节引用）

详见：[shiji-kb 项目](https://github.com/baojie/shiji-kb)

## 开发

### 文件结构

```
app/metro/
├── index.html              # 主页面
├── metro.css              # 样式
├── metro.js               # 主逻辑
├── data/
│   └── metro_map_data.json  # 数据文件 (4.2MB)
├── start.sh               # 启动脚本
├── create_deploy_package.sh  # 创建部署包
├── deploy_to_docs.sh      # 部署到docs目录
└── README.md              # 本文件
```

### 主要函数

- `render()`: 渲染整个地铁图
- `renderOneLine()`: 渲染单条线路（带曲线）
- `renderTransfers()`: 渲染换乘连接线
- `updateTimelineRulers()`: 更新固定时间刻度
- `updateLabelVisibility()`: 动态显示/隐藏标签
- `applyViewBox()`: 应用视图变换

## 更新日志

### 2026-03-25
- ✨ 新增固定时间刻度（顶部和底部）
- ✨ 换乘站线路弯曲（地铁风格S曲线）
- ✨ 换乘线改为实线（联络线风格）
- ✨ 换乘站光晕大小限制（最大9px）
- 📝 新增部署脚本（Netlify + GitHub Pages）

### 2026-03-19
- 🎉 初始版本发布
- ✨ 130线路 + 3197站点
- ✨ 时间轴对齐（公元前2700 - 公元220）
- ✨ 换乘站标识

## License

MIT

---

**史记知识库项目** | [GitHub](https://github.com/baojie/shiji-kb) | [在线演示](https://baojie.github.io/shiji-kb/app/metro/)
