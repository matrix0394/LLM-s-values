# 配置目录

## 目录结构

```
config/
├── country/                 # 国家映射配置
│   ├── country_codes.json        # ISO国家代码
│   ├── country_codes.pkl
│   ├── country_name_mapping.json # 国家名称映射
│   └── cultural_regions.json     # 文化区域划分
│
├── questions/              # 访谈问题配置
│   ├── ivs_questions.json          # IVS问题列表
│   ├── multilingual/              # 多语言问题
│   │   ├── complete.json         # 完整版
│   │   └── json/                # 各语言版本
│   │       ├── questions_ar.json
│   │       ├── questions_de.json
│   │       ├── questions_es.json
│   │       ├── questions_fr.json
│   │       └── questions_it.json
│   │
│   └── translation_templates/    # 翻译模板
│       ├── questions_zh-hk_TEMPLATE.json
│       └── questions_zh-tw_TEMPLATE.json
│
└── models/                 # 模型配置
    ├── llm_models.json            # LLM模型列表
    └── MODEL_CONFIG_README.md    # 模型配置说明
```

## 文件说明

### country/
国家代码和文化区域映射，用于将国家名称统一化。

### questions/
IVS访谈问题的配置，包括：
- 原始IVS问题列表
- 各语言的翻译版本
- 翻译模板

### models/
LLM模型配置，包括模型名称、API参数等。
