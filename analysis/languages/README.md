# WVS 语言覆盖分析

分析 13 种实验语言对 WVS 109 个国家的覆盖情况。

## 核心统计

| 指标 | 数值 |
|------|------|
| WVS 总国家数 | 109 |
| 已覆盖国家 | 66 (60.6%) |
| 已覆盖人口 | 43.9 亿 (62.0%) |

## 文件说明

| 文件 | 用途 |
|------|------|
| `map_languages_to_countries_final.py` | 核心数据：13 种语言到 109 国的映射 |
| `add_population_to_report.py` | 生成完整报告（JSON + Excel） |
| `update_excel_data_only.py` | 更新 Excel 数据，保留格式 |
| `language_expansion_analysis.py` | 语言扩展策略分析 |

## 使用方法

```bash
# 生成完整报告
python analysis/languages/add_population_to_report.py

# 更新 Excel 数据
python analysis/languages/update_excel_data_only.py

# 分析语言扩展策略
python analysis/languages/language_expansion_analysis.py
```

## 输出文件

- `results/analysis/language/语言覆盖汇报数据.json`
- `results/analysis/language/语言覆盖统计.xlsx`

## 13 种实验语言

英语、西班牙语、阿拉伯语、俄语、葡萄牙语、日语、韩语、法语、德语、意大利语、简体中文、繁体中文(香港)、繁体中文(台湾)
