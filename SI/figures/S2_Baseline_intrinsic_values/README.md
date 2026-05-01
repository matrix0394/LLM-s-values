# S2: Baseline Intrinsic Values

This section presents LLM baseline responses (Stage 1) without cultural roleplay context, revealing the **intrinsic value orientations** embedded in each model.

## Key Findings

1. **Cross-model consistency is moderate** (mean = 51%): Different LLMs show substantial variation in their intrinsic values, suggesting training data and alignment strategies significantly shape model value orientations.

2. **Highest consensus on social liberalism**: Homosexuality acceptance (F118) shows 73% cross-model agreement, with most models scoring 10 (fully acceptable).

3. **Lowest consensus on autonomy**: The autonomy index (Y003) shows only 30% agreement, indicating divergent model perspectives on individual vs. collective priorities.

4. **Chinese models cluster toward Traditional-Survival**: Qwen and DeepSeek models position in the lower-left quadrant, reflecting Chinese training data characteristics.

5. **Most LLMs align with Western developed countries**: The majority of models fall in the Secular-Self-expression quadrant, similar to Protestant European and English-speaking countries.

## Experimental Design

| Parameter | Value |
|-----------|-------|
| Models tested | 23 LLMs |
| Questions | 10 IVS core items |
| Languages | 6 UN official languages (en, fr, es, ru, ar, zh-cn) |
| Consensus rounds | 5 rounds per question |
| Consensus method | Mode of 5 responses |

## Figure Organization

### A1: Per-Model Language Stability (23 panels)

**File**: `A1_per_model/FigS2A1_all_models_grid.pdf`

Each panel shows one model's responses across all 6 languages, overlaid on IVS country coordinates.

**Purpose**: Assess within-model language stability

**Interpretation**:
- Tightly clustered points → High language stability (model gives consistent answers regardless of prompt language)
- Scattered points → Language-dependent responses (model's values shift with prompt language)

### A2: Per-Language Model Distribution (6 panels)

**File**: `A2_per_language/FigS2A2_all_languages_grid.pdf`

Each panel shows all 23 models' responses in one language, overlaid on IVS country coordinates.

**Purpose**: Assess cross-model variation within each language

**Interpretation**:
- Clustered models → Language induces similar values across models
- Scattered models → Models maintain distinct value orientations regardless of language

## Statistical Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Mean cross-model consistency | 51% | Moderate agreement |
| Highest consistency question | F118 (Homosexuality) | 73% |
| Lowest consistency question | Y003 (Autonomy) | 30% |
| PC1 range (Traditional-Secular) | -0.71 to 6.64 | 7.35 units span |
| PC2 range (Survival-Self-expression) | -1.42 to 5.20 | 6.62 units span |

## Notable Model Positions

| Model | PC1 | PC2 | Characterization |
|-------|-----|-----|------------------|
| gemini-2.5-flash | -0.71 | 5.20 | Most Secular + Self-expression |
| gpt-4o-mini | 6.64 | -1.42 | Most Traditional + Survival |
| deepseek-chat | 2.63 | -0.44 | Traditional + Survival (Chinese model) |
| qwen3-max | 0.76 | -0.37 | Slightly Traditional + Survival (Chinese model) |
| gpt-4o | 0.81 | 1.05 | Moderate (near center) |

## Implications for Main Analysis

1. **Baseline heterogeneity matters**: The 7+ unit spread in PC1 means models start from very different "default" positions before roleplay.

2. **Language stability varies**: Some models (e.g., GPT-4o) show high language stability; others shift significantly with prompt language.

3. **Training data signature**: Chinese models' Traditional-Survival positioning likely reflects Chinese internet content characteristics.

## Generation Script

```bash
python analysis/si/generate_figs2_baseline.py
```

## Data Source

- `SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv` - 23 models × 6 languages baseline coordinates

