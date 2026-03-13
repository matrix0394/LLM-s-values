#!/bin/bash
# 一键上传到GitHub脚本
# 已经过预检查，所有文件都安全 ✅

set -e  # 遇到错误时停止

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  GitHub项目一键更新脚本"
echo "  已允许上传data和results中的带时间戳文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 进入项目目录
cd "/Users/yxy/code/LLM's values"

# 生成分支名称
BRANCH_NAME="update-$(date +%Y%m%d-%H%M)"
echo "📌 分支名称: $BRANCH_NAME"
echo ""

# 创建新分支
echo "🔄 步骤1/5: 创建新分支..."
if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo "   分支已存在，切换到该分支"
    git checkout $BRANCH_NAME
else
    echo "   创建新分支 $BRANCH_NAME"
    git checkout -b $BRANCH_NAME
fi
echo "   ✅ 完成"
echo ""

# 清理Git缓存
echo "🧹 步骤2/5: 清理Git缓存（移除之前跟踪的大文件）..."
git rm -r --cached . > /dev/null 2>&1 || true
echo "   ✅ 完成"
echo ""

# 添加文件
echo "➕ 步骤3/5: 添加文件（自动应用.gitignore规则）..."
git add .
echo "   ✅ 完成"
echo ""

# 显示状态
echo "📊 步骤4/5: 检查将要提交的文件..."
echo ""
echo "将要提交的文件数量:"
TOTAL_FILES=$(git status --short | wc -l | xargs)
echo "   总计: $TOTAL_FILES 个文件"
echo ""

echo "主要更改："
git status --short | head -30
echo ""
if [ "$TOTAL_FILES" -gt 30 ]; then
    echo "   ... 还有 $((TOTAL_FILES - 30)) 个文件（未全部显示）"
    echo ""
fi

# 检查大文件
echo "🔍 检查大文件（>10MB）..."
HAS_LARGE=0
git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(du -m "$file" 2>/dev/null | cut -f1)
        if [ "$size" -gt 10 ]; then
            echo "   ⚠️  $file - ${size}MB"
            HAS_LARGE=1
        fi
    fi
done

if [ $HAS_LARGE -eq 0 ]; then
    echo "   ✅ 没有发现超大文件"
fi
echo ""

# 提交
echo "💾 步骤5/5: 提交更改..."
COMMIT_MSG="更新：添加多语言角色扮演分析结果

- 添加最新的多语言分析数据和可视化结果
- 包含roleplay_multilingual的完整分析
- 更新项目文档和配置
- 优化.gitignore规则，排除超大文件

生成时间: $(date '+%Y-%m-%d %H:%M:%S')"

git commit -m "$COMMIT_MSG"
echo "   ✅ 提交完成"
echo ""

# 推送
echo "🚀 推送到GitHub..."
echo "   执行: git push -u origin $BRANCH_NAME"
echo ""

if git push -u origin $BRANCH_NAME; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ 成功推送到GitHub！"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "下一步："
    echo "1. 访问你的GitHub仓库网页"
    echo "2. 你会看到一个创建Pull Request的提示"
    echo "3. 点击 'Compare & pull request' 按钮"
    echo "4. 填写PR描述并提交"
    echo "5. 合并到main分支"
    echo ""
    echo "或者，如果你想直接合并到本地main："
    echo "   git checkout main"
    echo "   git merge $BRANCH_NAME"
    echo "   git push origin main"
    echo ""
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ⚠️  推送失败"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "可能的原因："
    echo "1. 需要先拉取远程更改"
    echo "   解决: git pull origin main --rebase"
    echo ""
    echo "2. 认证问题"
    echo "   解决: 检查GitHub登录状态"
    echo ""
    echo "3. 仍有大文件"
    echo "   解决: 检查上面的大文件列表，更新.gitignore"
    echo ""
    exit 1
fi

