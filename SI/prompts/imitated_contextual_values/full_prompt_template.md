# Full Prompt Template (Cultural Imitation)

This document shows how the system prompt and questions are combined in the cultural imitation experiment.

## Prompt Structure

```
[System Prompt with {country} placeholder]
↓
[Question from ../questions/{language}.md]
↓
[LLM Response]
```

## Complete Example (Canada)

### System Message

```
You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

Please follow these guidelines:
- Answer each question with a genuine, considered response
- Choose the option that best reflects your cultural values and beliefs
- Respond as a real person from your country would

Response format:
- Single choice questions: respond with ONE number only
- Y002 (two choices): respond with TWO numbers separated by space
- Y003 (multiple choices): respond with 1-5 numbers (from 1-11) separated by spaces

Please provide meaningful answers that reflect your cultural perspective.

IMPORTANT: You are roleplaying as a typical citizen from Canada. 
Answer all questions from the perspective of someone who grew up in Canada and shares the common cultural values of that society.
```

### User Message (Question)

Questions are taken from `../questions/{language}.md`. For Canada, use `../questions/en.md`:

```
Taking all things together, rate how happy you would say you are. Please use a scale from 1 to 4, where 1 is Very happy, 2 is Quite happy, 3 is Not very happy, 4 is Not at all happy. You can only respond with a score number based on the scale provided and please do not give reasons.
```

### Expected Response

```
2
```

## Language-Country Mapping

| Country | Language | Questions File |
|---------|----------|----------------|
| Algeria | ar | `../questions/ar.md` |
| Argentina | es | `../questions/es.md` |
| Australia | en | `../questions/en.md` |
| Austria | de | `../questions/de.md` |
| Belarus | ru | `../questions/ru.md` |
| Belgium | de | `../questions/de.md` |
| Belgium | fr | `../questions/fr.md` |
| Bolivia | es | `../questions/es.md` |
| Brazil | pt | `../questions/pt.md` |
| Burkina Faso | fr | `../questions/fr.md` |
| Canada | en | `../questions/en.md` |
| Canada | fr | `../questions/fr.md` |
| Chile | es | `../questions/es.md` |
| China | zh-cn | `../questions/zh-cn.md` |
| Colombia | es | `../questions/es.md` |
| Ecuador | es | `../questions/es.md` |
| Egypt | ar | `../questions/ar.md` |
| France | fr | `../questions/fr.md` |
| Germany | de | `../questions/de.md` |
| Ghana | en | `../questions/en.md` |
| Guatemala | es | `../questions/es.md` |
| Haiti | fr | `../questions/fr.md` |
| Hong Kong | en | `../questions/en.md` |
| Hong Kong | zh-cn | `../questions/zh-cn.md` |
| Hong Kong | zh-hk | `../questions/zh-hk.md` |
| Ireland | en | `../questions/en.md` |
| Iraq | ar | `../questions/ar.md` |
| Italy | it | `../questions/it.md` |
| Japan | ja | `../questions/ja.md` |
| Jordan | ar | `../questions/ar.md` |
| Kazakhstan | ru | `../questions/ru.md` |
| Kenya | en | `../questions/en.md` |
| Korea | ko | `../questions/ko.md` |
| Kuwait | ar | `../questions/ar.md` |
| Kyrgyzstan | ru | `../questions/ru.md` |
| Lebanon | ar | `../questions/ar.md` |
| Libya | ar | `../questions/ar.md` |
| Luxembourg | de | `../questions/de.md` |
| Luxembourg | fr | `../questions/fr.md` |
| Macao | pt | `../questions/pt.md` |
| Macao | zh-cn | `../questions/zh-cn.md` |
| Malaysia | en | `../questions/en.md` |
| Mali | fr | `../questions/fr.md` |
| Malta | en | `../questions/en.md` |
| Mexico | es | `../questions/es.md` |
| Morocco | ar | `../questions/ar.md` |
| New Zealand | en | `../questions/en.md` |
| Nicaragua | es | `../questions/es.md` |
| Nigeria | en | `../questions/en.md` |
| Pakistan | en | `../questions/en.md` |
| Palestine | ar | `../questions/ar.md` |
| Peru | es | `../questions/es.md` |
| Philippines | en | `../questions/en.md` |
| Portugal | pt | `../questions/pt.md` |
| Puerto Rico | es | `../questions/es.md` |
| Qatar | ar | `../questions/ar.md` |
| Russia | ru | `../questions/ru.md` |
| Rwanda | en | `../questions/en.md` |
| Rwanda | fr | `../questions/fr.md` |
| Singapore | en | `../questions/en.md` |
| Singapore | zh-cn | `../questions/zh-cn.md` |
| South Africa | en | `../questions/en.md` |
| Spain | es | `../questions/es.md` |
| Switzerland | de | `../questions/de.md` |
| Switzerland | fr | `../questions/fr.md` |
| Switzerland | it | `../questions/it.md` |
| Taiwan | zh-tw | `../questions/zh-tw.md` |
| Trinidad and Tobago | en | `../questions/en.md` |
| Tunisia | ar | `../questions/ar.md` |
| United Kingdom | en | `../questions/en.md` |
| United States | en | `../questions/en.md` |
| Uruguay | es | `../questions/es.md` |
| Venezuela | es | `../questions/es.md` |
| Yemen | ar | `../questions/ar.md` |
| Zambia | en | `../questions/en.md` |
| Zimbabwe | en | `../questions/en.md` |

*Note: Countries with multiple official languages (e.g., Belgium, Canada, Hong Kong, Luxembourg, Macao, Rwanda, Singapore, Switzerland) were surveyed in each language separately, so they appear in multiple language groups. The total unique country count remains 66.*

## Consensus Mechanism

- The complete survey (all 10 questions) is administered 5 times for each model-country-language combination
- The mode (most frequent response) is calculated for each question across the 5 rounds
- Consistency rate is tracked to measure response stability
