# 论文图表配置总结 (V3)

## 主文 6 个图表（PNAS 限制）

| 图号 | 标题 | 位置 | 文件路径 | 状态 |
|------|------|------|----------|------|
| **Figure 1** | IVS 文化地图框架 | Introduction | `SI/figures/S1_IVS_cultural_map/FigS1_IVS_cultural_map.pdf` | ✅ 已有 |
| **Figure 2** | 基线语言效应 | Results §1 | `SI/figures/S2_Baseline_intrinsic_values/A2_per_language/` | ✅ 已有 |
| **Figure 3** | 数字东方主义 | Results §4 | `SI/figures/S5_English_advantage_and_orientalism/FigS5A_*.pdf` | ✅ 已有 |
| **Figure 4** | 东亚梯度 | Results §5 | `SI/figures/S6_East_Asia_analysis/FigS6C_*.pdf` | ✅ 已有 |
| **Figure 5** | 模型来源效应 | Results §7 | `SI/figures/S4_Model_and_response_analysis/FigS4G_*.pdf` | ✅ 已有 |
| **Figure 6** | 性能与一致性 | Results §8 | `SI/figures/summary/FigSx4_*.pdf` | ✅ 已有 |

---

## 主文 1 个表格

| 表号 | 标题 | 位置 | 内容 | 状态 |
|------|------|------|------|------|
| **Table 1** | 模型来源×语言家族交互 | Results §7 | 中国/美国/欧洲模型对汉藏/闪米特/斯拉夫/罗曼/日耳曼语言的英语优势 | ✅ 已在文中 |

---

## 各部分图表使用

### Introduction
- **Figure 1**: 建立 Inglehart-Welzel 文化地图框架
- 展示 66 个国家在 8 个文化区域的分布

### Results

#### §1: LLM 内在价值观（基线语言效应）
- **Figure 2**: 6 种语言的模型分布
- 关键发现：英语最世俗（PC1=+2.69），阿拉伯语最传统（PC1=+0.98），F=3.38, p=0.007
- 引用 SI Figure S2 详细分析

#### §2: 英语母语国家基线
- 文字描述
- 引用 SI Figure S3-B2

#### §3: 整体语言效应
- 文字描述：+8.3% 英语优势
- 引用 SI Figure S5B

#### §4: 数字东方主义
- **Figure 3**: 文化区域语言效应（核心发现）
- 关键发现：伊斯兰+17.4%，东正教+17.7%，新教欧洲-20.3%
- 引用 SI Figure S5C, S5D

#### §5: 东亚异质性
- **Figure 4**: 东亚梯度
- 关键发现：中国+0.07%，台湾+27.1%，香港+24.8%，澳门-13.6%
- 引用 SI Figure S6A, S6B

#### §6: 拉美复杂性
- 文字描述
- 引用 SI Figure S3-B2

#### §7: 模型来源
- **Figure 5**: 模型来源分析
- **Table 1**: 语言家族特定效应
- 关键发现：中国模型汉藏+1.9% vs 美国+16.8%
- 引用 SI Figure S4C

#### §8: 模型一致性
- **Figure 6**: 性能 vs 一致性散点图
- 关键发现：r=-0.65, GPT-4o 最佳（d=1.26）
- 引用 SI Figure Sx1, Sx2

### Discussion
- 引用主文 Figures 2-6
- 引用 SI 详细分析
- 无新图表

### Conclusion
- 无图表
- 总结关键数字

---

## 补充材料（SI）图表

### 完整 SI 图表列表

| 编号 | 标题 | 数量 | 用途 |
|------|------|------|------|
| **S1** | IVS 文化地图 | 1 | 参考基准 |
| **S2** | 基线内在价值观 | 24 | 详细语言效应 |
| **S3** | 文化角色扮演 | ~1,889 | 完整结果矩阵 |
| **S4** | 模型行为分析 | 7 | 性能特征 |
| **S5** | 东方主义分析 | 4 | 理论验证 |
| **S6** | 东亚分析 | 3 | 区域深入 |
| **Sx** | 统计概览 | 4 | 汇总分析 |

**总计**: ~1,932 个图表

---

## 图表制作状态

### ✅ 全部完成
- 所有主文图表已在 SI 中生成
- 所有 SI 图表已生成
- 格式符合 PNAS 要求（PDF 矢量格式）
- 颜色无障碍（色盲友好）

### 📝 待完成任务
1. 在论文文本中插入图表引用
2. 编写每个图表的详细 caption
3. 确保图表编号和引用一致
4. 检查图表质量和清晰度

---

## 下一步行动

### 1. 更新 Results 部分
- 在每个小节适当位置插入 "(Figure X)" 引用
- 确保文字描述与图表内容一致
- 添加 SI 图表引用

### 2. 编写图表说明（Captions）
每个图表需要包含：
- 简短标题
- 详细描述（2-3 句）
- 关键统计数据
- 符号和缩写解释

### 3. 格式检查
- 确认所有图表为 PDF 格式
- 检查分辨率和清晰度
- 验证颜色对比度

### 4. 交叉引用
- 确保所有 "Figure X" 引用正确
- 确保所有 "SI Figure SX" 引用正确
- 检查表格引用

---

## 图表说明模板

```
Figure X. [简短标题]. [详细描述，2-3句话，解释图表内容和主要发现]. [统计显著性]. [符号说明]. [样本量信息].
```

### 示例

```
Figure 3. Digital Orientalism: Cultural regions show opposite language effects. Non-Western cultures (Islamic/Arab, Orthodox/Slavic) show strong English advantage (+17.4%, +17.7%), while Western cultures (Protestant Europe, Catholic Europe) show native language advantage (-20.3%, -12.4%). Error bars represent ±1 standard error. Statistical significance: ***p<0.001, **p<0.01, *p<0.05. n=21 models × 66 countries × 13 languages.
```

---

**状态**: 图表规划完成，所有图表已生成 ✅  
**下一步**: 在论文文本中插入图表引用和编写 captions  
**日期**: 2026-01-16
