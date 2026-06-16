# Supplementary Materials

Paper: *"The Value Atlas of AI: Mapping World Human Values in Large Language Models"*

## Directory Structure

```
Supplementary Materials/
├── README.md                              ← This file
├── clean_data.py                          ← Data cleaning script (project raw → clean CSV)
│
├── data/                                  ← Cleaned data files (20 models)
│   ├── DataS1_ivs_pca_coordinates.csv     ← Data S1: IVS 112-country PCA coordinates
│   ├── DataS2_llm_baseline_pca.csv        ← Data S2: Baseline PCA (20 models × 6 languages)
│   ├── DataS3_llm_roleplay_pca.csv        ← Data S3b: Roleplay PCA (20 models, 2662 rows)
│   ├── DataS3_prompts.json                ← Data S3a: Full prompts in 13 languages
│   ├── model_imitation_accuracy.csv       ← Model imitation accuracy rankings
│   ├── english_advantage_average.csv      ← Country-level English Advantage
│   ├── regression_data.csv                ← Regression data (Study 2 robustness)
│   ├── figure1_data_66countries.csv       ← Fig. 1 source data
│   ├── figure2_baseline_20models.csv      ← Fig. 2 source data
│   ├── figure3_digital_orientalism.csv    ← Fig. 3 source data
│   ├── figure4_colonial_history.csv       ← Fig. 3 Panel B–D source data
│   ├── study1_intrinsic_bias.json         ← Study 1 statistics
│   ├── study2_english_advantage.json      ← Study 2 statistics
│   ├── study3_digital_orientalism.json    ← Study 3 statistics
│   ├── study4_colonial_legacies.json      ← Study 4 statistics
│   ├── study5_model_imitation.json        ← Model imitation statistics
│   ├── paper_statistics_all.json          ← All paper statistics combined
│   └── llm_models_config.json             ← Model configuration (20 models)
│
└── figures/                               ← Generated figures (20-model, S1–S4)
    ├── FigS1/                             ← IVS cultural map
    ├── FigS2/                             ← Model imitation accuracy analysis
    ├── FigS3/                             ← English Advantage & Digital Orientalism
    ├── FigS4/                             ← East Asia analysis
    └── FigS5/                             ← Colonial history
```

---

## Data S1–S3 (for journal submission)

These three files constitute the primary supplementary data deposited with the journal.

| Data File | Contents | Rows | Format | Source |
|-----------|----------|------|--------|--------|
| **Data S1** | IVS PCA coordinates for 112 countries/territories | 112 | CSV | `data/country_values/country_scores_pca.json` → `clean_data.py` |
| **Data S2** | LLM baseline intrinsic value coordinates (Study 1) | 120 | CSV | `data/llm_pca/intrinsic/llm_pca_entity_scores.json` → `clean_data.py` |
| **Data S3a** | Full system prompts + 10 survey questions in 13 languages | — | JSON | `config/questions/multilingual/multilingual_questions_complete.json` + `src/roleplay_multilingual/multilingual_roleplay_interview.py` |
| **Data S3b** | LLM roleplay PCA coordinates (Studies 2–4) | 2,662 | CSV | `data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.json` → `clean_data.py` |

### Data S1 columns
`Country`, `Cultural Region`, `PC1` (Survival → Self-Expression), `PC2` (Traditional → Secular-Rational)

### Data S2 columns
`model`, `language`, `PC1`, `PC2`

### Data S3b columns
`model`, `country`, `language`, `PC1`, `PC2`, `Cultural Region`

---

## Supplementary Tables (in LaTeX, `paper/tables/`)

| Table | Content | Data Source |
|-------|---------|------------|
| Table S1 | WVS 10 survey items | WVS Wave 7 documentation |
| Table S2 | 20 LLM models and metadata | `config/models/llm_models.json` |
| Table S3 | ANOVA results (Study 1) | `study1_intrinsic_bias.json` |
| Table S4 | Model imitation accuracy ranking (Study 2) | `study5_model_imitation.json` |
| Table S5 | Country-level English Advantage (Study 2) | `results/analysis/stage0_vs_stage3/english_advantage_average.csv` |
| Table S6 | Language family analysis (Study 3) | `study3_digital_orientalism.json` → `language_families` |
| Table S7 | Model origin × region EA (Study 3) | `study3_digital_orientalism.json` → `model_origin` |
| Table S8 | Colonial legacy entity-level data (Study 4) | `study4_colonial_legacies.json` |
| Table S9 | Regional English Advantage summary (Study 3) | `study3_digital_orientalism.json` → `regional_analysis` |

---

## Supplementary Figures

| Figure | Content | Generation Script |
|--------|---------|-------------------|
| Fig. S1 | IVS cultural map (112 countries) | `analysis/si/generate_figs1_cultural_map.py` |
| Fig. S2 | Model imitation accuracy, size, source, origin (4 panels) | `src/figures/generate_figS2_model_imitation.py` |
| Fig. S3 | EA distribution + geographic gradient (2 panels) | `src/figures/generate_figS3_orientalism.py` |
| Fig. S4 | East Asia cultural coordinate analysis (3 panels) | `src/figures/generate_figS4_east_asia.py` |

Panels are combined into composite images by `src/figures/combine_supplementary.py`.

---

## Main Text Figures

| Figure | Content | Data Source | Generation Script |
|--------|---------|-------------|-------------------|
| Fig. 1 | LLM vs WVS cultural value world maps | `results/paper_data/figure1_data_66countries.csv` | `src/analysis/figure_data/regenerate_paper_data.py` |
| Fig. 2 | LLM intrinsic values across 6 UN languages | `results/paper_data/figure2_baseline_20models.csv` | `analysis/figures/generate_fig2_baseline.py` |
| Fig. 3 | Digital Orientalism geographic anatomy | `results/paper_data/figure3_digital_orientalism.csv` + `figure4_colonial_history.csv` | External (R/manual) |

---

## Data Source Mapping

All data are derived from project raw JSON/PKL files. `clean_data.py` filters to 20 models.

| SM File | Project Source | Transform |
|---------|---------------|-----------|
| `ivs_pca_coordinates.csv` | `data/country_values/country_scores_pca.json` | JSON → CSV |
| `llm_baseline_pca.csv` | `data/llm_pca/intrinsic/llm_pca_entity_scores.json` | JSON → CSV (filtered) |
| `llm_roleplay_pca.csv` | `data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.json` | JSON → CSV (filtered) |
| `english_advantage_average.csv` | `results/analysis/stage0_vs_stage3/english_advantage_average.csv` | Direct copy |
| `figure*_*.csv` | `results/paper_data/*.csv` | Direct copy |
| `study*.json` | `results/analysis/study*.json` | Direct copy |
| `paper_statistics_all.json` | `results/analysis/paper_statistics_all.json` | Direct copy |
| `llm_models_config.json` | `config/models/llm_models.json` | Direct copy |

---

## Reproduction Steps

### 1. Generate clean data

```bash
python3 "Supplementary Materials/clean_data.py"
```

### 2. Regenerate supplementary figures

```bash
python3 src/figures/generate_figS2_model_imitation.py
python3 src/figures/generate_figS3_orientalism.py
python3 src/figures/generate_figS4_east_asia.py
python3 src/figures/combine_supplementary.py
```

### 3. Run full paper analysis pipeline

```bash
python3 src/run/run_paper_analysis.py --all
```

---

## Citation Style

Science template style: `Fig. S1`, `Table S1`, `Data S1` (not "Supplementary Figure 1").

---

## Pending Items

- [ ] Verify model parameter counts and API versions in Table S2
- [ ] Sync English/Chinese Markdown documents with final table numbering
