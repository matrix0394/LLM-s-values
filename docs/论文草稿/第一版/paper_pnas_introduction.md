# Introduction (PNAS Format)

**Target length: ~900 words**

Large language models (LLMs) have rapidly evolved from research prototypes into global communication infrastructure, with billions of users interacting with conversational AI systems across dozens of languages. These models increasingly mediate cross-cultural communication, provide localized information, and shape public discourse worldwide. As a result, a central question emerges: **Do LLMs represent cultural values equally well across languages, or do linguistic asymmetries in training data lead to systematic distortions in cultural representation?**

This question carries both theoretical and practical importance. From a theoretical perspective, it probes the relationship between language and cultural knowledge in artificial systems, echoing long-standing debates in linguistics and anthropology about how language mediates cultural understanding and value transmission. From a practical perspective, it bears directly on the equitable deployment of AI technologies. If cultural representations encoded in LLMs vary systematically with the language of interaction, then users engaging with the same system in different languages may receive culturally inconsistent or biased responses, potentially reinforcing existing global inequalities in knowledge production and representation.

## Linguistic Asymmetries in Cultural Representation

Scholars have long observed that knowledge about non-Western societies has often been produced, mediated, and circulated through Western languages and institutions. Analyses in the social sciences and humanities have documented how representations of culture are shaped not only by content but also by the linguistic and institutional channels through which that content is expressed. These insights raise the possibility that similar asymmetries may emerge in contemporary artificial intelligence systems trained predominantly on text from a small number of high-resource languages.

State-of-the-art LLMs are trained on massive corpora in which English-language data constitute a substantial majority. As a consequence, these models may encode non-Western cultures primarily through English-language descriptions—such as academic publications, journalism, and online discourse *about* these societies—rather than through native-language cultural production. If this is the case, models may paradoxically represent non-Western cultures more accurately when prompted in English than when prompted in their native languages, despite the intuitive expectation that native-language interaction should provide richer cultural context.

Before testing this possibility, however, it is necessary to establish whether language alone affects how models express values, independent of any cultural role-play. If prompt language systematically shifts model responses—for example, by inducing more secular or more traditional value profiles—then apparent language effects in cultural role-play could reflect baseline linguistic biases rather than differences in encoded cultural knowledge. Disentangling baseline language effects from cultural representation is therefore a prerequisite for meaningful evaluation.

## Research Design and Questions

To address these issues, we conduct a two-stage systematic evaluation of 23 state-of-the-art large language models developed in the United States, China, and Europe. In the first stage, we assess baseline language effects by administering items from the World Values Survey across six official United Nations languages, without assigning any cultural or national identity to the models. This stage establishes whether and how prompt language alone alters expressed value orientations.

In the second stage, we evaluate cultural representation under explicit role-play conditions. Models are instructed to respond as typical citizens of 66 countries, using both English and native-language prompts. Cultural alignment is quantified by comparing model-generated responses with country-level ground-truth values derived from large-scale human survey data using the Inglehart–Welzel cultural map framework. By holding model identity, prompts, and survey items constant while varying only the language of interaction, this design isolates the effect of language on cultural representation accuracy.

Our analysis is guided by four core research questions:

1. **Do LLMs exhibit systematic baseline value shifts across languages?** We test whether identical models express different value profiles when prompted in different languages, even in the absence of cultural role-play.

2. **Does prompt language affect cultural representation accuracy in LLMs?** We examine whether models role-playing the same country align more closely with ground-truth cultural values when prompted in English or in native languages.

3. **Is any observed language effect uniform across cultures, or does it vary systematically across regions and linguistic contexts?** We analyze heterogeneity across cultural regions and national settings to identify structured patterns rather than isolated cases.

4. **What factors help explain observed asymmetries?** We investigate associations between language effects and variables such as training data availability, linguistic distance from English, colonial and institutional history, language variants, and model origin.

## Contributions

This study makes four primary contributions. **Methodologically**, we introduce a two-stage evaluation framework that separates baseline language effects from cultural role-play accuracy, enabling clearer interpretation of multilingual model behavior. **Empirically**, we identify a robust asymmetry in multilingual cultural representation—termed *digital Orientalism*—whereby non-Western cultures are represented more accurately in English, while Western cultures are better represented in native languages. **Theoretically**, we show that this asymmetry is shaped by multiple interacting mechanisms, including training data composition, linguistic history, and model origin, rather than a simple West–non-West divide. **Practically**, our findings demonstrate that language translation alone is insufficient to ensure culturally appropriate AI behavior, underscoring the need for more balanced multilingual training data and evaluation practices as AI systems are deployed globally.

---

## References (Introduction)

1. OpenAI (2024) ChatGPT user statistics.
2. Whorf BL (1956) *Language, Thought, and Reality* (MIT Press).
3. Geertz C (1973) *The Interpretation of Cultures* (Basic Books).
4. Said EW (1978) *Orientalism* (Pantheon Books).
5. Bender EM, et al. (2021) On the dangers of stochastic parrots. *FAccT* 610-623.
6. Boroditsky L (2001) Does language shape thought? *Cognition* 1-17.
7. Nisbett RE, et al. (2001) Culture and systems of thought. *Psychol Rev* 291-310.
8. Bolukbasi T, et al. (2016) Man is to computer programmer as woman is to homemaker? *NeurIPS*.
9. Abid A, et al. (2021) Persistent anti-Muslim bias in large language models. *AIES*.
10. Navigli R, et al. (2023) Biases in large language models. *ACM Comput Surv*.
11. Goyal N, et al. (2022) The Flores-101 evaluation benchmark. *TACL*.
12. Ahuja K, et al. (2023) MEGA: Multilingual evaluation of generative AI. *arXiv*.
13. Inglehart R, Welzel C (2005) *Modernization, Cultural Change, and Democracy* (Cambridge Univ Press).
14. Inglehart R, Baker WE (2000) Modernization, cultural change, and the persistence of traditional values. *Am Sociol Rev* 19-51.
