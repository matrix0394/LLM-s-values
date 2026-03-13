# Study 4 - Methods Section (Revised)

## Study 4. Colonial History and Contemporary Language Effects (Exploratory)

**Research question.** Are contemporary language effects in LLM value representation associated with historical colonial relationships?

**Design.** We conduct exploratory analyses to test whether colonial history predicts contemporary language effects using three natural experiments that leverage quasi-experimental variation in colonial history while controlling for confounding factors such as geographic proximity, economic development, and ethnic composition.

*Experiment 4a: Hong Kong vs Macao comparison.* Both Hong Kong and Macao are Special Administrative Regions of China with similar political status, economic development levels (both high-income), geographic proximity (both in the Pearl River Delta), and ethnic composition (both predominantly ethnic Chinese). However, they differ sharply in colonial history: Hong Kong was under British rule (1842–1997), while Macao was under Portuguese rule (1557–1999). We compare English advantage in Hong Kong with Portuguese advantage in Macao, computed analogously as:

Portuguese Advantage (%) = 100 × (Distance_Chinese − Distance_Portuguese) / Distance_Chinese

where Distance_Chinese and Distance_Portuguese are mean Euclidean distances under Chinese (zh-cn) and Portuguese (pt) prompting across all 21 models. If colonial history shapes contemporary language effects, Hong Kong should show stronger English advantage than Macao shows Portuguese advantage, reflecting the greater global dominance of English and differential representation in training data. This comparison holds constant geography, culture, and development while varying colonial language.

*Experiment 4b: Latin American language variants.* Within Latin America, we compare English advantage across countries with different colonial languages: Spanish-speaking countries (n = 11: Argentina, Bolivia, Chile, Colombia, Ecuador, Guatemala, Mexico, Nicaragua, Peru, Uruguay, Venezuela), Portuguese-speaking Brazil (n = 1), and French-speaking Haiti (n = 1). All three groups share geographic region (Americas) and similar levels of economic development (middle-income), but differ in colonial language. We test whether English advantage varies systematically across these groups, potentially reflecting differential representation in English-language training data based on colonial linguistic legacies.

*Experiment 4c: African colonial history (data limitation).* We attempted to compare English advantage between African countries with substantial British colonial history (Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia) and African countries with minimal or no British colonial history (Ethiopia, Morocco, Algeria). However, we discovered that all British-colonized African countries in our dataset only have English language data, lacking native language comparisons (Swahili, Yoruba, Akan, Zulu, Shona, Bemba) needed to calculate English advantage. This data limitation prevented the planned analysis and is discussed as a methodological constraint reflecting systematic gaps in multilingual AI evaluation.

**Analysis.** For Experiments 4a and 4b, we compare English advantage (or colonial language advantage) between groups using appropriate statistical tests. For Experiment 4a, we compare Hong Kong's English advantage with Macao's Portuguese advantage using an independent-samples t-test with Welch's correction for unequal variances (n = 20 models per region after excluding two low-quality models). For Experiment 4b, we compare mean English advantage across Spanish-speaking, Portuguese-speaking, and French-speaking Latin American countries using one-way ANOVA. We report F-statistics, p-values, and effect sizes (η²). For Experiment 4c, we document the data limitation and discuss implications for future multilingual AI evaluation.

**Outcome.** For each experiment, we report: (i) mean English advantage (or colonial language advantage) for each group with 95% confidence intervals and sample sizes, (ii) test statistics (t or F) and p-values, (iii) effect sizes (Cohen's d for t-tests, η² for ANOVA), and (iv) standard deviations to characterize variance across models. We interpret results in light of statistical power limitations and high variance across models.

---

**Note on scope.** This study focuses on direct group comparisons. More comprehensive analyses controlling for contemporary socioeconomic factors (GDP, internet penetration, English proficiency) and testing mediation mechanisms (contemporary English usage patterns) require additional data not available in the current study and are left for future research.
