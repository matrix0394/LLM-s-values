# 日语和韩语访谈测试指南

## 📋 配置检查结果

### ✅ 配置完整性验证

1. **日语 (ja) 配置**
   - 国家: `Japan`
   - 题目数: 10题
   - 所有题目的 `question` 和 `scale` 字段已更新为日文

2. **韩语 (ko) 配置**
   - 国家: `Korea (the Republic of)`
   - 题目数: 10题
   - 所有题目的 `question` 和 `scale` 字段已更新为韩文

3. **语言-国家映射**
   - `Japan` → `ja`
   - `Korea (the Republic of)` → `ko`

## 🧪 测试方法

### 方法1: 使用测试脚本（推荐）

```bash
# 测试单个模型（默认使用 gpt-4o-mini）
python scripts/test_ja_ko_languages.py

# 测试指定模型
python scripts/test_ja_ko_languages.py --model openai/gpt-4o-mini

# 测试所有可用模型
python scripts/test_ja_ko_languages.py --all-models
```

### 方法2: 在Python交互式环境中测试

```python
# 启动Python
python3

# 然后运行以下代码
from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview

interviewer = MultilingualRoleplayInterview(consensus_count=1)

# 测试日语
result_ja = interviewer.interview_country_multilingual(
    model_name="openai/gpt-4o-mini",
    country="Japan",
    language="ja"
)

# 测试韩语
result_ko = interviewer.interview_country_multilingual(
    model_name="openai/gpt-4o-mini",
    country="Korea (the Republic of)",
    language="ko"
)
```

### 方法3: 使用完整分析流程

```python
from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner

runner = RoleplayMultilingualAnalysisRunner()
runner.step0_multilingual_interview()  # 会自动包含日语和韩语
```

## ⚠️ 常见错误

### 错误1: 在终端直接运行Python代码

**错误示例:**
```bash
$ from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
zsh: command not found: from
```

**原因:** Python代码需要在Python解释器中运行，不能直接在shell中运行。

**解决方法:**
1. 使用测试脚本: `python scripts/test_ja_ko_languages.py`
2. 进入Python交互式环境: `python3` 然后输入代码
3. 创建Python文件并运行: `python your_script.py`

## 🔍 验证要点

测试时请检查：

1. **问题文本是否为日/韩语**
   - 查看输出中的问题文本，确认是日文/韩文而非英文

2. **回答格式是否正确**
   - 确认模型返回的是数字答案（如 "1", "2", "3" 等）
   - 确认答案符合题目要求（单选题、多选题等）

3. **增量访谈功能**
   - 运行第二次时，已完成的访谈应该被跳过
   - 新数据会自动合并到已有数据中

4. **数据保存**
   - 检查 `data/roleplay_multilingual/llm_responses_roleplay_ml/` 目录
   - 确认生成了新的结果文件

## 📊 预期测试结果

- ✅ 日语访谈: 10个问题全部得到有效回答
- ✅ 韩语访谈: 10个问题全部得到有效回答
- ✅ 回答格式: 符合IVS问卷格式要求
- ✅ 数据保存: 结果正确保存到JSON文件

## 🚀 下一步

测试成功后，可以：
1. 运行完整的多语言访谈（包含所有语言）
2. 进行数据处理和分析
3. 运行PCA分析和可视化





