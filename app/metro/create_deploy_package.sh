#!/bin/bash

# 史记地铁图 - 创建GitHub Pages/Netlify部署包

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
METRO_DIR="$SCRIPT_DIR"

echo "📦 创建部署包 - 史记地铁图"
echo "================================"

# 创建临时部署目录
DEPLOY_DIR="/tmp/shiji-metro-deploy"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/data

# 复制所有文件
echo "📋 复制文件..."
cp "$METRO_DIR/index.html" $DEPLOY_DIR/
cp "$METRO_DIR/metro.css" $DEPLOY_DIR/
cp "$METRO_DIR/metro.js" $DEPLOY_DIR/
cp "$METRO_DIR/data/metro_map_data.json" $DEPLOY_DIR/data/

# 如果有README，也复制
if [ -f "$METRO_DIR/README.md" ]; then
  cp "$METRO_DIR/README.md" $DEPLOY_DIR/
fi

# 创建netlify配置
echo "⚙️  创建配置文件..."
cat > $DEPLOY_DIR/netlify.toml << 'EOF'
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "no-referrer-when-downgrade"

[[headers]]
  for = "/*.json"
  [headers.values]
    Content-Type = "application/json; charset=utf-8"
    Cache-Control = "public, max-age=3600"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
EOF

# 创建GitHub Pages的 _config.yml (如果需要)
cat > $DEPLOY_DIR/_config.yml << 'EOF'
# Jekyll configuration for GitHub Pages
include: ["data"]
EOF

# 创建.nojekyll文件（GitHub Pages优化）
touch $DEPLOY_DIR/.nojekyll

# 显示文件大小统计
echo ""
echo "📊 文件大小统计："
echo "   HTML:  $(du -h $DEPLOY_DIR/index.html | cut -f1)"
echo "   CSS:   $(du -h $DEPLOY_DIR/metro.css | cut -f1)"
echo "   JS:    $(du -h $DEPLOY_DIR/metro.js | cut -f1)"
echo "   Data:  $(du -h $DEPLOY_DIR/data/metro_map_data.json | cut -f1)"
echo "   总计:  $(du -sh $DEPLOY_DIR | cut -f1)"

# 创建压缩包
echo ""
echo "🗜️  创建压缩包..."
cd $DEPLOY_DIR
zip -r shiji-metro.zip * .nojekyll
mv shiji-metro.zip "$METRO_DIR/"

echo ""
echo "✅ 部署包创建完成！"
echo ""
echo "📦 文件位置："
echo "   压缩包: $METRO_DIR/shiji-metro.zip"
echo "   目录:   $DEPLOY_DIR"
echo ""
echo "🚀 部署方式："
echo ""
echo "【方式1: Netlify Drop】"
echo "1. 访问 https://app.netlify.com/drop"
echo "2. 拖拽 shiji-metro.zip 或整个文件夹 $DEPLOY_DIR"
echo "3. 等待部署完成"
echo ""
echo "【方式2: GitHub Pages】"
echo "1. 将 $DEPLOY_DIR 内容推送到 gh-pages 分支"
echo "2. 在仓库设置中启用 GitHub Pages"
echo "3. 访问 https://baojie.github.io/shiji-kb/metro/"
echo ""
echo "【方式3: 复制到 docs 目录】"
echo "运行以下命令复制到项目的 docs/app/metro："
echo "   bash $METRO_DIR/deploy_to_docs.sh"
echo ""
