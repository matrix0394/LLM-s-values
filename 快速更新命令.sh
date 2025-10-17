#!/bin/bash
# GitHub快速更新脚本
# 使用方法: bash 快速更新命令.sh

set -e  # 遇到错误时停止

echo "=== GitHub项目更新脚本 ==="
echo ""

# 进入项目目录
cd "/Users/yxy/code/LLM's values"

echo "步骤1: 检查当前状态..."
git status | head -20

echo ""
echo "步骤2: 创建新分支..."
BRANCH_NAME="update-$(date +%Y%m%d)"
echo "分支名称: $BRANCH_NAME"

# 检查分支是否已存在
if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo "分支 $BRANCH_NAME 已存在，切换到该分支"
    git checkout $BRANCH_NAME
else
    echo "创建新分支 $BRANCH_NAME"
    git checkout -b $BRANCH_NAME
fi

echo ""
echo "步骤3: 清理Git缓存（移除之前跟踪的大文件）..."
# 这会从索引中移除所有文件，然后根据.gitignore重新添加
git rm -r --cached . > /dev/null 2>&1 || true

echo ""
echo "步骤4: 添加文件..."
git add .

echo ""
echo "步骤5: 查看将要提交的文件状态..."
echo "以下是将要提交的文件（前50个）："
git status --short | head -50

echo ""
echo "即将提交的文件总数:"
git status --short | wc -l

echo ""
echo "检查是否有大文件（>10MB）被添加..."
git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(du -m "$file" | cut -f1)
        if [ "$size" -gt 10 ]; then
            echo "警告: $file 大小为 ${size}MB"
        fi
    fi
done

echo ""
echo "=== 准备工作完成 ==="
echo ""
echo "接下来你需要："
echo "1. 检查上面列出的文件是否正确"
echo "2. 如果确认无误，运行以下命令提交和推送："
echo ""
echo "   git commit -m '更新项目：添加多语言分析和数据处理优化'"
echo "   git push -u origin $BRANCH_NAME"
echo ""
echo "3. 然后访问GitHub网页创建Pull Request"
echo ""
echo "如果发现大文件被意外添加，请运行:"
echo "   git reset HEAD <文件名>"
echo "   然后更新.gitignore文件"

