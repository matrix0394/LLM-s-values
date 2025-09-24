# 文化地图项目 (Cultural Map Project)

基于世界价值观调查(World Values Survey)数据的文化地图分析项目，使用PCA分析生成Inglehart-Welzel文化地图。

## 项目结构

```
cultural_map_project/
├── data/                   # 输入数据目录
│   ├── *.sav              # SPSS数据文件（可选）
│   ├── ivs_df.pkl         # 处理后的IVS数据
│   └── country_codes.pkl  # 国家代码数据
├── results/               # 输出结果目录
│   ├── cultural_map.png   # 静态文化地图
│   ├── cultural_map_interactive.html  # 交互式地图
│   ├── country_scores_pca.pkl  # PCA分析结果
│   └── coordinate_comparison.csv  # 坐标对比结果
├── src/                   # 核心代码模块
│   ├── data_processing.py # 数据处理模块
│   ├── pca_analysis.py    # PCA分析模块
│   ├── ppca.py           # PPCA工具类
│   └── visualization.py   # 可视化模块
├── config/                # 配置文件
│   ├── ivs_questions.json # IVS问题配置
│   └── cultural_regions.json  # 文化区域配置
└── notebooks/             # Jupyter笔记本
    └── *.ipynb           # 分析笔记本
```

## 安装依赖

```bash
pip install pandas numpy matplotlib seaborn scikit-learn plotly loguru pyreadstat
```

## 使用方法

### 分步骤运行

按照以下顺序运行各个模块：

1. **数据处理**：
```bash
cd src
python data_processing.py
```

2. **PCA分析**：
```bash
python pca_analysis.py
```

3. **可视化**：
```bash
python visualization.py
```

### 注意事项

- 必须按照上述顺序运行，每个步骤依赖前一步的输出
- 数据处理模块会生成处理后的数据文件
- PCA分析模块使用PPCA作为工具类进行分析
- 可视化模块将结果输出到`results/`目录

## 核心功能模块

### 1. 数据处理 (data_processing.py)

- **IVSDataProcessor类**: 处理世界价值观调查数据
- 功能:
  - 加载SPSS格式的原始数据
  - 数据清洗和预处理
  - 提取核心价值观问题
  - 处理缺失值

### 2. PCA分析 (pca_analysis.py)

- **CulturalPCAAnalyzer类**: 执行主成分分析
- 功能:
  - 使用自定义PPCA（概率主成分分析）处理缺失数据
  - 应用Varimax旋转优化结果
  - 计算国家文化坐标
  - 分配文化区域
  - 坐标对比分析

### 3. 可视化 (visualization.py)

- **CulturalMapVisualizer类**: 生成文化地图
- 功能:
  - 绘制静态Inglehart-Welzel文化地图
  - 创建交互式文化地图
  - 绘制PCA载荷图
  - 自定义样式和颜色配置

## 输出结果

运行完成后，将在以下位置生成结果文件：

- `results/cultural_map.png` - 静态文化地图
- `results/cultural_map_interactive.html` - 交互式文化地图
- `results/pca_analysis.png` - PCA分析图表
- `data/country_scores_pca.pkl` - 国家文化坐标数据
- `data/pca_results.pkl` - PCA分析结果

## 配置文件

### ivs_questions.json
定义用于分析的IVS问题及其权重和方向。

### cultural_regions.json
定义文化区域的国家分组和可视化颜色配置。

## 技术特点

1. **处理缺失数据**: 使用PPCA算法有效处理调查数据中的缺失值
2. **Varimax旋转**: 优化主成分的可解释性
3. **坐标重新缩放**: 将PCA结果映射到Inglehart-Welzel标准坐标系
4. **模块化设计**: 核心功能分离，便于维护和扩展
5. **灵活的输入输出**: 支持多种数据格式和可视化选项

## 注意事项

1. 确保 `data/` 目录存在并包含必要的数据文件
2. 如果使用真实SPSS数据，请将 `.sav` 文件放在 `data/` 目录中
3. 程序会自动创建 `results/` 目录存储输出结果
4. 日志文件保存在 `results/cultural_map_analysis.log`

## 故障排除

- **数据文件缺失**: 程序会自动创建示例数据
- **依赖包问题**: 确保安装了所有必要的Python包
- **内存不足**: 对于大型数据集，可能需要调整样本大小
- **坐标对比失败**: 确保参考项目文件路径正确

## 许可证

本项目仅供学术研究使用。