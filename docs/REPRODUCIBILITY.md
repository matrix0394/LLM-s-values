# Reproducibility

本文件说明 `llm_values_2026_06` GitHub 交接包能直接复现什么，以及哪些全量数据需要另取。

## 环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 直接可跑

```bash
python3 src/run/run_paper_analysis.py --help
python3 src/run/run_paper_analysis.py
python3 src/run/run_paper_analysis.py --regression-only
python3 external_runners/hk_local_hf_interview_upload.py --help
```

主分析从包内轻量 PCA 坐标和 entity_scores 读取数据，输出到 `results/analysis/` 和 `results/paper_data/`。

正式 Study 2 应显示：20 models、920 observations、Overall English Advantage +3.6%。

## 包内数据

- `data/country_values/country_scores_pca.json`
- `data/country_values/country_scores_pca.pkl`
- `data/country_values/pca_model_fixed.pkl`
- `data/llm_pca/intrinsic/llm_pca_entity_scores.pkl/json`
- `data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.pkl/csv/json`
- `data/external/` 回归协变量
- `results/analysis/` Study JSON/CSV/XLSX/TXT
- `results/paper_data/` 论文图表/表格源数据

## 不在 GitHub 包内的数据

WVS 官方原始 `.sav` 不进 GitHub，让师弟官网下载。项目自跑的大 raw/intermediate 数据由你网盘/微信发，清单见 `START_HERE.md`。

## 从 WVS 官方数据重建人类 PCA

下载 `Integrated_values_surveys_1981-2022.sav` 后放到：

```text
data/raw/Integrated_values_surveys_1981-2022.sav
```

运行：

```bash
python3 src/run/run_country_values_analysis.py
```

## 从全量 LLM raw 重建

GitHub 包没有全量 raw interview。需要重做 parser 或 PCA 时，先让你把以下数据另发给师弟：

- `data/llm_interviews/multilingual/interview_raw/`
- `data/llm_interviews/intrinsic/interview_raw/`
- 需要深度 debug 时再发两个完整 PCA 中间对象 `llm_pca_results.pkl` 和 `roleplay_ml_pca_results_latest.pkl`

然后按固定链条处理：raw answer -> adjudication/解析 -> `pca_model_fixed.pkl` 投影 -> `run_paper_analysis.py` 统计。
