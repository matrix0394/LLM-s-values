# 统一多语言分析运行器使用指南

## 🚀 快速开始

只需运行一个命令：
```bash
python3 src/run/run_roleplay_multilingual_analysis.py
```

## 📋 运行模式选择

运行后会看到以下选项：

### 1. 完整分析流程
- **功能**: 访谈 → 数据处理 → PCA分析 → 可视化
- **适用**: 首次完整运行
- **包含**: 交互式选择访谈方式

### 2. 小规模验证测试 ⭐ 推荐新手
- **功能**: 3国家 × 3模型 × 3重复 + 完整后续分析
- **费用**: ~$0.59
- **时间**: ~20分钟
- **适用**: 验证系统功能，快速体验

### 3. 全面测试 ⭐ 推荐研究
- **功能**: 12国家 × 7模型 × 5重复 + 完整后续分析
- **费用**: ~$5.58
- **时间**: ~40分钟
- **适用**: 获得完整高质量数据

### 4. 仅数据处理
- **功能**: 处理现有访谈数据为IVS格式
- **适用**: 有访谈数据，需要重新处理

### 5. 仅PCA分析
- **功能**: 基于处理后数据进行PCA分析
- **适用**: 有处理后数据，需要重新分析

### 6. 仅可视化
- **功能**: 基于PCA结果生成图表和分析
- **适用**: 有PCA结果，需要重新可视化

## 🎯 关键改进

### ✅ 统一入口
- 所有功能都在一个脚本中
- 不再需要多个独立脚本
- 简化使用流程

### ✅ 自动流程
- 测试完成后自动进行后续步骤
- 数据处理 → PCA分析 → 可视化
- 无需手动干预

### ✅ 详细输出
- 实时显示模型回答过程
- 显示问题内容和原始回答
- 显示众数计算过程
- 监控访谈成功率

### ✅ 智能配置
- 自动检测配置文件类型
- 支持小规模和全面测试配置
- 自动转换结果格式

## 📊 输出文件

### 访谈数据
- `data/roleplay_multilingual/interview_data_YYYYMMDD_HHMMSS.json`

### 处理后数据
- `data/roleplay_multilingual/multilingual_roleplay_processed_responses_ivs_format_YYYYMMDD_HHMMSS.pkl`

### PCA结果
- `data/roleplay_multilingual/multilingual_entity_scores_pca_fixed_YYYYMMDD_HHMMSS.pkl`

### 可视化结果
- `results/roleplay_multilingual/multilingual_cultural_map_corrected.png`
- `results/roleplay_multilingual/interactive_language_comparison.html`
- `results/roleplay_multilingual/language_comparison_analysis.json`

## 💡 使用建议

### 首次使用
1. 选择 **"2. 小规模验证测试"**
2. 观察详细输出，了解系统工作方式
3. 检查生成的结果文件

### 正式研究
1. 选择 **"3. 全面测试"**
2. 获得完整的高质量数据
3. 用于正式分析和发表

### 调试问题
1. 选择 **"4-6"** 单独运行特定步骤
2. 定位问题所在环节
3. 重新运行有问题的步骤

## 🔧 配置文件

### 小规模测试
- `small_scale_test_config.json`
- 3国家 × 3模型 × 3重复

### 全面测试
- `comprehensive_multilingual_config.json`
- 12国家 × 7模型 × 5重复

## ⚠️ 注意事项

1. **API配额**: 确保有足够的API调用配额
2. **网络稳定**: 长时间运行需要稳定网络
3. **磁盘空间**: 确保有足够存储空间
4. **并发控制**: 系统已优化并发数，避免API限制

---

**现在只需要一个命令就能完成所有操作！** 🎉


