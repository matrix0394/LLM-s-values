# Methods Data Errors - Comprehensive Fix List

## Critical Data Errors Identified

### 1. Population Coverage Contradiction (62% vs 90%)
**Location**: Common Framework + Total observations
- Common Framework says: "66-country subset represents approximately 62% of world population" ✓
- Total observations says: "66 countries representing approximately 90% of world population" ✗

**Fix**: Delete "90%" from Total observations section. The 90% refers to IVS's full 109-country dataset, not our 66-country subset.

---

### 2. Cultural Region n Values Don't Sum to 66
**Location**: Study 2 Design section
- Protestant Europe: n=8
- Catholic Europe: n=16
- English-Speaking: n=6
- Orthodox Europe: n=14
- Latin America: n=16
- African-Islamic: n=25
- Confucian: n=7
- West & South Asia: n=16
- **Total = 108** (impossible for 66-country subset)

**Fix**: Remove all n values from the 8-region list in Study 2. Add note: "Regional classifications detailed in SI Appendix."

---

### 3. English-Speaking Countries: 21 vs 6
**Location**: Study 2 Design
- First mention: "English-native countries (n=21)"
- Regional classification: "English-Speaking (n=6)"

**Explanation**: 
- n=21 refers to countries where English is A major official language (used for questionnaire)
- n=6 refers to the "Anglosphere" cultural region (UK, US, Canada, Australia, NZ, South Africa)

**Fix**: Clarify the distinction or remove the n=6 from regional list.

---

### 4. Western/Non-Western n Values Conflict with 8-Region n Values
**Location**: Study 3 Design
- Catholic Europe: n=15 in Western list, but n=16 in 8-region list
- African-Islamic: n=20 in Non-Western list, but n=25 in 8-region list
- Orthodox Europe: n=4 in Non-Western list, but n=14 in 8-region list
- Confucian: n=6 in Non-Western list, but n=7 in 8-region list
- West & South Asia: n=10 in Non-Western list, but n=16 in 8-region list

**Explanation**: The 8-region classification includes ALL countries in the full IVS dataset (109 countries), while Western/Non-Western lists only include the 66-country subset used in this study.

**Fix**: Remove n values from 8-region list. Keep n values in Western/Non-Western lists (these are correct for the 66-country subset).

---

### 5. Study 4a Model Count: 20 vs 21
**Location**: Study 4a Analysis
- Says: "n = 20 models per region after excluding two low-quality models"
- Should be: 21 models (23 total - 2 excluded = 21)

**Possible explanations**:
- One model doesn't support Portuguese or Traditional Chinese?
- Additional exclusion for this specific experiment?

**Fix**: Need to verify actual data. If truly 20, explain why. If 21, correct the number.

---

### 6. Study 2 English Advantage Definition vs Statistical Test Mismatch
**Location**: Study 2 Analysis
- Definition says: "Distance_native and Distance_English are mean Euclidean distances... across all 21 models"
- Then says: "paired t-tests by country... pairing by model"

**Problem**: Can't do paired t-test on aggregated means. Need model-level differences.

**Fix**: Rewrite to clarify:
1. First compute advantage for each model: ΔD_m = D_m,native - D_m,English
2. Then do paired t-test on ΔD_m across 21 models
3. Report country-level advantage as mean(ΔD_m)

---

### 7. Cohen's d Formula Wrong for Paired Design
**Location**: Study 2 Analysis
- Current: d = (M_native - M_English) / SD_pooled (independent samples formula)
- Should be: d = mean(ΔD) / SD(ΔD) (paired formula)

**Fix**: Change to paired Cohen's d formula.

---

### 8. "Valid Response Rates Exceed 95%" is a Result, Not a Method
**Location**: Study 1 Design
- This is an empirical result that should be in Results or SI, not Methods

**Fix**: Either delete or change to "We track validity rates and report them in SI Appendix."

---

### 9. Model Origin Counts May Be Wrong
**Location**: Common Framework
- Says: US (n=10), China (n=8), Europe (n=5)
- Need to verify against actual model list

**From llm_models.json count**:
- US: GPT-4o, GPT-4o-mini, Claude 3.7, GPT-5.1, Claude 4.5, Gemini 3 Pro, Llama 3.3, Grok 4.1, Phi-3-mini, Llama-3.2-3B, gemma-3-4B, Gemini 2.5 Flash, Gemini 2.5 Pro = 13 models
- China: DeepSeek V3, Kimi-K2, Qwen3-1.7B, DeepSeek V3.1, Qwen3-Max, Qwen QwQ 32B, GLM-4.6, Doubao = 8 models ✓
- Europe: Mistral Nemo, Mistral-Medium-3.1 = 2 models

**Fix**: Correct to US (n=13), China (n=8), Europe (n=2). Or verify against SI Table S1.

---

### 10. Total Observations Calculation Unclear
**Location**: End of Methods
- Uses "2.1 languages (average)" - opaque
- Claims "90% of world population" - wrong (should be 62% for 66-country subset)

**Fix**: Either:
- Option A: Delete entire Total observations paragraph
- Option B: Rewrite with transparent calculation

---

## Summary of Required Actions

1. ✅ Fix population coverage (delete 90% from Total observations)
2. ✅ Remove n values from 8-region list in Study 2
3. ✅ Clarify English-speaking country definition (21 vs 6)
4. ✅ Keep Western/Non-Western n values, remove 8-region n values
5. ❓ Verify Study 4a model count (20 vs 21)
6. ✅ Fix English advantage definition and statistical test description
7. ✅ Fix Cohen's d formula to paired design
8. ✅ Remove or reframe "95% valid response rate"
9. ✅ Verify and correct model origin counts
10. ✅ Fix or delete Total observations paragraph

---

## Priority

**Must fix immediately** (data contradictions):
- Items 1, 2, 3, 4, 6, 7, 9, 10

**Need verification** (may be correct):
- Item 5 (Study 4a model count)

**Style/placement issues**:
- Item 8 (valid response rate)
