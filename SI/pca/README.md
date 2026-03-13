# Principal Component Analysis (PCA) Results - Supporting Information

Principal component analysis (PCA) was conducted on modal value profiles derived from five repeated interviews per condition. Supporting Information tables report entity-level PCA coordinates used for all visualizations. Raw PCA objects and intermediate outputs are available in the accompanying project repository.

Note: While the broader multilingual experiments cover 13 languages, the baseline PCA coordinates reported here (Table S6) are based on the six UN official languages to ensure cross-model comparability.

## Directory Structure

```
pca/
├── README.md                              # This file
├── Table_S5_IVS_PCA_coordinates.csv       # IVS/WVS country baseline coordinates
├── Table_S6_LLM_baseline_PCA_coordinates.csv  # LLM baseline (no cultural context)
├── Table_S7_LLM_roleplay_PCA_coordinates.csv  # LLM cultural imitation coordinates
└── Table_S8_PCA_component_summary.csv     # PCA component interpretation
```

## Table Descriptions

### Table S5: IVS/WVS Country PCA Coordinates

Country-level PCA coordinates from the Integrated Values Survey (IVS), serving as the reference cultural value map.

| Column | Description |
|--------|-------------|
| country | Country name |
| country_code | ISO 3166-1 numeric code |
| PC1 | First principal component (Survival vs. Self-Expression) |
| PC2 | Second principal component (Traditional vs. Secular-Rational) |
| cultural_region | Inglehart-Welzel cultural region classification |
| data_source | Data source identifier (IVS) |

### Table S6: LLM Baseline PCA Coordinates

PCA coordinates for LLMs responding without cultural context (baseline condition).

| Column | Description |
|--------|-------------|
| model_name | LLM model identifier |
| language | Survey language (6 UN official languages) |
| condition | Experimental condition (baseline) |
| PC1 | First principal component score |
| PC2 | Second principal component score |
| data_source | Data source identifier (LLM) |

Coordinates are projected onto the same PCA space defined by the IVS baseline.

### Table S7: LLM Roleplay PCA Coordinates

PCA coordinates for LLMs roleplaying as citizens of specific countries.

| Column | Description |
|--------|-------------|
| model_name | LLM model identifier |
| country | Target country for roleplay |
| country_code | ISO 3166-1 numeric code |
| language | Survey language |
| condition | Experimental condition (imitation) |
| PC1 | First principal component score |
| PC2 | Second principal component score |
| data_source | Data source identifier (LLM) |

Coordinates are projected onto the same PCA space defined by the IVS baseline.

### Table S8: PCA Component Summary

Interpretation of principal components based on Inglehart-Welzel cultural dimensions.

| Column | Description |
|--------|-------------|
| component | Principal component (PC1/PC2) |
| explained_variance_ratio | Proportion of variance explained |
| interpretation | Cultural dimension interpretation |
| key_items | WVS question IDs with largest absolute loadings |

## Methodology

- PCA was performed on standardized modal response profiles
- Coordinates are rescaled to match the IVS cultural map scale
- PC1 represents Survival vs. Self-Expression values (X-axis in Inglehart-Welzel map)
- PC2 represents Traditional vs. Secular-Rational values (Y-axis in Inglehart-Welzel map)

## Data Sources

Raw PCA objects and intermediate outputs are available in the accompanying project repository.
