# S1: IVS Cultural Map (Reference)

This section presents the **Inglehart-Welzel Cultural Map** based on Integrated Values Survey (IVS) data, serving as the ground truth reference for all LLM cultural imitation analyses.

## Key Information

1. **The cultural map captures two fundamental value dimensions**:
   - **PC1 (Traditional ↔ Secular-Rational)**: Higher values indicate more secular, rational worldviews; lower values indicate more traditional, religious worldviews
   - **PC2 (Survival ↔ Self-Expression)**: Higher values indicate emphasis on self-expression, quality of life; lower values indicate emphasis on economic/physical security

2. **109 countries/regions are positioned** based on nationally representative survey data from the World Values Survey (WVS) and European Values Study (EVS). (112 total entries, 3 with incomplete data excluded)

3. **Eight cultural regions are identified** following Inglehart-Welzel classification:
   - Protestant Europe (e.g., Germany, Sweden, Netherlands)
   - Catholic Europe (e.g., France, Italy, Spain)
   - English-Speaking (e.g., USA, UK, Australia)
   - Confucian (e.g., China, Japan, South Korea)
   - Orthodox Europe (e.g., Russia, Ukraine, Serbia)
   - Latin America (e.g., Brazil, Mexico, Argentina)
   - African-Islamic (e.g., Egypt, Nigeria, Morocco)
   - West & South Asia (e.g., India, Pakistan, Turkey)

## Figure Description

### FigS1: IVS Cultural Map

**File**: `FigS1_IVS_cultural_map.pdf`

**Content**: Scatter plot showing all 109 countries/regions positioned on the two-dimensional cultural map.

**Visual elements**:
- Each point represents one country/region
- Points are colored by cultural region (8 colors)
- Country labels are displayed for identification
- Axis labels indicate value dimensions

**Interpretation guide**:
- **Upper-right quadrant** (Secular + Self-Expression): Protestant Europe, some English-Speaking
- **Lower-right quadrant** (Secular + Survival): Orthodox Europe, some Confucian
- **Upper-left quadrant** (Traditional + Self-Expression): Latin America
- **Lower-left quadrant** (Traditional + Survival): African-Islamic, West & South Asia

## Statistical Summary

### Cultural Region Centroids

| Region | Mean PC1 | Mean PC2 | N Countries | Characterization |
|--------|----------|----------|-------------|------------------|
| Protestant Europe | 3.45 | 2.12 | 8 | Most Secular + Self-Expression |
| Catholic Europe | 1.89 | 1.45 | 16 | Secular + Self-Expression |
| English-Speaking | 2.15 | 1.78 | 5 | Secular + Self-Expression |
| Confucian | 1.52 | -0.35 | 7 | Secular + Survival |
| Orthodox Europe | 0.85 | -0.92 | 16 | Moderate + Survival |
| Latin America | -0.45 | 0.65 | 16 | Traditional + Self-Expression |
| West & South Asia | -1.12 | -0.78 | 16 | Traditional + Survival |
| African-Islamic | -1.85 | -1.25 | 25 | Most Traditional + Survival |

### Extreme Countries

| Dimension | Highest | Value | Lowest | Value |
|-----------|---------|-------|--------|-------|
| PC1 (Secular) | Sweden | 4.25 | Jordan | -2.85 |
| PC2 (Self-Expression) | Sweden | 3.15 | Pakistan | -2.45 |

## Theoretical Background

### Inglehart-Welzel Theory

Ronald Inglehart and Christian Welzel proposed that economic development drives predictable cultural shifts:

1. **Industrialization** → Shift from Traditional to Secular-Rational values
2. **Post-industrialization** → Shift from Survival to Self-Expression values

This creates a diagonal "modernization trajectory" from lower-left to upper-right on the cultural map.

### Why This Matters for LLM Analysis

The IVS cultural map provides:
1. **Ground truth**: Empirically validated cultural positions for 109 countries
2. **Benchmark**: Reference for measuring LLM cultural imitation accuracy
3. **Framework**: Interpretable dimensions for understanding cultural differences

## Data Source

- `SI/pca/Table_S5_IVS_PCA_coordinates.csv` - 109 countries with PC1, PC2 coordinates and cultural region labels

**Original data**: Integrated Values Survey (IVS), combining:
- World Values Survey (WVS) waves 5-7
- European Values Study (EVS) wave 5

**PCA method**: Probabilistic PCA (PPCA) fitted on 10 IVS core value items

## Generation Script

```bash
python analysis/si/generate_figs1_cultural_map.py
```

## Usage Notes

1. **As reference layer**: This map appears as semi-transparent colored background points in all S2-S6 figures, maintaining the cultural region color coding
2. **For distance calculation**: LLM coordinates are compared to IVS coordinates using Euclidean distance
3. **For region analysis**: Countries are grouped by cultural region for aggregate statistics

