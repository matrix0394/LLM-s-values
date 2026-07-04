# 结果目录

## 目录结构

```
results/
├── paper_data/                   # 论文核心数据（regenerate_paper_data.py 生成）
│   ├── figure1_data_*countries.csv
│   ├── figure2_baseline_20models.csv
│   ├── figure2_language_summary.csv
│   ├── figure3_digital_orientalism.csv
│   ├── figure4_colonial_history.csv
│   ├── regression_data.csv
│   └── french_advantage_12_countries.csv
│
├── analysis/                     # 分析中间结果（run_paper_analysis.py 及 analysis/ 脚本生成）
│   ├── study1_intrinsic_bias.json      # Study 1 统计
│   ├── study2_english_advantage.json   # Study 2 统计
│   ├── study3_digital_orientalism.json # Study 3 统计
│   ├── study4_colonial_legacies.json   # Study 4 统计
│   ├── paper_statistics_all.json
│   ├── regression_data_v5.csv
│   ├── stage0_vs_stage3/        # 距离与英语优势详细数据
│   ├── colonial_history/        # 殖民分析图表与摘要
│   ├── orientalism_analysis/    # 东方主义分析图表
│   └── visualization/           # PPT 方法论图表
│
├── figures/                      # 生成的图片
│   └── paper/                    # 正文图表
│       └── Fig2_baseline_intrinsic_values.{png,pdf}
│
└── country_values/               # IVS 国家价值观可视化
```

## 使用说明

### 论文数据 (paper_data/)

由 `src/analysis/figure_data/regenerate_paper_data.py` 生成，供正文 Figure 1–4 及回归分析使用。

### 分析结果 (analysis/)

- **study1–4_*.json**：`src/run/run_paper_analysis.py` 的主输出
- **stage0_vs_stage3/**：`analysis/core/stage0_vs_stage3_distance.py` 生成，殖民/东方主义脚本依赖
- 各子目录用途详见 `results/analysis/README.md`

### 图表 (figures/)

正文 Figure 2 由 `analysis/figures/generate_fig2_baseline.py` 生成。SI 图表输出到 `SI/figures/`。
