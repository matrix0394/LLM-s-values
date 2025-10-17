#!/bin/bash
# 清理Git历史中的大文件

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  清理Git历史中的大文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  警告：此操作会重写Git历史！"
echo ""

cd "/Users/yxy/code/LLM's values"

# 备份当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "📌 当前分支: $CURRENT_BRANCH"
echo ""

echo "🗑️  将要从Git历史中删除的文件："
echo "   1. data/valid_data.json (109.68 MB)"
echo "   2. data/Integrated_values_surveys_1981-2022.sav (818.89 MB)"
echo "   3. data/backup_numpy_problem_files/ivs_df.pkl (4289.07 MB)"
echo "   4. data/ivs_df.pkl (如果存在)"
echo ""

# 使用git filter-branch删除大文件
echo "🔧 开始清理Git历史..."
echo ""

# 删除文件的列表
FILES_TO_REMOVE=(
    "data/valid_data.json"
    "data/Integrated_values_surveys_1981-2022.sav"
    "data/backup_numpy_problem_files/ivs_df.pkl"
    "data/ivs_df.pkl"
)

for file in "${FILES_TO_REMOVE[@]}"; do
    echo "   移除: $file"
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch '$file'" \
        --prune-empty --tag-name-filter cat -- --all 2>/dev/null || true
done

echo ""
echo "✅ Git历史清理完成"
echo ""

# 清理refs
echo "🧹 清理引用和垃圾回收..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive
echo "   ✅ 完成"
echo ""

# 显示仓库大小
echo "📊 仓库大小:"
du -sh .git/
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ 清理完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "下一步："
echo "1. 强制推送到远程分支："
echo "   git push -f origin $CURRENT_BRANCH"
echo ""
echo "2. 或者删除远程分支重新推送："
echo "   git push origin --delete $CURRENT_BRANCH"
echo "   git push -u origin $CURRENT_BRANCH"
echo ""



