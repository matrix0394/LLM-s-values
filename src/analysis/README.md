# 分析脚本目录

## 目录结构

```
src/analysis/
├── comparative/          # 法语 vs 阿拉伯语比较分析
│   ├── analyze_french_vs_arabic.py
│   ├── analyze_french_supplementary.py
│   └── merge_and_clean_roleplay_data.py
│
├── figure_data/          # 生成图表输入数据
│   ├── generate_figure1_data.py
│   ├── generate_figure2_*.py
│   ├── generate_figure3_*.py
│   ├── generate_figure4_*.py
│   └── merge_and_pca_analysis.py
│
├── plotting/             # 绘图脚本
│   ├── plot_figure1_choropleth.py
│   ├── plot_figure2_*.py
│   ├── plot_figures.py
│   └── plot_figures_maps.py
│
├── reproduction/         # 复现脚本（验证论文结果）
│   ├── reproduce_english_advantage.py  # 英语优势复现
│   └── reproduce_full_pipeline.py       # 完整流程复现
│
├── (保留)                # 原 stage1/stage3 分析
│   ├── analyze_stage1_models.py
│   ├── analyze_stage3_roleplay.py
│   ├── compare_stage1_stage3_real_countries.py
│   └── complete_stage3_analysis.py
```

## 数据生成链

### 英语优势复现

```
输入:
  - SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv
  - data/country_values/country_scores_pca.json

脚本:
  - src/analysis/reproduction/reproduce_english_advantage.py

输出:
  - results/metrics/english_advantage_reproduced.csv
```

### 完整数据流程

见: `docs/data_flow_traceability.md`

## 运行示例

```bash
# 复现英语优势分析
python3 src/analysis/reproduction/reproduce_english_advantage.py
```
