# S6: East Asia Analysis

This section presents a focused analysis of **East Asian countries/regions** (China, Japan, South Korea, Taiwan, Hong Kong, Macao), revealing unique patterns in cultural imitation and language effects within the Confucian cultural sphere.

## Key Findings

1. **China shows exceptional imitation accuracy**: Mean distance = 0.97 (lowest among all 66 countries), with virtually no English advantage (+0.07%). This reflects abundant high-quality Chinese training data.

2. **Taiwan and Hong Kong show anomalous English advantage**:
   - Taiwan: +27.1% (highest in East Asia, 2nd globally)
   - Hong Kong (Cantonese): +24.8%
   - Hong Kong (Simplified Chinese): +15.8%
   
   This likely reflects international media coverage and limited Traditional Chinese/Cantonese training data.

3. **Japan and South Korea show balanced performance**: English advantage is minimal (+3.3% and +3.0% respectively), indicating sufficient Japanese and Korean training data.

4. **Macao shows strong native Chinese advantage**: Simplified Chinese outperforms English by 13.6%, contrasting sharply with Hong Kong despite similar political status. Portuguese (colonial legacy language) shows minimal difference (+1.8%).

5. **Colonial history matters**: Hong Kong (former British colony) shows strong English advantage; Macao (former Portuguese colony) shows native Chinese advantage — reflecting different international media attention and training data composition.

## East Asian Countries/Regions Overview

| Country/Region | Official Language(s) | IVS PC1 | IVS PC2 | Cultural Position |
|----------------|---------------------|---------|---------|-------------------|
| China | Simplified Chinese | 0.42 | -0.85 | Traditional-Survival |
| Japan | Japanese | 2.15 | 0.32 | Secular-Moderate |
| South Korea | Korean | 1.89 | 0.15 | Secular-Moderate |
| Taiwan | Traditional Chinese | 1.45 | -0.22 | Moderate-Survival |
| Hong Kong | Cantonese/Simplified | 1.78 | 0.45 | Secular-Moderate |
| Macao | Simplified Chinese/Portuguese | 1.52 | 0.28 | Moderate |

Note: Macao has three language conditions: Simplified Chinese (native), Portuguese (colonial legacy), and English.

## Figure Descriptions

### S6A: East Asia Cultural Coordinate Trajectory

**File**: `FigS6A_east_asia_trajectory.pdf`

**Content**: Scatter plot showing real IVS coordinates vs LLM-generated coordinates for all East Asian countries/regions.

**Visual elements**:
- ★ (Gold star): Real IVS coordinates (ground truth)
- Colored shapes: Language-specific model averages
- Light points: All individual model data points
- Arrows: Direction of deviation from real coordinates

**Key observations**:
- All regions show systematic shift toward Secular-Self-expression quadrant
- China shows smallest deviation (tightest clustering around star)
- Taiwan shows largest deviation and highest variance
- Hong Kong shows clear language-dependent clustering

**Interpretation**: LLMs exhibit "Westernization" bias — shifting all East Asian cultures toward Western European value positions.

### S6B: East Asia Distance Comparison

**File**: `FigS6B_east_asia_distance_comparison.pdf`

**Content**: Grouped bar chart comparing cultural distance across languages for each East Asian country/region.

**Bars per country**:
- Native language distance (e.g., Japanese for Japan)
- English distance
- (For multilingual regions: additional language bars)

**Key observations**:
- China: Native ≈ English (both ~0.97)
- Japan: Native slightly > English (1.85 vs 1.79)
- Taiwan: Native >> English (2.73 vs 1.99)
- Hong Kong: Native >> English (2.07 vs 1.56 for Cantonese)

**Interpretation**: English advantage is strongest for regions with limited native-language training data (Taiwan, Hong Kong) and absent for regions with abundant data (China, Japan).

### S6C: East Asia English Advantage Gradient

**File**: `FigS6C_east_asia_english_gradient.pdf`

**Content**: Horizontal bar chart showing English advantage for all East Asian country-language pairs, sorted by magnitude.

**Color coding**:
- Dark red (>20%): Strong English advantage
- Orange (10-20%): Moderate English advantage
- Green (0-10%): Slight English advantage
- Blue (<0%): Native advantage

**Key observations**:
- Taiwan (zh-tw): +27.1% — Strongest English advantage
- Hong Kong (zh-hk): +24.8% — Strong English advantage
- Hong Kong (zh-cn): +15.8% — Moderate English advantage
- Japan (ja): +3.3% — Minimal difference
- Korea (ko): +3.0% — Minimal difference
- China (zh-cn): +0.07% — No difference
- Macao (zh-cn): -13.6% — Native Chinese advantage
- Macao (pt): +1.8% — Colonial language, minimal difference

**Interpretation**: The gradient reveals a clear pattern — regions with high international media attention but limited native-language data show English advantage; regions with abundant native data show no advantage or native advantage.

## Statistical Summary

### Distance and English Advantage by Region

| Region | Language | Distance | English Distance | English Advantage |
|--------|----------|----------|------------------|-------------------|
| Taiwan | zh-tw | 2.73 | 1.99 | **+27.1%** |
| Hong Kong | zh-hk | 2.07 | 1.56 | **+24.8%** |
| Hong Kong | zh-cn | 1.85 | 1.56 | **+15.8%** |
| Japan | ja | 1.85 | 1.79 | +3.3% |
| South Korea | ko | 1.50 | 1.45 | +3.0% |
| China | zh-cn | 0.97 | 0.97 | +0.07% |
| Macao | zh-cn | 1.30 | 1.48 | **-13.6%** |
| Macao | pt (colonial) | 1.51 | 1.48 | +1.8% |

Note: For Macao, Simplified Chinese (zh-cn) is the actual native language, while Portuguese (pt) is a colonial legacy language. The native Chinese advantage (-13.6%) contrasts sharply with Hong Kong despite similar political status.

### Training Data Quality Inference

| Language | Inferred Quality | Evidence |
|----------|------------------|----------|
| Simplified Chinese (zh-cn) | Excellent | China lowest distance, Macao native advantage |
| Japanese (ja) | Good | Minimal English advantage (+3.3%) |
| Korean (ko) | Good | Minimal English advantage (+3.0%) |
| Traditional Chinese (zh-tw) | Limited | High English advantage (+27.1%) |
| Cantonese (zh-hk) | Limited | High English advantage (+24.8%) |

## Theoretical Implications

### Why Taiwan and Hong Kong Show Anomalous Patterns

1. **Limited training data**: Traditional Chinese and Cantonese have smaller internet footprints than Simplified Chinese
2. **High international attention**: Both regions receive extensive English-language media coverage (political, financial)
3. **Western perspective dominance**: LLMs may understand these regions primarily through English news sources

### Hong Kong vs Macao Contrast

Despite similar political status (Special Administrative Regions of China), Hong Kong and Macao show opposite patterns:

- **Hong Kong**: Former British colony → Strong English advantage (+24.8% for Cantonese, +15.8% for Simplified Chinese)
- **Macao**: Former Portuguese colony → Portuguese shows slight advantage over English (+1.8%), reflecting colonial linguistic legacy

Interestingly, for Macao, while Portuguese (colonial language) slightly outperforms English, Simplified Chinese significantly outperforms both (-13.6% vs English). This suggests that actual daily language usage (Simplified Chinese dominates Macao) matters more than colonial history for LLM cultural knowledge.

### China's Exceptional Performance

China shows the best imitation accuracy among all 66 countries because:
1. Massive Simplified Chinese internet ecosystem
2. High-quality Chinese training data in major LLMs
3. Chinese models (DeepSeek, Qwen) particularly excel on China

## Model Performance on East Asia

| Model | China Distance | Japan Distance | Korea Distance | Taiwan Distance |
|-------|----------------|----------------|----------------|-----------------|
| deepseek-chat | 0.36 | 1.52 | 1.28 | 2.15 |
| gpt-4o | 0.85 | 1.45 | 1.35 | 1.89 |
| qwen3-max | 0.72 | 1.68 | 1.42 | 2.31 |
| claude-3-7-sonnet | 1.12 | 1.78 | 1.55 | 2.45 |

**Key observation**: Chinese models (DeepSeek, Qwen) significantly outperform Western models on China, demonstrating training data advantage.

## Implications

1. **For China studies**: LLMs provide accurate cultural representations; native Chinese prompts work well
2. **For Taiwan/Hong Kong studies**: Consider using English prompts for more accurate results (counterintuitive but empirically supported)
3. **For Japan/Korea studies**: Either language works; no significant advantage
4. **For model selection**: Chinese models excel on East Asian contexts

## Generation Script

```bash
python analysis/si/generate_figs6_east_asia.py
```

## Data Sources

All data is computed directly from SI/pca files (self-contained):
- `SI/pca/Table_S5_IVS_PCA_coordinates.csv` - IVS reference coordinates
- `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv` - LLM roleplay coordinates

East Asian countries/regions are identified by ISO codes: CN, JP, KR, TW, HK, MO.

