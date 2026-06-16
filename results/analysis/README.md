# results/analysis/ — 分析结果

本目录存放论文四个 Study 的统计输出以及中间分析结果。

## 核心论文输出（`run_paper_analysis.py` 生成）

| 文件 | 说明 |
|------|------|
| `study1_intrinsic_bias.json` | Study 1：LLM 固有世俗理性偏差（20 模型 × 6 语言，ANOVA） |
| `study2_english_advantage.json` | Study 2：英语优势（国家级配对 t 检验，EA ~4.6%） |
| `study3_digital_orientalism.json` | Study 3：数字东方主义（区域 EA 均值，语言家族效应） |
| `study4_colonial_legacies.json` | Study 4：殖民遗产与语言效应（儒家梯度、非洲英法对比） |
| `paper_statistics_all.json` | 合并四个 Study 的统计结果 |
| `regression_data_v5.csv` | 回归数据（1041 行：模型 × 国家，含距离、HDI、GDP、殖民变量） |

## 中间分析结果

### `stage0_vs_stage3/`

由 `analysis/core/stage0_vs_stage3_distance.py` 生成。殖民分析和东方主义脚本依赖其中部分文件。

| 文件 | 说明 | 被谁使用 |
|------|------|----------|
| `english_advantage_average.csv` | 国家级英语优势均值 | `colonial_utils.py` |
| `english_advantage_by_model.csv` | 模型级英语优势 | `colonial_utils.py` |
| `distances_detailed.csv` | 逐国逐模型距离 | 东亚轨迹分析 |
| 其他 CSV / PNG | 探索性分析输出 | — |

### `colonial_history/`

由 `analysis/language/analyze_colonial_history_v4.py` 生成。

| 文件 | 说明 |
|------|------|
| `summary_statistics.txt` | Study 4 殖民分析统计摘要 |
| `*.png` | 东亚梯度、港澳对比、拉美变体图 |

### `orientalism_analysis/`

由 `analysis/figures/visualize_orientalism.py` 和东亚轨迹脚本生成。

| 文件 | 说明 |
|------|------|
| `*.png` | 东方主义/区域语言效应可视化（12 张） |

### `visualization/`

由 `analysis/visualization/` 脚本生成的 PPT 方法论图表。

| 文件 | 说明 |
|------|------|
| `*.png` | 研究框架、数据流程、PPCA、指标图等（9 张） |

## 待清理的旧文件

| 文件 | 说明 | 建议 |
|------|------|------|
| `cultural_distance_all.csv` / `.json` | 旧版距离数据（已被 study2 JSON 替代） | 可删除 |
| `arabic_french_all_records.csv` | 旧版阿拉伯-法语分析 | 可删除 |
| `study1_llm_values/` | 旧版 Study 1（已被 `study1_intrinsic_bias.json` 替代） | 可删除 |
