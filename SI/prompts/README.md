# Prompts - Supporting Information

This directory contains all prompts used in the study "Cultural Values in Large Language Models."

## Directory Structure

```
SI/prompts/
├── README.md                           # This file
├── questions/                          # Survey questions in 13 languages (1 original + 12 translations)
│   ├── README.md
│   ├── en.md                           # English (Original WVS)
│   ├── zh-cn.md                        # Simplified Chinese
│   ├── fr.md                           # French
│   ├── es.md                           # Spanish
│   ├── ar.md                           # Arabic
│   ├── de.md                           # German
│   ├── ru.md                           # Russian
│   ├── pt.md                           # Portuguese
│   ├── it.md                           # Italian
│   ├── ja.md                           # Japanese
│   ├── ko.md                           # Korean
│   ├── zh-tw.md                        # Traditional Chinese (Taiwan)
│   └── zh-hk.md                        # Traditional Chinese (Hong Kong)
├── baseline_intrinsic_values/          # Baseline experiments (no cultural context)
│   ├── README.md
│   ├── system_prompts_by_language/     # System prompts in 6 UN official languages
│   │   ├── en.md
│   │   ├── fr.md
│   │   ├── es.md
│   │   ├── ru.md
│   │   ├── ar.md
│   │   └── zh-cn.md
│   └── full_prompt.md                  # Complete prompt template
└── imitated_contextual_values/         # Cultural imitation experiments
    ├── README.md
    ├── system_prompts_by_language/     # System prompts in 13 languages
    │   ├── en.md
    │   ├── zh-cn.md
    │   ├── fr.md
    │   ├── es.md
    │   ├── ar.md
    │   ├── de.md
    │   ├── ru.md
    │   ├── pt.md
    │   ├── it.md
    │   ├── ja.md
    │   ├── ko.md
    │   ├── zh-tw.md
    │   └── zh-hk.md
    └── full_prompt_template.md         # Complete prompt template (references questions/)
```

## Data Sources

All content is extracted from source code and configuration files:

| Directory | Source File | Variable/Key |
|-----------|-------------|--------------|
| `questions/` | `config/multilingual_questions_complete.json` | `languages.{lang}.questions` |
| `baseline_intrinsic_values/` | `src/llm_values/llm_multilingual_interview.py` | `UN_LANGUAGE_SYSTEM_PROMPTS` |
| `imitated_contextual_values/` | `src/roleplay_English/llm_country_roleplay_interview.py` | `base_system_prompt` |

## Experimental Conditions

| Condition | Directory | Description |
|-----------|-----------|-------------|
| Baseline | `baseline_intrinsic_values/` | LLMs respond in 6 UN official languages without cultural context |
| Cultural Imitation | `imitated_contextual_values/` | LLMs roleplay as citizens of 66 countries in 13 languages |

## Survey Questions

10 questions from the World Values Survey (WVS):

| Code | Topic | Scale | Dimension |
|------|-------|-------|-----------|
| A008 | Feeling of happiness | 1-4 | Traditional vs. Secular-Rational |
| A165 | Most people can be trusted | 1-2 | Traditional vs. Secular-Rational |
| E018 | Future changes: Greater respect for authority | 1-3 | Traditional vs. Secular-Rational |
| E025 | Political action: signing a petition | 1-3 | Traditional vs. Secular-Rational |
| F063 | How important is God in your life | 1-10 | Survival vs. Self-Expression |
| F118 | Justifiable: homosexuality | 1-10 | Survival vs. Self-Expression |
| F120 | Justifiable: abortion | 1-10 | Survival vs. Self-Expression |
| G006 | How proud of nationality | 1-4 | Survival vs. Self-Expression |
| Y002 | Post-Materialist index 4-item | 2 from 4 | Traditional vs. Secular-Rational |
| Y003 | Autonomy Index | 5 from 11 | Traditional vs. Secular-Rational |

## Languages

13 languages (1 original English + 12 translations) covering 66 countries:

| Code | Language | Usage |
|------|----------|-------|
| en | English (Original) | 21 English-native countries + 45 non-native countries (lingua franca) |
| es | Spanish | 13 countries |
| ar | Arabic | 12 countries |
| fr | French | 9 countries |
| de | German | 5 countries |
| zh-cn | Simplified Chinese | 4 countries |
| ru | Russian | 4 countries |
| pt | Portuguese | 3 countries |
| it | Italian | 2 countries |
| ja | Japanese | 1 country |
| ko | Korean | 1 country |
| zh-tw | Traditional Chinese (TW) | 1 country |
| zh-hk | Traditional Chinese (HK) | 1 country |

*Note: Countries with multiple official languages (e.g., Belgium, Canada, Hong Kong, Luxembourg, Macao, Rwanda, Singapore, Switzerland) were surveyed in each language separately, so they appear in multiple language groups. The total unique country count remains 66.*

## Notes

- All prompts are reproduced exactly as used in the experiments
- System prompts enforce numeric-only responses to ensure parseable outputs
- Cultural imitation prompts use `{country}` placeholder for dynamic substitution
- Questions in `questions/` are referenced by both baseline and imitation experiments
