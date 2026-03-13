# Materials and Methods

## Overview

We conducted four studies to characterize human values embedded in large language models and their alignment with real-world cultural values. Study 1 estimates LLMs' intrinsic value orientations and compares them with IVS benchmarks. Study 2 investigates language-dependent differences in cultural representation, testing whether English versus official-language prompting systematically affects alignment accuracy. Study 3 tests whether language effects differ systematically between Western and non-Western countries. Study 4 conducts pre-specified case comparisons to examine associations between colonial history and contemporary language effects.

## Common Framework and Data (Studies 1–4)

**Cultural map and ground truth.** We adopt the Inglehart–Welzel cultural map, a two-dimensional value space defined by Survival versus Self-Expression values (PC1) and Traditional versus Secular-Rational values (PC2). Ground-truth cultural coordinates for 66 countries are obtained from the Integrated Values Survey (IVS), integrating World Values Survey Wave 7 (2017–2022) and European Values Study data. The IVS dataset covers 109 countries representing approximately 90% of the world's population; our 66-country subset represents approximately 62% of the world's population. We use ten survey items that load strongly on the two dimensions: happiness (A008), interpersonal trust (A165), respect for authority (E018), political action (E025), importance of God (F063), attitudes toward homosexuality (F118) and abortion (F120), national pride (G006), post-materialism (Y002), and autonomy (Y003).

**Models.** We evaluate 23 large language models (SI Appendix, Table S1) developed in the United States (n = 13), China (n = 8), and Europe (n = 2), spanning small (<10B parameters, n = 7) and large (≥10B parameters, n = 16) classes. Models are accessed via API endpoints between February and December 2025 using temperature = 0.1.

**Projection into cultural space.** All model responses are projected into the Inglehart–Welzel space using probabilistic principal component analysis (PPCA) trained on IVS ground-truth data, then applied to model responses without refitting. Cultural alignment is quantified as Euclidean distance between model-derived and IVS coordinates; smaller distances indicate more accurate representation.

---

## Study 1. Intrinsic Value Orientations of Large Language Models

**Research question.** What value orientations do LLMs express when no cultural context is provided, and how do these coordinates compare with IVS benchmarks?

**Design.** We assess LLMs' default value orientations by presenting the ten survey questions without assigning any national or cultural identity. Models receive a system prompt instructing them to function as a survey response system that outputs only numeric answers, with strict formatting requirements to ensure parseable responses. No country, nationality, or cultural context is mentioned in the prompts.

To examine language dependence in baseline value expression, the questionnaire is presented in six official United Nations languages: Arabic (ar), Chinese Simplified (zh-cn), English (en), French (fr), Russian (ru), and Spanish (es). Each of the 23 models is evaluated in all six languages, yielding 138 model–language combinations.

Each questionnaire is presented five times per model–language combination. The modal response across repetitions is used as the final answer. For list-type questions (autonomy), responses are normalized by sorting prior to mode calculation. All outputs are validated against strict format requirements; responses containing explanatory text or invalid values are rejected and reissued up to three times. Following IVS standards, model–language combinations are retained only if they provide valid answers to at least six of the ten items.

**Analysis.** We projected responses into the Inglehart–Welzel value space. For post-materialism (Y002), responses were converted to a three-level score (0 = materialist, 1 = mixed, 2 = post-materialist) following IVS coding rules. For autonomy (Y003), selected traits were aggregated into a traditional–secular index. PPCA extracted two principal components; Varimax rotation enhanced interpretability. We treat this PPCA mapping as fixed to ensure that model-derived coordinates are expressed in the same reference frame as IVS benchmarks. Component scores were linearly rescaled to align with IVS coordinates.

We summarize intrinsic coordinates and language effects in three complementary ways:

1. **Descriptive comparison with IVS benchmarks.** We computed mean LLM coordinates across all 138 model–language combinations and compared them with the mean and distribution of IVS country coordinates (n = 66), focusing on relative location in the PC1–PC2 plane.

2. **Language-specific effects.** We tested whether mean PC1 and PC2 differed across the six UN languages using one-way ANOVA, followed by Tukey HSD pairwise comparisons (details in SI Appendix).

3. **Model stability across languages.** For each model, we computed the range (max − min) and standard deviation of PC1 and PC2 across the six languages as measures of cross-linguistic stability.

**Primary outcome measures.** Projected coordinates (PC1, PC2) for each model–language combination.

---

## Study 2. Language-Dependent Differences in Cultural Representation

**Research question.** Does prompting language affect cultural representation accuracy when models roleplay as country citizens?

**Design.** We evaluate cultural representation by instructing models to roleplay as typical citizens of 66 countries. Models receive a system prompt that frames the task as a cultural values survey and instructs them to respond from the perspective of someone who grew up in the target country and shares its common cultural values. The prompt explicitly states: "You are roleplaying as a typical citizen from [Country]. Answer all questions from the perspective of someone who grew up in [Country] and shares the common cultural values of that society." (SI Appendix provides full prompts in all 13 languages.)

The 66 countries maximize geographic and cultural diversity while ensuring IVS reference data availability. Countries are grouped into eight cultural regions following established classifications (regional membership detailed in SI Appendix): Protestant Europe, Catholic Europe, English-Speaking, Orthodox Europe, Latin America, African-Islamic, Confucian, and West & South Asia.

For non–English-speaking countries (n = 45), surveys are presented in both English and the country's official language(s), enabling within-country language comparisons. For English-speaking countries where English is a primary official language (n = 21), surveys are presented only in English. Countries are included in language comparison analyses only when both English and non-English official language data are available; countries with English as the sole evaluation language form a separate English-only group. The 13 evaluated languages are listed in SI Appendix. Multilingual countries are evaluated separately for each official language (e.g., Switzerland: German, French, Italian).

Two small models (Llama-3.2-3B and Qwen-2.5-3B) are excluded due to low compliance with the numeric-only schema (high invalid-response rates under retries), which also resulted in extreme distances relative to IVS benchmarks. We retained 21 models. Each model–country–language combination is queried five times; modal responses are used. Response validation and projection procedures follow Study 1.

**Analysis.** For each non–English-speaking country, we compute model-level English advantage for each of the 21 models:

ΔD<sub>m</sub> = D<sub>m,native</sub> − D<sub>m,English</sub>

where D<sub>m,native</sub> and D<sub>m,English</sub> are the Euclidean distances between model m's derived coordinates and IVS coordinates under official-language and English prompting. Country-level English advantage is then computed as:

English Advantage (%) = 100 × mean(ΔD<sub>m</sub>) / mean(D<sub>m,native</sub>)

Positive values indicate better alignment under English; negative values indicate better alignment under the official language.

We quantify language effects through four complementary analyses:

1. **Paired t-tests by country.** For each country, we test whether ΔD<sub>m</sub> differs significantly from zero across 21 models using one-sample t-tests on model-level ΔD<sub>m</sub>.

2. **Consistency analysis.** We compute the proportion of models showing English advantage (ΔD<sub>m</sub> > 0) as a descriptive measure of cross-model consistency for each country.

3. **Effect size quantification.** We report paired Cohen's d = mean(ΔD<sub>m</sub>) / SD(ΔD<sub>m</sub>) for each country.

4. **Regional aggregation.** We aggregate English advantage within eight regions and test whether regional means differ from zero using one-sample t-tests.

**Primary outcome measures.** 
- Cultural distance: D = Euclidean distance between model-derived and IVS coordinates
- English advantage: ΔD (%) = 100 × (D<sub>native</sub> − D<sub>English</sub>) / D<sub>native</sub>

Statistical tests and effect sizes are detailed in SI Appendix.

---

## Study 3. Digital Orientalism in Non-Western Cultural Representation

**Research question.** Do language effects (English vs official language) differ systematically between Western and non-Western countries?

**Design.** We examine whether the English advantage identified in Study 2 systematically varies between Western and non-Western countries. Countries are classified into two primary groups (Western, n = 29; non-Western, n = 37) based on pre-specified region labels (SI Appendix). Western countries include Protestant Europe, Catholic Europe, and English-Speaking regions. Non-Western countries span African-Islamic, Orthodox Europe, Confucian, Latin America, and West & South Asia regions. Complete regional membership and country lists are detailed in SI Appendix.

We further stratify non-Western countries by cultural region to test for heterogeneity in the Orientalism effect and identify which regions show the strongest asymmetries.

**Analysis.** We characterize the digital Orientalism pattern through four analyses:

1. **Binary Western vs non-Western comparison.** We compare mean English advantage between Western and non-Western countries using independent-samples t-tests. Effect sizes are reported using Cohen's d.

2. **Regional stratification.** We compute mean English advantage within each of the eight cultural regions (Protestant Europe, Catholic Europe, English-Speaking, Orthodox Europe, Latin America, African-Islamic, Confucian, West & South Asia) and test whether each region's mean differs significantly from zero using one-sample t-tests. This identifies which specific regions drive the overall Orientalism effect and reveals regional heterogeneity. We report means, standard errors, 95% confidence intervals, and significance levels for each region.

3. **Distance–advantage coupling analysis.** We examine whether the magnitude of English advantage is systematically associated with a country's cultural distance from Western reference points. Cultural distance from the West is operationalized as the Euclidean distance in the Inglehart–Welzel space between each country's IVS coordinates and the mean IVS coordinates of English-speaking countries. We compute both Pearson correlation (assuming linear relationships) and Spearman correlation (robust to non-linear monotonic relationships) between cultural distance from the West and English advantage.

4. **Model origin effects.** We test whether model origin influences the magnitude of the Orientalism effect by comparing English advantage across US-developed, China-developed, and Europe-developed models. For each cultural region, we compare mean English advantage between model origin groups.

**Primary outcome measures.** English advantage (ΔD) aggregated by cultural region and model origin. Statistical comparisons and correlations are detailed in SI Appendix.

---

## Study 4. Colonial History and Contemporary Language Effects (Exploratory)

**Research question.** Are contemporary language effects in LLM value representation associated with historical colonial relationships?

**Design.** We conduct pre-specified case comparisons to examine associations between colonial history and contemporary language effects. Cases were selected to minimize obvious differences in geography and institutional context while varying colonial language exposure.

*Experiment 4a: Hong Kong vs Macao comparison.* Both Hong Kong and Macao are Special Administrative Regions of China with similar political status, economic development levels (both high-income), geographic proximity (both in the Pearl River Delta), and ethnic composition (both predominantly ethnic Chinese). However, they differ sharply in colonial history: Hong Kong was under British rule (1842–1997), while Macao was under Portuguese rule (1557–1999). We compare English advantage in Hong Kong with Portuguese advantage in Macao, computed analogously as:

Portuguese Advantage (%) = 100 × (Distance<sub>Chinese</sub> − Distance<sub>Portuguese</sub>) / Distance<sub>Chinese</sub>

where Distance<sub>Chinese</sub> and Distance<sub>Portuguese</sub> are mean Euclidean distances under Chinese (zh-cn) and Portuguese (pt) prompting across all 21 models. This comparison holds constant geography, culture, and development while varying colonial language.

*Experiment 4b: Latin American language variants.* Within Latin America, we compare English advantage across countries with different colonial languages: Spanish-speaking countries (n = 11: Argentina, Bolivia, Chile, Colombia, Ecuador, Guatemala, Mexico, Nicaragua, Peru, Uruguay, Venezuela), Portuguese-speaking Brazil (n = 1), and French-speaking Haiti (n = 1). All three groups share geographic region (Americas) but differ in colonial language. We test whether English advantage varies systematically across these groups.

*Experiment 4c: Systematic biases in African country representation.* For African countries where only English-language data are available (n = 11: Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia, Tanzania, Uganda, Botswana, Namibia, Malawi), we examine whether LLM representations under English prompting show systematic directional biases relative to IVS ground truth. We compute the mean coordinate difference (model-derived minus IVS) separately for PC1 (Survival vs Self-Expression) and PC2 (Traditional vs Secular-Rational) across all 21 models. Positive values indicate systematic bias toward Self-Expression (PC1) or Secular-Rational (PC2) values; negative values indicate bias toward Survival or Traditional values. We test whether these biases differ significantly from zero using one-sample t-tests.

**Analysis.** For Experiments 4a and 4b, we compare English advantage (or colonial language advantage) between groups using appropriate statistical tests. For Experiment 4a, we compare Hong Kong's English advantage with Macao's Portuguese advantage using an independent-samples t-test with Welch's correction for unequal variances (n = 20 models per region; one additional model beyond the two low-quality models excluded from all role-play studies lacks Portuguese or Traditional Chinese support). For Experiment 4b, we compare mean English advantage across Spanish-speaking, Portuguese-speaking, and French-speaking Latin American countries using one-way ANOVA. For Experiment 4c, we test whether mean coordinate differences (PC1 and PC2) differ significantly from zero using one-sample t-tests, and report Cohen's d as a measure of bias magnitude.

**Primary outcome measures.** 
- Experiments 4a-4b: Colonial language advantage: ΔD<sub>colonial</sub> (%) = 100 × (D<sub>Chinese</sub> − D<sub>colonial</sub>) / D<sub>Chinese</sub> for Hong Kong (English) and Macao (Portuguese)
- Experiment 4c: Mean coordinate bias: Δ<sub>PC1</sub> = mean(PC1<sub>model</sub> − PC1<sub>IVS</sub>) and Δ<sub>PC2</sub> = mean(PC2<sub>model</sub> − PC2<sub>IVS</sub>) across African countries

Statistical tests are detailed in SI Appendix.

---

**Note on scope.** This study focuses on direct group comparisons. More comprehensive analyses controlling for contemporary socioeconomic factors (GDP, internet penetration, English proficiency) and testing mediation mechanisms (contemporary English usage patterns) require additional data not available in the current study and are left for future research.

---

## Statistical Reporting and Robustness

All statistical tests use two-tailed tests with α = 0.05 unless otherwise specified. Effect sizes are reported using Cohen's d for between-group comparisons (d = [M₁ − M₂] / SD<sub>pooled</sub>) and paired Cohen's d for within-group comparisons (d = M<sub>diff</sub> / SD<sub>diff</sub>). For multiple comparisons within analysis sets, we report both uncorrected p-values and note when results survive Bonferroni correction (α<sub>corrected</sub> = 0.05 / n<sub>comparisons</sub>).

**Robustness checks.** Key findings are tested for robustness:

1. **Model quality filtering.** Two small models (Llama-3.2-3B and Qwen-2.5-3B) are excluded from Studies 2–4 due to low compliance with the numeric-only schema (high invalid-response rates under retries), which also resulted in extreme distances relative to IVS benchmarks. All reported results use the filtered set of 21 models.

2. **Large models only.** We repeat analyses on models with ≥10B parameters (n = 16) to test whether findings are driven by small models with potentially lower cultural knowledge (details in SI Appendix).

3. **Model origin consistency.** We assess whether the digital Orientalism pattern holds across models developed in different regions (US, China, Europe). Results are reported by model origin in SI Appendix.

**Data availability.** All model responses, IVS reference data, analysis code, and supplementary materials are available at [repository URL]. The study was conducted in accordance with institutional guidelines for AI research; no human subjects were involved. All data collection complied with the terms of service of the respective API providers.

---

**Sample summary:**
- Study 1: 138 model-language combinations (23 models × 6 languages)
- Studies 2–4: Approximately 2,900 model-country-language combinations (21 models × 66 countries × 1.85 languages average)
- Each combination evaluated 5 times; modal responses used for analysis
- Each evaluation consists of 10 survey items
- Coverage: 66 countries representing approximately 62% of world population
