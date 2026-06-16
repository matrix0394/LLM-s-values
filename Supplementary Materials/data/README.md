# Supplementary Data for "The Value Atlas of AI: Mapping World Human Values in Large Language Models"

This repository contains the supplementary data files referenced in the paper.
## Contents

- `DataS1_ivs_pca_coordinates.csv`
  - Inteçgrated Values Survey (IVS) cultural coordinates for 112 countries and territories.
  - Main columns: country or territory name, cultural region, PC1 (Self-Expression vs. Survival), and PC2 (Secular-Rational vs. Traditional).

- `DataS2_llm_baseline_pca.csv`
  - Baseline intrinsic-value coordinates for 20 large language models under the non-roleplay condition.
  - Each row corresponds to one model-language combination.
  - Main columns include model name, prompt language, PC1, and PC2.

- `DataS3_llm_roleplay_pca.csv`
  - Roleplay-condition PCA coordinates for 20 large language models across countries or territories and languages.
  - Each row corresponds to one model-country-language observation.
  - Main columns include model name, country or territory, prompt language, cultural region, PC1, and PC2.

- `DataS3_prompts.json`
  - Full prompt templates and multilingual survey materials used in the roleplay and questionnaire pipeline.
  - Includes system prompts and question text used to administer the World Values Survey items across languages.
