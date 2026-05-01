# Summary: Statistical Overview Figures

This section presents **aggregate statistical analyses** across the entire dataset, providing high-level insights into model performance, country difficulty, and cross-factor interactions.

## Key Findings

1. **Clear model performance tiers exist**:
   - Tier 1 (distance < 1.5): GPT-4o, DeepSeek series
   - Tier 2 (distance 1.5-2.0): Gemini, Claude, Qwen
   - Tier 3 (distance > 2.0): Small models (phi-3, llama-3.2-3b)

2. **Country difficulty is systematic**: Western European countries consistently rank as easiest; African-Islamic countries consistently rank as hardest across all models.

3. **Consistency correlates with accuracy**: Models with lower response variability (higher consistency) tend to achieve better cultural imitation (lower distance). Correlation r ≈ -0.65.

4. **Language effects are model-dependent**: Some models show strong language sensitivity (high variance across languages); others are relatively language-invariant.

## Figure Descriptions

### Sx1: Model × Country Heatmap

**File**: `FigSx1_heatmap_model_country.pdf`

**Content**: Heatmap showing mean cultural distance for each model-country combination.

**Dimensions**: 21 models (rows) × 66 countries (columns)

**Color scale**: 
- Blue: Low distance (good imitation)
- Yellow: Medium distance
- Red: High distance (poor imitation)

**Key observations**:
- Vertical blue stripes indicate "easy" countries (e.g., Germany, Netherlands)
- Vertical red stripes indicate "hard" countries (e.g., Tunisia, Jordan)
- Horizontal blue bands indicate high-performing models (e.g., GPT-4o)
- Horizontal red bands indicate low-performing models (e.g., llama-3.2-3b)

**Usage**: Identify optimal model-country pairings for specific research needs.

### Sx2: Model × Language Heatmap

**File**: `FigSx2_heatmap_model_language.pdf`

**Content**: Heatmap showing mean cultural distance for each model-language combination.

**Dimensions**: 21 models (rows) × 14 languages (columns)

**Annotations**: Cell values showing exact distances (2 decimal places)

**Key observations**:
- German (de) and French (fr) columns tend to show lower distances
- Arabic (ar) column tends to show higher distances
- Some models show high language sensitivity (large row variance)
- Others show language invariance (uniform row colors)

**Usage**: Identify which languages work best with which models.

### Sx3: Top/Bottom Country Rankings

**File**: `FigSx3_top_bottom_rankings.pdf`

**Content**: Multi-panel figure showing top 5 (best) and bottom 5 (worst) countries for each model.

**Layout**: One subplot per model, showing:
- Green bars: 5 easiest countries for this model
- Red bars: 5 hardest countries for this model

**Key observations**:
- Western European countries dominate "easiest" lists across all models
- African-Islamic countries dominate "hardest" lists across all models
- Some models show unique strengths (e.g., Chinese models excel on China)

**Usage**: Quick reference for model-specific recommendations.

### Sx4: Cultural Distance vs Consistency

**File**: `FigSx4_score_vs_consistency.pdf`

**Content**: Scatter plot with regression line showing relationship between mean distance and model consistency.

**Metrics**:
- X-axis: Mean cultural distance
- Y-axis: Model consistency = 1 / (1 + PC1_std + PC2_std)

**Key observations**:
- Negative correlation (r ≈ -0.65): More consistent models achieve lower distances
- GPT-4o: High consistency, low distance
- Small models: Low consistency, high distance

**Interpretation**: Response consistency is a good predictor of cultural imitation quality. Models that give stable, predictable responses also tend to be more accurate.

## Statistical Summary

### Model Performance Tiers

| Tier | Distance Range | Models | Characteristics |
|------|----------------|--------|-----------------|
| 1 (Excellent) | < 1.5 | GPT-4o, DeepSeek-chat, DeepSeek-v3.1 | Large, well-trained |
| 2 (Good) | 1.5 - 2.0 | Gemini-2.5-flash, Claude-3-7, Qwen3-max | Major commercial models |
| 3 (Moderate) | 2.0 - 2.5 | GPT-4o-mini, Grok, Gemma | Mid-tier models |
| 4 (Poor) | > 2.5 | phi-3-mini, llama-3.2-3b, Mistral-nemo | Small models |

### Country Difficulty Tiers

| Tier | Distance Range | Example Countries | Characteristics |
|------|----------------|-------------------|-----------------|
| Easy | < 1.5 | Germany, Netherlands, Sweden | Western European, rich training data |
| Moderate | 1.5 - 2.5 | Japan, Brazil, Russia | Major non-Western, moderate data |
| Hard | > 2.5 | Tunisia, Jordan, Pakistan | African-Islamic, limited data |

## Practical Recommendations

Based on summary analyses:

1. **Model selection**: Prioritize GPT-4o or DeepSeek for cross-cultural research
2. **Country awareness**: Expect 2-3× higher error for non-Western countries
3. **Language choice**: German/French prompts often outperform English for European countries
4. **Consistency check**: Monitor response variability as a quality indicator

## Generation Script

```bash
python -B analysis/si/generate_figs_summary.py
```

## Data Sources

- `SI/pca/Table_S5_IVS_PCA_coordinates.csv` - IVS reference coordinates
- `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv` - LLM roleplay coordinates
