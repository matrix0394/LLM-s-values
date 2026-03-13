# Materials and Methods

## Overview

We conducted four studies to characterize how large language models express and represent cultural values across languages. Study 1 establishes models' intrinsic value profiles in the absence of cultural role-play. Study 2 evaluates models' ability to imitate country-specific cultural values under explicit role-play instructions. Study 3 develops a unified scoring pipeline that maps model outputs into the Inglehart–Welzel cultural value space and quantifies cultural alignment. Study 4 analyzes language effects, regional patterns, and robustness of cultural imitation performance.

## Common Framework and Data (Studies 1–4)

**Cultural map and ground truth.** We adopt the Inglehart–Welzel cultural map to locate both model-expressed values and country-level cultural profiles in a two-dimensional value space defined by Survival versus Self-Expression values (PC1) and Traditional versus Secular-Rational values (PC2). Ground-truth cultural coordinates for 66 countries are obtained from the Integrated Values Survey (IVS), which integrates World Values Survey Wave 7 (2017–2022) and European Values Study data, covering more than 400,000 individual survey responses across 109 countries.

Following established practice, we use ten survey items that load strongly on the two dimensions: happiness (A008), interpersonal trust (A165), respect for authority (E018), political action (E025), importance of God (F063), attitudes toward homosexuality (F118) and abortion (F120), national pride (G006), post-materialism (Y002), and autonomy (Y003). These items define a fixed cultural coordinate system; all model-generated responses are scored on these items and projected into this established space.

**Models and querying setup.** We evaluate 23 large language models (SI Appendix, Table S1), developed in the United States (n = 10), China (n = 8), and Europe (n = 5), spanning both small (<10B parameters, n = 7) and large (≥10B parameters, n = 16) classes. Models include GPT-4o, Claude-3.5-Sonnet, Gemini-2.0-Flash, DeepSeek-V3, Qwen-2.5-72B, Mistral-Large, and others, selected to maximize diversity in origin, architecture, and scale. Models are accessed via API endpoints between February and December 2024 using a fixed temperature of 0.1 to minimize stochastic variation.

Across all model–language–condition combinations, each questionnaire is administered five times. The modal response across repetitions is used as the final answer to reduce stochastic variation while preserving the ordinal structure of survey items. For list-type questions (e.g., autonomy traits), responses are normalized by sorting prior to mode calculation to ensure order invariance.

**Response validation and quality control.** All outputs are validated against strict format requirements using language-specific parsers. Single-choice items must return a single integer within the allowed range (e.g., 1–10 for happiness), and multi-choice items must satisfy predefined cardinality constraints (e.g., exactly five traits for autonomy). Responses containing explanatory text, reasoning traces, or invalid values are rejected.

If a response fails validation, the question is reissued up to three times with progressively more explicit format instructions. Responses that fail all retries are marked invalid. Following IVS standards, model–country–language entities are retained only if they provide valid answers to at least six of the ten items. Across all conditions, valid response rates exceed 95%.

Certain models require additional handling: models that generate internal reasoning (e.g., o1-series) are instructed to suppress reasoning and return numeric answers only; models with higher latency are assigned extended timeouts (up to 60 seconds per question). All models are queried using identical temperature settings (0.1) and system-level instructions.

## Study 1. Intrinsic Value Profiles of Large Language Models

**Design.** In the intrinsic-value condition, models answer the ten survey questions without being assigned any national or cultural identity. The standardized prompt format is: "Please answer the following questions about your values and beliefs. For each question, provide only the numeric answer corresponding to your choice." No country, nationality, or cultural context is mentioned.

To examine language dependence in baseline value expression, the questionnaire is administered in the six official United Nations languages: Arabic, Chinese (Simplified), English, French, Russian, and Spanish. Each of the 23 models is evaluated in all six languages, yielding 138 model–language combinations.

**Outcome.** For each model and language, responses to the ten items are converted into item scores following IVS coding rules (see Study 3) and projected into the Inglehart–Welzel value space. The resulting coordinates (PC1, PC2) represent the model's intrinsic value profile under a given prompt language. Language effects on intrinsic values are assessed using one-way ANOVA with language as the factor and model as the unit of observation.

## Study 2. Cultural Imitation via Country Role-Play

**Design.** In the cultural imitation condition, models are prompted to respond as a typical adult citizen of a specified country. The standardized system prompt format is: "You are a typical adult citizen of [Country]. Please answer the following questions about values and beliefs as a typical [Country] citizen would. For each question, provide only the numeric answer." (See SI Appendix for full prompts in all 13 languages.)

Sixty-six countries are included, selected to maximize geographic and cultural diversity while ensuring the availability of IVS reference data. Countries are grouped into eight cultural regions following established classifications: Western Europe (n = 15), Eastern Europe (n = 10), Latin America (n = 11), Islamic/Arab (n = 8), Sub-Saharan Africa (n = 7), Confucian (n = 5), South Asia (n = 5), and Orthodox/Slavic (n = 5).

For non–English-native countries (n = 66), surveys are administered both in English and in the country's official language(s). Languages are selected based on official language status and speaker population. Thirteen languages are evaluated: Arabic, Chinese (Simplified and Traditional), Dutch, English, French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish, and Turkish. Multilingual countries are evaluated separately for each major official language (e.g., Canada: English and French; Switzerland: German, French, Italian; Belgium: Dutch and French). This design enables within-country comparisons of prompt language while holding country identity and model constant.

For English-native countries (n = 21), surveys are administered only in English, providing a baseline for cultural alignment under constant language conditions.

All 23 models are included in Study 1. For Study 2, two small models (Llama-3.2-3B and Qwen-2.5-3B) are excluded due to systematically low response quality, defined as mean cultural distances exceeding three standard deviations from the IVS reference distribution, resulting in 21 models for cultural role-play analyses.

**Outcome.** For each retained model, country, and prompt language, responses are projected into the same cultural space as IVS ground truth (see Study 3). Cultural imitation performance is quantified by the distance between model-derived coordinates and IVS country coordinates. Language effects are assessed by comparing English-language and native-language distances within the same country and model.

## Study 3. Cultural Scoring, Projection, and Distance Metrics

**Item coding.** Validated modal responses are assembled into a response matrix with rows representing model–country–language entities and columns representing the ten survey items. For the post-materialism item (Y002), responses are converted to a three-level materialism score (0 = materialist, 1 = mixed, 2 = post-materialist) following standard IVS coding rules based on priority rankings of four goals. For the autonomy item (Y003), respondents select five traits from eleven options; selected traits are aggregated into a traditional–secular index by contrasting traditional indicators (obedience, religious faith) with secular-rational indicators (independence, imagination, tolerance).

**Projection into the Inglehart–Welzel space.** Dimensionality reduction is performed using probabilistic principal component analysis (PPCA) to accommodate missing values. A fixed PPCA model is trained on IVS ground-truth data (66 countries × 10 items) and then applied to all model-generated responses without refitting, ensuring a common coordinate system across conditions. Two principal components are extracted, explaining 42% and 28% of variance respectively. Varimax rotation is applied to enhance interpretability while preserving orthogonality. The first rotated component (PC1) corresponds to the Survival–Self-Expression dimension; the second (PC2) corresponds to the Traditional–Secular dimension.

Model-derived component scores are linearly rescaled to align with IVS coordinates using regression-based transformations. Specifically, for each component, we fit a linear regression predicting IVS country scores from model-derived scores using the subset of observations where both are available, then apply the fitted transformation to all model-derived scores. This ensures that model coordinates are directly comparable to IVS coordinates in terms of scale and origin.

**Cultural distance and language advantage.** Cultural alignment is quantified as the Euclidean distance between model-derived coordinates (PC1_model, PC2_model) and the corresponding IVS country coordinates (PC1_IVS, PC2_IVS):

Distance = √[(PC1_model − PC1_IVS)² + (PC2_model − PC2_IVS)²]

Smaller distances indicate more accurate cultural representation. For non–English-native countries, an English advantage metric is computed as the relative reduction in distance under English-language prompting compared with native-language prompting, holding the country identity and model constant:

English Advantage (%) = 100 × (Distance_native − Distance_English) / Distance_native

Positive values indicate better performance under English prompting; negative values indicate better performance under native-language prompting.

## Study 4. Statistical Analysis of Cultural Imitation Performance

Study 4 analyzes the patterns, determinants, and robustness of cultural imitation performance observed in Studies 2 and 3. We conduct eight sets of analyses to characterize language effects, regional patterns, language family patterns, model origin effects, model quality effects, distance–advantage coupling, and robustness.

**Design.** All analyses use the cultural distance data from Study 3 as the primary outcome. For non–English-native countries, we compute an English advantage metric for each model–country pair:

English Advantage (%) = 100 × (Distance_native − Distance_English) / Distance_native

Positive values indicate better performance under English prompting; negative values indicate better performance under native-language prompting. This metric enables direct comparison of language effects across countries with different baseline distances.

**Analysis 1: Language effects on intrinsic value expression.** In the intrinsic-value condition (Study 1), language effects on expressed values are assessed using one-way ANOVA with prompt language (six levels) as the factor, separately for PC1 (Traditional–Secular) and PC2 (Survival–Self-Expression), treating each model as the unit of observation (n = 23 models × 6 languages = 138 observations). Post hoc pairwise comparisons use Tukey's HSD test to identify which language pairs differ significantly. This analysis establishes whether prompt language alone systematically shifts expressed values in the absence of cultural role-play.

**Analysis 2: Language effects on cultural imitation and regional patterns.** In the cultural imitation condition (Study 2), language effects are evaluated within the same country and model by contrasting imitation distances under English prompting versus native-language prompting. For each non–English-native country, we use paired t-tests across the 21 models to assess whether mean distances differ between English and native language(s). We quantify the magnitude using the English advantage metric defined above.

Regional summaries are obtained by aggregating country-level English advantage estimates within the eight cultural regions (Western Europe, Eastern Europe, Latin America, Islamic/Arab, Sub-Saharan Africa, Confucian, South Asia, Orthodox/Slavic) and testing whether the mean regional advantage differs from zero using one-sample t-tests. Regional comparisons use two-sample t-tests to identify which regions show significantly different language effects. This analysis tests whether language effects vary systematically across cultural contexts.

**Analysis 3: Language family stratification.** To assess whether language effects generalize beyond individual languages, we aggregate countries by language family based on linguistic classification: Germanic (German), Romance (Spanish, French, Italian, Portuguese), Slavic (Russian), Semitic (Arabic), Sino-Tibetan (Simplified Chinese, Traditional Chinese, Cantonese), Japonic (Japanese), and Koreanic (Korean). For each language family, we compute the mean English advantage across all model–country pairs where the native language belongs to that family. Paired t-tests compare native-language and English distances within each family, controlling for model and country effects. We test for heterogeneity across families using between-family comparisons and report corresponding effect sizes (Cohen's d).

**Analysis 4: Digital Orientalism (distance–advantage coupling).** To evaluate whether English advantage systematically increases with cultural dissimilarity from Western societies, we examine the association between (i) a country's cultural distance from an English-speaking reference point in the Inglehart–Welzel space (computed as the Euclidean distance from the mean coordinates of traditional English-speaking countries using IVS data) and (ii) the country's English advantage during cultural imitation. We compute Pearson and Spearman correlations between cultural distance and English advantage across all non–English-native countries. This analysis tests whether larger cross-cultural gaps correspond to larger relative gains under English prompting, consistent with a structured regional reversal pattern termed *digital Orientalism*.

**Analysis 5: Model origin effects.** To assess whether model origin influences language effects, we compare English advantage metrics across three model origin groups: United States-developed (n = 10), China-developed (n = 8), and Europe-developed (n = 3). For each cultural region and language family, we test whether mean English advantage differs across model origins using two-sample t-tests. This analysis tests whether models show regional specialization based on their origin—for example, whether Chinese models exhibit weaker English advantages for Sino-Tibetan languages than US models, or whether European models show stronger native-language advantages for geographically proximate cultures.

**Analysis 6: Model quality stratification.** Because low-quality outputs can inflate distances and distort relative advantages, we perform stratified analyses by model quality. Model quality is operationalized as each model's mean imitation distance averaged across all countries and languages (after applying response-validity filters). We compare English advantage across quality tiers (top 50% vs bottom 50% based on median distance) and test whether language effects are stronger or weaker among higher-performing models using two-sample t-tests. We also exclude systematically low-quality models (mean distance >3 SD from the overall mean) and recompute all analyses to ensure robustness.

**Analysis 7: Model characteristics.** We examine whether language effects vary by model characteristics: (i) model size (parameters: <10B vs ≥10B), (ii) model source (open-source vs closed-source), and (iii) model vendor (OpenAI, Anthropic, Google, Meta, DeepSeek, Alibaba, Mistral). For each characteristic, we compute mean English advantage and test for between-group differences using two-sample t-tests or ANOVA. This analysis tests whether architectural or organizational factors systematically influence multilingual cultural representation.

**Analysis 8: Robustness and sensitivity.** We assess robustness through five sensitivity analyses: (i) alternative distance metrics (Manhattan distance, Mahalanobis distance), (ii) alternative PCA specifications (no rotation, oblique rotation, different numbers of components), (iii) exclusion of outliers (countries with distances >2 SD from regional mean), (iv) alternative model subsets (large models only ≥10B parameters; excluding specific model families), and (v) alternative language groupings (geographic regions instead of linguistic families). For each sensitivity analysis, we recompute English advantage metrics and test whether the direction and significance of regional patterns remain consistent. Key conclusions are considered robust if they hold across all or most sensitivity specifications.

**Effect sizes and statistical reporting.** Effect sizes are reported using Cohen's d for between-group comparisons and paired Cohen's d for within-group comparisons. For regional analyses, we report both mean differences and standardized effect sizes. Consistency across models is quantified as the proportion of models showing the same directional effect (e.g., English advantage > 0 for a given country or region). All statistical tests use two-tailed tests with α = 0.05 unless otherwise specified. For multiple comparisons within analysis sets, we report both uncorrected p-values and note when results survive Bonferroni correction.

**Data availability.** All model responses, IVS reference data, analysis code, and supplementary materials are available at [repository URL]. The study was conducted in accordance with institutional guidelines for AI research; no human subjects were involved.

---

**Word count**: ~1,500 words
