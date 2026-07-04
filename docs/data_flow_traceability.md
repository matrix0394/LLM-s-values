# Data Flow Traceability

本项目所有旧模型、最新模型和多语言优化实验，都必须接回同一条评价链，才能和论文主线可比。

## 主链路

```text
WVS/EVS 官方调查数据
  -> src/run/run_country_values_analysis.py
  -> data/country_values/country_scores_pca.json
  -> data/country_values/pca_model_fixed.pkl

LLM raw answer
  -> 解析/adjudication 成 10 个 WVS/IVS 题目的数值回答
  -> 用 pca_model_fixed.pkl 投影到固定 PCA 空间
  -> 生成 data/llm_pca/* entity_scores
  -> src/run/run_paper_analysis.py
  -> results/analysis/study*.json 和 results/paper_data/*.csv
```

## 关键文件

- `data/country_values/pca_model_fixed.pkl`：固定 PCA 模型。新模型必须用它投影，不能重新拟合一个不可比的 PCA。
- `data/country_values/country_scores_pca.json`：人类国家/地区坐标。
- `data/llm_pca/intrinsic/llm_pca_entity_scores.pkl`：Study 1 baseline 坐标。
- `data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.pkl`：Study 2-4 和 model imitation 坐标。
- `results/analysis/regression_data_v5.csv`：回归数据。

## 新模型接入

1. 用固定问卷让模型回答 WVS/IVS 10 题。
2. 保存 raw answer，保留模型名、国家、语言、时间戳。
3. 用人工或自动 adjudication 把文本回答映射为 WVS 编码。
4. 用固定 PCA 模型投影到 PC1/PC2。
5. 计算到人类国家坐标的距离和 English Advantage。
6. 再进入 Study 1-4、model imitation 或新的优化实验比较。

## BLOOM/PolyLM

正式补测入口：

```bash
python3 external_runners/hk_local_hf_interview_upload.py --help
```

优先 alias：`bloomz_mt`、`polylm_chat_13b`。旧 `bloom-1b7`、`polylm-1.7b` raw 只保留为 pilot/smoke test。

## 样本边界

正式 paper sample 是 20 个模型。`qwen3-1.7b`、`glm-4.6`、`qwq-32b` 是探索模型，不进入正式 Study 1-4 统计。
