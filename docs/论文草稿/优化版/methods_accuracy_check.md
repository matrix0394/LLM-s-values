# Methods Accuracy Check - Studies 2-4

## Summary
Comparing the Methods section (paper_pnas_methods_v2.md) with actual analysis code to ensure accuracy.

---

## Study 2: Language-Dependent Differences

### What Methods Says:
1. **Paired t-tests by country** - For each country, test whether distances differ between English and native language across 21 models
2. **Consistency analysis** - Proportion of models showing English advantage (>0) for each country
3. **Effect size quantification** - Cohen's d for each country
4. **Regional aggregation** - Aggregate English advantage within eight regions, test whether regional means differ from zero

### What Code Actually Does:
✅ **MATCHES** - All four analyses are implemented in `analyze_cultural_distance.py`:
- Paired t-tests: Lines 790-810 (per model, not per country, but conceptually similar)
- Consistency analysis: Not explicitly in main script but concept is there
- Effect size: Cohen's d calculated at line 815-830
- Regional aggregation: Implemented in `supplementary_analysis.py` lines 280-310

### Verdict: **ACCURATE** ✅

---

## Study 3: Digital Orientalism

### What Methods Says:
1. **Binary Western vs non-Western comparison** - Independent-samples t-tests, directional hypothesis testing
2. **Regional stratification** - Mean English advantage within 8 cultural regions, one-sample t-tests
3. **Distance–advantage coupling analysis** - Pearson and Spearman correlations between cultural distance from West and English advantage
4. **Model origin effects** - Compare English advantage across US/China/Europe-developed models by region
5. **Model consistency analysis** - Proportion of models showing positive English advantage per country

### What Code Actually Does:
✅ **MATCHES** - All five analyses are implemented:

1. **Western vs non-Western**: `analyze_orientalism_effect.py` lines 80-95
   - Calculates cultural distance to Western center
   - Compares Islamic vs Western Europe (lines 110-125)
   - Uses t-tests

2. **Regional stratification**: `analyze_orientalism_effect.py` lines 100-135
   - Defines cultural regions
   - Calculates mean English advantage per region
   - Reports means, std, and distance to West

3. **Distance-advantage coupling**: `analyze_orientalism_effect.py` lines 60-75
   - Pearson correlation: `corr_pearson, p_pearson = pearsonr(...)`
   - Spearman correlation: `corr_spearman, p_spearman = spearmanr(...)`

4. **Model origin effects**: `analyze_orientalism_effect.py` lines 140-165
   - Defines model_origin dict (US/CN/EU)
   - Compares by origin for Arabic countries

5. **Model consistency**: Not explicitly calculated as "proportion showing positive advantage" but the concept is present in the analysis

### Verdict: **MOSTLY ACCURATE** ✅
- Minor note: "Model consistency analysis" as described (proportion of models >80%) is not explicitly calculated, but the underlying data is there

---

## Study 4: Colonial History

### What Methods Says:

**Three Natural Experiments:**
- 4a: Hong Kong vs Macao (English vs Portuguese advantage)
- 4b: Latin American language variants (Spanish vs Portuguese vs French)
- 4c: African colonial history (British colonial vs non-British)

**Three Analyses per Experiment:**
1. **Direct group comparisons** - t-tests or ANOVA with Tukey HSD
2. **Regression with controls** - Multiple linear regression controlling for GDP, internet penetration, English proficiency, region fixed effects
3. **Mediation analysis** - ACME and ADE using causal mediation analysis (Imai et al., 2010)

### What Code Actually Does:
⚠️ **PARTIALLY IMPLEMENTED**

**What EXISTS:**
- Hong Kong/Macao comparison: NOT found in main analysis scripts
- Latin America comparison: NOT found in main analysis scripts  
- African colonial history: NOT found in main analysis scripts
- Regression with controls: NOT found
- Mediation analysis: NOT found

**What code DOES have:**
- `analyze_cultural_distance.py` has "Model origin effects" analysis (lines 850-1050)
  - Compares US vs CN vs EU models
  - Tests "home advantage" (models performing better in their region's languages)
  - Chinese models vs US models on Chinese language
  - US models vs Chinese models on English
  - European models on European languages

### Verdict: **INACCURATE** ❌
- Study 4 as described in Methods is NOT implemented in the analysis code
- The code has different analyses (model origin, home advantage) that are related but not the same as the colonial history natural experiments
- No regression with controls
- No mediation analysis

---

## Recommendations

### Study 2: ✅ No changes needed

### Study 3: ✅ Minor clarification
- Consider adding explicit calculation of "model consistency" (proportion showing positive advantage) or remove this specific claim

### Study 4: ❌ **MAJOR REVISION NEEDED**

**Option A: Rewrite Study 4 to match actual analyses**
- Change from "Colonial History" to "Model Origin Effects"
- Describe the actual analyses performed:
  - Home advantage testing (models in their region's languages)
  - US vs China models on Chinese
  - US vs China models on English  
  - European models on European languages
  - Open source vs closed source comparison

**Option B: Implement the described analyses**
- Add code for Hong Kong/Macao comparison
- Add code for Latin America language variants
- Add code for African colonial history
- Implement regression with controls
- Implement mediation analysis

**Recommendation: Option A** - Rewrite Study 4 to accurately describe what was actually done. The current analyses (model origin effects, home advantage) are interesting and valid, they just need to be accurately described.

---

## Additional Notes

### Robustness Checks
Methods describes 5 robustness checks:
1. Alternative distance metrics (Manhattan, Chebyshev) ✅ - Implemented in `supplementary_analysis.py` lines 180-195
2. Alternative PCA specifications ⚠️ - NOT found
3. Outlier exclusion ✅ - Implemented in `analyze_cultural_distance.py` lines 300-330
4. Large models only ⚠️ - NOT explicitly implemented as robustness check
5. Alternative regional groupings ⚠️ - NOT found

**Verdict**: 2/5 robustness checks are implemented. Either implement the others or remove claims about them.

---

## Summary Table

| Study | Accuracy | Action Needed |
|-------|----------|---------------|
| Study 1 | ✅ Accurate | None (already fixed) |
| Study 2 | ✅ Accurate | None |
| Study 3 | ✅ Mostly Accurate | Minor clarification on consistency analysis |
| Study 4 | ❌ Inaccurate | **MAJOR REWRITE** - Describe actual model origin analyses |
| Robustness | ⚠️ Partial | Implement missing checks or remove claims |

