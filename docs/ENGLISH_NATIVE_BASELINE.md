# 英语母语国家基准配置文档

## 概述

本文档说明如何使用英语母语国家作为英文文化距离的基准参考。

## 功能说明

### 目的

在多语言角色扮演实验中，为了更准确地评估不同国家用英文回答时的文化差异，我们添加了英语母语国家作为基准。这些国家的回答可以代表"真正的英文文化"，从而为其他国家用英文回答时的文化距离提供参考点。

### 配置的英语母语国家

根据`country_codes.json`中的"English-Speaking"文化区域，我们选择了以下5个英语母语国家：

1. **United States of America (the)** - 美国
   - 国家代码: USA (840)
   - 文化区域: English-Speaking
   - 特点: 多元化国家，重视个人自由、民主、创新和平等机会

2. **United Kingdom of Great Britain and Northern Ireland (the)** - 英国
   - 国家代码: GBR (826)
   - 文化区域: English-Speaking
   - 特点: 英语发源地，重视传统、君主立宪、议会民主和个人权利

3. **Australia** - 澳大利亚
   - 国家代码: AUS (36)
   - 文化区域: English-Speaking
   - 特点: 多元文化国家，重视平等主义、"公平竞争"、户外生活方式

4. **Canada** - 加拿大
   - 国家代码: CAN (124)
   - 文化区域: English-Speaking
   - 特点: 双语多元文化国家，重视多样性、包容性、礼貌、和平

5. **New Zealand** - 新西兰
   - 国家代码: NZL (554)
   - 文化区域: English-Speaking
   - 特点: 重视平等主义、环境保护、双文化（毛利和欧洲）、社会正义

## 配置文件更新

### 1. multilingual_questions_complete.json

添加了新的语言配置项 `"en-native"`:

```json
{
  "languages": {
    "en-native": {
      "name": "English (Native Speakers)",
      "countries": [
        "United States of America (the)",
        "United Kingdom of Great Britain and Northern Ireland (the)",
        "Australia",
        "Canada",
        "New Zealand"
      ],
      "questions": {
        // ... 10个IVS问题的英文版本
      }
    }
  }
}
```

同时更新了`language_country_mapping`，将这5个国家映射到`"en-native"`。

### 2. comprehensive_multilingual_config.json

在`comprehensive_test_config.languages`中添加了`"en-native"`配置，包含详细的国家信息：

```json
{
  "comprehensive_test_config": {
    "languages": {
      "en-native": {
        "countries": [
          {
            "name": "United States of America (the)",
            "code": "USA",
            "numeric": 840,
            "priority": 1,
            "reason": "英语母语国家，英文文化基准，English-Speaking区域代表",
            "cultural_region": "English-Speaking"
          },
          // ... 其他4个国家
        ]
      }
    }
  }
}
```

### 3. multilingual_roleplay_interview.py

#### 系统提示词

添加了`"en-native"`的系统提示词：

```python
self.system_prompts = {
    "en-native": """You are participating in a cultural values survey. 
    Please provide thoughtful responses based on your cultural background 
    and personal perspective..."""
}
```

#### 国家文化背景

在`_get_country_context`方法中添加了每个英语母语国家的文化背景描述：

```python
"en-native": {
    "United States of America (the)": "You are an ordinary citizen of the United States...",
    "United Kingdom of Great Britain and Northern Ireland (the)": "You are an ordinary citizen of the United Kingdom...",
    "Australia": "You are an ordinary citizen of Australia...",
    "Canada": "You are an ordinary citizen of Canada...",
    "New Zealand": "You are an ordinary citizen of New Zealand..."
}
```

## 使用方法

### 基本使用

```python
from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview

# 创建访谈实例
interviewer = MultilingualRoleplayInterview()

# 访谈英语母语国家
result = interviewer.interview_country_multilingual(
    model_name="openai/gpt-4o-mini",
    country="United States of America (the)",
    language="en-native"
)
```

### 批量运行实验

多语言实验会自动包含`en-native`配置的国家：

```python
# 运行完整的多语言实验
results = interviewer.run_multilingual_experiment(
    models=["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"],
    max_workers=4
)
```

## 数据分析应用

### 1. 文化距离计算

可以计算其他国家（用英文回答）与英语母语国家之间的文化距离：

```python
# 示例：计算中国用英文回答与美国的文化距离
china_en_responses = get_responses(country="China", language="en")
usa_native_responses = get_responses(country="United States of America (the)", language="en-native")

distance = calculate_cultural_distance(china_en_responses, usa_native_responses)
```

### 2. 基准参考

在多语言悖论分析中，可以使用英语母语国家作为基准：

- 对比"中国用中文"vs"中国用英文"vs"美国用英文"
- 分析语言切换带来的文化距离变化
- 评估"英文回答"是否真的接近"英文文化"

### 3. 可视化分析

在PCA或其他降维分析中，可以将英语母语国家标记为特殊点：

```python
# 标记英语母语国家
english_native_countries = [
    "United States of America (the)",
    "United Kingdom of Great Britain and Northern Ireland (the)",
    "Australia",
    "Canada",
    "New Zealand"
]

# 在可视化中用不同颜色/形状标记
```

## 实验任务计算

添加英语母语国家后的任务规模：

### 原有配置
- 原生语言: 4种（zh-cn, ru, es, ar）
- 原生语言国家: 27个
- 英文对比: 27个国家用英文回答

### 新增配置
- **英语母语国家**: 5个
- **总国家-语言组合**: 54 + 5 = **59个**

### 完整实验规模（假设使用7个模型）
- 总任务数: 59 × 7 = **413个访谈任务**
- 每个任务10个问题
- 如果repeat_count=5: 413 × 10 × 5 = **20,650次API调用**

## 验证测试

运行测试脚本验证配置：

```bash
python3 test_native_english_config.py
```

测试内容包括：
1. ✅ multilingual_questions_complete.json配置
2. ✅ comprehensive_multilingual_config.json配置
3. ✅ MultilingualRoleplayInterview模块加载

## 注意事项

1. **语言标识**: 使用`"en-native"`而不是`"en"`来区分英语母语国家和其他国家用英文回答

2. **国家名称**: 使用完整的官方名称（如"United States of America (the)"），与`country_codes.json`保持一致

3. **文化区域**: 所有5个国家的文化区域都应为`"English-Speaking"`

4. **对比分析**: 在分析时注意区分：
   - `en-native`: 英语母语国家用英文回答（真实的英文文化）
   - `en`: 其他国家用英文回答（可能受母语文化影响）

## 未来扩展

可以考虑添加其他英语国家（如爱尔兰、南非等），但需要注意：
- 爱尔兰：主要为英语母语国家
- 南非：英语是官方语言之一，但多语言环境复杂
- 新加坡：英语是官方语言，但已包含在zh-cn的国家列表中

## 相关文档

- [多语言角色扮演系统README](MULTILINGUAL_ROLEPLAY_README.md)
- [快速开始指南](QUICK_START.md)
- [角色扮演系统文档](ROLEPLAY_SYSTEM_README.md)

---

**创建时间**: 2025-01-20  
**最后更新**: 2025-01-20  
**版本**: 1.0















