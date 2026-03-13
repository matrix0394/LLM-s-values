# 结果目录

## 目录结构

```
results/
├── metrics/                     # 基础指标计算结果
│   └── english_advantage_reproduced.csv
│
├── regression/                  # 回归分析数据
│   └── regression_data.csv
│
├── figures_data/               # 绘图输入数据（论文用）
│   ├── figure1_data_66countries.csv
│   ├── figure3_digital_orientalism.csv
│   ├── figure4_colonial_history.csv
│   └── french_advantage_12_countries.csv
│
├── figures/                    # 生成的图片
│   ├── figures/                # 各种图片
│   └── S2_Baseline_*/
│
├── analysis/                   # 各种分析结果（按主题分类）
│   ├── baseline_language_effect/
│   ├── colonial_history/
│   ├── french_advantage/
│   ├── language_family_analysis/
│   ├── orientalism_analysis/
│   ├── stage0_vs_stage3/
│   └── study1_llm_values/
│
├── country_values/             # IVS分析结果
├── llm_values/                 # LLM价值观结果
├── roleplay_English/           # 英语角色扮演结果（弃用）
├── roleplay_multilingual/      # 多语言角色扮演结果
├── stage1_analysis/           # Stage1分析结果
└── stage3_analysis/           # Stage3分析结果
```

## 使用说明

### 英语优势数据

复现脚本: `src/analysis/reproduction/reproduce_english_advantage.py`

运行后输出到: `results/metrics/english_advantage_reproduced.csv`

### 回归分析数据

输入文件: `results/regression/regression_data.csv`

注意: 此文件的 `english_advantage` 列存在计算问题（分母接近0时产生极端值），需修复后再使用。

### 绘图数据

所有绘图输入数据都在 `results/figures_data/` 目录下，这些是论文最终使用的数据。
