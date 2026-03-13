# Model Responses - Supporting Information

This directory summarizes large language model responses under baseline and contextualized value elicitation conditions. Raw and intermediate interview data are provided separately for reproducibility.

## Directory Structure

```
model_responses/
├── README.md                                    # This file
├── baseline_intrinsic_values/                   # Baseline condition (no cultural context)
│   ├── README.md
│   ├── Table_S1_baseline_modal_profiles.csv     # Modal responses per question
│   └── Table_S2_baseline_validity_summary.csv   # Validity and consistency metrics
└── imitated_contextual_values/                  # Cultural imitation condition
    ├── README.md
    ├── Table_S3_roleplay_modal_profiles.csv     # Modal responses per question
    └── Table_S4_roleplay_validity_summary.csv   # Validity and consistency metrics
```

## Data Description

### Modal Response Profiles (Table S1, S3)

Each row represents one question's modal response for a specific model-language-country combination:

| Column | Description |
|--------|-------------|
| model | LLM model identifier |
| condition | Experimental condition (baseline/imitation) |
| country | Target country (empty for baseline) |
| language | Survey language code |
| question_id | WVS question identifier (A008, A165, etc.) |
| value_dimension | Inglehart-Welzel dimension |
| modal_response | Most frequent response across 5 repetitions |
| consensus_count | Number of times modal response appeared |
| consistency_rate | Proportion of responses matching the mode |

### Validity Summary (Table S2, S4)

Aggregated metrics per model-language-country combination:

| Column | Description |
|--------|-------------|
| model | LLM model identifier |
| condition | Experimental condition |
| country | Target country |
| language | Survey language code |
| total_questions | Number of questions asked (10) |
| valid_responses | Number of parseable responses |
| invalid_responses | Number of unparseable responses |
| success_rate | Proportion of valid responses |
| mean_consistency_rate | Average consistency across questions |

## Methodology

- Each question was asked 5 times per model-language-country combination
- Modal response (mode) was calculated from the 5 repetitions
- Consistency rate measures response stability across repetitions
- All analyses in the main text use modal responses

## Data Sources

Raw interview data available at: `data/llm_values/interview_raw/` and `data/roleplay_multilingual/llm_responses_roleplay_ml/`
