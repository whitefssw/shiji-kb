#!/bin/bash

# 史记地铁图 - 部署到 docs/app/metro (用于GitHub Pages)

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCS_TARGET="$PROJECT_ROOT/docs/app/metro"

echo "🚀 部署史记地铁图到 docs 目录"
echo "================================"

# 创建目标目录
mkdir -p "$DOCS_TARGET/data"

# 复制文件
echo "📋 复制文件..."
cp "$SCRIPT_DIR/index.html" "$DOCS_TARGET/"
cp "$SCRIPT_DIR/metro.css" "$DOCS_TARGET/"
cp "$SCRIPT_DIR/metro.js" "$DOCS_TARGET/"
cp "$SCRIPT_DIR/data/metro_map_data.json" "$DOCS_TARGET/data/"

# 复制启动脚本（可选，本地测试用）
if [ -f "$SCRIPT_DIR/start.sh" ]; then
  cp "$SCRIPT_DIR/start.sh" "$DOCS_TARGET/"
fi

# 创建README
cat > "$DOCS_TARGET/README.md" << 'EOF'
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
EOF

# 显示文件列表
echo ""
echo "📊 已部署文件："
ls -lh "$DOCS_TARGET" | grep -v "^d"
echo ""
echo "Data:"
ls -lh "$DOCS_TARGET/data/"

echo ""
echo "✅ 部署完成！"
echo ""
echo "📁 目标目录："
echo "   $DOCS_TARGET"
echo ""
echo "🌐 GitHub Pages URL (推送后可访问)："
echo "   https://baojie.github.io/shiji-kb/app/metro/"
echo ""
echo "💡 下一步："
echo "   1. git add docs/app/metro"
echo "   2. git commit -m '部署史记地铁图到GitHub Pages'"
echo "   3. git push"
echo ""
