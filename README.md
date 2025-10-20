# 🌍 大语言模型跨语言文化价值观研究

## 📖 项目概述

本项目是一个基于世界价值观调查（World Values Survey, WVS）数据的大语言模型跨语言文化价值观研究平台。项目通过让LLM用不同语言模仿不同国家的文化背景回答价值观问题，系统性地研究**语言对LLM文化价值表达的影响**。

### 🎯 核心研究问题

**语言是否影响大语言模型对文化价值观的表达？**

通过严格的控制变量实验，让LLM用英语和母语分别模仿同一国家文化，对比其文化价值表达的准确性差异。

### 🔬 研究规模

- **7个主流模型**：GPT-4o-mini, Claude-3.7-Sonnet, Gemini-2.0-Flash, Llama-3.3-70B, Mistral-nemo, DeepSeek-v3, Qwen-QwQ
- **26个重点国家** + 112个参考国家
- **5种语言**：英语、中文、俄语、西班牙语、阿拉伯语
- **371个LLM实体** + 112个真实国家基准
- **18,500+次API调用**

## 🎨 核心发现：英语悖论

### 主要发现

通过大规模实证研究，我们发现了一个**反直觉的现象**：

- **65%的国家**（17/26）：用英语提问比母语更准确
- **平均英语优势**：8.22%
- **最显著案例**：
  - 🇷🇺 俄罗斯：英语准确度高出 **48%**
  - 🇲🇦 摩洛哥：英语准确度高出 **39%**
  - 🇨🇳 中国：英语准确度高出 **36%**

### 反例：拉美例外

拉美国家展现出完全相反的模式：
- 🇨🇱 智利：母语（西班牙语）准确度高出 **32%**
- 🇪🇨 厄瓜多尔：母语准确度高出 **27%**

### 模型差异

- **Mistral-nemo**：英语优势最强（20%）
- **Claude-3.7**：英语优势15%
- **Gemini-2.0**：唯一倾向母语的模型（1.8%）

### 研究意义

这个"英语悖论"现象：
1. 挑战了"母语总是更好"的常见假设
2. 揭示了LLM的英语中心主义和训练数据偏见
3. 为全球AI部署和多语言系统设计提供了重要指导

## 🏗️ 项目结构

### 核心模块

```
LLM's values/
├── src/                          # 核心代码模块
│   ├── base/                     # 基础框架 ⭐
│   │   ├── base_interview.py            # 统一访谈基类
│   │   ├── base_pca_analyzer.py         # 统一PCA分析基类
│   │   ├── base_cultural_map_visualizer.py  # 统一可视化基类
│   │   └── ivs_question_processor.py    # IVS问题处理器
│   │
│   ├── country_values/           # 真实国家数据处理
│   │   ├── data_processing.py          # WVS数据处理
│   │   ├── pca_analysis.py             # 国家PCA分析
│   │   └── visualization.py            # 文化地图绘制
│   │
│   ├── llm_values/              # LLM直接回答
│   │   ├── llm_interview.py            # LLM价值观访谈
│   │   ├── llm_pca_analysis.py         # LLM文化坐标分析
│   │   └── llm_visualization.py        # LLM文化地图
│   │
│   ├── roleplay_English/        # 英语角色扮演
│   │   ├── llm_country_roleplay_interview.py      # 英语角色扮演访谈
│   │   ├── llm_country_roleplay_pca_analysis.py   # 角色扮演PCA分析
│   │   └── llm_country_roleplay_visualization.py  # 角色扮演可视化
│   │
│   ├── roleplay_multilingual/   # 多语言对比实验 ⭐⭐⭐
│   │   ├── multilingual_roleplay_interview.py     # 多语言访谈
│   │   ├── multilingual_roleplay_pca_analysis.py  # 多语言PCA分析
│   │   ├── multilingual_roleplay_visualization.py # 多语言可视化
│   │   ├── controlled_multilingual_experiment.py  # 控制变量实验框架
│   │   └── comprehensive_multilingual_test.py     # 综合多语言测试
│   │
│   ├── run/                     # 统一运行入口
│   │   ├── run_country_values_analysis.py          # 运行国家分析
│   │   ├── run_llm_values_analysis.py              # 运行LLM分析
│   │   ├── run_roleplay_english_analysis.py        # 运行英语角色扮演
│   │   └── run_roleplay_multilingual_analysis.py   # 运行多语言分析
│   │
│   └── utils/                   # 工具函数
│
├── scripts/                     # 辅助脚本
│   ├── analysis/                # 数据分析脚本 ⭐
│   │   ├── comprehensive_multilingual_analysis.py   # 综合多语言分析
│   │   ├── quality_filtered_multilingual_analysis.py # 质量过滤分析
│   │   ├── deep_multilingual_analysis.py            # 深度多语言分析
│   │   └── model_response_quality_analysis.py       # 模型响应质量分析
│   │
│   ├── runners/                 # 运行脚本
│   │   ├── run_extended_multilingual_experiment.py  # 扩展多语言实验
│   │   ├── start_roleplay_system.py                 # 启动角色扮演系统
│   │   └── concurrent_roleplay_interview.py         # 并发角色扮演访谈
│   │
│   ├── maintenance/             # 维护脚本
│   │   ├── fix_numpy_compatibility.py               # 修复NumPy兼容性
│   │   └── regenerate_numpy_files.py                # 重新生成NumPy文件
│   │
│   ├── experiments/             # 实验脚本
│   │   ├── merge_mistral_models.py                  # 合并Mistral模型数据
│   │   └── process_merged_data.py                   # 处理合并数据
│   │
│   └── archive/                 # 归档脚本
│
├── config/                      # 配置文件
│   ├── ivs_questions.json                    # IVS问题配置
│   ├── llm_models.json                       # 模型API配置
│   ├── cultural_regions.json                 # 文化区域配置
│   ├── country_codes.json                    # 国家代码映射
│   ├── multilingual_questions_complete.json  # 完整多语言问题集
│   └── multilingual_questions/               # 多语言问题文档
│       ├── question - 简中.pdf
│       ├── question - 俄语.pdf
│       ├── question - 拉美西语.pdf
│       └── question - 阿语.pdf
│
├── data/                        # 数据文件
│   ├── raw/                     # 原始WVS数据（.sps文件）
│   ├── country_values/          # 真实国家数据
│   │   ├── ivs_df.pkl                       # WVS原始数据
│   │   ├── country_codes.pkl                # 国家代码
│   │   ├── valid_data.pkl                   # 清洗后数据
│   │   └── pca_results.pkl                  # PCA结果
│   │
│   ├── llm_values/              # LLM直接回答数据
│   │   └── [25个.pkl文件 + 12个.json文件]
│   │
│   ├── roleplay_English/        # 英语角色扮演数据
│   │   └── [1025个.pkl文件 + 779个.json文件]
│   │
│   ├── roleplay_multilingual/   # 多语言角色扮演数据 ⭐
│   │   └── [6个.pkl文件 + 6个.json文件]
│   │
│   └── backup/                  # 备份文件
│
├── results/                     # 分析结果输出
│   ├── country_values/          # 真实国家分析结果
│   │   └── [3个.png图表 + 1个.json + 1个.txt]
│   │
│   ├── llm_values/              # LLM分析结果
│   │   └── [14个.png图表 + 3个.md报告 + 1个.json]
│   │
│   ├── roleplay_English/        # 英语角色扮演结果
│   │   └── [40个.html + 27个.png + 6个.json + 6个.csv]
│   │
│   ├── roleplay_multilingual/   # 多语言对比结果 ⭐⭐⭐
│   │   └── [23个.png + 15个.html + 12个.json + 4个.csv]
│   │
│   └── deep_analysis/           # 深度分析结果
│       └── [3个.csv + 3个.png + 1个.md]
│
├── docs/                        # 项目文档
│   ├── README.md                           # 文档索引
│   ├── QUICK_START.md                      # 快速开始指南
│   ├── ROLEPLAY_SYSTEM_README.md           # 角色扮演系统文档
│   ├── MULTILINGUAL_ROLEPLAY_README.md     # 多语言系统文档
│   ├── roleplay_analysis_report.md         # 角色扮演分析报告
│   └── ai_pca_analysis_report.md           # AI PCA分析报告
│
├── logs/                        # 日志文件
│
└── references/                  # 参考资料
    ├── Generation_and_Preprocessing_Pipeline.py
    ├── Prompts_Questions.csv
    └── Prompts_Respondent_Descriptors_Cultural_Prompted.csv
```

## 🚀 快速开始

### 环境配置

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 主要依赖包括：
# - pandas, numpy, scipy (数据处理)
# - scikit-learn, factor-analyzer (统计分析)
# - matplotlib, seaborn, plotly (可视化)
# - openai, anthropics (API调用)
# - jupyter, ipykernel (Jupyter支持)
```

### API配置

在 `config/llm_models.json` 中配置你的API密钥：

```json
{
  "models": {
    "openai/gpt-4o-mini": {
      "api_key": "YOUR_OPENROUTER_API_KEY",
      "base_url": "https://openrouter.ai/api/v1",
      "region": "US"
    },
    ...
  }
}
```

### 运行实验

#### 1. 多语言对比实验（核心功能）⭐

```bash
# 运行综合多语言分析
python scripts/analysis/comprehensive_multilingual_analysis.py

# 运行质量过滤的多语言分析
python scripts/analysis/quality_filtered_multilingual_analysis.py

# 运行深度多语言分析（英语悖论研究）
python scripts/analysis/deep_multilingual_analysis.py
```

#### 2. 统一分析流程

```bash
# 运行国家真实数据分析
python src/run/run_country_values_analysis.py

# 运行LLM直接回答分析
python src/run/run_llm_values_analysis.py

# 运行英语角色扮演分析
python src/run/run_roleplay_english_analysis.py

# 运行多语言角色扮演分析
python src/run/run_roleplay_multilingual_analysis.py
```

#### 3. 新数据收集

```bash
# 启动角色扮演系统（英语）
python scripts/runners/start_roleplay_system.py

# 运行扩展多语言实验
python scripts/runners/run_extended_multilingual_experiment.py

# 并发角色扮演访谈
python scripts/runners/concurrent_roleplay_interview.py
```

## 📊 数据说明

### IVS核心问题（10个）

项目基于以下10个WVS核心问题构建文化价值观维度：

**传统 vs 世俗理性价值观：**
- A008: 宗教的重要性
- A165: 对权威的尊重
- C001: 工作的重要性
- C002: 家庭的重要性
- E018: 对政府的信任

**生存 vs 自我表达价值观：**
- E025: 对他人的信任
- F063: 收入平等观念
- F118: 性别平等观念
- F120: 同性恋接受度
- G006: 生活满意度

**后物质主义指数：**
- Y002: 四项选择题（物质主义/后物质主义）
- Y003: 五项选择题（价值观优先级）

### 文化区域分类

项目涵盖以下主要文化区域：

1. **English-Speaking** (英语国家)：美国、英国、澳大利亚、加拿大等
2. **Protestant Europe** (新教欧洲)：德国、荷兰、瑞典等
3. **Catholic Europe** (天主教欧洲)：法国、意大利、西班牙等
4. **Orthodox Europe** (东正教欧洲)：俄罗斯、希腊、罗马尼亚等
5. **Confucian** (儒家文化圈)：中国、日本、韩国、台湾等
6. **Latin America** (拉丁美洲)：墨西哥、巴西、阿根廷、智利等
7. **African-Islamic** (非洲-伊斯兰)：埃及、摩洛哥、尼日利亚等
8. **South & West Asia** (南亚西亚)：印度、土耳其、伊朗等

### 支持的语言

- **英语 (en)**: 基准语言，所有国家
- **中文 (zh-cn)**: 中国、台湾、香港、澳门
- **俄语 (ru)**: 俄罗斯、白俄罗斯、哈萨克斯坦、乌克兰、吉尔吉斯斯坦
- **西班牙语 (es)**: 西班牙、墨西哥、阿根廷、哥伦比亚、秘鲁、智利等
- **阿拉伯语 (ar)**: 埃及、沙特阿拉伯、伊拉克、阿尔及利亚、摩洛哥

## 🔬 研究方法

### 实验设计

**控制变量法**：
- **唯一变量**：语言（英语 vs 母语）
- **固定条件**：
  - 相同的目标国家
  - 相同的测试模型
  - 相同的问题集合
  - 相同的模型参数（temperature=0.1）
  - 相同的PCA分析方法
  - 相同的评估标准

### 分析流程

```
1. 数据收集
   └─> LLM角色扮演访谈（英语 + 母语）
   
2. 数据处理
   └─> IVSQuestionProcessor（统一处理逻辑）
   
3. PCA分析
   └─> BasePCAAnalyzer（主成分分析 + Varimax旋转）
   
4. 文化坐标计算
   └─> 映射到Inglehart-Welzel文化地图
   
5. 对比分析
   └─> 计算英语 vs 母语的距离差异
   
6. 结果可视化
   └─> 生成对比图表和分析报告
```

### 评估指标

- **绝对距离**：LLM实体与真实国家的欧氏距离
- **语言效应**：母语距离 - 英语距离
- **改善百分比**：(母语距离 - 英语距离) / 母语距离 × 100%
- **跨语言一致性**：同一国家在不同语言下的响应相似度

## 📈 主要结果

### 英语悖论统计

- **65%国家**（17/26）：英语表现更好
- **35%国家**（9/26）：母语表现更好
- **平均英语优势**：8.22%

### 最显著案例

**英语优势最大：**
1. 🇷🇺 俄罗斯：48%（距离 1.93 → 1.00）
2. 🇲🇦 摩洛哥：39%（距离 2.96 → 1.82）
3. 🇨🇳 中国：36%（距离 1.58 → 1.00）
4. 🇪🇬 埃及：31%（距离 2.15 → 1.48）
5. 🇮🇶 伊拉克：29%（距离 2.84 → 2.02）

**母语优势案例（拉美例外）：**
1. 🇨🇱 智利：32%（距离 1.77 → 2.33）
2. 🇪🇨 厄瓜多尔：27%（距离 2.22 → 2.84）
3. 🇵🇪 秘鲁：18%（距离 2.41 → 2.84）

### 模型性能对比

| 模型 | 平均英语距离 | 平均母语距离 | 英语优势 |
|------|--------------|--------------|----------|
| Mistral-nemo | 1.82 | 2.28 | **20.2%** |
| Claude-3.7 | 1.91 | 2.21 | **13.6%** |
| GPT-4o-mini | 1.94 | 2.15 | **9.8%** |
| Llama-3.3 | 2.01 | 2.18 | **7.8%** |
| DeepSeek-v3 | 2.05 | 2.22 | **7.7%** |
| Qwen-QwQ | 2.08 | 2.24 | **7.1%** |
| Gemini-2.0 | 2.12 | 2.08 | **-1.8%** ✱ |

✱ 唯一倾向母语的模型

### 文化区域差异

| 文化区域 | 国家数 | 平均英语优势 | 模式 |
|---------|--------|--------------|------|
| 东正教欧洲 | 5 | +32.4% | 强英语优势 |
| 非洲-伊斯兰 | 4 | +28.7% | 强英语优势 |
| 儒家文化圈 | 6 | +22.3% | 强英语优势 |
| 南亚西亚 | 3 | +14.5% | 中等英语优势 |
| 拉丁美洲 | 8 | **-15.2%** | **母语优势** ⭐ |

## 📝 分析报告

项目生成的主要分析报告位于 `results/` 目录：

### 多语言对比分析

- `results/roleplay_multilingual/` - 完整的多语言对比结果
  - 语言效应散点图
  - 模型性能对比图
  - 国家×模型热力图
  - 文化区域分析图
  - 跨语言一致性分析

### 深度分析

- `results/deep_analysis/` - 深入的统计分析
  - 语言效应的统计检验
  - 模型特性分析
  - 文化特征保持分析
  - 问题层面的敏感性分析

### 交互式可视化

- `results/roleplay_multilingual/*.html` - 交互式文化地图
  - 可缩放的Plotly图表
  - 悬停显示详细信息
  - 多维度筛选功能

## 🎓 研究意义

### 学术价值

1. **首次系统性研究**语言对LLM文化价值表达的影响
2. **发现反直觉现象**：英语悖论挑战常见假设
3. **大规模实证数据**：7模型×26国家×5语言
4. **方法论贡献**：控制变量的跨语言评估框架

### 实践价值

1. **AI全球化部署指导**：不同地区应选择何种语言
2. **多语言系统设计**：了解语言对模型行为的影响
3. **文化偏见评估**：识别模型的文化倾向和偏见
4. **模型选择建议**：不同场景下的最优模型

### 社会影响

1. **AI公平性**：揭示LLM的英语中心主义问题
2. **语言多样性**：强调非英语文化表达的重要性
3. **数字鸿沟**：关注非英语用户的AI体验
4. **文化保护**：警示AI可能对文化多样性的影响

## 📚 相关文档

### 核心文档

- **快速开始**: [`docs/QUICK_START.md`](docs/QUICK_START.md)
- **多语言实验指南**: [`MULTILINGUAL_EXPERIMENT_GUIDE.md`](MULTILINGUAL_EXPERIMENT_GUIDE.md)
- **角色扮演系统**: [`docs/ROLEPLAY_SYSTEM_README.md`](docs/ROLEPLAY_SYSTEM_README.md)
- **项目结构总结**: [`PROJECT_STRUCTURE_SUMMARY.md`](PROJECT_STRUCTURE_SUMMARY.md)

### 研究报告

- **角色扮演分析**: [`docs/roleplay_analysis_report.md`](docs/roleplay_analysis_report.md)
- **AI PCA分析**: [`docs/ai_pca_analysis_report.md`](docs/ai_pca_analysis_report.md)
- **模型响应分析**: [`docs/model_response_analysis.md`](docs/model_response_analysis.md)

### 开题汇报材料

- **完整汇报**: [`完整开题汇报_三阶段研究.md`](完整开题汇报_三阶段研究.md)
- **核心数据**: [`开题汇报_核心数据.md`](开题汇报_核心数据.md)
- **准备材料**: [`开题汇报_准备材料.md`](开题汇报_准备材料.md)
- **练习脚本**: [`汇报练习脚本.md`](汇报练习脚本.md)

## 🔧 开发指南

### 代码结构

- **基类架构** (`src/base/`): 所有分析模块继承自统一的基类
  - `BaseInterview`: 统一的访谈接口
  - `BasePCAAnalyzer`: 统一的PCA分析方法
  - `BaseCulturalMapVisualizer`: 统一的可视化方法
  - `IVSQuestionProcessor`: 统一的问题处理逻辑

- **模块化设计**: 每个研究阶段独立模块
  - `country_values`: 真实国家基准
  - `llm_values`: LLM直接回答
  - `roleplay_English`: 英语角色扮演
  - `roleplay_multilingual`: 多语言对比

### 添加新语言

1. 在 `config/multilingual_questions_complete.json` 添加语言配置
2. 翻译IVS问题和文化背景描述
3. 在 `src/roleplay_multilingual/` 中添加语言支持
4. 运行多语言实验收集数据
5. 使用统一的分析流程处理结果

### 添加新模型

1. 在 `config/llm_models.json` 添加模型配置
2. 确保API密钥和endpoint正确
3. 使用统一的访谈接口收集数据
4. 结果会自动纳入对比分析

## 🤝 贡献指南

1. 确保代码符合项目的基类架构
2. 新增功能请在相应的模块目录下开发
3. 重要实验结果请保存在 `results/` 目录
4. 更新相关文档
5. 运行测试确保兼容性

## 📄 许可证

本项目仅供学术研究使用。

## 📞 技术支持

如有问题，请查看：
1. `docs/` 目录下的详细文档
2. `logs/` 目录下的运行日志
3. `results/` 目录下的分析报告

---

## 🌟 核心贡献

**首次系统性研究了语言对大语言模型文化价值表达的影响，发现了"英语悖论"现象，为跨语言AI研究和全球化AI部署提供了重要的实证基础和方法论框架。**

---

**最后更新**: 2024年10月18日  
**项目状态**: 已完成阶段一核心实验，正在进行深度分析和论文撰写
