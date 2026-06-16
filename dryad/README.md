# Dataset for: The Value Atlas of AI

## Overview

This directory contains the processed data package prepared for the manuscript
*The Value Atlas of AI: Mapping World Human Values in Large Language Models*.
It includes the processed interview tables, projected PCA coordinates,
regression covariates, and publication-ready source data required to reproduce
the reported analyses.

This public release is intentionally organized around a processed-data-first
workflow. It is designed to support reproducibility without redistributing the
full raw commercial API-response caches used during private data collection.

Associated code repository:

- [The-Value-Atlas-of-AI-Code](https://github.com/matrix0394/The-Value-Atlas-of-AI-Code)

Contact:

- Xinyi You (`3144308868qq@gmail.com`)

## How To Use This Package

The layout intentionally mirrors the relative paths expected by the cleaned
GitHub repository. To use these files with the released code:

1. Download and extract this Dryad package.
2. Copy the contents of this directory into the root of the GitHub repository.
3. Keep the relative paths unchanged so that `data/`,
   `Supplementary Materials/data/`, and `results/paper_data/` land exactly
   where the scripts expect them.

## Included Data

- `data/country_values/`
  Fixed IVS benchmark coordinates and the saved PCA model used for projection.
- `data/external/`
  Country-level regression covariates used by `run_paper_analysis.py`.
- `data/llm_interviews/intrinsic/`
  Released processed interview tables for the intrinsic multilingual pipeline.
- `data/llm_interviews/multilingual/`
  Released processed interview tables for the multilingual roleplay pipeline.
- `data/llm_pca/`
  Precomputed intrinsic and roleplay coordinate tables.
- `Supplementary Materials/data/`
  Publication-ready source data tables and supplementary data files released
  with the paper.
- `results/paper_data/regression_data.csv`
  The publication-ready regression table released with the paper.

## Data Not Included

The following items are intentionally excluded from this public package:

- `data/raw/Integrated_values_surveys_1981-2022.sav`
- the full `data/llm_interviews/*/interview_raw/` API-response caches

If benchmark reconstruction from raw survey data is required, the raw benchmark
source file should be recreated and placed under `data/raw/`. In the original
project, this merged IVS input was derived from:

- the EVS Trend File 1981-2017, Version `3.0.0` (DOI: `10.4232/1.14021`)
- the WVS Trend File 1981-2022, Version `4.1.0` (DOI: `10.14281/18241.27`)

## File Formats

- `.csv`
  Publication-ready tabular data and figure source data.
- `.json`
  Structured metadata, processed interview tables, and summary statistics.
- `.pkl`
  Serialized Python objects used by the accompanying code repository,
  particularly for PCA models and processed tables.

The `.pkl` files are intended to be used with the accompanying Python analysis
code and tested environment documented in the GitHub repository. Because pickle
serialization is sensitive to library versions, these files are most reliably
read with the accompanying code repository and its documented Python
environment, including the pinned package versions listed in
`requirements.lock.txt`.
