# Stage3 全面测试指南

## ✅ 预检查完成

所有系统检查已通过，可以安全开始全面测试！

---

## 📊 测试规模

### 配置概览
- **配置文件**: `comprehensive_multilingual_config.json`
- **测试类型**: 完整多语言角色扮演测试

### 数据规模
| 维度 | 数量 | 说明 |
|------|------|------|
| 语言类型 | 6种 | zh-cn, ru, es, ar, en, en-native |
| 语言-国家对 | 59个 | 27本国语 + 27英语对比 + 5英语母语 |
| 独特国家数 | 32个 | 去重后的国家总数 |
| LLM模型 | 7个 | GPT, Claude, Gemini, LLaMA, DeepSeek, QWen, Mistral |
| 问题数 | 10个 | IVS核心问题 |
| 共识轮数 | 5轮 | 每问题5次取众数 |

### 计算量
```
总任务数 = 59 × 7 = 413 个任务
总API调用 = 413 × 10 × 5 = 20,650 次
预估成本 = ~$12-15 USD
预估时间 = 8-12 小时（并发执行）
```

---

## 🚀 启动测试

### 1. 运行主程序
```bash
python3 src/run/run_roleplay_multilingual_analysis.py
```

### 2. 选择测试选项
```
选择选项: 1
完整访谈测试（32国家×7模型×5轮）
```

### 3. 确认测试参数
程序会显示：
```
🚀 开始完整测试 (32国家×7模型×5轮)
   - 27个非英语国家（各自母语+英语）
   - 5个英语母语国家（仅英语）

📊 预估统计:
   - 语言-国家对: 59个
   - 任务数: 413个
   - 总API调用: 20,650次
   - 预估成本: ~$12.39 USD
   - 预估时间: 5.8 - 11.5 小时

是否继续？(y/n)
```

输入 `y` 确认开始。

---

## 📂 数据流程

### Step 0: 访谈
**文件位置**: `data/roleplay_multilingual/llm_responses_roleplay_ml/`

**生成文件**:
- `roleplay_results_ml_comprehensive_YYYYMMDD_HHMMSS.pkl` ← **主要结果**
- `roleplay_results_ml_comprehensive_YYYYMMDD_HHMMSS.json` ← 备份格式

**数据结构**:
```python
{
    'results': [
        {
            'model_name': 'openai/gpt-4o-mini',
            'country': {'name': 'China', ...},
            'language': 'zh-cn',
            'responses': {
                'A008': {
                    'answer': '...',
                    'numeric_value': 3,
                    ...
                },
                ...
            }
        },
        ...
    ],
    'test_type': 'comprehensive',
    'consensus_count': 5,
    ...
}
```

### Step 1: 数据处理
**文件位置**: `data/roleplay_multilingual/`

**生成文件**:
- `llm_roleplay_ml_processed_responses_ivs_format_*.pkl` ← IVS格式数据
- `llm_roleplay_ml_processed_responses_ivs_format_*.json`
- `llm_roleplay_ml_processed_responses_ivs_format_*.csv`

**处理内容**:
- ✅ Y002/Y003 numeric_value提取（非standardized_value）
- ✅ 众数投票（5轮取最多）
- ✅ 置信度计算
- ✅ IVS格式转换

### Step 2: PCA分析
**文件位置**: `data/roleplay_multilingual/`

**生成文件**:
- `roleplay_ml_pca_entity_scores_latest.pkl` ← **主要PCA结果**
- `roleplay_ml_pca_entity_scores_*.pkl` ← 带时间戳版本
- `roleplay_ml_analysis_metadata_*.json` ← 元数据

**分析内容**:
- ✅ PPCA处理缺失值
- ✅ Varimax旋转
- ✅ PC1/PC2 rescaling
- ✅ 与IVS数据merge
- ✅ 语言效应分析

**数据结构**:
```python
DataFrame包含:
- PC1, PC2 (原始PCA分数)
- PC1_rescaled, PC2_rescaled (标准化分数)
- country_code (国家名)
- language (语言类型: zh-cn/ru/es/ar/en/en-native)
- model_name (模型名称)
- data_source (Multilingual 或 IVS)
- Cultural Region (文化区域)
```

### Step 3: 语言对比分析
**文件位置**: `results/roleplay_multilingual/roleplay_ml_dashboard/`

**生成文件**:
- `language_comparison_analysis_*.json` ← 对比分析数据
- `language_distance_comparison_*.png` ← 距离对比图
- `country_level_language_comparison_*.png` ← 国家级对比
- `model_specific_language_comparison_*.png` ← 模型语言效果
- `interactive_language_comparison_*.html` ← 交互式对比
- `interactive_model_language_comparison_*.html` ← 交互式模型对比

**分析维度**:
1. **en-native (基准)**: 英语母语国家的表现
2. **en vs native**: 非英语国家用英语 vs 本国语言
3. **模型对比**: 各模型在不同语言的表现
4. **国家对比**: 各国在不同语言的差异

**核心指标**:
```python
{
    'en_native_avg_distance': 2.XXX,  # 基准线
    'english_avg_distance': 3.XXX,    # 非英语国家用英语
    'native_avg_distance': 4.XXX,     # 本国语言
    'english_vs_en_native': XX.X%,    # en比en-native差XX%
    'native_vs_en_native': XX.X%,     # native比en-native差XX%
    'language_improvement': XX.X%     # en vs native的改进
}
```

### Step 4: 可视化
**文件位置**: `results/roleplay_multilingual/roleplay_ml_dashboard/`

**生成文件**:
- `multilingual_cultural_map_corrected_*.png` ← **静态文化地图**
- `multilingual_cultural_map_interactive_fixed_*.html` ← **交互式地图**
- `language_model_comparison_*.png` ← 语言-模型综合对比
- `multilingual_accuracy_analysis_*.json` ← 准确性分析
- `multilingual_cultural_coordinates_*.json` ← 文化坐标
- `summary_statistics_*.txt` ← 统计摘要

**可视化特点**:
- ✅ 真实国家按文化区域着色（8个区域）
- ✅ 颜色与base完全一致
- ✅ IVS数据自动聚合（110个国家）
- ✅ 多语言数据按语言分组
- ✅ 交互式hover显示详细信息

---

## 🎯 预期结果

### 1. 数据完整性
- ✅ 413个任务全部完成
- ✅ 20,650次API调用成功
- ✅ 无缺失数据（或PPCA自动填充）

### 2. PCA结果
```
总实体数: ~137 个
- IVS数据: ~110 个国家（聚合后）
- Multilingual数据: 27 个实体（59个语言-国家对的某些子集）

PC1范围: [-10, 10]
PC2范围: [-10, 10]
```

### 3. 语言对比发现
预期发现（基于研究假设）:
- en-native表现最好（距离真实国家最近）
- en（非英语国家用英语）中等
- native（本国语言）表现取决于模型训练数据

### 4. 可视化输出
- 12个主要可视化文件
- 静态图PNG格式（高分辨率）
- 交互式HTML（可缩放、hover）

---

## ⚠️ 注意事项

### 1. 运行时间
- **快速场景**: ~6小时（高并发，网络好）
- **慢速场景**: ~12小时（低并发，网络慢）
- **建议**: 晚上运行，第二天查看结果

### 2. 错误处理
程序已内置错误处理：
- ✅ 自动重试（API失败）
- ✅ 跳过无效响应
- ✅ 详细错误日志
- ✅ 中断恢复（部分完成的任务会保存）

### 3. 成本控制
- 使用mix模型（不同价格）
- 预估成本：~$12-15 USD
- 实际成本可能因模型API价格变动而有所不同

### 4. 磁盘空间
预计需要：
- 原始数据: ~50 MB
- 处理后数据: ~30 MB
- PCA结果: ~10 MB
- 可视化文件: ~20 MB
- **总计**: ~110 MB

---

## 🔧 故障排查

### 问题1: 配置文件找不到
**错误**: `FileNotFoundError: comprehensive_multilingual_config.json`
**解决**: 确保在项目根目录运行，文件位于根目录下

### 问题2: API超时
**错误**: `TimeoutError` 或 `ConnectionError`
**解决**: 
1. 降低并发度（修改`max_workers`）
2. 检查网络连接
3. 检查API配额

### 问题3: 内存不足
**错误**: `MemoryError`
**解决**:
1. 关闭其他程序
2. 分批运行（先运行小规模测试）
3. 增加虚拟内存

### 问题4: 国家名称匹配失败
**现象**: en-native数据没有显示
**原因**: 国家名称格式不一致（已修复）
**验证**: 检查是否有"United States of America (the)"等后缀

### 问题5: 颜色显示不一致
**现象**: 文化区域颜色与Stage1/2不同
**原因**: 颜色配置不统一（已修复）
**验证**: 
- Protestant Europe应为 #d55e00（深橙红）
- Confucian应为 #cc0000（鲜红）

---

## 📞 技术支持

### 已修复的已知问题
✅ Y002/Y003 numeric_value提取
✅ 国家名称normalize匹配
✅ en-native基准缺失
✅ 文化区域颜色不一致
✅ IVS数据重复（未聚合）
✅ 可视化路径嵌套
✅ 文件命名不统一

### 架构改进
✅ PCA完全继承BasePCAAnalyzer
✅ 可视化继承BaseCulturalMapVisualizer
✅ 数据流标准化
✅ 命名规范统一

### 当前状态
🎉 **所有系统检查通过，可以安全开始全面测试！**

---

## 📝 运行日志示例

```
================================================================================
🌐 多语言角色扮演测试系统 v3.0
================================================================================

选择测试选项：
1. 完整访谈测试（32国家×7模型×5轮）
2. 小规模验证测试（5国家×3模型×1轮）
3. 仅语言对比分析（需要已有数据）
4. 仅生成可视化（需要已有数据）
5. 完整流程（访谈+处理+分析+可视化）
0. 退出

选择选项: 1

🚀 开始完整测试 (32国家×7模型×5轮)
   - 27个非英语国家（各自母语+英语）
   - 5个英语母语国家（仅英语）

📊 预估统计:
   - 语言-国家对: 59个
   - 任务数: 413个
   - 总API调用: 20,650次
   - 预估成本: ~$12.39 USD
   - 预估时间: 5.8 - 11.5 小时

是否继续？(y/n): y

============================================================
📋 步骤0: 多语言访谈 (32国家×7模型×5轮共识)
============================================================

🤖 使用所有可用模型: 7 个
   - openai/gpt-4o-mini
   - anthropic/claude-3.7-sonnet
   - google/gemini-2.0-flash-001
   - meta-llama/llama-3.3-70b-instruct
   - deepseek/deepseek-chat-v3-0324
   - qwen/qwq-32b
   - mistralai/mistral-nemo

✅ 加载完整测试配置: comprehensive_multilingual_config.json

准备运行 413 个多语言访谈任务
并发度: 3 (高并发模式)
每个任务将重复 5 轮问卷
预计总API调用: 413 × 10问题 × 5轮 = 20650 次

[进度显示...]
✅ 完成: 1/413 [China(zh-cn)/openai/gpt-4o-mini] 众数: 8/10
✅ 完成: 2/413 [China(zh-cn)/anthropic/claude-3.7-sonnet] 众数: 9/10
...

✅ 全部任务完成！
💾 结果已保存: roleplay_results_ml_comprehensive_20251103_080000.pkl

[继续执行step1-4...]
```

---

## 🎓 参考文档

- 项目README: `README.md`
- Stage3架构: `UNIFIED_RUNNER_GUIDE.md`
- 多语言配置: `MULTILINGUAL_ROLEPLAY_README.md`
- 英语基准: `ENGLISH_NATIVE_BASELINE.md`

---

**最后更新**: 2025-11-03
**状态**: ✅ 就绪测试




















