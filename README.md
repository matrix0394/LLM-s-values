# 🌍 大语言模型跨语言文化价值观研究

[![项目状态](https://img.shields.io/badge/状态-实验完成-success)](https://github.com/matrix0394/LLM-s-values)
[![最后更新](https://img.shields.io/badge/更新-2025.11.22-blue)](https://github.com/matrix0394/LLM-s-values)
[![阶段](https://img.shields.io/badge/阶段-Stage3_10模型完成-brightgreen)](https://github.com/matrix0394/LLM-s-values)

## 🚀 快速导航

- **📊 查看最新结果** → [正确的距离分析](results/distance_analysis_correct/)
- **📑 汇报材料** → [Stage3一页纸汇报](汇报md/11_18_10模型_日韩/Stage3_一页纸汇报_十模型日韩.md)
- **🎬 演示文稿** → [Slides](slides/stage3/11_19.html)
- **🔧 核心脚本** → [正确的距离计算](scripts/data_analysis/calculate_correct_distances.py)
- **� 方法说明** → [距离计算方法](#-距离计算方法)

---

## 📖 项目概述

本项目通过让大语言模型用不同语言模仿不同国家的文化背景回答价值观问题，系统性地研究**语言对LLM文化价值表达的影响**。

### 🎯 核心研究问题

**语言是否影响大语言模型对文化价值观的表达？**

通过严格的控制变量实验，让LLM用英语和母语分别模仿同一国家文化，对比其文化价值表达与真实国家的距离差异。

---

## 🔬 研究阶段与规模

### Stage 0: 真实文化价值观基准
- **数据源**: World Values Survey (WVS)
- **国家/地区数**: 109个
- **问题数**: 10个核心价值观问题
- **作用**: 提供真实文化坐标作为对比基准

### Stage 1: LLM原生文化倾向
- **模型数**: 10个主流LLM
- **问题**: 直接回答价值观问题（无角色扮演）
- **作用**: 测量每个模型的原生文化倾向
- **发现**: 不同模型展现不同的文化倾向基线

### Stage 2: 英语角色扮演（暂时停用）
- **状态**: 因数据兼容性问题暂时跳过
- **原计划**: 测试纯英语角色扮演效果

### Stage 3: 多语言对比实验（核心）⭐
- **10个模型**: GPT-4o-mini, Gemini 2.0/2.5, Claude 3.7/4.5, Llama 3.3, DeepSeek v3, Mistral Nemo, QwQ-32B, Grok
- **34个国家/地区**: 覆盖东亚、俄语区、阿拉伯、西班牙语区
- **10种语言**: 英语 + 9种母语（中文、日语、韩语、俄语、西班牙语、阿拉伯语等）
- **669条模仿数据**: 34国家/地区 × 10模型 × 2-3语言
- **控制变量设计**: 仅改变语言，其他条件完全相同

---

## 🏆 核心发现

### 1. 全球英语优势格局

基于**真实WVS坐标**的正确计算：

- **84.4%的国家显示英语优势**（54/64）
- **15.6%的国家显示母语优势**（10/64）
- **最强英语优势**：香港(粤语) +63.8%
- **最强母语优势**：智利 -35.2%

**英语优势 Top 5**：
1. 🥇 香港(粤语): +63.8%
2. 🥈 香港(简体): +61.8%
3. 🥉 白俄罗斯: +47.1%
4. 新加坡: +41.6%
5. 塔吉克斯坦: +36.7%

### 2. 东亚完整梯度

```
台湾简体 (+5.0%) → 韩国 (+5.2%) → 日本 (+5.9%) → 
澳门粤语 (+11.3%) → 澳门简体 (+15.4%) → 台湾繁体 (+15.5%) → 
中国 (+16.4%) → 新加坡 (+41.6%) → 香港简体 (+61.8%) → 香港粤语 (+63.8%)
```

**关键发现**：
- ✅ **所有东亚国家都是英语优势**（之前错误计算认为日本是母语优势）
- 🏆 **香港遥遥领先**：+63.8%，远超其他国家
- 📊 **日韩台接近中性**：+5-6%，母语和英语模仿都比较准确

### 3. 语言区对比

| 语言区 | 平均英语优势 | 特点 |
|--------|--------------|------|
| **东亚** | **+24.2%** | 最强，香港效应 |
| **俄语区** | **+19.9%** | 第二强，白俄罗斯突出 |
| 阿拉伯语 | +1.8% | 两极分化 |
| **西班牙语** | **-12.8%** | 唯一母语优势主导 |

### 4. "数据驱动东方学"理论验证

**核心公式**：
```
英语优势 = f(训练数据稀缺度40%, 他者讨论比重40%, 数据质量20%)
```

**验证案例**：
- **香港** (+63.8%): 数据极度稀缺 + 高他者讨论 → 最强英语优势
- **日本** (+5.9%): 数据稀缺 + 高数据质量 → 弱英语优势
- **西班牙** (-33.8%): 数据充足 + 高数据质量 → 强母语优势

---

## 📊 距离计算方法

### ✅ 正确的方法（当前使用）

```python
# 距离 = LLM模仿坐标与真实WVS坐标的欧氏距离
distance = sqrt((LLM_PC1 - 真实WVS_PC1)² + (LLM_PC2 - 真实WVS_PC2)²)

# 英语优势
英语优势 = (母语距离 - 英语距离) / 母语距离 × 100%
```

- **正值**：英语模仿比母语模仿更接近真实国家（英语优势）
- **负值**：母语模仿比英语模仿更接近真实国家（母语优势）



---

## 🔄 数据流程

```
Stage0 (真实基准)          Stage1 (LLM原生)          Stage3 (多语言模仿)
     ↓                          ↓                          ↓
WVS问卷数据              直接回答问题              角色扮演回答
(109国家/地区)           (10个模型)              (10模型×34国家/地区×10语言)
     ↓                          ↓                          ↓
PCA降维                   PCA降维                   PCA降维
     ↓                          ↓                          ↓
PC1/PC2坐标              PC1/PC2坐标              PC1/PC2坐标
     ↓                          ↓                          ↓
     └──────────────┬───────────┴───────────────┐
                    ↓                           ↓
            跨Stage分析                  可视化与理论验证
                    ↓                           ↓
        ┌───────────┼───────────┐       ┌──────┴──────┐
        ↓           ↓           ↓       ↓             ↓
  Stage0 vs   Stage1 vs   英语母语   东方主义    港台澳
   Stage3      Stage3      基准      理论验证    专项分析
    距离        分布        对比
```

**关键数据文件**：
- `country_scores_pca.json` - Stage0真实坐标（109个）
- `llm_pca_entity_scores.pkl` - Stage1原生坐标（10个）
- `roleplay_ml_pca_entity_scores_latest.pkl` - Stage3聚合坐标（778行）
  - IVS基准：109个国家/地区
  - Multilingual：669条模仿数据

---

## 🏗️ 项目结构

```
LLM's values/
├── README.md                          # 项目总README
│
├── 📁 data/                           # 数据存储
│   ├── country_values/               # Stage0: 真实国家/地区数据
│   │   ├── country_scores_pca.json  # 109个国家/地区的PCA坐标
│   │   ├── ivs_df.pkl               # 原始IVS问卷数据
│   │   └── country_codes.pkl        # 国家/地区代码映射
│   │
│   ├── llm_values/                   # Stage1: LLM原生倾向
│   │   ├── llm_pca_entity_scores.pkl  # 10个模型的原生坐标
│   │   └── llm_responses/           # 原始LLM回答
│   │
│   ├── roleplay_English/             # Stage2: 英语角色扮演（暂时跳过）
│   │   └── (兼容性问题，暂时跳过)
│   │
│   └── roleplay_multilingual/        # Stage3: 多语言角色扮演 ⭐
│       ├── roleplay_ml_pca_entity_scores_latest.pkl  # 778行聚合数据
│       │   # └─ IVS: 109个国家/地区（基准）
│       │   # └─ Multilingual: 669条模仿数据
│       ├── roleplay_ml_pca_results_latest.pkl  # 完整PCA结果
│       └── llm_responses_roleplay_ml/  # 原始访谈数据
│
├── 📁 src/                            # 源代码
│   ├── base/                         # 基础设施（所有Stage共享）
│   │   ├── base_pca_analyzer.py     # PCA分析基类
│   │   ├── base_interview.py        # 访谈基类
│   │   └── ivs_question_processor.py  # 问题处理器
│   │
│   ├── country_values/               # Stage0: 真实数据处理
│   │   └── country_pca_analysis.py
│   │
│   ├── llm_values/                   # Stage1: LLM原生分析
│   │   ├── llm_interview.py
│   │   └── llm_pca_analysis.py
│   │
│   ├── roleplay_English/             # Stage2: 英语角色扮演（已废弃）
│   │
│   ├── roleplay_multilingual/        # Stage3: 多语言角色扮演 ⭐
│   │   ├── multilingual_roleplay_interview.py  # 多语言访谈
│   │   ├── multilingual_roleplay_pca_analysis.py  # PCA分析
│   │   └── multilingual_roleplay_visualization.py  # 可视化
│   │
│   └── run/                          # 运行脚本
│       ├── run_country_values_analysis.py  # Stage0运行器
│       ├── run_llm_values_analysis.py      # Stage1运行器
│       ├── run_roleplay_english_analysis.py  # Stage2运行器（暂停）
│       └── run_roleplay_multilingual_analysis.py  # Stage3运行器
│
├── 📁 analysis/                       # 跨Stage分析脚本 ⭐
│   ├── README.md                     # 分析脚本说明
│   ├── stage0_vs_stage3_distance.py  # 核心：距离和英语优势
│   ├── stage1_vs_stage3_distribution.py  # 模型灵活性分析
│   └── visualize_orientalism.py      # 东方主义理论验证
│
├── 📁 results/                        # 分析结果
│   ├── analysis/                     # 跨Stage分析结果 ⭐
│   │   ├── stage0_vs_stage3/        # Stage0 vs Stage3对比
│   │   │   ├── distances_detailed.xlsx
│   │   │   ├── english_advantage_average.xlsx
│   │   │   ├── english_native_baseline.xlsx  # 英语母语国家/地区基准
│   │   │   └── *.png                # 可视化图表
│   │   │
│   │   ├── stage1_vs_stage3/        # Stage1 vs Stage3对比
│   │   │   ├── distribution_analysis.xlsx
│   │   │   ├── model_concentration.csv
│   │   │   └── *.png
│   │   │
│   │   └── orientalism_analysis/    # 东方主义理论验证
│   │       └── *.png
│   │
│   ├── country_values/               # Stage0结果
│   ├── llm_values/                   # Stage1结果
│   └── roleplay_multilingual/        # Stage3结果
│
├── 📁 config/                         # 配置文件
│   ├── multilingual_questions_complete.json  # 完整问题配置
│   └── country_language_mapping.json  # 国家/地区-语言映射
│
├── 📁 汇报md/                         # 汇报文档
│   └── 11_18_10模型_日韩/
│       ├── Stage3_一页纸汇报_十模型日韩.md
│       └── Stage3_十模型_日韩_详细分析报告.md
│
└── 📁 slides/                         # 演示文稿
    └── stage3/
        └── 11_19.html
```

---

## 🚀 快速开始

### 1. 查看核心分析结果

```bash
# Stage0 vs Stage3: 距离和英语优势分析
cd results/analysis/stage0_vs_stage3/
start english_advantage_average.xlsx
start english_native_baseline.xlsx

# Stage1 vs Stage3: 模型灵活性分析
cd results/analysis/stage1_vs_stage3/
start distribution_analysis.xlsx
```

### 2. 运行分析脚本

```bash
# 核心分析：Stage0 vs Stage3
python analysis/stage0_vs_stage3_distance.py

# 模型灵活性分析：Stage1 vs Stage3
python analysis/stage1_vs_stage3_distribution.py

# 东方主义理论验证
python analysis/visualize_orientalism.py
```

### 3. 重新生成Stage3数据（如果需要）

```bash
# 运行Stage3完整流程
python src/run/run_roleplay_multilingual_analysis.py
```

### 4. 查看汇报材料

```bash
# 主汇报（一页纸）
cat "汇报md/11_18_10模型_日韩/Stage3_一页纸汇报_十模型日韩.md"

# 打开slides
start slides/stage3/11_19.html
```

---

## 📚 核心文档

### 分析脚本说明
- [Analysis README](analysis/README.md) - 所有跨Stage分析脚本的完整说明
- [Base模块README](src/base/README.md) - 基础设施说明

### Stage文档
- **Stage0**: [Country Values README](src/country_values/README.md)
- **Stage1**: [LLM Values README](src/llm_values/README.md)
- **Stage3**: [Roleplay Multilingual README](src/roleplay_multilingual/README.md)

### 汇报材料
- [Stage3一页纸汇报](汇报md/11_18_10模型_日韩/Stage3_一页纸汇报_十模型日韩.md)
- [详细分析报告](汇报md/11_18_10模型_日韩/Stage3_十模型_日韩_详细分析报告.md)

### Slides
- [最新演示文稿](slides/stage3/11_19.html)

---

## 🔧 技术栈

- **Python 3.8+**
- **核心库**：pandas, numpy, scikit-learn, matplotlib, seaborn
- **API**：OpenAI, Anthropic, Google, DeepSeek, etc.
- **数据源**：World Values Survey (WVS)

---

## ⚠️ 重要说明

### 关于距离计算

1. **正确方法**（当前使用）：
   - 从真实WVS坐标计算距离
   - 位置：`results/distance_analysis_correct/`
   - 脚本：`scripts/data_analysis/calculate_correct_distances.py`

2. **错误方法**（已废弃）：
   - 从原点(0,0)计算距离
   - 位置：`results/distance_analysis/`（标记为DEPRECATED）
   - 不要使用这些结果！

### 关于坐标系统

- 使用 **rescaled坐标**（与WVS标准对齐）
- PC1_rescaled = 1.81 × PC1 + 0.38
- PC2_rescaled = 1.61 × PC2 - 0.01

---

## 📝 引用

如果你使用了本项目的代码或数据，请引用：

```bibtex
@misc{llm_cultural_values_2025,
  title={Cross-lingual Cultural Value Expression in Large Language Models},
  author={Your Name},
  year={2025},
  url={https://github.com/matrix0394/LLM-s-values}
}
```

---

## 📧 联系方式

- **GitHub**: [@matrix0394](https://github.com/matrix0394)
- **项目主页**: [LLM's values](https://github.com/matrix0394/LLM-s-values)

---

## 📅 更新日志

### 2025-11-22 (Phase 1 完成) ⭐
- ✅ **修复Stage3 PCA数据聚合**：正确保存778行实体数据（109国家/地区 + 669模仿数据）
- ✅ **添加英语母语国家/地区基准**：美英澳新加基准距离3.26 vs 所有英语模仿2.12
- ✅ **修正政治敏感性**：所有港台澳表述改为"国家/地区"或"地区"
- ✅ **重构分析代码**：
  - 删除重复脚本（`calculate_distances.py`, `generate_alignment_report.py`）
  - 跳过Stage2（数据兼容性问题）
  - 重命名`stage1_vs_stage23_distribution.py` → `stage1_vs_stage3_distribution.py`
  - 最终保留3个核心分析脚本
- ✅ **完善分析功能**：
  - 所有脚本使用完整模型名称（不简化）
  - 过滤Stage1数据中的IVS真实国家数据
  - 修复坐标使用（`PC1_rescaled`, `PC2_rescaled`）
- ✅ **更新项目文档**：全面更新README，涵盖Stage0-3完整结构

### 2025-11-18
- ✅ 添加日本和韩国数据
- ✅ 扩展到10个模型
- ✅ 完成东亚完整梯度分析

### 2025-10-20
- ✅ 完成Stage3多语言对比实验
- ✅ 发现"英语悖论"现象
- ✅ 提出"数据驱动东方学"理论

---

## 📊 项目状态

| 阶段 | 状态 | 说明 |
|------|------|------|
| **Stage0** | ✅ 完成 | 109个国家/地区真实文化坐标 |
| **Stage1** | ✅ 完成 | 10个LLM原生文化倾向 |
| **Stage2** | ⏸️ 暂停 | 数据兼容性问题 |
| **Stage3** | ✅ 完成 | 10模型×34国家/地区×10语言 |
| **跨Stage分析** | ✅ 完成 | 3个核心分析脚本 |
| **论文撰写** | 🚧 进行中 | - |

---

**最后更新**: 2025-11-22  
**项目状态**: Phase 1 完成，数据分析完成，论文撰写中  
**下一步**: Phase 2 - 扩展更多模型和语言
