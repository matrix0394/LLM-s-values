# SI 图表生成脚本

生成论文 Supplementary Information (SI) 中的所有图表。SI 用于写论文附录，图表数据由项目 pipeline 生成后更新到 SI。

## 数据来源

`si_config.py` 中的数据加载函数**优先从项目数据读取**，找不到时才用 SI/pca/：
- Table_S5 (IVS) → `data/country_values/Table_S5_IVS_PCA_coordinates.csv`
- Table_S6 (baseline) → `data/llm_pca/intrinsic/Table_S6_LLM_baseline_PCA_coordinates.csv`
- Table_S7 (roleplay) → `data/llm_pca/multilingual/Table_S7_LLM_roleplay_PCA_coordinates.csv`

## 架构

所有脚本共享 `si_config.py` 中的统一配置：
- 颜色定义（文化区域、语言、模型）
- 字体和样式常量
- 数据加载函数
- 通用绑图函数

## 图表生成脚本

| 脚本 | 输出 | 说明 |
|------|------|------|
| `generate_figs1_cultural_map.py` | S1 | IVS 文化地图参考图 |
| `generate_figs2_baseline.py` | S2 | LLM 基线内在价值观 |
| `generate_figs3_b1b2.py` | S3-B1/B2 | 模型/国家维度角色扮演 |
| `generate_figs3_b3.py` | S3-B3 | (模型, 国家) 组合 |
| `generate_figs3_b4.py` | S3-B4 | (国家, 语言) 组合 |
| `generate_figs3_b5.py` | S3-B5 | (模型, 语言) 组合 |
| `generate_figs4_model_response.py` | S4 | 模型响应分析 |
| `generate_figs5_orientalism.py` | S5 | 英语优势与东方主义 |
| `generate_figs6_east_asia.py` | S6 | 东亚地区专项分析 |
| `generate_figs7_colonial_history.py` | S7 | 殖民历史效应分析 |
| `generate_figs_summary.py` | Summary | 热力图、排名、散点图 |

## 工具脚本

| 脚本 | 用途 |
|------|------|
| `unify_country_names.py` | 统一 IVS 与 roleplay 数据的国家名称 |

## 使用

```bash
# 从项目根目录运行
cd /path/to/LLM\'s\ values

# 生成单个图表
python3 analysis/si/generate_figs1_cultural_map.py

# 生成所有图表
for f in analysis/si/generate_figs*.py; do python3 "$f"; done
```

## 输出

所有图表输出到 `SI/figures/` 目录，同时生成 PNG 和 PDF 格式。
