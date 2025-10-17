# 控制变量多语言对比实验指南

## 🎯 实验目标

验证**语言对LLM文化价值观表达的影响**，通过严格的控制变量实验设计，确保语言是唯一变量，其他所有条件完全一致。

## 📋 实验设计

### 控制变量（唯一变量）
- **语言**: 英文(en)、中文(zh-cn)、俄文(ru)、西班牙文(es)、阿拉伯文(ar)
- **本土化**: 每种语言使用相应的本土化问题表述和文化背景描述

### 固定条件（完全相同）
- **目标国家**: 中国、俄罗斯、墨西哥、埃及、德国、日本
- **测试模型**: GPT-4o-mini, DeepSeek-Chat, Gemini-2.0-Flash (移除了昂贵的Claude)
- **问题集合**: A008, A165, E018, E025, F063, F118, F120, G006, Y002, Y003
- **模型参数**: temperature=0.1, max_tokens=50 (固定)
- **重复次数**: 每个条件2-3次
- **处理逻辑**: 统一的`IVSQuestionProcessor`
- **PCA方法**: 统一的`BasePCAAnalyzer`
- **可视化**: 统一的`BaseCulturalMapVisualizer`

## 🚀 快速开始

### 1. 试点实验（推荐先运行）

```bash
python run_real_controlled_multilingual_experiment.py
# 选择 "1. 试点实验"
```

### 3. 仅分析现有数据（调试PCA）

如果问答数据已收集完成，但PCA分析出错需要调试：

```bash
python run_real_controlled_multilingual_experiment.py
# 选择 "3. 仅分析现有数据"
```

**优势**:
- 跳过API调用，节省时间和成本
- 直接使用现有的checkpoint数据
- 适合调试PCA、可视化等后续步骤
- 自动检测可用的数据文件

**试点配置**:
- 语言: 英文 + 中文 (2种)
- 国家: 中国 + 德国 (2个)
- 模型: GPT-4o-mini (1个)
- 重复: 1次
- **总API调用**: 2×2×1×1×10 = 40次

### 2. 完整实验

```bash
python run_real_controlled_multilingual_experiment.py
# 选择 "2. 完整实验"
```

**完整配置**:
- 语言: 英文 + 中文 + 俄文 (3种)
- 国家: 中国、俄罗斯、墨西哥、德国、日本 (5个)
- 模型: GPT-4o-mini + DeepSeek + Gemini (3个)
- 重复: 2次
- **总API调用**: 3×5×3×2×10 = 900次

## 💰 成本估算

### 模型成本（每1000次调用）
- **GPT-4o-mini**: ~$0.10
- **DeepSeek-Chat**: ~$0.05
- **Gemini-2.0-Flash**: 免费额度内

### 实验成本估算
- **试点实验**: ~$0.01
- **完整实验**: ~$0.45

## 📁 文件结构

```
src/multilingual/
├── controlled_multilingual_experiment.py    # 主实验框架
├── multilingual_roleplay_interview.py       # 原有多语言访谈
├── multilingual_roleplay_pca_analysis.py    # 原有PCA分析
└── unified_multilingual_pca_analysis.py     # 统一PCA分析

config/
└── multilingual_questions_complete.json     # 多语言问题配置

scripts/
├── run_real_controlled_multilingual_experiment.py  # 实验运行脚本
├── test_real_multilingual_api.py                   # API测试脚本
└── demo_controlled_multilingual_experiment.py      # 演示脚本（已移除模拟数据）
```

## 🔧 核心组件

### 1. ControlledLanguageInterview
```python
# 特定语言的控制访谈
interviewer = ControlledLanguageInterview(
    language="zh-cn",
    config=experiment_config,
    data_path="data"
)

# 访谈所有目标国家
results = interviewer.interview_all_countries()
```

### 2. ControlledMultilingualPCA
```python
# 控制变量的多语言PCA分析
analyzer = ControlledMultilingualPCA(data_path="data")
pca_results = analyzer.run_language_specific_analysis("zh-cn")
```

### 3. ControlledMultilingualVisualization
```python
# 多语言对比可视化
visualizer = ControlledMultilingualVisualization(data_path="data")
viz_results = visualizer.create_language_comparison_plots(analysis_results)
```

## 📊 实验流程

### 第一步: 数据收集
```
🌍 英文访谈 → 🏛️ 中国 → 🤖 GPT-4o-mini → 📝 10个问题
🌍 中文访谈 → 🏛️ 中国 → 🤖 GPT-4o-mini → 📝 10个问题
🌍 俄文访谈 → 🏛️ 俄罗斯 → 🤖 GPT-4o-mini → 📝 10个问题
...
```

### 第二步: 统一处理
```
📝 原始响应 → 🔄 IVSQuestionProcessor → 📊 标准化数据
- Y002: "1 3" → 物质主义评分: 1
- Y003: "1 2 3 5 7" → 主要值: 1
- A008: "1" → 数值: 1
```

### 第三步: PCA分析
```
📊 标准化数据 → 🔬 BasePCAAnalyzer → 📈 PCA坐标
- 相同的PPCA算法
- 相同的Varimax旋转
- 相同的缩放参数
```

### 第四步: 对比分析
```
📈 PCA坐标 → 🔍 语言差异分析 → 📋 实验报告
- 语言间距离矩阵
- 跨语言一致性评分
- 文化特征保持分析
```

## 📈 结果分析

### 1. 语言差异分析
- **同一国家在不同语言下的PCA坐标差异**
- **语言间的平均距离矩阵**
- **语言对文化定位的影响程度**

### 2. 跨语言一致性
- **每个国家的跨语言响应一致性**
- **问题层面的语言敏感性分析**
- **模型层面的语言稳定性评估**

### 3. 文化特征保持
- **不同语言下文化区分度的保持情况**
- **文化聚类模式的稳定性**
- **语言对文化表达的影响评估**

## 🎨 可视化输出

### 1. 多语言PCA对比图
```
📊 multilingual_pca_comparison.png
- 2×3子图布局
- 每种语言一个子图
- 相同的坐标尺度
- 国家标签和颜色编码
```

### 2. 语言差异热图
```
🔥 language_difference_heatmap.png
- 语言×语言矩阵
- 平均PCA坐标距离
- 颜色强度表示差异程度
```

### 3. 一致性分析图
```
📈 consistency_analysis.png
- 每个国家的跨语言一致性条形图
- 颜色编码: 绿色=一致, 红色=不一致
- 标准差作为一致性指标
```

## 🔍 预期结果类型

### 理想情况（语言无影响）
- ✅ 不同语言下同一国家的PCA坐标高度相似
- ✅ 跨语言一致性分数接近1.0
- ✅ 文化聚类模式保持稳定
- ✅ 语言间平均距离 < 0.1

### 语言效应显著
- ⚠️ 不同语言下同一国家的PCA坐标差异较大
- ⚠️ 跨语言一致性分数 < 0.7
- ⚠️ 某些语言下文化特征被放大或削弱
- ⚠️ 语言间平均距离 > 0.3

### 部分语言敏感
- 📊 特定问题（Y002、Y003）显示更大的语言差异
- 📊 某些国家显示更强的语言效应
- 📊 不同模型对语言的敏感性不同
- 📊 混合的一致性模式

## ⚠️ 注意事项

### API配置
1. **确保API密钥配置正确**:
   ```bash
   # 检查 config/api_keys.json
   {
     "openai": "sk-...",
     "deepseek": "sk-...",
     "google": "..."
   }
   ```

2. **检查模型配置**:
   ```bash
   # 检查 config/model_configs.json
   ```

### 成本控制
1. **先运行试点实验**验证配置
2. **监控API调用次数**和成本
3. **使用检查点功能**防止实验中断后重复调用
4. **调整repeat_count**控制重复次数

### 错误处理
1. **网络错误**: 自动重试机制
2. **API限制**: 调用间隔延迟
3. **响应解析错误**: 统一的错误处理
4. **实验中断**: 检查点恢复功能

## 📝 实验报告

### 自动生成的文件
```
data/results/controlled_multilingual_experiment/
├── controlled_experiment_YYYYMMDD_HHMMSS.json     # 完整实验结果
├── checkpoint_interviews_YYYYMMDD_HHMMSS.json     # 访谈数据检查点
├── experiment_summary_YYYYMMDD_HHMMSS.json        # 实验摘要
├── multilingual_pca_comparison.png                # PCA对比图
├── language_difference_heatmap.png                # 语言差异热图
└── consistency_analysis.png                       # 一致性分析图
```

### 关键指标
- **数据收集成功率**: 成功响应 / 总调用次数
- **跨语言一致性**: 平均一致性分数
- **语言差异程度**: 平均语言间距离
- **文化保持度**: 文化区分度保持率

## 🎉 使用示例

### 快速测试
```bash
# 1. 测试API连接
python test_real_multilingual_api.py

# 2. 运行试点实验
python run_real_controlled_multilingual_experiment.py
# 选择 "1"

# 3. 查看结果
ls data/results/controlled_multilingual_experiment/
```

### 完整实验
```bash
# 1. 确认配置和成本
python run_real_controlled_multilingual_experiment.py
# 选择 "2"，确认继续

# 2. 等待实验完成（可能需要30-60分钟）

# 3. 分析结果
# 查看生成的可视化图表和实验报告
```

## 💡 研究价值

1. **验证LLM跨语言文化表达的一致性**
2. **识别语言对文化价值观表达的影响机制**
3. **为多语言文化研究提供方法论基础**
4. **评估不同LLM模型的跨语言稳定性**
5. **为文化比较研究提供可靠的数据基础**

---

## 📞 支持

如有问题，请检查：
1. API密钥配置是否正确
2. 网络连接是否稳定
3. 模型配置是否有效
4. 数据目录权限是否正确

实验框架基于统一的base类架构，确保了处理逻辑的一致性和结果的可靠性。

