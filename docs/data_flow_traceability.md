# LLM价值观分析 - 数据流程追溯文档

## 完整数据流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           阶段0: IVS基准PCA模型                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  输入:                                                                    │
│    - data/country_values/wvs_processed/  (WVS原始数据)                    │
│    - data/country_values/ivs_merged_*.pkl (IVS合并数据)                  │
│                                                                             │
│  处理:                                                                    │
│    - src/country_values/pca_analysis.py                                    │
│    - src/base/ppca.py (概率PCA)                                           │
│    - Varimax旋转 + 缩放到Inglehart-Welzel坐标                            │
│                                                                             │
│  输出:                                                                    │
│    - data/country_values/pca_model_fixed.pkl  ★关键文件★                 │
│      (包含: ppca_C, ppca_means, ppca_stds, rotation_matrix,              │
│       pc_rescale_params)                                                  │
│    - data/country_values/country_scores_pca.json (IVS国家坐标)            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        阶段1: LLM访谈数据收集                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  输入:                                                                    │
│    - prompts/  (访谈问题模板)                                              │
│                                                                             │
│  处理:                                                                    │
│    - 使用LLM API批量生成访谈回答                                           │
│    - 5次重复访谈取众数 (consensus)                                        │
│                                                                             │
│  输出:                                                                    │
│    - data/llm_values/interview_raw/*.json (140个文件)                    │
│      例: anthropic_claude-sonnet-4.5_ar_20251227_215834.json              │
│    - data/roleplay_multilingual/llm_responses_roleplay_ml/                │
│      (按模型-国家-语言分组的访谈结果)                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      阶段2: 数据处理 (IVS格式)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  输入:                                                                    │
│    - data/llm_values/interview_raw/*.json                                 │
│    - config/multilingual_questions_complete.json                           │
│                                                                             │
│  处理:                                                                    │
│    - src/roleplay_multilingual/multilingual_roleplay_data_processor.py   │
│    - 提取10个IVS问题答案                                                  │
│    - 转换为IVS格式                                                        │
│                                                                             │
│  输出:                                                                    │
│    - data/roleplay_multilingual/                                          │
│      llm_roleplay_ml_processed_responses_ivs_format_20251217_175345.pkl  │
│    - 包含字段: country_code, model_name, language, A008, A165, E018...    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      阶段3: PCA投影 (固定模型)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  输入:                                                                    │
│    - data/roleplay_multilingual/..._ivs_format_*.pkl                      │
│    - data/country_values/pca_model_fixed.pkl  ★关键文件★                │
│                                                                             │
│  处理:                                                                    │
│    - src/roleplay_multilingual/multilingual_roleplay_pca_analysis.py     │
│    - 使用transform_with_fixed_pca()方法                                   │
│    - 投影到与IVS相同的PCA空间                                             │
│                                                                             │
│  输出:                                                                    │
│    - data/roleplay_multilingual/roleplay_ml_pca_results_20251217_175350.pkl│
│    - SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段4: 英语优势分析                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  输入:                                                                    │
│    - SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv                   │
│    - data/country_values/country_scores_pca.json (IVS基准)               │
│                                                                             │
│  处理:                                                                    │
│    - analysis/reproduce_english_advantage.py                               │
│    - 计算每国英语vs母语到IVS的欧氏距离                                    │
│    - advantage = (d_native - d_english) / d_native * 100%               │
│                                                                             │
│  输出:                                                                    │
│    - results/metrics/english_advantage_reproduced.csv                            │
│    - 与论文对比验证                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 关键文件说明

### 1. pca_model_fixed.pkl (固定PCA模型)
**位置**: `data/country_values/pca_model_fixed.pkl`

这是整个分析的**核心**，确保所有数据投影到同一个PCA空间：

```python
{
    'ppca_C': 载荷矩阵 (10x2),        # PPCA提取的主成分
    'ppca_means': 均值 (10,),         # 每个IVS问题的均值
    'ppca_stds': 标准差 (10,),        # 每个IVS问题的标准差
    'rotation_matrix': 旋转矩阵 (2x2), # Varimax旋转
    'rotated_loadings': 旋转后载荷,   # 用于解释主成分含义
    'pc_rescale_params': 缩放参数,    # {'PC1': (1.81, 0.38), 'PC2': (1.61, -0.01)}
    'question_ids': IVS问题列表        # ['A008', 'A165', 'E018', ...]
}
```

### 2. Table_S7_LLM_roleplay_PCA_coordinates.csv (最终坐标)
**位置**: `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv`

这是用于所有后续分析的**最终数据**：

| 列名 | 说明 |
|------|------|
| model_name | LLM模型名称 |
| country | 国家名称 |
| country_code | ISO数字代码 |
| language | 访谈语言 (en, ar, zh-cn, fr, es, ru, ja, ko, pt) |
| condition | 实验条件 (imitation) |
| PC1 | 主成分1 (Survival vs Self-expression) |
| PC2 | 主成分2 (Traditional vs Secular-Rational) |
| data_source | 数据来源 (LLM) |

## PCA变换公式

给定原始IVS问题回答向量 **x** = (x₁, x₂, ..., x₁₀)：

1. **标准化**: z = (x - μ) / σ
2. **PPCA投影**: p = z · C
3. **Varimax旋转**: r = p · R
4. **重缩放**: 
   - PC1_rescaled = 1.81 × PC1 + 0.38
   - PC2_rescaled = 1.61 × PC2 - 0.01

## 验证结果

使用 `src/analysis/reproduction/reproduce_english_advantage.py` 验证：

| 指标 | 结果 |
|------|------|
| 关键国家平均差异 | **-0.01%** |
| 完全匹配 | Tunisia, Jordan, Taiwan, Hong Kong, etc. |

## 追溯命令

```bash
# 查看数据流程
ls -la data/llm_values/interview_raw/*.json | head
ls -la data/roleplay_multilingual/*.pkl
ls -la SI/pca/Table_S7*.csv

# 验证PCA模型
python3 -c "
import pickle
with open('data/country_values/pca_model_fixed.pkl', 'rb') as f:
    m = pickle.load(f)
print('Keys:', m.keys())
"
```
