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

论文图表和统计数据位于 `results/paper_data/`；中间分析结果与 Study 1-4 JSON 位于 `results/analysis/`，详见 [results/README.md](results/README.md)。

---

## 核心目录结构

```
LLM's values/
│
├── src/                                    # 源代码
│   ├── base/                              # 共享基础模块（PCA、访谈、IVS 处理器）
│   ├── country_values/                    # Stage 0: WVS 真实国家数据处理
│   ├── llm_values/                        # Stage 1: LLM 内在价值观（baseline）
│   ├── roleplay_multilingual/             # Stage 3: 多语言角色扮演
│   │
│   ├── analysis/                          # 分析模块
│   │   ├── figure_data/                  #   论文图表数据生成
│   │   │   └── regenerate_paper_data.py  #     生成 Figure 1-4 数据
│   │   ├── distance/                     #   文化距离与英语优势计算
│   │   └── comparative/                  #   数据清洗与对比分析
│   │
│   └── run/                               # 运行入口
│       ├── run_paper_analysis.py          #   论文主分析（Study 1-4 + 回归）
│       ├── run_country_values_analysis.py #   Stage 0
│       ├── run_llm_values_analysis.py     #   Stage 1 英语单语版
│       ├── run_llm_multilingual_analysis.py # Stage 1 多语言版
│       └── run_roleplay_multilingual_analysis.py  # Stage 3
│
├── analysis/                               # 分析脚本（与 src 并行）
│   ├── si/                               # SI 附录图表生成
│   ├── core/                             # 核心距离分析（stage0 vs stage3）
│   ├── figures/                          # 正文图表
│   │   └── generate_fig2_baseline.py     #   正文 Figure 2
│   ├── language/                         # 殖民历史、东方主义分析
│   ├── baseline/                         # 基线语言效应
│   ├── model/                            # 模型分析
│   └── utils/                            # 工具脚本
│
├── data/                                   # 数据
│   ├── country_values/                    # WVS 基准（country_scores_pca.json, pca_model_fixed.pkl）
│   │   └── Table_S5_IVS_PCA_coordinates.csv  # IVS 坐标（SI 副本）
│   ├── external/                          # 回归用外部数据（GDP、HDI、殖民历史等）
│   │   ├── regression_covariates.csv     # 上游协变量表
│   │   └── ...
│   ├── llm_pca/                           # LLM PCA 坐标（项目生成）
│   │   ├── intrinsic/                    #   Table_S6 基线坐标
│   │   └── multilingual/                 #   Table_S7 角色扮演坐标
│   └── llm_interviews/                    # 原始访谈 JSON
│       ├── intrinsic/interview_raw/      #   Stage 1
│       └── multilingual/interview_raw/   #   Stage 3
│
├── results/                                # 分析结果
│   ├── paper_data/                        # 论文图表数据（Figure 1-4、regression_data）
│   ├── analysis/                          # Study 1-4 JSON、中间分析、图表
│   ├── figures/paper/                     # 正文图表输出（如 Fig2）
│   └── country_values/                    # Stage 0 可视化结果
│
├── SI/                                     # Supplementary Information（论文附录）
│   ├── pca/                               # Table S5-S8 坐标表（由 data 生成后复制）
│   ├── figures/                           # SI 图表输出
│   └── prompts/                           # 提示词、问题配置
│
├── config/                                 # 配置（国家、模型、问题）
├── docs/                                   # 文档、论文草稿
├── slides/                                 # 汇报 PPT
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

---

## 回归分析外部数据

回归分析（`run_paper_analysis.py`）所需的外部数据统一存放在 `data/external/`：

| 文件/目录 | 说明 |
|-----------|------|
| `regression_covariates.csv` | 上游协变量表（国家 × HDI、GDP、殖民变量等） |
| `country_list_for_regression.csv` | 回归国家列表 |
| `external_ef_epi.csv` | EF EPI 英语能力指数 |
| `HDR25_Statistical_Annex_HDI_Table.xlsx` | HDI 人类发展指数 |
| `external_colonial_history.csv` | 殖民历史数据 |
| `world_bank_gdp/` | 世界银行人均 GDP |
| `Internet_Inclusivity_Index/` | 互联网包容性指数 |

---

## 回归用到的外部数据

回归分析所需外部数据统一存放在 `data/external/`：

| 文件/目录 | 说明 |
|-----------|------|
| `regression_covariates.csv` | 国家元数据（HDI、GDP、殖民历史等） |
| `external_ef_epi.csv` | EF EPI 英语能力指数 |
| `external_colonial_history.csv` | 殖民历史 |
| `HDR25_Statistical_Annex_HDI_Table.xlsx` | HDI 人类发展指数 |
| `world_bank_gdp/` | 世界银行 GDP per capita |
| `Internet_Inclusivity_Index/` | 互联网包容性指数 |
