# Materials and Methods (PNAS Format)

**Target length: ~800 words**

## Data and Cultural Framework

We adopt the Inglehart–Welzel cultural map to locate societies in a two-dimensional value space defined by Survival versus Self-Expression values (PC1) and Traditional versus Secular-Rational values (PC2). Ground-truth cultural coordinates are obtained from the Integrated Values Survey (IVS), which combines World Values Survey Wave 7 (2017–2022) and European Values Study data, covering 109 countries and more than 90% of the world's population.

Following established practice, ten survey items that load strongly on the two dimensions are used: happiness (A008), interpersonal trust (A165), respect for authority (E018), political action (E025), importance of God (F063), attitudes toward homosexuality (F118) and abortion (F120), national pride (G006), post-materialism (Y002), and autonomy (Y003). These items define a fixed cultural coordinate system. All model-generated responses are projected into this predefined space rather than used to re-estimate the dimensions.

## Models

We evaluate 21 large language models developed in the United States, China, and Europe, spanning both small (<10B parameters) and large (≥10B) model classes. Models are accessed via official APIs between [Month–Month] 2025 using a fixed temperature of 0.1. Two small models are excluded due to systematically low response quality, defined as mean cultural distances exceeding three standard deviations from the IVS reference distribution.

## Experimental Design

Two experimental conditions are implemented.

**Intrinsic-value condition.** Models answer the ten survey questions without being assigned any national or cultural identity. To examine language dependence, the questionnaire is administered in the six official United Nations languages: Arabic, Chinese, English, French, Russian, and Spanish. Responses in this condition are interpreted as each model's default cultural orientation.

**Cultural imitation condition.** Models are instructed to role-play as a typical adult citizen of a specified country using a standardized system prompt. Sixty-six countries are included, selected to maximize geographic and cultural diversity while ensuring the availability of IVS reference data. Countries are grouped into eight cultural regions following established classifications. For non–English-native countries, surveys are administered both in English and in the country's official language(s); multilingual countries are evaluated separately for each official language. This design enables within-country comparisons that isolate the effect of prompt language while holding country identity constant.

For all model–language–condition combinations, each questionnaire is administered five times. The modal response across repetitions is used as the final answer, preserving the ordinal structure of survey items while reducing stochastic variation. For list-type questions, responses are normalized by sorting prior to mode calculation to ensure order invariance. Across all conditions, valid response rates exceed 95%.

## Response Validation and Quality Control

Responses are subject to multiple quality control procedures. First, all outputs are validated against strict format requirements using language-specific parsers. Single-choice items must return a single integer within the allowed range, and multi-choice items must satisfy predefined cardinality constraints. Responses containing explanatory text or invalid values are rejected.

If a response fails validation, the question is re-asked up to three times with progressively more explicit format instructions. Responses that fail all retries are marked invalid. Following IVS standards, entities are retained only if they provide valid answers to at least six of the ten items. When multiple interviews exist for the same model–country–language combination, only the most recent is retained.

Certain models require additional handling. Models that generate internal reasoning are instructed to suppress reasoning and return numeric answers only. Models with higher latency are assigned extended timeouts. All models are queried with identical temperature settings to minimize stochastic variation.

## Cultural Scoring and Dimensionality Reduction

Validated modal responses are assembled into a response matrix. For the post-materialism item (Y002), responses are converted to a three-level materialism score following standard coding rules. For the autonomy item (Y003), selected traits are aggregated into a traditional–secular index by contrasting traditional and secular-rational indicators.

Dimensionality reduction is performed using probabilistic principal component analysis (PPCA) to accommodate missing values. A fixed PPCA model is trained on IVS ground-truth data and then applied to all model-generated responses without refitting, ensuring a common coordinate system across conditions. Varimax rotation is applied to enhance interpretability while preserving orthogonality. Model-derived component scores are linearly rescaled to align with IVS coordinates using regression-based transformations.

Cultural alignment is quantified as the Euclidean distance between model-derived coordinates and the corresponding IVS country coordinates. Smaller distances indicate more accurate cultural representation. For non–English-native countries, an English advantage metric is computed as the relative reduction in distance under English-language prompting compared with native-language prompting.

## Statistical Analysis

Within-country comparisons between English and native-language conditions are conducted using paired t-tests, pairing observations by model. Effect sizes are reported as Cohen's *d*. Regional analyses aggregate paired differences within the eight cultural regions, with 95% confidence intervals computed from standard errors. Multiple comparisons are controlled using Bonferroni correction.

Robustness checks include Wilcoxon signed-rank tests and binomial sign tests, as well as analyses with and without outliers identified by interquartile range and 3σ criteria. All analyses are conducted in Python using standard scientific libraries.
