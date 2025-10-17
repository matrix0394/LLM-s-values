# 多语言访谈全模型配置指南

## 🎯 配置修改完成

现在当你在多语言访谈中选择 **"2. 重新进行访谈"** 时，系统会自动使用**所有7个配置的模型**进行访谈。

## 🤖 包含的模型

系统会从 `config/llm_models.json` 自动加载以下所有模型：

| 序号 | 模型名称 | 提供商 | 区域 |
|------|----------|--------|------|
| 1 | `openai/gpt-4o-mini` | OpenAI | US |
| 2 | `google/gemini-2.0-flash-001` | Google | US |
| 3 | `anthropic/claude-3.7-sonnet` | Anthropic | US |
| 4 | `meta-llama/llama-3.3-70b-instruct` | Meta | US |
| 5 | `deepseek/deepseek-chat-v3-0324` | DeepSeek | CN |
| 6 | `qwen/qwq-32b` | Qwen | CN |
| 7 | `mistralai/mistral-nemo` | Mistral | EU |

## 📊 访谈规模

### 访谈矩阵
```
7个模型 × 4个国家 × 5种语言 = 140个访谈任务
```

### 详细分解
- **模型**: 7个 (所有配置的模型)
- **国家**: 4个 (China, Russian Federation, Mexico, Egypt)
- **语言**: 5种 (en, zh-cn, ru, es, ar)
- **每个任务**: 10个IVS问题

### 总计
- **API调用数**: 140次
- **问题总数**: 1,400个问题
- **预计时间**: 30-60分钟 (取决于并发设置和API响应速度)

## 🚀 使用方法

### 1. 启动多语言分析
```python
from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner

runner = RoleplayMultilingualAnalysisRunner()
runner.run_complete_analysis()
```

### 2. 交互式选择
当系统检测到现有数据时，会显示：
```
💡 发现充足的访谈数据
请选择操作:
  1. 使用现有数据，跳过访谈
  2. 重新进行访谈（会生成新的时间戳文件）
请输入选择 (1 或 2): 
```

**输入 `2`** 来使用所有7个模型重新访谈。

### 3. 自动执行流程
选择重新访谈后，系统会自动：
1. ✅ 加载所有7个模型
2. ✅ 执行140个访谈任务
3. ✅ 保存结果到带时间戳的文件
4. ✅ 进行数据处理和PCA分析
5. ✅ 生成可视化和对比分析

## ⚙️ 技术实现

### 修改的文件
- `src/roleplay_multilingual/multilingual_roleplay_interview.py`

### 关键修改
```python
def run_multilingual_experiment(self, models: List[str] = None, max_workers: int = 4):
    if models is None:
        # 从配置文件加载所有可用模型
        models = self._load_all_available_models()
        print(f"🤖 使用所有可用模型: {len(models)} 个")

def _load_all_available_models(self) -> List[str]:
    """从配置文件加载所有可用的模型"""
    config_path = Path("config/llm_models.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return list(config.get("models", {}).keys())
```

## 🔧 性能优化建议

### 并发设置
```python
# 默认设置 (推荐)
max_workers = 3  # 平衡速度和稳定性

# 快速模式 (可能不稳定)
max_workers = 5  # 更快但可能遇到API限制

# 保守模式 (最稳定)
max_workers = 1  # 最慢但最稳定
```

### API限制考虑
- OpenRouter有并发限制
- 建议使用默认的 `max_workers=3`
- 如遇到限制错误，系统会自动降级到单线程模式

## 📁 输出文件

所有文件都会包含时间戳，避免覆盖：

### 访谈数据
```
data/roleplay_multilingual/
├── interview_data_20251016_HHMMSS.json
└── multilingual_roleplay_processed_responses_ivs_format_20251016_HHMMSS.pkl
```

### 分析结果
```
data/roleplay_multilingual/
├── multilingual_entity_scores_pca_fixed_20251016_HHMMSS.pkl
└── multilingual_entity_scores_pca_fixed_20251016_HHMMSS.json
```

### 可视化文件
```
results/roleplay_multilingual/
├── multilingual_cultural_map_corrected_20251016_HHMMSS.png
├── language_comparison_analysis_20251016_HHMMSS.json
├── language_distance_comparison_20251016_HHMMSS.png
└── interactive_language_comparison_20251016_HHMMSS.html
```

## 🎯 预期结果

使用所有7个模型后，你将获得：

### 1. 更全面的模型对比
- 7个不同模型的文化价值观表现
- 跨模型的一致性分析
- 模型特定的语言效果对比

### 2. 更丰富的数据
- 从16个数据点增加到112个数据点 (7×16)
- 更稳定的统计分析
- 更可靠的PCA结果

### 3. 更详细的可视化
- 包含所有7个模型的文化地图
- 模型间的聚类分析
- 语言效果的模型特异性分析

## ⚠️ 注意事项

### API成本
- 140次API调用会产生相应费用
- 建议先用少量模型测试

### 时间投入
- 完整访谈可能需要30-60分钟
- 建议在空闲时间运行

### 错误处理
- 系统有自动重试机制
- 部分失败不会影响整体流程
- 所有错误都会详细记录

---

**现在你可以运行 `runner.run_complete_analysis()` 并选择 `2` 来体验所有7个模型的多语言访谈！** 🚀



