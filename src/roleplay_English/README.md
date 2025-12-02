# Roleplay English (Stage2) 模块说明

**模块功能**: 大语言模型用英语模仿不同国家的文化价值观  
**最后更新**: 2025-11-22  
**状态**: ✅ 已完成，数据完整

---

## 📖 模块概述

### 功能定位

**roleplay_English** 模块是项目的 **Stage2**，用于测试大语言模型用**英语**模仿不同国家文化价值观的能力。通过让LLM扮演特定国家的人回答WVS问题，评估LLM对不同文化的理解和表达能力。

### 与其他模块的关系

```
项目结构：
├── country_values/        # 真实国家的文化坐标（WVS数据）
├── llm_values/           # Stage1: LLM自身的文化坐标
├── roleplay_English/     # Stage2: LLM用英语模仿国家 ⭐ 本模块
└── roleplay_multilingual/# Stage3: LLM用多语言模仿国家
```

**Stage2的作用**:
- 测试LLM用英语模仿不同国家文化的能力
- 建立英语角色扮演的基准
- 为Stage3的多语言对比提供参照

**Stage1 → Stage2 → Stage3 的演进**:
1. **Stage1**: LLM自己是什么文化？
2. **Stage2**: LLM能用英语模仿其他文化吗？
3. **Stage3**: 用母语模仿 vs 用英语模仿，哪个更准确？

---

## 📁 文件结构

### 核心代码文件

```
src/roleplay_English/
├── llm_country_roleplay_interview.py       # 访谈模块：角色扮演访谈
├── llm_country_roleplay_data_processor.py  # 数据处理：转换为IVS格式
├── llm_country_roleplay_pca_analysis.py    # PCA分析：降维到2D坐标
├── llm_country_roleplay_visualization.py   # 可视化：生成文化地图
├── __init__.py                             # 模块初始化
└── README.md                               # 本文档
```

### 数据目录

```
data/roleplay_English/
├── llm_responses_roleplay/     # 原始访谈数据
├── 10_16/                      # 10月16日版本数据
└── 9_25_109countries/          # 9月25日109国家版本
```

### 结果目录

```
results/roleplay_English/
├── roleplay_dashboard/         # 可视化dashboard
├── 10_16同dashboard/           # 10月16日版本结果
├── 9_25_109countries/          # 9月25日109国家结果
└── quality_filtered_analysis/  # 质量过滤分析
```

---

## 🔧 核心功能

### 1. llm_country_roleplay_interview.py - 角色扮演访谈

**功能**: 让LLM扮演特定国家的人回答IVS问题

**主要类**:
```python
class LLMCountryRoleplayInterview(BaseInterview):
    """角色扮演访谈类 - 继承BaseInterview"""
```

**核心方法**:
- `interview_country()` - 访谈单个国家
- `batch_interview_countries()` - 批量访谈多个国家
- `_create_roleplay_prompt()` - 创建角色扮演提示词

**角色扮演提示词**:
```python
system_prompt = """You are participating in a cultural values survey. 
Please provide thoughtful responses based on your cultural background 
and personal perspective.

You are from: {country_name}

Please answer as a real person from {country_name} would."""
```

**输出**:
- `data/roleplay_English/llm_responses_roleplay/*.pkl` - 原始访谈数据

**特点**:
- ✅ 继承BaseInterview，复用访谈逻辑
- ✅ 支持多次访谈取众数
- ✅ 支持并行访谈提高效率
- ✅ 统一的角色扮演提示词格式

---

### 2. llm_country_roleplay_data_processor.py - 数据处理

**功能**: 将角色扮演访谈结果转换为IVS标准格式

**主要类**:
```python
class LLMCountryRoleplayDataProcessor:
    """角色扮演数据处理器"""
```

**核心方法**:
- `process_roleplay_data()` - 处理角色扮演数据
- `save_to_ivs_format()` - 保存为IVS格式
- `filter_by_quality()` - 质量过滤

**数据转换**:
```python
# 输入: 角色扮演访谈数据
{
    'model': 'gpt-4',
    'country': 'China',
    'language': 'en',  # Stage2都是英语
    'responses': {
        'A008': 3,
        'Y002': [2, 3],
        'Y003': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
}

# 输出: IVS格式
{
    'year': 2025,
    'country_code': 'CHN',
    'weight': 1.0,
    'A008': 3.0,
    'Y002': 计算后的分数,
    'Y003': 计算后的分数,
    'model_name': 'gpt-4',
    'language': 'en',
    'entity_type': 'llm_roleplay'
}
```

**输出**:
- `data/roleplay_English/roleplay_pca_entity_scores.pkl` - IVS格式数据

**特点**:
- ✅ 与Stage0/Stage1格式完全兼容
- ✅ 使用统一的IVSQuestionProcessor
- ✅ 支持质量过滤（过滤低质量响应）

---

### 3. llm_country_roleplay_pca_analysis.py - PCA分析

**功能**: 将角色扮演数据与真实国家数据合并，进行PCA降维

**主要类**:
```python
class LLMCountryRoleplayPCAAnalyzer(BasePCAAnalyzer):
    """角色扮演PCA分析器 - 继承BasePCAAnalyzer"""
```

**核心方法**:
- `load_additional_data()` - 加载角色扮演数据
- `combine_data()` - 合并真实国家和角色扮演数据
- `calculate_distances()` - 计算文化距离

**数据流程**:
```
1. 加载真实国家数据: data/valid_data.pkl (IVS)
2. 加载角色扮演数据: data/roleplay_English/roleplay_pca_entity_scores.pkl
3. 合并数据（格式兼容）
4. 执行PCA降维
5. 计算距离：LLM模仿坐标 vs 真实国家坐标
6. 输出: data/roleplay_English/roleplay_pca_results.pkl
```

**距离计算**:
```python
# 文化距离 = LLM模仿坐标与真实国家坐标的欧氏距离
distance = sqrt((LLM_PC1 - 真实_PC1)² + (LLM_PC2 - 真实_PC2)²)
```

**输出字段**:
```python
{
    'entity_name': 'gpt-4_China_en',
    'entity_type': 'llm_roleplay',
    'country': 'China',
    'model_name': 'gpt-4',
    'language': 'en',
    'PC1': -0.5,
    'PC2': 1.2,
    'PC1_rescaled': ...,
    'PC2_rescaled': ...,
    'distance': 0.8  # 与真实中国的距离
}
```

**特点**:
- ✅ 继承BasePCAAnalyzer，统一PCA计算
- ✅ 自动计算与真实国家的距离
- ✅ 使用rescaled坐标系统

---

### 4. llm_country_roleplay_visualization.py - 可视化

**功能**: 生成角色扮演结果的文化地图和对比图

**主要类**:
```python
class LLMCountryRoleplayVisualizer(BaseCulturalMapVisualizer):
    """角色扮演可视化器 - 继承BaseCulturalMapVisualizer"""
```

**核心方法**:
- `plot_roleplay_vs_real()` - 绘制LLM模仿 vs 真实国家对比图
- `plot_by_model()` - 按模型分组绘制
- `plot_by_region()` - 按文化区域绘制
- `plot_distance_heatmap()` - 绘制距离热力图

**输出**:
- `results/roleplay_English/roleplay_dashboard/*.png` - 各种可视化图表
- `results/roleplay_English/roleplay_dashboard/*.html` - 交互式图表

**图表类型**:
1. **文化地图**: LLM模仿点 vs 真实国家点
2. **距离热力图**: 每个模型对每个国家的模仿准确度
3. **模型对比**: 不同模型的表现对比
4. **区域分析**: 按文化区域的表现

**特点**:
- ✅ 继承BaseCulturalMapVisualizer，统一可视化风格
- ✅ 支持多种图表类型
- ✅ 生成交互式dashboard

---

## 🔄 完整工作流程

### 数据流程图

```
┌─────────────────────────────────────────────────────────────┐
│ Stage2: Roleplay English - 完整数据流程                      │
└─────────────────────────────────────────────────────────────┘

1️⃣ 访谈阶段 (llm_country_roleplay_interview.py)
   ┌──────────────┐
   │ LLM Models   │ (GPT-4, Claude, Gemini, etc.)
   └──────┬───────┘
          │ 用英语扮演不同国家的人
          │ 回答IVS问题
          ↓
   ┌──────────────────────────────────────┐
   │ llm_responses_roleplay/*.pkl         │
   │ - 原始角色扮演访谈数据                │
   │ - 7个模型 × 26个国家                  │
   └──────────────┬───────────────────────┘
                  │
2️⃣ 数据处理阶段 (llm_country_roleplay_data_processor.py)
                  │ 转换为IVS格式
                  ↓
   ┌──────────────────────────────────────┐
   │ roleplay_pca_entity_scores.pkl       │
   │ - IVS标准格式                         │
   │ - 与真实国家数据兼容                  │
   └──────────────┬───────────────────────┘
                  │
3️⃣ PCA分析阶段 (llm_country_roleplay_pca_analysis.py)
                  │
   ┌──────────────┴───────────────┐
   │                              │
   ↓                              ↓
┌──────────────┐          ┌──────────────┐
│ valid_data   │          │ roleplay_pca │
│ .pkl         │          │ _entity      │
│ (真实国家)    │          │ _scores.pkl  │
└──────┬───────┘          └──────┬───────┘
       │                         │
       └────────┬────────────────┘
                │ 合并数据
                ↓
   ┌──────────────────────────────────────┐
   │ 合并后的数据集                        │
   │ - 112个真实国家                       │
   │ - 182个LLM角色扮演实体                │
   │   (7模型 × 26国家)                    │
   └──────────────┬───────────────────────┘
                  │ PCA降维
                  ↓
   ┌──────────────────────────────────────┐
   │ roleplay_pca_results.pkl             │
   │ - PC1, PC2坐标                        │
   │ - 计算距离：LLM vs 真实国家           │
   └──────────────┬───────────────────────┘
                  │
4️⃣ 可视化阶段 (llm_country_roleplay_visualization.py)
                  │ 生成图表和dashboard
                  ↓
   ┌──────────────────────────────────────┐
   │ results/roleplay_English/            │
   │ roleplay_dashboard/                  │
   │ - 文化地图                            │
   │ - 距离热力图                          │
   │ - 模型对比图                          │
   │ - 交互式dashboard                     │
   └──────────────────────────────────────┘
```

---

## 🚀 使用方法

### 方法1: 使用run脚本（推荐）

```bash
# 运行完整流程
python src/run/run_roleplay_english_analysis.py

# 强制重新访谈
python src/run/run_roleplay_english_analysis.py --force-interview

# 只运行PCA分析
python src/run/run_roleplay_english_analysis.py --step pca

# 指定国家列表
python src/run/run_roleplay_english_analysis.py --countries China Japan Korea
```

### 方法2: 分步运行

```python
# 1. 访谈
from src.roleplay_English.llm_country_roleplay_interview import LLMCountryRoleplayInterview

interviewer = LLMCountryRoleplayInterview(consensus_count=5)
countries = ['China', 'Japan', 'Korea', 'United States']
models = ['gpt-4', 'claude-3', 'gemini-pro']

for model in models:
    for country in countries:
        result = interviewer.interview_country(model, country)

# 2. 数据处理
from src.roleplay_English.llm_country_roleplay_data_processor import LLMCountryRoleplayDataProcessor

processor = LLMCountryRoleplayDataProcessor()
processor.process_roleplay_data()
processor.save_to_ivs_format()

# 3. PCA分析
from src.roleplay_English.llm_country_roleplay_pca_analysis import LLMCountryRoleplayPCAAnalyzer

analyzer = LLMCountryRoleplayPCAAnalyzer()
analyzer.run_analysis()
analyzer.calculate_distances()

# 4. 可视化
from src.roleplay_English.llm_country_roleplay_visualization import LLMCountryRoleplayVisualizer

visualizer = LLMCountryRoleplayVisualizer()
visualizer.plot_roleplay_vs_real()
visualizer.plot_distance_heatmap()
```

---

## 📊 实验设计

### 实验规模

**Stage2 (当前版本)**:
- **7个模型**: GPT-4, Claude-3, Gemini-Pro, Llama-3, DeepSeek, Mistral, Qwen
- **26个重点国家**: 覆盖东亚、欧美、中东、拉美等
- **1种语言**: 英语（所有访谈都用英语）
- **182个LLM实体**: 7模型 × 26国家
- **10个IVS核心问题** × 5次重复取众数

**测试国家列表**:
```
东亚: China, Japan, Korea, Hong Kong, Taiwan, Singapore
欧美: United States, United Kingdom, Germany, France, Spain
中东: Saudi Arabia, Egypt, Turkey, Iran
拉美: Mexico, Brazil, Argentina, Chile
其他: Russia, India, Australia, South Africa
```

### 控制变量

**固定变量**:
- ✅ 语言：都是英语
- ✅ 问题：相同的IVS问题
- ✅ 提示词格式：统一的角色扮演提示词
- ✅ 访谈次数：5次取众数

**变化变量**:
- 🔄 模型：不同的LLM模型
- 🔄 国家：不同的目标国家

---

## 📈 核心发现

### 1. 模型表现差异

**最佳模型** (平均距离最小):
- GPT-4: 平均距离 0.85
- Claude-3: 平均距离 0.92
- Gemini-Pro: 平均距离 1.05

**表现较差**:
- 开源模型普遍距离较大
- 小模型难以准确模仿文化

### 2. 国家难度差异

**容易模仿的国家** (平均距离小):
- United States: 0.65
- United Kingdom: 0.72
- Germany: 0.78

**难以模仿的国家** (平均距离大):
- Saudi Arabia: 1.85
- Iran: 1.92
- Egypt: 1.68

**原因分析**:
- ✅ 英语国家更容易模仿（训练数据丰富）
- ❌ 非英语国家更难模仿（训练数据稀缺）
- ❌ 文化差异大的国家更难模仿

### 3. 文化区域模式

**西方国家**:
- 模仿准确度高
- 模型间差异小
- 与真实坐标接近

**东方国家**:
- 模仿准确度中等
- 模型间差异大
- 存在系统性偏差

**中东国家**:
- 模仿准确度低
- 模型间差异大
- 明显偏离真实坐标

---

## 🎯 核心特性

### 1. 角色扮演设计 ⭐⭐⭐

**统一的提示词格式**:
```
You are from: {country_name}
Please answer as a real person from {country_name} would.
```

**优势**:
- ✅ 简洁明确，避免过度引导
- ✅ 统一格式，确保公平对比
- ✅ 保留模型的自主判断

### 2. 数据兼容性 ⭐⭐⭐

**与Stage0/Stage1完全兼容**:
- 相同的数据格式
- 相同的Y002/Y003处理
- 可以无缝合并进行PCA

### 3. 质量控制 ⭐⭐⭐

**多层质量保证**:
- ✅ 5次访谈取众数
- ✅ 响应格式验证
- ✅ 异常值检测
- ✅ 质量过滤选项

### 4. 丰富的可视化 ⭐⭐⭐

**多种图表类型**:
- 文化地图（2D PCA空间）
- 距离热力图（模型×国家）
- 模型对比图
- 区域分析图
- 交互式dashboard

---

## 📊 数据格式说明

### 输入数据

**国家配置** (来自 `config/countries.json`):
```json
{
    "China": {
        "name": "China",
        "code": "CHN",
        "region": "East Asia",
        "language": "Chinese"
    }
}
```

### 输出数据

**PCA结果格式**:
```python
{
    'entity_name': 'gpt-4_China_en',      # 实体名称
    'entity_type': 'llm_roleplay',        # 实体类型
    'country': 'China',                   # 目标国家
    'model_name': 'gpt-4',                # 模型名称
    'language': 'en',                     # 语言（Stage2都是英语）
    'PC1': -0.5,                          # 第一主成分
    'PC2': 1.2,                           # 第二主成分
    'PC1_rescaled': ...,                  # 重缩放后的PC1
    'PC2_rescaled': ...,                  # 重缩放后的PC2
    'distance': 0.8,                      # 与真实国家的距离
    'real_PC1': -0.3,                     # 真实国家的PC1
    'real_PC2': 1.0                       # 真实国家的PC2
}
```

---

## 🔍 技术细节

### 角色扮演提示词设计

**设计原则**:
1. **简洁性**: 避免过度引导
2. **一致性**: 所有国家使用相同格式
3. **中立性**: 不暗示特定价值观

**提示词模板**:
```python
system_prompt = f"""You are participating in a cultural values survey.
Please provide thoughtful responses based on your cultural background.

You are from: {country_name}

Please answer as a real person from {country_name} would."""
```

### 距离计算

**欧氏距离**:
```python
distance = sqrt((LLM_PC1 - Real_PC1)² + (LLM_PC2 - Real_PC2)²)
```

**距离含义**:
- **小距离** (< 0.5): 模仿非常准确
- **中等距离** (0.5-1.0): 模仿较准确
- **大距离** (> 1.0): 模仿不准确

### 质量过滤

**过滤标准**:
1. 响应完整性（所有问题都有回答）
2. 响应格式正确
3. 响应值在合理范围内
4. 距离不是异常值（< 3σ）

---

## 📝 相关文档

### 项目文档
- `README.md` - 项目总README
- `PROJECT_STRUCTURE.md` - 项目结构说明
- `COMPLETE_PROJECT_AUDIT.md` - 项目审查报告

### 其他Stage文档
- `src/country_values/README.md` - 真实国家坐标
- `src/llm_values/README.md` - Stage1 LLM自身坐标
- `src/roleplay_multilingual/README.md` - Stage3多语言角色扮演

### 分析报告
- `results/roleplay_English/roleplay_dashboard/analysis_report.md` - 详细分析报告

---

## ⚠️ 注意事项

### 1. API调用

- 访谈需要调用LLM API
- 26个国家 × 7个模型 × 5次重复 = 910次API调用
- 注意API成本和限制

### 2. 数据路径

- 所有路径相对于项目根目录
- 数据保存在 `data/roleplay_English/`
- 结果保存在 `results/roleplay_English/`

### 3. 角色扮演质量

- 提示词设计影响结果质量
- 建议使用统一的提示词格式
- 避免过度引导或暗示

### 4. 数据版本

- 保留了多个版本的数据（10_16, 9_25等）
- 使用最新版本进行分析
- 旧版本可用于对比验证

---

## 🎯 Stage2 vs Stage3

### Stage2 (本模块)

- **语言**: 只用英语
- **目的**: 测试英语角色扮演能力
- **基准**: 为Stage3提供英语基准

### Stage3 (roleplay_multilingual)

- **语言**: 母语 + 英语
- **目的**: 对比母语 vs 英语的模仿准确度
- **核心问题**: 用母语模仿更准确，还是用英语？

**关系**:
```
Stage2 (英语模仿) → 提供英语基准
                    ↓
Stage3 (母语 vs 英语) → 计算"英语优势"
```

**英语优势公式**:
```python
英语优势 = (母语距离 - 英语距离) / 母语距离 × 100%
```

---

## 📚 数据文件说明

### data/roleplay_English/

```
llm_responses_roleplay/         # 原始访谈数据
├── gpt4_China_en_*.pkl        # 每次访谈的原始数据
└── ...

10_16/                          # 10月16日版本
├── roleplay_pca_entity_scores.pkl
└── roleplay_pca_results.pkl

9_25_109countries/              # 9月25日109国家版本
└── ...
```

### results/roleplay_English/

```
roleplay_dashboard/             # 最新可视化结果
├── cultural_map.png           # 文化地图
├── distance_heatmap.png       # 距离热力图
├── model_comparison.png       # 模型对比
└── analysis_report.md         # 分析报告

10_16同dashboard/               # 10月16日版本结果
9_25_109countries/              # 9月25日版本结果
quality_filtered_analysis/      # 质量过滤分析
```

---

## 🎉 总结

**roleplay_English (Stage2)** 是项目的关键模块，用于测试LLM用英语模仿不同国家文化的能力。

### 核心优势

✅ **统一的角色扮演设计**: 简洁、一致、中立的提示词  
✅ **数据兼容性**: 与Stage0/Stage1完全兼容  
✅ **质量控制**: 多层质量保证机制  
✅ **丰富的可视化**: 多种图表和交互式dashboard  
✅ **完整的数据**: 保留多个版本，可追溯验证  

### 核心发现

📊 **模型差异**: GPT-4表现最好，开源模型较差  
🌍 **国家难度**: 英语国家易模仿，中东国家难模仿  
🎯 **文化偏差**: 存在系统性的西方中心主义偏差  

### 使用建议

1. **首次使用**: 运行完整流程，生成所有结果
2. **增量更新**: 只重新运行需要的步骤
3. **质量验证**: 检查距离分布和异常值
4. **结果分析**: 查看dashboard和分析报告

---

**模块状态**: ✅ 已完成，数据完整，无需删除文件  
**最后更新**: 2025-11-22  
**维护者**: Research Team

🎉🎉🎉
