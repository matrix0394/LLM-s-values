# 分析脚本目录

本目录包含数据分析与图表生成脚本，按功能分类组织。

## 目录结构

```
analysis/
├── core/           # 核心 Stage 对比分析
├── language/       # 语言/殖民分析（Study 4 等）
├── model/          # 模型相关分析
├── figures/        # 正文图表（Figure 2）
├── si/             # SI 附录图表（Fig S1-S7）
├── baseline/       # 基线语言效应
├── utils/          # 工具脚本
└── README.md
```

---

## core/ — 核心 Stage 对比分析

| 脚本 | 功能 |
|------|------|
| `stage0_vs_stage3_distance.py` | **主分析**：WVS vs 多语言角色扮演，英语优势、距离计算 |
| `stage0_vs_stage2_distance.py` | Stage0 vs Stage2（英语角色扮演）|

输出：`results/analysis/stage0_vs_stage3/`

---

## language/ — 语言/殖民分析

| 脚本 | 功能 |
|------|------|
| `analyze_colonial_history_v4.py` | **Study 4**：殖民遗产（港澳、拉美、非洲） |
| `colonial_utils.py` | 殖民分析工具（距离、英语优势） |
| `colonial_visualizations.py` | 殖民分析可视化 |
| `analyze_orientalism_effect.py` | 东方主义/语言他者化效应 |

详见 `language/README_colonial_history.md`。

---

## model/ — 模型分析

| 脚本 | 功能 |
|------|------|
| `analyze_cultural_distance.py` | 文化距离计算，输出 `cultural_distance_analysis.csv` |
| `analyze_by_model_quality.py` | 按模型质量分层分析 |

---

## figures/ — 正文图表

| 脚本 | 功能 |
|------|------|
| `generate_fig2_baseline.py` | **正文 Figure 2**：20 模型 × 6 语言 baseline 文化地图 |

输出：`results/figures/paper/Fig2_baseline_intrinsic_values.{png,pdf}`

---

## si/ — SI 附录图表

生成论文 Supplementary Information 图表（Fig S1–S7）。所有脚本共享 `si_config.py`。

| 脚本 | 输出 |
|------|------|
| `generate_figs1_cultural_map.py` | S1 文化地图 |
| `generate_figs2_baseline.py` | S2 基线内在价值观 |
| `generate_figs3_b1b2.py` ~ `b5.py` | S3 各子图 |
| `generate_figs4_model_response.py` | S4 模型响应分析 |
| `generate_figs5_orientalism.py` | S5 东方主义 |
| `generate_figs6_east_asia.py` | S6 东亚分析 |
| `generate_figs7_colonial_history.py` | S7 殖民历史 |
| `generate_figs_summary.py` | 汇总生成 |

详见 `si/README.md`。

---

## baseline/ — 基线分析

| 脚本 | 功能 |
|------|------|
| `analyze_language_effect_on_baseline.py` | 语言对 LLM 基线内在价值观的影响 |

---

## utils/ — 工具脚本

| 脚本 | 功能 |
|------|------|
| `quick_analyze_results.py` | 快速汇总 cultural_distance_analysis |
| `calc_region_stats.py` | 区域英语优势统计 |
| `supplementary_analysis.py` | 补充分析（混合效应等） |

---

## 输出目录

| 目录 | 内容 |
|------|------|
| `results/analysis/stage0_vs_stage3/` | 主分析结果 |
| `results/analysis/colonial_history/` | Study 4 殖民分析图表 |
| `results/analysis/orientalism_analysis/` | 东方主义图表 |
| `results/analysis/visualization/` | PPT 方法论图表 |
| `results/figures/paper/` | 正文 Figure 2 |
| `SI/figures/` | SI 附录图表 |
