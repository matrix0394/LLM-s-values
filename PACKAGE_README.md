# llm_values_2026_06 Package

这是已经裁好的交接项目包。它不是原始工作区镜像，也不是整理建议；它就是准备放到 GitHub 分支 `codex/llm_values_2026_06` 的轻量可运行版本。

## 保留内容

- `src/`：固定 runner 和核心模块，包含论文主分析、WVS PCA、LLM baseline、多语言 roleplay、距离分析等代码。
- `config/`：国家、模型、题目 JSON 配置。已移走生成 Word/PDF/HTML/TEX 题目文档的临时脚本和输出。
- `external_runners/hk_local_hf_interview_upload.py`：后续 BLOOM/PolyLM、本地 HF、Colab/AutoDL 访谈入口。
- `data/country_values/`：`country_scores_pca.json`、`pca_model_fixed.pkl` 等轻量核心文件。
- `data/llm_pca/`：主分析所需 LLM PCA 坐标和 entity_scores，不含完整 PCA 中间对象。
- `data/external/`：回归协变量。
- `data/llm_interviews/`：只保留 BLOOM/PolyLM 香港旧 pilot 的少量 raw 记录。
- `results/analysis/`：Study JSON、CSV/XLSX/TXT 统计结果，不含 PNG/PPT。
- `results/paper_data/`：论文图表和表格源数据 CSV。
- `docs/`：交接和复现说明。

## 已移走内容

移走的位置：

```text
/private/tmp/llm_values_2026_06_removed_not_for_github_20260617/
```

移走类型：

- 根目录旧 `analysis/` 脚本堆和旧 pilot PPT。
- `Supplementary Materials/` 和 `dryad/`，包括其中误带的嵌套 `.git`。
- 旧图表、PNG、PPT、PDF、DOCX、HTML、TEX。
- Python backup 文件。
- `data/llm_pca/intrinsic/llm_pca_results.pkl` 和 `data/llm_pca/multilingual/roleplay_ml_pca_results_latest.pkl`。

## 验证命令

```bash
python3 src/run/run_paper_analysis.py --help
python3 src/run/run_paper_analysis.py --study 2
python3 external_runners/hk_local_hf_interview_upload.py --help
```

Study 2 正式口径：20 models、920 observations、Overall English Advantage +3.6%。

## 另发数据

需要时通过网盘/微信发给师弟：

```text
data/country_values/ivs_df.pkl                                      约 4.2G
data/country_values/valid_data.pkl                                  约 31M
data/llm_interviews/multilingual/interview_raw/                      约 176M
data/llm_interviews/intrinsic/interview_raw/                         约 4.5M
data/llm_pca/intrinsic/llm_pca_results.pkl                           约 32M
data/llm_pca/multilingual/roleplay_ml_pca_results_latest.pkl          约 47M
```

WVS/EVS 官方 `Integrated_values_surveys_1981-2022.sav` 让师弟从官网下，不进 GitHub。
