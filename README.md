# 🌍 大语言模型跨语言文化价值观研究

[![项目状态](https://img.shields.io/badge/状态-实验完成-success)](https://github.com/matrix0394/LLM-s-values)
[![最后更新](https://img.shields.io/badge/更新-2025.10.20-blue)](https://github.com/matrix0394/LLM-s-values)
[![阶段](https://img.shields.io/badge/阶段-Stage3完成-brightgreen)](https://github.com/matrix0394/LLM-s-values)

## 🚀 快速导航

- **查看研究成果** → [学术展示系统](slides/stage3/stage3_academic_presentation.html)
- **开始使用** → [汇报材料使用指南](汇报材料使用指南_START_HERE.md)
- **了解核心发现** → [英语悖论专题](#🎨-核心发现英语悖论)
- **运行代码** → [快速开始指南](#🚀-快速开始)
- **查看数据** → [项目结构](#🏗️-项目结构)

---

## 📖 项目概述

本项目是一个基于世界价值观调查（World Values Survey, WVS）数据的大语言模型跨语言文化价值观研究平台。项目通过让LLM用不同语言模仿不同国家的文化背景回答价值观问题，系统性地研究**语言对LLM文化价值表达的影响**。

### 🎯 核心研究问题

**语言是否影响大语言模型对文化价值观的表达？**

通过严格的控制变量实验，让LLM用英语和母语分别模仿同一国家文化，对比其文化价值表达的准确性差异。

### 🔬 研究规模（三阶段设计）

#### Stage 1: LLM自身价值观
- **7个主流模型** 直接回答价值观问题
- **112个真实国家** 作为文化基准
- **10个IVS核心问题** × 5次重复取众数

#### Stage 2: 英语角色扮演
- **7个模型** × **26个重点国家**
- **英语** 提示词角色扮演
- **182个LLM实体** vs 真实国家对比

#### Stage 3: 多语言对比实验 ⭐
- **7个模型** × **26个国家** × **2种语言**（英语+母语）
- **5种语言**：英语、中文、俄语、西班牙语、阿拉伯语
- **371个LLM实体** + 112个真实国家基准
- **18,500+次API调用**
- **控制变量设计**：仅改变语言，其他条件完全相同

## 🎨 核心发现：英语悖论

### 💥 震撼发现

通过大规模实证研究，我们发现了一个**完全违背直觉的现象**：

**26个国家中：**
- ✅ **22个国家（84.6%）：英语更准确！**
- ❌ 4个国家（15.4%）：母语更准确

**整体数据：**
- 母语平均距离：2.193
- 英语平均距离：1.929
- **英语改进幅度：12.0%**

### 🔥 Top 5 英语优势最大案例

| 排名 | 国家 | 母语距离 | 英语距离 | 英语优势 |
|------|------|----------|----------|----------|
| 1️⃣ | 🇨🇳 **中国** | 1.94 | 1.03 | **↓ 47.0%** 🔥 |
| 2️⃣ | 🇸🇬 新加坡 | 1.52 | 1.01 | ↓ 33.7% |
| 3️⃣ | 🇹🇼 台湾 | 3.78 | 2.58 | ↓ 31.8% |
| 4️⃣ | 🇲🇴 澳门 | 1.92 | 1.35 | ↓ 29.7% |
| 5️⃣ | 🇧🇾 白俄罗斯 | 2.15 | 1.54 | ↓ 28.6% |

**关键发现：**
- 华语圈占据前4名！
- 用英语问ChatGPT关于中国的价值观，比用中文准确**47%**！
- 平均英语优势：30-47%

### ⚠️ 少数例外：母语优势案例

| 排名 | 国家 | 母语距离 | 英语距离 | 母语优势 |
|------|------|----------|----------|----------|
| 1️⃣ | 🇵🇪 秘鲁 | 1.91 | 2.37 | ↑ 24.0% |
| 2️⃣ | 🇱🇧 黎巴嫩 | 1.99 | 2.36 | ↑ 18.3% |
| 3️⃣ | 🇺🇦 乌克兰 | 2.63 | 2.94 | ↑ 12.0% |
| 4️⃣ | 🇮🇶 伊拉克 | 2.07 | 2.10 | ↑ 1.6% |

**仅4个国家（15.4%）母语更好，无系统性模式**

### 🤖 模型性能差异

不同模型的英语优势程度：

- **Mistral-nemo**：英语优势最强
- **Claude-3.7-Sonnet**：强英语优势，最佳整体表现
- **GPT-4o-mini**：显著英语优势
- **Llama-3.3-70B**：中等英语优势
- **DeepSeek-v3**：中等英语优势
- **Qwen-QwQ**：较低有效率
- **Gemini-2.0-Flash**：相对平衡

### 🎯 研究意义

这个"**英语悖论**"现象：
1. **挑战常识**：完全颠覆"母语总是更好"的假设（84.6%国家英语更好！）
2. **揭示偏见**：暴露LLM的英语中心主义和训练数据不平衡问题
3. **实践指导**：为全球AI部署和多语言系统设计提供关键数据支持
4. **理论贡献**：首次系统性量化语言对LLM文化表达的影响

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
├── slides/                      # 学术展示材料 ⭐⭐⭐
│   └── stage3/                  # Stage3多语言实验展示
│       ├── stage3_academic_presentation.html     # 完整版学术展示系统
│       ├── stage3_academic_presentation_small.html  # 精简版展示
│       ├── images/                                # 可视化图表
│       │   ├── chart_1_language_coverage.png
│       │   ├── chart_2_84_percent_paradox.png
│       │   ├── chart_3_china_example.png
│       │   ├── chart_4_top_countries.png
│       │   ├── chart_5_model_comparison.png
│       │   ├── chart_6_language_regions.png
│       │   └── chart_7_overall_summary.png
│       ├── LLM跨文化价值观.pptx                  # PowerPoint版本
│       └── README_使用指南.md                     # 使用说明
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

### 查看学术展示 ⭐

```bash
# 方式1：直接在浏览器打开学术展示系统
open slides/stage3/stage3_academic_presentation.html

# 方式2：使用提供的快捷脚本（macOS）
cd slides/stage3
./open_presentation.sh

# 方式3：查看精简版（适合快速预览）
open slides/stage3/stage3_academic_presentation_small.html
```

**学术展示系统特性：**
- 📊 完整的研究成果可视化
- 🎯 7个核心发现展示页
- 📈 交互式图表和数据
- 🎨 专业的学术风格设计
- 📱 响应式布局，支持演示模式

### 运行实验

#### 1. 多语言对比实验（核心功能）⭐

```bash
# 运行综合多语言分析
python scripts/analysis/comprehensive_multilingual_analysis.py

# 运行质量过滤的多语言分析
python scripts/analysis/quality_filtered_multilingual_analysis.py

# 运行深度多语言分析（英语悖论研究）
python scripts/analysis/deep_multilingual_analysis.py

# Stage2 vs Stage3对比分析
python scripts/analysis/compare_stage2_stage3_english.py
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

## 📈 主要结果（基于最新数据）

### 总体统计

**26个国家中：**
- ✅ **22个国家（84.6%）**：英语表现更好
- ❌ **4个国家（15.4%）**：母语表现更好

**整体指标：**
- 母语平均距离：**2.193**
- 英语平均距离：**1.929**
- **平均英语改进：12.0%**

### Top 10 英语优势最大案例

| 排名 | 国家 | 母语距离 | 英语距离 | 英语优势 |
|------|------|----------|----------|----------|
| 1️⃣ | 🇨🇳 中国 | 1.94 | 1.03 | **↓ 47.0%** 🔥 |
| 2️⃣ | 🇸🇬 新加坡 | 1.52 | 1.01 | **↓ 33.7%** |
| 3️⃣ | 🇹🇼 台湾 | 3.78 | 2.58 | **↓ 31.8%** |
| 4️⃣ | 🇲🇴 澳门 | 1.92 | 1.35 | **↓ 29.7%** |
| 5️⃣ | 🇧🇾 白俄罗斯 | 2.15 | 1.54 | ↓ 28.6% |
| 6️⃣ | 🇷🇺 俄罗斯 | 2.40 | 1.73 | ↓ 27.8% |
| 7️⃣ | 🇪🇬 埃及 | 2.15 | 1.56 | ↓ 27.4% |
| 8️⃣ | 🇩🇿 阿尔及利亚 | 2.39 | 1.77 | ↓ 25.9% |
| 9️⃣ | 🇲🇦 摩洛哥 | 2.32 | 1.78 | ↓ 23.3% |
| 🔟 | 🇭🇰 香港 | 1.64 | 1.28 | ↓ 22.0% |

**关键洞察：**
- 华语圈（中国、台湾、香港、澳门、新加坡）英语优势极为显著
- 前10名平均英语优势：**28.7%**
- 中国案例最震撼：用英语问比用中文准确**47%**！

### 母语优势案例（仅4个）

| 排名 | 国家 | 母语距离 | 英语距离 | 母语优势 |
|------|------|----------|----------|----------|
| 1️⃣ | 🇵🇪 秘鲁 | 1.91 | 2.37 | ↑ 24.0% |
| 2️⃣ | 🇱🇧 黎巴嫩 | 1.99 | 2.36 | ↑ 18.3% |
| 3️⃣ | 🇺🇦 乌克兰 | 2.63 | 2.94 | ↑ 12.0% |
| 4️⃣ | 🇮🇶 伊拉克 | 2.07 | 2.10 | ↑ 1.6% |

**仅占总数的15.4%，无系统性地理或语言模式**

### 各语言区表现

| 语言 | 国家数 | 英语优势国家 | 母语优势国家 | 平均改进 |
|------|--------|--------------|--------------|----------|
| 中文 | 5 | 5 (100%) | 0 | **+31.6%** 🔥 |
| 俄语 | 5 | 4 (80%) | 1 | **+18.4%** |
| 阿拉伯语 | 10 | 8 (80%) | 2 | **+13.2%** |
| 西班牙语 | 6 | 5 (83%) | 1 | **+5.1%** |

**中文区英语优势最为显著（100%国家，平均+31.6%）**

### 模型间差异

各模型在多语言实验中的整体表现：

| 模型 | 平均距离 | 有效率 | 英语优势倾向 | 综合评价 |
|------|----------|--------|--------------|----------|
| Claude-3.7-Sonnet | 1.95 | 98.2% | 强 | 🥇 最佳 |
| Gemini-2.0-Flash | 2.08 | 96.8% | 中等 | 🥈 优秀 |
| DeepSeek-v3 | 2.18 | 95.4% | 强 | 良好 |
| Mistral-nemo | 2.12 | 94.5% | 最强 | 良好 |
| Llama-3.3-70B | 2.25 | 96.1% | 中等 | 良好 |
| GPT-4o-mini | 2.45 | 91.2% | 强 | 一般 |
| Qwen-QwQ | 2.38 | 21.8% | 强 | ⚠️ 低效 |

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

### 汇报材料（完整更新版）⭐

**Stage3多语言实验专题：**
- **完整汇报材料**: [`汇报材料_Stage3多语言实验_最新版.md`](汇报材料_Stage3多语言实验_最新版.md)
- **学术展示系统**: [`slides/stage3/stage3_academic_presentation.html`](slides/stage3/stage3_academic_presentation.html)
- **PPT制作指南**: [`Stage3_PPT制作指南.md`](Stage3_PPT制作指南.md)
- **提示词示例**: [`Stage3_提示词示例详细版_PPT素材.md`](Stage3_提示词示例详细版_PPT素材.md)

**三阶段研究整体：**
- **完整三阶段汇报**: [`汇报材料_完整三阶段研究_最新版.md`](汇报材料_完整三阶段研究_最新版.md)
- **完整开题汇报**: [`完整开题汇报_三阶段研究.md`](完整开题汇报_三阶段研究.md)
- **核心数据**: [`开题汇报_核心数据.md`](开题汇报_核心数据.md)
- **准备材料**: [`开题汇报_准备材料.md`](开题汇报_准备材料.md)
- **练习脚本**: [`汇报练习脚本.md`](汇报练习脚本.md)
- **口袋速查卡**: [`开题汇报_口袋速查卡.md`](开题汇报_口袋速查卡.md)

**专题分析：**
- **多语言英语悖论**: [`Stage3专题汇报_多语言英语悖论.md`](Stage3专题汇报_多语言英语悖论.md)
- **Stage2 vs Stage3对比**: [`Stage2_vs_Stage3_英文对比分析_中文总结.md`](Stage2_vs_Stage3_英文对比分析_中文总结.md)
- **PC2负数问题**: [`PC2负数问题分析报告.md`](PC2负数问题分析报告.md)

**使用指南：**
- **START HERE**: [`汇报材料使用指南_START_HERE.md`](汇报材料使用指南_START_HERE.md)
- **材料更新总结**: [`汇报材料更新总结.md`](汇报材料更新总结.md)

## 🔧 开发指南

### 技术特性

**1. 统一的基类架构 ⭐**
- `BaseInterview`: 统一的访谈接口和重复取众数机制
- `BasePCAAnalyzer`: 统一的PCA分析方法（主成分分析 + Varimax旋转）
- `BaseCulturalMapVisualizer`: 统一的Inglehart-Welzel文化地图可视化
- `IVSQuestionProcessor`: 统一的IVS问题处理和评分逻辑

**2. 模块化设计**
- 每个研究阶段（Stage1/2/3）独立模块
- 可复用的数据处理和分析组件
- 灵活的配置管理系统

**3. 重复访谈与众数机制**
- 每个问题访谈5次，自动取众数
- 提高数据可靠性，减少随机性影响
- 保存完整的访谈历史和统计信息

**4. 交互式可视化**
- Plotly驱动的交互式文化地图
- 支持缩放、悬停、筛选等交互操作
- HTML格式，便于分享和展示

**5. 完整的学术展示系统**
- 基于HTML的专业展示系统
- 响应式设计，支持演示模式
- 集成所有核心研究发现

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

## 📊 项目进度

### ✅ 已完成
- **Stage 1**: LLM自身价值观研究（7个模型 × 10个问题 × 5次重复）
- **Stage 2**: 英语角色扮演实验（7个模型 × 26个国家）
- **Stage 3**: 多语言对比实验（7个模型 × 26个国家 × 5种语言）
- **数据分析**: 完整的PCA分析、文化地图可视化、统计检验
- **学术展示**: 完整的HTML展示系统和PPT材料
- **汇报材料**: 全套开题汇报和专题分析文档

### 🔄 进行中
- 深度分析和论文撰写
- 补充实验和数据验证
- 交互式可视化优化

---

**最后更新**: 2025年10月20日  
**项目状态**: 三阶段实验全部完成，学术展示系统已上线，正在进行论文撰写
