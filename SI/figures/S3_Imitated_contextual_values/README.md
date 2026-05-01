# S3: Imitated Contextual Values

This section presents LLM cultural roleplay results (Stage 3), where models were prompted to respond as citizens of specific countries. These figures reveal **cultural imitation patterns** across models, countries, and languages.

## Key Findings

1. **GPT-4o achieves best overall imitation accuracy** (mean distance = 1.26), followed by DeepSeek series (1.50-1.59).

2. **Small models struggle with cultural imitation**: phi-3-mini (2.86) and llama-3.2-3b (3.17) show significantly higher distances.

3. **Language itself carries cultural information**: German prompts yield the most "Secular" responses (PC1 = 3.80), while Arabic prompts yield the most "Traditional" responses (PC1 = -1.58) — a 5.38 unit difference.

4. **Western countries are easier to imitate**: European countries show lower mean distances than African-Islamic or East Asian countries.

5. **Systematic "Westernization" bias**: LLMs tend to shift all countries toward the Secular-Self-expression quadrant.

## Experimental Design

| Parameter | Value |
|-----------|-------|
| Models | 21 LLMs |
| Countries/Regions | 66 (from IVS dataset) |
| Languages | 13 (including English and native languages) |
| Total data points | 2,562 (model × country × language combinations) |

## Figure Organization (~1,889 figures)

### B1: Per Model, Language Averaged (21 figures)

**Directory**: `B1_per_model_languageAvg/`

**File pattern**: `FigS3B1_{model}_languageAvg.pdf`

**Content**: Each model's roleplay results averaged across all languages, colored by cultural region.

**Purpose**: Compare model-level cultural imitation patterns

**Key observations**:
- GPT-4o shows tightest clustering around IVS targets
- Small models show systematic bias toward specific quadrants
- Chinese models perform well on East Asian countries

### B2: Per Country, Model Averaged (66 figures)

**Directory**: `B2_per_country_modelAvg/`

**File pattern**: `FigS3B2_{country}_modelAvg.pdf`

**Content**: Each country's representation averaged across all models, colored by model.

**Purpose**: Identify which countries are consistently well/poorly imitated

**Key observations**:
- Western European countries show tight model consensus
- African-Islamic countries show high model variance
- East Asian countries show language-dependent patterns

### B3: Per Model × Per Country (~1,386 figures)

**Directory**: `B3_per_model_per_country/`

**File pattern**: `FigS3B3_{model}_{country}.pdf`

**Content**: Specific model-country combinations showing all language variants.

**Purpose**: Detailed analysis of model-country-language interactions

**Key observations**:
- Language choice significantly affects imitation accuracy
- Some model-country pairs show high language stability
- English often outperforms native language for non-Western countries

### B4: Per Country × Per Language (~122 figures)

**Directory**: `B4_per_country_per_language/`

**File pattern**: `FigS3B4_{country}_{lang}.pdf`

**Content**: Country-language pairs showing all model results.

**Purpose**: Compare model performance for specific country-language pairs

**Key observations**:
- Model variance is higher for "difficult" countries
- Language-country mismatch (e.g., Arabic for Japan) shows interesting patterns

### B5: Per Model × Per Language (~294 figures)

**Directory**: `B5_per_model_per_language/`

**File pattern**: `FigS3B5_{model}_{lang}.pdf`

**Content**: Model-language pairs showing all country results.

**Purpose**: Analyze language-specific model behavior across countries

**Key observations**:
- Each language induces a characteristic "cultural pull"
- Models show different sensitivity to language effects

## Statistical Summary

### Model Performance Ranking (Top 5)

| Rank | Model | Mean Distance |
|------|-------|---------------|
| 1 | gpt-4o | 1.26 |
| 2 | deepseek-chat | 1.50 |
| 3 | deepseek-chat-v3.1 | 1.59 |
| 4 | doubao-1-5-pro | 1.63 |
| 5 | gemini-2.5-flash | 1.71 |

### Language Effect on Cultural Coordinates

| Language | Mean PC1 | Mean PC2 | Cultural Position |
|----------|----------|----------|-------------------|
| German (de) | 3.80 | 2.03 | Most Secular + Self-expression |
| Arabic (ar) | -1.58 | -0.52 | Most Traditional + Survival |
| English (en) | 0.26 | 0.45 | Near center |
| Chinese (zh-cn) | 0.77 | 1.35 | Moderate |

## Visual Elements

All figures include:
- **Semi-transparent colored background points**: IVS country coordinates (reference), colored by cultural region
- **Gold star (★)**: Target country's real IVS position
- **Colored points**: LLM-generated coordinates
- **Dashed lines**: Connect LLM points to real coordinates (showing deviation)

## Implications for Main Analysis

1. **Model selection matters**: 2.5× difference between best (1.26) and worst (3.17) models.

2. **Language is not neutral**: Prompt language systematically shifts cultural coordinates.

3. **"Westernization" is universal**: All models show bias toward Secular-Self-expression values.

4. **Country difficulty varies**: Western countries are 2-3× easier to imitate than non-Western countries.

## Generation Scripts

```bash
python analysis/si/generate_figs3_b1b2.py  # B1 and B2
python analysis/si/generate_figs3_b3.py    # B3
python analysis/si/generate_figs3_b4.py    # B4
python analysis/si/generate_figs3_b5.py    # B5
```

## Data Sources

- `SI/pca/Table_S5_IVS_PCA_coordinates.csv` - IVS reference coordinates (109 countries)
- `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv` - LLM roleplay coordinates (21 models × 66 countries × 13 languages)

