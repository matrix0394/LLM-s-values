# Discussion (PNAS Format)

**Target length: ~2,200 words**

## Overview: Language Shapes Cultural Representation at Two Levels

This study identifies a robust asymmetry in multilingual cultural representation by large language models (LLMs): for many non-Western societies, cultural role-play aligns more closely with human survey ground truth when models are prompted in English than when prompted in the society's native language(s), whereas Western European societies show the opposite pattern. Interpreting this asymmetry requires separating two distinct language-dependent processes.

First, prompt language can shift expressed values even in the absence of any cultural role-play. When models answer the same value items in different languages without an assigned identity, their responses move systematically along the traditional–secular dimension, while remaining comparatively stable on the survival–self-expression dimension. This establishes that language is not a neutral interface to a fixed internal value profile.

Second, beyond baseline shifts in expressed values, language affects the fidelity of cultural role-play itself. The regional reversal in accuracy between Western and non-Western societies cannot be accounted for by a uniform baseline language effect alone; rather, it indicates that cultural knowledge encoded by LLMs is unevenly distributed across languages. Below, we interpret the observed pattern as a structural asymmetry in the linguistic sources from which models learn cultural information, and we use cross-region heterogeneity and model-origin comparisons to constrain plausible mechanisms.

---

## Digital Orientalism as a Training-Data Asymmetry

We refer to the observed regional reversal in language effects as *digital Orientalism*: non-Western cultures are represented more accurately under English prompting, while Western European cultures are represented more accurately under native-language prompting. The term is meant to capture an asymmetry in representation rather than to assert intent. Classic analyses of cultural knowledge production have noted that depictions of non-Western societies have often been mediated through Western languages and institutions, with external descriptions sometimes standing in for local perspectives. Our results suggest that a related asymmetry can manifest in contemporary LLMs at scale.

A parsimonious interpretation is that *training data function as a cultural archive with uneven linguistic coverage*. Contemporary LLMs are trained on large internet-derived corpora that contain substantially more English content than most other languages, and English sources frequently include descriptions *about* non-Western societies (e.g., international journalism, academic writing, travel writing, and online discourse). When native-language digital footprints are smaller, more fragmented, or less represented in model training, English descriptions can become the dominant channel through which a model learns to associate a country with particular social norms and value profiles. Under this view, English prompting can surface an English-mediated representation of the target culture that is closer to the human-survey reference than what the model retrieves when operating in the native language.

Several results constrain alternative explanations. If English advantage were driven primarily by a single baseline shift toward a universal "English profile," then we would expect language effects to be relatively uniform across countries. Instead, we observe sharp within-region contrasts among settings that are otherwise similar, suggesting that accuracy depends on the availability and character of culturally specific information in the relevant language(s), not only on language-conditioned value expression.

---

## Explaining Heterogeneity: When English Advantage Weakens or Reverses

Although the regional reversal is systematic, it is not monolithic. The magnitude—and in some cases the direction—of language effects varies substantially across countries. This variation is informative because it helps identify conditions under which digital Orientalism weakens or reverses.

### Data abundance in native languages

One pathway to language parity is the presence of a large and high-activity native-language digital ecosystem. Countries with extensive native-language content can provide models with sufficient coverage to produce culturally aligned responses without relying on English mediation. Cases exhibiting near parity, or native-language advantage, are consistent with this mechanism: where native-language data are abundant and diverse, native prompting can retrieve richer and more internally representative cultural signals.

China (+0.07%) exemplifies this pathway. With over 1 billion internet users generating vast quantities of Simplified Chinese content across social media, e-commerce, forums, and streaming platforms, China's digital ecosystem provides abundant training data that overcomes the general pattern of English advantage through sheer quantity. Similarly, Brazil (−5.2%) as the world's largest Portuguese-speaking country has created a substantial Portuguese-language internet ecosystem that generates sufficient training data to reverse the Orientalism effect.

### Cultural production that travels across languages

A second pathway is extensive cross-linguistic cultural production, where a society's cultural exports generate substantial non-external, community-generated content in English. In such contexts, English does not merely contain outside descriptions; it can also contain dense cultural knowledge produced by creators, diaspora communities, and transnational audiences. Under this mechanism, English prompting can yield culturally aligned outputs without necessarily implying an externalizing lens.

Japan (+3.3%) and South Korea (+3.0%) illustrate this pathway. Both countries have successfully exported cultural products—anime, manga, K-pop, K-dramas—that generate massive global audiences and, critically, substantial English-language content *by* Japanese and Korean creators and fans rather than merely *about* these cultures by Western observers. This cultural soft power creates authentic English-language knowledge that complements native-language data, resulting in minimal English advantage despite being non-Western societies.

Importantly, this pathway predicts that English advantage should be smaller (approaching parity) when English-language content is driven by cultural production and fan communities rather than primarily by news or academic discourse. The contrast with Taiwan (+27.1%) and Hong Kong (+24.8%)—which share Confucian cultural roots but are known primarily through political and economic news coverage—supports this interpretation.

### Linguistic history and institutional bilingualism

A third pathway concerns the persistence of institutional bilingualism and historical language regimes. Where English remains embedded in education, governance, or international-facing media, English-language discourse about a society can be especially prominent and locally anchored. Conversely, where a colonial language has limited contemporary use and minimal digital presence, it may not provide an informational advantage.

The Hong Kong–Macao contrast provides a natural experiment. Both are Special Administrative Regions of China with similar political status and economic development, yet Hong Kong shows strong English advantage (+24.8%) while Macao shows strong Simplified Chinese advantage (−13.6%). Hong Kong's British colonial history established English as a co-official language and created a bilingual elite that continues to produce substantial English-language content. In contrast, Macao's Portuguese colonial legacy left minimal linguistic imprint in contemporary digital representation, with Portuguese spoken by less than 1% of the population.

Contrasts among otherwise similar settings are consistent with the idea that what matters is not colonial history per se, but the degree to which it shapes present-day language practices and content production. Haiti (+20.4%), as the only French-speaking country in Latin America, shows the highest English advantage in the region, suggesting that French-Latin American training data is particularly scarce despite Haiti's French colonial history.

Together, these pathways suggest that digital Orientalism should be understood as an emergent property of (i) native-language data coverage, (ii) whether English content is primarily external description or includes substantial cultural production, and (iii) the contemporary linguistic institutions that govern digital communication. These mechanisms can operate jointly, explaining why societies with shared cultural traditions can nonetheless occupy very different positions in the multilingual performance landscape.

---

## Why Western Europe Differs

Western European societies show the opposite pattern—higher cultural alignment under native-language prompting—consistent with a different data regime. Many Western European languages have long-standing traditions of high-volume written production across literature, journalism, scholarship, and public debate, much of which has been digitized. For these societies, native-language corpora can provide dense, internally diverse representations that preserve nuance better than English summaries, translations, or external commentary. In this setting, English prompting can still access abundant content, but it may retrieve a more mediated or homogenized representation compared to native-language prompting.

Protestant Europe shows the strongest native advantage (−20.3%), followed by Catholic Europe (−12.4%). Switzerland (−33.5%), Germany (−26.1%), and Italy (−24.5%) lead the native-advantage rankings. These results reflect centuries of literacy, scholarship, and self-representation in native languages—German philosophical traditions, French literary culture, Italian artistic discourse—that have been digitized and incorporated into LLM training data.

At the same time, holding language constant does not eliminate bias. Even within English-speaking settings, models can systematically deviate from survey ground truth in consistent directions, indicating that the problem is not solely multilingual coverage but also whose voices are most represented in the underlying digital data. Traditional English-speaking countries like Ireland (distance = 3.96), Australia (2.83), and Canada (2.63) show larger errors than African English-speaking countries like Nigeria (1.03), Ghana (1.32), and Rwanda (1.23), with systematic shifts toward more secular and self-expressive positions.

This observation aligns with a broader point: cultural representation in LLMs reflects both *coverage* (how much data exist in a language) and *composition* (which subpopulations and viewpoints dominate that data). The overrepresentation of liberal, secular, and progressive voices in English-language internet content creates systematic biases even when language is held constant.

---

## Model Origin and the Limits of Cultural Proximity

Comparisons across model origins provide further evidence that training data composition contributes to the observed asymmetry. Models developed in different regions plausibly draw on different data pipelines and have different relative strengths on linguistically proximate content. Consistent with this, we observe that model origin is associated with systematic differences in the magnitude of language effects for certain language families.

Chinese models showed significantly weaker Orientalism effects for Sino-Tibetan languages (+1.9%) compared to US models (+16.8%, p < 0.01), and weaker effects for Semitic languages (+8.2% vs. +19.6%, p < 0.05). European models showed the strongest native advantage for Slavic languages (−43.3%), likely reflecting Mistral's European training data emphasis and geographic proximity to Slavic-speaking regions.

However, cultural proximity is not a complete solution. Models with strong performance in their home linguistic ecosystems can still show English advantages for distant cultures, and models that encode strong native-language advantages for nearby regions can show English advantages elsewhere. Chinese models still showed English advantage for Arabic countries (+8.2%), and US models showed native advantage for Germanic languages (−15.7%). These patterns suggest that regional specialization can mitigate but does not eliminate the structural asymmetry in multilingual cultural coverage.

More broadly, they imply that improving cultural competence requires not only building more models in more places, but also addressing the multilingual and cross-cultural distribution of training data within and across model development ecosystems. A truly equitable AI ecosystem would require either (a) globally diverse training data in all models, or (b) a portfolio of regionally specialized models that users can select based on their cultural context. The current paradigm—predominantly US-trained models with some Chinese and European alternatives—provides neither global diversity nor comprehensive regional specialization.

---

## Practical Implications

Three practical implications follow from these findings.

First, **translation is not equivalent to cultural competence**. Deploying an interface in a local language does not guarantee that the model's cultural representations in that language are grounded in equally rich cultural evidence. For many non-Western societies, English prompts currently yield more accurate cultural representations than native-language prompts—a counterintuitive finding with immediate implications for global AI deployment.

Second, **data diversity is central**. The patterns observed here are consistent with the view that cultural alignment depends strongly on the availability and representativeness of culturally grounded content in the relevant languages and variants. Improving multilingual cultural performance therefore requires deliberate investment in high-quality native-language corpora, including region-specific language variants and locally produced cultural content. Strategies include partnering with native-language content creators, prioritizing quality over quantity, addressing language variants (European vs. Latin American Spanish/Portuguese), and leveraging cultural soft power.

Third, **evaluation should be multilingual and culture-aware**. Benchmarking model performance only in English can mask systematic failures in native-language cultural representation. Evaluation protocols should vary prompt language while holding tasks constant and should include measures of cultural alignment tied to human ground truth where feasible. Current AI development practices, dominated by English-language evaluation, may inadvertently optimize for English performance at the expense of native-language cultural competence.

---

## Limitations and Future Directions

This study has several limitations that motivate future work.

**Baseline language confounds.** A central limitation is that prompt language systematically shifts expressed values even without role-play, which can modulate observed accuracy differences. Although multiple results are more consistent with a cultural-knowledge mechanism than with baseline shifts alone, future work should develop designs that more directly control for baseline language positions (e.g., using matched baselines within each language, or tasks that are less value-laden while still culturally informative).

**Cultural framework and construct coverage.** We operationalize culture using the Inglehart–Welzel map and a fixed set of value items. While this framework is widely used and enables cross-national comparability, it may not capture culturally salient constructs outside its scope. The two-dimensional Traditional-Secular and Survival-Self-expression framework may miss important cultural dimensions salient in non-Western contexts, such as Confucian values (hierarchy, harmony, face), Islamic values (ummah, halal/haram), or African values (ubuntu, communalism). Extending evaluation to additional cultural dimensions—including frameworks developed in non-Western contexts—would provide a more complete account of cultural representation.

**Within-country heterogeneity.** Country-level ground truth necessarily aggregates across age, education, urban–rural residence, ethnicity, and other cleavages. LLM outputs may overrepresent digitally active subpopulations, potentially producing apparent deviations from national averages. Ireland's case illustrates this: LLMs represent Ireland as highly secular, which may accurately reflect young, urban, educated Irish voices that dominate internet discourse while missing older, rural, traditional perspectives. Future work should evaluate whether models capture within-country diversity (e.g., by conditioning role-play on demographic strata) and whether language effects differ across subpopulations.

**Temporal mismatch.** Survey ground truth is collected over multi-year windows (2017–2022), while LLM training data may reflect different time periods. Discrepancies may reflect either model bias or genuine cultural change. We cannot determine whether LLM-WVS discrepancies reflect LLM biases or genuine cultural evolution. Longitudinal designs—tracking both model behavior and survey measures over time—would help separate these factors.

**Causality.** Our evidence for training-data mechanisms is correlational. We show that regions with more native-language training data (China, Brazil) exhibit weaker English advantage, and that models with more diverse training data (Chinese models) show weaker biases. But we cannot definitively prove causality without experimental interventions. Stronger causal tests would include controlled training or fine-tuning interventions that increase native-language cultural content, as well as ablation studies that modify the composition of English-language content about target cultures.

**Task generality.** We focus on value-expression items under a standardized role-play prompt. Language effects may differ across tasks such as factual cultural QA, translation, summarization, or conversational assistance. The digital Orientalism pattern may not generalize to other tasks or prompting strategies (e.g., few-shot learning, chain-of-thought reasoning). Future studies should test whether the same asymmetry arises across tasks and methodologies.

Despite these limitations, our results provide a quantitative characterization of language-dependent cultural representation in LLMs and identify a reproducible asymmetry that future data and model interventions can target. The digital Orientalism pattern is robust across models, regions, and analytical choices, suggesting a fundamental feature of current AI systems rather than a methodological artifact. Addressing digital Orientalism will likely require both improved multilingual data coverage and evaluation practices that treat cultural competence as a first-class objective in model development.

---

**Concluding Remarks**

This study provides the first systematic quantification of language-dependent cultural biases in large language models, revealing two distinct layers of language effects: baseline shifts in expressed values and asymmetries in encoded cultural knowledge. The digital Orientalism pattern—non-Western cultures represented more accurately in English, Western cultures more accurately in native languages—reflects structural asymmetries in training data composition rather than inherent properties of languages or cultures.

Multiple mechanisms shape this pattern: training data availability (China vs. Taiwan), colonial legacy (Hong Kong vs. Macao), cultural soft power (Japan and Korea), language variants (European vs. Latin American Spanish/Portuguese), and model origin (regional specialization). No single mechanism accounts for all variation; rather, these factors interact to produce highly heterogeneous outcomes even within cultural regions.

The findings have immediate practical implications. Language translation alone cannot ensure culturally appropriate AI behavior. For many non-Western societies, English prompts currently yield more accurate cultural representations than native-language prompts—a counterintuitive result that challenges assumptions underlying global AI deployment. Addressing this asymmetry requires systematic efforts to diversify multilingual training data, develop culture-aware evaluation practices, and rethink how AI systems are trained and deployed globally.

Chinese models demonstrate that diversification is both possible and effective: their weaker biases for Chinese-language content prove that training data composition can be improved. However, cultural proximity provides only partial mitigation. A truly equitable AI ecosystem requires either globally diverse training data in all models or a portfolio of regionally specialized models that users can select based on cultural context.

As AI systems mediate cross-cultural communication for billions of users, ensuring they represent all cultures equitably is not merely a technical challenge but a moral imperative. Our methodology provides a foundation for measuring progress toward this goal, enabling researchers and developers to quantify cultural representation and track improvements across model generations. The digital Orientalism pattern reveals how AI systems inherit historical knowledge asymmetries—but also shows pathways toward more equitable cultural representation.
