# Analysis 分析脚本目录

**目的**: 集中管理所有跨Stage的分析脚本  
**原则**: 每个分析一个脚本，功能清晰，避免重复  
**输出**: 所有结果保存在 `results/analysis/` 目录下

---

## 📁 完整结构（3个核心脚本）

```
analysis/
├── README.md                              # 本文档
│
├── stage0_vs_stage3_distance.py           # ⭐ Stage0 vs Stage3距离分析（核心）
│
├── stage1_vs_stage3_distribution.py       # Stage1原生 vs Stage3模仿分布
│
└── visualize_orientalism.py               # 东方主义理论可视化
```

---

## 📏 1. stage0_vs_stage3_distance.py ⭐⭐⭐

**功能**: 对比真实国家坐标（Stage0）和多语言模仿坐标（Stage3），计算英语优势

**输入**:
- `data/country_values/country_scores_pca.json` - 真实国家坐标
- `data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl` - Stage3多语言坐标

**输出** (`results/analysis/stage0_vs_stage3/`):
- `distances_detailed.xlsx` - 所有距离（母语+英语）
- `english_advantage_by_model.xlsx` - 每个模型的英语优势
- `english_advantage_average.xlsx` - 平均英语优势
- `english_native_baseline.xlsx` - 英语母语国家/地区基准数据 ⭐
- `english_native_baseline_stats.csv` - 基准统计信息 ⭐
- `english_advantage_analysis.png` - 英语优势分析图
- `coordinates_comparison.png` - 母语vs英语坐标对比
- `east_asia_analysis.png` - 东亚国家/地区详细分析

**分析内容**:
1. 计算母语模仿距离和英语模仿距离
2. **英语母语国家/地区基准**: 美国、英国、澳大利亚、新西兰、加拿大的英语模仿距离 ⭐
3. 计算英语优势：`(母语距离 - 英语距离) / 母语距离 × 100%`
4. 全球排名：哪些国家/地区英语优势最强
5. 东亚梯度：香港 > 新加坡 > 中国 > 台湾 > 澳门 > 日本 > 韩国（包含国家和地区）
6. 按模型对比：不同模型的语言偏好

**运行**:
```bash
python analysis/stage0_vs_stage3_distance.py
```

**核心发现**:
- **英语母语国家/地区基准**: 3.26（澳大利亚、新西兰、加拿大）⭐
- **所有英语模仿平均**: 2.12（比基准低1.15，说明非英语国家/地区反而更接近！）
- 香港地区(粤语): +48.0% 英语优势（全球最高）
- 母语 vs 英语平均距离对比
- 西班牙语国家多为母语优势（负值）

---

## 2. stage1_vs_stage3_distribution.py

**功能**: 分析大模型原生坐标（Stage1）和模仿坐标（Stage3）的分布集中度

**输入**:
- `data/llm_values/llm_pca_entity_scores.json` - Stage1原生坐标
- `data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl` - Stage3模仿坐标

**输出** (`results/analysis/stage1_vs_stage3/`):
- `distribution_analysis.xlsx` - 偏离距离详细数据
- `model_concentration.csv` - 每个模型的集中度统计
- `distribution_by_model.png` - 按模型的分布图
- `deviation_analysis.png` - 偏离距离分析
- `concentration_heatmap.png` - 集中度热力图

**分析内容**:
1. 计算每个模型的原生坐标（Stage1）
2. 计算角色扮演坐标（Stage3）到原生坐标的距离
3. 分析哪些模型最"灵活"（偏离大）vs 最"固执"（集中在原生）
4. 对比英语和母语的偏离程度

**运行**:
```bash
python analysis/stage1_vs_stage3_distribution.py
```

**研究问题**:
- 模型能否"跳出"自己的文化倾向？
- 哪些模型最"灵活"（偏离最大）？
- 哪些模型最"固执"（集中在原生坐标）？

---

## 3. visualize_orientalism.py

**功能**: 对比Stage2（纯英语）和Stage3中的英语部分，验证数据一致性

**输入**:
- `data/roleplay_English/roleplay_pca_*.pkl` - Stage2英语坐标
- `data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl` - Stage3英语坐标

**输出** (`results/analysis/stage2_vs_stage3/`):
- `english_comparison.xlsx` - 逐点对比数据
- `country_differences.csv` - 按国家/地区的差异
- `model_differences.csv` - 按模型的差异
- `coordinate_correlation.png` - PC1/PC2相关性图
- `difference_analysis.png` - 差异分析图
- `coordinate_distribution.png` - 坐标分布对比

**分析内容**:
1. 匹配相同的国家-模型组合
2. 计算Stage2和Stage3英语坐标的欧氏距离
3. 计算PC1和PC2的相关系数
4. 识别差异最大的国家和模型

**运行**:
```bash
python analysis/stage2_vs_stage3_english.py
```

**验证目标**:
- Stage2和Stage3的英语数据是否一致？
- 如果不一致，差异有多大？
- 差异是否系统性的？

---

## 🎨 5. visualize_orientalism.py

**功能**: 生成东方主义/他者理论验证的可视化图表

**理论背景**:
- "他者"（The Other）理论：LLM对非英语国家的刻板印象
- 东方主义：西方视角下对东方的简化和刻板化
- 发现：英语优势在东亚地区最强，尤其是港台澳

**依赖**: ⚠️ 必须先运行 `stage0_vs_stage3_distance.py`

**输入**:
- `results/analysis/stage0_vs_stage3/distances_detailed.xlsx` - 距离数据
- `results/analysis/stage0_vs_stage3/english_advantage_average.xlsx` - 英语优势数据

**输出** (`results/analysis/orientalism_analysis/`):
- `east_asia_complete_gradient.png` - 东亚完整梯度（包括日韩）
- `hk_tw_mo_multilingual.png` - 港台澳多语言对比
- `global_language_regions.png` - 全球语言区域对比
- `orientalism_theory_validation.png` - 他者理论验证
- `japan_korea_analysis.png` - 日韩专项分析

**运行**:
```bash
# 1. 先运行依赖脚本
python analysis/stage0_vs_stage3_distance.py

# 2. 再运行可视化
python analysis/visualize_orientalism.py
```

**价值**: ✅ 理论贡献的可视化支持，专注于东亚地区分析

---

## 📊 分析矩阵总结

### 跨Stage对比分析

| 对比 | 脚本 | 核心问题 | 输出目录 |
|------|------|---------|---------|
| Stage0 vs Stage2 | `stage0_vs_stage2_distance.py` | 英语模仿准确度 | `results/analysis/stage0_vs_stage2/` |
| Stage0 vs Stage3 | `stage0_vs_stage3_distance.py` ⭐ | 母语vs英语效果 | `results/analysis/stage0_vs_stage3/` |
| Stage1 vs Stage2/3 | `stage1_vs_stage23_distribution.py` | 模仿是否偏离原生 | `results/analysis/stage1_vs_stage23/` |
| Stage2 vs Stage3 | `stage2_vs_stage3_english.py` | 英语数据一致性 | `results/analysis/stage2_vs_stage3/` |

### 核心分析功能

| 分析类型 | 脚本 | 输出 |
|---------|------|------|
| 距离和英语优势 | `calculate_distances.py` ⭐ | `results/distance_analysis_correct/` |
| 坐标对齐验证 | `generate_alignment_report.py` | `results/alignment_analysis/` |
| 理论验证可视化 | `visualize_orientalism.py` | `results/orientalism_analysis/` |

---

## 🎯 完整分析覆盖范围

### 1. 距离分析 ✅

- **Stage0 vs Stage2**: 真实国家 vs 英语模仿
- **Stage0 vs Stage3**: 真实国家 vs 母语/英语模仿
- **英语优势计算**: 母语 vs 英语哪个更准确

### 2. 分布分析 ✅

- **Stage1 vs Stage2/3**: 原生坐标 vs 模仿坐标的集中度
- **模型灵活性**: 哪些模型能"跳出"自己的文化倾向

### 3. 一致性验证 ✅

- **Stage2 vs Stage3**: 英语数据是否一致
- **Stage1 vs Stage3**: 坐标系统是否对齐

### 4. 理论验证 ✅

- **东方主义理论**: 英语国家的悖论
- **他者理论**: LLM对非英语国家的刻板印象

### 5. 统计分析 ✅

- **按国家/地区**: 哪些国家/地区最容易/难模仿
- **按模型**: 哪些模型表现最好
- **按语言区**: 东亚、阿拉伯、西班牙语、俄语
- **全球排名**: Top 20英语优势国家/地区

---

## 🚀 运行所有分析

```bash
# 1. 核心分析（必须先运行）
python analysis/calculate_distances.py

# 2. Stage对比分析
python analysis/stage0_vs_stage2_distance.py
python analysis/stage0_vs_stage3_distance.py
python analysis/stage1_vs_stage23_distribution.py
python analysis/stage2_vs_stage3_english.py

# 3. 验证和可视化
python analysis/generate_alignment_report.py
python analysis/visualize_orientalism.py
```

---

## 📁 输出目录结构

```
results/analysis/
├── stage0_vs_stage2/              # Stage0 vs Stage2分析
│   ├── distances_detailed.xlsx
│   ├── distance_analysis.png
│   └── coordinates_scatter.png
│
├── stage0_vs_stage3/              # Stage0 vs Stage3分析（核心）
│   ├── distances_detailed.xlsx
│   ├── english_advantage_*.xlsx
│   ├── english_advantage_analysis.png
│   ├── coordinates_comparison.png
│   └── east_asia_analysis.png
│
├── stage1_vs_stage23/             # Stage1原生 vs Stage2/3模仿
│   ├── distribution_analysis.xlsx
│   ├── distribution_by_model.png
│   ├── deviation_analysis.png
│   └── concentration_heatmap.png
│
├── stage2_vs_stage3/              # Stage2 vs Stage3英语对比
│   ├── english_comparison.xlsx
│   ├── coordinate_correlation.png
│   ├── difference_analysis.png
│   └── coordinate_distribution.png
│
└── (其他目录)
    ├── distance_analysis_correct/  # 原有的核心距离分析
    ├── alignment_analysis/         # 坐标对齐验证
    └── orientalism_analysis/       # 理论验证
```

---

## ✅ 整理总结

### 核心分析脚本（5个）

1. ✅ `stage0_vs_stage2_distance.py` - Stage0 vs Stage2距离分析
2. ✅ `stage0_vs_stage3_distance.py` ⭐ - Stage0 vs Stage3距离分析（核心）
3. ✅ `stage1_vs_stage23_distribution.py` - 原生vs模仿分布集中度
4. ✅ `stage2_vs_stage3_english.py` - Stage2 vs Stage3英语一致性
5. ✅ `visualize_orientalism.py` - 理论验证可视化

### 已删除的重复脚本（2个）

1. ❌ `calculate_distances.py` - 功能已被 `stage0_vs_stage3_distance.py` 覆盖
2. ❌ `generate_alignment_report.py` - 功能已被 `stage1_vs_stage23_distribution.py` 覆盖

### 最终效果

- **脚本数量**: 5个核心分析脚本
- **功能覆盖**: 完整覆盖所有跨Stage对比需求
- **输出清晰**: 所有结果统一保存在 `results/analysis/` 下
- **无重复**: 每个脚本功能明确，无冗余
- **数据正确**: 使用正确的 rescaled 坐标和聚合后的实体数据

---

**最后更新**: 2025-11-22  
**状态**: ✅ 完整分析体系已建立  
**维护者**: Research Team

🎉🎉🎉

