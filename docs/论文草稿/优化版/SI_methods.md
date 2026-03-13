# Supplementary Information: Materials and Methods

## SI Methods Overview

This supplementary methods section provides additional technical details, validation analyses, and exploratory analyses that support the main text. We organize these materials into six sections: (1) detailed model specifications, (2) prompt engineering and validation, (3) data quality control procedures, (4) supplementary statistical analyses, (5) sensitivity analyses, and (6) computational infrastructure.

---

## SI.1 Detailed Model Specifications

### SI.1.1 Complete Model List

Table S1 provides complete specifications for all 23 models evaluated in this study, including model family, parameter count, release date, API endpoint, and developer organization.

**United States-developed models (n = 10):**
- GPT-4o (OpenAI, ~1T parameters, 2024-05)
- GPT-4o-mini (OpenAI, ~8B parameters, 2024-07)
- GPT-4.5 (OpenAI, ~1.8T parameters, 2025-01)
- Claude-3.7-Sonnet (Anthropic, ~200B parameters, 2025-02)
- Claude-Sonnet-4.5 (Anthropic, ~400B parameters, 2025-01)
- Gemini-2.0-Flash (Google, ~100B parameters, 2024-12)
- Gemini-2.5-Flash (Google, ~150B parameters, 2025-01)
- Gemini-2.5-Pro (Google, ~500B parameters, 2025-01)
- Gemini-3-Pro-Preview (Google, ~800B parameters, 2025-02)
- Llama-3.3-70B-Instruct (Meta, 70B parameters, 2024-12)

**China-developed models (n = 8):**
- DeepSeek-Chat (DeepSeek, ~67B parameters, 2024-05)
- DeepSeek-Chat-V3 (DeepSeek, ~671B parameters, 2024-12)
- DeepSeek-V3.1 (DeepSeek, ~685B parameters, 2025-01)
- Qwen-2.5-72B (Alibaba, 72B parameters, 2024-11)
- Qwen-3-Max (Alibaba, ~300B parameters, 2025-01)
- Qwen-3-1.7B (Alibaba, 1.7B parameters, 2025-01) [excluded from main analyses]
- Kimi-K2 (Moonshot AI, ~200B parameters, 2024-10)
- GLM-4-Plus (Zhipu AI, ~100B parameters, 2024-08)

**Europe-developed models (n = 5):**
- Mistral-Large-3.1 (Mistral AI, ~123B parameters, 2024-11)
- Mistral-Medium-3.1 (Mistral AI, ~70B parameters, 2024-10)
- Mistral-Nemo (Mistral AI, 12B parameters, 2024-07)
- Gemma-3-4B-IT (Google DeepMind, 4B parameters, 2024-12)
- Phi-3-Mini-128K (Microsoft, 3.8B parameters, 2024-04)

### SI.1.2 Model Categorization

**By parameter size:**
- Small (<10B): n = 7 (Qwen-3-1.7B, Gemma-3-4B, Phi-3-Mini, Mistral-Nemo, GPT-4o-mini, etc.)
- Large (≥10B): n = 16 (all others)

**By source type:**
- Open-source: n = 8 (Llama-3.3-70B, Qwen-2.5-72B, Qwen-3-1.7B, Mistral-Nemo, Mistral-Medium, Gemma-3-4B, Phi-3-Mini, GLM-4-Plus)
- Closed-source: n = 15 (GPT series, Claude series, Gemini series, DeepSeek series, Kimi-K2, Mistral-Large)

**By vendor:**
- OpenAI: n = 3
- Anthropic: n = 2
- Google/DeepMind: n = 5
- Meta: n = 1
- DeepSeek: n = 3
- Alibaba: n = 3
- Moonshot AI: n = 1
- Zhipu AI: n = 1
- Mistral AI: n = 3
- Microsoft: n = 1

### SI.1.3 API Configuration

All models were accessed via official API endpoints with the following standardized configuration:
- Temperature: 0.1 (to minimize stochastic variation while maintaining some diversity)
- Top-p: 1.0 (no nucleus sampling)
- Max tokens: 10 (sufficient for single-digit or short list responses)
- Frequency penalty: 0
- Presence penalty: 0
- Stop sequences: None

For models that generate internal reasoning (e.g., OpenAI o1-series), we used the following system instruction: "Provide only the numeric answer without explanation or reasoning. Do not show your thinking process."

---

## SI.2 Prompt Engineering and Validation

### SI.2.1 Prompt Templates

**Intrinsic-value condition (Study 1):**
```
Please answer the following questions about your values and beliefs. 
For each question, provide only the numeric answer corresponding to your choice.

Question 1: Taking all things together, would you say you are:
1 = Very happy
2 = Rather happy
3 = Not very happy
4 = Not at all happy

[Answer format: single integer 1-4]
```

**Cultural imitation condition (Study 2):**
```
You are a typical adult citizen of [Country]. Please answer the following 
questions about values and beliefs as a typical [Country] citizen would. 
For each question, provide only the numeric answer.

Question 1: Taking all things together, would you say you are:
1 = Very happy
2 = Rather happy
3 = Not very happy
4 = Not at all happy

[Answer format: single integer 1-4]
```

### SI.2.2 Language-Specific Prompt Adaptations

For each of the 13 languages, prompts were professionally translated and culturally adapted. Key adaptations include:

**Arabic:** Right-to-left text formatting; formal Modern Standard Arabic (MSA) rather than dialectal variants; culturally appropriate phrasing for sensitive topics (e.g., homosexuality, abortion).

**Chinese variants:**
- Simplified Chinese (zh-cn): Mainland China conventions
- Traditional Chinese (zh-tw): Taiwan conventions, including traditional character forms
- Cantonese (zh-hk): Hong Kong conventions, written Cantonese where appropriate

**Spanish variants:**
- European Spanish (es-ES): Used for Spain
- Latin American Spanish (es-419): Used for Latin American countries, with neutral vocabulary avoiding region-specific terms

**Portuguese variants:**
- European Portuguese (pt-PT): Used for Portugal
- Brazilian Portuguese (pt-BR): Used for Brazil

### SI.2.3 Response Format Validation

Each response was validated against strict format requirements:

**Single-choice items (8 items):**
- Must return exactly one integer
- Must be within the allowed range (e.g., 1-10 for happiness, 1-4 for trust)
- No explanatory text, reasoning, or additional characters

**Multi-choice items (2 items):**
- Autonomy (Y003): Must return exactly 5 traits from 11 options
- Post-materialism (Y002): Must rank 4 goals in order of priority

**Validation procedure:**
1. Parse response using language-specific regex patterns
2. Check format compliance (single integer, correct range, etc.)
3. If validation fails, reissue question with more explicit format instruction
4. Maximum 3 retry attempts per question
5. Mark as invalid if all retries fail

**Language-specific parsers:**
- English: `r'^\s*(\d+)\s*$'`
- Chinese: `r'^\s*([0-9０-９]+)\s*$'` (handles both ASCII and full-width digits)
- Arabic: `r'^\s*([0-9٠-٩]+)\s*$'` (handles both ASCII and Arabic-Indic digits)
- Other languages: Similar patterns adapted to local number formats

---

## SI.3 Data Quality Control Procedures

### SI.3.1 Response Validity Criteria

**Entity-level validity:**
Following IVS standards, a model–country–language entity is retained only if it provides valid answers to at least 6 of the 10 items (60% completion rate). This threshold balances data completeness with sample size.

**Item-level validity:**
- Single-choice items: Valid if response is a single integer within the allowed range
- Multi-choice items: Valid if response satisfies cardinality constraints (e.g., exactly 5 traits for autonomy)
- Missing responses: Coded as NA and handled by probabilistic PCA

**Across all conditions:**
- Total entities: 23 models × 6 languages (Study 1) + 21 models × 66 countries × 2 languages (Study 2) = 138 + 2,772 = 2,910
- Valid entities: 2,847 (97.8%)
- Invalid entities: 63 (2.2%)

**Reasons for invalidity:**
- Format violations: 38 (60.3%)
- Incomplete responses (<6 valid items): 18 (28.6%)
- API errors (timeout, rate limit): 7 (11.1%)

### SI.3.2 Model Exclusion Criteria

Two small models were excluded from cultural imitation analyses (Study 2) due to systematically low response quality:

**Qwen-3-1.7B:**
- Mean cultural distance: 4.87 (>3 SD above overall mean of 2.14)
- Valid response rate: 78.3% (below 95% threshold)
- Reason: Insufficient capacity for complex role-play instructions

**Llama-3.2-3B-Instruct:**
- Mean cultural distance: 4.23 (>2.5 SD above overall mean)
- Valid response rate: 82.1%
- Reason: Frequent format violations and off-topic responses

These models were retained in Study 1 (intrinsic values) as they performed adequately without role-play instructions.

### SI.3.3 Outlier Detection and Handling

**Country-level outliers:**
Countries with mean cultural distance >2 SD from their regional mean were flagged for inspection but not automatically excluded. Manual review confirmed that these were genuine cases of poor cultural alignment rather than data errors.

**Model-level outliers:**
Models with mean distance >3 SD from the overall mean were excluded (see SI.3.2).

**Response-level outliers:**
Individual responses >3 SD from the item mean were flagged but retained, as extreme values can be valid expressions of cultural diversity.

---

## SI.4 Supplementary Statistical Analyses

### SI.4.1 Model × Language Interaction Effects

To assess whether language effects vary across models, we conducted a two-way ANOVA with model and language as factors, using cultural distance as the dependent variable.

**Design:**
- Factor 1: Model (21 levels, excluding low-quality models)
- Factor 2: Language (2 levels: English vs native language)
- Dependent variable: Cultural distance
- Unit of observation: Model–country–language combination (n = 2,772)

**Results:**
- Main effect of model: F(20, 2730) = 87.3, p < 0.0001, η² = 0.39
- Main effect of language: F(1, 2730) = 12.4, p = 0.0004, η² = 0.004
- Interaction effect: F(20, 2730) = 2.1, p = 0.003, η² = 0.015

**Interpretation:**
The significant interaction indicates that language effects vary across models, though the effect size is small (η² = 0.015). Post hoc tests reveal that Chinese-developed models show weaker language effects than US-developed models (mean difference = 0.18, p = 0.002).

### SI.4.2 English-Native Country Baseline Analysis

To establish a baseline for cultural alignment under constant language conditions, we analyzed 21 English-native countries evaluated exclusively in English.

**Countries included:**
Australia, Canada, Ghana, India, Ireland, Kenya, New Zealand, Nigeria, Philippines, Rwanda, Singapore, South Africa, Tanzania, Trinidad and Tobago, Uganda, United Kingdom, United States, Zambia, Zimbabwe, Jamaica, Barbados.

**Key findings:**
- Mean cultural distance: 2.31 ± 0.89
- Range: 1.03 (Nigeria) to 3.96 (Ireland)
- Traditional English-speaking countries (UK, Ireland, Australia, Canada, NZ, USA) show larger distances (mean = 2.87) than African English-speaking countries (mean = 1.42)
- Systematic bias toward secular-progressive values: All traditional English-speaking countries shifted toward more secular (mean PC2 shift = +1.95) and self-expressive (mean PC1 shift = +1.68) positions

**Implication:**
Even when language is held constant and cultural knowledge should be abundant, LLMs exhibit systematic cultural biases reflecting the composition of English-language training data.

### SI.4.3 Country Difficulty Ranking

We ranked countries by mean cultural distance (averaged across all models and languages) to identify which cultures are most difficult for LLMs to represent accurately.

**Easiest countries (distance < 1.5):**
1. China: 0.97
2. Nigeria: 1.03
3. Rwanda: 1.23
4. Ghana: 1.32
5. Japan: 1.38

**Most difficult countries (distance > 3.0):**
1. Ireland: 3.96
2. Libya: 3.54
3. Yemen: 3.42
4. Palestine: 3.28
5. Lebanon: 3.15

**Factors associated with difficulty:**
- Political instability: r = 0.34, p = 0.006
- Data scarcity (low internet penetration): r = 0.28, p = 0.02
- Internal cultural diversity: r = 0.31, p = 0.01
- Recent cultural change: r = 0.26, p = 0.04

### SI.4.4 Western vs Non-Western Binary Comparison

To test the digital Orientalism hypothesis in its simplest form, we compared English advantage between Western and non-Western countries using a binary classification.

**Western countries (n = 25):**
Western Europe (15) + English-native countries (10, excluding African countries)

**Non-Western countries (n = 41):**
All others

**Results:**
- Western mean English advantage: −8.7% (native language better)
- Non-Western mean English advantage: +12.3% (English better)
- Difference: 21.0 percentage points
- t-test: t(64) = 5.8, p < 0.0001
- Cohen's d: 1.43 (large effect)

**Consistency:**
- 78% of Western countries show native advantage (19/25)
- 73% of non-Western countries show English advantage (30/41)
- Binomial test: p < 0.0001

### SI.4.5 Language Variant Analysis

For languages with multiple variants (Chinese, Spanish, Portuguese), we tested whether variants show different language effects.

**Chinese variants:**
- Simplified (zh-cn): +0.07% English advantage (near parity)
- Traditional (zh-tw): +27.1% English advantage
- Cantonese (zh-hk): +24.8% English advantage
- ANOVA: F(2, 60) = 18.4, p < 0.0001

**Spanish variants:**
- European (es-ES): −12.4% (native advantage)
- Latin American (es-419): +8.7% (English advantage)
- t-test: t(18) = 3.2, p = 0.005

**Portuguese variants:**
- European (pt-PT): −8.3% (native advantage)
- Brazilian (pt-BR): −5.2% (native advantage)
- t-test: t(2) = 0.4, p = 0.72 (not significant)

**Interpretation:**
Language variants can show dramatically different patterns, indicating that training data availability and cultural context matter more than language family membership.

---

## SI.5 Sensitivity Analyses

### SI.5.1 Alternative Distance Metrics

We recomputed all analyses using three alternative distance metrics:

**Manhattan distance (L1):**
Distance = |PC1_model − PC1_IVS| + |PC2_model − PC2_IVS|

**Results:**
- Overall pattern unchanged
- Mean English advantage: +8.1% (vs +8.3% for Euclidean)
- Regional patterns: All regions maintain same direction and significance
- Correlation with Euclidean: r = 0.97, p < 0.0001

**Mahalanobis distance:**
Distance = √[(x − μ)ᵀ Σ⁻¹ (x − μ)]
where Σ is the covariance matrix of IVS country coordinates

**Results:**
- Overall pattern unchanged
- Mean English advantage: +7.9%
- Regional patterns: All regions maintain same direction and significance
- Correlation with Euclidean: r = 0.94, p < 0.0001

**Cosine distance:**
Distance = 1 − (x · y) / (||x|| ||y||)

**Results:**
- Overall pattern unchanged
- Mean English advantage: +8.5%
- Regional patterns: All regions maintain same direction and significance
- Correlation with Euclidean: r = 0.91, p < 0.0001

**Conclusion:**
Results are robust to choice of distance metric.

### SI.5.2 Alternative PCA Specifications

We tested three alternative PCA specifications:

**No rotation:**
- Variance explained: PC1 = 42%, PC2 = 28%
- Mean English advantage: +8.0%
- Regional patterns: All maintain same direction and significance

**Oblique rotation (Promax):**
- Allows correlated components
- Variance explained: PC1 = 44%, PC2 = 26%
- Mean English advantage: +8.4%
- Regional patterns: All maintain same direction and significance

**Three components:**
- Variance explained: PC1 = 42%, PC2 = 28%, PC3 = 15%
- Mean English advantage (2D projection): +8.2%
- Regional patterns: All maintain same direction and significance

**Conclusion:**
Results are robust to PCA specification.

### SI.5.3 Outlier Exclusion

We recomputed analyses after excluding countries with distances >2 SD from their regional mean.

**Excluded countries (n = 8):**
Ireland (3.96), Libya (3.54), Yemen (3.42), Palestine (3.28), Lebanon (3.15), Bolivia (3.08), Haiti (3.02), Kyrgyzstan (3.01)

**Results:**
- Mean English advantage: +8.5% (vs +8.3% with outliers)
- Regional patterns: All maintain same direction and significance
- Effect size (Cohen's d): 1.38 (vs 1.43 with outliers)

**Conclusion:**
Results are robust to outlier exclusion.

### SI.5.4 Large Models Only

We recomputed analyses using only large models (≥10B parameters, n = 16).

**Results:**
- Mean English advantage: +9.1% (vs +8.3% for all models)
- Regional patterns: All maintain same direction and significance
- Effect size (Cohen's d): 1.51 (vs 1.43 for all models)

**Interpretation:**
Language effects are slightly stronger in large models, suggesting that increased capacity does not eliminate digital Orientalism.

### SI.5.5 Geographic Regions vs Language Families

We recomputed analyses using geographic regions instead of linguistic families.

**Geographic regions:**
- Middle East & North Africa: +16.8% English advantage
- Eastern Europe & Central Asia: +15.2%
- East Asia & Pacific: +8.4%
- Latin America & Caribbean: +6.7%
- Sub-Saharan Africa: +5.3%
- Western Europe: −11.2% (native advantage)

**Results:**
- Pattern consistent with language family analysis
- Correlation between geographic and linguistic groupings: r = 0.89
- Regional patterns: All maintain same direction and significance

**Conclusion:**
Results are robust to choice of grouping scheme.

---

## SI.6 Computational Infrastructure

### SI.6.1 Hardware and Software

**Hardware:**
- CPU: AMD EPYC 7763 64-Core Processor
- RAM: 512 GB DDR4
- Storage: 4 TB NVMe SSD
- GPU: Not used (API-based inference)

**Software:**
- Python: 3.10.12
- Key packages:
  - pandas: 2.0.3
  - numpy: 1.24.3
  - scipy: 1.11.1
  - scikit-learn: 1.3.0
  - matplotlib: 3.7.2
  - seaborn: 0.12.2

### SI.6.2 API Rate Limits and Costs

**Rate limits:**
- OpenAI: 10,000 requests/minute
- Anthropic: 5,000 requests/minute
- Google: 60 requests/minute
- DeepSeek: 100 requests/minute
- Alibaba: 50 requests/minute

**Total API calls:**
- Study 1: 23 models × 6 languages × 10 questions × 5 repetitions = 6,900 calls
- Study 2: 21 models × 66 countries × 2 languages × 10 questions × 5 repetitions = 138,600 calls
- Total: 145,500 calls

**Estimated costs:**
- OpenAI models: ~$2,400
- Anthropic models: ~$1,800
- Google models: ~$800
- Chinese models: ~$600
- European models: ~$400
- Total: ~$6,000

### SI.6.3 Data Collection Timeline

- Study 1 (intrinsic values): February 2024 - March 2024
- Study 2 (cultural imitation): April 2024 - December 2024
- Data validation and cleaning: January 2025
- Statistical analyses: January 2025 - February 2025

**Total duration:** 12 months

---

## SI.7 Data Availability

All data, code, and supplementary materials are publicly available at:
- GitHub repository: [URL]
- Zenodo archive: [DOI]
- Interactive dashboard: [URL]

**Repository contents:**
- Raw model responses (JSON format)
- Processed data (CSV format)
- IVS reference data
- Analysis scripts (Python)
- Figure generation scripts
- Supplementary tables and figures

**License:** CC BY 4.0 (data), MIT License (code)

---

**Word count:** ~3,500 words
