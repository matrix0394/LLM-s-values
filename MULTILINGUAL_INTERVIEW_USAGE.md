# Multilingual Roleplay Interview Usage Guide

## 概述

`roleplay_multilingual`模块现在已经集成了完整的访谈功能，可以直接在run脚本中进行多语言角色扮演访谈。

## 新增功能

### 1. 步骤0: 多语言角色扮演访谈

新增了`step0_multilingual_interview()`方法，可以：
- 使用英文和本国语言访谈真实国家
- 调用`MultilingualRoleplayInterview`类进行批量访谈
- 自动保存访谈结果到`data/roleplay_multilingual/`目录

### 2. 完整流程集成

现在完整的分析流程包括：
- **步骤0**: 多语言角色扮演访谈（可选）
- **步骤1**: 多语言Roleplay数据处理
- **步骤2**: 多语言+IVS联合PCA分析
- **步骤3**: 英文vs本国语言效果对比分析
- **步骤4**: 综合可视化

## 使用方法

### 方法1: 完整分析（包含访谈）

```python
from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner

# 创建运行器
runner = RoleplayMultilingualAnalysisRunner()

# 运行完整分析（包含访谈）
success = runner.run_complete_analysis()
```

### 方法2: 跳过访谈，使用现有数据

```python
# 跳过访谈步骤，直接使用现有数据
success = runner.run_complete_analysis(skip_interview=True)
```

### 方法3: 仅运行访谈

```python
# 仅运行访谈步骤
success = runner.run_interview_only()
```

## 访谈配置

### 默认国家列表
如果没有推荐国家文件，将使用以下默认国家：
- China, United States, Germany, Brazil, India
- Japan, France, Russia, Mexico, Australia

### 语言设置
- **英文**: english
- **本国语言**: native（根据国家自动选择）

### 模型设置
- 使用`config/llm_models.json`中配置的所有可用模型
- 默认并发数: 3

## 数据文件结构

### 访谈数据文件
```
data/roleplay_multilingual/
├── interview_data_20251016_HHMMSS.json  # 访谈原始数据
├── multilingual_roleplay_processed_responses_ivs_format.pkl  # 处理后数据
└── multilingual_entity_scores_pca_fixed.pkl  # PCA结果
```

### 结果文件
```
results/roleplay_multilingual/
├── multilingual_cultural_map_corrected.png  # 文化地图
├── language_distance_comparison.png  # 语言效果对比
├── model_specific_language_comparison.png  # 模型语言对比
└── language_comparison_analysis.json  # 对比分析结果
```

## 访谈数据格式

访谈结果保存为JSON格式：
```json
{
  "timestamp": "20251016_HHMMSS",
  "total_tasks": 120,
  "successful_tasks": 115,
  "success_rate": 0.958,
  "models": ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet", ...],
  "languages": ["zh-cn", "en", "ru", "es-la", "ar"],
  "responses": {
    "model_country_language": {
      "model_name": "openai/gpt-4o-mini",
      "country": "China",
      "language": "zh-cn",
      "responses": [...]
    }
  }
}
```

## 命令行使用

```bash
# 进入项目目录
cd "/Users/yxy/code/LLM's values"

# 运行完整分析
python3 -c "
from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner
runner = RoleplayMultilingualAnalysisRunner()
runner.run_complete_analysis()
"

# 仅运行访谈
python3 -c "
from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner
runner = RoleplayMultilingualAnalysisRunner()
runner.run_interview_only()
"
```

## 注意事项

1. **API配置**: 确保`config/llm_models.json`和环境变量正确配置
2. **数据完整性**: 访谈会自动检查现有数据，避免重复访谈
3. **并发控制**: 默认使用3个并发线程，可根据API限制调整
4. **错误处理**: 访谈失败不会中断整个流程，会继续处理其他任务
5. **数据兼容**: 新的访谈数据与现有的数据处理流程完全兼容

## 故障排除

### 常见问题

1. **访谈失败**: 检查API配置和网络连接
2. **数据格式错误**: 确保使用正确的国家名称和语言代码
3. **文件权限**: 确保对数据目录有写权限

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

runner = RoleplayMultilingualAnalysisRunner()
runner.run_interview_only()
```





