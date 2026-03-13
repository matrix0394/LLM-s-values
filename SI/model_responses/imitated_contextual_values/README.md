# Imitated Contextual Values - Model Responses

This directory summarizes model responses under contextualized imitation prompts, where models were instructed to answer as typical citizens of specified countries. These results are used to evaluate how LLM value profiles shift under explicit national-context instructions.

## Experimental Condition
- Condition: Imitation (national context; roleplay as a typical citizen of a specified country)
- Models: 21 LLMs
- Countries: 66 countries
- Languages: 13 languages total; **for multilingual countries, multiple native/official language variants were evaluated** according to the predefined country–language mapping used in the prompts.
- Questions: 10 value-related questions
- Runs: 5 independent repetitions per model × country × language × question

## Files
- `Table_S3_roleplay_modal_profiles.csv`
  - Modal response profiles aggregated across the 5 runs (used for all analyses unless otherwise noted).
- `Table_S4_roleplay_validity_summary.csv`
  - Summary statistics for response validity and stability (e.g., success rate, consistency).

## Key Metrics
- **modal_response**: The most frequent response among 5 runs.
- **consensus_count**: Number of runs matching the modal response (1–5).
- **consistency_rate**: consensus_count / 5 (range: 0.2–1.0, since 5 runs were collected).

## Notes
- The **question set is identical** across baseline and imitation conditions; only the instruction context differs.
- No additional demographic attributes were specified beyond the national-context instruction.
- Full raw and intermediate outputs are maintained in the project repository; SI tables report analysis-ready modal profiles and stability summaries.
