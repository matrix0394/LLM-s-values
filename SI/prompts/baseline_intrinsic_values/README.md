# Baseline Intrinsic Values

This directory contains the prompts used in baseline experiments, where LLMs respond to survey questions without any cultural context or roleplay instructions.

## Purpose

The baseline condition measures each LLM's **intrinsic cultural values** - the default value positions embedded in the model through its training data, without any external cultural framing.

## Files

| File/Directory | Description |
|----------------|-------------|
| `system_prompts_by_language/` | System prompts in 6 UN official languages |
| `full_prompt.md` | Complete prompt template showing how components are combined |

## System Prompts by Language

| File | Language |
|------|----------|
| `system_prompts_by_language/en.md` | English |
| `system_prompts_by_language/fr.md` | Français (French) |
| `system_prompts_by_language/es.md` | Español (Spanish) |
| `system_prompts_by_language/ru.md` | Русский (Russian) |
| `system_prompts_by_language/ar.md` | العربية (Arabic) |
| `system_prompts_by_language/zh-cn.md` | 简体中文 (Simplified Chinese) |

## Methodology

1. Each LLM is presented with survey questions in 6 UN official languages
2. No cultural context or country-specific framing is provided
3. The LLM responds based on its inherent values from training data
4. The complete survey (all 10 questions) is administered 5 times to establish consensus
5. The mode (most frequent response) is calculated for each question across the 5 rounds
6. Results represent the LLM's "default" cultural position

## Questions Reference

Survey questions in 6 UN official languages are located in:
- `../questions/en.md` (English)
- `../questions/zh-cn.md` (Simplified Chinese)
- `../questions/es.md` (Spanish)
- `../questions/ar.md` (Arabic)
- `../questions/fr.md` (French)
- `../questions/ru.md` (Russian)
