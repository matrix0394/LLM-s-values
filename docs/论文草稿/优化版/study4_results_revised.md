# Study 4 - Results Section (Revised)

## Study 4. Colonial History and Contemporary Language Effects

We conducted exploratory analyses to test whether historical colonial relationships predict contemporary language effects in LLM cultural representation. Despite theoretically motivated hypotheses, we found limited evidence for systematic colonial history effects, highlighting the challenges of detecting historical influences in contemporary AI systems.

### Experiment 4a: Hong Kong vs Macao Comparison

We compared English advantage in Hong Kong (British colony 1842–1997) with Portuguese advantage in Macao (Portuguese colony 1557–1999). Hong Kong showed a positive English advantage (M = 15.84%, 95% CI [−62.08, 93.76]), indicating better alignment under English than Chinese prompting on average. In contrast, Macao showed a negative Portuguese advantage (M = −15.67%, 95% CI [−90.35, 59.01]), indicating better alignment under Chinese than Portuguese prompting (Fig. S7B).

However, the difference between Hong Kong and Macao was not statistically significant (t(37.9) = 0.509, p = 0.614, Cohen's d = 0.161). The large confidence intervals and negligible effect size reflect substantial variance across models (Hong Kong SD = 179.23%; Macao SD = 170.37%), with individual models showing highly inconsistent patterns. This high variance prevented detection of systematic colonial language effects despite the theoretically motivated comparison.

### Experiment 4b: Latin American Language Variants

We compared English advantage across Latin American countries with different colonial languages: Spanish-speaking countries (n = 11, M = 5.43%, SD = 10.17%), Portuguese-speaking Brazil (M = 3.58%), and French-speaking Haiti (M = 20.38%). One-way ANOVA revealed no significant differences across groups (F(2, 10) = 1.035, p = 0.391, η² = 0.171) (Fig. S7C). Despite a large effect size (η² = 0.171), the small sample sizes for Portuguese (n = 1) and French (n = 1) countries limited statistical power to detect differences.

### Experiment 4c: African Colonial History (Data Limitation)

We attempted to compare English advantage between African countries with and without British colonial history. However, we discovered that all British-colonized African countries in our dataset (Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia) only have English language data, lacking native language comparisons (Swahili, Yoruba, Akan, Zulu, Shona, Bemba) needed to calculate English advantage (Fig. S7D).

This data limitation reflects a systematic gap in multilingual AI evaluation: countries where English is an official language due to colonial history are often evaluated only in English, preventing assessment of native language representation. This prevented the planned analysis and highlights the need for more comprehensive multilingual evaluation datasets that include native languages of formerly colonized regions.

### Summary

Our exploratory analyses found limited evidence for systematic colonial history effects on contemporary language representation in LLMs. The null findings may reflect: (1) genuine absence of colonial legacy effects in training data, (2) high variance across models masking systematic patterns, (3) insufficient statistical power due to small sample sizes, or (4) colonial effects being mediated by contemporary factors (e.g., current English usage, internet content distribution) that we could not control for. Future research with larger model samples, control variables for contemporary linguistic practices, and more comprehensive multilingual datasets may be better positioned to detect colonial history effects.
