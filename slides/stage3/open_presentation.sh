#!/bin/bash

# Stage 3 学术展示快速启动脚本

echo "=================================="
echo "  Stage 3 学术展示启动"
echo "=================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HTML_FILE="$SCRIPT_DIR/stage3_academic_presentation.html"

# 检查文件是否存在
if [ ! -f "$HTML_FILE" ]; then
    echo "❌ 错误: 找不到 HTML 文件"
    echo "   路径: $HTML_FILE"
    exit 1
fi

# 检查图片文件夹
if [ ! -d "$SCRIPT_DIR/images" ]; then
    echo "⚠️  警告: images 文件夹不存在"
    echo "   正在生成图表..."
    cd "$SCRIPT_DIR/../.."
    python3 scripts/visualization/generate_stage3_slides_charts.py
    if [ $? -ne 0 ]; then
        echo "❌ 图表生成失败"
        exit 1
    fi
fi

echo "✅ 文件检查完成"
echo ""
echo "选择打开方式："
echo "  1) 直接在浏览器打开"
echo "  2) 启动本地服务器 (推荐，更稳定)"
echo ""
read -p "请选择 (1 或 2): " choice

case $choice in
    1)
        echo ""
        echo "🚀 正在打开浏览器..."
        open "$HTML_FILE"
        echo "✅ 已在默认浏览器中打开"
        ;;
    2)
        echo ""
        echo "🚀 启动本地服务器..."
        echo "   地址: http://localhost:8000/stage3_academic_presentation.html"
        echo ""
        echo "📝 使用说明:"
        echo "   - 按 Ctrl+C 停止服务器"
        echo "   - 浏览器会自动打开"
        echo ""
        
        # 启动服务器
        cd "$SCRIPT_DIR"
        
        # 尝试打开浏览器
        sleep 2 && open "http://localhost:8000/stage3_academic_presentation.html" &
        
        # 启动 Python HTTP 服务器
        python3 -m http.server 8000
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac






