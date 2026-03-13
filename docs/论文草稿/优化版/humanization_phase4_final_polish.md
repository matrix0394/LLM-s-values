# Phase 4 Humanization - Final Polish (5 Critical Fixes)

## Summary
Applied 5 final critical fixes to remove the last remaining AI traces from both English and Chinese versions. These changes eliminate mechanism explanations, prediction statements, and reframe the sample size reporting to avoid appearing to inflate numbers.

---

## All 5 Changes Applied ✅

### **Change 1: Study 3 Analysis #4 - Remove mechanism explanation**
**Location**: Study 3, Analysis section, Model origin effects
**Rationale**: "potentially reflecting differences in training data composition, curation practices, or cultural proximity" is Discussion content, not Methods

**English**:
- Before: "...to test whether models developed in different regions encode cultural knowledge differently, potentially reflecting differences in training data composition, curation practices, or cultural proximity."
- After: "For each cultural region, we compare mean English advantage between model origin groups."

**Chinese**:
- Before: "以测试在不同区域开发的模型是否以不同方式编码文化知识，可能反映训练数据组成、策展实践或文化接近性的差异。"
- After: "对于每个文化区域，我们比较模型来源组之间的平均英语优势。"

---

### **Change 2: Study 4a - Remove prediction sentence**
**Location**: Study 4, Experiment 4a
**Rationale**: "If colonial history matters, Hong Kong should show..." is a prediction/expectation, belongs in Discussion not Methods

**English**:
- Before: "If colonial history matters, Hong Kong should show stronger English advantage than Macao shows Portuguese advantage, given English's greater global dominance and likely differential representation in training data."
- After: (Deleted entire sentence)

**Chinese**:
- Before: "如果殖民历史有影响，香港应显示比澳门的葡萄牙语优势更强的英语优势，反映英语的更大全球主导地位和训练数据中的差异表征。"
- After: (Deleted entire sentence)

---

### **Change 3: Study 4b - Remove mechanism speculation**
**Location**: Study 4, Experiment 4b
**Rationale**: "potentially reflecting differential representation in English-language training data based on colonial linguistic legacies" is mechanism explanation

**English**:
- Before: "We test whether English advantage varies systematically across these groups, potentially reflecting differential representation in English-language training data based on colonial linguistic legacies."
- After: "We test whether English advantage varies systematically across these groups."

**Chinese**:
- Before: "我们测试英语优势是否在这些组间系统性变化，可能反映基于殖民语言遗产的英语训练数据中的差异表征。"
- After: "我们测试英语优势是否在这些组间系统性变化。"

---

### **Change 4: Study 3 Design - Clarify classification criteria**
**Location**: Study 3, Design section
**Rationale**: "cultural-historical criteria" is vague; "region labels" is more specific and operational

**English**:
- Before: "based on pre-specified cultural-historical criteria"
- After: "based on pre-specified region labels (SI Appendix)"

**Chinese**:
- Before: "基于预先指定的文化历史标准"
- After: "基于预先指定的区域标签（SI附录）"

---

### **Change 5: Total observations → Sample summary**
**Location**: End of Methods section
**Rationale**: Current framing (models × languages × questions × repetitions) looks like inflating numbers; reframe as evaluation units

**English**:
- Before: 
```
**Total observations:** 
- Study 1 (Intrinsic values): 23 models × 6 languages × 10 questions × 5 repetitions = 6,900 observations
- Studies 2–4 (Cultural role-play): 21 models × 66 countries × 2.1 languages (average) × 10 questions × 5 repetitions = 145,530 observations
- Total: 152,430 observations across 66 countries (representing approximately 62% of world population)
```

- After:
```
**Sample summary:**
- Study 1: 138 model-language combinations (23 models × 6 languages), each evaluated 5 times
- Studies 2–4: Approximately 2,900 model-country-language combinations (21 models × 66 countries × 2.1 languages average), each evaluated 5 times
- Each evaluation consists of responses to 10 survey items
- Coverage: 66 countries representing approximately 62% of world population
```

**Chinese**:
- Before:
```
**总观测数：** 
- 研究1（内在价值观）：23个模型 × 6种语言 × 10个问题 × 5次重复 = 6,900次观测
- 研究2-4（文化角色扮演）：21个模型 × 66个国家 × 2.1种语言（平均）× 10个问题 × 5次重复 = 145,530次观测
- 总计：152,430次观测，涵盖66个国家（代表约62%的世界人口）
```

- After:
```
**样本总结：**
- 研究1：138个模型-语言组合（23个模型 × 6种语言），每个评估5次
- 研究2-4：约2,900个模型-国家-语言组合（21个模型 × 66个国家 × 2.1种语言平均），每个评估5次
- 每次评估包含对10个调查项目的回应
- 覆盖范围：66个国家，代表约62%的世界人口
```

---

## What We Removed:

### ❌ Mechanism explanations:
- "potentially reflecting differences in training data composition, curation practices, or cultural proximity"
- "potentially reflecting differential representation in English-language training data based on colonial linguistic legacies"
- "given English's greater global dominance and likely differential representation in training data"

### ❌ Prediction statements:
- "If colonial history matters, Hong Kong should show..."

### ❌ Vague terminology:
- "cultural-historical criteria" → "region labels"

### ❌ Inflated sample size framing:
- "Total observations" counting item-level responses
- "152,430 observations" (looks like inflating)

---

## What We Kept:

### ✅ Clear operational descriptions:
- "compare mean English advantage between model origin groups"
- "test whether English advantage varies systematically"
- "based on pre-specified region labels"

### ✅ Honest sample size reporting:
- "Sample summary" (not "Total observations")
- Evaluation units (combinations) not item-level responses
- Clear structure: combinations × repetitions × items

### ✅ Appropriate transparency:
- Coverage information (66 countries, 62% population)
- Number of evaluations per combination
- Number of items per evaluation

---

## Impact:

### Before (AI-like):
- Explained mechanisms in Methods
- Made predictions about results
- Used vague criteria descriptions
- Inflated sample size appearance

### After (Human-like):
- Describes methods only
- No predictions or expectations
- Specific operational definitions
- Honest, clear sample reporting

---

## Total Humanization Changes Across All Phases: 33

- **Phase 1**: 11 changes (basic humanization)
- **Phase 2**: 8 changes (removing subtle AI traces)
- **Phase 3**: 9 changes (removing major AI traces)
- **Phase 4**: 5 changes (final polish)

---

## Key Improvements in Phase 4:

1. **Removed ALL mechanism explanations** from Methods
2. **Removed ALL prediction statements** from Methods
3. **Clarified vague terminology** (criteria → labels)
4. **Reframed sample size** to avoid inflation appearance
5. **Maintained transparency** while being honest about units

---

## Files Updated:
- ✅ `docs/论文草稿/优化版/paper_pnas_methods_v2.md` (English)
- ✅ `docs/论文草稿/优化版/paper_pnas_methods_v2_CN.md` (Chinese)

---

## Final Assessment:

Your Methods section now:
- ✅ Contains ZERO mechanism explanations
- ✅ Contains ZERO prediction statements
- ✅ Contains ZERO results-oriented language
- ✅ Uses specific, operational terminology
- ✅ Reports sample size honestly and clearly
- ✅ Maintains strict Methods-Results-Discussion separation
- ✅ Sounds like a careful human researcher wrote it

**The Methods section is now ready for PNAS submission.**
