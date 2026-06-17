# llm_values_2026_06 交接清单

这份清单对应已经裁好的最终项目包 `/private/tmp/llm_values_2026_06` 和 GitHub 分支 `codex/llm_values_2026_06`。

## 交给师弟的 GitHub 包

仓库：`https://github.com/matrix0394/LLM-s-values.git`  
分支：`codex/llm_values_2026_06`

包内只保留以下内容：

- `src/`：项目固定代码入口和核心模块。
- `config/`：国家、模型、WVS/IVS 题目 JSON 配置。
- `external_runners/hk_local_hf_interview_upload.py`：BLOOM/PolyLM、本地 HF、Colab/AutoDL 后续 runner。
- `data/country_values/`：人类 PCA 坐标和固定 PCA 模型。
- `data/llm_pca/`：主线分析所需 LLM PCA 坐标和 entity_scores。
- `data/external/`：回归协变量。
- `data/llm_interviews/`：BLOOM/PolyLM 香港旧 pilot 小 raw 记录。
- `results/analysis/`：Study JSON、CSV/XLSX/TXT 统计结果。
- `results/paper_data/`：论文图表/表格源数据 CSV。
- `docs/`：复现和数据流说明。

已经移走的内容：旧根目录 `analysis/`、PPT、PNG/PDF/DOCX/HTML/TEX、`Supplementary Materials/`、`dryad/`、backup 文件、完整 PCA 中间对象、嵌套 `.git`。移走备份在 `/private/tmp/llm_values_2026_06_removed_not_for_github_20260617/`。

## 师弟 clone 后先跑

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/run/run_paper_analysis.py --study 2
python3 external_runners/hk_local_hf_interview_upload.py --help
```

Study 2 应为：20 models、920 observations、Overall English Advantage +3.6%。

## 你另发给师弟的数据

通过网盘或微信发。这些不是 GitHub 包必需，但需要完全重建或 debug 时有用。

| 本机路径 | 大小 | 用途 |
|---|---:|---|
| `data/country_values/ivs_df.pkl` | 约 4.2G | WVS .sav 读入后的派生缓存，省去重新解析 SPSS |
| `data/country_values/valid_data.pkl` | 约 31M | 过滤后的 IVS 有效样本缓存 |
| `data/llm_interviews/multilingual/interview_raw/` | 约 176M | 全量多语言角色扮演 API/raw 回答，用于 parser/debug |
| `data/llm_interviews/intrinsic/interview_raw/` | 约 4.5M | baseline raw 回答 |
| `data/llm_pca/intrinsic/llm_pca_results.pkl` | 约 32M | baseline 完整 PCA 中间对象 |
| `data/llm_pca/multilingual/roleplay_ml_pca_results_latest.pkl` | 约 47M | roleplay 完整 PCA 中间对象 |

不用发：`.venv/`、旧 zip、旧 PPT/图表、`Supplementary Materials/`、`dryad/`。

## WVS/EVS 官方数据

`Integrated_values_surveys_1981-2022.sav` 让师弟从 WVS 官方网站下载：`https://www.worldvaluessurvey.org/`。

下载后放到：

```text
data/raw/Integrated_values_surveys_1981-2022.sav
```

然后运行：

```bash
python3 src/run/run_country_values_analysis.py
```

本机当前有 `data/country_values/Integrated_values_surveys_1981-2022.sav`，但它是官方原始数据，不进 GitHub。

## 后续工作入口

- 旧模型补测：`external_runners/hk_local_hf_interview_upload.py`，优先 `bloomz_mt` 和 `polylm_chat_13b`。
- 最新模型更新：接入现有 WVS/IVS 题目 JSON，输出 raw answer，再进入解析和 PCA 投影。
- 多语言优化：比较 prompt、本地化题干、解析/adjudication、翻译/后处理或微调方法是否减少语言偏差。

旧 `bloom-1b7`、`polylm-1.7b` pilot 只作失败/调试样本，不当正式结果。
