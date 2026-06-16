# Reproducibility Guide

> 本文档说明如何复现论文中的全部统计结果  
> 对应论文的 Data Availability 和 Code Availability 声明

---

## 一、系统要求

- Python 3.10+
- ~4 GB RAM (加载 PCA 数据)
- ~300 MB 磁盘空间 (不含原始 IVS 数据)

## 二、安装

```bash
git clone https://github.com/xxx/llm-cultural-values.git
cd llm-cultural-values
pip install -r requirements.txt
```

## 三、数据说明

### 项目内包含的数据

| 文件 | 位置 | 说明 |
|------|------|------|
| IVS 国家 PCA 坐标 | `data/country_values/country_scores_pca.json` | 66 国 IVS/WVS 基准坐标 |
| 固定 PCA 模型 | `data/country_values/pca_model_fixed.pkl` | PPCA + Varimax 旋转参数 |
| LLM 角色扮演 PCA 坐标 | `data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.pkl` | 20 模型 × 66 国 × 14 语言 |
| LLM 内在价值观 PCA 坐标 | `data/llm_pca/intrinsic/` | 23 模型 × 6 语言 |
| 外部回归变量 | `data/external/regression_covariates.csv` | HDI, GDP, 殖民史等 |

### 需要单独获取的数据

| 数据 | 来源 | 说明 |
|------|------|------|
| Integrated Values Survey | https://www.worldvaluessurvey.org/ | 原始 IVS/WVS 调查数据 (~5 GB)，仅当需要重建 PCA 模型时才需要 |

### 不应上传的文件

```
data/country_values/ivs_df.pkl                    # 4.2 GB, 第三方版权数据
data/country_values/Integrated_values_surveys_*.sav  # 原始 SPSS 文件
venv/
__pycache__/
*.backup*
.DS_Store
docs/论文草稿/          # 论文草稿 (投稿前不公开)
```

## 四、复现论文全部统计量

### 一键复现

```bash
python src/run/run_paper_analysis.py
```

这会运行 Study 1–5 并输出以下文件：

| 输出文件 | 说明 |
|---------|------|
| `results/analysis/study1_intrinsic_bias.json` | Study 1: 内在价值观偏见 |
| `results/analysis/study2_english_advantage.json` | Study 2: 英语优势统计 |
| `results/analysis/study3_digital_orientalism.json` | Study 3: 数字东方主义 |
| `results/analysis/study4_colonial_legacies.json` | Study 4: 殖民遗产 |
| `results/analysis/study5_model_imitation.json` | Study 5: 模型模仿准确度 |
| `results/analysis/model_imitation_accuracy.csv` | 逐模型准确度排名 |
| `results/analysis/model_imitation_by_region.csv` | 按文化区域的模型表现 |
| `results/analysis/regression_data_v5.csv` | 回归分析完整数据 |
| `results/analysis/paper_statistics_all.json` | 全部统计量合集 |

### 运行单个 Study

```bash
python src/run/run_paper_analysis.py --study 2 3    # 只跑 Study 2 和 3
python src/run/run_paper_analysis.py --study 5      # 只跑模型对比
python src/run/run_paper_analysis.py --regression-only  # 只生成回归 CSV
```

### 从原始访谈数据重建 PCA

如果你修改了原始访谈数据或 PCA 模型，可以完整重建：

```bash
python src/run/run_paper_analysis.py --rebuild-from-raw
```

这会从 `data/llm_interviews/` 中的原始 JSON 文件开始，经过 IVS 格式化 → PCA 投影 → 统计分析的完整流程。

## 五、生成 SI 图表

```bash
# 生成全部 SI 图
cd analysis/si
python generate_figs1_cultural_map.py
python generate_figs2_baseline.py
python generate_figs4_model_response.py
python generate_figs5_orientalism.py
python generate_figs6_east_asia.py
python generate_figs7_colonial_history.py
```

输出保存到 `SI/figures/` 目录。

## 六、数据流追溯

```
原始访谈 (data/llm_interviews/*/interview_raw/)
    ↓ 处理 (src/roleplay_multilingual/)
IVS 格式 (data/llm_interviews/*/processed/)
    ↓ PCA 投影 (data/country_values/pca_model_fixed.pkl)
PCA 坐标 (data/llm_pca/*)
    ↓ 距离计算 + 统计检验 (src/run/run_paper_analysis.py)
Study 1-5 统计 (results/analysis/study*.json)
    ↓ 可视化 (analysis/si/generate_figs*.py)
SI 图表 (SI/figures/)
```

详见: `docs/data_flow_traceability.md`

## 七、项目目录结构

```
.
├── config/                  # 实验配置 (国家列表, 模型列表, 问卷)
├── data/
│   ├── country_values/      # IVS 基准数据 + PCA 模型
│   ├── external/            # 外部回归变量 (HDI, GDP, 殖民史)
│   ├── llm_interviews/      # LLM 原始访谈数据
│   └── llm_pca/             # LLM PCA 投影结果
├── src/
│   ├── run/
│   │   └── run_paper_analysis.py  # ★ 核心分析脚本 (Study 1-5)
│   ├── analysis/            # 分析工具
│   ├── base/                # 基础类
│   ├── roleplay_multilingual/  # 多语言角色扮演处理
│   └── country_values/      # IVS 数据处理
├── analysis/si/             # SI 图表生成脚本
├── results/
│   ├── analysis/            # 统计结果 (JSON/CSV)
│   └── paper_data/          # 论文数据 (图表用)
├── SI/                      # Supplementary Information 文件
└── docs/                    # 文档
```

## 八、Code Availability 声明（论文用）

> All analysis code used to generate the results reported in this paper is available
> at https://github.com/xxx/llm-cultural-values. The complete pipeline—from raw
> LLM interview data through PCA projection to final statistical tests—can be
> reproduced with a single command: `python src/run/run_paper_analysis.py`.
