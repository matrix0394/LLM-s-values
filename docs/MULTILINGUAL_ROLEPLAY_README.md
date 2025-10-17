# 多语言角色扮演功能使用指南

## 功能概述

这个新功能允许大模型使用本国语言（简体中文、俄语、拉美西语、阿拉伯语）来回答IVS问题，模拟特定国家的文化价值观，并与英文版本的结果进行对比分析。

## 目标国家选择

基于语言和文化区域，我们选择了以下代表性国家：

- **简体中文**: 中国
- **俄语**: 俄罗斯联邦
- **拉美西语**: 墨西哥、阿根廷、哥伦比亚
- **阿拉伯语**: 埃及、约旦、摩洛哥

## 文件结构

```
├── config/
│   ├── multilingual_questions.json    # 多语言问题配置
│   └── multilingual_questions/        # 原始PDF文件
├── src/roleplay/
│   └── multilingual_roleplay_interview.py  # 多语言角色扮演核心模块
├── scripts/experiments/
│   └── multilingual_roleplay_experiment.py # 完整实验脚本
└── start_multilingual_experiment.py   # 简化启动脚本
```

## 使用方法

### 1. 准备工作

确保你已经：
- 设置了必要的API密钥（OPENAI_API_KEY等）
- 完善了多语言问题翻译（需要从PDF中提取完整翻译）

### 2. 完善多语言问题配置

当前的 `config/multilingual_questions.json` 只包含了简体中文的完整翻译，你需要：

1. 从 `config/multilingual_questions/` 中的PDF文件提取其他语言的问题翻译
2. 更新 `multilingual_questions.json` 中对应语言的问题内容

### 3. 运行实验

#### 方法1：使用简化启动脚本（推荐）
```bash
python start_multilingual_experiment.py
```

#### 方法2：直接运行实验脚本
```bash
python scripts/experiments/multilingual_roleplay_experiment.py
```

#### 方法3：自定义实验
```python
from scripts.experiments.multilingual_roleplay_experiment import MultilingualRoleplayExperiment

experiment = MultilingualRoleplayExperiment()
results = experiment.run_experiment(
    models=["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"],
    max_workers=2
)
```

### 4. 查看结果

实验结果将保存在：
- `data/results/multilingual_experiments/` - 完整实验结果
- `data/results/multilingual_roleplay/` - 原始访谈数据

## 实验流程

1. **多语言访谈**: 让大模型使用对应语言回答IVS问题
2. **结果分析**: 分析各语言的成功率和回答质量
3. **对比分析**: 与英文基线结果进行对比
4. **报告生成**: 生成详细的分析报告

## 预期分析内容

### 成功率对比
- 各语言的整体成功率
- 不同模型在各语言上的表现
- 特定国家的模拟效果

### 文化准确性分析
- 本国语言 vs 英文的文化坐标差异
- 语言对文化价值观表达的影响
- 不同问题在各语言中的回答模式

### 语言效应研究
- 语言是否影响价值观的表达
- 哪些文化维度受语言影响最大
- 模型的多语言文化理解能力

## 注意事项

1. **API限制**: 多语言实验会产生大量API调用，注意控制并发数和成本
2. **翻译质量**: 确保问题翻译准确，保持原意不变
3. **文化背景**: 每种语言的文化背景描述需要准确反映当地文化特点
4. **结果解读**: 需要结合文化学和语言学知识来解读结果差异

## 下一步计划

1. **完善翻译**: 从PDF中提取并完善所有语言的问题翻译
2. **扩展模型**: 测试更多大模型的多语言表现
3. **增加国家**: 为每种语言添加更多代表性国家
4. **深度分析**: 实现文化坐标的定量对比分析
5. **可视化**: 创建多语言文化地图对比可视化

## 研究价值

这个功能将帮助回答以下重要研究问题：

1. 语言是否影响大模型对文化价值观的理解和表达？
2. 使用本国语言是否能提高文化模拟的准确性？
3. 不同语言在表达特定文化维度时是否存在系统性差异？
4. 大模型的多语言文化理解能力如何？

这对于理解大模型的文化偏见、改进跨文化AI系统具有重要意义。








