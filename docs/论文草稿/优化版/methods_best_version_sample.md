# Materials and Methods (Best Version - Combining Both Approaches)

## Overview

To quantify how human values are expressed by large language models, we organized our work into four complementary studies. Study 1 estimates models' value coordinates when no country identity is provided and compares these with survey benchmarks in the Inglehart–Welzel value space. Study 2 evaluates whether language matters in country role-play by contrasting English prompting with official-language prompting for the same country. Study 3 tests for "digital Orientalism" by examining whether English prompting yields systematically smaller cultural distances for non-Western regions while Western Europe shows the opposite pattern. Study 4 conducts pre-specified case comparisons to see whether language effects differ across contexts with distinct colonial-language exposures.

## Common Framework and Data (Studies 1–4)

**Cultural map and ground truth.** Our analysis uses the Inglehart–Welzel cultural map, which positions countries in a two-dimensional value space. PC1 captures Survival versus Self-Expression values, and PC2 reflects Traditional versus Secular-Rational values. We obtained benchmark coordinates for 66 countries from the Integrated Values Survey (IVS), which combines World Values Survey Wave 7 (2017–2022) with the European Values Study. The full IVS dataset covers 109 countries (about 90% of the world population); our 66-country subset represents approximately 62% under the IVS/WVS coverage definition.

To construct model- and survey-based coordinates in the same space, we use ten WVS items commonly employed for the Inglehart–Welzel map: happiness (A008), interpersonal trust (A165), respect for authority (E018), political action (E025), importance of God (F063), attitudes toward homosexuality (F118) and abortion (F120), national pride (G006), post-materialism (Y002), and autonomy (Y003).

**Models.** We evaluated 23 large language models (SI Appendix, Table S1), including models developed in the United States (n = 13), China (n = 8), and Europe (n = 2). These include small (<10B parameters, n = 7) and large (≥10B parameters, n = 16) model classes. All models were accessed via API endpoints between February and December 2025 with temperature set to 0.1.

**Projection into cultural space.** We project model outputs into the Inglehart–Welzel space using probabilistic principal component analysis (PPCA) trained on IVS ground-truth data, then apply this trained mapping to model responses without refitting. We quantify cultural alignment as the Euclidean distance between the model-derived coordinate and the corresponding IVS coordinate; smaller distances indicate closer alignment.

---

## Study 1. Intrinsic Value Orientations of Large Language Models

**Research question.** What value orientations do LLMs express when no cultural context is provided, and how do these compare to human populations?

**Design.** We presented the ten survey questions to models without assigning any national or cultural identity. The system prompt instructed models to function as a survey response system outputting only numeric answers in a strict format. No country, nationality, or cultural context was mentioned.

To examine whether language itself influences baseline value expression, we administered the questionnaire in six official UN languages: Arabic (ar), Simplified Chinese (zh-cn), English (en), French (fr), Russian (ru), and Spanish (es). We tested all 23 models in all six languages, yielding 138 model–language combinations.

Each questionnaire was presented five times per model–language combination, with the modal response used as the final answer. For list-type questions (autonomy), responses were normalized by sorting before mode calculation. All outputs were validated against strict format requirements; responses containing explanatory text or invalid values were rejected and reissued up to three times. Following IVS standards, we retained model–language combinations only if they provided valid answers to at least six of the ten items.

**Analysis.** We projected responses into the Inglehart–Welzel value space. For post-materialism (Y002), responses were converted to a three-level score (0 = materialist, 1 = mixed, 2 = post-materialist) following IVS coding rules. For autonomy (Y003), selected traits were aggregated into a traditional–secular index. PPCA extracted two principal components (explaining 42% and 28% of variance); Varimax rotation enhanced interpretability. Component scores were linearly rescaled to align with IVS coordinates.

We assessed intrinsic value orientations and language effects through three analyses:

1. **Descriptive comparison with human values.** We computed mean LLM coordinates across all 138 model–language combinations and compared them descriptively with the mean and distribution of IVS country coordinates (n = 66), examining whether LLM values tend toward the secular-rational and self-expression quadrant relative to human populations.

2. **Language-specific effects.** We conducted one-way ANOVA to test whether mean PC1 and PC2 coordinates differed significantly across the six UN languages, followed by Tukey HSD post-hoc pairwise comparisons. We report F-statistics, p-values, and the range of language effects (maximum − minimum mean coordinate across languages).

3. **Model stability across languages.** For each model, we computed the range (max − min) and standard deviation of PC1 and PC2 coordinates across the six languages as measures of cross-linguistic stability. Smaller ranges indicate more consistent value expression across languages.

**Primary outcome measures.** Cultural coordinates (PC1, PC2) for each model–language combination. Statistical comparisons across languages and models are detailed in SI Appendix.

