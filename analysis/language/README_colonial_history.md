# Colonial History Analysis (Study 4)

This directory contains the implementation of Study 4: Colonial History and Contemporary Language Effects.

## Overview

Study 4 tests whether colonial history affects contemporary LLM cultural representations through three natural experiments:

1. **Experiment 4a**: Hong Kong (British) vs Macao (Portuguese) comparison
2. **Experiment 4b**: Latin American language variants (Spanish, Portuguese, French)
3. **Experiment 4c**: African colonial history effects (with data limitations)

## Files

### Core Analysis Scripts

- **`analyze_colonial_history_v4.py`** - Main analysis script
  - Implements all three experiments
  - Generates statistical results
  - Creates visualizations
  - Run: `python analysis/language/analyze_colonial_history_v4.py`

- **`colonial_utils.py`** - Utility functions
  - `calculate_english_advantage()` - Calculate English advantage metric
  - `calculate_cultural_distance()` - Calculate Euclidean distance
  - `COLONIAL_HISTORY` - Colonial history mapping dictionary
  - Data loading and filtering functions

- **`colonial_visualizations.py`** - Visualization functions
  - `plot_east_asian_gradient()` - East Asian colonial gradient
  - `plot_latin_america_variants()` - Latin American language variants
  - `plot_hk_macao_comparison()` - Hong Kong vs Macao comparison
  - `generate_all_figures()` - Generate all figures

### SI Figure Generation

- **`../si/generate_figs7_colonial_history.py`** - SI figure generation
  - Generates publication-quality figures for Supplementary Information
  - Self-contained: computes from SI/pca data directly
  - Outputs to `SI/figures/S7_Colonial_history/`
  - Run: `python analysis/si/generate_figs7_colonial_history.py`

### Legacy Scripts (for reference)

- `analyze_colonial_history_v3.py` - Previous version (has methodological issues)
- `analyze_colonial_history_v2.py` - Earlier version
- `analyze_colonial_history.py` - Original version

## Key Improvements in v4

1. **Separate Hong Kong and Macao analysis** (no averaging)
2. **Compare English advantages** (not absolute distances)
3. **Proper handling of African data limitations**
4. **Correct statistical comparisons** (percentage improvements, not raw distances)
5. **Integration with SI figure system**

## Usage

### Quick Start

```bash
# Run complete analysis
python analysis/language/analyze_colonial_history_v4.py

# Generate SI figures only
python analysis/si/generate_figs7_colonial_history.py
```

### Output Locations

**Analysis outputs:**
- Figures: `results/analysis/colonial_history/*.png`
- Summary: `results/analysis/colonial_history/summary_statistics.txt`

**SI figures (publication-quality):**
- Figures: `SI/figures/S7_Colonial_history/*.png` and `*.pdf`

## Data Requirements

### Required Data (included in repository)

- `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv` - LLM roleplay PCA coordinates
- `SI/pca/Table_S5_IVS_PCA_coordinates.csv` - IVS ground truth coordinates
- `results/analysis/stage0_vs_stage3/english_advantage_average.csv` - Pre-computed advantages

### Optional Data (for regression analysis)

- GDP per capita data
- Internet penetration rates
- English proficiency index (EF EPI)
- Regional classifications

**Note**: Regression analysis (Task 6) and mediation analysis (Task 7) are not yet implemented due to missing control variable data.

## Methodology

### English Advantage Metric

```
English Advantage (%) = 100 × (Distance_native - Distance_english) / Distance_native
```

- **Positive values**: English produces better cultural alignment than native language
- **Negative values**: Native language produces better alignment
- **Zero**: No difference between English and native language

### Statistical Tests

- **Experiment 4a**: Independent-samples t-test (Welch's correction)
- **Experiment 4b**: One-way ANOVA with Tukey HSD post-hoc
- **Effect sizes**: Cohen's d (t-tests), eta-squared (ANOVA)
- **Confidence intervals**: 95% for all estimates

### Data Filtering

Low-quality models are excluded:
- `llama-3.2-3b-instruct`
- `qwen3-1.7b`

## Results Summary

### Experiment 4a: Hong Kong vs Macao

- **Hong Kong English advantage**: 15.84%
- **Macao Portuguese advantage**: -15.67%
- **Statistical test**: t(37.9) = 0.509, p = 0.6138 (not significant)
- **Effect size**: Cohen's d = 0.161 (negligible)

**Interpretation**: No significant difference detected, likely due to high variance across models.

### Experiment 4b: Latin American Variants

- **Spanish-speaking** (n=11): 5.43% ± 10.17%
- **Portuguese-speaking** (n=1): 3.58%
- **French-speaking** (n=1): 20.38%
- **Statistical test**: F(2, 10) = 1.035, p = 0.3905 (not significant)
- **Effect size**: η² = 0.171 (large)

**Interpretation**: No significant differences, limited by small sample sizes.

### Experiment 4c: African Colonial History

**CRITICAL LIMITATION**: British-colonized African countries (Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia) only have English language data. They lack native language data needed to calculate English advantage.

**Impact**: Cannot test the colonial hypothesis in the African context.

**Recommendation**: Acknowledge as methodological limitation. Future work should collect native language data.

## Visualizations

All visualizations use a consistent color scheme:
- **Red** (#E74C3C): Strong English advantage (>20%)
- **Orange** (#F39C12): Moderate English advantage (10-20%)
- **Green** (#27AE60): Weak English advantage (0-10%)
- **Blue** (#3498DB): Native language advantage (<0%)

### Generated Figures

1. **East Asian Colonial Gradient** - Shows Hong Kong, Macao, China, Japan, Korea
2. **Latin American Language Variants** - Compares Spanish, Portuguese, French groups
3. **Hong Kong vs Macao Comparison** - Side-by-side with distributions
4. **African Limitation Report** - Documents data limitation

## Dependencies

```python
pandas>=1.3.0
numpy>=1.20.0
scipy>=1.7.0
matplotlib>=3.4.0
statsmodels>=0.13.0  # For ANOVA post-hoc tests
```

## Troubleshooting

### Unicode Encoding Issues (Windows)

If you encounter `UnicodeEncodeError` on Windows, the script automatically uses ASCII-safe characters ([OK], [X], [!]) instead of Unicode symbols (✓, ✗, ⚠).

### Missing Data Files

Ensure you have run the prerequisite analyses:
```bash
# Generate stage0 vs stage3 comparison data
python analysis/stage0_vs_stage3_distance.py
```

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/project
python analysis/language/analyze_colonial_history_v4.py
```

## References

### Requirements Document
`.kiro/specs/study4-colonial-analysis-improvement/requirements.md`

### Design Document
`.kiro/specs/study4-colonial-analysis-improvement/design.md`

### Methods Document
`docs/论文草稿/优化版/paper_pnas_methods_v2.md`

## Future Work

1. **Regression Analysis** (Task 6)
   - Requires control variables: GDP, internet penetration, EF EPI
   - Multiple linear regression with colonial history binary variables
   - Calculate incremental R² for colonial effects

2. **Mediation Analysis** (Task 7)
   - Requires Common Crawl data for contemporary English usage
   - Causal mediation analysis (Imai et al., 2010)
   - Decompose effects into ACME and ADE

3. **Extended African Analysis**
   - Collect native language data for British-colonized countries
   - Enable proper colonial hypothesis testing in Africa

## Contact

For questions about this analysis, refer to the specification documents in `.kiro/specs/study4-colonial-analysis-improvement/`.
