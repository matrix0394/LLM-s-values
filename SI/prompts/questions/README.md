# Survey Questions

This directory contains the World Values Survey (WVS) questions. The original WVS questions are in English, translated into 12 additional languages for a total of 13 languages.

## Questions Overview

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

## Language Files

| File | Language | Usage |
|------|----------|-------|
| `en.md` | English (Original) | 21 English-native countries + 45 non-native countries (lingua franca) |
| `zh-cn.md` | Simplified Chinese | China, Hong Kong, Macao, Singapore |
| `es.md` | Spanish | 13 countries |
| `ar.md` | Arabic | 12 countries |
| `fr.md` | French | 9 countries |
| `de.md` | German | Germany, Austria |
| `ru.md` | Russian | Russia, Belarus, Kazakhstan, Kyrgyzstan |
| `pt.md` | Portuguese | Brazil, Macao, Portugal |
| `it.md` | Italian | Italy |
| `ja.md` | Japanese | Japan |
| `ko.md` | Korean | Korea |
| `zh-tw.md` | Traditional Chinese (Taiwan) | Taiwan |
| `zh-hk.md` | Traditional Chinese (Hong Kong) | Hong Kong |

## Usage

These questions are referenced by both experimental conditions:
- **Baseline Experiments**: Uses questions in 6 UN official languages (`en.md`, `zh-cn.md`, `es.md`, `ar.md`, `fr.md`, `ru.md`)
- **Cultural Imitation Experiments**: Uses language-specific questions based on target country (all 13 languages)
