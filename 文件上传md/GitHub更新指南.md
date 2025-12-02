# GitHub更新指南

## 更新步骤

### 1. 检查当前状态

首先检查你的Git状态和当前分支：

```bash
cd "/Users/yxy/code/LLM's values"
git status
git branch
```

### 2. 创建新分支

创建并切换到一个新的分支（推荐命名方式）：

```bash
# 方式1: 创建并切换到新分支
git checkout -b update-2024-10

# 或者方式2: 基于当前main/master创建
git checkout -b feature/data-analysis-update
```

### 3. 添加.gitignore（如果还没有）

`.gitignore`文件已经创建，它会自动排除大文件。验证一下：

```bash
git status
```

你应该看到被忽略的文件不会出现在"未跟踪文件"列表中。

### 4. 添加和提交更改

```bash
# 添加所有符合规则的文件
git add .

# 查看将要提交的文件（确认没有大文件）
git status

# 如果看到意外的大文件，使用以下命令移除：
# git reset HEAD <文件名>

# 提交更改
git commit -m "更新：添加多语言分析功能和优化数据处理"
```

### 5. 推送到GitHub

```bash
# 推送新分支到远程仓库
git push -u origin update-2024-10

# 如果遇到错误，可能需要先拉取远程更改
git pull origin main --rebase
git push -u origin update-2024-10
```

### 6. 在GitHub上创建Pull Request

1. 访问你的GitHub仓库页面
2. 你会看到一个黄色提示框，显示你刚推送的分支
3. 点击 "Compare & pull request" 按钮
4. 填写PR描述，说明你的更新内容
5. 提交Pull Request

### 7. 合并分支（可选）

如果你确认分支没问题，可以：
- 在GitHub上直接合并PR
- 或者在本地合并：

```bash
git checkout main
git merge update-2024-10
git push origin main
```

## 常见问题处理

### 问题1: 推送时提示文件太大

如果仍然有大文件被推送，可以：

```bash
# 查看哪些文件太大
git ls-files -s | awk '$4 > 100000000 {print $4, $5}'

# 从暂存区移除大文件
git rm --cached <大文件路径>

# 更新.gitignore
# （已经创建，可以手动调整）

# 重新提交
git commit --amend
git push -f origin update-2024-10
```

### 问题2: 历史提交中包含大文件

如果之前已经提交过大文件，需要清理历史：

```bash
# 使用git filter-branch（谨慎操作！）
git filter-branch --tree-filter 'rm -f data/country_values/ivs_df.pkl' HEAD

# 或者使用BFG Repo-Cleaner（推荐，更快）
# 下载BFG: https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files ivs_df.pkl
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

### 问题3: 需要保留某些大文件

考虑使用Git LFS：

```bash
# 安装Git LFS
git lfs install

# 跟踪特定类型的大文件
git lfs track "*.pkl"
git lfs track "data/important_large_file.json"

# 添加.gitattributes
git add .gitattributes
git commit -m "添加Git LFS支持"
```

## 清理建议

### 删除不需要的备份文件

```bash
# 删除备份目录（这些文件已在.gitignore中）
rm -rf "data/backup/"

# 删除带时间戳的旧文件，只保留最新的
# （需要手动检查每个目录）
```

### 检查将要上传的文件大小

```bash
# 查看当前跟踪的文件总大小
git ls-files | xargs du -h | sort -h | tail -20

# 查看仓库大小
du -sh .git/
```

## 最佳实践

1. **定期提交**: 不要积累太多更改
2. **清晰的提交信息**: 描述每次提交做了什么
3. **分支管理**: 
   - `main`: 稳定版本
   - `dev`: 开发版本
   - `feature/*`: 新功能分支
   - `fix/*`: 修复分支
4. **代码审查**: 重要更改通过PR进行审查
5. **文档更新**: 更新代码的同时更新README

## 数据管理策略

由于项目包含大量数据文件，建议：

1. **在README中添加数据说明**:
   - 数据来源（IVS官方网站链接）
   - 数据获取方式
   - 数据预处理步骤

2. **提供数据生成脚本**:
   - 确保其他人可以重现你的数据处理流程
   - 已有的脚本在`scripts/`目录中

3. **外部数据存储（可选）**:
   - 对于必须分享的大文件，考虑使用：
     - Google Drive
     - Zenodo (学术数据，获得DOI)
     - OSF (Open Science Framework)
     - Hugging Face Datasets

4. **版本说明**:
   - 在`CHANGELOG.md`中记录每次更新的内容
   - 标注数据版本和代码版本

