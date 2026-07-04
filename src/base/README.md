# Base模块 - 统一基础设施

## 📦 模块概述

Base模块提供Stage1-3共享的基础设施，包括：
- 数据处理基类
- 可视化基类
- 问题处理器
- 访谈基类

---

## 📁 文件结构

```
src/base/
├── __init__.py
├── base_pca_analyzer.py              # PCA分析基类 ⭐
├── base_cultural_map_visualizer.py   # 可视化基类 ⭐
├── base_interview.py                 # 访谈基类
├── ivs_question_processor.py         # IVS问题处理器
├── ppca.py                          # PPCA算法实现 🔬
├── README.md                        # 本文件
└── (文档已移除测试文件)
```

---

## 🚀 快速开始

### 1. PCA分析

```python
from src.base.base_pca_analyzer import BasePCAAnalyzer

class MyAnalyzer(BasePCAAnalyzer):
    def load_additional_data(self):
        # 加载你的数据
        return data
    
    def combine_data(self):
        # 使用统一方法处理数据
        data = self.prepare_country_codes_for_merge(raw_data)
        data = self.merge_country_metadata(data)
        return data

# 运行分析
analyzer = MyAnalyzer(data_path="data")
entity_scores = analyzer.run_full_analysis()
```

### 2. 可视化

```python
from src.base.base_cultural_map_visualizer import BaseCulturalMapVisualizer

class MyVisualizer(BaseCulturalMapVisualizer):
    def load_data(self):
        # 加载你的数据
        return data

visualizer = MyVisualizer()

# 获取颜色
region_color = visualizer.get_color_for_region('Orthodox Europe')
model_color = visualizer.get_color_for_model('GPT')

# 绘制地图
visualizer.plot_basic_cultural_map(data)
```

---

## 📚 核心功能

### PPCA算法 (ppca.py)

Probabilistic PCA算法实现，用于处理缺失数据的主成分分析。

```python
from src.base.ppca import PPCA

# 使用PPCA
ppca = PPCA()
ppca.fit(data, d=2, min_obs=1, verbose=True)
components = ppca.transform()
```

**特点**：
- ✅ 处理缺失数据
- ✅ 概率PCA实现
- ✅ 被所有Stage的PCA分析使用

### BasePCAAnalyzer（重构版）

#### 数据清理
```python
# 静态方法 - 可直接调用
clean_code = BasePCAAnalyzer.clean_country_code('100.0')  # '100'
```

#### 数据准备
```python
# 添加标准化的country_code_clean列
df = analyzer.prepare_country_codes_for_merge(df)
```

#### 元数据合并
```python
# 智能合并，支持多种匹配策略
df = analyzer.merge_country_metadata(df)
```

#### 完整流程
```python
analyzer.run_full_analysis()  # 一键运行
```

### BaseCulturalMapVisualizer（重构版）

#### 颜色获取
```python
# 文化区域（8个）
color = visualizer.get_color_for_region('Confucian')

# LLM模型（7个，智能匹配）
color = visualizer.get_color_for_model('gpt-4o-mini')
color = visualizer.get_color_for_model('GPT')  # 简称
color = visualizer.get_color_for_model('gpt')  # 小写
```

#### 绘图
```python
# 基础文化地图
visualizer.plot_basic_cultural_map(data, title="My Map")

# 决策边界
visualizer.plot_decision_boundary(data)

# 对比图
visualizer.create_comparison_plot(data, group_column='region')
```

---

## 🎨 颜色方案

### 8个文化区域

| 区域 | 颜色 |
|-----|------|
| Orthodox Europe | ![#0072b2](https://via.placeholder.com/15/0072b2/000000?text=+) `#0072b2` |
| Catholic Europe | ![#e69f00](https://via.placeholder.com/15/e69f00/000000?text=+) `#e69f00` |
| Protestant Europe | ![#d55e00](https://via.placeholder.com/15/d55e00/000000?text=+) `#d55e00` |
| English-Speaking | ![#009e73](https://via.placeholder.com/15/009e73/000000?text=+) `#009e73` |
| Confucian | ![#cc0000](https://via.placeholder.com/15/cc0000/000000?text=+) `#cc0000` |
| West & South Asia | ![#f0e442](https://via.placeholder.com/15/f0e442/000000?text=+) `#f0e442` |
| African-Islamic | ![#cc79a7](https://via.placeholder.com/15/cc79a7/000000?text=+) `#cc79a7` |
| Latin America | ![#7f7f7f](https://via.placeholder.com/15/7f7f7f/000000?text=+) `#7f7f7f` |

### 7个LLM模型

| 模型 | 颜色 |
|------|------|
| GPT | ![#ff4444](https://via.placeholder.com/15/ff4444/000000?text=+) `#ff4444` |
| Claude | ![#00bfff](https://via.placeholder.com/15/00bfff/000000?text=+) `#00bfff` |
| Gemini | ![#4285f4](https://via.placeholder.com/15/4285f4/000000?text=+) `#4285f4` |
| LLaMA | ![#8b4513](https://via.placeholder.com/15/8b4513/000000?text=+) `#8b4513` |
| DeepSeek | ![#ff6b35](https://via.placeholder.com/15/ff6b35/000000?text=+) `#ff6b35` |
| QWen | ![#ffaa00](https://via.placeholder.com/15/ffaa00/000000?text=+) `#ffaa00` |
| Mistral | ![#9370db](https://via.placeholder.com/15/9370db/000000?text=+) `#9370db` |

查看可视化: `color_palette_visualization.png`

---

## 🧪 测试

### 运行所有测试

```bash
# 功能测试
python3 src/base/test_refactored_base.py

# 颜色测试
python3 src/base/test_color_mapping.py
```

### 预期结果

```
✅ 所有测试通过！
🎉 重构成功！
```

---

## 📖 详细文档

| 文档 | 内容 |
|-----|------|
| **BASE_REFACTOR_GUIDE.md** | PCA分析器重构详解、Stage1-3使用示例 |
| **COLOR_SCHEME_GUIDE.md** | 完整颜色方案、使用指南、最佳实践 |
| **REFACTOR_SUMMARY.md** | 重构总结、测试结果、下一步建议 |

---

## 💡 最佳实践

### 1. 继承基类

```python
# ✅ 好 - 继承base类
class MyAnalyzer(BasePCAAnalyzer):
    pass

# ❌ 不好 - 复制粘贴代码
class MyAnalyzer:
    def perform_pca(self):
        # 大量重复代码...
```

### 2. 使用工具方法

```python
# ✅ 好 - 使用统一方法
df = analyzer.prepare_country_codes_for_merge(df)
df = analyzer.merge_country_metadata(df)

# ❌ 不好 - 自己实现
df['country_code_clean'] = df['country_code'].apply(lambda x: ...)
df = df.merge(...)
```

### 3. 智能颜色匹配

```python
# ✅ 好 - 使用方法
color = visualizer.get_color_for_model(model_name)

# ❌ 不好 - 硬编码
if 'gpt' in model_name.lower():
    color = '#ff4444'
```

---

## 🔄 版本历史

### v2.0 (2025-11-01) - 重构版本
- ✨ 新增统一数据处理方法
- ✨ 新增智能颜色匹配
- 🐛 修复颜色重复问题
- 🐛 修正文化区域数量（11→8）
- 📚 完善文档和测试

### v1.0 (原始版本)
- 基本PCA分析功能
- 基本可视化功能

---

## 🤝 贡献

### 添加新功能

1. 在base类中添加方法
2. 编写测试
3. 更新文档
4. 确保向后兼容

### 报告问题

遇到问题请检查：
1. 是否正确继承base类
2. 是否实现了抽象方法
3. 数据格式是否正确
4. 参考测试代码

---

## 📞 帮助

- **快速开始**: 看本文件
- **详细用法**: 看 `BASE_REFACTOR_GUIDE.md`
- **颜色方案**: 看 `COLOR_SCHEME_GUIDE.md`
- **测试示例**: 看 `test_*.py` 文件
- **重构总结**: 看 `REFACTOR_SUMMARY.md`

---

**Base模块 - 一次编写，到处使用！** 🚀

