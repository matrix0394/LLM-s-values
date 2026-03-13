# Study 4 论文写作建议

基于实际分析结果（2026-01-23）

## 实际结果总结

### Experiment 4a: Hong Kong vs Macao
- **Hong Kong English advantage**: 15.84%
- **Macao Portuguese advantage**: -15.67%
- **统计检验**: t(37.9) = 0.509, **p = 0.6138** (不显著)
- **效应量**: Cohen's d = 0.161 (negligible)
- **问题**: 高方差（HK SD=179.23%, Macao SD=170.37%）

### Experiment 4b: Latin American Language Variants
- **Spanish** (n=11): 5.43% ± 10.17%
- **Portuguese** (n=1): 3.58%
- **French** (n=1): 20.38%
- **统计检验**: F(2, 10) = 1.035, **p = 0.3905** (不显著)
- **效应量**: η² = 0.171 (large effect size但不显著)
- **问题**: 样本量太小（Portuguese n=1, French n=1）

### Experiment 4c: African Colonial History
- **CRITICAL LIMITATION**: 所有英国殖民的非洲国家只有英语数据，缺少本地语言数据
- **无法计算English advantage**（需要native vs English对比）
- **无法进行原设计的分析**

### 回归分析和中介分析
- **未实现**：缺少控制变量数据（GDP、互联网普及率、EF EPI等）

---

## 写作策略建议

### 🎯 推荐方案：诚实报告 + 重新框架

**核心思路**：
1. 承认殖民历史效应**难以检测**，但这本身就是一个有价值的发现
2. 重新框架为"探索性分析"而非"确证性检验"
3. 强调方法学挑战和未来研究方向

---

## 具体写作建议

### 1. Methods部分修改

**当前问题**：Methods写得太确定，承诺了三层分析（直接对比、回归、中介），但实际只完成了直接对比且结果不显著。

**修改建议**：

#### Option A: 简化为探索性分析（推荐）

```markdown
## Study 4. Colonial History and Contemporary Language Effects (Exploratory)

**Research question.** Are contemporary language effects in LLM value representation 
associated with historical colonial relationships?

**Design.** We conduct exploratory analyses to test whether colonial history predicts 
contemporary language effects using three natural experiments:

*Experiment 4a: Hong Kong vs Macao comparison.* We compare English advantage in 
Hong Kong (British colony 1842–1997) with Portuguese advantage in Macao (Portuguese 
colony 1557–1999). Both are Special Administrative Regions of China with similar 
political status, economic development, geographic proximity, and ethnic composition, 
but differ in colonial history. Portuguese advantage is computed analogously as:

Portuguese Advantage (%) = 100 × (Distance_Chinese − Distance_Portuguese) / Distance_Chinese

We test whether Hong Kong's English advantage exceeds Macao's Portuguese advantage, 
which would reflect English's greater global dominance in training data.

*Experiment 4b: Latin American language variants.* We compare English advantage 
across Latin American countries with different colonial languages: Spanish-speaking 
(n=11), Portuguese-speaking (Brazil, n=1), and French-speaking (Haiti, n=1). We 
test whether English advantage varies systematically across these groups using 
one-way ANOVA.

*Experiment 4c: African colonial history.* We attempted to compare English advantage 
between African countries with and without British colonial history. However, we 
discovered that British-colonized African countries in our dataset only have English 
language data, lacking native language comparisons needed to calculate English 
advantage. This data limitation prevented the planned analysis and is discussed as 
a methodological constraint.

**Analysis.** For Experiments 4a and 4b, we compare English advantage (or colonial 
language advantage) between groups using independent-samples t-tests (4a) and 
one-way ANOVA (4b). We report means, standard errors, 95% confidence intervals, 
test statistics, p-values, and effect sizes (Cohen's d or η²). For Experiment 4c, 
we document the data limitation and discuss implications for future research.

**Outcome.** We report mean advantages for each group with 95% CIs, test statistics, 
p-values, and effect sizes. We interpret results in light of statistical power 
limitations and high variance across models.
```

**关键改动**：
- 标题加上"(Exploratory)"
- 删除回归和中介分析的承诺
- 明确说明4c的数据限制
- 降低语气，从"test causal hypotheses"改为"exploratory analyses"

---

### 2. Results部分写作

**策略**：诚实报告结果，强调方法学挑战

```markdown
## Study 4. Colonial History and Contemporary Language Effects

We conducted exploratory analyses to test whether historical colonial relationships 
predict contemporary language effects in LLM cultural representation. Despite 
theoretically motivated hypotheses, we found limited evidence for systematic 
colonial history effects, highlighting the challenges of detecting historical 
influences in contemporary AI systems.

### Experiment 4a: Hong Kong vs Macao Comparison

We compared English advantage in Hong Kong (British colony 1842–1997) with 
Portuguese advantage in Macao (Portuguese colony 1557–1999). Hong Kong showed 
a positive English advantage (M = 15.84%, 95% CI [−62.08, 93.76]), indicating 
better alignment under English than Chinese prompting on average. In contrast, 
Macao showed a negative Portuguese advantage (M = −15.67%, 95% CI [−90.35, 59.01]), 
indicating better alignment under Chinese than Portuguese prompting.

However, the difference between Hong Kong and Macao was not statistically 
significant (t(37.9) = 0.509, p = 0.614, Cohen's d = 0.161). The large confidence 
intervals and negligible effect size reflect substantial variance across models 
(Hong Kong SD = 179.23%; Macao SD = 170.37%), with individual models showing 
highly inconsistent patterns. This high variance prevented detection of systematic 
colonial language effects despite the theoretically motivated comparison.

### Experiment 4b: Latin American Language Variants

We compared English advantage across Latin American countries with different 
colonial languages: Spanish-speaking countries (n = 11, M = 5.43%, SD = 10.17%), 
Portuguese-speaking Brazil (M = 3.58%), and French-speaking Haiti (M = 20.38%). 
One-way ANOVA revealed no significant differences across groups (F(2, 10) = 1.035, 
p = 0.391, η² = 0.171). Despite a large effect size (η² = 0.171), the small 
sample sizes for Portuguese (n = 1) and French (n = 1) countries limited 
statistical power to detect differences.

### Experiment 4c: African Colonial History (Data Limitation)

We attempted to compare English advantage between African countries with and 
without British colonial history. However, we discovered that all British-colonized 
African countries in our dataset (Kenya, Nigeria, Ghana, South Africa, Zimbabwe, 
Zambia) only have English language data, lacking native language comparisons 
(Swahili, Yoruba, Akan, Zulu, Shona, Bemba) needed to calculate English advantage.

This data limitation reflects a systematic gap in multilingual AI evaluation: 
countries where English is an official language due to colonial history are often 
evaluated only in English, preventing assessment of native language representation. 
This prevented the planned analysis and highlights the need for more comprehensive 
multilingual evaluation datasets that include native languages of formerly 
colonized regions.

### Summary

Our exploratory analyses found limited evidence for systematic colonial history 
effects on contemporary language representation in LLMs. The null findings may 
reflect: (1) genuine absence of colonial legacy effects in training data, (2) 
high variance across models masking systematic patterns, (3) insufficient 
statistical power due to small sample sizes, or (4) colonial effects being 
mediated by contemporary factors (e.g., current English usage) that we could 
not control for. Future research with larger model samples, control variables 
for contemporary linguistic practices, and more comprehensive multilingual 
datasets may be better positioned to detect colonial history effects.
```

**关键特点**：
- 诚实报告不显著结果
- 解释为什么不显著（高方差、小样本）
- 明确说明数据限制
- 提供合理的替代解释
- 指出未来研究方向

---

### 3. Discussion部分

**在Discussion中进一步讨论**：

```markdown
### Challenges in Detecting Colonial History Effects

Study 4's exploratory analyses revealed substantial challenges in detecting 
historical colonial influences on contemporary AI systems. Despite theoretically 
motivated natural experiments comparing Hong Kong vs Macao and Latin American 
countries with different colonial languages, we found no significant differences 
in language effects.

Several factors may explain these null findings. First, high variance across 
models (SDs exceeding 170% in some cases) suggests that individual models encode 
cultural knowledge in highly idiosyncratic ways, potentially reflecting differences 
in training data composition, curation practices, and model architectures. This 
heterogeneity may mask systematic patterns that exist at the training data level 
but are not consistently reflected across models.

Second, colonial history effects may be mediated by contemporary factors we could 
not control for, such as current English usage patterns, internet content 
distribution, and economic integration with English-speaking countries. Without 
data on these mediating variables, we cannot distinguish between direct colonial 
legacy effects and effects explained by current linguistic and economic practices.

Third, the data limitation we encountered in Experiment 4c—British-colonized 
African countries lacking native language evaluations—highlights a systematic 
gap in multilingual AI evaluation. Countries where English is an official language 
due to colonial history are often evaluated only in English, creating a blind 
spot for assessing native language representation. This reflects broader challenges 
in multilingual AI research, where language availability in evaluation datasets 
is itself shaped by historical power dynamics.

These findings underscore the complexity of tracing historical influences through 
contemporary AI systems and highlight the need for: (1) larger model samples to 
overcome high variance, (2) control variables for contemporary linguistic and 
economic factors, (3) more comprehensive multilingual evaluation datasets including 
native languages of formerly colonized regions, and (4) alternative methodologies 
such as training data analysis to directly examine how colonial histories are 
encoded in pre-training corpora.
```

---

## 4. SI部分

**在SI中提供完整的技术细节**：

- 完整的统计表格（所有三个实验）
- 数据限制的详细说明
- 模型级别的结果（显示高方差）
- 敏感性分析（如果有的话）

**SI图表**（已生成）：
- S7A: East Asian colonial gradient
- S7B: Hong Kong vs Macao comparison  
- S7C: Latin American language variants
- S7D: African data limitation report

---

## 5. 关键信息传达

### 要传达的核心信息：

✅ **我们进行了严谨的探索性分析**
✅ **我们诚实报告了null results**
✅ **我们识别了重要的方法学限制**
✅ **我们为未来研究指明了方向**

### 避免的陷阱：

❌ 不要过度解读不显著的结果
❌ 不要隐藏数据限制
❌ 不要承诺未完成的分析
❌ 不要让Study 4削弱整篇论文

---

## 6. 整体论文结构建议

**如果担心Study 4削弱论文**，可以考虑：

### Option 1: 保留但降级
- 将Study 4作为"exploratory"或"supplementary"分析
- 在主文中简短报告，详细内容放SI
- 强调这是初步探索，需要更多研究

### Option 2: 完全移到SI
- 主文只保留Study 1-3（都有显著发现）
- Study 4作为SI的补充分析
- 在Discussion中简要提及

### Option 3: 重新框架为方法学贡献
- 强调我们发现了数据限制（4c）
- 强调高模型方差是一个重要发现
- 将null results作为对领域的贡献

---

## 我的最终推荐

**推荐Option 1: 保留但降级 + 诚实报告**

**理由**：
1. 诚实报告null results是科学诚信的体现
2. 方法学限制的发现本身有价值
3. 为未来研究指明方向
4. 不会严重削弱Study 1-3的强结果

**具体操作**：
1. Methods中简化Study 4，标记为"exploratory"
2. Results中诚实报告，强调方法学挑战
3. Discussion中深入讨论为什么难以检测
4. SI中提供完整技术细节和图表

**预期效果**：
- 展示研究的完整性和诚信
- 不会因为null results被拒稿（如果方法严谨）
- 为领域贡献方法学见解
- 保持论文的整体叙事连贯性

---

## 需要你决定的问题

1. **是否保留Study 4在主文中？**
   - [ ] 是，作为exploratory analysis
   - [ ] 否，移到SI

2. **如果保留，采用哪种框架？**
   - [ ] 诚实报告null results + 方法学讨论（推荐）
   - [ ] 只报告4a，删除4b和4c
   - [ ] 其他方案

3. **是否需要我帮你重写Methods和Results的Study 4部分？**
   - [ ] 是，请帮我重写
   - [ ] 否，我自己改

请告诉我你的选择，我可以帮你完成具体的写作！
