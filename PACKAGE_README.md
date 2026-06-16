# llm_values_2026_06 交接包说明

这是给师弟接手“大模型价值观”后续工作的交接包，包含所需代码、配置、核心文档、轻量复现数据、已有结果，以及 BLOOM/PolyLM 旧 pilot 记录。

## 目录内容

```text
src/                         项目代码
config/                      国家、模型、题目配置
external_runners/            本地 HF / Colab / AutoDL runner
docs/                        复现、数据流、交接说明
data/country_values/         人类 PCA 坐标和冻结 PCA 模型
data/llm_pca/                已生成 LLM PCA 坐标
data/external/               回归协变量
data/llm_interviews/...      BLOOM/PolyLM 香港旧 pilot raw
results/analysis/            Study 结果、pilot 结果、audit 结果
results/paper_data/          论文图表和表格源数据
analysis/                    分析脚本和旧 pilot audit
Supplementary Materials/     publication-ready 表格
dryad/                       公开数据提交材料
```

## 关键入口

```text
src/run/run_paper_analysis.py
external_runners/hk_local_hf_interview_upload.py
docs/code_data_handoff_2026-06.md
docs/REPRODUCIBILITY.md
docs/data_flow_traceability.md
```

## 已验证能跑

在本目录下运行：

```bash
python3 src/run/run_paper_analysis.py --help
python3 src/run/run_paper_analysis.py
python3 src/run/run_paper_analysis.py --regression-only
python3 external_runners/hk_local_hf_interview_upload.py --help
```

当前正式样本结果：

```text
Study 1: 20 models, 120 model-language combinations
Study 2: 20 models, 920 observations
English Advantage = 3.594%
Hong Kong EA = 20.561%
Model imitation: 20 models, 66 countries
```

## 后续任务

师兄安排的后续工作主要是：

- 测旧模型：例如 BLOOM/PolyLM 等本地或开源多语言模型。
- 测最新模型：把新的 API 模型或开源模型接入现有问卷和 PCA 评价流程。
- 做多语言优化：prompt、本地化题干、回答解析、adjudication、翻译/后处理或微调方法。

所有新实验都要接回固定链条：

```text
raw answer
  -> adjudication / 解析成 WVS 选项
  -> pca_model_fixed.pkl 投影成 PCA 坐标
  -> 与 country_scores_pca.json 的人类坐标算距离
  -> English Advantage / model imitation / 其他分析
```

## BLOOM / PolyLM

包里保留了旧香港 pilot：

```text
data/llm_interviews/multilingual/interview_raw/bloom-1b7/
data/llm_interviews/multilingual/interview_raw/polylm-1.7b/
results/analysis/local_hf_hk_pilot_20260428_*.csv
analysis/outputs/hk_legacy_parsing_audit_summary.csv
analysis/outputs/hk_legacy_parsing_audit_rows.csv
```

这些旧记录只能作为 smoke test / 失败记录，不能当正式结论。后续正式跑 BLOOM/PolyLM，用：

```text
external_runners/hk_local_hf_interview_upload.py
```

常用 alias：

```text
bloomz_mt
polylm_chat_13b
```

## 没放进包的大文件

这个包不包含：

```text
WVS/EVS 官方原始 .sav
data/country_values/ivs_df.pkl
data/country_values/valid_data.pkl
全量 data/llm_interviews/*/interview_raw/
.env 或任何 API key
```

如果要从头重建人类基准，需要从 WVS/EVS 官方下载原始 `.sav`，再运行 `src/run/run_country_values_analysis.py`。
