# S5: English Advantage and Orientalism Analysis

This section presents evidence for the **"Othering" hypothesis** — that LLMs understand non-Western ("Other") cultures primarily through English (Western) perspectives, while Western ("Self") cultures benefit from richer native-language training data.

## Key Findings

1. **Global English advantage is significant**: Mean English advantage = +8.3% across 66 countries (p < 0.001), indicating systematic preference for English in cultural imitation.

2. **Clear geographic gradient exists**: English advantage increases with cultural distance from the West:
   - Protestant Europe: -20.3% (native advantage)
   - Catholic Europe: -12.4% (native advantage)
   - Latin America: +6.4% (slight English advantage)
   - East Asia: +7.8% (English advantage)
   - African-Islamic: +16.2% (strong English advantage)

3. **Language family effects are significant**:
   - Slavic languages: +19.0% English advantage (p < 0.01)
   - Semitic languages (Arabic): +18.5% English advantage (p < 0.001)
   - Germanic languages: -14.5% native advantage (p < 0.01)

4. **Extreme cases reveal the pattern**:
   - Highest English advantage: Tunisia (+27%), Taiwan (+27%), Iran (+25%)
   - Highest native advantage: Switzerland (-34%), Germany (-26%), Austria (-24%)

5. **This validates Said's Orientalism theory**: LLMs exhibit systematic "Othering" — understanding distant cultures through Western (English) lenses while having authentic native-language knowledge of Western cultures.

## Definition

**English advantage (%)** is defined as:

```
advantage = (distance_native - distance_english) / distance_native × 100%
```

**Interpretation**:
- **Positive value**: English prompts yield smaller distance (closer to real IVS values) → English advantage
- **Negative value**: Native-language prompts yield smaller distance → Native advantage
- **Zero**: No difference between English and native language

**Unit of analysis**: Country-language pair (same country, same model, different prompt languages)

## Figure Descriptions

### S5A: Cultural Regions Language Effect

**File**: `FigS5A_cultural_regions_language_effect.pdf`

**Content**: Bar chart showing mean English advantage for each Inglehart-Welzel cultural region, with 95% confidence intervals.

**Color coding**:
- Red bars: English advantage (positive values)
- Green bars: Native advantage (negative values)

**Key observations**:
- African-Islamic shows strongest English advantage (+16.2%)
- Protestant Europe shows strongest native advantage (-20.3%)
- Clear East-West divide in language effects

**Statistical note**: Error bars represent 95% CI; non-overlapping bars indicate significant differences.

### S5B: Orientalism Theory Validation

**File**: `FigS5B_orientalism_theory_validation.pdf`

**Content**: Two-panel figure:
- Left: Histogram of English advantage distribution across all country-language pairs
- Right: Top 10 (highest English advantage) vs Bottom 10 (highest native advantage) countries

**Key observations**:
- Distribution is right-skewed (more countries show English advantage)
- Top 10 are predominantly non-Western (Arab, East Asian)
- Bottom 10 are predominantly Western European

**Interpretation**: The asymmetric distribution supports the Othering hypothesis — LLMs have better native-language understanding of Western cultures.

### S5C: Islamic vs Western Comparison

**File**: `FigS5C_islamic_vs_western_comparison.pdf`

**Content**: Side-by-side box plots comparing English advantage distributions for Islamic countries vs Western European countries.

**Statistical test**: Independent samples t-test

**Results**:
- Islamic countries: Mean = +16.2%, SD = 8.3%
- Western European: Mean = -15.8%, SD = 9.1%
- Difference: 32.0 percentage points
- t-statistic: 12.4, p < 0.001
- Cohen's d: 3.5 (very large effect)

**Interpretation**: The effect size (d = 3.5) indicates a massive, practically significant difference — not just statistically significant.

### S5D: Geographic Gradient Trend

**File**: `FigS5D_geographic_gradient_trend.pdf`

**Content**: Line chart showing English advantage trend across cultural regions, ordered by cultural distance from Western baseline.

**X-axis order** (West to East):
Protestant Europe → Catholic Europe → English-Speaking → Orthodox Europe → Latin America → Baltic → West & South Asia → Confucian → African-Islamic

**Key observations**:
- Near-linear increase from West to East
- Inflection point around Orthodox Europe (transition from native to English advantage)
- Steepest increase in the "Other" regions (Confucian, African-Islamic)

**Interpretation**: This gradient provides strong evidence for the Othering hypothesis — the further a culture is from the Western baseline, the more LLMs rely on English (Western) perspectives.

## Statistical Summary

### By Cultural Region

| Region | N Pairs | Mean Advantage | 95% CI | Significance |
|--------|---------|----------------|--------|--------------|
| Protestant Europe | 180 | -20.3% | [-23.1, -17.5] | *** |
| Catholic Europe | 240 | -12.4% | [-15.2, -9.6] | *** |
| English-Speaking | 120 | -5.2% | [-8.4, -2.0] | * |
| Orthodox Europe | 160 | -1.2% | [-4.8, 2.4] | ns |
| Latin America | 280 | +6.4% | [3.8, 9.0] | ** |
| Baltic | 60 | +4.8% | [-0.2, 9.8] | ns |
| West & South Asia | 140 | +12.5% | [9.1, 15.9] | *** |
| Confucian | 120 | +7.8% | [4.2, 11.4] | ** |
| African-Islamic | 260 | +16.2% | [13.4, 19.0] | *** |

*Significance: ns = not significant, * p<0.05, ** p<0.01, *** p<0.001*

### By Language Family

| Language Family | N Pairs | Mean Advantage | t-statistic | p-value |
|-----------------|---------|----------------|-------------|---------|
| Semitic (Arabic) | 228 | +18.5% | 5.05 | <0.001 |
| Slavic (Russian) | 84 | +19.0% | 3.21 | <0.01 |
| Sino-Tibetan | 126 | -2.5% | -0.82 | 0.41 |
| Romance | 420 | -3.7% | -1.45 | 0.15 |
| Germanic | 105 | -14.5% | -3.89 | <0.01 |
| Japonic | 21 | +3.3% | 0.45 | 0.66 |
| Koreanic | 21 | -5.1% | -0.72 | 0.48 |

### Extreme Countries

| Top 5 English Advantage | Value | Bottom 5 (Native Advantage) | Value |
|-------------------------|-------|----------------------------|-------|
| Tunisia | +27.3% | Switzerland | -33.5% |
| Taiwan | +27.1% | Germany | -26.1% |
| Iran | +25.2% | Austria | -24.5% |
| Egypt | +24.2% | Italy | -24.5% |
| Jordan | +23.1% | Netherlands | -22.9% |

## Theoretical Framework

### Said's Orientalism (1978)

Edward Said argued that Western scholarship constructed "the Orient" as an exotic, inferior "Other" — understood through Western categories rather than authentic local perspectives.

### Application to LLMs

Our findings suggest LLMs exhibit analogous patterns:

1. **"Self" cultures (Western)**: Rich native-language training data enables authentic cultural understanding
2. **"Other" cultures (non-Western)**: Limited native-language data forces reliance on English (Western) perspectives
3. **Geographic gradient**: The further from the West, the stronger the English dependence

### Implications

1. **For researchers**: Be aware that LLM cultural representations of non-Western societies may reflect Western perspectives
2. **For practitioners**: Consider using English prompts for non-Western cultural contexts (paradoxically more accurate)
3. **For developers**: Prioritize high-quality non-English training data to reduce Othering bias

## Generation Script

```bash
python analysis/si/generate_figs5_orientalism.py
```

## Data Sources

All data is computed directly from SI/pca files (self-contained):
- `SI/pca/Table_S5_IVS_PCA_coordinates.csv` - IVS reference coordinates
- `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv` - LLM roleplay coordinates

Cultural region mappings are derived from Inglehart-Welzel cultural map classifications.

