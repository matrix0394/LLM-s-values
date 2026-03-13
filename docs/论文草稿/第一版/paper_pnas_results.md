# Results (PNAS Format)

**Target length: ~2,000 words**

## Baseline Language Effects in LLM Value Expression

Before examining cultural role-play, we first assessed baseline value expression by directly asking 23 large language models to respond to 10 Integrated Values Survey (IVS) items across six official United Nations languages (English, French, Spanish, Russian, Arabic, and Simplified Chinese), without any cultural role-play context (n = 138 model–language combinations). This analysis establishes whether prompt language alone affects expressed values.

Across all languages, models clustered in the secular–self-expression quadrant of the Inglehart–Welzel cultural map, indicating a general Western-leaning value profile. At the same time, expressed values varied substantially with prompt language. A one-way ANOVA revealed a significant language effect on the Traditional–Secular dimension (PC1; F = 3.38, p = 0.007), whereas no significant effect was observed on the Survival–Self-Expression dimension (PC2; F = 0.85, p = 0.52). English prompts yielded the most secular responses (mean PC1 = +2.69 ± 1.85), while Arabic prompts yielded the most traditional responses (mean PC1 = +0.98 ± 1.49), corresponding to a 1.71-unit shift along PC1. Pairwise comparisons confirmed that Arabic prompts elicited more traditional values than all other languages (all p < 0.05).

Language sensitivity varied markedly across models. The most stable model exhibited a 1.69-unit range across languages, whereas the least stable exhibited a 5.85-unit range. For example, one model ranged from PC1 = −0.70 when prompted in English to PC1 = +4.77 when prompted in Chinese, spanning nearly the full distance between Western Europe and East Asia on the cultural map. Together, these results indicate that expressed value orientations are strongly language dependent, even in the absence of cultural role-play. This baseline dependence is therefore taken into account when interpreting subsequent analyses.

---

## English-Speaking Countries Reveal a Baseline Cultural Bias

To establish a reference point under constant language conditions, we examined cultural alignment for 21 English-speaking countries, all evaluated using English prompts. Contrary to expectations, traditional English-speaking countries exhibited larger cultural distances than several African English-speaking countries. Ireland showed the largest distance (3.96), followed by Australia (2.83), New Zealand (2.63), and Canada (2.63), whereas Nigeria (1.03), Ghana (1.32), and Rwanda (1.23) ranked among the most accurately represented countries.

Deviation patterns were highly systematic. For all traditional English-speaking countries, model representations shifted toward more secular and more self-expressive positions relative to ground-truth IVS coordinates. Ireland illustrates this pattern: although its IVS position is moderately traditional (PC2 = −0.68), model representations placed it in a highly secular position (PC2 = +1.85), corresponding to a 2.52-unit shift. This pattern is consistent with the composition of English-language training data, which disproportionately reflects secular and progressive viewpoints. These results establish a baseline pattern of cultural deviation even when language is held constant.

---

## Overall Language Effects and Regional Reversal

Across 66 non–English-native countries evaluated in both English and native languages, English prompts yielded, on average, an 8.3% reduction in cultural distance relative to native-language prompts (p < 0.001). However, this aggregate effect concealed substantial cross-country variation. Individual countries ranged from a 33.5% native-language advantage (Switzerland) to a 27.3% English-language advantage (Tunisia).

The distribution of language effects was strongly asymmetric, with a long right tail of countries exhibiting large English advantages and comparatively few showing similarly large native-language advantages. When countries were grouped by cultural region, a clear regional reversal emerged. Non-Western regions—including Islamic/Arab, Orthodox/Slavic, West and South Asian, and Confucian societies—showed consistent English-language advantages, whereas Western European countries showed the opposite pattern, with higher accuracy under native-language prompting. We refer to this systematic regional reversal in language effects as *digital Orientalism*.

**Regional patterns**: Islamic/Arab countries exhibited the strongest English advantage (+17.4%, p < 0.0001), with all 12 Arab countries showing this pattern. Orthodox/Slavic countries showed comparable effects (+17.7%, p = 0.008). West and South Asian countries (+12.5%, p < 0.001) and Confucian countries (+7.8%, p < 0.01) also showed significant English advantages. In contrast, Western European countries showed native-language advantage (−11.5%, p = 0.03), with Protestant Europe (−20.3%, p < 0.001) and Catholic Europe (−12.4%, p < 0.01) exhibiting the strongest effects.

---

## East Asian Heterogeneity in Language Effects

To examine potential mechanisms underlying this regional asymmetry, we analyzed language effects within East Asia, a region sharing broad cultural traditions but exhibiting large differences in digital ecosystems and linguistic history. China showed near-perfect language parity (+0.07% English advantage) and the lowest mean cultural distance among all countries (0.97). Japan (+3.3%) and South Korea (+3.0%) likewise exhibited minimal English advantage.

In contrast, Taiwan and Hong Kong displayed among the strongest English advantages observed globally (+27.1% and +24.8%, respectively). Macao provided a contrasting case, exhibiting a strong Simplified Chinese advantage (−13.6%). These differences coincide with variation in native-language data availability and international English-language coverage, illustrating pronounced heterogeneity within a single cultural region.

The East Asian gradient—from China's near-perfect parity through Japan and Korea's minimal advantage to Taiwan and Hong Kong's strong English advantage—suggests that training data availability, cultural soft power (anime, K-pop), and colonial legacy (British Hong Kong vs. Portuguese Macao) interact to shape language effects. This within-region heterogeneity cannot be explained by baseline language effects alone, pointing to differences in how cultural knowledge is encoded across languages in training data.

---

## Latin American Variation Beyond Language Family

Latin American countries similarly exhibited wide variation in language effects, spanning a 25.6 percentage point range from +20.4% (Haiti) to −5.2% (Brazil). Haiti, the only French-speaking country in the region, showed the strongest English advantage. Several smaller Spanish-speaking countries also exhibited substantial English advantage despite sharing a language with Spain, suggesting that European Spanish training data does not fully transfer to Latin American variants.

Brazil differed from this pattern, showing a native-language advantage. As the world's largest Portuguese-speaking country with over 200 million speakers, Brazil has created a substantial Portuguese-language internet ecosystem that generates abundant training data. Across the region, language effects varied substantially even among countries sharing the same language family, indicating that language family alone does not account for observed differences in cultural alignment. Rather, the size and quality of native-language digital ecosystems, as well as language variants (European vs. Latin American Spanish/Portuguese), appear to play critical roles.

---

## Model Origin and Regional Specialization

To assess whether digital Orientalism reflects model-specific artifacts, we compared models by region of origin: Chinese (DeepSeek, Qwen, n = 3), US (GPT, Claude, n = 4), and European (Mistral, Gemini, n = 3). Models developed in China showed weaker English-language advantages for Sino-Tibetan languages (+1.9%) compared to US models (+16.8%, p < 0.01). For Semitic languages (Arabic), Chinese models showed +8.2% English advantage versus +19.6% for US models (p < 0.05). European models showed the strongest native-language advantages for Slavic languages (−43.3%).

At the same time, all model groups exhibited English advantages for certain non-Western regions. Chinese models still showed English advantage for Arabic countries (+8.2%), and US models showed native advantage for Germanic languages (−15.7%). These results indicate that model origin contributes to regional specialization in cultural representation but does not eliminate the observed regional asymmetry in language effects. Cultural proximity provides partial mitigation but not elimination of bias.

**Table 1** summarizes these model origin × language family interactions, showing that training data composition matters but no single model origin provides universal cultural competence.

---

## Consistency and Robustness of the Effect

The regional reversal in language effects proved highly consistent across models. Nineteen of 21 models (90%) showed the same direction of language effect for Islamic countries, with higher accuracy under English prompting. Absolute performance varied across models—GPT-4o achieved the lowest mean cultural distance (1.26), while small models showed 2–3× larger errors—but the direction of language effects was independent of overall model accuracy.

Effect sizes were large. The contrast between Western and non-Western regions yielded a Cohen's d of 1.43, indicating a very large effect by conventional standards. Excluding outliers (countries with distances > 2 SD), varying PCA specifications (varimax rotation, different numbers of components), and restricting analyses to subsets of models (top 5 performers, US models only, Chinese models only) all produced comparable results. Together, these analyses indicate that digital Orientalism is a large, consistent, and robust pattern across current large language models.

---

## Results Summary

Taken together, these results demonstrate a systematic regional asymmetry in how large language models represent cultural values across languages. Non-Western cultures are represented more accurately under English prompting, whereas Western European cultures show higher accuracy under native-language prompting. This pattern is consistent across models, regions, and analytical specifications, establishing digital Orientalism as a robust empirical phenomenon.

The pattern cannot be explained by baseline language effects alone: within-region heterogeneity (China vs. Taiwan, Hong Kong vs. Macao, Brazil vs. Haiti) points to differences in training data availability, colonial legacy, cultural soft power, and language variants. Model origin creates regional specialization but does not eliminate the fundamental asymmetry. The effect is large (Cohen's d = 1.43), consistent (19/21 models), and robust to analytical choices, suggesting a structural feature of how cultural knowledge is encoded in contemporary LLMs.
