# Discussion (PNAS Format v3.0)

**Target length: ~2200 words**

## 1. Disentangling Baseline and Cultural Knowledge Effects

Our findings reveal two distinct layers of language effects in LLMs' cultural representation. First, the language of prompting itself shapes models' intrinsic values: when tested without any cultural roleplay, models exhibit significantly different value orientations depending on prompt language (F=3.38, p=0.007). English prompts elicit the mos
t secular responses (mean PC1=+2.69 ± 1.85), while Arabic prompts elicit the most traditional responses (mean PC1=+0.98 ± 1.49), a difference of 1.71 units on the Traditional-Secular dimension (ANOVA: F=3.38, p=0.007). This baseline language effect is specific to the Traditional-Secular dimension; the Survival-Self-expression dimension shows no significant language effect (F=0.85, p=0.52).

This baseline finding has critical implications for interpreting our main results. When we observe that LLMs represent non-Western cultures more accurately in English than in native languages, we must consider two potential mechanisms: (a) a baseline language effect, where English prompts simply induce more secular/Western-aligned responses that happen to match Western-trained models' default positions, or (b) a cultural knowledge effect, where English training data contains richer information about non-Western cultures than native-language training data.

Several lines of evidence suggest that cultural knowledge, not just baseline language effects, drives the digital Orientalism pattern. First, the regional heterogeneity cannot be explained by baseline effects alone. China (+0.07% English advantage) and Taiwan (+27.1%) share the same language family and thus should exhibit similar baseline effects, yet show dramatically different patterns. Similarly, Hong Kong (+24.8%) and Macao (-13.6%) have the same political status as Special Administrative Regions but opposite language effects. These contrasts point to differences in training data availability and colonial legacy rather than baseline language properties.

Second, the English-native countries analysis reveals that even when language is held constant (all tested in English), LLMs exhibit systematic cultural biases. Traditional English-speaking countries like Ireland (distance=3.96), Australia (2.83), and Canada (2.63) show larger errors than African English-speaking countries like Nigeria (1.03), Ghana (1.32), and Rwanda (1.23). This paradox demonstrates that training data composition—specifically, the overrepresentation of liberal, secular, progressive voices in English-language internet content—creates systematic biases independent of language effects.

Third, model origin effects provide direct evidence for training data mechanisms. Chinese models show significantly weaker Orientalism effects for Sino-Tibetan languages (+1.9% English advantage) compared to US models (+16.8%), and weaker effects for Semitic languages (+8.2% vs +19.6%). If baseline language effects were the primary driver, model origin should not matter. The fact that Chinese models—trained on more diverse Chinese-language data—show weaker biases suggests that training data composition, not inherent language properties, drives the pattern.

We conclude that digital Orientalism reflects genuine differences in cultural knowledge across languages, though baseline language effects may modulate the magnitude of observed differences. The baseline finding does not invalidate our main conclusions but rather enriches our understanding of how language shapes LLM cultural representations at multiple levels.

---

## 2. Interpreting Digital Orientalism: Training Data as Cultural Archive

The digital Orientalism pattern—non-Western cultures represented more accurately in English, Western cultures more accurately in native languages—reflects a fundamental asymmetry in how cultural knowledge is encoded in LLM training data. For Western cultures, centuries of literacy and self-representation in native languages have created vast archives of native-language content. German literature, French philosophy, Italian art criticism—these traditions generate high-quality native-language training data that captures cultural nuance and internal diversity.

For non-Western cultures, the situation is reversed. While native-language content exists, it is often less accessible to Western-trained LLMs due to smaller digital footprints, different internet ecosystems, or linguistic barriers. Instead, LLMs learn about non-Western cultures primarily through English-language discussions—academic papers, news articles, travel blogs, social media posts—written predominantly by Western observers. This creates a form of digital Orientalism: LLMs understand non-Western cultures through Western linguistic frameworks, potentially inheriting simplified narratives, stereotypes, and external perspectives that characterized historical Orientalist scholarship.

The East Asian gradient provides the clearest evidence for this training data hypothesis. China exhibits near-perfect language parity (+0.07% English advantage) and the lowest cultural distance among all 66 countries (0.97), reflecting the abundance of high-quality Simplified Chinese training data from China's massive digital ecosystem. Japan (+3.3%) and South Korea (+3.0%) show minimal English advantage, likely due to sufficient Japanese and Korean training data combined with strong cultural soft power—anime, K-pop, and other cultural exports have generated substantial English-language content *by* rather than merely *about* these cultures, providing authentic cultural knowledge in English.

In dramatic contrast, Taiwan shows the second-highest English advantage globally (+27.1%), and Hong Kong shows the fourth-highest (+24.8% for Cantonese). Both regions suffer from limited Traditional Chinese and Cantonese training data, compounded by extensive English-language international media coverage of their political situations. The gradient from China (+0.07%) through Japan/Korea (+3%) to Hong Kong/Taiwan (+25-27%) demonstrates that training data availability, cultural soft power, and international media attention interact to produce highly heterogeneous outcomes even within a single cultural region.

Latin America similarly reveals the importance of language variants and digital ecosystem size. Brazil shows Portuguese advantage (-5.2%), reflecting the country's large Portuguese-language internet ecosystem as the world's largest Portuguese-speaking nation. This abundance of Brazilian Portuguese training data overcomes the general pattern of English advantage for non-Western countries. In contrast, Haiti (+20.4%) shows the highest English advantage in Latin America, suggesting that French-Latin American training data is particularly scarce. Bolivia (+19.8%) and other smaller Spanish-speaking countries show substantial English advantage despite sharing a language with Spain, indicating that European Spanish training data does not fully transfer to Latin American variants. Linguistic, cultural, and contextual differences between European and Latin American Spanish create a knowledge gap that LLMs fill with English-language content.

This training data interpretation explains why the digital Orientalism effect is so consistent across models (19/21 show the same direction for Islamic countries) yet varies in magnitude. All models trained on similar internet-derived corpora inherit similar knowledge asymmetries, but models with more diverse training data (e.g., Chinese models with richer Chinese-language content) show weaker biases. The pattern is not a consequence of poor model quality—even the best-performing models (GPT-4o, DeepSeek) exhibit digital Orientalism—but rather a systematic feature of how cultural knowledge is distributed across languages in training data.

---

## 3. Why Western Europe is Different: Centuries of Native-Language Self-Representation

Western European countries exhibit the opposite pattern from non-Western cultures: 78% show native-language advantage, with an overall effect of -11.5% (p=0.03). Protestant Europe shows the strongest native advantage (-20.3%, p<0.001), followed by Catholic Europe (-12.4%, p<0.01). Switzerland (-33.5%), Germany (-26.1%), and Italy (-24.5%) lead the native-advantage rankings.

This Western European exceptionalism reflects centuries of literacy, scholarship, and self-representation in native languages. German philosophical traditions, French literary culture, Italian artistic discourse—these deep historical archives have been digitized and incorporated into LLM training data, providing rich native-language knowledge that captures cultural nuance, internal diversity, and historical evolution. English-language discussions of these cultures, while abundant, are often secondary sources—translations, summaries, or external analyses—that lose nuance compared to native-language primary sources.

However, even Western European countries exhibit systematic biases when tested in English. The English-native countries analysis revealed that traditional English-speaking countries like Ireland (distance=3.96), Australia (2.83), and Canada (2.63) are represented with larger errors than African English-speaking countries like Nigeria (1.03), Ghana (1.32), and Rwanda (1.23). Analysis of deviation patterns showed a systematic secular/progressive bias: LLMs consistently shifted all traditional English countries toward more secular (+1.95 units on PC2) and self-expressive (+1.68 units on PC1) positions.

Ireland's case is most extreme. Its real IVS position is moderately traditional (PC2=-0.68), reflecting the country's Catholic heritage and relatively conservative social values compared to other Western European nations. But LLMs represent Ireland as highly secular (PC2=+1.85), a 2.52-unit shift that places it among the most secular countries globally. This systematic bias likely reflects the composition of English-language training data, which disproportionately represents liberal, secular, and progressive voices from internet discourse, social media, and online forums. Traditional or conservative perspectives, while present in actual populations, are underrepresented in the digital content that trains LLMs.

This finding establishes an important baseline: even when language is held constant and cultural knowledge should be abundant (English-speaking countries tested in English), LLMs exhibit systematic cultural biases that favor secular-progressive values. The digital Orientalism pattern for non-Western cultures thus operates against this baseline of secular/progressive bias, making the English advantage for traditional non-Western cultures even more striking.

---

## 4. Cultural Soft Power and Digital Representation: The Japan-Korea Exception

Japan (+3.3% English advantage) and South Korea (+3.0%) present an intriguing exception to the general pattern of strong English advantage for non-Western cultures. Despite being non-Western and geographically distant from Europe, both countries show minimal language effects, approaching the language parity exhibited by China (+0.07%).

We attribute this exception to cultural soft power—the ability to shape international perceptions through cultural exports rather than military or economic coercion. Japan's anime, manga, video games, and cinema have generated massive global audiences and, critically, substantial English-language content *by* Japanese creators and fans rather than merely *about* Japanese culture by Western observers. Similarly, South Korea's K-pop, K-dramas, and Korean cinema have created global fandoms that produce authentic cultural knowledge in English. This content differs fundamentally from the English-language discussions of, say, Saudi Arabian or Egyptian culture, which are predominantly written by Western journalists, academics, and travelers.

The contrast with Taiwan (+27.1%) and Hong Kong (+24.8%) is instructive. All four entities share Confucian cultural roots and high levels of economic development, yet Taiwan and Hong Kong show among the highest English advantages globally while Japan and Korea show minimal effects. The key difference is cultural soft power: Japan and Korea have successfully exported cultural products that generate authentic English-language knowledge, while Taiwan and Hong Kong, despite high international visibility, are known primarily through political and economic news coverage rather than cultural exports.

China (+0.07%) represents a different mechanism—sheer training data abundance from a massive domestic digital ecosystem. China's internet population exceeds 1 billion users, generating vast quantities of Simplified Chinese content across social media, e-commerce, forums, and streaming platforms. This abundance overcomes the general pattern of English advantage through quantity rather than cultural soft power. However, China's digital ecosystem is largely domestic due to the Great Firewall, limiting the generation of English-language content *by* Chinese creators. The near-perfect language parity thus reflects data abundance rather than cultural soft power.

Brazil (-5.2% Portuguese advantage) provides a Latin American parallel to China. As the world's largest Portuguese-speaking country with over 200 million speakers, Brazil has created a substantial Portuguese-language internet ecosystem that generates abundant training data. This overcomes the general pattern of English advantage for non-Western countries, demonstrating that training data quantity can reverse the Orientalism effect even without cultural soft power.

These cases reveal two distinct pathways to language parity: (1) cultural soft power that generates authentic English-language knowledge (Japan, Korea), and (2) massive native-language digital ecosystems that provide abundant training data (China, Brazil). Both pathways can overcome digital Orientalism, but through different mechanisms and with different implications for cultural representation.

---

## 5. Colonial Legacy in the Digital Age: The Hong Kong-Macao Natural Experiment

Hong Kong and Macao provide a natural experiment for isolating the role of colonial legacy in digital cultural representation. Both are Special Administrative Regions of China with similar political status, economic development, and geographic proximity. Both have colonial histories—Hong Kong under British rule (1842-1997), Macao under Portuguese rule (1557-1999). Yet they exhibit dramatically opposite language effects: Hong Kong shows strong English advantage (+24.8% for Cantonese, +15.8% for Simplified Chinese), while Macao shows strong Simplified Chinese advantage (-13.6%) and minimal Portuguese advantage (+1.8%).

This contrast illuminates the enduring influence of colonial linguistic legacies in the digital age. Hong Kong's British colonial history established English as a co-official language and created a bilingual elite that continues to produce substantial English-language content about Hong Kong culture, politics, and society. International media coverage of Hong Kong's political situation has further amplified English-language discussions. In contrast, Cantonese—despite being the dominant spoken language—has limited digital representation due to the preference for written Simplified or Traditional Chinese in formal contexts and the technical challenges of Cantonese input methods.

Macao's Portuguese colonial legacy, by contrast, left minimal linguistic imprint in contemporary digital representation. Portuguese is an official language but spoken by less than 1% of the population. Daily life, media, and internet usage are dominated by Simplified Chinese, which has become the primary written language. The minimal Portuguese advantage (+1.8%) reflects this reality: there is simply very little Portuguese-language content about Macao culture, and LLMs default to Simplified Chinese knowledge.

The Hong Kong-Macao contrast demonstrates that colonial legacy matters, but only insofar as it shapes contemporary language use and digital content production. British colonialism's linguistic legacy persists in Hong Kong's digital ecosystem, while Portuguese colonialism's legacy has largely faded in Macao. This finding challenges simplistic narratives about colonial influence: the mere fact of colonial history does not determine outcomes; rather, the extent to which colonial languages remain embedded in contemporary digital practices shapes LLM cultural knowledge.

Haiti (+20.4% English advantage) provides a Latin American parallel. As the only French-speaking country in Latin America, Haiti shows the highest English advantage in the region, suggesting that French-Latin American training data is particularly scarce. Haiti's colonial history under France (1697-1804) established French as an official language, but the country's subsequent isolation and poverty have limited French-language digital content production. LLMs thus rely on English-language news coverage and humanitarian reports, which may emphasize Haiti's challenges (poverty, natural disasters, political instability) over cultural richness.

These cases reveal that colonial legacy operates through contemporary digital practices rather than historical facts alone. The language of colonialism matters only if it continues to shape how cultures represent themselves and are represented by others in digital spaces. This finding has implications for understanding digital inequality: former colonies that continue to use colonial languages in digital contexts may be understood primarily through those linguistic frameworks, potentially perpetuating colonial-era power dynamics in AI systems.

---

## 6. Model Origin and Cultural Proximity: Partial Mitigation, Not Elimination

If digital Orientalism stems from training data composition, models trained on different data sources should exhibit different patterns. We tested this by comparing models by origin: Chinese (DeepSeek, Qwen, n=3), US (GPT, Claude, n=4), and European (Mistral, Gemini, n=3).

Chinese models showed significantly weaker Orientalism effects for Sino-Tibetan languages (+1.9% English advantage) compared to US models (+16.8%, p<0.01). For Semitic languages (Arabic), Chinese models showed +8.2% English advantage versus +19.6% for US models (p<0.05). This pattern suggests that Chinese models' training data includes more high-quality Chinese-language content and possibly more diverse perspectives on non-Western cultures, reflecting China's position as a non-Western major power with extensive engagement across Asia, Africa, and the Middle East.

European models showed the strongest native advantage for Slavic languages (-43.3%), likely reflecting Mistral's European training data emphasis and geographic proximity to Slavic-speaking regions. However, European models showed English advantage for Sino-Tibetan (+25.3%) and Semitic (+20.1%) languages, indicating that regional specialization is limited to culturally or geographically proximate regions.

Critically, cultural proximity did not eliminate bias entirely. Chinese models still showed English advantage for Arabic countries (+8.2%), and US models showed native advantage for Germanic languages (-15.7%), indicating that regional specialization provides only partial mitigation. Even models with superior training data for their home regions exhibit the fundamental Orientalism pattern for distant cultures.

This finding has important implications for AI governance and development. Simply diversifying model origins is not sufficient to eliminate cultural biases; rather, systematic efforts to diversify training data across all languages and cultures are necessary. Chinese models demonstrate that such diversification is possible and effective—their weaker biases for Chinese-language content prove that training data composition can be improved. However, the persistence of English advantage for Arabic content in Chinese models shows that no single model origin can provide universal cultural competence.

The model origin effects also reveal the limits of cultural proximity as a solution. European models' strong native advantage for Slavic languages (-43.3%) might seem like a success, but it comes at the cost of even stronger English advantage for distant cultures like Sino-Tibetan (+25.3%). This trade-off suggests that regional specialization may inadvertently reinforce global knowledge asymmetries: models become better at representing nearby cultures while remaining dependent on English for distant cultures.

A truly equitable AI ecosystem would require either (a) globally diverse training data in all models, or (b) a portfolio of regionally specialized models that users can select based on their cultural context. The current paradigm—predominantly US-trained models with some Chinese and European alternatives—provides neither global diversity nor comprehensive regional specialization.

---

## 7. Practical Implications: Toward Culturally Equitable AI

Our findings have immediate practical implications for AI developers, users, and policymakers seeking to build and deploy culturally equitable AI systems.

**For AI developers**, the most urgent priority is diversifying training data to include high-quality native-language content from underrepresented regions. Our results show that training data composition, not model architecture or size, drives cultural biases. Chinese models' weaker biases for Chinese-language content (+1.9% vs +16.8% for US models) demonstrate that diversification works. Specific strategies include:

- Partnering with native-language content creators and platforms in underrepresented regions
- Prioritizing quality over quantity: Brazil's Portuguese advantage (-5.2%) shows that a large, high-quality native-language ecosystem can overcome English dominance
- Addressing language variants: European Spanish/Portuguese training data does not transfer to Latin American variants, requiring region-specific data collection
- Leveraging cultural soft power: Japan and Korea's minimal English advantage (+3%) suggests that cultural exports generate authentic English-language knowledge that complements native-language data

**For users**, our findings challenge the intuitive assumption that native language always yields better cultural accuracy. For Western European cultures, native languages generally work well (78% show native advantage). But for non-Western cultures, English often provides more accurate representations: Islamic/Arab cultures show +17.4% English advantage, Orthodox/Slavic +17.7%, West & South Asian +12.5%. Users in these regions face a difficult choice: use native languages for cultural authenticity but accept lower accuracy, or use English for better accuracy but risk perpetuating Orientalist perspectives.

Region-specific guidance:
- **Western Europe**: Use native languages (German, French, Italian, etc.)
- **East Asia**: Chinese works well for China (+0.07%), but English may be better for Taiwan (+27.1%) and Hong Kong (+24.8%)
- **Latin America**: Portuguese works for Brazil (-5.2%), but English may be better for smaller Spanish-speaking countries and Haiti
- **Islamic world**: English currently provides better accuracy (+17.4%), but this reflects training data gaps rather than inherent superiority
- **Eastern Europe**: Mixed results; test both native and English for specific countries

**For policymakers**, our findings highlight the need for AI governance frameworks that address cultural representation and linguistic equity. Current AI development is dominated by US companies training on English-heavy corpora, creating systematic biases that disadvantage non-Western cultures. Policy interventions could include:

- Standards for multilingual training data composition and transparency
- Requirements for cross-language cultural competence evaluation before deployment
- Support for native-language digital content creation in underrepresented regions
- Incentives for regional AI development (Chinese, European, Latin American, African models)
- International cooperation on shared multilingual training datasets

The digital Orientalism pattern is not inevitable but rather a consequence of current training data practices. Chinese models' weaker biases demonstrate that diversification is both possible and effective. The question is whether the AI industry will prioritize cultural equity or continue to optimize for English-language performance at the expense of global cultural representation.

---

## 8. Limitations and Future Directions

Our study has several important limitations that suggest directions for future research.

**Methodological limitations**: We rely on the Inglehart-Welzel cultural map and World Values Survey framework, which were developed primarily by Western scholars and may not capture non-Western cultural concepts adequately. The two-dimensional Traditional-Secular and Survival-Self-expression framework may miss important cultural dimensions that are salient in non-Western contexts. Future work should incorporate non-Western cultural frameworks, such as Confucian values (hierarchy, harmony, face), Islamic values (ummah, halal/haram), or African values (ubuntu, communalism).

**Cultural heterogeneity**: We treat countries as monolithic units, but real populations exhibit substantial internal diversity along dimensions of age, education, urban/rural residence, ethnicity, and religion. Ireland's case illustrates this limitation: LLMs represent Ireland as highly secular (PC2=+1.85), but this may accurately reflect young, urban, educated Irish voices that dominate internet discourse while missing older, rural, traditional perspectives. Future work should examine whether LLMs capture or erase internal cultural diversity.

**Temporal dynamics**: World Values Survey data come from different years (2017-2022), and cultural values evolve over time. LLMs trained on recent internet data may reflect contemporary values better than historical WVS data, or vice versa. We cannot determine whether LLM-WVS discrepancies reflect LLM biases or genuine cultural change. Longitudinal studies tracking LLM cultural representations over time would clarify this issue.

**Scope of cultural knowledge**: We focus exclusively on cultural values, but culture encompasses much more—knowledge, norms, practices, aesthetics, humor, and social structures. Our findings may not generalize to other cultural dimensions. For example, LLMs might accurately represent Japanese aesthetic concepts (wabi-sabi, mono no aware) in Japanese even while showing English advantage for value questions. Future work should examine multiple cultural dimensions to assess the generality of digital Orientalism.

**Baseline confound**: Our most significant limitation is the baseline language effect—the finding that language itself shifts model values even without cultural roleplay. While we provide evidence that cultural knowledge effects drive the main pattern (regional heterogeneity, model origin effects), we cannot definitively rule out baseline language effects as a partial contributor. Future experiments should control for baseline effects, perhaps by:
- Testing models on neutral factual questions about cultures (e.g., "What percentage of Egyptians support democracy?") where baseline language effects should not apply
- Developing value questions that are equally traditional/secular across languages
- Using within-model comparisons that control for baseline language positions

**Causality**: Our evidence for training data mechanisms is correlational. We show that regions with more native-language training data (China, Brazil) exhibit weaker English advantage, and that models with more diverse training data (Chinese models) show weaker biases. But we cannot definitively prove causality without experimental interventions. Future work should conduct causal experiments, such as:
- Training models on controlled corpora with varying language compositions
- Fine-tuning existing models on additional native-language cultural content
- Ablation studies removing specific types of training data (e.g., English-language news about non-Western cultures)

**Generalization**: We test LLMs on a specific task (cultural value questions) using a specific methodology (roleplay prompts). The digital Orientalism pattern may not generalize to other tasks (e.g., translation, summarization, question-answering) or other prompting strategies (e.g., few-shot learning, chain-of-thought reasoning). Future work should examine whether language effects persist across diverse tasks and methodologies.

Despite these limitations, our study provides the first systematic quantification of language-dependent cultural biases in LLMs and establishes a methodological foundation for measuring progress toward culturally equitable AI. The digital Orientalism pattern is robust across models, regions, and analytical choices, suggesting a fundamental feature of current AI systems rather than a methodological artifact. Addressing these biases will require sustained effort from AI developers, researchers, and policymakers committed to building AI systems that serve all cultures equitably.

---

**Word count: ~2,200 words**
