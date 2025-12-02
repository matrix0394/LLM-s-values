# Mistral 模型合并使用说明

## 概述

本系统已经配置为自动处理 `mistralai/mistral-nemo:free` 和 `mistralai/mistral-nemo` 模型的回答文件合并。系统会自动跳过 `mistral-nemo:free` 已完成的任务，避免重复调用。

## 已完成的操作

### 1. 文件合并
- ✅ 已将 `mistralai/mistral-nemo:free` 的34个国家回答文件复制到 `mistralai_mistral-nemo_merged` 目录
- ✅ 创建了合并后的回答文件结构

### 2. 检查点更新
- ✅ 更新了检查点文件，将 `mistral-nemo:free` 已完成的任务映射到 `mistral-nemo`
- ✅ 系统现在会跳过这些已完成的任务

### 3. 系统配置
- ✅ 更新了 `full_concurrent_roleplay.py`，添加了模型映射逻辑
- ✅ 创建了 `run_with_mistral_mapping.py` 运行脚本

## 使用方法

### 方法1：使用专用运行脚本（推荐）
```bash
python3 run_with_mistral_mapping.py
```

### 方法2：直接运行原系统
```bash
python3 full_concurrent_roleplay.py
```

## 系统行为

### 自动跳过逻辑
- 系统会自动识别 `mistral-nemo:free` 已完成的任务
- 将这些任务映射为 `mistral-nemo` 已完成
- 在运行过程中跳过这些任务，避免重复调用

### 文件保存
- 新的 `mistral-nemo` 回答会保存到 `data/llm_responses_roleplay/mistralai_mistral-nemo/` 目录
- 合并后的文件在 `data/llm_responses_roleplay/mistralai_mistral-nemo_merged/` 目录

## 当前状态

- **Free版本完成**: 34个国家
- **Paid版本完成**: 0个国家（待运行）
- **总任务数**: 763 (7个模型 × 109个国家)
- **已完成任务**: 812（包含映射的任务）

## 运行建议

1. **首次运行**: 使用 `run_with_mistral_mapping.py` 查看当前状态
2. **确认跳过**: 系统会显示哪些任务会被跳过
3. **开始运行**: 确认后系统会开始运行剩余任务
4. **自动保存**: 系统会定期保存检查点和结果文件

## 注意事项

- 系统会自动处理模型名称映射，无需手动干预
- 检查点文件会记录所有已完成的任务
- 可以随时中断和恢复运行
- 合并后的文件会保持原有的JSON和PKL格式

## 故障排除

如果遇到问题：
1. 检查 `data/llm_responses_roleplay/roleplay_checkpoint.json` 文件
2. 确认 `mistralai_mistral-nemo:free` 目录存在
3. 运行 `python3 merge_mistral_models.py` 重新合并文件
