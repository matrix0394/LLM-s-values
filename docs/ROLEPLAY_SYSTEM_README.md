# 完整并发Roleplay访谈系统

## 系统概述

这是一个完整的并发roleplay访谈系统，支持所有7个模型对109个国家的文化价值观模拟访谈。

### 主要功能

- ✅ **全模型覆盖**: 支持所有7个模型 (GPT-4o-mini, Gemini, Claude, Llama, DeepSeek, Qwen, Mistral)
- ✅ **全国家覆盖**: 支持country_scores_pca.json中的109个国家
- ✅ **并发执行**: 支持8个并发线程，大幅提升执行速度
- ✅ **断点续传**: 支持随时停止和恢复，自动跳过已完成的任务
- ✅ **实时监控**: 实时显示进度和预计完成时间
- ✅ **自动保存**: 每10个任务自动保存检查点
- ✅ **结果分析**: 自动分析回答效果，识别问题模型和国家
- ✅ **优化建议**: 生成针对性的prompt优化建议

## 文件结构

```
├── full_concurrent_roleplay.py      # 主系统文件
├── analyze_and_optimize.py          # 结果分析文件
├── start_roleplay_system.py         # 启动管理脚本
├── ROLEPLAY_SYSTEM_README.md        # 使用说明
└── data/llm_responses_roleplay/     # 结果存储目录
    ├── roleplay_checkpoint.json     # 检查点文件
    ├── roleplay_results.json        # 最终结果文件
    └── analysis_results_*.json      # 分析结果文件
```

## 使用方法

### 1. 启动系统

```bash
# 方法1: 使用管理脚本 (推荐)
python3 start_roleplay_system.py

# 方法2: 直接启动
python3 full_concurrent_roleplay.py
```

### 2. 管理操作

使用管理脚本时，可以选择以下操作：

1. **启动系统** - 开始或恢复访谈
2. **停止系统** - 安全停止当前运行
3. **查看进度** - 显示当前完成情况
4. **分析结果** - 分析已完成的结果
5. **退出** - 退出管理界面

### 3. 停止和恢复

- **安全停止**: 按 `Ctrl+C` 或使用管理脚本的停止功能
- **自动保存**: 系统会自动保存检查点，下次启动时自动恢复
- **跳过已完成**: 系统会自动跳过已经完成的模型-国家组合

## 系统配置

### 并发设置

```python
# 在 full_concurrent_roleplay.py 中修改
system = FullConcurrentRoleplaySystem(
    max_workers=8,        # 并发线程数 (建议4-10)
    checkpoint_interval=10 # 检查点间隔 (每N个任务保存一次)
)
```

### 模型配置

系统会自动加载 `config/llm_models.json` 中的所有模型：

- `openai/gpt-4o-mini`
- `google/gemini-2.0-flash-001`
- `anthropic/claude-3.7-sonnet`
- `meta-llama/llama-3.3-70b-instruct`
- `deepseek/deepseek-chat-v3-0324`
- `qwen/qwq-32b`
- `mistralai/mistral-nemo:free`

### 问题配置

系统会访谈以下10个问题：

- `A008` - 生活满意度
- `A165` - 宗教重要性
- `E018` - 政治参与
- `E025` - 政治信任
- `F063` - 上帝重要性
- `F118` - 工作重要性
- `F120` - 家庭重要性
- `G006` - 性别角色
- `Y002` - 儿童教育价值观 (双选)
- `Y003` - 儿童教育价值观 (多选)

## 执行时间估算

- **总任务数**: 7个模型 × 109个国家 = 763个任务
- **每个任务**: 10个问题 × 平均2秒 = 约20秒
- **并发执行**: 8个线程
- **预计总时间**: 约30-40分钟 (取决于API响应速度)

## 结果分析

### 自动分析功能

系统会自动分析以下方面：

1. **模型表现**: 各模型的成功率统计
2. **国家表现**: 各国家的平均成功率
3. **问题难度**: 各问题的回答成功率
4. **问题组合**: 识别表现较差的模型-国家组合

### 优化建议

系统会生成以下优化建议：

1. **模型优化**: 为表现较差的模型设计专门prompt
2. **国家优化**: 为表现较差的国家提供更详细的文化背景
3. **问题优化**: 为最难回答的问题设计专门prompt
4. **组合优化**: 为特定模型-国家组合设计定制化prompt

## 监控和调试

### 实时监控

系统会实时显示：

- 当前进度 (已完成/总数)
- 执行时间
- 预计剩余时间
- 当前正在执行的任务

### 日志文件

- 检查点文件: `data/llm_responses_roleplay/roleplay_checkpoint.json`
- 结果文件: `data/llm_responses_roleplay/roleplay_results.json`
- 分析文件: `data/llm_responses_roleplay/analysis_results_*.json`

### 错误处理

- 自动重试机制
- 错误记录和统计
- 失败任务标记
- 继续执行未完成任务

## 性能优化

### 已实现的优化

1. **并发执行**: 8个线程同时工作
2. **断点续传**: 避免重复执行已完成任务
3. **智能重试**: 针对不同模型使用不同重试策略
4. **内存优化**: 及时释放不需要的数据
5. **API优化**: 针对不同模型使用最优参数

### 进一步优化建议

1. **调整并发数**: 根据API限制调整max_workers
2. **优化检查点间隔**: 根据任务大小调整checkpoint_interval
3. **模型优先级**: 优先执行表现好的模型
4. **国家分组**: 按文化区域分组执行

## 故障排除

### 常见问题

1. **API限制**: 减少并发数或增加延迟
2. **内存不足**: 减少checkpoint_interval
3. **网络问题**: 检查网络连接和API密钥
4. **权限问题**: 确保有写入data目录的权限

### 恢复方法

1. **检查点恢复**: 系统会自动从检查点恢复
2. **手动清理**: 删除检查点文件重新开始
3. **部分恢复**: 手动编辑检查点文件跳过特定任务

## 结果使用

### 数据格式

结果文件包含以下信息：

```json
{
  "timestamp": "2025-09-25T03:30:00",
  "total_tasks": 763,
  "successful_tasks": 720,
  "total_questions": 7630,
  "total_valid_responses": 6840,
  "overall_success_rate": 89.6,
  "results": [
    {
      "model": "google/gemini-2.0-flash-001",
      "country": "United States",
      "timestamp": "2025-09-25T03:30:00",
      "total_questions": 10,
      "valid_responses": 9,
      "success_rate": 90.0,
      "responses": [...]
    }
  ]
}
```

### 后续处理

1. **数据清洗**: 使用分析结果识别和清理无效数据
2. **PCA分析**: 将结果用于文化地图分析
3. **可视化**: 生成文化地图和对比图表
4. **报告生成**: 生成详细的分析报告

## 注意事项

1. **API成本**: 大量并发请求可能产生较高API费用
2. **网络稳定**: 确保网络连接稳定，避免中断
3. **存储空间**: 确保有足够的磁盘空间存储结果
4. **时间安排**: 建议在网络使用较少的时间段运行
5. **监控运行**: 建议定期检查运行状态和进度

## 技术支持

如果遇到问题，请检查：

1. 系统日志和错误信息
2. API密钥和网络连接
3. 磁盘空间和权限
4. 模型配置和参数设置

系统设计为高度自动化，大部分情况下可以无人值守运行。
