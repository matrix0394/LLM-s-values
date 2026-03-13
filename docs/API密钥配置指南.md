# API密钥配置指南

## 📅 更新时间
2024年12月6日

---

## 🎯 问题说明

运行程序时出现以下错误：
```
警告: 模型 gpt-4o 的API密钥 OPENKEY_API_KEY 未设置
❌ 没有可用的模型，请检查API密钥配置
```

**原因**: 程序需要API密钥才能调用LLM模型

---

## 🔑 需要配置的API密钥

根据 `config/llm_models.json`，当前需要：

### OpenKey平台 (8个模型)
```
环境变量名: OPENKEY_API_KEY
用途: GPT-4o, GPT-4o-mini, Claude, Gemini, DeepSeek, Kimi, Qwen
```

### OpenRouter平台 (14个模型，可选)
```
环境变量名: OPENROUTER_API_KEY
用途: GPT-5.1, Claude 4.5, Gemini 3, LLaMA, Grok, Mistral, Phi等
```

---

## 📋 配置方法

### 方法1: .env 文件配置（推荐✅）

#### 步骤1: 安装 python-dotenv

```powershell
pip install python-dotenv
```

#### 步骤2: 创建 .env 文件

在项目根目录创建 `.env` 文件：

```powershell
# 进入项目根目录
cd "E:\Code\value of LLM\LLM's values"

# 创建.env文件
New-Item -Path .env -ItemType File -Force

# 或者直接用记事本创建
notepad .env
```

#### 步骤3: 编辑 .env 文件

在 `.env` 文件中添加：

```env
# OpenKey API密钥（必需）
OPENKEY_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenRouter API密钥（可选，如果要使用OpenRouter的14个模型）
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**注意**:
- ⚠️ 将 `sk-xxx...` 替换为你的实际API密钥
- ⚠️ 不要在密钥前后加引号
- ⚠️ 不要提交 `.env` 文件到Git（已在 `.gitignore` 中）

#### 步骤4: 验证配置

```powershell
# 重新运行程序
python .\src\run\run_llm_values_analysis.py

# 应该看到：
# ✅ 已加载环境变量: E:\Code\value of LLM\LLM's values\.env
# 🔍 发现可用模型: 8个
```

---

### 方法2: Windows 系统环境变量

#### 临时设置（当前PowerShell会话有效）

```powershell
# 设置OpenKey API密钥
$env:OPENKEY_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 设置OpenRouter API密钥（可选）
$env:OPENROUTER_API_KEY = "sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 验证设置
echo $env:OPENKEY_API_KEY

# 运行程序
python .\src\run\run_llm_values_analysis.py
```

**缺点**: 关闭PowerShell后失效

---

#### 永久设置（推荐）

**方法A: 图形界面设置**

1. 按 `Win + R`，输入 `sysdm.cpl`，回车
2. 点击"高级"标签
3. 点击"环境变量"按钮
4. 在"用户变量"区域，点击"新建"
5. 变量名: `OPENKEY_API_KEY`
6. 变量值: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
7. 点击"确定"保存
8. **重启PowerShell**使其生效

**方法B: PowerShell命令设置**

```powershell
# 设置用户级环境变量（永久）
[System.Environment]::SetEnvironmentVariable('OPENKEY_API_KEY', 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'User')

# 设置OpenRouter（可选）
[System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', 'sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'User')

# 重启PowerShell使其生效
```

**方法C: PowerShell配置文件**

```powershell
# 编辑PowerShell配置文件
notepad $PROFILE

# 如果文件不存在，先创建
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}

# 在配置文件中添加：
$env:OPENKEY_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:OPENROUTER_API_KEY = "sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 保存后重新加载
. $PROFILE
```

---

### 方法3: Linux/Mac 配置

#### 临时设置

```bash
export OPENKEY_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export OPENROUTER_API_KEY="sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### 永久设置

```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
nano ~/.bashrc

# 添加以下行
export OPENKEY_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export OPENROUTER_API_KEY="sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 保存后重新加载
source ~/.bashrc
```

---

## 🔍 验证配置

### 检查环境变量是否设置成功

**PowerShell**:
```powershell
# 检查OPENKEY_API_KEY
echo $env:OPENKEY_API_KEY

# 检查OPENROUTER_API_KEY
echo $env:OPENROUTER_API_KEY

# 应该显示你的API密钥（如果设置成功）
```

**Python**:
```python
import os
print("OPENKEY_API_KEY:", os.getenv('OPENKEY_API_KEY'))
print("OPENROUTER_API_KEY:", os.getenv('OPENROUTER_API_KEY'))
```

---

## 📁 .env 文件示例

创建 `E:\Code\value of LLM\LLM's values\.env` 文件：

```env
# ============================================
# API密钥配置
# ============================================

# OpenKey平台 API密钥（必需）
# 用于: GPT-4o, GPT-4o-mini, Claude 3.7, Gemini 2.5, DeepSeek, Kimi, Qwen
OPENKEY_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenRouter平台 API密钥（可选）
# 用于: GPT-5.1, Claude 4.5, Gemini 3, LLaMA, Grok, Mistral, Phi等
# OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# 注意事项
# ============================================
# 1. 不要在密钥前后加引号
# 2. 不要提交此文件到Git（已在.gitignore中）
# 3. 如果不使用OpenRouter，可以注释掉OPENROUTER_API_KEY
# 4. 修改后需要重启程序才能生效
```

---

## 🔒 安全提示

### .gitignore 配置

确保 `.env` 文件不会被提交到Git：

```gitignore
# 在 .gitignore 中添加
.env
*.env
.env.*
```

### 检查是否已添加

```powershell
# 检查.gitignore
cat .gitignore | Select-String ".env"

# 应该看到：
# .env
```

---

## 🚀 完整配置流程（推荐）

### 1. 安装依赖

```powershell
pip install python-dotenv
```

### 2. 创建 .env 文件

```powershell
cd "E:\Code\value of LLM\LLM's values"
notepad .env
```

### 3. 添加API密钥

```env
OPENKEY_API_KEY=sk-你的实际密钥
```

### 4. 保存并验证

```powershell
# 运行程序
python .\src\run\run_llm_values_analysis.py

# 应该看到：
# ✅ 已加载环境变量: E:\Code\value of LLM\LLM's values\.env
# 🔍 发现可用模型: 8个
```

---

## ❓ 常见问题

### Q1: 为什么设置了环境变量还是提示未设置？

**A**: 可能的原因：
1. PowerShell没有重启（系统环境变量需要重启）
2. 环境变量名拼写错误（必须是 `OPENKEY_API_KEY`）
3. .env文件路径不对（必须在项目根目录）
4. python-dotenv未安装

**解决方法**:
```powershell
# 1. 检查环境变量
echo $env:OPENKEY_API_KEY

# 2. 检查.env文件
cat .env

# 3. 检查python-dotenv
pip show python-dotenv

# 4. 重启PowerShell
```

---

### Q2: 我只想使用部分模型，需要配置所有API密钥吗？

**A**: 不需要。只配置你要使用的平台的API密钥即可。

- 只用OpenKey的8个模型 → 只配置 `OPENKEY_API_KEY`
- 只用OpenRouter的14个模型 → 只配置 `OPENROUTER_API_KEY`
- 两个平台都用 → 两个都配置

---

### Q3: .env 文件和系统环境变量哪个优先级高？

**A**: .env 文件优先级更高（会覆盖系统环境变量）

**优先级顺序**:
1. .env 文件中的配置（最高）
2. 系统环境变量
3. PowerShell临时设置（最低）

---

### Q4: 如何获取API密钥？

**A**: 

**OpenKey平台**:
1. 访问 OpenKey 官网
2. 注册/登录账号
3. 进入API密钥管理页面
4. 创建新的API密钥
5. 复制密钥（格式: `sk-xxx...`）

**OpenRouter平台**:
1. 访问 OpenRouter 官网
2. 注册/登录账号
3. 进入API密钥管理页面
4. 创建新的API密钥
5. 复制密钥（格式: `sk-or-xxx...`）

---

## ✅ 配置完成检查清单

- [ ] 安装了 `python-dotenv`
- [ ] 创建了 `.env` 文件在项目根目录
- [ ] 添加了 `OPENKEY_API_KEY`（如果使用OpenKey）
- [ ] 添加了 `OPENROUTER_API_KEY`（如果使用OpenRouter）
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 运行程序能看到"✅ 已加载环境变量"
- [ ] 运行程序能看到"🔍 发现可用模型: X个"

---

## 🎉 配置成功示例

```powershell
PS E:\Code\value of LLM\LLM's values> python .\src\run\run_llm_values_analysis.py

✅ 已加载环境变量: E:\Code\value of LLM\LLM's values\.env
🏠 项目根目录: E:\Code\value of LLM\LLM's values
📁 数据目录: E:\Code\value of LLM\LLM's values\data
📁 结果目录: E:\Code\value of LLM\LLM's values\results

======================================================================
🎯 Stage1: LLM Values 分析系统
======================================================================

🤖 初始化LLM访谈器（consensus_count=5）...

🔍 发现可用模型: 8个
   1. gpt-4o (US)
   2. gpt-4o-mini (US)
   3. claude-3-7-sonnet (US)
   4. gemini-2.5-flash (US)
   5. gemini-2.5-pro (US)
   6. deepseek-chat (CN)
   7. kimi-k2 (CN)
   8. qwen3-1.7b (CN)
```

---

## 📞 需要帮助？

如果配置后仍有问题，请检查：
1. API密钥是否正确（复制时是否完整）
2. 环境变量名是否正确（区分大小写）
3. .env文件是否在正确的位置
4. python-dotenv是否正确安装

**调试命令**:
```powershell
# 检查环境变量
python -c "import os; print('OPENKEY_API_KEY:', os.getenv('OPENKEY_API_KEY'))"

# 检查.env文件
cat .env

# 检查python-dotenv
pip show python-dotenv
```
