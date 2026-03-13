# PCA Calculation Results Documentation

Generated: 2026-03-12 10:11:28

## 1. Intrinsic (Baseline) Analysis
Output: `data/llm_pca/intrinsic/`

- **Total entities**: 250
- **IVS countries**: 112
- **LLM model-language combinations**: 138

### LLM Models (23)

- anthropic/claude-sonnet-4.5
- claude-3-7-sonnet-20250219
- deepseek-chat
- deepseek/deepseek-chat-v3.1
- doubao-1-5-pro-32k-250115
- google/gemini-2.5-flash
- google/gemini-2.5-pro
- google/gemini-3-pro-preview
- google/gemma-3-4b-it
- gpt-4o
- gpt-4o-mini
- kimi-k2
- meta-llama/llama-3.2-3b-instruct
- meta-llama/llama-3.3-70b-instruct
- microsoft/phi-3-mini-128k-instruct
- mistralai/mistral-medium-3.1
- mistralai/mistral-nemo
- openai/gpt-5.1
- qwen/qwen3-max
- qwen/qwq-32b
- qwen3-1.7b
- x-ai/grok-4.1-fast
- z-ai/glm-4.6

### Languages (0)


### PCA Score Ranges

| | PC1 (Survival vs Self-Expression) | PC2 (Traditional vs Secular) |
|---|---|---|
| All | [-2.974, 6.644] | [-2.674, 5.237] |
| LLM | [-2.974, 6.644] | [-1.707, 5.237] |
| IVS | [-1.865, 4.431] | [-2.674, 2.276] |

## 2. Multilingual Roleplay Analysis
Output: `data/llm_pca/multilingual/`

- **Total entities**: 781
- **IVS countries**: 112
- **Multilingual roleplay entries**: 669

### LLM Models (10)

- anthropic/claude-3.7-sonnet
- anthropic/claude-sonnet-4.5
- deepseek/deepseek-chat-v3-0324
- google/gemini-2.0-flash-001
- google/gemini-2.5-flash
- meta-llama/llama-3.3-70b-instruct
- mistralai/mistral-nemo
- openai/gpt-4o-mini
- qwen/qwq-32b
- x-ai/grok-code-fast-1

### Countries (33)

- Algeria
- Argentina
- Australia
- Belarus
- Canada
- Chile
- China
- Colombia
- Ecuador
- Egypt
- Guatemala
- Hong Kong
- Iraq
- Japan
- Jordan
- Kazakhstan
- Korea, Republic of
- Kyrgyzstan
- Lebanon
- Macao
- Mexico
- Morocco
- New Zealand
- Peru
- Russian Federation
- Singapore
- Spain
- Taiwan, Province of China
- Tajikistan
- Tunisia
- Ukraine
- United Kingdom
- United States of America

### Languages (10)

- ar
- en
- en-native
- es
- ja
- ko
- ru
- zh-cn
- zh-hk
- zh-tw

### PCA Score Ranges

| | PC1 (Survival vs Self-Expression) | PC2 (Traditional vs Secular) |
|---|---|---|
| All | [-4.818, 8.386] | [-3.661, 4.180] |
| Roleplay | [-4.818, 8.386] | [-3.661, 4.180] |
| IVS | [-1.865, 4.431] | [-2.674, 2.276] |

## 3. PCA Methodology

Both analyses use the **fixed PCA model** trained on IVS data (Stage0).
This ensures all coordinates are in the same coordinate system.

1. PPCA (Probabilistic PCA) fitted on IVS data with `d=2, min_obs=1`
2. Varimax rotation applied to principal components
3. Rescaling: `PC1_rescaled = 1.81 * PC1 + 0.38`, `PC2_rescaled = 1.61 * PC2 - 0.01`
4. LLM/Roleplay data projected using the same fixed model (no refitting)
5. Entity scores = mean of PC1_rescaled and PC2_rescaled per country_code
