# 数据目录

## 目录结构

```
data/
├── country_values/           # IVS 国家价值观基准数据
│   ├── pca_model_fixed.pkl   # ★ 核心PCA模型（固定）
│   ├── country_scores_pca.json  # IVS国家PCA坐标
│   ├── country_codes.json    # 国家代码映射
│   ├── ivs_df.pkl           # IVS原始数据
│   └── valid_data.json      # 有效国家列表
│
├── llm_interviews/          # LLM访谈数据
│   ├── multilingual/         # 多语言访谈（主数据）
│   │   ├── interview_raw/   # 原始API返回
│   │   │   └── {model}_{language}_{timestamp}.json
│   │   └── processed/      # 处理后的IVS格式
│   │       └── multilingual_*.pkl, multilingual_*.json
│   │
│   └── stage1/              # 早期Stage1数据
│       └── ...
│
└── llm_pca/                # LLM PCA投影结果
    ├── imitation/           # 模仿的 (roleplay)
    │   └── Table_S7_LLM_roleplay_PCA_coordinates.csv
    │
    └── intrinsic/           # 本身价值观 (baseline)
        └── Table_S6_LLM_baseline_PCA_coordinates.csv
```

## 关键文件说明

### 1. pca_model_fixed.pkl
**位置**: `data/country_values/pca_model_fixed.pkl`

这是整个分析的**核心PCA模型**，包含：
- PPCA载荷矩阵
- Varimax旋转矩阵
- 重缩放参数

所有LLM数据都通过此模型投影到与IVS相同的坐标空间。

### 2. llm_pca/imitation/Table_S7_*.csv
**位置**: `data/llm_pca/imitation/Table_S7_LLM_roleplay_PCA_coordinates.csv`

多语言角色扮演访谈的PCA坐标（用于计算英语优势）。

### 3. llm_pca/intrinsic/Table_S6_*.csv
**位置**: `data/llm_pca/intrinsic/Table_S6_LLM_baseline_PCA_coordinates.csv`

大模型本身价值观的PCA坐标（不经过角色扮演）。

## 数据流程

详见: `docs/data_flow_traceability.md`

```
原始访谈 (llm_interviews/multilingual/interview_raw)
    ↓ 处理
IVS格式 (llm_interviews/multilingual/processed)
    ↓ PCA投影
PCA坐标 (llm_pca/imitation/Table_S7_*.csv)
    ↓ 距离计算
英语优势 (results/metrics/english_advantage_reproduced.csv)
```

## 备份数据（不常用）

以下数据已移至 `backup/data_backup/`：

- `roleplay_English/` - 英语角色扮演数据（弃用）
- `roleplay_multilingual/` - 多语言角色扮演原始数据
- `temp_failures/` - API调用失败记录
- `llm_values/` - 旧LLM数据
