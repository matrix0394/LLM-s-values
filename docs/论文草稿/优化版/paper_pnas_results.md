## Results

### Baseline Language Effects in LLM Value Expression

Before examining cultural role-play, we first assessed baseline value expression by directly asking 23 large language models to respond to 10 Integrated Values Survey (IVS) items across six official United Nations languages (English, French, Spanish, Russian, Arabic, and Simplified Chinese), without any cultural role-play context (n = 138 model–language combinations). This analysis establishes whether prompt language alone affects expressed values.

Across all languages, models clustered in the secular–self-expression quadrant of the Inglehart–Welzel cultural map, indicating a general Western-leaning value profile. At the same time, expressed values varied substantially with prompt language. A one-way ANOVA revealed a significant language effect on the Traditional–Secular dimension (PC1; F = 3.38, p = 0.007), whereas no significant effect was observed on the Survival–Self-Expression dimension (PC2; F = 0.85, p = 0.52). English prompts yielded the most secular responses (mean PC1 = +2.69 ± 1.85), while Arabic prompts yielded the most traditional responses (mean PC1 = +0.98 ± 1.49), corresponding to a 1.71-unit shift along PC1. Pairwise comparisons confirmed that Arabic prompts elicited more traditional values than all other languages (all p < 0.05).

Language sensitivity varied markedly across models. The most stable model exhibited a 1.69-unit range across languages, whereas the least stable exhibited a 5.85-unit range. For example, one model ranged from PC1 = −0.70 when prompted in English to PC1 = +4.77 when prompted in Chinese, spanning nearly the full distance between Western Europe and East Asia on the cultural map. Together, these results indicate that expressed value orientations are strongly language dependent, even in the absence of cultural role-play. This baseline dependence is therefore taken into account when interpreting subsequent analyses.

### English-Speaking Countries Reveal a Baseline Cultural Bias

To establish a reference point under constant language conditions, we examined cultural alignment for 21 English-speaking countries, all evaluated using English prompts. Contrary to expectations, traditional English-speaking countries exhibited larger cultural distances than several African English-speaking countries. Ireland showed the largest distance (3.96), followed by Australia (2.83), New Zealand (2.63), and Canada (2.63), whereas Nigeria (1.03), Ghana (1.32), and Rwanda (1.23) ranked among the most accurately represented countries.

Deviation patterns were highly systematic. For all traditional English-speaking countries, model representations shifted toward more secular and more self-expressive positions relative to ground-truth IVS coordinates. Ireland illustrates this pattern: although its IVS position is moderately traditional (PC2 = −0.68), model representations placed it in a highly secular position (PC2 = +1.85), corresponding to a 2.52-unit shift. This pattern is consistent with the composition of English-language training data, which disproportionately reflects secular and progressive viewpoints. These results establish a baseline pattern of cultural deviation even when language is held constant.

### Overall Language Effects and Regional Reversal

Across 66 non–English-native countries evaluated in both English and native languages, English prompts yielded, on average, an 8.3% reduction in cultural distance relative to native-language prompts (p < 0.001). However, this aggregate effect concealed substantial cross-country variation. Individual countries ranged from a 33.5% native-language advantage (Switzerland) to a 27.3% English-language advantage (Tunisia).

The distribution of language effects was strongly asymmetric, with a long right tail of countries exhibiting large English advantages and comparatively few showing similarly large native-language advantages. When countries were grouped by cultural region, a clear regional reversal emerged. Non-Western regions—including Islamic/Arab, Orthodox/Slavic, West and South Asian, and Confucian societies—showed consistent English-language advantages, whereas Western European countries showed the opposite pattern, with higher accuracy under native-language prompting. We refer to this systematic regional reversal in language effects as *digital Orientalism*.

### East Asian Heterogeneity in Language Effects

To examine potential mechanisms underlying this regional asymmetry, we analyzed language effects within East Asia, a region sharing broad cultural traditions but exhibiting large differences in digital ecosystems and linguistic history. China showed near-perfect language parity (+0.07% English advantage) and the lowest mean cultural distance among all countries (0.97). Japan (+3.3%) and South Korea (+3.0%) likewise exhibited minimal English advantage.

In contrast, Taiwan and Hong Kong displayed among the strongest English advantages observed globally (+27.1% and +24.8%, respectively). Macao provided a contrasting case, exhibiting a strong Simplified Chinese advantage (−13.6%). These differences coincide with variation in native-language data availability and international English-language coverage, illustrating pronounced heterogeneity within a single cultural region.

### Latin American Variation Beyond Language Family

Latin American countries similarly exhibited wide variation in language effects, spanning a 25.6 percentage point range from +20.4% (Haiti) to −5.2% (Brazil). Haiti, the only French-speaking country in the region, showed the strongest English advantage. Several smaller Spanish-speaking countries also exhibited substantial English advantage despite sharing a language with Spain.

Brazil differed from this pattern, showing a native-language advantage. Across the region, language effects varied substantially even among countries sharing the same language family, indicating that language family alone does not account for observed differences in cultural alignment.

### Model Origin and Regional Specialization

To assess whether digital Orientalism reflects model-specific artifacts, we compared models by region of origin. Models developed in China showed weaker English-language advantages for Sino-Tibetan and Semitic languages than models developed in the United States, whereas European models showed strong native-language advantages for Slavic languages. At the same time, all model groups exhibited English advantages for certain non-Western regions.

These results indicate that model origin contributes to regional specialization in cultural representation but does not eliminate the observed regional asymmetry in language effects.

### Consistency and Robustness of the Effect

The regional reversal in language effects proved highly consistent across models. Nineteen of 21 models (90%) showed the same direction of language effect for Islamic countries, with higher accuracy under English prompting. Absolute performance varied across models, but the direction of language effects was independent of overall model accuracy.

Effect sizes were large. The contrast between Western and non-Western regions yielded a Cohen’s d of 1.43. Excluding outliers, varying PCA specifications, and restricting analyses to subsets of models all produced comparable results. Together, these analyses indicate that digital Orientalism is a large, consistent, and robust pattern across current large language models.

### Study 4. Colonial History and Contemporary Language Effects

We conducted exploratory analyses to test whether historical colonial relationships predict contemporary language effects in LLM cultural representation. Despite theoretically motivated hypotheses, we found limited evidence for systematic colonial history effects, highlighting the challenges of detecting historical influences in contemporary AI systems.

**Experiment 4a: Hong Kong vs Macao Comparison.** We compared English advantage in Hong Kong (British colony 1842–1997) with Portuguese advantage in Macao (Portuguese colony 1557–1999). Hong Kong showed a positive English advantage (M = 15.84%, 95% CI [−62.08, 93.76]), indicating better alignment under English than Chinese prompting on average. In contrast, Macao showed a negative Portuguese advantage (M = −15.67%, 95% CI [−90.35, 59.01]), indicating better alignment under Chinese than Portuguese prompting (Fig. S7B).

However, the difference between Hong Kong and Macao was not statistically significant (t(37.9) = 0.509, p = 0.614, Cohen's d = 0.161). The large confidence intervals and negligible effect size reflect substantial variance across models (Hong Kong SD = 179.23%; Macao SD = 170.37%), with individual models showing highly inconsistent patterns. This high variance prevented detection of systematic colonial language effects despite the theoretically motivated comparison.

**Experiment 4b: Latin American Language Variants.** We compared English advantage across Latin American countries with different colonial languages: Spanish-speaking countries (n = 11, M = 5.43%, SD = 10.17%), Portuguese-speaking Brazil (M = 3.58%), and French-speaking Haiti (M = 20.38%). One-way ANOVA revealed no significant differences across groups (F(2, 10) = 1.035, p = 0.391, η² = 0.171) (Fig. S7C). Despite a large effect size (η² = 0.171), the small sample sizes for Portuguese (n = 1) and French (n = 1) countries limited statistical power to detect differences.

**Experiment 4c: African Colonial History (Data Limitation).** We attempted to compare English advantage between African countries with and without British colonial history. However, we discovered that all British-colonized African countries in our dataset (Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia) only have English language data, lacking native language comparisons (Swahili, Yoruba, Akan, Zulu, Shona, Bemba) needed to calculate English advantage (Fig. S7D).

This data limitation reflects a systematic gap in multilingual AI evaluation: countries where English is an official language due to colonial history are often evaluated only in English, preventing assessment of native language representation. This prevented the planned analysis and highlights the need for more comprehensive multilingual evaluation datasets that include native languages of formerly colonized regions.

**Summary.** Our exploratory analyses found limited evidence for systematic colonial history effects on contemporary language representation in LLMs. The null findings may reflect: (1) genuine absence of colonial legacy effects in training data, (2) high variance across models masking systematic patterns, (3) insufficient statistical power due to small sample sizes, or (4) colonial effects being mediated by contemporary factors (e.g., current English usage, internet content distribution) that we could not control for. Future research with larger model samples, control variables for contemporary linguistic practices, and more comprehensive multilingual datasets may be better positioned to detect colonial history effects.

### Results Summary

Taken together, these results demonstrate a systematic regional asymmetry in how large language models represent cultural values across languages. Non-Western cultures are represented more accurately under English prompting, whereas Western European cultures show higher accuracy under native-language prompting. This pattern is consistent across models, regions, and analytical specifications, establishing digital Orientalism as a robust empirical phenomenon. Study 4's exploratory analyses of colonial history effects revealed methodological challenges and data limitations that inform future research on historical influences in AI systems.
