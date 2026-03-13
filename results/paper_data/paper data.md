# Paper Data 

## Figure 1：文化价值观世界地图

**数据文件**：`figure1_data_66countries.csv`

这个文件有 66 个国家/地区，每行一个国家。需要画 4 张地图拼在一起：

| 位置 | 内容 | 用哪列 |
|------|------|--------|
| 左上 | LLM 英语角色扮演 PC1 热力图 | `LLM_EN_PC1` |
| 左下 | LLM 英语角色扮演 PC2 热力图 | `LLM_EN_PC2` |
| 右上 | WVS 真实 PC1 热力图（对照） | `WVS_PC1` |
| 右下 | WVS 真实 PC2 热力图（对照） | `WVS_PC2` |

**列说明**：

| 列名 | 含义 |
|------|------|
| `country` | 国家名（英文） |
| `LLM_EN_PC1` | 20个模型用英语角色扮演该国时的 PC1 均值 |
| `LLM_EN_PC2` | 同上，PC2 均值 |
| `WVS_PC1` | WVS 真实调查的 PC1 坐标 |
| `WVS_PC2` | WVS 真实调查的 PC2 坐标 |
| `cultural_region` | 文化区域（Inglehart-Welzel 分类） |
| `is_islamic` | 是否伊斯兰文化圈（1=是，0=否） |

---

## Figure 2：LLM 内在价值观（6种语言 × 20模型）

**数据文件**：`figure2_baseline_20models.csv`（详细数据）、`figure2_language_summary.csv`（语言均值汇总）

这个图展示 20 个模型在没有角色扮演时（baseline），用 6 种语言回答 WVS 问题得到的 PCA 坐标。

![image-20260313162047884](/Users/yxy/Library/Application Support/typora-user-images/image-20260313162047884.png)

阿拉伯语的均值明显偏左下（更传统/生存），说明语言本身会影响 LLM 的价值观表达。

---

## Figure 3：数字东方主义

**数据文件**：`figure3_digital_orientalism.csv`

包含 18 个国家/地区的 distance 数据：12 个中东国家 + 6 个东亚（儒家）国家。

| 列名 | 含义 |
|------|------|
| `country` | 国家名 |
| `cultural_region` | Middle East 或 Confucian |
| `native_language` | 该国官方语言代码（ar / zh-cn / zh-hk / ja / ko / pt） |
| `native_distance_mean` | 用官方语言角色扮演时，LLM 坐标到 WVS 真实坐标的欧氏距离（20模型均值） |
| `en_distance_mean` | 用英语角色扮演时的距离（20模型均值） |
| `advantage_mean` | 英语优势 = (d_native - d_english) / d_native × 100% |
| `n_models` | 模型数量（都是20） |

---

## Figure 4：殖民历史

**数据文件**：`figure4_colonial_history.csv`

包含 27 个国家/地区，按殖民历史分组：

| 区域 | 国家数 | 殖民者 | 说明 |
|------|--------|--------|------|
| Sub-Saharan Africa (British) | 6 | UK | Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia |
| Sub-Saharan Africa (French) | 2 | FR | Mali, Burkina Faso |
| Latin America (Spanish) | 11 | ES | Argentina, Bolivia, Chile, Colombia, Ecuador, Guatemala, Mexico, Nicaragua, Peru, Uruguay, Venezuela |
| Latin America (Portuguese) | 1 | PT | Brazil |
| Latin America (French) | 1 | FR | Haiti |
| Confucian | 6 | 混合 | China, Japan, Korea, Taiwan, Hong Kong, Macao |

**列说明**（和 Figure 3 类似，多了几列）：

| 列名 | 含义 |
|------|------|
| `colonial_power` | 殖民宗主国代码（UK / FR / ES / PT / JP / None） |
| `is_en_native` | 是否英语母语国家（True/False） |

**特别注意**：

- 英国殖民的非洲 6 国（Kenya 等）是英语母语国家，所以 `native_distance_mean == en_distance_mean`，`advantage_mean = 0`。因为它们的官方语言就是英语，没有"英语优势"。
- 澳门的官方语言写的是 `pt`（葡萄牙语），因为这部分讨论的是殖民历史语境下的语言影响。

论文里非洲部分用了**两种不同的指标**，不是统一用英语优势：

| 子区域 | 国家数 | 论文用的指标 | 原因 |
|--------|--------|-------------|------|
| 英国殖民地（6国） | Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia | **PC2 偏差**（LLM_EN_PC2 - WVS_PC2） | 母语就是英语，没有 EA 可算 |
| 法国殖民地（2国） | Mali, Burkina Faso | **英语优势 %** | 母语是法语，可以算 EA |

英国殖民地 6 国的 PC2 偏差数据（正值=LLM 更世俗）：

| 国家 | PC2 偏差 | 含义 |
|------|---------|------|
| South Africa | +1.71 | LLM 大幅世俗化 |
| Zimbabwe | +0.83 | LLM 世俗化 |
| Ghana | +0.75 | LLM 世俗化 |
| Nigeria | +0.56 | LLM 世俗化 |
| Kenya | -0.29 | 略偏传统 |
| Zambia | -0.62 | 偏传统 |

这些数据可以从 `figure1_data_66countries.csv` 算出来：`PC2_bias = LLM_EN_PC2 - WVS_PC2`。

非洲的数据如果只按英语优势画图，只有两个国家，Mali, Burkina Faso。

1. **方案1**：非洲 8 国全画，但用 `en_distance_mean`（英语距离）作为统一填色指标，而不是英语优势。这个指标对所有国家都有意义（不管母语是不是英语），表示"LLM 用英语模仿这个国家时离真实文化有多远"。distance 越大颜色越深 = LLM 越不准。
3. **方案 2**：只画法国殖民地 2 国 + 拉丁美洲 13 国 + 儒家 6 国（都有 EA），非洲英国殖民地单独做一个小的图展示 PC2 偏差。

---

## Regression Data：回归分析数据

**数据文件**：`regression_data.csv`

这是做回归分析用的完整数据，每行是一个 (模型, 国家) 组合，共 1040 行（20 模型 × ~46 非英语国家，个别国家有多种母语所以略多）。

### 因变量（三选一）

文件里提供了三种英语优势的计算方式：

| 列名 | 公式 | 范围 | 特点 |
|------|------|------|------|
| `english_advantage_pct` | (d_native - d_en) / d_native × 100% | [-4580%, 94%] | 原始百分比，有极端值（分母接近0时） |
| `ea_winsorized` | 同上，但截断到 [-200%, 200%] | [-200%, 200%] | 去掉了最极端的值，但分布仍然偏斜 |
| `log_ratio` | log(d_en / d_native) | [-2.76, 3.85] | 对数比，分布接近对称 |

论文中用的是(d_native - d_en) / d_native × 100%，对于多个国家，或者多个模型，极端值会因为平均不显现，但是对于单个国家单个模型的英语优势数据，如果官方语言的模仿效果很好，这样计算的英语优势会很极端。

### 自变量

| 列名 | 含义 | 示例 |
|------|------|------|
| `d_english` | 英语角色扮演的欧氏距离 | 1.018 |
| `d_native` | 母语角色扮演的欧氏距离 | 0.957 |
| `cultural_region` | 文化区域 | African-Islamic |
| `is_islamic` | 是否伊斯兰文化圈 | True/False |
| `language_family` | 语系 | Semitic, Romance, ... |
| `model_origin` | 模型来源国 | US, China |
| `internet_collectivity_index` | 互联网包容性指数（EIU Inclusive Internet Index OVERALL，0-100） | 32.59 |
| `colonial_power` | 殖民宗主国代码 | FR, UK, ES, ... |
| `gdp_per_capita` | 人均 GDP | 4960.3 |
| `HDI` | 人类发展指数 | 0.763 |
| `has_colonial_history` | 是否有殖民历史（二值变量） | 0/1 |
| `freedom_on_net` | 网络自由度评分（Freedom House） | 部分国家有缺失值 |

### 缺失数据说明

regression_data.csv 里有些自变量存在缺失值，下面列出来了。

**`internet_collectivity_index`（互联网包容性指数）— 缺 7 个国家**

| 缺失国家 | 原因 |
|----------|------|
| Belarus, Iraq, Libya, Yemen | 不在 EIU Inclusive Internet Index 的 120 国覆盖范围内 |
| Haiti, Palestine | 同上 |
| Macao | 作为特别行政区未单独评估 |

- 数据来源：Economist Impact "Inclusive Internet Index" Edition 5 (2021)，覆盖 120 个国家
- 原始数据在 `archive/Internet_Inclusivity_Index_ Score_(DEFAULT_weight_profile).csv`
- 用的是 `OVERALL` 总分（0-100），值越高表示互联网越包容
- **影响**：7 个缺失国家占 46 国的 15%，其中 5 个是中东/非洲小国。

**`freedom_on_net`（网络自由度）— 缺 20 个国家**

| 缺失类型 | 国家 |
|----------|------|
| 西欧小国（Freedom House 未评估） | Austria, Belgium, Luxembourg, Portugal, Spain, Switzerland |
| 拉美/非洲（未评估） | Bolivia, Burkina Faso, Guatemala, Haiti, Mali, Peru, Uruguay |
| 中东（未评估） | Algeria, Kuwait, Qatar, Yemen |
| 特别行政区/地区 | Hong Kong, Macao, Palestine |

- 数据来源：Freedom House "Freedom on the Net" 报告，只覆盖约 72 个国家
- **影响**：缺失率高达 43%（20/46），不建议作为主要回归变量。如果一定要用，样本量会从 1040 降到约 570 行

**`colonial_power`（殖民历史）— 缺 10 个国家**

缺失的都是**欧洲国家和日本**（Austria, Belgium, France, Germany, Italy, Japan, Luxembourg, Portugal, Spain, Switzerland），它们本身就是殖民者而不是被殖民者，所以 `colonial_power` 为空。`has_colonial_history = 0` 已经标记了这些国家。

**完全无缺失的变量**：`d_english`, `d_native`, `english_advantage_pct`, `ea_winsorized`, `log_ratio`, `cultural_region`, `is_islamic`, `language_family`, `model_origin`, `gdp_per_capita`, `HDI`, `has_colonial_history`



## 关键参数

- 模型数：20（排除了 qwen3-1.7b, glm-4.6, qwq-32b 这三个数据不全的模型）
- 国家/地区总数：66（20 英语母语 + 46 非英语）
- 回归数据只包含 46 个非英语国家（英语母语国家没有"英语优势"这个概念）
