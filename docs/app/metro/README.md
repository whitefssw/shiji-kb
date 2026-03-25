# 史记地铁图

《史记》130篇历史事件的交互式时间线可视化，采用地铁线路图的设计风格。

## 在线访问

- 🌐 GitHub Pages: https://baojie.github.io/shiji-kb/app/metro/
- 📖 项目主页: https://github.com/baojie/shiji-kb

## 功能特性

- **130条线路**：对应《史记》130篇（本纪、世家、列传等）
- **3197个站点**：历史事件节点
- **时间轴对齐**：公元前2700年至公元220年
- **换乘站**：标识跨章节的关联事件
- **交互功能**：
  - 平移、缩放查看
  - 搜索事件、人物、地点
  - 点击事件查看详情
  - 筛选显示特定线路

## 本地运行

```bash
# 启动本地服务器
./start.sh

# 或指定端口
./start.sh 8080

# 然后访问
open http://localhost:8080
```

## 技术栈

- 纯JavaScript（无框架依赖）
- SVG 绘图
- 响应式设计
- 4MB JSON数据

## 数据来源

所有历史事件和时间线数据来自《史记》原文，经过结构化提取和时间推理。

详见：[shiji-kb 项目](https://github.com/baojie/shiji-kb)

---

Generated: $(date +"%Y-%m-%d %H:%M:%S")
