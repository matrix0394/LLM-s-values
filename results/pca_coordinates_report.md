# PCA坐标结果文档

生成时间：2026-03-11 22:28:18

## 一、概述

本项目共有两条PCA分析流水线：

| 流水线 | 数据来源 | 输出路径 | 说明 |
|--------|----------|---------|------|
| **Intrinsic（内生式）** | `data/llm_interviews/intrinsic/interview_raw/` | `data/llm_pca/intrinsic/` | 模型以自身身份回答，无国家角色扮演 |
| **Multilingual Roleplay（多语言角色扮演）** | `data/llm_interviews/multilingual/interview_raw/` | `data/llm_pca/multilingual/` | 模型扮演指定国家回答，测试语言效应 |

两条流水线均采用**联合PCA**：将LLM数据与IVS真实国家数据合并，使用Stage0固定的PCA模型（`data/country_values/pca_model_fixed.pkl`）进行`transform`，确保所有坐标处于同一坐标系中，距离计算有意义。

---

## 二、Intrinsic LLM访谈坐标（6种UN官方语言）

模型数量：23  |  记录数（模型×语言）：138

### 2.1 各模型各语言坐标汇总

| 模型名称 | 语言 | PC1 (Self-Expression) | PC2 (Secular-Rational) |
|---------|------|----------------------|------------------------|
| anthropic/claude-sonnet-4.5 | ar | 0.4842 | 1.6264 |
| anthropic/claude-sonnet-4.5 | en | 2.9895 | 2.1080 |
| anthropic/claude-sonnet-4.5 | es | 4.3439 | 2.1793 |
| anthropic/claude-sonnet-4.5 | fr | 3.5009 | 2.1848 |
| anthropic/claude-sonnet-4.5 | ru | 2.9655 | 2.8550 |
| anthropic/claude-sonnet-4.5 | zh-cn | 1.7952 | 1.5987 |
| claude-3-7-sonnet-20250219 | ar | 2.7797 | -0.5474 |
| claude-3-7-sonnet-20250219 | en | 4.3294 | 0.5355 |
| claude-3-7-sonnet-20250219 | es | 4.1758 | 0.2553 |
| claude-3-7-sonnet-20250219 | fr | 2.7523 | 0.9778 |
| claude-3-7-sonnet-20250219 | ru | 1.9953 | 0.5168 |
| claude-3-7-sonnet-20250219 | zh-cn | 2.9655 | 2.8550 |
| deepseek-chat | ar | 1.6937 | -0.5301 |
| deepseek-chat | en | 2.6278 | -0.4386 |
| deepseek-chat | es | 1.4246 | 0.3837 |
| deepseek-chat | fr | 2.2637 | 0.6054 |
| deepseek-chat | ru | 3.7099 | 0.4849 |
| deepseek-chat | zh-cn | 4.9478 | -0.2357 |
| deepseek/deepseek-chat-v3.1 | ar | 2.0038 | -0.4207 |
| deepseek/deepseek-chat-v3.1 | en | 4.4407 | -0.6101 |
| deepseek/deepseek-chat-v3.1 | es | 3.9457 | -0.4970 |
| deepseek/deepseek-chat-v3.1 | fr | 0.6720 | 0.3015 |
| deepseek/deepseek-chat-v3.1 | ru | 1.1581 | 1.5767 |
| deepseek/deepseek-chat-v3.1 | zh-cn | 3.6881 | -0.6923 |
| doubao-1-5-pro-32k-250115 | ar | -1.4409 | -1.2100 |
| doubao-1-5-pro-32k-250115 | en | 2.8215 | -0.9355 |
| doubao-1-5-pro-32k-250115 | es | 3.9832 | 1.2584 |
| doubao-1-5-pro-32k-250115 | fr | 3.9832 | 1.2584 |
| doubao-1-5-pro-32k-250115 | ru | 3.6340 | 0.3395 |
| doubao-1-5-pro-32k-250115 | zh-cn | 2.8588 | 0.1971 |
| google/gemini-2.5-flash | ar | 2.2263 | 1.2686 |
| google/gemini-2.5-flash | en | -0.7048 | 5.2001 |
| google/gemini-2.5-flash | es | 2.2919 | -0.2541 |
| google/gemini-2.5-flash | fr | 4.1282 | -0.1136 |
| google/gemini-2.5-flash | ru | 2.0622 | -1.5846 |
| google/gemini-2.5-flash | zh-cn | 4.7691 | -1.3068 |
| google/gemini-2.5-pro | ar | 1.7805 | -0.3309 |
| google/gemini-2.5-pro | en | 3.1244 | 0.6858 |
| google/gemini-2.5-pro | es | 1.4375 | 2.1790 |
| google/gemini-2.5-pro | fr | 1.8407 | 1.7095 |
| google/gemini-2.5-pro | ru | 1.8407 | 1.7095 |
| google/gemini-2.5-pro | zh-cn | 2.2679 | 0.4929 |
| google/gemini-3-pro-preview | ar | -1.3127 | -1.6399 |
| google/gemini-3-pro-preview | en | 0.4209 | 1.1832 |
| google/gemini-3-pro-preview | es | 2.0163 | 1.4422 |
| google/gemini-3-pro-preview | fr | 2.5212 | 2.2373 |
| google/gemini-3-pro-preview | ru | 1.0542 | 1.4660 |
| google/gemini-3-pro-preview | zh-cn | 1.0542 | 1.4660 |
| google/gemma-3-4b-it | ar | -2.3446 | -0.4098 |
| google/gemma-3-4b-it | en | 1.1977 | 2.3206 |
| google/gemma-3-4b-it | es | 0.5905 | 2.3297 |
| google/gemma-3-4b-it | fr | -0.4067 | 2.4109 |
| google/gemma-3-4b-it | ru | -2.9741 | -0.0137 |
| google/gemma-3-4b-it | zh-cn | -0.7722 | 1.7930 |
| gpt-4o | ar | -0.4808 | 2.3126 |
| gpt-4o | en | 0.8105 | 1.0541 |
| gpt-4o | es | 2.8197 | 2.8154 |
| gpt-4o | fr | 2.7440 | 1.3167 |
| gpt-4o | ru | 3.2684 | 0.4453 |
| gpt-4o | zh-cn | 2.9829 | 1.4185 |
| gpt-4o-mini | ar | 1.4580 | -0.2858 |
| gpt-4o-mini | en | 6.6439 | -1.4228 |
| gpt-4o-mini | es | 4.0480 | 1.4748 |
| gpt-4o-mini | fr | 3.9063 | 0.2110 |
| gpt-4o-mini | ru | 4.6845 | -1.3178 |
| gpt-4o-mini | zh-cn | 4.2818 | 0.8790 |
| kimi-k2 | ar | 2.5473 | 0.1179 |
| kimi-k2 | en | 3.8878 | 0.4057 |
| kimi-k2 | es | 4.5586 | 0.2742 |
| kimi-k2 | fr | 4.7026 | 0.9711 |
| kimi-k2 | ru | 2.9832 | 1.7068 |
| kimi-k2 | zh-cn | 6.1703 | -1.0265 |
| meta-llama/llama-3.2-3b-instruct | ar | 0.0430 | 1.1086 |
| meta-llama/llama-3.2-3b-instruct | en | 0.5000 | 2.4209 |
| meta-llama/llama-3.2-3b-instruct | es | 3.5779 | 1.8052 |
| meta-llama/llama-3.2-3b-instruct | fr | 2.7786 | 1.7855 |
| meta-llama/llama-3.2-3b-instruct | ru | 1.3774 | 1.5053 |
| meta-llama/llama-3.2-3b-instruct | zh-cn | 0.0685 | 0.4843 |
| meta-llama/llama-3.3-70b-instruct | ar | 0.9121 | 0.5256 |
| meta-llama/llama-3.3-70b-instruct | en | 2.1329 | 1.9151 |
| meta-llama/llama-3.3-70b-instruct | es | 1.1532 | 1.9676 |
| meta-llama/llama-3.3-70b-instruct | fr | 2.0098 | 2.1605 |
| meta-llama/llama-3.3-70b-instruct | ru | 0.8300 | 3.2949 |
| meta-llama/llama-3.3-70b-instruct | zh-cn | 3.1381 | 1.7912 |
| microsoft/phi-3-mini-128k-instruct | ar | 0.0761 | 0.3387 |
| microsoft/phi-3-mini-128k-instruct | en | 2.6053 | 0.9780 |
| microsoft/phi-3-mini-128k-instruct | es | 3.1446 | 1.0728 |
| microsoft/phi-3-mini-128k-instruct | fr | 2.8496 | 1.0999 |
| microsoft/phi-3-mini-128k-instruct | ru | 3.1969 | 0.5484 |
| microsoft/phi-3-mini-128k-instruct | zh-cn | 2.0117 | 1.4192 |
| mistralai/mistral-medium-3.1 | ar | 1.2243 | -0.6871 |
| mistralai/mistral-medium-3.1 | en | 0.8138 | 3.5959 |
| mistralai/mistral-medium-3.1 | es | 1.8476 | 2.6507 |
| mistralai/mistral-medium-3.1 | fr | 3.2740 | -1.1039 |
| mistralai/mistral-medium-3.1 | ru | 2.9459 | 0.6142 |
| mistralai/mistral-medium-3.1 | zh-cn | 3.2834 | 2.6632 |
| mistralai/mistral-nemo | ar | 1.4131 | 4.9846 |
| mistralai/mistral-nemo | en | 6.0521 | -0.4711 |
| mistralai/mistral-nemo | es | 0.6917 | 4.3689 |
| mistralai/mistral-nemo | fr | 3.2977 | 3.9193 |
| mistralai/mistral-nemo | ru | 0.2016 | 4.0554 |
| mistralai/mistral-nemo | zh-cn | 0.7575 | 4.8601 |
| openai/gpt-5.1 | ar | 2.6422 | 2.6596 |
| openai/gpt-5.1 | en | 2.6422 | 2.6596 |
| openai/gpt-5.1 | es | 4.0142 | 2.7021 |
| openai/gpt-5.1 | fr | 4.7123 | 3.6923 |
| openai/gpt-5.1 | ru | 0.9886 | 2.9886 |
| openai/gpt-5.1 | zh-cn | 3.9901 | 3.4491 |
| qwen/qwen3-max | ar | 3.1548 | -1.6067 |
| qwen/qwen3-max | en | 0.7599 | -0.3662 |
| qwen/qwen3-max | es | 4.1933 | 0.2267 |
| qwen/qwen3-max | fr | 0.3152 | 0.8790 |
| qwen/qwen3-max | ru | 5.6256 | -1.1138 |
| qwen/qwen3-max | zh-cn | 1.8178 | -1.7066 |
| qwen/qwq-32b | ar | 0.3482 | 3.2256 |
| qwen/qwq-32b | en | 2.5504 | 4.1078 |
| qwen/qwq-32b | es | 2.7855 | 2.9686 |
| qwen/qwq-32b | fr | 2.7680 | 2.9973 |
| qwen/qwq-32b | ru | 0.4259 | 5.2373 |
| qwen/qwq-32b | zh-cn | 0.8891 | 3.7973 |
| qwen3-1.7b | ar | -0.5341 | 4.8068 |
| qwen3-1.7b | en | 3.4952 | -0.0769 |
| qwen3-1.7b | es | -1.1994 | 4.0622 |
| qwen3-1.7b | fr | 0.7575 | 4.8601 |
| qwen3-1.7b | ru | 4.1589 | 0.6991 |
| qwen3-1.7b | zh-cn | -1.0065 | 4.5573 |
| x-ai/grok-4.1-fast | ar | 2.3343 | 4.9322 |
| x-ai/grok-4.1-fast | en | 5.0249 | 2.6395 |
| x-ai/grok-4.1-fast | es | 1.3895 | 3.6730 |
| x-ai/grok-4.1-fast | fr | 5.4945 | 1.4782 |
| x-ai/grok-4.1-fast | ru | 1.5817 | 4.8500 |
| x-ai/grok-4.1-fast | zh-cn | 1.1236 | 4.2638 |
| z-ai/glm-4.6 | ar | 1.5657 | 0.1062 |
| z-ai/glm-4.6 | en | 2.6371 | -0.1380 |
| z-ai/glm-4.6 | es | 1.0542 | 1.4660 |
| z-ai/glm-4.6 | fr | 0.6609 | 2.8438 |
| z-ai/glm-4.6 | ru | 0.6609 | 2.8438 |
| z-ai/glm-4.6 | zh-cn | 1.0301 | 2.2130 |

### 2.2 各语言平均坐标

| 语言 | 平均PC1 | 平均PC2 |
|------|---------|---------|
| ar | 0.9815 | 0.8846 |
| en | 2.6871 | 1.1892 |
| es | 2.5343 | 1.7741 |
| fr | 2.6751 | 1.6818 |
| ru | 2.1033 | 1.4655 |
| zh-cn | 2.3527 | 1.5318 |

### 2.3 IVS真实国家坐标（基准，112个国家）

| 国家 | 文化区域 | PC1 (Self-Expression) | PC2 (Secular-Rational) |
|------|---------|----------------------|------------------------|
| Albania | African-Islamic | -0.9818 | -0.2804 |
| Algeria | African-Islamic | -1.0635 | -0.8397 |
| Andorra | Catholic Europe | 2.9995 | 1.4204 |
| Azerbaijan | African-Islamic | -1.3107 | -1.0891 |
| Argentina | Latin America | 0.7647 | -0.1880 |
| Australia | English-Speaking | 3.3612 | 0.7100 |
| Austria | Catholic Europe | 2.1530 | 1.0715 |
| Bangladesh | African-Islamic | -1.0373 | -1.8551 |
| Armenia | Orthodox Europe | -1.2218 | -1.0043 |
| Belgium | Catholic Europe | 2.4095 | 0.8956 |
| Bolivia (Plurinational State of) | Latin America | -0.5193 | -1.3858 |
| Bosnia and Herzegovina | Orthodox Europe | -0.6759 | 0.1872 |
| Brazil | Latin America | 0.0143 | -0.3564 |
| Bulgaria | Orthodox Europe | -0.6076 | 1.0678 |
| Myanmar | West & South Asia | -1.2867 | -1.4825 |
| Belarus | Orthodox Europe | -0.3382 | 0.5094 |
| Canada | English-Speaking | 3.1377 | 0.9553 |
| Chile | Latin America | 0.2226 | -0.1563 |
| China | Confucian | -0.0043 | 0.6869 |
| Taiwan (Province of China) | Confucian | -0.1525 | 1.3510 |
| Colombia | Latin America | 0.1297 | -1.9558 |
| Croatia | Catholic Europe | 0.4411 | 0.4405 |
| Cyprus | Orthodox Europe | -0.2371 | -0.4285 |
| 197.0 |  | -0.7196 | -0.1994 |
| Czechia | Catholic Europe | 1.4942 | 1.7678 |
| Denmark | Protestant Europe | 4.2813 | 1.8460 |
| Ecuador | Latin America | -0.1858 | -2.0780 |
| Ethiopia | African-Islamic | -1.0522 | -1.2610 |
| Estonia | Protestant Europe | 0.2896 | 1.3189 |
| Finland | Protestant Europe | 2.8995 | 1.3228 |
| France | Catholic Europe | 2.6562 | 1.1930 |
| Georgia | Orthodox Europe | -1.4996 | -1.0976 |
| Palestine, State of | African-Islamic | -1.6869 | -1.0360 |
| Germany | Protestant Europe | 2.2903 | 1.7950 |
| Ghana | African-Islamic | -1.1858 | -2.3480 |
| Greece | Orthodox Europe | -0.0171 | 0.2417 |
| Guatemala | Latin America | 0.3323 | -1.0905 |
| Haiti | Latin America | 0.2835 | -0.7053 |
| Hong Kong | Confucian | 0.5673 | 1.7672 |
| Hungary | Catholic Europe | 0.1820 | 0.8360 |
| Iceland | Protestant Europe | 3.9785 | 1.1384 |
| India | West & South Asia | -0.5777 | -0.8914 |
| Indonesia | African-Islamic | -1.2364 | -1.3225 |
| Iran (Islamic Republic of) | African-Islamic | -1.2547 | -0.9416 |
| Iraq | African-Islamic | -1.2467 | -0.7422 |
| Ireland | Catholic Europe | 1.4781 | -0.6801 |
| Italy | Catholic Europe | 1.1003 | 0.5055 |
| Japan | Confucian | 1.5875 | 2.0382 |
| Kazakhstan | African-Islamic | -0.6790 | -0.5441 |
| Jordan | African-Islamic | -1.7794 | -1.9998 |
| Kenya | African-Islamic | -0.1617 | -0.9336 |
| Korea (the Republic of) | Confucian | 0.0245 | 1.3397 |
| Kuwait | African-Islamic | 0.3378 | -1.1095 |
| Kyrgyzstan | African-Islamic | -0.8787 | -1.5853 |
| Lebanon | African-Islamic | -1.1551 | -0.5374 |
| Latvia | Catholic Europe | -0.0626 | 0.9881 |
| Libya | African-Islamic | -1.3297 | -1.9898 |
| Lithuania | Catholic Europe | -0.3201 | 1.0984 |
| Luxembourg | Catholic Europe | 2.2680 | 0.8774 |
| Macao | Confucian | 0.8458 | 1.6738 |
| Malaysia | West & South Asia | -0.5739 | -0.8427 |
| Maldives | African-Islamic | -0.8156 | -1.4853 |
| Mali | African-Islamic | -0.1521 | -1.3862 |
| Malta | Catholic Europe | -0.2147 | -1.4678 |
| Mexico | Latin America | 0.5796 | -1.5944 |
| Mongolia | Confucian | 0.6373 | 1.2445 |
| Moldova (the Republic of) | Orthodox Europe | -1.8581 | 0.5216 |
| Montenegro | Orthodox Europe | -0.2533 | 0.0341 |
| Morocco | African-Islamic | -1.2974 | -0.9016 |
| Netherlands (the) | Protestant Europe | 3.3784 | 1.5541 |
| New Zealand | English-Speaking | 3.3111 | 0.7641 |
| Nicaragua | Latin America | -0.5272 | -1.9531 |
| Nigeria | African-Islamic | -1.1790 | -1.5972 |
| Norway | Protestant Europe | 4.1852 | 1.7562 |
| Pakistan | African-Islamic | -0.7685 | -1.5343 |
| Peru | Latin America | -0.4193 | -0.9224 |
| Philippines (the) | Latin America | -0.0514 | -1.7205 |
| Poland | Catholic Europe | 0.1972 | -0.3490 |
| Portugal | Catholic Europe | -0.0465 | -0.2432 |
| Puerto Rico | Latin America | 0.8707 | -1.5902 |
| Qatar | African-Islamic | -0.4501 | -2.6741 |
| Romania | Orthodox Europe | -1.2734 | -0.2530 |
| Russian Federation (the) | Orthodox Europe | -0.6920 | 0.4689 |
| Rwanda | African-Islamic | -1.1755 | -1.6065 |
| Serbia | Orthodox Europe | -0.2436 | 0.5902 |
| Singapore | West & South Asia | 0.3365 | -0.0469 |
| Slovakia | Catholic Europe | 0.4904 | 0.8544 |
| Viet Nam | West & South Asia | 0.5015 | -0.7033 |
| Slovenia | Catholic Europe | 1.4739 | 1.0783 |
| South Africa | African-Islamic | 0.0345 | -0.8346 |
| Zimbabwe | African-Islamic | -1.7190 | -1.3092 |
| Spain | Catholic Europe | 1.6596 | 0.7773 |
| Sweden | Protestant Europe | 4.4311 | 2.2756 |
| Switzerland | Protestant Europe | 3.2036 | 1.2257 |
| Tajikistan | African-Islamic | -0.2685 | -1.7976 |
| Thailand | West & South Asia | 0.1401 | -0.3689 |
| Trinidad and Tobago | Latin America | -0.5502 | -2.1330 |
| Tunisia | African-Islamic | -1.8653 | -0.9187 |
| Turkey | African-Islamic | -1.1137 | -1.0790 |
| Ukraine | Orthodox Europe | -0.8346 | 0.5129 |
| Republic of North Macedonia | Orthodox Europe | 0.0526 | 0.2223 |
| Egypt | African-Islamic | -1.4627 | -0.4924 |
| United Kingdom of Great Britain and Northern Ireland (the) | English-Speaking | 3.1062 | 1.0912 |
| United States of America (the) | English-Speaking | 2.0787 | 0.3202 |
| Burkina Faso | African-Islamic | -0.8588 | -1.2262 |
| Uruguay | Latin America | 1.4359 | -0.1281 |
| Uzbekistan | African-Islamic | 0.0951 | -1.9554 |
| Venezuela (Bolivarian Republic of) | Latin America | -0.2624 | -1.1704 |
| Yemen | African-Islamic | -1.3770 | -1.4155 |
| Zambia | African-Islamic | -0.9603 | -0.5082 |
| 909.0 |  | 1.7081 | 0.0989 |
| 915.0 |  | -0.7174 | -1.3369 |

---

## 三、Multilingual Roleplay角色扮演坐标

模型数量：10  |  国家数量：33  |  语言数量：10  |  记录数：669

**模型列表（10个）：** anthropic/claude-3.7-sonnet, anthropic/claude-sonnet-4.5, deepseek/deepseek-chat-v3-0324, google/gemini-2.0-flash-001, google/gemini-2.5-flash, meta-llama/llama-3.3-70b-instruct, mistralai/mistral-nemo, openai/gpt-4o-mini, qwen/qwq-32b, x-ai/grok-code-fast-1

**国家列表（33个）：** Algeria, Argentina, Australia, Belarus, Canada, Chile, China, Colombia, Ecuador, Egypt, Guatemala, Hong Kong, Iraq, Japan, Jordan, Kazakhstan, Korea, Republic of, Kyrgyzstan, Lebanon, Macao, Mexico, Morocco, New Zealand, Peru, Russian Federation, Singapore, Spain, Taiwan, Province of China, Tajikistan, Tunisia, Ukraine, United Kingdom, United States of America

**语言列表（10个）：** ar, en, en-native, es, ja, ko, ru, zh-cn, zh-hk, zh-tw

### 3.1 各模型×国家×语言坐标

| 模型 | 国家 | 语言 | PC1 | PC2 |
|------|------|------|-----|-----|
| anthropic/claude-3.7-sonnet | Algeria | ar | -1.9276 | -2.1676 |
| anthropic/claude-sonnet-4.5 | Algeria | ar | 0.0318 | -2.2725 |
| deepseek/deepseek-chat-v3-0324 | Algeria | ar | -1.6887 | -2.0657 |
| google/gemini-2.0-flash-001 | Algeria | ar | -1.7168 | -2.0012 |
| google/gemini-2.5-flash | Algeria | ar | 0.6776 | -2.2459 |
| meta-llama/llama-3.3-70b-instruct | Algeria | ar | -1.7168 | -2.0012 |
| mistralai/mistral-nemo | Algeria | ar | 0.6490 | -1.3197 |
| openai/gpt-4o-mini | Algeria | ar | 0.9615 | -1.4975 |
| qwen/qwq-32b | Algeria | ar | -0.5556 | -2.1250 |
| x-ai/grok-code-fast-1 | Algeria | ar | -1.7875 | -2.3969 |
| anthropic/claude-3.7-sonnet | Algeria | en | -1.8057 | -1.9616 |
| anthropic/claude-sonnet-4.5 | Algeria | en | 0.0543 | -0.7877 |
| deepseek/deepseek-chat-v3-0324 | Algeria | en | -1.3561 | -1.6934 |
| google/gemini-2.0-flash-001 | Algeria | en | -2.3547 | -0.9510 |
| google/gemini-2.5-flash | Algeria | en | 0.0318 | -2.2725 |
| meta-llama/llama-3.3-70b-instruct | Algeria | en | -1.7875 | -2.3969 |
| mistralai/mistral-nemo | Algeria | en | 1.0012 | -1.1270 |
| openai/gpt-4o-mini | Algeria | en | -0.4105 | -1.5401 |
| qwen/qwq-32b | Algeria | en | 0.0318 | -2.2725 |
| x-ai/grok-code-fast-1 | Algeria | en | 0.1944 | -1.0170 |
| anthropic/claude-3.7-sonnet | Argentina | en | 2.9573 | 1.5725 |
| anthropic/claude-sonnet-4.5 | Argentina | en | 1.4536 | 1.8043 |
| deepseek/deepseek-chat-v3-0324 | Argentina | en | 2.8885 | 0.4708 |
| google/gemini-2.0-flash-001 | Argentina | en | 1.8009 | 1.2528 |
| google/gemini-2.5-flash | Argentina | en | 3.5528 | 1.2997 |
| meta-llama/llama-3.3-70b-instruct | Argentina | en | 2.5158 | 1.6656 |
| mistralai/mistral-nemo | Argentina | en | 5.5979 | 0.7958 |
| openai/gpt-4o-mini | Argentina | en | 4.3417 | 1.6435 |
| qwen/qwq-32b | Argentina | en | 4.2919 | 2.9908 |
| x-ai/grok-code-fast-1 | Argentina | en | 3.9894 | 3.0046 |
| anthropic/claude-3.7-sonnet | Argentina | es | 1.8899 | 1.2132 |
| anthropic/claude-sonnet-4.5 | Argentina | es | 2.5139 | 1.6014 |
| deepseek/deepseek-chat-v3-0324 | Argentina | es | 2.8885 | 0.4708 |
| google/gemini-2.0-flash-001 | Argentina | es | 0.2687 | 0.1412 |
| google/gemini-2.5-flash | Argentina | es | 3.6403 | 1.1564 |
| meta-llama/llama-3.3-70b-instruct | Argentina | es | 2.8727 | 0.9238 |
| mistralai/mistral-nemo | Argentina | es | 0.8511 | -1.5507 |
| openai/gpt-4o-mini | Argentina | es | 6.0297 | -0.7525 |
| qwen/qwq-32b | Argentina | es | 4.2590 | 2.7452 |
| x-ai/grok-code-fast-1 | Argentina | es | 3.5047 | 2.7937 |
| anthropic/claude-3.7-sonnet | Australia | en-native | 6.1241 | 2.4487 |
| anthropic/claude-sonnet-4.5 | Australia | en-native | 6.5023 | 2.7279 |
| deepseek/deepseek-chat-v3-0324 | Australia | en-native | 6.5513 | 1.2321 |
| google/gemini-2.0-flash-001 | Australia | en-native | 5.1785 | 2.2954 |
| google/gemini-2.5-flash | Australia | en-native | 4.1507 | 2.7378 |
| meta-llama/llama-3.3-70b-instruct | Australia | en-native | 4.5392 | 2.4385 |
| mistralai/mistral-nemo | Australia | en-native | 7.9966 | 0.0315 |
| openai/gpt-4o-mini | Australia | en-native | 6.2429 | 1.1248 |
| qwen/qwq-32b | Australia | en-native | 7.4770 | 2.7325 |
| x-ai/grok-code-fast-1 | Australia | en-native | 7.0498 | 3.9491 |
| anthropic/claude-3.7-sonnet | Belarus | en | -0.5464 | 0.7419 |
| anthropic/claude-sonnet-4.5 | Belarus | en | -0.3965 | 0.8834 |
| deepseek/deepseek-chat-v3-0324 | Belarus | en | -1.0899 | 0.2033 |
| google/gemini-2.0-flash-001 | Belarus | en | -0.4855 | 0.9230 |
| google/gemini-2.5-flash | Belarus | en | -0.7572 | 0.5756 |
| meta-llama/llama-3.3-70b-instruct | Belarus | en | -0.6941 | 0.4538 |
| mistralai/mistral-nemo | Belarus | en | -0.8619 | 0.2171 |
| openai/gpt-4o-mini | Belarus | en | 1.4665 | 0.5011 |
| qwen/qwq-32b | Belarus | en | -0.5697 | 0.3629 |
| x-ai/grok-code-fast-1 | Belarus | en | -0.5066 | 0.9946 |
| anthropic/claude-3.7-sonnet | Belarus | ru | -0.6333 | 0.4786 |
| anthropic/claude-sonnet-4.5 | Belarus | ru | 0.5024 | 0.4263 |
| deepseek/deepseek-chat-v3-0324 | Belarus | ru | 1.0858 | -1.2846 |
| google/gemini-2.0-flash-001 | Belarus | ru | -1.1788 | 0.2429 |
| google/gemini-2.5-flash | Belarus | ru | 1.2196 | 0.4420 |
| meta-llama/llama-3.3-70b-instruct | Belarus | ru | -0.9378 | 0.0419 |
| mistralai/mistral-nemo | Belarus | ru | 0.9214 | 0.9908 |
| openai/gpt-4o-mini | Belarus | ru | 0.3509 | 0.5317 |
| qwen/qwq-32b | Belarus | ru | -2.1174 | 0.0967 |
| x-ai/grok-code-fast-1 | Belarus | ru | -0.0764 | 0.5448 |
| anthropic/claude-3.7-sonnet | Canada | en-native | 4.7089 | 1.2330 |
| anthropic/claude-sonnet-4.5 | Canada | en-native | 6.5023 | 2.7279 |
| deepseek/deepseek-chat-v3-0324 | Canada | en-native | 6.5513 | 1.2321 |
| google/gemini-2.0-flash-001 | Canada | en-native | 5.3893 | 2.4617 |
| google/gemini-2.5-flash | Canada | en-native | 5.4897 | 2.5348 |
| meta-llama/llama-3.3-70b-instruct | Canada | en-native | 6.2548 | 1.9217 |
| mistralai/mistral-nemo | Canada | en-native | 7.5934 | 0.5010 |
| openai/gpt-4o-mini | Canada | en-native | 5.0631 | 2.2592 |
| qwen/qwq-32b | Canada | en-native | 6.9104 | 3.7718 |
| x-ai/grok-code-fast-1 | Canada | en-native | 6.9980 | 3.6285 |
| anthropic/claude-3.7-sonnet | Chile | en | 2.8683 | 1.6121 |
| anthropic/claude-sonnet-4.5 | Chile | en | 2.0994 | 1.8309 |
| deepseek/deepseek-chat-v3-0324 | Chile | en | 2.6497 | 0.3690 |
| google/gemini-2.0-flash-001 | Chile | en | 1.5861 | 0.4040 |
| google/gemini-2.5-flash | Chile | en | 3.1031 | 1.0315 |
| meta-llama/llama-3.3-70b-instruct | Chile | en | 1.4004 | -0.0727 |
| mistralai/mistral-nemo | Chile | en | 5.8102 | -1.2697 |
| openai/gpt-4o-mini | Chile | en | 3.7037 | 2.6937 |
| qwen/qwq-32b | Chile | en | 3.0599 | 2.0820 |
| x-ai/grok-code-fast-1 | Chile | en | 1.6888 | 2.1879 |
| anthropic/claude-3.7-sonnet | Chile | es | 1.9126 | 0.9176 |
| anthropic/claude-sonnet-4.5 | Chile | es | 2.0642 | 1.3332 |
| deepseek/deepseek-chat-v3-0324 | Chile | es | 2.7018 | -0.4425 |
| google/gemini-2.0-flash-001 | Chile | es | 0.0539 | -0.7077 |
| google/gemini-2.5-flash | Chile | es | 3.2187 | 0.8237 |
| meta-llama/llama-3.3-70b-instruct | Chile | es | 0.4917 | 0.6961 |
| mistralai/mistral-nemo | Chile | es | 1.4505 | 1.4265 |
| openai/gpt-4o-mini | Chile | es | 4.7281 | 0.1760 |
| qwen/qwq-32b | Chile | es | 1.1298 | 2.4246 |
| x-ai/grok-code-fast-1 | Chile | es | 1.9407 | 0.8531 |
| anthropic/claude-3.7-sonnet | China | en | 0.0705 | -0.0805 |
| anthropic/claude-sonnet-4.5 | China | en | 0.5132 | 0.1806 |
| deepseek/deepseek-chat-v3-0324 | China | en | 0.5132 | 0.1806 |
| google/gemini-2.0-flash-001 | China | en | -0.7931 | -0.2806 |
| google/gemini-2.5-flash | China | en | -0.0976 | 0.0967 |
| meta-llama/llama-3.3-70b-instruct | China | en | 0.1875 | -0.1845 |
| mistralai/mistral-nemo | China | en | 2.9854 | 0.8280 |
| openai/gpt-4o-mini | China | en | 1.6415 | -0.1887 |
| qwen/qwq-32b | China | en | 0.9115 | 0.1343 |
| x-ai/grok-code-fast-1 | China | en | 1.2135 | 0.8679 |
| anthropic/claude-3.7-sonnet | China | zh-cn | 0.2743 | 0.0787 |
| anthropic/claude-sonnet-4.5 | China | zh-cn | 0.5132 | 0.1806 |
| deepseek/deepseek-chat-v3-0324 | China | zh-cn | -0.1326 | 0.1540 |
| google/gemini-2.0-flash-001 | China | zh-cn | -0.9990 | -0.1369 |
| google/gemini-2.5-flash | China | zh-cn | 1.8947 | 0.2373 |
| meta-llama/llama-3.3-70b-instruct | China | zh-cn | 0.8199 | 0.3145 |
| mistralai/mistral-nemo | China | zh-cn | 2.5041 | -2.4707 |
| openai/gpt-4o-mini | China | zh-cn | 2.5331 | -0.0531 |
| qwen/qwq-32b | China | zh-cn | 1.2674 | 0.1321 |
| x-ai/grok-code-fast-1 | China | zh-cn | 0.3569 | 0.6749 |
| anthropic/claude-3.7-sonnet | Colombia | en | 2.5091 | -0.9275 |
| anthropic/claude-sonnet-4.5 | Colombia | en | 1.5812 | 0.0939 |
| deepseek/deepseek-chat-v3-0324 | Colombia | en | 2.3411 | -0.7503 |
| google/gemini-2.0-flash-001 | Colombia | en | 1.3424 | -0.0079 |
| google/gemini-2.5-flash | Colombia | en | 2.6486 | 0.4532 |
| meta-llama/llama-3.3-70b-instruct | Colombia | en | 0.4733 | -0.1062 |
| mistralai/mistral-nemo | Colombia | en | 2.0259 | -0.4276 |
| openai/gpt-4o-mini | Colombia | en | 3.8288 | -0.3605 |
| qwen/qwq-32b | Colombia | en | 1.7087 | -1.2494 |
| x-ai/grok-code-fast-1 | Colombia | en | -0.1042 | 0.2434 |
| anthropic/claude-3.7-sonnet | Colombia | es | 2.7480 | -0.8256 |
| anthropic/claude-sonnet-4.5 | Colombia | es | 1.9664 | 0.3802 |
| deepseek/deepseek-chat-v3-0324 | Colombia | es | 1.8914 | -1.0186 |
| google/gemini-2.0-flash-001 | Colombia | es | -0.2788 | -1.0800 |
| google/gemini-2.5-flash | Colombia | es | 1.4580 | -0.2157 |
| meta-llama/llama-3.3-70b-instruct | Colombia | es | 0.2809 | 0.5297 |
| mistralai/mistral-nemo | Colombia | es | 2.0297 | 0.8135 |
| openai/gpt-4o-mini | Colombia | es | 5.9079 | -0.9584 |
| qwen/qwq-32b | Colombia | es | 0.9049 | 0.2810 |
| x-ai/grok-code-fast-1 | Colombia | es | -0.3781 | 0.1989 |
| anthropic/claude-3.7-sonnet | Ecuador | en | 2.1765 | -1.2998 |
| anthropic/claude-sonnet-4.5 | Ecuador | en | 1.5812 | 0.0939 |
| deepseek/deepseek-chat-v3-0324 | Ecuador | en | 1.8674 | -0.2716 |
| google/gemini-2.0-flash-001 | Ecuador | en | 1.1035 | -0.1098 |
| google/gemini-2.5-flash | Ecuador | en | 1.9657 | -1.4661 |
| meta-llama/llama-3.3-70b-instruct | Ecuador | en | 1.4004 | -0.0727 |
| mistralai/mistral-nemo | Ecuador | en | 2.5564 | -0.0228 |
| openai/gpt-4o-mini | Ecuador | en | 3.5899 | -0.4624 |
| qwen/qwq-32b | Ecuador | en | 3.1951 | 1.6593 |
| x-ai/grok-code-fast-1 | Ecuador | en | 1.4055 | -0.1297 |
| anthropic/claude-3.7-sonnet | Ecuador | es | 1.3199 | -1.4927 |
| anthropic/claude-sonnet-4.5 | Ecuador | es | 1.3704 | -0.0724 |
| deepseek/deepseek-chat-v3-0324 | Ecuador | es | 1.8914 | -1.0186 |
| google/gemini-2.0-flash-001 | Ecuador | es | -1.0002 | -1.6956 |
| google/gemini-2.5-flash | Ecuador | es | 1.3199 | -1.4927 |
| meta-llama/llama-3.3-70b-instruct | Ecuador | es | 1.8693 | -0.8106 |
| mistralai/mistral-nemo | Ecuador | es | 0.4699 | -0.1575 |
| openai/gpt-4o-mini | Ecuador | es | 4.8867 | -1.7008 |
| qwen/qwq-32b | Ecuador | es | 3.2858 | 0.5088 |
| x-ai/grok-code-fast-1 | Ecuador | es | -0.8985 | -0.4650 |
| anthropic/claude-3.7-sonnet | Egypt | ar | -1.7168 | -2.0012 |
| anthropic/claude-sonnet-4.5 | Egypt | ar | 0.0318 | -2.2725 |
| deepseek/deepseek-chat-v3-0324 | Egypt | ar | -1.6887 | -2.0657 |
| google/gemini-2.0-flash-001 | Egypt | ar | -1.9276 | -2.1676 |
| google/gemini-2.5-flash | Egypt | ar | -0.1790 | -2.4389 |
| meta-llama/llama-3.3-70b-instruct | Egypt | ar | -1.7168 | -2.0012 |
| mistralai/mistral-nemo | Egypt | ar | 0.7787 | -1.7283 |
| openai/gpt-4o-mini | Egypt | ar | 0.9615 | -1.4975 |
| qwen/qwq-32b | Egypt | ar | -0.5556 | -2.1250 |
| x-ai/grok-code-fast-1 | Egypt | ar | -1.5486 | -2.2950 |
| anthropic/claude-3.7-sonnet | Egypt | en | -1.9276 | -2.1676 |
| anthropic/claude-sonnet-4.5 | Egypt | en | -1.4779 | -1.8994 |
| deepseek/deepseek-chat-v3-0324 | Egypt | en | 0.6033 | -1.7983 |
| google/gemini-2.0-flash-001 | Egypt | en | -1.9276 | -2.1676 |
| google/gemini-2.5-flash | Egypt | en | -0.1790 | -2.4389 |
| meta-llama/llama-3.3-70b-instruct | Egypt | en | -1.7875 | -2.3969 |
| mistralai/mistral-nemo | Egypt | en | -0.0670 | -3.3327 |
| openai/gpt-4o-mini | Egypt | en | -0.6213 | -1.7064 |
| qwen/qwq-32b | Egypt | en | -0.5556 | -2.1250 |
| x-ai/grok-code-fast-1 | Egypt | en | -1.5767 | -2.2305 |
| anthropic/claude-3.7-sonnet | Guatemala | en | 0.4150 | -0.4799 |
| anthropic/claude-sonnet-4.5 | Guatemala | en | 0.8927 | -0.2762 |
| deepseek/deepseek-chat-v3-0324 | Guatemala | en | 1.4417 | -1.2868 |
| google/gemini-2.0-flash-001 | Guatemala | en | -1.3055 | -0.2731 |
| google/gemini-2.5-flash | Guatemala | en | -0.0066 | -0.8126 |
| meta-llama/llama-3.3-70b-instruct | Guatemala | en | -0.9969 | 0.8462 |
| mistralai/mistral-nemo | Guatemala | en | 2.9363 | -0.7720 |
| openai/gpt-4o-mini | Guatemala | en | 2.7131 | 0.4860 |
| qwen/qwq-32b | Guatemala | en | -1.8922 | 0.9923 |
| x-ai/grok-code-fast-1 | Guatemala | en | -1.7201 | -0.5987 |
| anthropic/claude-3.7-sonnet | Guatemala | es | 1.0810 | -1.5946 |
| anthropic/claude-sonnet-4.5 | Guatemala | es | 0.8927 | -0.2762 |
| deepseek/deepseek-chat-v3-0324 | Guatemala | es | 1.2534 | 0.0317 |
| google/gemini-2.0-flash-001 | Guatemala | es | -1.4498 | -1.9638 |
| google/gemini-2.5-flash | Guatemala | es | 0.6839 | -1.9488 |
| meta-llama/llama-3.3-70b-instruct | Guatemala | es | -0.9183 | -0.0701 |
| mistralai/mistral-nemo | Guatemala | es | 1.1912 | 0.3019 |
| openai/gpt-4o-mini | Guatemala | es | 4.5260 | -2.0086 |
| qwen/qwq-32b | Guatemala | es | -1.6053 | -0.3999 |
| x-ai/grok-code-fast-1 | Guatemala | es | -2.1866 | -1.2448 |
| anthropic/claude-3.7-sonnet | Hong Kong | en | 1.2704 | 1.6524 |
| anthropic/claude-sonnet-4.5 | Hong Kong | en | 1.7302 | 2.4618 |
| deepseek/deepseek-chat-v3-0324 | Hong Kong | en | 0.2960 | 1.9360 |
| google/gemini-2.0-flash-001 | Hong Kong | en | 0.1141 | 1.3327 |
| google/gemini-2.5-flash | Hong Kong | en | -0.3460 | 2.3037 |
| meta-llama/llama-3.3-70b-instruct | Hong Kong | en | 0.9026 | 2.3529 |
| mistralai/mistral-nemo | Hong Kong | en | 0.8208 | 1.3842 |
| openai/gpt-4o-mini | Hong Kong | en | 0.9378 | 1.2801 |
| qwen/qwq-32b | Hong Kong | en | 0.1210 | 1.3398 |
| x-ai/grok-code-fast-1 | Hong Kong | en | 0.5932 | 3.0928 |
| anthropic/claude-3.7-sonnet | Hong Kong | zh-cn | 1.2717 | 1.2010 |
| anthropic/claude-sonnet-4.5 | Hong Kong | zh-cn | 3.6567 | 2.1113 |
| deepseek/deepseek-chat-v3-0324 | Hong Kong | zh-cn | 2.4902 | 1.2504 |
| google/gemini-2.0-flash-001 | Hong Kong | zh-cn | -1.0752 | 0.7674 |
| google/gemini-2.5-flash | Hong Kong | zh-cn | 2.2314 | 2.5781 |
| meta-llama/llama-3.3-70b-instruct | Hong Kong | zh-cn | 0.9266 | 1.6059 |
| mistralai/mistral-nemo | Hong Kong | zh-cn | 1.5487 | -2.8782 |
| openai/gpt-4o-mini | Hong Kong | zh-cn | 2.3224 | 0.9840 |
| qwen/qwq-32b | Hong Kong | zh-cn | 0.7745 | 1.7673 |
| x-ai/grok-code-fast-1 | Hong Kong | zh-cn | 3.0626 | 4.0968 |
| anthropic/claude-3.7-sonnet | Hong Kong | zh-hk | 1.2461 | 4.1798 |
| anthropic/claude-sonnet-4.5 | Hong Kong | zh-hk | 2.4662 | 1.9974 |
| deepseek/deepseek-chat-v3-0324 | Hong Kong | zh-hk | 2.2448 | 1.8669 |
| google/gemini-2.0-flash-001 | Hong Kong | zh-hk | -0.0078 | 1.1267 |
| google/gemini-2.5-flash | Hong Kong | zh-hk | 2.3144 | 1.0268 |
| meta-llama/llama-3.3-70b-instruct | Hong Kong | zh-hk | 1.8582 | 3.0474 |
| mistralai/mistral-nemo | Hong Kong | zh-hk | 4.6685 | -0.4929 |
| openai/gpt-4o-mini | Hong Kong | zh-hk | 3.3759 | 2.6315 |
| qwen/qwq-32b | Hong Kong | zh-hk | 1.0029 | 1.9049 |
| x-ai/grok-code-fast-1 | Hong Kong | zh-hk | 2.7019 | 3.7889 |
| anthropic/claude-3.7-sonnet | Iraq | ar | -3.1073 | -1.0332 |
| anthropic/claude-sonnet-4.5 | Iraq | ar | -0.3954 | -1.0560 |
| deepseek/deepseek-chat-v3-0324 | Iraq | ar | -1.6887 | -2.0657 |
| google/gemini-2.0-flash-001 | Iraq | ar | -1.9276 | -2.1676 |
| google/gemini-2.5-flash | Iraq | ar | -1.2818 | -2.1410 |
| meta-llama/llama-3.3-70b-instruct | Iraq | ar | -1.7168 | -2.0012 |
| mistralai/mistral-nemo | Iraq | ar | 0.4878 | -1.0187 |
| openai/gpt-4o-mini | Iraq | ar | 0.9615 | -1.4975 |
| qwen/qwq-32b | Iraq | ar | -3.5345 | 0.1833 |
| x-ai/grok-code-fast-1 | Iraq | ar | -3.6052 | -0.2123 |
| anthropic/claude-3.7-sonnet | Iraq | en | -3.5345 | 0.1833 |
| anthropic/claude-sonnet-4.5 | Iraq | en | -3.5345 | 0.1833 |
| deepseek/deepseek-chat-v3-0324 | Iraq | en | -1.3561 | -1.6934 |
| google/gemini-2.0-flash-001 | Iraq | en | -2.3547 | -0.9510 |
| google/gemini-2.5-flash | Iraq | en | -3.7453 | 0.0170 |
| meta-llama/llama-3.3-70b-instruct | Iraq | en | -2.2146 | -1.1803 |
| mistralai/mistral-nemo | Iraq | en | -2.0399 | -0.6739 |
| openai/gpt-4o-mini | Iraq | en | -1.0485 | -0.4899 |
| qwen/qwq-32b | Iraq | en | -4.8183 | 1.2069 |
| x-ai/grok-code-fast-1 | Iraq | en | -3.3944 | -0.0460 |
| anthropic/claude-3.7-sonnet | Japan | en | 0.2968 | 1.5635 |
| anthropic/claude-sonnet-4.5 | Japan | en | 0.2968 | 1.5635 |
| deepseek/deepseek-chat-v3-0324 | Japan | en | 0.7520 | 0.2825 |
| google/gemini-2.0-flash-001 | Japan | en | 0.3249 | 1.4990 |
| google/gemini-2.5-flash | Japan | en | 0.2030 | 1.2931 |
| meta-llama/llama-3.3-70b-instruct | Japan | en | 2.2130 | 0.2854 |
| mistralai/mistral-nemo | Japan | en | 3.9565 | -0.7756 |
| openai/gpt-4o-mini | Japan | en | 2.3300 | 0.1814 |
| qwen/qwq-32b | Japan | en | 2.1184 | 1.8743 |
| x-ai/grok-code-fast-1 | Japan | en | 1.3460 | 2.2414 |
| anthropic/claude-3.7-sonnet | Japan | ja | 1.1942 | 1.3533 |
| anthropic/claude-sonnet-4.5 | Japan | ja | 2.0389 | 2.0106 |
| deepseek/deepseek-chat-v3-0324 | Japan | ja | 1.2431 | -0.1424 |
| google/gemini-2.0-flash-001 | Japan | ja | 1.1919 | 0.4528 |
| google/gemini-2.5-flash | Japan | ja | 2.8922 | -0.3383 |
| meta-llama/llama-3.3-70b-instruct | Japan | ja | -0.4329 | 0.8370 |
| mistralai/mistral-nemo | Japan | ja | 1.6590 | -0.2174 |
| openai/gpt-4o-mini | Japan | ja | 2.9604 | -0.0663 |
| qwen/qwq-32b | Japan | ja | 1.9273 | 1.3764 |
| x-ai/grok-code-fast-1 | Japan | ja | 1.2907 | 0.5111 |
| anthropic/claude-3.7-sonnet | Jordan | ar | -1.5949 | -1.7953 |
| anthropic/claude-sonnet-4.5 | Jordan | ar | 0.0318 | -2.2725 |
| deepseek/deepseek-chat-v3-0324 | Jordan | ar | -1.6887 | -2.0657 |
| google/gemini-2.0-flash-001 | Jordan | ar | -1.9276 | -2.1676 |
| google/gemini-2.5-flash | Jordan | ar | -0.1790 | -2.4389 |
| meta-llama/llama-3.3-70b-instruct | Jordan | ar | -1.7168 | -2.0012 |
| mistralai/mistral-nemo | Jordan | ar | 1.2700 | -3.2328 |
| openai/gpt-4o-mini | Jordan | ar | 0.9615 | -1.4975 |
| qwen/qwq-32b | Jordan | ar | -0.7664 | -2.2914 |
| x-ai/grok-code-fast-1 | Jordan | ar | -1.9276 | -2.1676 |
| anthropic/claude-3.7-sonnet | Jordan | en | -1.8057 | -1.9616 |
| anthropic/claude-sonnet-4.5 | Jordan | en | -1.6887 | -2.0657 |
| deepseek/deepseek-chat-v3-0324 | Jordan | en | -1.3561 | -1.6934 |
| google/gemini-2.0-flash-001 | Jordan | en | -1.6887 | -2.0657 |
| google/gemini-2.5-flash | Jordan | en | -0.1790 | -2.4389 |
| meta-llama/llama-3.3-70b-instruct | Jordan | en | -1.7875 | -2.3969 |
| mistralai/mistral-nemo | Jordan | en | 0.0742 | -1.3292 |
| openai/gpt-4o-mini | Jordan | en | 0.9615 | -1.4975 |
| qwen/qwq-32b | Jordan | en | -2.3547 | -0.9510 |
| x-ai/grok-code-fast-1 | Jordan | en | -1.7875 | -2.3969 |
| anthropic/claude-3.7-sonnet | Kazakhstan | en | -0.7846 | -1.2192 |
| anthropic/claude-sonnet-4.5 | Kazakhstan | en | -0.4014 | 0.5734 |
| deepseek/deepseek-chat-v3-0324 | Kazakhstan | en | -0.4519 | -0.8469 |
| google/gemini-2.0-flash-001 | Kazakhstan | en | -1.0899 | 0.2033 |
| google/gemini-2.5-flash | Kazakhstan | en | 0.9359 | -1.4260 |
| meta-llama/llama-3.3-70b-instruct | Kazakhstan | en | -0.5107 | -1.1747 |
| mistralai/mistral-nemo | Kazakhstan | en | 1.6967 | -2.2025 |
| openai/gpt-4o-mini | Kazakhstan | en | 1.3222 | -1.1897 |
| qwen/qwq-32b | Kazakhstan | en | 0.1853 | -0.7914 |
| x-ai/grok-code-fast-1 | Kazakhstan | en | -0.8441 | 0.3123 |
| anthropic/claude-3.7-sonnet | Kazakhstan | ru | -0.9659 | 0.1063 |
| anthropic/claude-sonnet-4.5 | Kazakhstan | ru | 1.4742 | -0.8974 |
| deepseek/deepseek-chat-v3-0324 | Kazakhstan | ru | 1.1748 | -1.3242 |
| google/gemini-2.0-flash-001 | Kazakhstan | ru | -0.8735 | -1.1796 |
| google/gemini-2.5-flash | Kazakhstan | ru | 1.5250 | -0.9805 |
| meta-llama/llama-3.3-70b-instruct | Kazakhstan | ru | -0.9378 | 0.0419 |
| mistralai/mistral-nemo | Kazakhstan | ru | 0.0706 | -1.1300 |
| openai/gpt-4o-mini | Kazakhstan | ru | 1.9112 | -0.7442 |
| qwen/qwq-32b | Kazakhstan | ru | 0.6147 | 0.6181 |
| x-ai/grok-code-fast-1 | Kazakhstan | ru | -1.0549 | 0.1459 |
| anthropic/claude-3.7-sonnet | Korea, Republic of | en | -0.6354 | 0.7815 |
| anthropic/claude-sonnet-4.5 | Korea, Republic of | en | 2.1343 | 1.2526 |
| deepseek/deepseek-chat-v3-0324 | Korea, Republic of | en | 2.2289 | -0.3362 |
| google/gemini-2.0-flash-001 | Korea, Republic of | en | 1.4739 | 0.8181 |
| google/gemini-2.5-flash | Korea, Republic of | en | 2.5364 | 0.8673 |
| meta-llama/llama-3.3-70b-instruct | Korea, Republic of | en | -0.0233 | -0.3509 |
| mistralai/mistral-nemo | Korea, Republic of | en | 1.1611 | -0.0957 |
| openai/gpt-4o-mini | Korea, Republic of | en | 1.1213 | -0.3484 |
| qwen/qwq-32b | Korea, Republic of | en | 0.7240 | 0.3469 |
| x-ai/grok-code-fast-1 | Korea, Republic of | en | -0.7831 | 0.4934 |
| anthropic/claude-3.7-sonnet | Korea, Republic of | ko | 0.5771 | 0.9723 |
| anthropic/claude-sonnet-4.5 | Korea, Republic of | ko | 1.7777 | 1.6273 |
| deepseek/deepseek-chat-v3-0324 | Korea, Republic of | ko | 0.7935 | -0.4107 |
| google/gemini-2.0-flash-001 | Korea, Republic of | ko | 2.4298 | -0.2678 |
| google/gemini-2.5-flash | Korea, Republic of | ko | 1.1261 | -0.0384 |
| meta-llama/llama-3.3-70b-instruct | Korea, Republic of | ko | 1.6684 | -0.1207 |
| mistralai/mistral-nemo | Korea, Republic of | ko | 1.3363 | 0.1842 |
| openai/gpt-4o-mini | Korea, Republic of | ko | 2.6840 | 1.2901 |
| qwen/qwq-32b | Korea, Republic of | ko | 1.1309 | 0.2717 |
| x-ai/grok-code-fast-1 | Korea, Republic of | ko | 0.7093 | -0.0610 |
| anthropic/claude-3.7-sonnet | Kyrgyzstan | en | -1.4506 | -0.1046 |
| anthropic/claude-sonnet-4.5 | Kyrgyzstan | en | -1.2117 | -0.0027 |
| deepseek/deepseek-chat-v3-0324 | Kyrgyzstan | en | 1.5074 | -0.9519 |
| google/gemini-2.0-flash-001 | Kyrgyzstan | en | -1.3007 | 0.0369 |
| google/gemini-2.5-flash | Kyrgyzstan | en | 0.0591 | -0.4777 |
| meta-llama/llama-3.3-70b-instruct | Kyrgyzstan | en | -1.4156 | -0.1619 |
| mistralai/mistral-nemo | Kyrgyzstan | en | 3.3787 | -0.8687 |
| openai/gpt-4o-mini | Kyrgyzstan | en | 1.6548 | -0.8174 |
| qwen/qwq-32b | Kyrgyzstan | en | -0.0048 | 1.6380 |
| x-ai/grok-code-fast-1 | Kyrgyzstan | en | -1.3218 | 0.1085 |
| anthropic/claude-3.7-sonnet | Kyrgyzstan | ru | 0.7546 | -0.1005 |
| anthropic/claude-sonnet-4.5 | Kyrgyzstan | ru | 0.9710 | -1.4834 |
| deepseek/deepseek-chat-v3-0324 | Kyrgyzstan | ru | 1.1748 | -1.3242 |
| google/gemini-2.0-flash-001 | Kyrgyzstan | ru | 1.0858 | -1.2846 |
| google/gemini-2.5-flash | Kyrgyzstan | ru | 1.4669 | -1.5982 |
| meta-llama/llama-3.3-70b-instruct | Kyrgyzstan | ru | -1.6544 | -0.2638 |
| mistralai/mistral-nemo | Kyrgyzstan | ru | -1.3072 | 0.7553 |
| openai/gpt-4o-mini | Kyrgyzstan | ru | 1.9112 | -0.7442 |
| qwen/qwq-32b | Kyrgyzstan | ru | -0.0048 | 1.6380 |
| x-ai/grok-code-fast-1 | Kyrgyzstan | ru | -1.8652 | -0.4301 |
| anthropic/claude-3.7-sonnet | Lebanon | ar | -2.9630 | 0.6575 |
| anthropic/claude-sonnet-4.5 | Lebanon | ar | -0.9058 | 1.5055 |
| deepseek/deepseek-chat-v3-0324 | Lebanon | ar | -1.1172 | -1.5915 |
| google/gemini-2.0-flash-001 | Lebanon | ar | -1.5924 | 1.1190 |
| google/gemini-2.5-flash | Lebanon | ar | -0.1695 | -0.7393 |
| meta-llama/llama-3.3-70b-instruct | Lebanon | ar | -0.5457 | -1.1174 |
| mistralai/mistral-nemo | Lebanon | ar | 0.8279 | -0.4117 |
| openai/gpt-4o-mini | Lebanon | ar | 1.8937 | -0.7155 |
| qwen/qwq-32b | Lebanon | ar | -0.0452 | 2.3810 |
| x-ai/grok-code-fast-1 | Lebanon | ar | -2.7722 | 2.2534 |
| anthropic/claude-3.7-sonnet | Lebanon | en | -1.7832 | -0.4769 |
| anthropic/claude-sonnet-4.5 | Lebanon | en | 0.8647 | -0.2117 |
| deepseek/deepseek-chat-v3-0324 | Lebanon | en | 0.7476 | -0.1076 |
| google/gemini-2.0-flash-001 | Lebanon | en | -1.5444 | -0.3750 |
| google/gemini-2.5-flash | Lebanon | en | 0.1559 | 0.5595 |
| meta-llama/llama-3.3-70b-instruct | Lebanon | en | -0.8568 | 0.6169 |
| mistralai/mistral-nemo | Lebanon | en | 3.9402 | -1.2844 |
| openai/gpt-4o-mini | Lebanon | en | 0.8394 | 0.9867 |
| qwen/qwq-32b | Lebanon | en | -1.5328 | 3.2454 |
| x-ai/grok-code-fast-1 | Lebanon | en | -1.3843 | 1.6743 |
| anthropic/claude-3.7-sonnet | Macao | en | -0.1577 | 0.9853 |
| anthropic/claude-sonnet-4.5 | Macao | en | 0.3201 | 1.1890 |
| deepseek/deepseek-chat-v3-0324 | Macao | en | 0.3201 | 1.1890 |
| google/gemini-2.0-flash-001 | Macao | en | -0.2466 | 1.0249 |
| google/gemini-2.5-flash | Macao | en | 1.7079 | 0.6099 |
| meta-llama/llama-3.3-70b-instruct | Macao | en | 0.2107 | -0.5591 |
| mistralai/mistral-nemo | Macao | en | 4.2508 | 1.0566 |
| openai/gpt-4o-mini | Macao | en | 2.4932 | -0.3058 |
| qwen/qwq-32b | Macao | en | 1.3136 | -0.2510 |
| x-ai/grok-code-fast-1 | Macao | en | 0.4194 | -0.0898 |
| anthropic/claude-3.7-sonnet | Macao | zh-cn | 0.2920 | 1.2535 |
| anthropic/claude-sonnet-4.5 | Macao | zh-cn | 3.1042 | 0.9472 |
| deepseek/deepseek-chat-v3-0324 | Macao | zh-cn | 2.4677 | -0.2344 |
| google/gemini-2.0-flash-001 | Macao | zh-cn | 0.3304 | -0.0502 |
| google/gemini-2.5-flash | Macao | zh-cn | 1.7281 | -0.5314 |
| meta-llama/llama-3.3-70b-instruct | Macao | zh-cn | 0.2613 | 0.8613 |
| mistralai/mistral-nemo | Macao | zh-cn | 2.9257 | -2.1380 |
| openai/gpt-4o-mini | Macao | zh-cn | 2.2006 | 0.7780 |
| qwen/qwq-32b | Macao | zh-cn | 1.2674 | 0.1321 |
| x-ai/grok-code-fast-1 | Macao | zh-cn | -0.4302 | -0.2756 |
| anthropic/claude-3.7-sonnet | Macao | zh-hk | 0.2872 | 0.9435 |
| anthropic/claude-sonnet-4.5 | Macao | zh-hk | 2.2132 | 0.8930 |
| deepseek/deepseek-chat-v3-0324 | Macao | zh-hk | 1.9187 | 0.7763 |
| google/gemini-2.0-flash-001 | Macao | zh-hk | 0.4194 | -0.0898 |
| google/gemini-2.5-flash | Macao | zh-hk | 1.8500 | -0.3254 |
| meta-llama/llama-3.3-70b-instruct | Macao | zh-hk | 2.0549 | 1.2365 |
| mistralai/mistral-nemo | Macao | zh-hk | 4.6925 | -1.2399 |
| openai/gpt-4o-mini | Macao | zh-hk | 3.1803 | 0.7255 |
| qwen/qwq-32b | Macao | zh-hk | 1.0791 | 1.4505 |
| x-ai/grok-code-fast-1 | Macao | zh-hk | -1.0039 | -0.4469 |
| anthropic/claude-3.7-sonnet | Mexico | en | 2.9588 | -0.6593 |
| anthropic/claude-sonnet-4.5 | Mexico | en | 0.8124 | 0.3127 |
| deepseek/deepseek-chat-v3-0324 | Mexico | en | 2.3411 | -0.7503 |
| google/gemini-2.0-flash-001 | Mexico | en | 1.4642 | 0.1980 |
| google/gemini-2.5-flash | Mexico | en | 1.7976 | -1.2890 |
| meta-llama/llama-3.3-70b-instruct | Mexico | en | 2.3451 | -0.0678 |
| mistralai/mistral-nemo | Mexico | en | 0.0421 | 0.4278 |
| openai/gpt-4o-mini | Mexico | en | 3.7807 | 1.1335 |
| qwen/qwq-32b | Mexico | en | -0.0680 | -0.9136 |
| x-ai/grok-code-fast-1 | Mexico | en | -0.3431 | 0.1415 |
| anthropic/claude-3.7-sonnet | Mexico | es | 2.7480 | -0.8256 |
| anthropic/claude-sonnet-4.5 | Mexico | es | 1.9664 | 0.3802 |
| deepseek/deepseek-chat-v3-0324 | Mexico | es | 2.3411 | -0.7503 |
| google/gemini-2.0-flash-001 | Mexico | es | -0.5225 | -1.4919 |
| google/gemini-2.5-flash | Mexico | es | 2.6542 | -1.0960 |
| meta-llama/llama-3.3-70b-instruct | Mexico | es | 0.0372 | 0.3373 |
| mistralai/mistral-nemo | Mexico | es | 2.4630 | 0.7099 |
| openai/gpt-4o-mini | Mexico | es | 5.2426 | -1.7030 |
| qwen/qwq-32b | Mexico | es | 1.2560 | 0.6229 |
| x-ai/grok-code-fast-1 | Mexico | es | -0.3781 | 0.1989 |
| anthropic/claude-3.7-sonnet | Morocco | ar | 0.3644 | -1.9002 |
| anthropic/claude-sonnet-4.5 | Morocco | ar | 0.0318 | -2.2725 |
| deepseek/deepseek-chat-v3-0324 | Morocco | ar | -1.3280 | -1.7579 |
| google/gemini-2.0-flash-001 | Morocco | ar | -1.7168 | -2.0012 |
| google/gemini-2.5-flash | Morocco | ar | 0.2426 | -2.1062 |
| meta-llama/llama-3.3-70b-instruct | Morocco | ar | -1.5060 | -1.8349 |
| mistralai/mistral-nemo | Morocco | ar | 0.9334 | -1.4330 |
| openai/gpt-4o-mini | Morocco | ar | 0.9615 | -1.4975 |
| qwen/qwq-32b | Morocco | ar | -1.4498 | -1.9638 |
| x-ai/grok-code-fast-1 | Morocco | ar | -1.6887 | -2.0657 |
| anthropic/claude-3.7-sonnet | Morocco | en | -1.5669 | -1.8598 |
| anthropic/claude-sonnet-4.5 | Morocco | en | 0.4815 | -2.0043 |
| deepseek/deepseek-chat-v3-0324 | Morocco | en | 0.6033 | -1.7983 |
| google/gemini-2.0-flash-001 | Morocco | en | -1.9051 | -0.6828 |
| google/gemini-2.5-flash | Morocco | en | 0.0318 | -2.2725 |
| meta-llama/llama-3.3-70b-instruct | Morocco | en | -1.5486 | -2.2950 |
| mistralai/mistral-nemo | Morocco | en | 1.2540 | -2.4635 |
| openai/gpt-4o-mini | Morocco | en | 1.2003 | -1.3956 |
| qwen/qwq-32b | Morocco | en | 0.0159 | -1.6509 |
| x-ai/grok-code-fast-1 | Morocco | en | -1.7875 | -2.3969 |
| anthropic/claude-3.7-sonnet | New Zealand | en-native | 4.9286 | 2.3919 |
| anthropic/claude-sonnet-4.5 | New Zealand | en-native | 4.5429 | 2.8328 |
| deepseek/deepseek-chat-v3-0324 | New Zealand | en-native | 6.8744 | -0.0952 |
| google/gemini-2.0-flash-001 | New Zealand | en-native | 5.1785 | 2.2954 |
| google/gemini-2.5-flash | New Zealand | en-native | 6.1887 | 1.6656 |
| meta-llama/llama-3.3-70b-instruct | New Zealand | en-native | 4.5392 | 2.4385 |
| mistralai/mistral-nemo | New Zealand | en-native | 8.3861 | -0.0977 |
| openai/gpt-4o-mini | New Zealand | en-native | 6.2429 | 1.1248 |
| qwen/qwq-32b | New Zealand | en-native | 6.4810 | 3.0860 |
| x-ai/grok-code-fast-1 | New Zealand | en-native | 6.5755 | 1.4971 |
| anthropic/claude-3.7-sonnet | Peru | en | 1.2254 | 0.0961 |
| anthropic/claude-sonnet-4.5 | Peru | en | 1.9139 | 0.4662 |
| deepseek/deepseek-chat-v3-0324 | Peru | en | 2.1303 | -0.9167 |
| google/gemini-2.0-flash-001 | Peru | en | 0.9865 | -0.0057 |
| google/gemini-2.5-flash | Peru | en | 1.5385 | -0.2496 |
| meta-llama/llama-3.3-70b-instruct | Peru | en | 0.9227 | -0.2764 |
| mistralai/mistral-nemo | Peru | en | 4.2649 | -0.7532 |
| openai/gpt-4o-mini | Peru | en | 3.5899 | -0.4624 |
| qwen/qwq-32b | Peru | en | 0.9440 | -0.0610 |
| x-ai/grok-code-fast-1 | Peru | en | 0.7169 | -0.4998 |
| anthropic/claude-3.7-sonnet | Peru | es | 1.4417 | -1.2868 |
| anthropic/claude-sonnet-4.5 | Peru | es | 1.7556 | 0.2139 |
| deepseek/deepseek-chat-v3-0324 | Peru | es | 2.1303 | -0.9167 |
| google/gemini-2.0-flash-001 | Peru | es | -0.8783 | -1.4897 |
| google/gemini-2.5-flash | Peru | es | 1.3724 | -1.5787 |
| meta-llama/llama-3.3-70b-instruct | Peru | es | 0.4973 | -0.8532 |
| mistralai/mistral-nemo | Peru | es | 0.9342 | 0.5187 |
| openai/gpt-4o-mini | Peru | es | 4.8867 | -1.7008 |
| qwen/qwq-32b | Peru | es | 1.9649 | -0.3603 |
| x-ai/grok-code-fast-1 | Peru | es | 0.9453 | -0.3622 |
| anthropic/claude-3.7-sonnet | Russian Federation | en | -0.7572 | 0.5756 |
| anthropic/claude-sonnet-4.5 | Russian Federation | en | -0.6402 | 0.4715 |
| deepseek/deepseek-chat-v3-0324 | Russian Federation | en | -0.4169 | -0.9043 |
| google/gemini-2.0-flash-001 | Russian Federation | en | -0.7292 | 0.5111 |
| google/gemini-2.5-flash | Russian Federation | en | -0.4519 | -0.8469 |
| meta-llama/llama-3.3-70b-instruct | Russian Federation | en | -0.2670 | -0.7628 |
| mistralai/mistral-nemo | Russian Federation | en | 0.3684 | 0.5030 |
| openai/gpt-4o-mini | Russian Federation | en | 0.5567 | -0.8154 |
| qwen/qwq-32b | Russian Federation | en | -1.6363 | -1.1022 |
| x-ai/grok-code-fast-1 | Russian Federation | en | -0.5395 | 0.7491 |
| anthropic/claude-3.7-sonnet | Russian Federation | ru | -0.6333 | 0.4786 |
| anthropic/claude-sonnet-4.5 | Russian Federation | ru | -0.1732 | -0.4924 |
| deepseek/deepseek-chat-v3-0324 | Russian Federation | ru | 1.4360 | -0.9409 |
| google/gemini-2.0-flash-001 | Russian Federation | ru | -0.7517 | -0.9737 |
| google/gemini-2.5-flash | Russian Federation | ru | 1.0472 | -1.1843 |
| meta-llama/llama-3.3-70b-instruct | Russian Federation | ru | -0.8160 | 0.2478 |
| mistralai/mistral-nemo | Russian Federation | ru | -1.7288 | 0.4226 |
| openai/gpt-4o-mini | Russian Federation | ru | 0.3004 | -0.8886 |
| qwen/qwq-32b | Russian Federation | ru | -0.6991 | -1.0597 |
| x-ai/grok-code-fast-1 | Russian Federation | ru | -0.9611 | 0.4164 |
| anthropic/claude-3.7-sonnet | Singapore | en | 0.0258 | -0.6432 |
| anthropic/claude-sonnet-4.5 | Singapore | en | 0.9580 | 0.1388 |
| deepseek/deepseek-chat-v3-0324 | Singapore | en | 0.5084 | -0.1294 |
| google/gemini-2.0-flash-001 | Singapore | en | 0.3865 | -0.3354 |
| google/gemini-2.5-flash | Singapore | en | 2.1960 | -0.5818 |
| meta-llama/llama-3.3-70b-instruct | Singapore | en | 0.2107 | -0.5591 |
| mistralai/mistral-nemo | Singapore | en | 2.4627 | -1.0241 |
| openai/gpt-4o-mini | Singapore | en | 2.7040 | -0.1395 |
| qwen/qwq-32b | Singapore | en | 1.2394 | 0.1966 |
| x-ai/grok-code-fast-1 | Singapore | en | 0.7822 | -0.0849 |
| anthropic/claude-3.7-sonnet | Singapore | zh-cn | 0.7143 | -0.2731 |
| anthropic/claude-sonnet-4.5 | Singapore | zh-cn | 4.1254 | 0.1191 |
| deepseek/deepseek-chat-v3-0324 | Singapore | zh-cn | 0.8362 | -0.0672 |
| google/gemini-2.0-flash-001 | Singapore | zh-cn | -0.0351 | -0.6681 |
| google/gemini-2.5-flash | Singapore | zh-cn | 2.1960 | -0.5818 |
| meta-llama/llama-3.3-70b-instruct | Singapore | zh-cn | 0.6323 | -0.2264 |
| mistralai/mistral-nemo | Singapore | zh-cn | 3.7129 | -1.1875 |
| openai/gpt-4o-mini | Singapore | zh-cn | 3.7293 | -0.2851 |
| qwen/qwq-32b | Singapore | zh-cn | 2.6801 | 0.5250 |
| x-ai/grok-code-fast-1 | Singapore | zh-cn | 0.8199 | -0.4390 |
| anthropic/claude-3.7-sonnet | Spain | en | 2.6709 | 2.3051 |
| anthropic/claude-sonnet-4.5 | Spain | en | 2.9146 | 2.7170 |
| deepseek/deepseek-chat-v3-0324 | Spain | en | 3.0104 | 0.6768 |
| google/gemini-2.0-flash-001 | Spain | en | 0.6239 | 1.9983 |
| google/gemini-2.5-flash | Spain | en | 3.6506 | 2.2527 |
| meta-llama/llama-3.3-70b-instruct | Spain | en | 2.5399 | 0.9186 |
| mistralai/mistral-nemo | Spain | en | 6.5113 | -0.4224 |
| openai/gpt-4o-mini | Spain | en | 3.9026 | 1.3395 |
| qwen/qwq-32b | Spain | en | 4.2638 | 3.0552 |
| x-ai/grok-code-fast-1 | Spain | en | 6.9104 | 3.7718 |
| anthropic/claude-3.7-sonnet | Spain | es | 1.4817 | 1.7399 |
| anthropic/claude-sonnet-4.5 | Spain | es | 1.9887 | 2.2321 |
| deepseek/deepseek-chat-v3-0324 | Spain | es | 2.6777 | 0.3045 |
| google/gemini-2.0-flash-001 | Spain | es | 0.1044 | 0.7126 |
| google/gemini-2.5-flash | Spain | es | 5.5243 | 1.7520 |
| meta-llama/llama-3.3-70b-instruct | Spain | es | 2.0745 | 0.9050 |
| mistralai/mistral-nemo | Spain | es | 1.9637 | 0.0910 |
| openai/gpt-4o-mini | Spain | es | 5.4863 | -1.2911 |
| qwen/qwq-32b | Spain | es | 3.9792 | 1.1889 |
| x-ai/grok-code-fast-1 | Spain | es | 4.1104 | 3.0621 |
| anthropic/claude-3.7-sonnet | Taiwan, Province of China | en | 2.3431 | 2.2428 |
| anthropic/claude-sonnet-4.5 | Taiwan, Province of China | en | 1.7302 | 2.4618 |
| deepseek/deepseek-chat-v3-0324 | Taiwan, Province of China | en | 0.7232 | 0.7194 |
| google/gemini-2.0-flash-001 | Taiwan, Province of China | en | 2.1624 | 1.1882 |
| google/gemini-2.5-flash | Taiwan, Province of China | en | 3.3818 | 1.3861 |
| meta-llama/llama-3.3-70b-instruct | Taiwan, Province of China | en | 0.6323 | -0.2264 |
| mistralai/mistral-nemo | Taiwan, Province of China | en | 2.5331 | -0.0531 |
| openai/gpt-4o-mini | Taiwan, Province of China | en | 2.8539 | 0.0020 |
| qwen/qwq-32b | Taiwan, Province of China | en | 2.5737 | 0.5933 |
| x-ai/grok-code-fast-1 | Taiwan, Province of China | en | 4.8643 | 0.7061 |
| anthropic/claude-3.7-sonnet | Taiwan, Province of China | zh-cn | 1.7213 | 1.4692 |
| anthropic/claude-sonnet-4.5 | Taiwan, Province of China | zh-cn | 3.6567 | 2.1113 |
| deepseek/deepseek-chat-v3-0324 | Taiwan, Province of China | zh-cn | 2.6785 | -0.0680 |
| google/gemini-2.0-flash-001 | Taiwan, Province of China | zh-cn | 0.3304 | -0.0502 |
| google/gemini-2.5-flash | Taiwan, Province of China | zh-cn | 2.8236 | -0.2366 |
| meta-llama/llama-3.3-70b-instruct | Taiwan, Province of China | zh-cn | 0.2052 | 0.9902 |
| mistralai/mistral-nemo | Taiwan, Province of China | zh-cn | 2.2470 | -2.4102 |
| openai/gpt-4o-mini | Taiwan, Province of China | zh-cn | 2.3224 | 0.9840 |
| qwen/qwq-32b | Taiwan, Province of China | zh-cn | 3.0233 | 0.8615 |
| x-ai/grok-code-fast-1 | Taiwan, Province of China | zh-cn | 4.5424 | 2.1555 |
| anthropic/claude-3.7-sonnet | Taiwan, Province of China | zh-tw | 1.6733 | 2.9633 |
| anthropic/claude-sonnet-4.5 | Taiwan, Province of China | zh-tw | 3.4459 | 1.9450 |
| deepseek/deepseek-chat-v3-0324 | Taiwan, Province of China | zh-tw | 1.3647 | 1.8439 |
| google/gemini-2.0-flash-001 | Taiwan, Province of China | zh-tw | 0.6254 | -0.2335 |
| google/gemini-2.5-flash | Taiwan, Province of China | zh-tw | 3.0694 | -0.1275 |
| meta-llama/llama-3.3-70b-instruct | Taiwan, Province of China | zh-tw | 1.8822 | 2.3004 |
| mistralai/mistral-nemo | Taiwan, Province of China | zh-tw | 4.4489 | -1.6518 |
| openai/gpt-4o-mini | Taiwan, Province of China | zh-tw | 3.5410 | 1.0334 |
| qwen/qwq-32b | Taiwan, Province of China | zh-tw | 2.9928 | 2.3268 |
| x-ai/grok-code-fast-1 | Taiwan, Province of China | zh-tw | 4.8211 | 2.5101 |
| anthropic/claude-3.7-sonnet | Tajikistan | en | -1.3561 | -1.6934 |
| anthropic/claude-sonnet-4.5 | Tajikistan | en | -1.4779 | -1.8994 |
| deepseek/deepseek-chat-v3-0324 | Tajikistan | en | -1.2342 | -1.4875 |
| google/gemini-2.0-flash-001 | Tajikistan | en | -1.6614 | -0.2709 |
| google/gemini-2.5-flash | Tajikistan | en | 0.3644 | -1.9002 |
| meta-llama/llama-3.3-70b-instruct | Tajikistan | en | -1.6489 | -1.8130 |
| mistralai/mistral-nemo | Tajikistan | en | 0.9486 | -1.0410 |
| openai/gpt-4o-mini | Tajikistan | en | 0.4656 | -1.3826 |
| qwen/qwq-32b | Tajikistan | en | -1.0795 | -1.9457 |
| x-ai/grok-code-fast-1 | Tajikistan | en | -2.0038 | -1.0140 |
| anthropic/claude-3.7-sonnet | Tajikistan | ru | -2.9280 | 0.6002 |
| anthropic/claude-sonnet-4.5 | Tajikistan | ru | -0.4571 | -2.1505 |
| deepseek/deepseek-chat-v3-0324 | Tajikistan | ru | 0.6033 | -1.7983 |
| google/gemini-2.0-flash-001 | Tajikistan | ru | -1.5949 | -1.7953 |
| google/gemini-2.5-flash | Tajikistan | ru | 1.2561 | -1.7646 |
| meta-llama/llama-3.3-70b-instruct | Tajikistan | ru | -1.6544 | -0.2638 |
| mistralai/mistral-nemo | Tajikistan | ru | -0.8113 | 0.6404 |
| openai/gpt-4o-mini | Tajikistan | ru | 1.6723 | -0.8460 |
| qwen/qwq-32b | Tajikistan | ru | -1.5957 | -0.6895 |
| x-ai/grok-code-fast-1 | Tajikistan | ru | -2.1979 | -0.8024 |
| anthropic/claude-3.7-sonnet | Tunisia | ar | 0.6033 | -1.7983 |
| anthropic/claude-sonnet-4.5 | Tunisia | ar | -0.2975 | -0.1030 |
| deepseek/deepseek-chat-v3-0324 | Tunisia | ar | 0.8422 | -1.6965 |
| google/gemini-2.0-flash-001 | Tunisia | ar | -1.1453 | -1.5271 |
| google/gemini-2.5-flash | Tunisia | ar | 2.0642 | -1.0419 |
| meta-llama/llama-3.3-70b-instruct | Tunisia | ar | -0.5786 | -1.3629 |
| mistralai/mistral-nemo | Tunisia | ar | 0.9094 | -0.6860 |
| openai/gpt-4o-mini | Tunisia | ar | 1.2003 | -1.3956 |
| qwen/qwq-32b | Tunisia | ar | 0.7299 | 1.6250 |
| x-ai/grok-code-fast-1 | Tunisia | ar | -1.7423 | 0.9775 |
| anthropic/claude-3.7-sonnet | Tunisia | en | 0.1761 | -0.5818 |
| anthropic/claude-sonnet-4.5 | Tunisia | en | 0.6258 | -0.3136 |
| deepseek/deepseek-chat-v3-0324 | Tunisia | en | 0.9640 | -1.4905 |
| google/gemini-2.0-flash-001 | Tunisia | en | -1.7832 | -0.4769 |
| google/gemini-2.5-flash | Tunisia | en | 0.7939 | -0.4907 |
| meta-llama/llama-3.3-70b-instruct | Tunisia | en | -0.9073 | -0.8034 |
| mistralai/mistral-nemo | Tunisia | en | 1.1182 | -1.2311 |
| openai/gpt-4o-mini | Tunisia | en | 2.3018 | -1.2421 |
| qwen/qwq-32b | Tunisia | en | 2.0435 | 1.4934 |
| x-ai/grok-code-fast-1 | Tunisia | en | 0.4052 | -0.8507 |
| anthropic/claude-3.7-sonnet | Ukraine | en | 1.3828 | 1.5253 |
| anthropic/claude-sonnet-4.5 | Ukraine | en | 1.3647 | 1.8439 |
| deepseek/deepseek-chat-v3-0324 | Ukraine | en | 1.9371 | 0.7459 |
| google/gemini-2.0-flash-001 | Ukraine | en | -0.3260 | 0.0415 |
| google/gemini-2.5-flash | Ukraine | en | 3.2634 | -0.2225 |
| meta-llama/llama-3.3-70b-instruct | Ukraine | en | -0.5587 | 0.3193 |
| mistralai/mistral-nemo | Ukraine | en | 4.3342 | -0.4612 |
| openai/gpt-4o-mini | Ukraine | en | 1.7097 | 0.7567 |
| qwen/qwq-32b | Ukraine | en | 1.7286 | 0.8826 |
| x-ai/grok-code-fast-1 | Ukraine | en | 3.2610 | 2.4625 |
| anthropic/claude-3.7-sonnet | Ukraine | ru | 0.2141 | 3.3494 |
| anthropic/claude-sonnet-4.5 | Ukraine | ru | 1.2568 | 1.2251 |
| deepseek/deepseek-chat-v3-0324 | Ukraine | ru | 2.3616 | 0.6419 |
| google/gemini-2.0-flash-001 | Ukraine | ru | 1.9409 | 1.1402 |
| google/gemini-2.5-flash | Ukraine | ru | 3.4717 | 1.3447 |
| meta-llama/llama-3.3-70b-instruct | Ukraine | ru | -0.9859 | 1.5359 |
| mistralai/mistral-nemo | Ukraine | ru | 1.1895 | 1.3303 |
| openai/gpt-4o-mini | Ukraine | ru | 1.7578 | -0.7373 |
| qwen/qwq-32b | Ukraine | ru | -0.8771 | 1.9567 |
| x-ai/grok-code-fast-1 | Ukraine | ru | 2.8394 | 2.1298 |
| anthropic/claude-3.7-sonnet | United Kingdom | en-native | 4.2866 | 2.7596 |
| anthropic/claude-sonnet-4.5 | United Kingdom | en-native | 5.1303 | 2.6853 |
| deepseek/deepseek-chat-v3-0324 | United Kingdom | en-native | 3.6847 | 2.0468 |
| google/gemini-2.0-flash-001 | United Kingdom | en-native | 2.3613 | 2.6587 |
| google/gemini-2.5-flash | United Kingdom | en-native | 3.9118 | 2.6359 |
| meta-llama/llama-3.3-70b-instruct | United Kingdom | en-native | 4.1120 | 3.6551 |
| mistralai/mistral-nemo | United Kingdom | en-native | 8.0206 | -0.7155 |
| openai/gpt-4o-mini | United Kingdom | en-native | 5.0631 | 2.2592 |
| qwen/qwq-32b | United Kingdom | en-native | 3.2753 | 3.0248 |
| x-ai/grok-code-fast-1 | United Kingdom | en-native | 5.6603 | 3.9351 |
| anthropic/claude-3.7-sonnet | United States of America | en-native | 6.0903 | 1.3722 |
| anthropic/claude-sonnet-4.5 | United States of America | en-native | 4.5260 | 1.9656 |
| deepseek/deepseek-chat-v3-0324 | United States of America | en-native | 3.9660 | 1.3713 |
| google/gemini-2.0-flash-001 | United States of America | en-native | 5.7914 | 2.0764 |
| google/gemini-2.5-flash | United States of America | en-native | 4.5260 | 1.9656 |
| meta-llama/llama-3.3-70b-instruct | United States of America | en-native | 4.5677 | 1.4782 |
| mistralai/mistral-nemo | United States of America | en-native | 7.2087 | 0.9402 |
| openai/gpt-4o-mini | United States of America | en-native | 6.7788 | 1.7423 |
| qwen/qwq-32b | United States of America | en-native | 6.6618 | 1.8464 |
| x-ai/grok-code-fast-1 | United States of America | en-native | 4.7408 | 2.8145 |
| anthropic/claude-3.7-sonnet | None | ar | -1.9276 | -2.1676 |
| anthropic/claude-sonnet-4.5 | None | ar | -1.9983 | -2.5632 |
| deepseek/deepseek-chat-v3-0324 | None | ar | -1.8152 | -3.6613 |
| google/gemini-2.0-flash-001 | None | ar | -2.1384 | -2.3339 |
| google/gemini-2.5-flash | None | ar | -2.1384 | -2.3339 |
| meta-llama/llama-3.3-70b-instruct | None | ar | -0.9586 | -3.4683 |
| mistralai/mistral-nemo | None | ar | 1.2700 | -3.2328 |
| openai/gpt-4o-mini | None | ar | -0.2324 | -3.4523 |
| qwen/qwq-32b | None | ar | -1.6230 | -2.4843 |
| x-ai/grok-code-fast-1 | None | ar | -2.8549 | -2.7562 |
| anthropic/claude-3.7-sonnet | None | en | -1.9276 | -2.1676 |
| anthropic/claude-sonnet-4.5 | None | en | -1.9276 | -2.1676 |
| deepseek/deepseek-chat-v3-0324 | nan | en | -0.0737 | -0.5678 |
| deepseek/deepseek-chat-v3-0324 | None | en | -1.6044 | -3.4949 |
| google/gemini-2.0-flash-001 | nan | en | -0.4855 | 0.9230 |
| google/gemini-2.0-flash-001 | None | en | -2.7842 | -2.3605 |
| google/gemini-2.5-flash | None | en | -2.8549 | -2.7562 |
| meta-llama/llama-3.3-70b-instruct | None | en | -1.9983 | -2.5632 |
| mistralai/mistral-nemo | None | en | -1.1417 | -2.3703 |
| openai/gpt-4o-mini | nan | en | 0.3557 | 0.8417 |
| openai/gpt-4o-mini | None | en | -1.4122 | -2.3180 |
| qwen/qwq-32b | None | en | -1.6230 | -2.4843 |
| x-ai/grok-code-fast-1 | None | en | -2.8549 | -2.7562 |
| deepseek/deepseek-chat-v3-0324 | nan | en-native | 4.9445 | 1.7702 |
| google/gemini-2.0-flash-001 | nan | en-native | 4.4852 | 1.6152 |
| openai/gpt-4o-mini | nan | en-native | 7.9586 | 0.6080 |
| deepseek/deepseek-chat-v3-0324 | nan | ru | 1.4360 | -0.9409 |
| google/gemini-2.0-flash-001 | nan | ru | -0.5320 | 0.1852 |
| openai/gpt-4o-mini | nan | ru | 0.8999 | -0.4789 |

### 3.2 各国家×语言平均坐标

| 国家 | 语言 | 平均PC1 | 平均PC2 |
|------|------|---------|---------|
| Algeria | ar | -0.7073 | -2.0093 |
| Algeria | en | -0.6401 | -1.6020 |
| Argentina | en | 3.3390 | 1.6501 |
| Argentina | es | 2.8719 | 0.8743 |
| Australia | en-native | 6.1812 | 2.1718 |
| Belarus | en | -0.4441 | 0.5857 |
| Belarus | ru | -0.0864 | 0.2511 |
| Canada | en-native | 6.1461 | 2.2272 |
| Chile | en | 2.7970 | 1.0869 |
| Chile | es | 1.9692 | 0.7501 |
| China | en | 0.7146 | 0.1554 |
| China | zh-cn | 0.9032 | -0.0889 |
| Colombia | en | 1.8355 | -0.3039 |
| Colombia | es | 1.6530 | -0.1895 |
| Ecuador | en | 2.0842 | -0.2082 |
| Ecuador | es | 1.4515 | -0.8397 |
| Egypt | ar | -0.7561 | -2.0593 |
| Egypt | en | -0.9517 | -2.2263 |
| Guatemala | en | 0.2478 | -0.2175 |
| Guatemala | es | 0.3468 | -0.9173 |
| Hong Kong | en | 0.6440 | 1.9136 |
| Hong Kong | zh-cn | 1.7210 | 1.3484 |
| Hong Kong | zh-hk | 2.1871 | 2.1077 |
| Iraq | ar | -1.5808 | -1.3010 |
| Iraq | en | -2.8041 | -0.3444 |
| Japan | en | 1.3838 | 1.0009 |
| Japan | ja | 1.5965 | 0.5777 |
| Jordan | ar | -0.7538 | -2.1931 |
| Jordan | en | -1.1612 | -1.8797 |
| Kazakhstan | en | 0.0058 | -0.7762 |
| Kazakhstan | ru | 0.2938 | -0.5344 |
| Korea, Republic of | en | 0.9938 | 0.3429 |
| Korea, Republic of | ko | 1.4233 | 0.3447 |
| Kyrgyzstan | en | -0.0105 | -0.1601 |
| Kyrgyzstan | ru | 0.2533 | -0.4836 |
| Lebanon | ar | -0.7389 | 0.3341 |
| Lebanon | en | -0.0554 | 0.4627 |
| Macao | en | 1.0632 | 0.4849 |
| Macao | zh-cn | 1.4147 | 0.0742 |
| Macao | zh-hk | 1.6691 | 0.3923 |
| Mexico | en | 1.5131 | -0.1466 |
| Mexico | es | 1.7808 | -0.3618 |
| Morocco | ar | -0.5156 | -1.8833 |
| Morocco | en | -0.3221 | -1.8820 |
| New Zealand | en-native | 5.9938 | 1.7139 |
| Peru | en | 1.8233 | -0.2662 |
| Peru | es | 1.5050 | -0.7816 |
| Russian Federation | en | -0.4513 | -0.1621 |
| Russian Federation | ru | -0.2979 | -0.3974 |
| Singapore | en | 1.1474 | -0.3162 |
| Singapore | zh-cn | 1.9411 | -0.3084 |
| Spain | en | 3.6998 | 1.8613 |
| Spain | es | 2.9391 | 1.0697 |
| Taiwan, Province of China | en | 2.3798 | 0.9020 |
| Taiwan, Province of China | zh-cn | 2.3551 | 0.5807 |
| Taiwan, Province of China | zh-tw | 2.7865 | 1.2910 |
| Tajikistan | en | -0.8683 | -1.4448 |
| Tajikistan | ru | -0.7708 | -0.8870 |
| Tunisia | ar | 0.2586 | -0.7009 |
| Tunisia | en | 0.5738 | -0.5987 |
| Ukraine | en | 1.8097 | 0.7894 |
| Ukraine | ru | 1.3169 | 1.3917 |
| United Kingdom | en-native | 4.5506 | 2.4945 |
| United States of America | en-native | 5.4857 | 1.7573 |

### 3.3 IVS真实国家坐标（基准，112个国家）

| 国家 | 文化区域 | PC1 | PC2 |
|------|---------|-----|-----|
| nan | African-Islamic | -0.9818 | -0.2804 |
| nan | African-Islamic | -1.0635 | -0.8397 |
| nan | Catholic Europe | 2.9995 | 1.4204 |
| nan | African-Islamic | -1.3107 | -1.0891 |
| nan | Latin America | 0.7647 | -0.1880 |
| nan | English-Speaking | 3.3612 | 0.7100 |
| nan | Catholic Europe | 2.1530 | 1.0715 |
| nan | African-Islamic | -1.0373 | -1.8551 |
| nan | Orthodox Europe | -1.2218 | -1.0043 |
| nan | Catholic Europe | 2.4095 | 0.8956 |
| nan | Latin America | -0.5193 | -1.3858 |
| nan | Orthodox Europe | -0.6759 | 0.1872 |
| nan | Latin America | 0.0143 | -0.3564 |
| nan | Orthodox Europe | -0.6076 | 1.0678 |
| nan | West & South Asia | -1.2867 | -1.4825 |
| nan | Orthodox Europe | -0.3382 | 0.5094 |
| nan | English-Speaking | 3.1377 | 0.9553 |
| nan | Latin America | 0.2226 | -0.1563 |
| nan | Confucian | -0.0043 | 0.6869 |
| nan | Confucian | -0.1525 | 1.3510 |
| nan | Latin America | 0.1297 | -1.9558 |
| nan | Catholic Europe | 0.4411 | 0.4405 |
| nan | Orthodox Europe | -0.2371 | -0.4285 |
| nan |  | -0.7196 | -0.1994 |
| nan | Catholic Europe | 1.4942 | 1.7678 |
| nan | Protestant Europe | 4.2813 | 1.8460 |
| nan | Latin America | -0.1858 | -2.0780 |
| nan | African-Islamic | -1.0522 | -1.2610 |
| nan | Protestant Europe | 0.2896 | 1.3189 |
| nan | Protestant Europe | 2.8995 | 1.3228 |
| nan | Catholic Europe | 2.6562 | 1.1930 |
| nan | Orthodox Europe | -1.4996 | -1.0976 |
| nan | African-Islamic | -1.6869 | -1.0360 |
| nan | Protestant Europe | 2.2903 | 1.7950 |
| nan | African-Islamic | -1.1858 | -2.3480 |
| nan | Orthodox Europe | -0.0171 | 0.2417 |
| nan | Latin America | 0.3323 | -1.0905 |
| nan | Latin America | 0.2835 | -0.7053 |
| nan | Confucian | 0.5673 | 1.7672 |
| nan | Catholic Europe | 0.1820 | 0.8360 |
| nan | Protestant Europe | 3.9785 | 1.1384 |
| nan | West & South Asia | -0.5777 | -0.8914 |
| nan | African-Islamic | -1.2364 | -1.3225 |
| nan | African-Islamic | -1.2547 | -0.9416 |
| nan | African-Islamic | -1.2467 | -0.7422 |
| nan | Catholic Europe | 1.4781 | -0.6801 |
| nan | Catholic Europe | 1.1003 | 0.5055 |
| nan | Confucian | 1.5875 | 2.0382 |
| nan | African-Islamic | -0.6790 | -0.5441 |
| nan | African-Islamic | -1.7794 | -1.9998 |
| nan | African-Islamic | -0.1617 | -0.9336 |
| nan | Confucian | 0.0245 | 1.3397 |
| nan | African-Islamic | 0.3378 | -1.1095 |
| nan | African-Islamic | -0.8787 | -1.5853 |
| nan | African-Islamic | -1.1551 | -0.5374 |
| nan | Catholic Europe | -0.0626 | 0.9881 |
| nan | African-Islamic | -1.3297 | -1.9898 |
| nan | Catholic Europe | -0.3201 | 1.0984 |
| nan | Catholic Europe | 2.2680 | 0.8774 |
| nan | Confucian | 0.8458 | 1.6738 |
| nan | West & South Asia | -0.5739 | -0.8427 |
| nan | African-Islamic | -0.8156 | -1.4853 |
| nan | African-Islamic | -0.1521 | -1.3862 |
| nan | Catholic Europe | -0.2147 | -1.4678 |
| nan | Latin America | 0.5796 | -1.5944 |
| nan | Confucian | 0.6373 | 1.2445 |
| nan | Orthodox Europe | -1.8581 | 0.5216 |
| nan | Orthodox Europe | -0.2533 | 0.0341 |
| nan | African-Islamic | -1.2974 | -0.9016 |
| nan | Protestant Europe | 3.3784 | 1.5541 |
| nan | English-Speaking | 3.3111 | 0.7641 |
| nan | Latin America | -0.5272 | -1.9531 |
| nan | African-Islamic | -1.1790 | -1.5972 |
| nan | Protestant Europe | 4.1852 | 1.7562 |
| nan | African-Islamic | -0.7685 | -1.5343 |
| nan | Latin America | -0.4193 | -0.9224 |
| nan | Latin America | -0.0514 | -1.7205 |
| nan | Catholic Europe | 0.1972 | -0.3490 |
| nan | Catholic Europe | -0.0465 | -0.2432 |
| nan | Latin America | 0.8707 | -1.5902 |
| nan | African-Islamic | -0.4501 | -2.6741 |
| nan | Orthodox Europe | -1.2734 | -0.2530 |
| nan | Orthodox Europe | -0.6920 | 0.4689 |
| nan | African-Islamic | -1.1755 | -1.6065 |
| nan | Orthodox Europe | -0.2436 | 0.5902 |
| nan | West & South Asia | 0.3365 | -0.0469 |
| nan | Catholic Europe | 0.4904 | 0.8544 |
| nan | West & South Asia | 0.5015 | -0.7033 |
| nan | Catholic Europe | 1.4739 | 1.0783 |
| nan | African-Islamic | 0.0345 | -0.8346 |
| nan | African-Islamic | -1.7190 | -1.3092 |
| nan | Catholic Europe | 1.6596 | 0.7773 |
| nan | Protestant Europe | 4.4311 | 2.2756 |
| nan | Protestant Europe | 3.2036 | 1.2257 |
| nan | African-Islamic | -0.2685 | -1.7976 |
| nan | West & South Asia | 0.1401 | -0.3689 |
| nan | Latin America | -0.5502 | -2.1330 |
| nan | African-Islamic | -1.8653 | -0.9187 |
| nan | African-Islamic | -1.1137 | -1.0790 |
| nan | Orthodox Europe | -0.8346 | 0.5129 |
| nan | Orthodox Europe | 0.0526 | 0.2223 |
| nan | African-Islamic | -1.4627 | -0.4924 |
| nan | English-Speaking | 3.1062 | 1.0912 |
| nan | English-Speaking | 2.0787 | 0.3202 |
| nan | African-Islamic | -0.8588 | -1.2262 |
| nan | Latin America | 1.4359 | -0.1281 |
| nan | African-Islamic | 0.0951 | -1.9554 |
| nan | Latin America | -0.2624 | -1.1704 |
| nan | African-Islamic | -1.3770 | -1.4155 |
| nan | African-Islamic | -0.9603 | -0.5082 |
| nan |  | 1.7081 | 0.0989 |
| nan |  | -0.7174 | -1.3369 |