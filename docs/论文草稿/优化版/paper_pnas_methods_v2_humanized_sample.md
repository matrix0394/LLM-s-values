# Materials and Methods (Humanized Sample)

## Overview

To understand how human values are embedded in large language models, we designed four complementary studies. In Study 1, we examine what value orientations LLMs express when they're not assigned any cultural identity—essentially asking whether they lean toward secular-rational and self-expression values compared to human populations. Study 2 then investigates a practical question: does it matter whether we prompt models in English or in a country's official language when trying to capture that country's cultural values? Building on this, Study 3 tests for what we call "digital Orientalism"—the possibility that non-Western cultures might actually be represented more accurately through English than through their own languages, perhaps because of how training data is structured. Finally, Study 4 takes an exploratory look at whether colonial history might help explain some of these language effects.

## Common Framework and Data (Studies 1–4)

**Cultural map and ground truth.** Our analysis relies on the Inglehart–Welzel cultural map, which positions countries in a two-dimensional space based on their values. The first dimension (PC1) captures Survival versus Self-Expression values, while the second (PC2) reflects Traditional versus Secular-Rational values. We obtained ground-truth coordinates for 66 countries from the Integrated Values Survey (IVS), which combines data from World Values Survey Wave 7 (2017–2022) and the European Values Study. While the full IVS dataset covers 109 countries (representing about 90% of the world's population), our 66-country subset still represents approximately 62% of the global population. 

To construct these coordinates, we use ten survey items that previous research has shown load strongly on these two dimensions: happiness (A008), interpersonal trust (A165), respect for authority (E018), political action (E025), importance of God (F063), attitudes toward homosexuality (F118) and abortion (F120), national pride (G006), post-materialism (Y002), and autonomy (Y003).

**Models.** We evaluated 23 large language models (listed in SI Appendix, Table S1), including models developed in the United States (n = 13), China (n = 8), and Europe (n = 2). These span both small (<10B parameters, n = 7) and large (≥10B parameters, n = 16) model classes. All models were accessed through API endpoints between February and December 2025, with temperature set to 0.1 to ensure relatively consistent responses.

**Projection into cultural space.** To compare model responses with human survey data, we project all model outputs into the same Inglehart–Welzel space. We do this using probabilistic principal component analysis (PPCA) trained on the IVS ground-truth data, then apply this trained model to project model responses without refitting. This gives us a consistent way to measure cultural alignment: we simply calculate the Euclidean distance between where a model's responses place it and where the IVS data says a country actually is. Smaller distances mean better alignment.

---

## Study 1. Intrinsic Value Orientations of Large Language Models

**Research question.** What value orientations do LLMs express when they're not given any cultural context, and how do these compare to human populations?

**Design.** To answer this, we presented the ten survey questions to models without assigning them any national or cultural identity. The system prompt simply instructed models to act as a survey response system, outputting only numeric answers in a strict format. We deliberately avoided mentioning any country, nationality, or cultural context.

Since we wanted to check whether the language itself might influence responses, we administered the questionnaire in six official UN languages: Arabic (ar), Simplified Chinese (zh-cn), English (en), French (fr), Russian (ru), and Spanish (es). We tested all 23 models in all six languages, giving us 138 model–language combinations to analyze.

For reliability, we ran each questionnaire five times per model–language combination and took the modal (most common) response as our final answer. For list-type questions like autonomy, we sorted responses before calculating the mode to avoid order effects. We validated all outputs against strict format requirements—if a model produced explanatory text or invalid values, we rejected the response and tried again (up to three times). Following IVS standards, we only kept model–language combinations that provided valid answers to at least six of the ten items.

**Analysis.** After collecting responses, we projected them into the Inglehart–Welzel value space. This required some preprocessing: for post-materialism (Y002), we converted responses to a three-level score (0 = materialist, 1 = mixed, 2 = post-materialist) following IVS coding rules. For autonomy (Y003), we aggregated selected traits into a traditional–secular index. The PPCA extraction yielded two principal components explaining 42% and 28% of variance respectively. We applied Varimax rotation to make the components more interpretable, then linearly rescaled the scores to align with IVS coordinates.

Our analysis focused on three questions:

1. **How do LLM values compare to human values?** We calculated mean LLM coordinates across all 138 model–language combinations and compared them descriptively with the distribution of IVS country coordinates (n = 66). This tells us whether LLMs tend to cluster in the secular-rational and self-expression quadrant relative to human populations.

2. **Do different languages produce different values?** We used one-way ANOVA to test whether mean PC1 and PC2 coordinates differed significantly across the six UN languages, followed by Tukey HSD post-hoc tests to identify which specific language pairs differed. We report F-statistics, p-values, and the range of language effects (the difference between the highest and lowest mean coordinate across languages).

3. **How stable are individual models across languages?** For each model, we calculated the range (max − min) and standard deviation of its PC1 and PC2 coordinates across the six languages. This measures cross-linguistic stability—models with smaller ranges are more consistent in their value expression regardless of language.

**Primary outcome measures.** Cultural coordinates (PC1, PC2) for each model–language combination. Full statistical comparisons across languages and models are provided in SI Appendix.

