# Requirements Document

## Introduction

This document specifies requirements for improving Study 4's colonial history analysis to match the methods described in `paper_pnas_methods_v2.md`. The current implementation (`analyze_colonial_history_v3.py`) has methodological issues: (1) Experiment 4a averages Hong Kong and Macao together, causing Hong Kong's strong English advantage (+0.328) to be canceled by Macao's Portuguese disadvantage (-0.202), resulting in non-significance (p=0.6481), (2) Experiment 4c shows non-significance for African colonial effects (p=0.7254) without investigating why, and (3) visualizations in `visualize_orientalism.py` clearly show Hong Kong's large English advantage, contradicting the statistical non-significance.

The methods document specifies three natural experiments with three types of analysis (direct comparison, regression with controls, mediation analysis). The current implementation only does direct comparisons and has the averaging problem.

## Glossary

- **English Advantage**: The percentage improvement in cultural distance when using English versus native language: 100 × (Distance_native − Distance_English) / Distance_native. Positive values indicate English produces better cultural alignment.
- **Portuguese Advantage**: Analogous metric for Macao: 100 × (Distance_Chinese − Distance_Portuguese) / Distance_Chinese.
- **Experiment 4a**: Hong Kong vs Macao comparison. Tests whether Hong Kong's English advantage exceeds Macao's Portuguese advantage, reflecting English's greater global dominance.
- **Experiment 4b**: Latin American language variants. Compares English advantage across Spanish-speaking (n=11), Portuguese-speaking (Brazil, n=1), and French-speaking (Haiti, n=1) countries.
- **Experiment 4c**: African colonial history effects. Compares English advantage between African countries with British colonial history (n=8) versus without (n=3).
- **Direct Group Comparison**: Basic statistical tests (t-tests, ANOVA) comparing groups without controlling for confounds.
- **Regression Analysis**: Multiple linear regression controlling for GDP, internet penetration, English proficiency, and regional fixed effects.
- **Mediation Analysis**: Causal mediation analysis testing whether colonial effects are mediated by contemporary English usage patterns.
- **Cultural Distance**: Euclidean distance between LLM-generated and IVS PCA coordinates.

## Requirements

### Requirement 1

**User Story:** As a researcher, I want to analyze Hong Kong and Macao separately in the East Asian comparison, so that I can see each territory's distinct colonial language effect without averaging them together.

#### Acceptance Criteria

1. WHEN analyzing East Asian colonial effects THEN the system SHALL compute Hong Kong's English advantage separately from Macao's Portuguese advantage
2. WHEN comparing colonized versus non-colonized East Asian countries THEN the system SHALL compare Hong Kong's English advantage against the English advantage of non-colonized countries (China, Japan, Korea)
3. WHEN comparing colonized versus non-colonized East Asian countries THEN the system SHALL compare Macao's Portuguese advantage against the Portuguese advantage of non-colonized countries separately
4. WHEN displaying results THEN the system SHALL show both individual comparisons and explain why Hong Kong and Macao should not be averaged together
5. WHEN computing statistical significance THEN the system SHALL use appropriate tests for comparing English advantages across groups (not absolute distances)

### Requirement 2

**User Story:** As a researcher, I want to understand why the African colonial analysis shows no significant effect, so that I can use the correct analysis method or acknowledge the limitation.

#### Acceptance Criteria

1. WHEN analyzing African colonial effects THEN the system SHALL recognize that British-colonized African countries (Kenya, Nigeria, Ghana, etc.) only have `en-native` data without native language comparisons
2. WHEN British-colonized African countries lack native language data THEN the system SHALL NOT compute English advantage (which requires native language comparison)
3. WHEN analyzing African colonial effects THEN the system SHALL use an alternative approach: compare English advantage of colonized African countries with English advantage of non-colonized African countries that DO have native languages (e.g., Morocco with Arabic, Ethiopia with Amharic if available)
4. WHEN native language data is unavailable for key comparison groups THEN the system SHALL report this as a limitation and explain why the analysis cannot be performed as originally designed
5. WHEN displaying African results THEN the system SHALL clearly state the methodological constraint and suggest alternative interpretations

### Requirement 3

**User Story:** As a researcher, I want to implement the correct statistical comparison for colonial history effects, so that my analysis matches the methods document and tests the right hypothesis.

#### Acceptance Criteria

1. WHEN testing colonial history effects THEN the system SHALL compare English advantages (percentage improvements) between groups, NOT absolute cultural distances
2. WHEN comparing Hong Kong versus non-colonized East Asian countries THEN the system SHALL test whether Hong Kong's English advantage is significantly larger than the English advantage of China, Japan, and Korea
3. WHEN comparing Latin American countries THEN the system SHALL test whether English advantage varies by colonial language (Spanish vs Portuguese vs French) using ANOVA on English advantage values
4. WHEN sample sizes permit THEN the system SHALL use independent-samples t-tests to compare mean English advantages between groups
5. WHEN reporting results THEN the system SHALL clearly state that the comparison is of "English advantage" (relative improvement) not "absolute distance in English"

### Requirement 4

**User Story:** As a researcher, I want to generate visualizations that match the orientalism analysis style, so that I can clearly show colonial history effects in a way consistent with the rest of the paper.

#### Acceptance Criteria

1. WHEN visualizing East Asian colonial effects THEN the system SHALL create a bar chart similar to `visualize_orientalism.py`'s East Asia gradient showing Hong Kong, Macao, China, Japan, Korea with their English advantages
2. WHEN visualizing Latin American effects THEN the system SHALL create a grouped bar chart showing English advantage by colonial language group with error bars
3. WHEN visualizing any colonial comparison THEN the system SHALL use the same color scheme as orientalism visualizations (red for English advantage, green for native advantage)
4. WHEN displaying results THEN the system SHALL include both the visualization and statistical test results side-by-side
5. WHEN Hong Kong shows large English advantage in visualization but statistical test is marginal THEN the system SHALL explain this discrepancy (e.g., high variance, small sample size)

### Requirement 5

**User Story:** As a researcher, I want to implement the three analysis levels described in the methods document (direct comparison, regression, mediation), so that the implementation matches what was promised in the paper.

#### Acceptance Criteria

1. WHEN performing direct group comparisons THEN the system SHALL use independent-samples t-tests for Experiment 4a (Hong Kong vs Macao) and Experiment 4c (African colonial history), and one-way ANOVA with Tukey HSD post-hoc for Experiment 4b (Latin America)
2. WHEN performing regression analysis THEN the system SHALL code colonial history as binary variables (British: yes/no, French: yes/no, Portuguese: yes/no, Spanish: yes/no) and use multiple linear regression with control variables: log GDP per capita, internet penetration rate, English proficiency index (EF EPI), and geographic region fixed effects
3. WHEN performing regression analysis THEN the system SHALL report regression coefficients (β) with standard errors, t-statistics, p-values, 95% confidence intervals, R² for full model, and incremental R² contributed by colonial history variables
4. WHEN performing mediation analysis THEN the system SHALL use causal mediation analysis (Imai et al., 2010) to decompose colonial history effects into ACME (average causal mediation effect via contemporary English usage) and ADE (average direct effect), OR acknowledge this as future work if Common Crawl data is unavailable
5. WHEN reporting outcomes THEN the system SHALL report for each experiment: (i) mean English advantage per group with 95% CI, (ii) t/F-statistics and p-values with effect sizes (Cohen's d or η²), (iii) regression results if performed, (iv) mediation results if performed, (v) effect sizes for all comparisons

### Requirement 6

**User Story:** As a researcher, I want to properly handle the Experiment 4b finding that shows significance (p=0.0204), so that I can report this positive result correctly.

#### Acceptance Criteria

1. WHEN analyzing Latin American language variants THEN the system SHALL recognize that the ANOVA shows significant differences (F=3.956, p=0.0204)
2. WHEN ANOVA is significant THEN the system SHALL perform Tukey HSD post-hoc tests to identify which pairs of colonial language groups differ significantly
3. WHEN reporting Experiment 4b results THEN the system SHALL highlight that French-speaking Haiti shows significantly higher English advantage (+0.707) than Spanish-speaking countries (+0.082)
4. WHEN interpreting Experiment 4b THEN the system SHALL explain this finding in terms of differential representation in English-language training data
5. WHEN displaying Experiment 4b THEN the system SHALL create visualizations showing the gradient across colonial language groups with significance markers

### Requirement 7

**User Story:** As a researcher, I want to integrate the corrected Study 4 analysis with the existing orientalism visualizations, so that colonial history effects are shown as part of the broader geographic gradient pattern.

#### Acceptance Criteria

1. WHEN generating orientalism visualizations THEN the system SHALL annotate Hong Kong and Macao with their colonial history and show how they fit into the East Asian gradient
2. WHEN showing cultural region effects THEN the system SHALL overlay colonial history information to show how it modulates regional patterns
3. WHEN displaying the geographic gradient THEN the system SHALL highlight countries with colonial histories using distinct markers
4. WHEN presenting Study 4 results THEN the system SHALL reference the orientalism visualizations to show consistency between analyses
5. WHEN both analyses are complete THEN the system SHALL generate a summary figure showing how colonial history contributes to the overall Orientalism effect
