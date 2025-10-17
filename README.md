# 🌍 LLM文化价值观研究项目

## 📖 项目概述

本项目是一个基于世界价值观调查(World Values Survey, IVS)数据的大语言模型文化价值观研究平台。项目通过让LLM模仿不同国家的文化背景回答价值观问题，分析和对比LLM在不同语言环境下的文化表达差异。

## 🏗️ 核心功能

### 1. 基础框架 (`src/base/`)
- **PCA分析**: 基于IVS数据的主成分分析
- **数据处理**: IVS问题处理和标准化
- **可视化**: 文化地图绘制和交互式图表

### 2. 国家真实坐标 (`src/core/`)
- 基于真实IVS调查数据生成国家文化坐标
- Inglehart-Welzel文化地图构建
- 文化区域分类和可视化

### 3. LLM价值观分析 (`src/llm_analysis/`)
- LLM直接回答价值观问题
- 计算LLM的文化坐标位置
- 分析LLM的文化倾向

### 4. 英文角色扮演 (`src/roleplay/`)
- LLM用英文模仿不同国家文化
- 对比模仿效果与真实国家的差异
- 多模型性能评估

### 5. 多语言对比实验 (`src/multilingual/`)
- **核心功能**: LLM用英文vs本国语言模仿国家文化
- 支持中文、俄语、西班牙语、阿拉伯语等多种语言
- 语言对文化表达影响的定量分析

## 🚀 快速开始

### 环境配置
```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥 (在config/目录下配置相应的API密钥)
```

### 主要实验脚本

#### 1. 多语言对比实验 (推荐)
```bash
# 运行扩展多语言实验 - 核心功能
python run_extended_multilingual_experiment.py
```

#### 2. 角色扮演系统
```bash
# 启动角色扮演系统
python start_roleplay_system.py
```

#### 3. 使用示例
```bash
# 查看基本使用方法
python example_usage.py
```

## 📁 项目结构

```
LLM's values/
├── src/                          # 核心代码模块
│   ├── base/                     # 基础框架
│   ├── core/                     # 国家真实坐标
│   ├── llm_analysis/             # LLM价值观分析
│   ├── roleplay/                 # 英文角色扮演
│   └── multilingual/             # 多语言对比实验 ⭐
├── config/                       # 配置文件
│   ├── ivs_questions.json        # IVS问题配置
│   ├── llm_models.json          # 模型配置
│   ├── cultural_regions.json    # 文化区域配置
│   └── multilingual_questions_complete.json  # 多语言问题
├── data/                         # 数据文件
│   ├── raw/                      # 原始IVS数据
│   ├── processed/                # 处理后数据
│   ├── results/                  # 实验结果
│   └── backup/                   # 备份文件
├── scripts/                      # 辅助脚本
│   ├── analysis/                 # 分析脚本
│   ├── experiments/              # 实验脚本
│   ├── maintenance/              # 维护脚本
│   ├── runners/                  # 运行脚本
│   └── archive/                  # 归档脚本
├── docs/                         # 文档
├── results/                      # 输出结果
└── logs/                         # 日志文件
```

## 🎯 核心实验：多语言文化对比

### 实验设计
- **研究问题**: 语言是否影响LLM的文化价值表达？
- **实验方法**: 让LLM用英文和本国语言分别模仿同一国家
- **对比指标**: PCA文化坐标距离、与真实国家的相似度

### 支持的语言和国家
- **中文**: 中国、台湾、香港、澳门
- **俄语**: 俄罗斯、白俄罗斯、哈萨克斯坦、乌克兰、吉尔吉斯斯坦
- **西班牙语**: 西班牙、墨西哥、阿根廷、哥伦比亚、秘鲁
- **阿拉伯语**: 埃及、沙特阿拉伯、伊拉克、阿尔及利亚、摩洛哥

### 支持的模型
- OpenAI GPT-4o-mini
- Google Gemini-2.0-Flash
- Meta Llama-3.3-70B
- DeepSeek Chat v3
- Qwen QwQ-32B
- Mistral Nemo

## 📊 主要发现

基于已完成的实验分析：

1. **语言效应显著**: 不同语言下LLM的文化表达存在系统性差异
2. **模型差异**: 不同模型对语言的敏感性不同
3. **文化特异性**: 某些文化特征在特定语言下表达更准确

详细分析报告请查看 `results/` 目录下的相关文件。

## 📚 文档指南

- **快速开始**: `docs/QUICK_START.md`
- **多语言实验指南**: `MULTILINGUAL_EXPERIMENT_GUIDE.md`
- **项目清理计划**: `PROJECT_CLEANUP_PLAN.md`
- **角色扮演系统**: `docs/ROLEPLAY_SYSTEM_README.md`

## 🔧 开发和维护

### 脚本说明
- `scripts/analysis/`: 数据分析和可视化脚本
- `scripts/experiments/`: 实验相关脚本
- `scripts/maintenance/`: 数据修复和维护脚本
- `scripts/runners/`: 各种运行脚本

### 数据管理
- 原始数据存储在 `data/raw/`
- 处理后数据存储在 `data/processed/`
- 实验结果存储在 `data/results/`
- 备份文件存储在 `data/backup/`

## 🤝 贡献指南

1. 确保代码符合项目结构规范
2. 新增功能请在相应的模块目录下开发
3. 重要实验结果请保存在 `results/` 目录
4. 更新相关文档

## 📄 许可证

本项目仅供学术研究使用。

## 📞 支持

如有问题，请查看：
1. `docs/` 目录下的相关文档
2. `logs/` 目录下的运行日志
3. `results/` 目录下的分析报告

---

**核心贡献**: 首次系统性研究了语言对大语言模型文化价值表达的影响，为跨语言AI研究提供了重要的方法论和实证基础。