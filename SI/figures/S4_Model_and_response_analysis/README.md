# S4: Model and Response Analysis

This section presents analytical figures examining **model behavior patterns** and **performance characteristics** across baseline and roleplay conditions.

## Key Findings

1. **Roleplay increases response variability**: Models show 2-3× higher PC1 standard deviation under roleplay condition compared to baseline, indicating successful cultural differentiation.

2. **Model size correlates with imitation accuracy**: Large models (>70B parameters) achieve mean distance of ~1.75, while small models (<10B) show ~3.0 — a significant performance gap.

3. **Flexibility ≠ Accuracy**: grok-4.1-fast shows highest flexibility but only moderate accuracy. GPT-4o shows moderate flexibility but best accuracy.

4. **Western countries are systematically easier**: Top 15 easiest countries are predominantly Western European; Bottom 15 hardest are predominantly African-Islamic.

5. **Open vs Closed source**: No significant difference in overall performance (p > 0.05).

## Figure Descriptions

### S4A: Model Response Consistency

**File**: `FigS4A_consistency_distribution_by_model.pdf`

**Content**: Paired bar chart comparing PC1 standard deviation for each model under Baseline vs Roleplay conditions.

**Metric**: PC1 standard deviation (lower = more consistent responses)

**Key observations**:
- All models show higher variability under Roleplay (expected behavior)
- Variability increase ranges from 1.5× to 4×

### S4B: Model Roleplay Flexibility

**File**: `FigS4B_model_flexibility.pdf`

**Content**: Horizontal bar chart ranking models by mean deviation from their baseline (intrinsic) values during roleplay.

**Metric**: Mean Euclidean distance from baseline centroid (higher = more flexible)

**Key observations**:
- phi-3-mini-128k-instruct is most conservative
- grok-4.1-fast is most flexible
- Small parameter models cluster at the conservative end

### S4C: Model Cultural Imitation Performance

**File**: `FigS4C_imitation_shift_by_model.pdf`

**Content**: Horizontal bar chart ranking models by mean cultural distance (best performers on top).

**Metric**: Mean Euclidean distance from IVS coordinates (lower = better)

**Key observations**:
- GPT-4o leads with lowest mean distance
- DeepSeek models cluster in top 5
- Small models (phi-3, llama-3.2-3b) rank at bottom

### S4D: Country Imitation Difficulty

**File**: `FigS4D_imitation_country_shift_summary.pdf`

**Content**: Dual panel showing Top 15 easiest (left) and Bottom 15 hardest (right) countries to imitate.

**Metric**: Mean distance across all models and languages

**Key observations**:
- Easiest: Predominantly Western European (Germany, Netherlands, Sweden)
- Hardest: Predominantly African-Islamic (Tunisia, Jordan, Egypt)

### S4E: Model Size Analysis

**File**: `FigS4E_model_size_analysis.pdf`

**Content**: Two-panel analysis of model size vs accuracy.

**Left panel**: Bar chart by size category (Small/Medium/Large)

**Right panel**: All models ranked, colored by size category

**Key observations**:
- Clear negative correlation: larger models achieve lower distances
- Diminishing returns above ~70B parameters

### S4F: Open Source vs Closed Source

**File**: `FigS4F_open_vs_closed_source.pdf`

**Content**: Two-panel comparison.

**Left panel**: Bar chart with significance test (Mann-Whitney U)

**Right panel**: All models ranked, colored by source type

**Statistical result**: n.s. (not significant, p > 0.05)

### S4G: Model Origin and Vendor Analysis

**File**: `FigS4G_vendor_origin_analysis.pdf`

**Content**: Two-panel analysis by model origin country and vendor.

**Left panel**: Bar chart by origin (USA, China, Europe) with ANOVA test

**Right panel**: Vendor ranking, colored by origin

**Key observations**:
- Chinese models (DeepSeek, Alibaba) show competitive performance
- USA models show more variance

## Generation Script

```bash
python -B analysis/si/generate_figs4_model_response.py
```

## Data Sources

- `SI/pca/Table_S5_IVS_PCA_coordinates.csv` - IVS reference coordinates
- `SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv` - LLM baseline coordinates
- `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv` - LLM roleplay coordinates
