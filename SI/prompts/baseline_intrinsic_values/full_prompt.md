# Full Prompt Template (Baseline)

This document shows how the system prompt and questions are combined in the baseline experiment.

## Prompt Structure

```
[System Prompt from system_prompts_by_language/{lang}.md]
↓
[Question from ../questions/{lang}.md with embedded response instruction]
↓
[LLM Response]
```

## Complete Example (English)

### System Message

From `system_prompts_by_language/en.md`:

```
CRITICAL: You are a survey response system. Your ONLY task is to output numbers.

STRICT OUTPUT FORMAT:
1. Single choice: ONE number only
2. Two choices (Y002): TWO numbers with ONE space
3. Multiple choice (Y003): 1-5 numbers with spaces

ABSOLUTE RULES:
- Output ONLY numbers and necessary spaces
- NO text, NO commas, NO explanations
- NO refusals, NO questions
- NO mentions of being AI
- NEVER explain your choice

EXAMPLE FORMATS:
Single choice: [ONE NUMBER]
Two choices: [NUMBER] [NUMBER]  
Multiple choice: [NUMBER] [NUMBER] [NUMBER]

REMEMBER: Numbers ONLY. Any other output = FAILURE.
```

### User Message (Question)

Questions are taken from `../questions/{lang}.md`. Example from `../questions/en.md`:

```
Taking all things together, rate how happy you would say you are. Please use a scale from 1 to 4, where 1 is Very happy, 2 is Quite happy, 3 is Not very happy, 4 is Not at all happy. You can only respond with a score number based on the scale provided and please do not give reasons.
```

### Expected Response

```
2
```

## Supported Languages

6 UN official languages are supported:

| Language | System Prompt | Questions |
|----------|---------------|-----------|
| English | `system_prompts_by_language/en.md` | `../questions/en.md` |
| French | `system_prompts_by_language/fr.md` | `../questions/fr.md` |
| Spanish | `system_prompts_by_language/es.md` | `../questions/es.md` |
| Russian | `system_prompts_by_language/ru.md` | `../questions/ru.md` |
| Arabic | `system_prompts_by_language/ar.md` | `../questions/ar.md` |
| Chinese | `system_prompts_by_language/zh-cn.md` | `../questions/zh-cn.md` |

## API Call Structure

```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": question_text}
]
```

## Consensus Mechanism

- Each question is asked 5 times (`consensus_count=5`)
- The mode (most frequent response) is calculated
- Consistency rate tracks response stability
