# Baseline Intrinsic Values - Model Responses

This directory contains summarized LLM responses from the baseline condition, where models responded to World Values Survey questions without any cultural context or roleplay instructions.

## Experimental Condition

- **Condition**: Baseline (no cultural framing)
- **Languages**: 6 UN official languages (en, fr, es, ru, ar, zh-cn)
- **Repetitions**: 5 per question
- **Analysis Method**: Modal response (most frequent answer)

## Files

| File | Description |
|------|-------------|
| `Table_S1_baseline_modal_profiles.csv` | Modal responses for each model-language-question combination |
| `Table_S2_baseline_validity_summary.csv` | Validity and consistency metrics per model-language |

## Key Metrics

- **Modal Response**: The most frequently occurring response across 5 repetitions
- **Consistency Rate**: Proportion of responses matching the mode (range: 0.2-1.0)
- **Success Rate**: Proportion of valid (parseable) responses

## Notes````````````````

- Baseline responses represent each LLM's intrinsic cultural values
- No country-specific or cultural context was provided
- Results serve as the reference point for measuring cultural adaptation
