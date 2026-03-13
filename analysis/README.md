# 分析脚本目录

本目录包含所有数据分析脚本，按功能分类组织。

## � 目析录结构

```
analysis/
├── core/           # 核心Stage对比分析
├── language/       # 语言/语系相关分析
├── model/          # 模型相关分析
├── figures/        # 图表生成脚本
├── si/             # SI (Supplementary Information) 图表
├── visualization/  # PPT/演示用可视化
├── languages/      # 语言数据处理工具
├── utils/          # 工具脚本
└── README.md
```

---

## 📊 core/ - 核心Stage对比分析

| 脚本 | 功能 |
|------|------|
| `stage0_vs_stage3_distance.py` | **主分析**：真实国家(Stage0) vs 多语言角色扮演(Stage3)，英语优势分析 |
| `stage0_vs_stage3_from_csv.py` | 同上，使用预计算CSV数据验证 |
| `stage0_vs_stage2_distance.py` | 真实国家(Stage0) vs 英语角色扮演(Stage2) |
| `stage1_vs_stage3_distribution.py` | LLM直接回答(Stage1) vs 角色扮演(Stage3)分布对比 |
| `stage2_vs_stage3_english.py` | 英语角色扮演(Stage2) vs 多语言角色扮演(Stage3)对比 |

**运行主分析：**
```bash
python analysis/core/stage0_vs_stage3_distance.py
```

---

## 🌍 language/ - 语言/语系相关分析

| 脚本 | 功能 |
|------|------|
| `analyze_by_language_family_v2.py` | 按语系分层分析（使用正确的语言学分类） |
| `analyze_model_by_language_family.py` | 模型×语系交叉分析 |
| `analyze_orientalism_effect.py` | 语言他者化效应分析（东方主义理论） |

---

## 🤖 model/ - 模型相关分析

| 脚本 | 功能 |
|------|------|
| `analyze_by_model_quality.py` | 按模型质量分层分析 |
| `analyze_cultural_distance.py` | 文化距离计算与分析（综合脚本） |

---

## 📈 figures/ - 图表生成脚本

| 脚本 | 功能 |
|------|------|
| `generate_publication_figures.py` | 发表级图表（Nature/PNAS风格） |
| `generate_stage1_figures.py` | Stage1分析图表 |
| `generate_east_asia_trajectory.py` | 东亚地区文化坐标轨迹图 |
| `generate_modal_profile_figures.py` | 模态分布图表 |
| `visualize_orientalism.py` | 东方主义/他者理论可视化 |

---

## 📑 si/ - SI图表生成

用于生成论文补充材料(Supplementary Information)的图表。

| 脚本 | 功能 |
|------|------|
| `si_config.py` | 统一配置（颜色、模型分类等） |
| `generate_figs1_cultural_map.py` | Fig S1: 文化地图 |
| `generate_figs2_baseline.py` | Fig S2: 基线分析 |
| `generate_figs3_b1b2.py` ~ `b5.py` | Fig S3: 各子图 |
| `generate_figs4_model_response.py` | Fig S4: 模型响应分析 |
| `generate_figs5_orientalism.py` | Fig S5: 东方主义效应 |
| `generate_figs6_east_asia.py` | Fig S6: 东亚分析 |
| `generate_figs_summary.py` | 汇总生成所有SI图表 |
| `unify_country_names.py` | 国家名称统一工具（一次性脚本，保留作为文档） |

详见 `si/README.md`

---

## 🎨 visualization/ - PPT/演示用可视化

用于开题答辩、汇报等场合的中文可视化图表。

| 脚本 | 功能 |
|------|------|
| `data_flow_v3.py` | 数据处理流程图 |
| `generate_language_distribution.py` | 语言分布可视化 |
| `generate_ppt_method_figures.py` | PPT方法部分图表 |
| `research_framework.py` | 研究框架图 |
| `research_scale_chart.py` | 研究规模图表 |

---

## 🌐 languages/ - 语言数据处理

语言扩展和国家映射相关工具。

| 脚本 | 功能 |
|------|------|
| `language_expansion_analysis.py` | 语言扩展分析 |
| `map_languages_to_countries_final.py` | 语言-国家映射 |
| `add_population_to_report.py` | 添加人口数据 |
| `update_excel_data_only.py` | 更新Excel数据 |

详见 `languages/README.md`

---

## 🔧 utils/ - 工具脚本

| 脚本 | 功能 |
|------|------|
| `quick_analyze_results.py` | 快速分析结果汇总 |
| `calc_region_stats.py` | 计算区域统计 |
| `supplementary_analysis.py` | 补充分析（论文支撑材料） |
| `verify_pc_definition.py` | 验证PC1/PC2定义是否正确 |

---

## 🔬 分析维度总览

### 1. 英语优势分析
- **问题**: 用英语 vs 母语提问，哪个能让LLM更准确模仿文化？
- **指标**: 英语优势 = (母语距离 - 英语距离) / 母语距离 × 100%
- **脚本**: `core/stage0_vs_stage3_distance.py`

### 2. 语系分析
- **问题**: 不同语系的英语优势是否不同？
- **分组**: 闪米特语系、斯拉夫语系、罗曼语系、日耳曼语系、汉藏语系、日本语系、韩语系
- **脚本**: `language/analyze_by_language_family_v2.py`

### 3. 东方主义效应
- **问题**: 文化距离越远的国家，英语优势是否越大？
- **理论**: Said的东方主义理论
- **脚本**: `language/analyze_orientalism_effect.py`, `figures/visualize_orientalism.py`

### 4. 模型质量分析
- **问题**: 高质量模型的英语优势是否更明显？
- **脚本**: `model/analyze_by_model_quality.py`

---

## 📤 输出目录

| 目录 | 内容 |
|------|------|
| `results/analysis/stage0_vs_stage3/` | 主分析结果 |
| `results/analysis/orientalism_analysis/` | 东方主义分析图表 |
| `results/analysis/language_family_analysis/` | 语系分析结果 |
| `results/figures/` | 发表级图表 |

---

## ⚠️ 注意事项

1. **排除模型**: 默认排除低质量模型 `qwen3-1.7b`
2. **英语优势计算**: 使用平均距离计算百分比，避免极端值影响
3. **多语言国家**: 为有多种官方语言的国家分别创建对比

---

**最后更新**: 2025-01-14
