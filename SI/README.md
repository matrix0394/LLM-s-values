# Supporting Information (SI)

This directory contains all Supporting Information materials for the study "Cultural Values in Large Language Models: A Multilingual Analysis."

## Directory Structure

```
SI/
├── README.md                    # This file
├── prompts/                     # All prompts used in experiments
├── model_responses/             # LLM response data and validity metrics
├── pca/                         # Principal Component Analysis results
└── figures/                     # Cultural map visualizations
```

## Contents Overview

| Directory | Description | Key Files |
|-----------|-------------|-----------|
| `prompts/` | Survey questions (13 languages) and system prompts for baseline and cultural imitation experiments | `questions/*.md`, `baseline_intrinsic_values/`, `imitated_contextual_values/` |
| `model_responses/` | Modal response profiles and validity summaries | Tables S1-S4 |
| `pca/` | PCA coordinates for IVS countries and LLM responses | Tables S5-S8 |
| `figures/` | Cultural map visualizations (~1,932 figures total) | Figures S1-S6, Summary |

---

# Materials and Methods 

## Data and Cultural Framework

We adopt the Inglehart–Welzel cultural map to locate both model-expressed values and country-level cultural profiles in a two-dimensional value space defined by Survival versus Self-Expression values (PC1) and Traditional versus Secular-Rational values (PC2). Ground-truth cultural coordinates for 66 countries are obtained from the Integrated Values Survey (IVS), which integrates World Values Survey Wave 7 (2017–2022) and European Values Study data, covering 109 countries and more than 90% of the world's population.

Following established practice, we use ten survey items that load strongly on the two dimensions: happiness (A008), interpersonal trust (A165), respect for authority (E018), political action (E025), importance of God (F063), attitudes toward homosexuality (F118) and abortion (F120), national pride (G006), post-materialism (Y002), and autonomy (Y003). These items define a fixed cultural coordinate system. Model-generated responses are projected onto this established space for all analyses.

## Models

We evaluate 23 large language models (see SI Appendix, Table S1 for complete list) developed in the United States, China, and Europe, spanning both small (<10B parameters) and large (≥10B) model classes. Models include GPT-4o, Claude-4.5-Sonnet, Gemini-2.0-Flash, DeepSeek-V3,Mistral Nemo, and others, selected to maximize diversity in origin, architecture, and scale. Models are accessed via API endpoints between February and December 2025 using a fixed temperature of 0.1.

All 23 models are included in the intrinsic-value condition. For the cultural imitation condition, two small models are excluded due to systematically low response quality, defined as mean cultural distances exceeding three standard deviations from the IVS reference distribution, resulting in 21 models for cultural role-play analyses.

## Experimental Design

Two experimental conditions are implemented.

**Intrinsic-value condition.** Models answer the ten survey questions without being assigned any national or cultural identity. To examine language dependence, the questionnaire is administered in the six official United Nations languages: Arabic, Chinese, English, French, Russian, and Spanish. Responses in this condition are interpreted as each model's default cultural orientation.

**Cultural imitation condition.** Models are prompted to respond as a typical adult citizen of a specified country using a standardized system prompt (see SI Appendix for full prompts in all languages). Sixty-six countries are included, selected to maximize geographic and cultural diversity while ensuring the availability of IVS reference data. Countries are grouped into eight cultural regions following established classifications.

For non–English-native countries, surveys are administered both in English and in the country's official language(s). Languages are selected based on official language status and speaker population; multilingual countries are evaluated separately for each major official language (e.g., Canada: English and French; Switzerland: German, French, Italian). This setup allows within-country comparisons of prompt language while holding country identity constant.

For all model–language–condition combinations, each questionnaire is administered five times. The modal response across repetitions is used as the final answer, preserving the ordinal structure of survey items while reducing stochastic variation. For list-type questions, responses are normalized by sorting prior to mode calculation to ensure order invariance. Across all conditions, valid response rates exceed 95%.

## Response Validation and Quality Control

Responses are subject to multiple quality control procedures. All outputs are first validated against strict format requirements using language-specific parsers. Single-choice items must return a single integer within the allowed range, and multi-choice items must satisfy predefined cardinality constraints. Responses containing explanatory text or invalid values are rejected.

If a response fails validation, the question is reissued up to three times with progressively more explicit format instructions. Responses that fail all retries are marked invalid. Following IVS standards, entities are retained only if they provide valid answers to at least six of the ten items.

Certain models require additional handling. Models that generate internal reasoning are instructed to suppress reasoning and return numeric answers only. Models with higher latency are assigned extended timeouts. All models are queried using identical temperature settings to minimize stochastic variation.

## Cultural Scoring and Dimensionality Reduction

Validated modal responses are assembled into a response matrix. For the post-materialism item (Y002), responses are converted to a three-level materialism score following standard coding rules. For the autonomy item (Y003), selected traits are aggregated into a traditional–secular index by contrasting traditional and secular-rational indicators.

Dimensionality reduction is performed using probabilistic principal component analysis (PPCA) to accommodate missing values. A fixed PPCA model is trained on IVS ground-truth data and then applied to all model-generated responses without refitting, ensuring a common coordinate system across conditions. Varimax rotation is applied to enhance interpretability while preserving orthogonality. Model-derived component scores are linearly rescaled to align with IVS coordinates using regression-based transformations.

Cultural alignment is quantified as the Euclidean distance between model-derived coordinates and the corresponding IVS country coordinates. Smaller distances indicate more accurate cultural representation. For non–English-native countries, an English advantage metric is computed as the relative reduction in distance under English-language prompting compared with native-language prompting.

## Statistical Analysis

Language effects are assessed using paired tests, pairing observations by model. Regional patterns are examined by aggregating results within eight cultural regions. Results are robust to alternative test statistics and outlier definitions.

---

## Table Index

| Table | Location | Description |
|-------|----------|-------------|
| S1 | `model_responses/baseline_intrinsic_values/` | Baseline modal response profiles (23 models) |
| S2 | `model_responses/baseline_intrinsic_values/` | Baseline validity summary |
| S3 | `model_responses/imitated_contextual_values/` | Cultural imitation modal response profiles (21 models) |
| S4 | `model_responses/imitated_contextual_values/` | Cultural imitation validity summary |
| S5 | `pca/` | IVS/WVS country PCA coordinates (66 countries) |
| S6 | `pca/` | LLM baseline PCA coordinates |
| S7 | `pca/` | LLM cultural imitation PCA coordinates |
| S8 | `pca/` | PCA component summary |

## Figure Index

| Figure | Location | Description | Count |
|--------|----------|-------------|-------|
| S1 | `figures/S1_IVS_cultural_map/` | IVS reference cultural map | 1 |
| S2 | `figures/S2_Baseline_intrinsic_values/` | LLM baseline responses (6 UN languages) | 24 |
| S3 | `figures/S3_Imitated_contextual_values/` | LLM cultural imitation responses (66 countries × 13 languages) | ~1,889 |
| S4 | `figures/S4_Model_and_response_analysis/` | Model behavior and performance analysis | 7 |
| S5 | `figures/S5_English_advantage_and_orientalism/` | English advantage and Othering analysis | 4 |
| S6 | `figures/S6_East_Asia_analysis/` | East Asia focused analysis | 3 |
| Summary | `figures/summary/` | Statistical overview figures | 4 |

## Cultural Dimensions

All analyses are based on the Inglehart-Welzel cultural map framework:

| Dimension | Axis | Description |
|-----------|------|-------------|
| Survival vs. Self-Expression | PC1 (X-axis) | Priority on economic security vs. quality of life and tolerance |
| Traditional vs. Secular-Rational | PC2 (Y-axis) | Emphasis on religion, authority, and traditional family values |

## Survey Questions

The ten World Values Survey items used in this study:

| Code | Question | Dimension |
|------|----------|-----------|
| A008 | Happiness | Self-Expression |
| A165 | Interpersonal trust | Self-Expression |
| E018 | Respect for authority | Traditional |
| E025 | Political action | Self-Expression |
| F063 | Importance of God | Traditional |
| F118 | Attitudes toward homosexuality | Self-Expression |
| F120 | Attitudes toward abortion | Self-Expression |
| G006 | National pride | Traditional |
| Y002 | Post-materialism | Self-Expression |
| Y003 | Autonomy | Secular-Rational |

Full question text in all 13 languages available in `prompts/questions/`.

## Data Sources

- **World Values Survey (WVS) Wave 7** (2017–2022)
- **European Values Study (EVS)**
- **Integrated Values Survey (IVS)** - Combined WVS and EVS data
- **Large Language Models**: 23 models for baseline, 21 models for cultural imitation
  - US-based: GPT-4o, Claude-4.5-Sonnet, Gemini-2.0-Flash, Llama-3.1, Mistral Nemo
  - China-based: DeepSeek-V3, Qwen-2.5, GLM-4
  - Europe-based: Mistral models

## Languages Covered

**Baseline condition (6 UN official languages):**
- Arabic, Chinese, English, French, Russian, Spanish

**Cultural imitation condition (13 languages):**
- Arabic, Chinese (Simplified), English, French, German, Hindi, Italian, Japanese, Korean, Portuguese, Russian, Spanish, Turkish

## Countries and Regions

**66 countries grouped into 8 cultural regions:**

1. **Western Europe**: France, Germany, Netherlands, Switzerland, UK, etc.
2. **Eastern Europe**: Poland, Russia, Ukraine, etc.
3. **Latin America**: Argentina, Brazil, Chile, Mexico, etc.
4. **Middle East & North Africa**: Egypt, Iran, Iraq, Turkey, etc.
5. **Sub-Saharan Africa**: Ethiopia, Ghana, Kenya, Nigeria, South Africa, etc.
6. **South Asia**: Bangladesh, India, Pakistan
7. **East Asia**: China, Japan, South Korea, Taiwan
8. **Southeast Asia**: Indonesia, Malaysia, Philippines, Thailand, Vietnam

Full country list with language assignments available in `config/` directory.

## Notes

- All prompts are reproduced exactly as used in experiments
- Raw interview data available in `data/` directory (not included in SI for size reasons)
- Analysis scripts available in `analysis/` directory
- Data collection period: February–December 2025
- Temperature setting: 0.1 (fixed across all models)
- Repetitions: 5 per model-language-country combination
- Response aggregation: Modal response (mode) across 5 repetitions

## Contact

For questions about the data or methods, please refer to the main manuscript or contact the corresponding author.
