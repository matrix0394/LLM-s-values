# Multilingual Roleplay 时间戳和交互式功能指南

## 🎯 新功能概述

### 1. **交互式访谈选择**
- 当检测到现有访谈数据时，系统会提供交互式选择
- 用户可以选择使用现有数据或重新访谈
- 避免意外覆盖重要数据

### 2. **时间戳文件管理**
- 所有生成的文件都包含时间戳 `YYYYMMDD_HHMMSS`
- 自动读取最新文件，避免版本混乱
- 保留历史版本，便于对比和回溯

### 3. **智能文件检测**
- 自动检测文件新旧程度
- 只有在必要时才重新处理数据
- 提高运行效率

## 📋 文件命名规则

### 访谈数据
```
data/roleplay_multilingual/
├── interview_data_20251016_143000.json          # 访谈原始数据
├── interview_data_20251016_150000.json          # 新的访谈数据
└── interview_data_20251016_160000.json          # 最新访谈数据
```

### 处理后数据
```
data/roleplay_multilingual/
├── multilingual_roleplay_processed_responses_ivs_format_20251016_143000.pkl
├── multilingual_entity_scores_pca_fixed_20251016_143500.pkl
└── multilingual_entity_scores_pca_fixed_20251016_143500.json
```

### 分析结果
```
results/roleplay_multilingual/
├── language_comparison_analysis_20251016_144000.json
├── multilingual_accuracy_analysis_20251016_144500.json
└── summary_statistics_20251016_144500.txt
```

### 可视化文件
```
results/roleplay_multilingual/
├── multilingual_cultural_map_corrected_20251016_145000.png
├── multilingual_cultural_map_interactive_fixed_20251016_145000.html
├── language_distance_comparison_20251016_145100.png
├── country_level_language_comparison_20251016_145100.png
├── interactive_language_comparison_20251016_145100.html
├── model_specific_language_comparison_20251016_145200.png
├── interactive_model_language_comparison_20251016_145200.html
├── language_model_comparison_20251016_145300.png
└── multilingual_cultural_coordinates_20251016_145300.json
```

## 🎮 交互式使用流程

### 场景1: 首次运行
```bash
python3 -c "
from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner
runner = RoleplayMultilingualAnalysisRunner()
runner.run_complete_analysis()
"
```

**输出示例:**
```
🎤 步骤0: 多语言角色扮演访谈
❌ 多语言问答数据文件不存在
🚀 开始多语言角色扮演访谈...
[进行访谈...]
```

### 场景2: 检测到现有数据
```bash
python3 -c "
from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner
runner = RoleplayMultilingualAnalysisRunner()
runner.run_complete_analysis()
"
```

**输出示例:**
```
🎤 步骤0: 多语言角色扮演访谈
✅ 发现已有访谈数据: interview_data_20251016_143000.json
📊 现有访谈数据统计:
   - 国家数量: 19
   - 总访谈条目: 456
💡 发现充足的访谈数据
请选择操作:
  1. 使用现有数据，跳过访谈
  2. 重新进行访谈（会生成新的时间戳文件）
请输入选择 (1 或 2): 
```

### 场景3: 选择重新访谈
```
请输入选择 (1 或 2): 2
🔄 选择重新访谈，将生成新的数据文件
🚀 开始多语言角色扮演访谈...
[进行新访谈...]
💾 访谈结果已保存到: interview_data_20251016_160000.json
```

### 场景4: 选择使用现有数据
```
请输入选择 (1 或 2): 1
✅ 选择使用现有数据，跳过访谈步骤
📊 步骤1: 多语言Roleplay数据处理
📁 找到 1 个访谈数据文件
📁 使用最新文件: interview_data_20251016_143000.json
```

## 🔄 智能文件管理

### 自动选择最新文件
系统会自动选择最新的文件进行处理：

```python
# 示例：查找最新访谈文件
interview_files = list(data_path.glob("interview_data_*.json"))
latest_file = max(interview_files, key=lambda x: x.stat().st_mtime)
```

### 文件时间比较
系统会比较文件时间，避免不必要的重复处理：

```
✅ 发现 2 个已处理数据文件
✅ 使用最新文件: multilingual_roleplay_processed_responses_ivs_format_20251016_143000.pkl
💡 处理文件比访谈文件新，且数据充足
```

### 增量处理
只有在以下情况才会重新处理：
- 访谈文件比处理文件新
- 处理文件数据不足（< 10行）
- 找不到处理文件

## 📊 使用建议

### 1. **日常使用**
```python
# 推荐：让系统自动选择
runner.run_complete_analysis()
```

### 2. **强制重新访谈**
```python
# 仅重新访谈
runner.run_interview_only()
```

### 3. **跳过访谈**
```python
# 直接使用现有数据
runner.run_complete_analysis(skip_interview=True)
```

### 4. **查看文件历史**
```bash
# 查看所有访谈文件
ls -lt data/roleplay_multilingual/interview_data_*.json

# 查看所有结果文件
ls -lt results/roleplay_multilingual/*_*.png
```

## 🛠️ 故障排除

### 问题1: 交互式输入不工作
**原因**: 在非交互式环境中运行
**解决**: 使用 `skip_interview=True` 或 `run_interview_only()`

### 问题2: 文件版本混乱
**原因**: 手动修改了文件时间戳
**解决**: 删除旧文件或使用明确的文件路径

### 问题3: 磁盘空间不足
**原因**: 时间戳文件积累过多
**解决**: 定期清理旧文件
```bash
# 只保留最新的3个文件
find data/roleplay_multilingual/ -name "*_*.pkl" -type f | sort -r | tail -n +4 | xargs rm -f
```

## 🔒 数据安全

### 备份策略
- 所有文件都有时间戳，自然形成版本历史
- 重要结果会同时保存为 `.pkl` 和 `.json` 格式
- 交互式选择避免意外覆盖

### 恢复方法
```python
# 恢复到特定时间点的数据
timestamp = "20251016_143000"
pca_file = f"data/roleplay_multilingual/multilingual_entity_scores_pca_fixed_{timestamp}.pkl"
entity_scores = pd.read_pickle(pca_file)
```

## 📈 性能优化

### 缓存机制
- 自动检测文件新旧程度
- 避免重复处理相同数据
- 智能跳过不必要的步骤

### 并发控制
- 访谈步骤支持并发控制
- 文件锁定机制防止冲突
- 优雅的错误处理和恢复

---

**注意**: 所有时间戳都使用本地时间，格式为 `YYYYMMDD_HHMMSS`。确保系统时间准确以获得正确的文件排序。





