# WVS/Inglehart 文化地图国家说明

## 概述

本文档说明 WVS (World Values Survey) 文化地图中的国家数量差异。

## WVS 文化地图原始国家 (109个)

WVS/Inglehart 文化地图在 [config/country/cultural_regions_checked](cultural_regions_checked) 中定义，包含 **109个国家** (不含表头行)。

这些国家按文化区域分类如下：

| 文化区域 | 数量 | 国家列表 |
|----------|------|----------|
| Protestant Europe | 9 | Sweden, Denmark, Norway, Finland, Netherlands, Switzerland, Germany, Iceland, Estonia |
| English-Speaking | 5 | United States, Great Britain, Canada, Australia, New Zealand |
| Catholic Europe | 16 | France, Belgium, Luxembourg, Spain, Portugal, Andorra, Italy, Austria, Slovenia, Slovakia, Hungary, Poland, Lithuania, Latvia, Czech Republic, Croatia |
| Orthodox Europe | 13 | Russia, Ukraine, Belarus, Bulgaria, Serbia, North Macedonia, Greece, Romania, Moldova, Armenia, Georgia, Bosnia, Montenegro, Cyprus |
| Confucian | 7 | China, Japan, South Korea, Taiwan, Hong Kong SAR, Macao SAR, Mongolia |
| West & South Asia | 7 | India, Thailand, Singapore, Israel, Myanmar, Malaysia, Vietnam |
| Latin America | 15 | Mexico, Guatemala, Haiti, Puerto Rico, Colombia, Ecuador, Peru, Bolivia, Brazil, Argentina, Chile, Uruguay, Venezuela, Nicaragua, Trinidad, Philippines |
| African-Islamic | 37 | South Africa, Iran, Turkey, Albania, Burkina Faso, Egypt, Morocco, Algeria, Tunisia, Libya, Jordan, Iraq, Palestine, Lebanon, Yemen, Qatar, Saudi Arabia, Pakistan, Bangladesh, Maldives, Azerbaijan, Kazakhstan, Kyrgyzstan, Uzbekistan, Tajikistan, Indonesia, Nigeria, Ghana, Tanzania, Ethiopia, Uganda, Rwanda, Zimbabwe, Mali, Kenya |

## 我们计算的有效国家 (112个)

根据 IVS 数据和 PCA 分析，我们计算出 **112个有效国家**的国家级 PCA 分数。

数据来源: [config/country/country_codes.pkl](../config/country/country_codes.pkl)

### 112个国家列表

```
African-Islamic (34): Albania, Algeria, Azerbaijan, Bangladesh, Burkina Faso, Egypt, Ethiopia, Ghana, Indonesia, Iran, Iraq, Jordan, Kazakhstan, Kenya, Kuwait, Kyrgyzstan, Lebanon, Libya, Malaysia, Maldives, Mali, Morocco, Nigeria, Pakistan, Palestine, Qatar, Saudi Arabia, Tajikistan, Tanzania, Tunisia, Turkey, Uganda, Uzbekistan, Zambia, Zimbabwe

Catholic Europe (18): Andorra, Austria, Belgium, Croatia, Czechia, France, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Poland, Portugal, Slovakia, Slovenia, Spain

Latin America (16): Argentina, Bolivia, Brazil, Chile, Colombia, Ecuador, Guatemala, Haiti, Mexico, Nicaragua, Peru, Philippines, Puerto Rico, Trinidad and Tobago, Uruguay, Venezuela

Orthodox Europe (14): Armenia, Belarus, Bosnia and Herzegovina, Bulgaria, Cyprus, Georgia, Greece, Moldova, Montenegro, North Macedonia, Romania, Russia, Serbia, Ukraine

Protestant Europe (9): Denmark, Estonia, Finland, Germany, Iceland, Netherlands, Norway, Sweden, Switzerland

Confucian (7): China, Hong Kong, Japan, Korea (Republic of), Macao, Mongolia, Taiwan

West & South Asia (6): India, Israel, Myanmar, Singapore, Thailand, Viet Nam

English-Speaking (5): Australia, Canada, New Zealand, United Kingdom, United States
```

## 差异说明

我们计算的 112 个国家比 WVS 原始的 109 个国家多出 **3个国家**：

| 代码 | 国家 | 文化区域 | 说明 |
|------|------|----------|------|
| 372 | Ireland | Catholic Europe | 新增 - 原 WVS 未包含但 IVS 有数据 |
| 414 | Kuwait | African-Islamic | 新增 - 原 WVS 未包含但 IVS 有数据 |
| 470 | Malta | Catholic Europe | 新增 - 原 WVS 未包含但 IVS 有数据 |

这 3 个国家在 IVS (Integrated Values Studies) 数据集中有有效的调查数据，因此被纳入 PCA 分析。

## 注意事项

1. **PCA 分数一致性**: 我们的 PCA 计算结果与参考项目 `model_cultural_comp-main` 完全一致，112 个国家的 PC1 和 PC2 分数相同。

2. **文化区域定义**: 我们的文化区域定义参考了 `cultural_regions.json` 配置文件，与 WVS 原始分类略有不同（如增加了 Kuwait, Zambia 等）。

3. **补充国家代码**: 197, 909, 915 现已补回到国家代码映射中，分别对应 Northern Cyprus、Northern Ireland 和 Kosovo，因此 112 个 IVS 实体现在都能在导出坐标表中显示国家名称。

## 文件位置

- WVS 原始国家代码检查: `config/country/cultural_regions_checked`
- 有效 112 国数据: `data/country_values/country_scores_pca.pkl` / `.json`
- 完整 IVS PCA 结果: `data/country_values/valid_data.pkl` / `.json`
- 文化区域配置: `config/country/cultural_regions.json`
- 国家代码映射: `config/country/country_codes.pkl` / `.json`
