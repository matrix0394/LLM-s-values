# 论文图表规划 (V3)

**PNAS 格式要求**：主文最多 6 个图表（图或表）

---

## 图表分配策略

### 主文图表（6个）

#### **Figure 1: 研究设计和文化地图框架**
- **位置**: Introduction 结尾
- **来源**: SI/figures/S1_IVS_cultural_map/
- **内容**: 
  - Inglehart-Welzel 文化地图，显示 66 个国家的真实 IVS 位置
  - 8 个文化区域的颜色编码
  - 两个维度：Traditional-Secular (PC2) 和 Survival-Self-Expression (PC1)
- **目的**: 建立分析框架，展示文化多样性
- **说明文字**: "World Values Survey cultural map showing 66 countries across 8 cultural regions. PC1 (x-axis): Survival-Self-Expression values; PC2 (y-axis): Traditional-Secular values."

---

#### **Figure 2: 基线语言效应 - LLM 内在价值观**
- **位置**: Results 第一部分
- **来源**: SI/figures/S2_Baseline_intrinsic_values/A2_per_language/
- **内容**: 
  - 6 种语言（英语、法语、西班牙语、俄语、阿拉伯语、简体中文）的模型分布
  - 显示英语最世俗（PC1=+2.69），阿拉伯语最传统（PC1=+0.98）
  - 23 个模型的散点分布
- **目的**: 证明语言本身影响模型价值观（基线效应）
- **统计**: F=3.38, p=0.007
- **说明文字**: "Baseline language effect: LLM intrinsic values vary by prompt language. English prompts elicit most secular responses (PC1=+2.69), Arabic prompts elicit most traditional (PC1=+0.98). Each point represents one model in one language (n=138)."

---

#### **Figure 3: 数字东方主义 - 文化区域语言效应**
- **位置**: Results 核心发现
- **来源**: SI/figures/S5_English_advantage_and_orientalism/FigS5A_cultural_regions_language_effect.pdf
- **内容**: 
  - 按文化区域分组的英语优势百分比
  - 显示非西方（伊斯兰+17.4%，东正教+17.7%）vs 西方（新教欧洲-20.3%）的对比
  - 误差条显示区域内变异
- **目的**: 展示核心发现 - 数字东方主义模式
- **统计**: 伊斯兰 p<0.0001, 东正教 p=0.008, 新教欧洲 p<0.001
- **说明文字**: "Digital Orientalism: Non-Western cultures show English advantage (Islamic/Arab +17.4%, Orthodox/Slavic +17.7%), while Western cultures show native advantage (Protestant Europe -20.3%). Error bars: ±1 SE."

---

#### **Figure 4: 东亚梯度 - 训练数据和殖民遗产**
- **位置**: Results 区域异质性部分
- **来源**: SI/figures/S6_East_Asia_analysis/FigS6C_east_asia_english_gradient.pdf
- **内容**: 
  - 中国、日本、韩国、台湾、香港、澳门的英语优势对比
  - 显示从中国（+0.07%）到台湾（+27.1%）的梯度
  - 香港-澳门对比（+24.8% vs -13.6%）
- **目的**: 展示区域内异质性，说明训练数据和殖民遗产的作用
- **说明文字**: "East Asian gradient reveals training data and colonial legacy effects. China shows near-perfect parity (+0.07%), while Taiwan (+27.1%) and Hong Kong (+24.8%) show strong English advantage. Hong Kong-Macao contrast illustrates colonial legacy: British (+24.8%) vs Portuguese (-13.6%)."

---

#### **Figure 5: 模型来源效应 - 区域专业化**
- **位置**: Results 模型来源部分
- **来源**: SI/figures/S4_Model_and_response_analysis/FigS4G_vendor_origin_analysis.pdf
- **内容**: 
  - 左图：按模型来源（USA、China、Europe）的平均文化距离，带 ANOVA 检验
  - 右图：所有模型按供应商排名，按来源着色
  - 显示中国模型（DeepSeek、Alibaba）的竞争性表现
- **目的**: 展示模型来源对整体性能的影响，配合 Table 1 展示语言家族特定效应
- **统计**: ANOVA 检验结果
- **说明文字**: "Model origin affects overall performance. Chinese models (DeepSeek, Qwen) show competitive accuracy, while US models exhibit higher variance. Combined with language-specific analysis (Table 1), this reveals regional specialization: Chinese models show weaker Orientalism for Sino-Tibetan (+1.9% vs +16.8% for US models) and Semitic languages (+8.2% vs +19.6%)."

---

#### **Figure 6: 模型性能和一致性**
- **位置**: Results 或 Discussion
- **来源**: SI/figures/summary/FigSx4_score_vs_consistency.pdf
- **内容**: 
  - 散点图：文化距离 vs 跨语言一致性
  - 显示 GPT-4o、DeepSeek 等顶级模型
  - 相关性 r=-0.65
- **目的**: 展示模型性能差异和一致性-准确性关系
- **说明文字**: "Model performance varies dramatically. GPT-4o achieves lowest cultural distance (1.26), while small models show 2-3× larger errors. Consistency correlates with accuracy (r=-0.65, p<0.001)."

---

## 补充材料图表（SI）

### 必须引用的 SI 图表

#### **Figure S1: IVS 文化地图参考**
- 完整的 109 国家文化地图
- 作为所有分析的参考基准

#### **Figure S2: 基线详细分析**
- A1: 每个模型的语言稳定性（23 个图）
- A2: 每种语言的模型分布（6 个图）

#### **Figure S3: 文化角色扮演详细结果**
- B1: 每个模型的平均表现（21 个图）
- B2: 每个国家的平均表现（66 个图）
- B3: 模型×国家交叉（~1,386 个图）
- B4: 国家×语言交叉（~122 个图）
- B5: 模型×语言交叉（~294 个图）

#### **Figure S4: 模型行为分析**
- S4A: 基线 vs 角色扮演一致性对比
- S4B: 响应分布分析
- S4C: 模型排名
- S4D: 国家难度排名

#### **Figure S5: 东方主义详细分析**
- S5A: 文化区域语言效应（主文 Figure 3）
- S5B: 东方主义理论验证
- S5C: 伊斯兰 vs 西方对比
- S5D: 地理梯度趋势

#### **Figure S6: 东亚详细分析**
- S6A: 东亚文化轨迹
- S6B: 东亚距离对比
- S6C: 东亚英语梯度（主文 Figure 4）

#### **Figure Sx: 统计概览**
- Sx1: 模型×国家热图
- Sx2: 模型×语言热图
- Sx3: 顶部/底部排名
- Sx4: 得分 vs 一致性（主文 Figure 6）

---

## 各部分图表引用计划

### Abstract
- 无图表
- 引用关键数字和统计

### Introduction
- **Figure 1**: IVS 文化地图（建立框架）
- 文字引用：提到 23 模型、66 国家、13 语言的规模

### Results

#### 第一部分：基线语言效应
- **Figure 2**: 基线语言效应
- 引用 SI Figure S2 的详细分析

#### 第二部分：英语母语国家基线
- 文字描述，引用 SI Figure S3-B2 中的相关国家

#### 第三部分：整体语言效应
- 文字描述统计
- 引用 SI Figure S5B（分布分析）

#### 第四部分：数字东方主义
- **Figure 3**: 文化区域语言效应（核心发现）
- 引用 SI Figure S5C, S5D（详细分析）

#### 第五部分：东亚异质性
- **Figure 4**: 东亚梯度
- 引用 SI Figure S6A, S6B（轨迹和距离）

#### 第六部分：拉美复杂性
- 文字描述
- 引用 SI Figure S3-B2（拉美国家详细结果）

#### 第七部分：模型来源
- **Figure 5**: 模型来源效应
- 引用 SI Figure S4C（模型排名）

#### 第八部分：模型一致性
- **Figure 6**: 性能 vs 一致性
- 引用 SI Figure Sx1, Sx2（热图）

### Discussion
- 引用主文 Figures 2-6
- 引用 SI 详细分析支持论点
- 无新图表

### Conclusion
- 无图表
- 总结关键数字

---

## 表格计划

### **Table 1: 模型来源×语言家族交互**（已在 Results 中）
- 位置: Results 第七部分
- 内容: 中国/美国/欧洲模型对不同语言家族的英语优势
- 数据来源: 分析结果汇总

### **Table S1-S8**: 补充材料表格
- 已存在于 SI/model_responses/ 和 SI/pca/

---

## 图表制作优先级

### 高优先级（主文必需）
1. ✅ Figure 1: IVS 文化地图（已有 SI/S1）
2. ✅ Figure 2: 基线语言效应（已有 SI/S2）
3. ✅ Figure 3: 数字东方主义（已有 SI/S5A）
4. ✅ Figure 4: 东亚梯度（已有 SI/S6C）
5. ✅ Figure 5: 模型来源效应（已有 SI/S4G）
6. ✅ Figure 6: 性能 vs 一致性（已有 SI/Sx4）

### 中优先级（可能需要改编）
- Figure 5 的制作（如果 SI 中没有合适的）
- 确保所有主文图表符合 PNAS 格式要求

### 低优先级（SI 已完成）
- 所有 SI 图表已生成
- 只需确保引用正确

---

## 下一步行动

1. **检查 Figure 5 是否需要新建**
   - 查看 SI/S4 是否有合适的模型来源对比图
   - 如果没有，需要生成新图

2. **确认所有图表格式**
   - PNAS 要求 PDF 矢量格式 ✅
   - 颜色无障碍（色盲友好）✅
   - 字体大小和清晰度

3. **编写图表说明文字**
   - 每个图表需要详细的 caption
   - 包含统计显著性
   - 解释所有符号和缩写

4. **更新论文文本**
   - 在适当位置插入 "Figure X" 引用
   - 确保文字和图表一致
   - 添加 SI 引用

---

## 图表文件路径汇总

```
主文图表：
- Figure 1: SI/figures/S1_IVS_cultural_map/FigS1_IVS_cultural_map.pdf
- Figure 2: SI/figures/S2_Baseline_intrinsic_values/A2_per_language/[合并图]
- Figure 3: SI/figures/S5_English_advantage_and_orientalism/FigS5A_cultural_regions_language_effect.pdf
- Figure 4: SI/figures/S6_East_Asia_analysis/FigS6C_east_asia_english_gradient.pdf
- Figure 5: SI/figures/S4_Model_and_response_analysis/FigS4G_vendor_origin_analysis.pdf
- Figure 6: SI/figures/summary/FigSx4_score_vs_consistency.pdf
```

---

**状态**: 规划完成，等待确认和实施
**日期**: 2026-01-16
