# The Value Atlas of AI: Mapping World Human Values in Large Language Models

## 项目概述

本项目系统性研究**语言对大语言模型文化价值表达的影响**。通过让 20 个 LLM 用不同语言模仿 66 个国家/地区的文化背景回答 WVS 价值观问题，发现了普遍的英语优势现象和数字东方主义效应。

### 核心发现

- **Study 1**: LLM 内在价值观存在显著的世俗-理性偏差，阿拉伯语与英语差异最大
- **Study 2**: 46 个非英语国家中，英语角色扮演普遍比母语更接近真实文化坐标（EA = +4.6%）
- **Study 3**: 非西方国家英语优势显著高于西方国家（数字东方主义），文化距离与英语优势正相关
- **Study 4**: 殖民历史塑造了 LLM 的文化表征模式

### 实验规模

- **20 个模型**: GPT-4o/4o-mini/5.1, Claude 3.7/4.5, Gemini 2.5/3, DeepSeek v3/v3.1, Llama 3.2/3.3, Mistral Medium/Nemo, Phi-3, Gemma-3, Doubao, Kimi-K2, Qwen3-Max, Grok-4.1
- **66 个国家/地区**: 20 英语母语 + 46 非英语
- **6 种核心语言**: English, Arabic, Chinese, French, Russian, Spanish

---

## 快速开始

### 运行论文分析流程

```bash
# 完整分析（Study 1-4 + 回归数据）
python3 src/run/run_paper_analysis.py

# 从原始访谈数据重建 PCA 后再分析
python3 src/run/run_paper_analysis.py --rebuild-from-raw

# 只运行特定 Study
python3 src/run/run_paper_analysis.py --study 1 2

# 生成论文图表数据
python3 src/analysis/figure_data/regenerate_paper_data.py
```

### 查看论文数据

论文所有图表和统计数据位于 `results/paper_data/`，详见 [Paper Data README](results/paper_data/README.md)。

---

## 核心目录结构

```
LLM's values/
│
├── src/                                    # 源代码
│   ├── base/                              # 共享基础模块
│   │   ├── base_pca_analyzer.py          #   PCA 分析基类
│   │   ├── base_interview.py             #   访谈基类
│   │   ├── ivs_question_processor.py     #   WVS 问题处理器
│   │   └── ppca.py                       #   概率 PCA 实现
│   │
│   ├── country_values/                    # Stage 0: 真实国家 WVS 数据处理
│   ├── llm_values/                        # Stage 1: LLM 内在价值观（baseline）
│   ├── roleplay_multilingual/             # Stage 3: 多语言角色扮演
│   │   ├── multilingual_roleplay_interview.py
│   │   ├── multilingual_roleplay_data_processor.py
│   │   └── multilingual_roleplay_pca_analysis.py
│   │
│   ├── analysis/                          # 分析模块
│   │   ├── figure_data/                  #   论文图表数据生成
│   │   │   └── regenerate_paper_data.py  #     生成 Figure 1-4 数据
│   │   ├── distance/                     #   文化距离与英语优势计算
│   │   ├── comparative/                  #   法语优势等对比分析
│   │   └── plotting/                     #   绘图脚本
│   │
│   └── run/                               # 运行入口
│       ├── run_paper_analysis.py          #   论文主分析流程（Study 1-4）
│       ├── run_country_values_analysis.py #   Stage 0
│       ├── run_llm_values_analysis.py     #   Stage 1
│       └── run_roleplay_multilingual_analysis.py  # Stage 3
│
├── data/                                   # 数据存储
│   ├── country_values/                    # WVS 真实坐标
│   │   ├── country_scores_pca.json       #   109 个国家 PCA 坐标
│   │   └── pca_model_fixed.pkl           #   固定 PCA 模型
│   ├── llm_pca/                           # LLM PCA 坐标
│   │   ├── intrinsic/                    #   Stage 1 内在坐标
│   │   └── multilingual/                 #   Stage 3 角色扮演坐标
│   └── llm_interviews/                    # 原始访谈 JSON
│       └── multilingual/interview_raw/
│
├── results/                                # 分析结果
│   ├── paper_data/                        # 论文图表数据（核心输出）
│   │   ├── figure1_data_66countries.csv  #   Fig.1: 地图热力图数据
│   │   ├── figure2_baseline_20models.csv #   Fig.2: 6 语言 baseline
│   │   ├── figure3_digital_orientalism.csv  # Fig.3: 东方主义 distance
│   │   ├── figure4_colonial_history.csv  #   Fig.4: 殖民遗产 distance
│   │   ├── regression_data.csv           #   回归分析数据
│   │   ├── french_advantage_12_countries.csv  # 法语优势数据
│   │   └── study[1-4]_*.json             #   各 Study 统计结果
│   ├── analysis/                          # 中间分析结果
│   └── figures/                           # 历史图表文件
│
├── SI/                                     # Supplementary Information
│   └── pca/                               # PCA 坐标表
│       ├── Table_S5_IVS_PCA_coordinates.csv
│       ├── Table_S6_LLM_baseline_PCA_coordinates.csv
│       ├── Table_S7_LLM_roleplay_PCA_coordinates.csv
│       └── Table_S8_PCA_component_summary.csv
│
├── config/                                 # 配置文件
│   ├── country/                           # 国家代码与语言映射
│   ├── models/                            # 模型配置
│   └── questions/                         # WVS 问题配置
│
└── .env                                    # API keys
```

---

## 论文图表说明

### Figure 1: 文化价值观世界地图（4 张热力图）

左侧：LLM 英语角色扮演 PC1 热力图 + WVS PC1 热力图对照
右侧：LLM 英语角色扮演 PC2 热力图 + WVS PC2 热力图对照

数据：`results/paper_data/figure1_data_66countries.csv`

### Figure 2: LLM 内在价值观（6 种语言 × 20 模型）

展示 20 个模型在 6 种语言下的 baseline PCA 坐标分布。

数据：`results/paper_data/figure2_baseline_20models.csv`

### Figure 3: 数字东方主义（distance 地图）

中东 + 东亚地区的英语优势 distance 地图。

数据：`results/paper_data/figure3_digital_orientalism.csv`

### Figure 4: 殖民遗产（distance 地图）

撒哈拉以南非洲（8 国）+ 拉丁美洲（13 国）+ 儒家（6 国）的 distance 地图。

数据：`results/paper_data/figure4_colonial_history.csv`

---

## 技术栈

- **Python 3.10+**
- **核心库**: pandas, numpy, scipy, scikit-learn
- **PCA**: 概率 PCA (PPCA) + 固定旋转矩阵
- **LLM API**: OpenAI, Anthropic, Google, DeepSeek, Mistral, etc.
- **数据源**: World Values Survey / Integrated Values Survey (WVS/IVS)

---

## 距离计算方法

```
distance = √((LLM_PC1 - WVS_PC1)² + (LLM_PC2 - WVS_PC2)²)
English Advantage = (d_native - d_english) / d_native × 100%
```

- **正值**: 英语角色扮演比母语更接近真实文化坐标（英语优势）
- **负值**: 母语角色扮演更接近真实文化坐标（母语优势）
