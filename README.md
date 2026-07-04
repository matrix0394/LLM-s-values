# The Value Atlas of AI: LLM Values Handoff Project

这是 `llm_values_2026_06` 交接版项目。它保留可运行代码、核心配置、轻量 PCA 坐标和统计结果，用于复现主线分析，并继续测试旧模型、最新模型和多语言优化方法。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 src/run/run_paper_analysis.py --help
python3 src/run/run_paper_analysis.py --study 2
python3 external_runners/hk_local_hf_interview_upload.py --help
```

Study 2 正式口径应为 20 models、920 observations、Overall English Advantage +3.6%。

## 主要入口

- `src/run/run_paper_analysis.py`：论文主分析，运行 Study 1-4、model imitation、回归数据生成。
- `src/run/run_country_values_analysis.py`：从 WVS/EVS 官方原始数据重建人类 PCA 基准。
- `src/run/run_llm_values_analysis.py`：LLM intrinsic/baseline 流程。
- `src/run/run_roleplay_multilingual_analysis.py`：多语言国家角色扮演流程。
- `external_runners/hk_local_hf_interview_upload.py`：BLOOM/PolyLM、本地 HF、Colab/AutoDL 后续模型访谈入口。

## 核心目录

```text
src/                 代码
config/              国家、模型、题目 JSON 配置
data/country_values/ 人类国家 PCA 坐标和固定 PCA 模型
data/llm_pca/        LLM PCA 坐标和 entity_scores
data/external/       回归协变量
data/llm_interviews/ 只保留 BLOOM/PolyLM 香港旧 pilot 小样本 raw
results/analysis/    Study 统计结果
results/paper_data/  论文图表/表格源数据
docs/                交接、复现、数据流说明
external_runners/    外部/本地模型 runner
```

## 数据边界

这个 GitHub 包不包含官方 WVS/EVS 原始 `.sav`、`ivs_df.pkl`、`valid_data.pkl`、全量 API/raw interview、完整 PCA 中间对象、旧图表、PPT、`Supplementary Materials` 或 `dryad`。

需要从头重建人类基准时，让师弟从 WVS 官网下载 `Integrated_values_surveys_1981-2022.sav`，放到 `data/raw/` 后运行：

```bash
python3 src/run/run_country_values_analysis.py
```

需要 debug raw answer、重做 parser 或完整重建 LLM 中间数据时，由你通过网盘/微信单独发 `START_HERE.md` 中列出的项目自跑数据。

## 后续实验原则

所有新模型都接回同一条链：raw answer -> adjudication/解析 -> 固定 PCA 投影 -> 与人类国家坐标算距离 -> Study 1-4/model imitation/优化实验比较。

正式 Study 1-4 使用 20-model paper sample。`qwen3-1.7b`、`glm-4.6`、`qwq-32b` 是后续探索模型，不混入正式统计。
