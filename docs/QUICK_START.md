# 文化地图项目快速启动指南

## 项目概述

本项目实现了基于IVS（国际价值观调查）数据的Inglehart-Welzel文化地图分析，包括：

1. **数据处理**: 加载和预处理IVS数据
2. **主成分分析**: 使用PPCA进行降维分析
3. **文化地图绘制**: 创建Inglehart-Welzel文化地图
4. **结果可视化**: 多种图表展示分析结果

## 项目结构

```
cultural_map_project/
├── README.md                    # 项目说明
├── QUICK_START.md              # 快速启动指南
├── requirements.txt            # Python依赖
├── create_sample_data.py       # 创建示例数据脚本
├── setup_project.py           # 项目设置脚本
│
├── config/                    # 配置文件
│   ├── ivs_questions.json     # IVS问题配置
│   └── cultural_regions.json  # 文化区域配置
│
├── src/                       # 源代码模块
│   ├── __init__.py
│   ├── data_processing.py     # 数据处理模块
│   ├── pca_analysis.py        # PCA分析模块
│   └── visualization.py       # 可视化模块
│
├── notebooks/                 # Jupyter notebooks
│   └── 01_cultural_map_analysis.ipynb  # 主要分析notebook
│
├── data/                      # 数据文件
│   ├── ivs_df.pkl            # IVS原始数据
│   ├── country_codes.pkl     # 国家代码数据
│   └── *.csv                 # CSV格式数据
│
├── outputs/                   # 输出结果
│   ├── cultural_map.png      # 文化地图
│   ├── pca_loadings.png      # 载荷图
│   └── country_scores_pca.pkl # 国家文化得分
│
└── logs/                      # 日志文件
```

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+和以下主要依赖：

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
pip install factor-analyzer ppca loguru jupyter
```

或使用requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 创建示例数据

如果没有真实的IVS数据，可以创建示例数据：

```bash
python create_sample_data.py
```

### 3. 运行分析

启动Jupyter并运行主要分析notebook：

```bash
jupyter notebook notebooks/01_cultural_map_analysis.ipynb
```

### 4. 查看结果

分析完成后，查看outputs目录中的结果：

- `cultural_map.png`: Inglehart-Welzel文化地图
- `pca_loadings.png`: PCA载荷图
- `explained_variance.png`: 解释方差图
- `country_scores_pca.pkl`: 国家文化得分数据

## 核心功能模块

### 1. 数据处理 (`src/data_processing.py`)

- `IVSDataProcessor`: IVS数据加载和预处理
- `CountryMetadataProcessor`: 国家元数据处理

### 2. PCA分析 (`src/pca_analysis.py`)

- `CulturalPCAAnalyzer`: 文化价值观PCA分析
- `StandardPCAAnalyzer`: 标准PCA分析（备选）

### 3. 可视化 (`src/visualization.py`)

- `CulturalMapVisualizer`: 文化地图可视化
- 支持多种图表类型：文化地图、载荷图、解释方差图等

## IVS十个核心问题

本项目基于以下10个IVS问题构建文化地图：

**传统 vs 世俗理性价值观维度：**
- A008: 宗教的重要性
- A165: 对权威的尊重
- C001: 工作的重要性
- C002: 家庭的重要性
- E001: 政治参与

**生存 vs 自我表达价值观维度：**
- E002: 经济安全感
- E003: 社会宽容度
- E004: 生活满意度
- F063: 环境保护意识
- F118: 性别平等观念

## 文化区域分类

项目支持以下8个主要文化区域：

1. **English-Speaking** (英语国家)
2. **Protestant Europe** (新教欧洲)
3. **Catholic Europe** (天主教欧洲)
4. **Orthodox Europe** (东正教欧洲)
5. **Confucian** (儒家文化圈)
6. **Latin America** (拉丁美洲)
7. **African-Islamic** (非洲-伊斯兰)
8. **West & South Asia** (西亚南亚)

## 下一步开发计划

1. **大模型API集成**
   - 添加对主流大模型API的支持
   - 实现大模型回答IVS问题的功能

2. **大模型文化评估**
   - 计算大模型的文化坐标
   - 分析大模型的文化倾向

3. **国家文化模拟**
   - 大模型模仿不同国家文化回答问题
   - 验证模拟效果的准确性

4. **交互式界面**
   - 开发Web界面
   - 实时文化地图更新

## 故障排除

### 常见问题

1. **Python环境问题**
   - 确保使用Python 3.8+
   - 检查是否正确安装了所有依赖

2. **数据文件缺失**
   - 运行`create_sample_data.py`创建示例数据
   - 或提供真实的IVS数据文件

3. **PPCA分析失败**
   - 系统会自动回退到标准PCA
   - 检查数据质量和缺失值情况

4. **可视化问题**
   - 确保安装了matplotlib和seaborn
   - 检查中文字体设置

### 获取帮助

- 查看日志文件：`logs/`目录
- 检查数据质量报告
- 参考原始项目：`model_cultural_comp-main`

## 许可证

本项目基于MIT许可证开源。