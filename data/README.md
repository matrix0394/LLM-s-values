# 数据目录

## 目录结构

```
data/
├── country_values/               # IVS 国家价值观基准数据
│   ├── pca_model_fixed.pkl       # ★ 核心 PCA 模型（固定）
│   ├── country_scores_pca.json   # IVS 国家 PCA 坐标
│   ├── country_scores_pca.pkl    # 同上（pkl 格式）
│   ├── Table_S5_IVS_PCA_coordinates.csv  # IVS 坐标（供 SI 与图表脚本使用）
│   ├── ivs_df.pkl                # IVS 原始数据
│   └── valid_data.pkl             # 有效国家列表
│
├── external/                     # 回归分析外部数据
│   ├── regression_covariates.csv # 上游协变量表（HDI、GDP、殖民史等）
│   ├── country_list_for_regression.csv
│   ├── external_colonial_history.csv
│   ├── external_ef_epi.csv       # EF EPI 英语能力指数
│   ├── HDR25_Statistical_Annex_HDI_Table.xlsx  # HDI
│   ├── Internet_Inclusivity_Index/            # 互联网包容性指数
│   └── world_bank_gdp/           # 世界银行 GDP per capita
│
├── llm_interviews/               # LLM 访谈原始数据
│   ├── intrinsic/                # Stage 1 内在价值观（6 语言 × 20 模型）
│   │   └── interview_raw/        # 原始 API 返回 JSON
│   └── multilingual/             # Stage 3 多语言角色扮演
│       ├── interview_raw/        # 原始 API 返回
│       └── processed/            # 处理后的 IVS 格式（*_latest.*）
│
└── llm_pca/                     # LLM PCA 投影结果
    ├── intrinsic/                # Stage 1 内在坐标（baseline）
    │   ├── Table_S6_LLM_baseline_PCA_coordinates.csv
    │   ├── llm_pca_entity_scores.json
    │   └── llm_pca_results.pkl   # PCA 模型
    └── multilingual/             # Stage 3 角色扮演坐标
        ├── Table_S7_LLM_roleplay_PCA_coordinates.csv
        ├── roleplay_ml_pca_entity_scores_latest.json
        └── roleplay_ml_pca_results_latest.pkl
```

## 关键文件说明

### 1. pca_model_fixed.pkl
**位置**: `data/country_values/pca_model_fixed.pkl`

整个分析使用的**固定 PCA 模型**，包含 PPCA 载荷、Varimax 旋转与重缩放参数。所有 LLM 数据均通过此模型投影到 IVS 同一坐标空间。

### 2. llm_pca/intrinsic/Table_S6_*.csv
Stage 1 内在价值观的 PCA 坐标，对应「不进行角色扮演」时的模型表达。分析脚本（如 `si_config.py`）优先从 `data/llm_pca/` 读取，缺失时回退到 `SI/pca/`。

### 3. llm_pca/multilingual/Table_S7_*.csv
Stage 3 多语言角色扮演的 PCA 坐标，用于计算英语优势与文化距离。

### 4. external/
回归分析所需的外部数据。`run_paper_analysis.py` 依赖
`data/external/regression_covariates.csv` 中的 HDI、GDP、殖民史等变量，
并据此生成论文主表 `results/paper_data/regression_data.csv`。

## 数据流程

```
原始访谈 (llm_interviews/*/interview_raw)
    ↓ 处理
IVS 格式 (llm_interviews/*/processed 或 intrinsic)
    ↓ PCA 投影（pca_model_fixed.pkl）
PCA 坐标 (llm_pca/intrinsic, llm_pca/multilingual)
    ↓ 距离计算
Study 1-4 统计 (results/analysis/study*.json)
```

详见: `docs/data_flow_traceability.md`
