# PNAS Paper Structure

## Main Text Sections

### 1. Abstract (260 words)
**File**: `paper_pnas_abstract.md`
**Chinese**: `paper_pnas_abstract_CN.md`

**Key points**:
- Baseline: Language shifts model values (English PC1=+2.69, Arabic PC1=+0.98, F=3.38, p=0.007)
- 23 models, 66 countries, 13 languages
- Digital Orientalism: Islamic/Arab +17.4%, Orthodox/Slavic +17.7%, Western Europe -11.5%
- East Asian gradient: China +0.07%, Taiwan +27.1%, Hong Kong +24.8%
- Model origin: Chinese models +1.9% for Sino-Tibetan (vs US +16.8%)
- Effect size: Cohen's d=1.43, consistent across 19/21 models

---

### 2. Significance Statement (120 words)
**File**: `paper_pnas_significance.md`
**Chinese**: `paper_pnas_significance_CN.md`

**Key message**: AI systems inherit historical patterns of knowledge production, understanding non-Western cultures primarily through Western linguistic frameworks.

---

### 3. Introduction (~900 words)
**File**: `paper_pnas_introduction.md`
**Chinese**: `paper_pnas_introduction_CN.md`

**Structure**:
- Opening: LLMs as global cultural intermediaries
- Theoretical background: Orientalism, linguistic relativity, training data bias
- Research questions:
  1. Baseline language effects on model values
  2. Overall pattern: English vs native languages
  3. Regional heterogeneity
  4. Mechanisms: training data, colonial legacy, cultural soft power, model origin
- Contributions:
  1. Methodological: First systematic evaluation (23 models, 66 countries, 13 languages)
  2. Empirical: Digital Orientalism pattern (d=1.43)
  3. Theoretical: Multi-mechanism framework
  4. Practical: Implications for global AI deployment

---

### 4. Materials and Methods (~800 words)
**File**: `paper_pnas_methods.md`
**Chinese**: `paper_pnas_methods_CN.md`

**Sections**:
- Data and Cultural Framework (Inglehart-Welzel map, IVS, 10 survey items)
- Models (23 LLMs from US, China, Europe)
- Experimental Design (baseline + roleplay conditions)
- Response Validation and Quality Control
- Cultural Scoring and Dimensionality Reduction (PPCA)
- Statistical Analysis (paired t-tests, effect sizes, robustness checks)

---

### 5. Results (~2,050 words)
**File**: `paper_pnas_results.md`
**Chinese**: `paper_pnas_results_CN.md`

**Structure** (8 sections):
1. LLM Intrinsic Values Reveal Western Bias and Language-Dependent Variation (~350 words)
2. Baseline: English-Native Countries Reveal Systematic Biases (~200 words)
3. Overall Language Effect Masks Regional Heterogeneity (~150 words)
4. Digital Orientalism: Cultural Regions Show Opposite Language Effects (~350 words)
5. East Asian Heterogeneity: Colonial Legacy and Cultural Soft Power (~350 words)
6. Latin American Complexity: Beyond the Spanish-Speaking Monolith (~250 words)
7. Model Origin and Regional Specialization (~300 words)
8. Model-Language Interaction Consistency (~200 words)
9. Effect Size and Statistical Robustness (~200 words)

---

### 6. Discussion (~2,200 words)
**File**: `paper_pnas_discussion.md`
**Chinese**: `paper_pnas_discussion_CN.md`

**Note**: PNAS format typically does not have a separate Conclusion section. Conclusions are integrated into the final part of the Discussion.

**Structure** (8 sections):
1. Disentangling Baseline and Cultural Knowledge Effects (~300 words)
2. Interpreting Digital Orientalism: Training Data as Cultural Archive (~400 words)
3. Why Western Europe is Different: Centuries of Native-Language Self-Representation (~250 words)
4. Cultural Soft Power and Digital Representation: The Japan-Korea Exception (~300 words)
5. Colonial Legacy in the Digital Age: The Hong Kong-Macao Natural Experiment (~300 words)
6. Model Origin and Cultural Proximity: Partial Mitigation, Not Elimination (~300 words)
7. Practical Implications: Toward Culturally Equitable AI (~250 words)
8. Limitations and Future Directions (~300 words)

**Concluding remarks** (integrated in Discussion):
- Two-level finding: baseline language effect + cultural knowledge effect
- Digital Orientalism pattern: non-Western cultures more accurate in English
- Multi-mechanism framework: training data, colonial legacy, cultural soft power
- Implications: native language ≠ better accuracy for non-Western cultures
- Path forward: diversify training data, cross-language evaluation, transparency

---

## Figures (Main Text - Max 6)

### Figure 1: IVS Cultural Map Framework
**Location**: Introduction
**Source**: `SI/figures/S1_IVS_cultural_map/FigS1_IVS_cultural_map.pdf`
**Content**: Inglehart-Welzel cultural map showing 66 countries across 8 cultural regions
**Purpose**: Establish analytical framework, demonstrate global cultural diversity
**Caption**: "World Values Survey cultural map showing 66 countries across 8 cultural regions. PC1 (x-axis): Survival-Self-Expression values; PC2 (y-axis): Traditional-Secular values."

---

### Figure 2: Baseline Language Effect
**Location**: Results §1
**Source**: `SI/figures/S2_Baseline_intrinsic_values/A2_per_language/`
**Content**: Distribution of 23 models across 6 languages (English, French, Spanish, Russian, Arabic, Simplified Chinese)
**Key Finding**: English most secular (PC1=+2.69), Arabic most traditional (PC1=+0.98), F=3.38, p=0.007
**Purpose**: Demonstrate that language itself shifts model values (baseline effect)
**Caption**: "Baseline language effect: LLM intrinsic values vary by prompt language. English prompts elicit most secular responses (PC1=+2.69), Arabic prompts elicit most traditional (PC1=+0.98). Each point represents one model in one language (n=138 model-language combinations). ANOVA: F=3.38, p=0.007."

---

### Figure 3: Digital Orientalism - Cultural Regions
**Location**: Results §4
**Source**: `SI/figures/S5_English_advantage_and_orientalism/FigS5A_cultural_regions_language_effect.pdf`
**Content**: English advantage (%) by cultural region with error bars
**Key Finding**: Islamic/Arab +17.4% (p<0.0001), Orthodox/Slavic +17.7% (p=0.008), Protestant Europe -20.3% (p<0.001)
**Purpose**: Core finding - demonstrate digital Orientalism pattern
**Caption**: "Digital Orientalism: Cultural regions show opposite language effects. Non-Western cultures (Islamic/Arab +17.4%, Orthodox/Slavic +17.7%) show strong English advantage, while Western cultures (Protestant Europe -20.3%, Catholic Europe -12.4%) show native language advantage. Error bars: ±1 SE. ***p<0.001, **p<0.01, *p<0.05."

---

### Figure 4: East Asian Gradient
**Location**: Results §5
**Source**: `SI/figures/S6_East_Asia_analysis/FigS6C_east_asia_english_gradient.pdf`
**Content**: English advantage for 6 East Asian countries/regions
**Key Finding**: China +0.07%, Japan +3.3%, Korea +3.0%, Taiwan +27.1%, Hong Kong +24.8%, Macao -13.6%
**Purpose**: Demonstrate regional heterogeneity, illustrate training data and colonial legacy effects
**Caption**: "East Asian gradient reveals training data and colonial legacy effects. China shows near-perfect parity (+0.07%), while Taiwan (+27.1%) and Hong Kong (+24.8%) show strong English advantage. Hong Kong-Macao contrast illustrates colonial legacy: British (+24.8%) vs Portuguese (-13.6%)."

---

### Figure 5: Model Origin Effects
**Location**: Results §7
**Source**: `SI/figures/S4_Model_and_response_analysis/FigS4G_vendor_origin_analysis.pdf`
**Content**: Two panels - (Left) Average cultural distance by model origin with ANOVA; (Right) All models ranked by vendor, colored by origin
**Key Finding**: Chinese models show competitive performance, combined with Table 1 shows language-specific effects
**Purpose**: Demonstrate that training data diversification can reduce bias
**Caption**: "Model origin affects overall performance. Chinese models (DeepSeek, Qwen) show competitive accuracy, while US models exhibit higher variance. Combined with language-specific analysis (Table 1), this reveals regional specialization: Chinese models show weaker Orientalism for Sino-Tibetan (+1.9% vs +16.8% for US models) and Semitic languages (+8.2% vs +19.6%)."

---

### Figure 6: Performance vs Consistency
**Location**: Results §8
**Source**: `SI/figures/summary/FigSx4_score_vs_consistency.pdf`
**Content**: Scatter plot of cultural distance vs cross-language consistency for all 21 models
**Key Finding**: Correlation r=-0.65 (p<0.001), GPT-4o best (distance=1.26)
**Purpose**: Show model performance variation and consistency-accuracy relationship
**Caption**: "Model performance varies dramatically. GPT-4o achieves lowest cultural distance (1.26), while small models show 2-3× larger errors. Consistency correlates with accuracy (r=-0.65, p<0.001), suggesting that models with stable cross-language representations achieve better cultural imitation."

---

## Tables (Main Text)

### Table 1: Model Origin × Language Family Interaction
**Location**: Results §7

| Model Origin | Sino-Tibetan | Slavic | Semitic | Romance | Germanic |
|--------------|--------------|--------|---------|---------|----------|
| China (n=3)  | +1.9%*       | +19.4% | +8.2%*  | +13.0%  | -25.2%   |
| USA (n=4)    | +16.8%       | +5.7%  | +19.6%  | -0.7%   | -15.7%   |
| Europe (n=3) | +25.3%       | -43.3%*| +20.1%  | -14.1%  | +13.0%   |

*Significant difference from other origins (p<0.05)

---

## Supporting Information

### SI Figures (~1,932 figures)
- **S1**: IVS cultural map (1 figure)
- **S2**: Baseline intrinsic values (24 figures)
- **S3**: Cultural roleplay results (~1,889 figures)
- **S4**: Model behavior analysis (7 figures)
- **S5**: Orientalism analysis (4 figures)
- **S6**: East Asia analysis (3 figures)
- **Sx**: Statistical overview (4 figures)

### SI Tables
- **S1-S2**: Baseline modal responses and validity
- **S3-S4**: Roleplay modal responses and validity
- **S5**: IVS PCA coordinates (109 countries)
- **S6**: LLM baseline PCA coordinates (23 models × 6 languages)
- **S7**: LLM roleplay PCA coordinates (21 models × 66 countries × 13 languages)
- **S8**: PCA component summary

---

## Word Count

| Section | Target | Actual |
|---------|--------|--------|
| Abstract | 260 | 260 |
| Significance | 120 | 118 |
| Introduction | 800 | ~900 |
| Methods | 800 | ~800 |
| Results | 2000 | ~2,050 |
| Discussion (with conclusions) | 2200 | ~2,200 |
| **Total** | **~6,200** | **~6,300** |

**Note**: PNAS format does not have a separate Conclusion section. Conclusions are integrated into the Discussion.

---

## Key Findings Summary

### Baseline Language Effect
- English prompts → most secular (PC1=+2.69)
- Arabic prompts → most traditional (PC1=+0.98)
- Significant effect: F=3.38, p=0.007
- Models don't have single "intrinsic" values

### Digital Orientalism
- Islamic/Arab: +17.4% English advantage (p<0.0001)
- Orthodox/Slavic: +17.7% (p=0.008)
- Western Europe: -11.5% native advantage (p=0.03)
- Effect size: Cohen's d=1.43 (very large)

### Regional Heterogeneity
- **East Asia**: China +0.07%, Taiwan +27.1%, Hong Kong +24.8%, Macao -13.6%
- **Latin America**: Haiti +20.4%, Bolivia +19.8%, Brazil -5.2%
- **Model Origin**: Chinese models +1.9% for Sino-Tibetan (vs US +16.8%)

### Mechanisms
1. Training data availability (China vs Taiwan)
2. Colonial legacy (Hong Kong vs Macao)
3. Cultural soft power (Japan/Korea +3%)
4. Language variants (European vs Latin American Spanish/Portuguese)
5. Model origin (regional specialization)

---

## File Organization

```
docs/论文草稿/第一版/
├── paper_pnas_abstract.md
├── paper_pnas_abstract_CN.md
├── paper_pnas_significance.md
├── paper_pnas_significance_CN.md
├── paper_pnas_introduction.md
├── paper_pnas_introduction_CN.md
├── paper_pnas_methods.md
├── paper_pnas_methods_CN.md
├── paper_pnas_results.md
├── paper_pnas_results_CN.md
├── paper_pnas_discussion.md
├── paper_pnas_discussion_CN.md
├── paper_pnas_conclusion.md
├── paper_pnas_conclusion_CN.md
├── paper_pnas_SI_outline.md
├── FIGURE_PLANNING_V3.md
├── FIGURE_SUMMARY_V3.md
└── FIGURE_SUMMARY_V3_CN.md
```

---

**Last Updated**: 2026-01-16
