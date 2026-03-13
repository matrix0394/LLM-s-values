# Study 4 整合指南

## 概述

我已经为Study 4创建了三个修订文档：
1. `study4_methods_revised.md` - Methods部分
2. `study4_results_revised.md` - Results部分  
3. `study4_discussion_addition.md` - Discussion部分补充

## 如何整合到现有论文

### 1. Methods部分 (`paper_pnas_methods_v2.md`)

**位置**：替换当前的"Study 4. Colonial History and Contemporary Language Effects"部分

**操作**：
```markdown
找到：## Study 4. Colonial History and Contemporary Language Effects
替换为：study4_methods_revised.md 的全部内容
```

**关键改动**：
- 标题加上"(Exploratory)"
- 删除了回归分析和中介分析的承诺
- 明确说明Experiment 4c的数据限制
- 降低了语气，从"test causal hypotheses"改为"exploratory analyses"
- 添加了"Note on scope"说明未完成的分析

### 2. Results部分（需要创建或更新）

**位置**：在Results章节中添加Study 4部分

**操作**：
- 如果已有Study 4 Results，替换为`study4_results_revised.md`的内容
- 如果没有，在Study 3之后添加

**关键特点**：
- 诚实报告不显著结果
- 提供具体数值和置信区间
- 解释为什么不显著（高方差、小样本）
- 明确说明数据限制
- 引用SI图表（Fig. S7B, S7C, S7D）

### 3. Discussion部分 (`paper_pnas_discussion.md`)

**位置**：在Discussion中添加新的小节

**操作**：
```markdown
建议位置：在讨论Study 3之后，或在"Limitations"部分之前

添加：study4_discussion_addition.md 的内容
```

**关键内容**：
- 深入讨论为什么难以检测殖民历史效应
- 四个主要解释：高方差、中介因素、数据限制、统计功效
- 与Study 3对比（为什么Orientalism显著但colonial history不显著）
- 方法学贡献
- 未来研究方向

### 4. SI部分

**已完成**：
- SI图表已生成（S7A-S7D）在 `SI/figures/S7_Colonial_history/`
- 统计摘要在 `results/analysis/colonial_history/summary_statistics.txt`

**需要添加到SI文档**：
```markdown
## Figure S7. Colonial History Analysis

**S7A. East Asian Colonial Gradient.** English advantage for Hong Kong, Macao, 
China, Japan, and Korea. Hong Kong (British colony 1842–1997) shows positive 
English advantage (15.84%), while Macao (Portuguese colony 1557–1999) shows 
negative Portuguese advantage (−15.67%). Error bars represent standard errors 
across 20 models.

**S7B. Hong Kong vs Macao Comparison.** Direct comparison of colonial language 
advantages. Left panel: bar chart with 95% confidence intervals. Right panel: 
violin plots showing distribution across models. The difference is not 
statistically significant (t(37.9) = 0.509, p = 0.614, Cohen's d = 0.161).

**S7C. Latin American Language Variants.** English advantage across Latin 
American countries with different colonial languages: Spanish-speaking (n=11), 
Portuguese-speaking (Brazil, n=1), and French-speaking (Haiti, n=1). One-way 
ANOVA shows no significant differences (F(2, 10) = 1.035, p = 0.391, η² = 0.171).

**S7D. African Colonial History Data Limitation.** Documentation of systematic 
data gap: all British-colonized African countries (Kenya, Nigeria, Ghana, South 
Africa, Zimbabwe, Zambia) only have English language data, lacking native 
language comparisons needed to calculate English advantage.
```

## 5. Abstract和Overview更新

### Abstract
如果Abstract提到Study 4，需要更新为：

```markdown
旧版：
"Study 4 demonstrates that colonial history predicts contemporary language effects..."

新版：
"Study 4 explores associations between colonial history and contemporary language 
effects through exploratory analyses, revealing challenges in detecting historical 
influences and identifying systematic gaps in multilingual AI evaluation."
```

### Methods Overview
已在`study4_methods_revised.md`中更新：

```markdown
旧版：
"Study 4 explores associations between colonial history and contemporary language 
effects in value representation."

新版：
"Study 4 explores associations between colonial history and contemporary language 
effects in value representation." (保持不变，因为这个表述已经足够中性)
```

## 6. 字数统计

**修订后的Study 4字数**：
- Methods: ~600 words
- Results: ~350 words
- Discussion addition: ~850 words
- **Total: ~1,800 words**

**对比原版**：
- 原版Methods: ~1,200 words (包含未实现的分析)
- 修订版更简洁，删除了未完成的承诺

## 7. 关键信息传达检查清单

修订版确保传达以下信息：

✅ **诚实性**
- [ ] 明确标记为"exploratory"
- [ ] 诚实报告不显著结果
- [ ] 不隐藏数据限制

✅ **科学严谨性**
- [ ] 提供完整统计信息（p值、效应量、CI）
- [ ] 解释null results的可能原因
- [ ] 讨论统计功效限制

✅ **方法学贡献**
- [ ] 识别了数据限制（非洲语言缺失）
- [ ] 强调高模型方差是重要发现
- [ ] 为未来研究指明方向

✅ **叙事连贯性**
- [ ] 与Study 1-3保持一致的风格
- [ ] 不削弱整体论文的说服力
- [ ] 展示研究的完整性

## 8. 审稿人可能的问题及回应

### Q1: "为什么Study 4没有显著结果？"
**回应**（已在Discussion中）：
- 高模型方差（SD>170%）
- 小样本量（拉美n=1）
- 缺少控制变量
- 可能的中介效应

### Q2: "为什么不删除Study 4？"
**回应**：
- Null results有科学价值
- 方法学限制的发现重要
- 展示研究诚信
- 为未来研究指明方向

### Q3: "数据限制是否影响结论？"
**回应**（已在Results和Discussion中）：
- 明确说明限制
- 这本身是一个发现（系统性数据缺口）
- 不影响Study 1-3的结论

### Q4: "为什么不做回归/中介分析？"
**回应**（已在Methods的Note中）：
- 需要额外数据（GDP、EF EPI等）
- 留待未来研究
- 当前分析已提供有价值的初步证据

## 9. 最终检查

在提交前，确保：

- [ ] Methods中删除了所有未完成分析的承诺
- [ ] Results中所有数值与实际分析结果一致
- [ ] Discussion中充分解释了null results
- [ ] SI图表引用正确（S7A-S7D）
- [ ] Abstract和Overview与修订版一致
- [ ] 字数符合期刊要求
- [ ] 所有统计报告格式一致

## 10. 文件清单

修订完成后，你应该有：

**主文档**：
- [ ] `paper_pnas_methods_v2.md` (已更新Study 4)
- [ ] `paper_pnas_results.md` (已添加Study 4)
- [ ] `paper_pnas_discussion.md` (已添加Study 4讨论)

**SI文档**：
- [ ] SI Methods (引用Study 4 Methods)
- [ ] SI Results (详细统计表格)
- [ ] SI Figures (S7A-S7D)

**分析文件**：
- [ ] `analysis/si/generate_figs7_colonial_history.py` (图表生成)
- [ ] `results/analysis/colonial_history/summary_statistics.txt` (统计摘要)
- [ ] `SI/figures/S7_Colonial_history/*.png` 和 `*.pdf` (图表)

## 需要帮助？

如果你需要我：
1. 直接修改 `paper_pnas_methods_v2.md` 文件
2. 创建完整的Results章节
3. 修改Discussion文件
4. 创建SI文档的Study 4部分

请告诉我！
