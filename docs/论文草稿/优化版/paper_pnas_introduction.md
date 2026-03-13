## Introduction

Large language models (LLMs) have rapidly evolved from research prototypes into global communication infrastructure, with billions of users interacting with conversational AI systems across dozens of languages. These models increasingly mediate cross-cultural communication, provide localized information, and shape public discourse worldwide. As a result, a central empirical question arises: does the language used to interact with an LLM systematically affect how cultural values are expressed and represented by the model? More specifically, when the same model is queried about the same society, does prompt language influence the accuracy of its expressed cultural values?

This question carries both theoretical and practical importance. From a theoretical perspective, it speaks to long-standing debates about the relationship between language and cultural knowledge—whether linguistic form merely conveys content or actively shapes value expression. From a practical perspective, it bears directly on the equitable deployment of AI technologies. If identical systems express different cultural value profiles depending on the language of interaction, users across linguistic communities may encounter systematically divergent representations of culture, even when engaging with the same model.

### Linguistic Imbalances and Cultural Representation in LLMs

Contemporary LLMs are trained on massive multilingual corpora characterized by pronounced linguistic imbalances. English-language data constitute a substantial share of available training material, while many languages—particularly those spoken outside Western Europe and North America—remain comparatively underrepresented. As a consequence, models may encode cultural knowledge unevenly across languages, relying disproportionately on English-language descriptions of societies—such as academic writing, journalism, and online discourse—rather than on native-language cultural production.

This imbalance raises a counterintuitive possibility: LLMs may represent non-Western societies more accurately when prompted in English than when prompted in their native languages. Such a pattern would not reflect simple translation failure, but deeper asymmetries in how cultural information is learned, structured, and retrieved within multilingual models. Evaluating this possibility, however, requires careful separation of language-dependent baseline effects from language-dependent accuracy in cultural role-play.

### Disentangling Baseline Language Effects from Cultural Role-Play

Before assessing cultural representation, it is essential to establish whether prompt language alone systematically alters how models express values, independent of any assigned cultural or national identity. If identical models produce different value profiles across languages in a neutral setting, then apparent language effects in cultural role-play could reflect baseline linguistic biases rather than differences in encoded cultural knowledge. Identifying such baseline language effects is therefore a necessary foundation for interpreting multilingual evaluations of cultural representation.

### Research Design and Questions

To address these issues, we conduct a two-stage evaluation of 23 state-of-the-art large language models developed in the United States, China, and Europe. In the first stage, we assess baseline language effects by administering items from the World Values Survey across six official United Nations languages, without assigning any cultural role-play. This stage establishes whether and how prompt language alone shifts expressed value orientations.

In the second stage, we evaluate cultural representation under explicit role-play conditions. Models are instructed to respond as typical adult citizens of 66 countries, using both English and native-language prompts. Cultural alignment is quantified by comparing model-generated responses with country-level ground-truth values derived from large-scale human survey data using the Inglehart–Welzel cultural map. By holding model identity, survey items, and prompts constant while varying only the language of interaction, this design isolates the role of language in shaping cultural value expression and representation accuracy.

Our analysis addresses four research questions:

1. **Do LLMs exhibit systematic baseline shifts in expressed values across languages, independent of cultural role-play?**

2. **Does prompt language affect the accuracy of cultural value representation under role-play conditions?**

3. **Are language effects uniform across societies, or do they vary systematically across cultural regions and linguistic contexts?**

4. **How are observed language effects associated with model origin, training data imbalances, and linguistic context?**

### Contributions

Together, these analyses make four primary contributions. **Methodologically**, we introduce a two-stage framework that separates baseline language effects from cultural role-play accuracy. **Empirically**, we document a robust asymmetry—termed *digital Orientalism*—in which non-Western cultures are represented more accurately under English prompting, while Western cultures tend to be better represented in native languages. **Theoretically**, our findings link multilingual model behavior to structural imbalances in training data and linguistic mediation. **Practically**, the results demonstrate that language translation alone is insufficient to ensure culturally appropriate value expression, underscoring the need for more balanced approaches to multilingual training, evaluation, and deployment of AI systems.
