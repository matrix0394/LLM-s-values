# 🧹 项目文件整理计划

## 📊 项目概述
这是一个LLM文化价值观研究项目，主要功能包括：
- 基于IVS数据生成国家文化地图  
- LLM模仿不同国家的文化价值观
- 对比英文vs本国语言的模仿效果
- 生成可视化分析报告

## 🗂️ 目录结构优化

### 保留的核心目录
```
src/                    # 核心代码模块 ✅
├── base/              # 基础框架
├── core/              # 国家真实坐标
├── llm_analysis/      # 大模型价值观分析
├── roleplay/          # 英文模仿功能
└── multilingual/      # 多语言模仿功能

config/                # 配置文件 ✅
├── ivs_questions.json
├── llm_models.json
├── cultural_regions.json
└── multilingual_questions_complete.json

data/                  # 数据文件 🧹
├── raw/              # 原始IVS数据
├── processed/        # 处理后的数据
└── results/          # 实验结果

docs/                  # 文档 🧹
└── 保留核心文档，删除过时文档
```

### 需要整理的目录

#### 1. 根目录脚本 🧹
**保留主要脚本：**
- `run_extended_multilingual_experiment.py` ✅ (新功能主脚本)
- `start_roleplay_system.py` ✅ (角色扮演系统)
- `example_usage.py` ✅ (使用示例)

**删除冗余脚本：**
- `run_simple_multilingual_experiment.py` ❌ (功能重复)
- `run_optimized_multilingual_experiment.py` ❌ (功能重复)  
- `run_smart_multilingual_experiment.py` ❌ (功能重复)
- `demo_correct_multilingual_experiment.py` ❌ (演示脚本)
- `test_*.py` ❌ (测试脚本)
- `verify_*.py` ❌ (验证脚本)
- `check_existing_data.py` ❌ (检查脚本)
- `analyze_system_parameters.py` ❌ (分析脚本)
- `full_concurrent_roleplay.py` ❌ (重复功能)

#### 2. scripts/ 目录重组 🧹
```
scripts/
├── experiments/       # 实验脚本 ✅
├── maintenance/       # 维护脚本 ✅  
├── runners/          # 运行脚本 🧹 (部分合并到experiments)
└── archive/          # 归档旧脚本 🆕
```

#### 3. data/ 目录清理 🧹
```
data/
├── raw/              # 原始数据 ✅
├── processed/        # 处理后数据 ✅
├── results/          # 实验结果 🧹
│   ├── latest/       # 最新结果 🆕
│   └── archive/      # 历史结果 🆕
└── backup/           # 备份数据 🆕 (合并archive内容)
```

#### 4. 文档整理 🧹
**保留核心文档：**
- `README.md` ✅
- `MULTILINGUAL_EXPERIMENT_GUIDE.md` ✅ (新功能指南)
- `docs/QUICK_START.md` ✅
- `docs/README.md` ✅

**删除过时文档：**
- `OPTIMIZATION_GUIDE.md` ❌ (已过时)
- `OPTIMIZATION_USAGE.md` ❌ (已过时)
- `MIGRATION_PLAN_PCA.md` ❌ (迁移完成)
- `MULTILINGUAL_CONFIG_CORRECTIONS.md` ❌ (配置已修正)
- `STABILITY_ANALYSIS_REPORT.md` ❌ (分析完成)
- `LLM_DISTRIBUTION_ANALYSIS_REPORT.md` ❌ (移至results/)

#### 5. 临时文件清理 ❌
- `Target(3)/` 目录 (重复的多语言问题文件)
- `logs/` 中的旧日志
- `results/` 中的临时文件
- `__pycache__/` 缓存文件

## 🎯 整理优先级

### 高优先级 (立即执行)
1. 删除根目录冗余脚本
2. 清理临时文件和目录
3. 整理data/目录结构

### 中优先级 (后续执行)  
1. 重组scripts/目录
2. 归档历史结果文件
3. 更新文档结构

### 低优先级 (可选)
1. 优化config/目录
2. 清理旧的实验结果
3. 更新README文档

## 📝 执行检查清单

- [ ] 备份重要数据
- [ ] 删除冗余脚本文件
- [ ] 清理临时目录
- [ ] 重组数据目录结构
- [ ] 归档历史文件
- [ ] 更新主要文档
- [ ] 验证核心功能正常

## ⚠️ 注意事项

1. **备份重要数据**：执行清理前先备份关键文件
2. **保留最新结果**：确保最新的实验结果不被删除
3. **测试核心功能**：清理后验证主要脚本能正常运行
4. **更新文档**：及时更新README和使用指南

## 🎉 预期效果

整理完成后，项目将具有：
- ✅ 清晰的目录结构
- ✅ 明确的功能模块划分  
- ✅ 简化的脚本入口
- ✅ 有序的数据管理
- ✅ 完善的文档体系

























