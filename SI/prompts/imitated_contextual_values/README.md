# Imitated Contextual Values

This directory contains the prompts used in cultural imitation experiments, where LLMs roleplay as citizens of specific countries.

## Purpose

The cultural imitation condition measures LLMs' ability to adapt their responses to match the **contextual cultural values** of specific countries, testing whether models can simulate different cultural perspectives.

## Files

| File/Directory | Description |
|----------------|-------------|
| `system_prompts_by_language/` | System prompts translated into 13 languages |
| `full_prompt_template.md` | Complete prompt template with country placeholder |

## System Prompts by Language

| File | Language | Countries |
|------|----------|-----------|
| `system_prompts_by_language/en.md` | English (Original) | 21 English-native + others as lingua franca |
| `system_prompts_by_language/es.md` | Español (Spanish) | 13 |
| `system_prompts_by_language/ar.md` | العربية (Arabic) | 12 |
| `system_prompts_by_language/fr.md` | Français (French) | 9 |
| `system_prompts_by_language/de.md` | Deutsch (German) | 5 |
| `system_prompts_by_language/zh-cn.md` | 简体中文 (Simplified Chinese) | 4 |
| `system_prompts_by_language/ru.md` | Русский (Russian) | 4 |
| `system_prompts_by_language/pt.md` | Português (Portuguese) | 3 |
| `system_prompts_by_language/it.md` | Italiano (Italian) | 2 |
| `system_prompts_by_language/ja.md` | 日本語 (Japanese) | 1 |
| `system_prompts_by_language/ko.md` | 한국어 (Korean) | 1 |
| `system_prompts_by_language/zh-tw.md` | 繁體中文 (Traditional Chinese - Taiwan) | 1 |
| `system_prompts_by_language/zh-hk.md` | 繁體中文 (Traditional Chinese - Hong Kong) | 1 |

*Note: Countries with multiple official languages (e.g., Belgium, Canada, Hong Kong, Luxembourg, Macao, Rwanda, Singapore, Switzerland) were surveyed in each language separately, so they appear in multiple language groups. The total unique country count remains 66.*

## Methodology

This experiment covers 66 countries with two conditions:

### Condition A: English Imitation
- System prompt and questions in English
- LLM roleplays as citizen of target country
- Tests cultural adaptation ability in English

### Condition B: Native Language Imitation
- System prompt in target language (from `system_prompts_by_language/`)
- Survey questions in native language (from `../questions/`)
- Tests cultural adaptation in native linguistic context

### Consensus Mechanism
- The complete survey (all 10 questions) is administered 5 times for each model-country-language combination
- The mode (most frequent response) is calculated for each question across the 5 rounds
- This approach ensures response stability and reduces random variation

## Questions Reference

Survey questions are located in `../questions/{language}.md`

## Countries Covered

66 countries across 13 languages. See `full_prompt_template.md` for complete mapping.
