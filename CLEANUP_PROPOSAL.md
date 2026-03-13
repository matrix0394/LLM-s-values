# 项目清理建议（2026-03-13 更新）

> 以下文件/目录可以安全删除。数据已通过 `results/paper_data/` 提供给师兄使用。
> 所有分析结果可通过 `python src/run/run_paper_analysis.py --rebuild-from-raw` 重新生成。

---

## 一、强烈建议删除（过时/重复，共约 1.9 GB）

### 1. `backup/` 整个目录（~1.0 GB）

| 路径 | 说明 | 大小 |
|------|------|------|
| `backup/analysis_backup/` | 17 个旧分析脚本，已有新版本在 `src/analysis/` 和 `analysis/` | ~200KB |
| `backup/data_backup/` | 旧的 LLM 访谈响应数据备份，原始数据仍在 `data/` | ~1.0 GB |
| `backup/scripts_backup/` | 3 个旧脚本，与 `src/analysis/comparative/` 重复 | ~30KB |

### 2. `.backup` 文件（3 个）

| 文件 | 说明 |
|------|------|
| `src/base/base_pca_analyzer.py.backup_20251217` | 旧备份 |
| `src/roleplay_multilingual/multilingual_roleplay_pca_analysis.py.backup_20251217` | 旧备份 |
| `src/run/run_roleplay_multilingual_analysis.py.backup_20251208_153708` | 旧备份 |

### 3. `LLM-Value/` 目录（~563 MB）

外部参考项目的 SI 材料副本。如果只是参考用途，可以删除或替换为 git submodule。

### 4. `SI/` 目录（~309 MB）

Supplementary Information 的图表/数据。如果已合并到论文或 `results/` 中，可删除。
> ⚠️ 如果师兄还需要 SI 原始图片，先确认再删。

### 5. `model_cultural_comp-main/` 目录（~3 MB）

外部参考项目，非核心代码。

### 6. `scripts/` 目录（空）

空文件夹，无内容。

---

## 二、建议删除（旧的中间数据，可重新生成）

### 7. 时间戳中间数据文件

| 路径 | 说明 | 保留 |
|------|------|------|
| `data/llm_pca/multilingual/roleplay_ml_pca_*_2026031*.pkl` | 重建过程中的多个中间 pkl | 只保留 `*_latest.pkl` |
| `data/llm_interviews/multilingual/processed/*_2026031*.{csv,json,pkl}` | 多次重建的中间处理文件 | 只保留 `*_latest.*` |
| `data/llm_interviews/multilingual/processed/multilingual_processed_20251228_*` | 旧版处理结果 | 删除 |
| `data/llm_interviews/multilingual/processed/multilingual_summary_report_*` | 旧版报告 | 删除 |

### 8. `results/figures_data/` 目录

已被 `results/paper_data/` 替代（包含更新后的数据+README）。

### 9. `results/figures/` 目录（~12 MB）

旧的图表文件。如果图表可以重新生成或已过时，可删除。
> ⚠️ 包含 `regression_data_v4.csv` 等被 `run_paper_analysis.py` 引用的文件，检查后再删。

---

## 三、建议删除（重复/旧版脚本）

### 10. `src/analysis/` 下的旧脚本

| 文件 | 说明 |
|------|------|
| `src/analysis/comparative/` | 3 个脚本，与 `backup/scripts_backup/` 重复 |
| `src/analysis/figure_data/` | 7 个旧图表数据生成脚本 |
| `src/analysis/plotting/` | 5 个旧绑图脚本 |
| `src/analysis/reproduction/` | 2 个旧复现脚本 |

> 以上功能已被 `src/run/run_paper_analysis.py` 统一替代。

### 11. `src/run/run_roleplay_multilingual_analysis_clean.py`

与 `run_roleplay_multilingual_analysis.py` 重复。

### 12. `analysis/language/` 旧版本脚本

| 文件 | 说明 |
|------|------|
| `analyze_colonial_history.py` | v1，已有 v4 |
| `analyze_colonial_history_v2.py` | v2，已有 v4 |
| `analyze_colonial_history_v3.py` | v3，已有 v4 |

---

## 四、可以考虑删除（按需保留）

### 13. 旧分析结果目录

| 路径 | 大小 | 说明 |
|------|------|------|
| `results/roleplay_English/` | ~148 MB | 英语角色扮演的旧 dashboard/结果 |
| `results/roleplay_multilingual/` | ~129 MB | 多语言角色扮演的旧 dashboard/结果 |
| `results/llm_values/` | ~31 MB | LLM 价值观的旧 dashboard |
| `results/stage1_analysis/` | ~1.5 MB | Stage 1 旧分析 |
| `results/stage3_analysis/` | ~124 KB | Stage 3 旧分析 |
| `results/regression/` | ~108 KB | 旧回归结果 |
| `results/metrics/` | ~4 KB | 旧指标 |

> 这些旧结果已被 `results/analysis/` 和 `results/paper_data/` 替代。

### 14. 文档

| 路径 | 说明 |
|------|------|
| `docs/汇报md/` | 各次汇报 md，看是否还需要回顾 |
| `docs/论文草稿/优化版/` | 旧版论文优化稿 |
| `docs/论文草稿/第一版/` | 第一版论文草稿 |
| `docs/文件上传md/` | 文件上传说明 |

### 15. 其他

| 路径 | 说明 |
|------|------|
| `logs/` | 旧日志文件 |
| `.hypothesis/` | pytest hypothesis 缓存 |
| `__pycache__/` | Python 缓存（4 处） |
| `slides/` | 汇报 PPT/HTML，看是否还需要 |
| `references/` | 参考文献 PDF，看是否还需要 |
| `CLEANUP_PROPOSAL.md` | 本文件（清理完后删除） |

---

## 五、必须保留

| 路径 | 说明 |
|------|------|
| `src/base/` | 核心基础库 |
| `src/roleplay_multilingual/` | 核心数据处理（不含 .backup） |
| `src/run/run_paper_analysis.py` | 主分析脚本 |
| `src/llm_values/` | LLM 访谈库 |
| `config/` | 配置文件 |
| `data/country_values/` | WVS 基准数据 |
| `data/llm_interviews/multilingual/interview_raw/` | 原始访谈数据（不可删） |
| `data/llm_interviews/multilingual/processed/*_latest.*` | 最新处理结果 |
| `data/llm_interviews/intrinsic/` | Stage 1 数据 |
| `data/llm_pca/` | PCA 结果（只保留 `*_latest.pkl`） |
| `results/analysis/` | 最新分析 JSON/CSV |
| `results/paper_data/` | 给师兄的数据 |
| `results/country_values/` | 国家价值观结果 |
| `docs/论文草稿/导师论文/` | 论文定稿目录 |
| `analysis/` | 分析脚本（大部分仍有用） |
| `.env`, `.gitignore`, `README.md` | 项目配置 |
