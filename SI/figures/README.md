# SI Figures - Supporting Information

This directory contains all supplementary figures for the paper, organized by analysis theme. Each subdirectory includes a detailed README with key findings, statistical summaries, and interpretation guidance.

**Data**: 21 models × 66 countries/regions × 13 languages  
**Total Figures**: ~1,930

---

## Quick Reference: Key Findings by Section

| Section | Main Finding |
|---------|--------------|
| S1 | IVS cultural map shows 8 distinct cultural regions along Traditional-Secular and Survival-Self-Expression dimensions |
| S2 | LLM baseline values show 51% cross-model consistency; most models cluster in Secular-Self-Expression quadrant |
| S3 | GPT-4o achieves best imitation accuracy (d=1.26); 2.5× gap between best and worst models |
| S4 | Model size correlates with accuracy; small models are "culturally rigid" |
| S5 | English advantage follows geographic gradient: +16% for Islamic, -20% for Protestant Europe (Othering effect) |
| S6 | China shows exceptional accuracy (d=0.97); Taiwan/Hong Kong show anomalous English advantage (+27%) |
| Summary | Model factor explains 35% of variance; consistency correlates with accuracy (r=-0.65) |

---

## Directory Structure

```
SI/figures/
├── S1_IVS_cultural_map/                      # Reference map (1 figure)
├── S2_Baseline_intrinsic_values/             # LLM baseline (24 figures)
│   ├── A1_per_model/                         # 23 model panels
│   └── A2_per_language/                      # 6 language panels
├── S3_Imitated_contextual_values/            # Roleplay results (~1,889 figures)
│   ├── B1_per_model_languageAvg/             # 21 figures
│   ├── B2_per_country_modelAvg/              # 66 figures
│   ├── B3_per_model_per_country/             # ~1,386 figures
│   ├── B4_per_country_per_language/          # ~122 figures
│   └── B5_per_model_per_language/            # ~294 figures
├── S4_Model_and_response_analysis/           # Model analysis (4 figures)
├── S5_English_advantage_and_orientalism/     # Othering analysis (4 figures)
├── S6_East_Asia_analysis/                    # East Asia focus (3 figures)
└── summary/                                  # Statistical overview (4 figures)
```

---

## Section Summaries

### S1: IVS Cultural Map (1 figure)
**Purpose**: Reference map showing World Values Survey cultural coordinates for 109 countries.

**Key content**: Two-dimensional cultural map with PC1 (Traditional-Secular) and PC2 (Survival-Self-Expression) axes, colored by 8 cultural regions.

**Usage**: Ground truth for all distance calculations; appears as semi-transparent colored background in subsequent figures, maintaining cultural region color coding.

---

### S2: Baseline Intrinsic Values (24 figures)
**Purpose**: Reveal LLM intrinsic value orientations without cultural roleplay context.

**Key findings**:
- Cross-model consistency is moderate (51%)
- Most LLMs align with Western developed countries (Secular-Self-Expression)
- Chinese models cluster toward Traditional-Survival

**Figures**: Per-model language stability (A1) and per-language model distribution (A2)

---

### S3: Imitated Contextual Values (~1,889 figures)
**Purpose**: Comprehensive visualization of LLM cultural roleplay results.

**Key findings**:
- GPT-4o achieves best accuracy (d=1.26)
- Language itself carries cultural information (5.38 unit difference between German and Arabic)
- Systematic "Westernization" bias across all models

**Figures**: Five cross-tabulations (B1-B5) covering model, country, and language dimensions

---

### S4: Model and Response Analysis (4 figures)
**Purpose**: Analyze model behavior patterns and performance characteristics.

**Key findings**:
- Roleplay increases response variability 2-3×
- Model size correlates with accuracy (62% gap between large and small)
- Flexibility ≠ Accuracy (GPT-4o is moderate flexibility but best accuracy)

**Figures**: Consistency comparison (S4A), response distribution (S4B), model ranking (S4C), country difficulty (S4D)

---

### S5: English Advantage and Orientalism (4 figures)
**Purpose**: Test the "Othering" hypothesis — whether LLMs understand non-Western cultures through Western perspectives.

**Key findings**:
- Global English advantage = +8.3% (p < 0.001)
- Clear geographic gradient: Protestant Europe (-20%) → Islamic (+16%)
- Validates Said's Orientalism theory in LLM context

**Figures**: Regional comparison (S5A), distribution analysis (S5B), Islamic vs Western (S5C), geographic gradient (S5D)

---

### S6: East Asia Analysis (3 figures)
**Purpose**: Focused analysis of Confucian cultural sphere (China, Japan, Korea, Taiwan, Hong Kong, Macao).

**Key findings**:
- China shows exceptional accuracy (d=0.97, lowest globally)
- Taiwan and Hong Kong show anomalous English advantage (+27%, +25%)
- Colonial history matters: Hong Kong (British) vs Macao (Portuguese) show opposite patterns

**Figures**: Cultural trajectory (S6A), distance comparison (S6B), English advantage gradient (S6C)

---

### Summary: Statistical Overview (4 figures)
**Purpose**: Aggregate analyses across entire dataset.

**Key findings**:
- Model factor explains 35% of variance
- Consistency correlates with accuracy (r = -0.65)
- Clear model performance tiers (Tier 1: GPT-4o, DeepSeek)

**Figures**: Model×Country heatmap (Sx1), Model×Language heatmap (Sx2), rankings (Sx3), consistency scatter (Sx4)

---

## Generation Scripts

| Section | Script | Runtime |
|---------|--------|---------|
| S1 | `analysis/si/generate_figs1_cultural_map.py` | ~10s |
| S2 | `analysis/si/generate_figs2_baseline.py` | ~30s |
| S3-B1,B2 | `analysis/si/generate_figs3_b1b2.py` | ~2min |
| S3-B3 | `analysis/si/generate_figs3_b3.py` | ~30min |
| S3-B4 | `analysis/si/generate_figs3_b4.py` | ~5min |
| S3-B5 | `analysis/si/generate_figs3_b5.py` | ~10min |
| S4 | `analysis/si/generate_figs4_model_response.py` | ~1min |
| S5 | `analysis/si/generate_figs5_orientalism.py` | ~1min |
| S6 | `analysis/si/generate_figs6_east_asia.py` | ~30s |
| Summary | `analysis/si/generate_figs_summary.py` | ~2min |

**Generate all figures**:
```bash
# Run from project root
python analysis/si/generate_all_si_figures.py
```

---

## Data Sources

| Data | File | Description |
|------|------|-------------|
| IVS PCA | `SI/pca/Table_S5_IVS_PCA_coordinates.csv` | 109 countries reference |
| LLM Baseline | `SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv` | 23 models × 6 languages |
| LLM Roleplay | `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv` | 21 models × 66 countries × 14 languages |

---

## Notes for Paper Writing

1. **Terminology**: Taiwan, Hong Kong, Macao are labeled as "regions" (not "countries") throughout
2. **Format**: All figures are PDF (vector format) as required by PNAS
3. **Accessibility**: All colors are colorblind-safe
4. **Reproducibility**: Each subdirectory README contains exact generation commands

---

## Citation

If using these figures, please cite:
- IVS data: Inglehart et al., World Values Survey
- Cultural map framework: Inglehart & Welzel (2005)
- This analysis: [Your paper citation]

