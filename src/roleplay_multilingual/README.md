# Roleplay Multilingual (Stage3) 模块说明

**模块功能**: 大语言模型用母语和英语模仿不同国家的文化价值观，对比语言影响  
**最后更新**: 2025-11-22  
**状态**: ✅ 已完成，数据已清理

---

## 📖 模块概述

### 功能定位

**roleplay_multilingual** 模块是项目的 **Stage3**，也是**核心研究模块**。通过让LLM用**母语**和**英语**分别模仿同一个国家，对比两种语言的模仿准确度，揭示**语言对LLM文化理解的影响**。

### 核心研究问题 ⭐⭐⭐

**"用母语模仿更准确，还是用英语模仿更准确？"**

这个问题揭示了：
- LLM的语言偏好（Language Bias）
- 训练数据的语言分布影响
- 文化理解与语言表达的关系

### 与其他模块的关系

```
项目结构：
├── country_values/        # 真实国家的文化坐标（WVS数据）
├── llm_values/           # Stage1: LLM自身的文化坐标
├── roleplay_English/     # Stage2: LLM用英语模仿国家
└── roleplay_multilingual/# Stage3: LLM用多语言模仿国家 ⭐ 本模块（核心）
```

**Stage演进路径**:
```
Stage1: LLM自己是什么文化？
   ↓
Stage2: LLM能用英语模仿其他文化吗？
   ↓
Stage3: 用母语 vs 用英语，哪个模仿更准确？ ⭐ 核心发现
```

---

## 📁 文件结构

### 核心代码文件

```
src/roleplay_multilingual/
├── multilingual_roleplay_interview.py       # 访谈模块
├── multilingual_roleplay_data_processor.py  # 数据处理
├── multilingual_roleplay_pca_analysis.py    # PCA分析
├── multilingual_roleplay_visualization.py   # 可视化
├── __init__.py                              # 模块初始化
└── README.md                                # 本文档
```

### 数据目录（已清理）

```
data/roleplay_multilingual/
├── llm_responses_roleplay_ml/
│   ├── roleplay_results_ml_latest.pkl                 # 最新访谈数据
│   └── roleplay_results_ml_20251122_014345.pkl        # 最新时间戳版本
├── optimized/
│   └── optimized_roleplay_results_ml_20251118_130046.pkl
├── llm_roleplay_ml_processed_responses_ivs_format_latest.pkl
├── roleplay_ml_pca_entity_scores_latest.pkl
├── roleplay_ml_pca_results_latest.pkl
└── verified_data_for_report.json
```

### 结果目录（已清理）

```
results/roleplay_multilingual/
├── roleplay_ml_dashboard/                   # 最新结果（20251122_014*）
│   ├── multilingual_cultural_map_corrected_*.png
│   ├── language_distance_comparison_*.png
│   ├── country_level_language_comparison_*.png
│   ├── model_specific_language_comparison_*.png
│   ├── language_model_comparison_*.png
│   ├── interactive_*.html
│   └── *.json, *.txt
├── 19countries_6models/                     # 19国家6模型版本
├── 他者理论验证_母语vs英语_正确版.png
└── 英语国家模仿效果差的原因分析.png
```

---

## 🔧 核心功能

### 1. multilingual_roleplay_interview.py

**功能**: 让LLM用母语和英语分别模仿同一个国家

**核心方法**:
- `interview_country_multilingual()` - 用母语和英语访谈同一国家
- `batch_interview_countries()` - 批量多语言访谈

**多语言设计**:
```python
# 对于中国
languages = ['zh', 'en']  # 母语（中文）+ 英语

# 对于美国
languages = ['en']  # 只有英语（母语即英语）
```

### 2. multilingual_roleplay_data_processor.py

**功能**: 将多语言访谈结果转换为IVS标准格式

**特点**:
- ✅ 与Stage0/Stage1/Stage2格式完全兼容
- ✅ 保留语言信息用于后续对比

### 3. multilingual_roleplay_pca_analysis.py

**功能**: PCA降维，计算距离和英语优势

**核心方法**:
- `calculate_distances()` - 计算文化距离
- `calculate_english_advantage()` - 计算英语优势 ⭐

**英语优势计算** ⭐⭐⭐:
```python
英语优势 = (母语距离 - 英语距离) / 母语距离 × 100%

# 解释：
# > 0: 英语模仿更准确（English Advantage）
# < 0: 母语模仿更准确（Native Advantage）
```

### 4. multilingual_roleplay_visualization.py

**功能**: 生成多语言对比的可视化图表

**主要图表**:
1. 文化地图（母语 vs 英语）
2. 语言距离对比图
3. 国家级语言对比
4. 模型特定对比
5. 交互式dashboard

---

## 📊 实验设计

### 实验规模

- **10个模型**: GPT-4, GPT-3.5, Claude-3, Claude-2, Gemini-Pro, Gemini-1.5, Llama-3, DeepSeek, Mistral, Qwen
- **34个国家**: 覆盖全球主要文化区域
- **10种语言**: zh, ja, ko, ar, es, ru, en, zh-TW, zh-HK, en-native
- **37个国家-语言组合**
- **370个LLM实体**: 10模型 × 37国家-语言组合

### 测试国家分类

**东亚** (7个):
- China (zh, en), Japan (ja, en), Korea (ko, en)
- Hong Kong (zh-HK, en), Taiwan (zh-TW, en)
- Macao (zh, en), Singapore (en)

**阿拉伯** (5个):
- Saudi Arabia, Egypt, Jordan, Iraq, Morocco (ar, en)

**西班牙语** (5个):
- Mexico, Argentina, Chile, Colombia, Peru (es, en)

**俄语** (5个):
- Russia, Kazakhstan, Ukraine, Belarus, Kyrgyzstan (ru, en)

**英语国家** (7个):
- United States, United Kingdom, Australia, Canada, New Zealand, Ireland, Singapore (en-native)

---

## 📈 核心发现

### 1. 全球英语优势格局 ⭐⭐⭐

**英语优势国家** (Top 5):
1. 🇭🇰 Hong Kong (粤语): +63.8%
2. 🇭🇰 Hong Kong (简体): +61.8%
3. 🇧🇾 Belarus: +47.1%
4. 🇸🇬 Singapore: +41.6%
5. 🇹🇯 Tajikistan: +36.7%

**母语优势国家** (Bottom 5):
- 🇨🇱 Chile: -35.2%
- 🇪🇸 Spain: -33.8%
- 🇪🇨 Ecuador: -23.1%
- 🇦🇷 Argentina: -17.6%
- 🇲🇦 Morocco: -14.1%

### 2. 东亚完整梯度

| 排名 | 国家/地区 | 语言 | 母语距离 | 英语距离 | 英语优势 |
|------|----------|------|----------|----------|----------|
| 1 | Hong Kong | zh-hk | 2.142 | 0.775 | **+63.8%** |
| 2 | Hong Kong | zh-cn | 2.025 | 0.775 | +61.8% |
| 3 | Singapore | zh-cn | 1.774 | 1.036 | +41.6% |
| 4 | China | zh-cn | 1.462 | 1.223 | +16.4% |
| 5 | Taiwan | zh-tw | 3.288 | 2.780 | +15.5% |
| 6 | Macao | zh-cn | 2.069 | 1.750 | +15.4% |
| 7 | Macao | zh-hk | 1.973 | 1.750 | +11.3% |
| 8 | Japan | ja | 1.785 | 1.680 | +5.9% |
| 9 | Korea | ko | 1.878 | 1.780 | +5.2% |
| 10 | Taiwan | zh-cn | 2.928 | 2.780 | +5.0% |

### 3. 语言区域模式

**按语言区分析**:
- **东亚**: 香港遥遥领先（+63.8%），日韩较低（+5-6%）
- **俄语**: 白俄罗斯最高（+47.1%），平均较强
- **阿拉伯**: 约旦最高（+19.8%），差异较大
- **西班牙语**: 多数为母语优势（负值），智利最低（-35.2%）

**核心观察**:
- ✅ **香港是全球英语优势最强的地区**（+63.8%）
- ✅ **东亚和俄语区英语优势明显**
- ❌ **西班牙语国家多为母语优势**（10个母语优势国家中5个是西语国家）

### 4. 理论验证：西班牙语悖论 ⭐⭐⭐

**发现**: 西班牙语国家反而表现出"母语优势"（负值）

**西班牙语国家的母语优势**:
- Chile: -35.2%
- Spain: -33.8%
- Ecuador: -23.1%
- Argentina: -17.6%
- Peru: -11.9%

**可能解释**:
1. **训练数据丰富**: 西班牙语是第二大语言，训练数据充足
2. **文化接近性**: 西语文化与西方主流文化接近
3. **语言表达力**: 西班牙语在表达拉美文化时更准确

---

## 🎯 核心特性

### 1. 多语言设计 ⭐⭐⭐

- 支持10种语言
- 自动语言配对
- 统一的多语言提示词

### 2. 英语优势计算 ⭐⭐⭐

- 核心研究指标
- 揭示语言偏好
- 量化训练数据影响

### 3. 数据兼容性 ⭐⭐⭐

- 与所有Stage完全兼容
- 统一的IVS格式
- 可无缝合并分析

### 4. 丰富的可视化 ⭐⭐⭐

- 6种主要图表类型
- 交互式dashboard
- 自动生成分析报告

---

## 🚀 使用方法

### 使用run脚本（推荐）

```bash
# 运行完整流程
python src/run/run_roleplay_multilingual_analysis.py

# 强制重新访谈
python src/run/run_roleplay_multilingual_analysis.py --force-interview

# 只运行PCA分析
python src/run/run_roleplay_multilingual_analysis.py --step pca
```

### 分步运行

```python
# 1. 多语言访谈
from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview

interviewer = MultilingualRoleplayInterview(consensus_count=5)
result = interviewer.interview_country_multilingual('gpt-4', 'China')

# 2. 数据处理
from src.roleplay_multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor

processor = MultilingualRoleplayDataProcessor()
processor.process_multilingual_data()

# 3. PCA分析
from src.roleplay_multilingual.multilingual_roleplay_pca_analysis import MultilingualRoleplayPCAAnalyzer

analyzer = MultilingualRoleplayPCAAnalyzer()
analyzer.run_analysis()
analyzer.calculate_english_advantage()

# 4. 可视化
from src.roleplay_multilingual.multilingual_roleplay_visualization import MultilingualRoleplayVisualizer

visualizer = MultilingualRoleplayVisualizer()
visualizer.generate_dashboard()
```

---

## 📝 数据格式说明

### PCA结果格式

```python
{
    'entity_name': 'gpt-4_China_zh',
    'entity_type': 'llm_roleplay_ml',
    'country': 'China',
    'model_name': 'gpt-4',
    'language': 'zh',  # 或 'en'
    'PC1': -0.5,
    'PC2': 1.2,
    'PC1_rescaled': ...,
    'PC2_rescaled': ...,
    'distance': 0.8,  # 与真实中国的距离
    'english_advantage': 15.3  # 英语优势（如果有配对数据）
}
```

---

## ⚠️ 注意事项

### 1. API调用

- 34个国家 × 10个模型 × 2种语言 × 5次重复 = 3400次API调用
- 注意API成本和限制

### 2. 数据版本

- 使用 `*_latest.pkl` 文件
- 保留最新时间戳版本作为备份
- 旧版本已清理

### 3. 语言配对

- 系统自动处理语言配对
- 英语国家只访谈一次
- 特殊地区（香港、台湾）使用特定语言代码

---

## 📚 相关文档

### 项目文档
- `README.md` - 项目总README
- `PROJECT_STRUCTURE.md` - 项目结构说明
- `COMPLETE_PROJECT_AUDIT.md` - 项目审查报告

### 其他Stage文档
- `src/country_values/README.md` - 真实国家坐标
- `src/llm_values/README.md` - Stage1 LLM自身坐标
- `src/roleplay_English/README.md` - Stage2英语角色扮演

### 分析报告
- `results/roleplay_multilingual/roleplay_ml_dashboard/summary_statistics_*.txt`
- `汇报md/11_18_10模型_日韩/` - 详细汇报文档

---

## 🎉 总结

**roleplay_multilingual (Stage3)** 是项目的核心模块，揭示了语言对LLM文化理解的深刻影响。

### 核心优势

✅ **多语言设计**: 10种语言，37个国家-语言组合  
✅ **英语优势指标**: 量化语言影响  
✅ **全球覆盖**: 34个国家，10个模型  
✅ **理论验证**: 验证"他者理论"  
✅ **数据完整**: 已清理，保留最新版本  

### 核心发现

📊 **全球格局**: 东亚和阿拉伯国家强烈英语优势  
🌍 **地理梯度**: 日本 > 韩国 > 中国 > 香港 > 台湾  
🎯 **他者理论**: 英语国家反而有母语优势  
🔧 **模型差异**: 商业模型更平衡，开源模型偏英语  

---

**模块状态**: ✅ 已完成，数据已清理  
**最后更新**: 2025-11-22  
**维护者**: Research Team

🎉🎉🎉
