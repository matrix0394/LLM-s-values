# 🚀 快速启动：运行选项4测试中文变体

> **一键启动**：繁体中文 vs 简体中文的他者理论验证

---

## ✅ 准备工作（已完成）

- ✅ Bug已修复（IVS坐标聚合问题）
- ✅ 繁体中文问卷已创建（zh-tw, zh-hk）
- ✅ 系统提示词已添加
- ✅ 访谈器已验证
- ✅ 数据合并逻辑已实现

**状态**：🟢 **所有系统就绪，可以立即运行！**

---

## 🎯 测试目标

验证Said的"他者"理论在LLM中的体现：

### 核心假设
| 地区 | 殖民历史 | 预期英语优势 | 理论依据 |
|------|---------|------------|---------|
| 🇭🇰 香港 | 英国150年 | **最高** | 英语官方地位，训练数据以英语为主 |
| 🇹🇼 台湾 | 日本50年 | **低** | 中文主导，无英语殖民 |
| 🇲🇴 澳门 | 葡萄牙400年 | **中等？** | 非英语殖民，待验证 |
| 🇨🇳 大陆 | - | **基准** | 简体中文对照组 |

---

## 🚀 运行步骤

### 方法1：命令行（推荐）

```bash
# 进入项目目录
cd "/Users/yxy/code/LLM's values"

# 运行主程序
python src/run/run_roleplay_multilingual_analysis.py
```

### 方法2：直接Python

```python
cd "/Users/yxy/code/LLM's values"
python3 << 'END'
from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner

runner = RoleplayMultilingualAnalysisRunner()
runner._run_chinese_variant_test_with_full_pipeline()
END
```

---

## 📋 交互流程

### 步骤1：选择选项
```
🌐 Stage3: Roleplay Multilingual 分析系统

请选择要执行的操作：

1️⃣  重新全部访谈 (32国家×7模型，完整测试)
2️⃣  测试小规模访谈 (3模型×5国家×各语言组合，快速验证)
3️⃣  只分析现有数据 (数据处理 → PCA → 可视化)
4️⃣  【他者理论验证】测试中文变体 (繁体中文 vs 简体中文)  ← 选这个
0️⃣  退出

请输入选项 (0-4): 4
```

### 步骤2：确认执行
```
🔬 选项4: 【他者理论验证】测试中文变体
  - 测试地区：
    · 香港 (繁体中文 zh-hk)
    · 台湾 (繁体中文 zh-tw)
    · 澳门 (繁体中文 zh-hk)
  - 对比基准：大陆简体中文 (zh-cn) 已有数据
  - 7个模型
  - 共识轮数: 5轮
  - 完成后合并数据并重新运行完整分析流程

确认执行? (y/n): y  ← 输入y
```

### 步骤3：自动执行

系统会自动完成以下步骤：

#### 📝 步骤1：访谈繁体中文地区（15-30分钟）
```
🌏 访谈 Hong Kong (zh-hk)...
   模型数: 7
   共识轮数: 5
   
   ============================================================
   任务: openai/gpt-4o-mini 扮演 Hong Kong (zh-hk)
   ============================================================
   [访谈进行中...]
   ✅ openai/gpt-4o-mini 扮演 Hong Kong (zh-hk) 完成: 10 个回答
   
   [其他6个模型依次进行...]
   
✅ Hong Kong (zh-hk) 完成，成功 7/7 个模型

🌏 访谈 Taiwan (Province of China) (zh-tw)...
   [同样流程...]

🌏 访谈 Macao (zh-hk)...
   [同样流程...]
```

**预计时间**：
- 总API调用：3地区 × 7模型 × 5轮 × 10问题 = **1050次**
- 时间：**15-30分钟**（取决于API速度和并发度）
- 成本：**$0.50-2.00**（取决于使用的模型）

#### 📝 步骤2：合并数据（1分钟）
```
📝 合并繁体中文数据到现有数据
   读取现有数据: roleplay_ml_processed_XXXXXX.pkl
   现有数据: XXX 条
   
   新数据（繁体中文）: 105 条
   移除旧数据后: XXX 条
   合并后总数据: XXX 条
   
   ✅ 合并数据已保存: roleplay_ml_processed_XXXXXX_with_variants.pkl
   ✅ 最新数据已保存: roleplay_ml_processed_latest.pkl
```

#### 📝 步骤3：重新运行完整分析（2-5分钟）
```
🔄 开始数据处理...
   ✅ 数据处理完成

🔄 开始PCA分析...
   ✅ PCA分析完成
   💾 保存到: roleplay_ml_pca_entity_scores_latest.pkl

🔄 开始语言对比分析...
   📊 三种语言类型平均距离对比:
      🇺🇸 en-native: X.XXX
      🌏 en: Y.YYY
      🗣️ native: Z.ZZZ
   ✅ 语言对比分析完成

🔄 开始文化地图可视化...
   ✅ 可视化完成
```

### 步骤4：查看结果
```
🎉 中文变体测试与分析全部完成！

📊 数据说明:
   - 新增繁体中文数据: 105 条
   - 总数据量: XXX 条
   - 可以查看language_comparison_analysis结果了解繁简体差异

🎊 分析完成!
```

---

## 📊 结果文件

### 数据文件
```
data/roleplay_multilingual/
├── roleplay_ml_processed_latest.pkl              ← 包含繁体数据
├── roleplay_ml_pca_entity_scores_latest.pkl      ← 新PCA结果
└── llm_responses_roleplay_ml/
    └── roleplay_results_ml_XXXXXX.json           ← 原始访谈数据
```

### 分析结果
```
results/roleplay_multilingual/roleplay_ml_dashboard/
├── language_comparison_analysis_XXXXXX.json      ← 语言对比（含繁简体）
├── language_distance_comparison_XXXXXX.png       ← 距离对比图
├── country_level_language_comparison_XXXXXX.png  ← 国家级对比
├── interactive_language_comparison_XXXXXX.html   ← 交互式可视化
└── cultural_map_*.png                            ← 文化地图
```

---

## 🔍 快速查看结果

### 方法1：查看JSON报告
```bash
# 打开最新的语言对比分析
cd "/Users/yxy/code/LLM's values"
cat results/roleplay_multilingual/roleplay_ml_dashboard/language_comparison_analysis_*.json | head -100
```

### 方法2：运行分析脚本
```bash
python << 'EOF'
import json
from pathlib import Path

# 找到最新的分析文件
dashboard = Path("results/roleplay_multilingual/roleplay_ml_dashboard")
files = list(dashboard.glob("language_comparison_analysis_*.json"))
if files:
    latest = max(files, key=lambda x: x.stat().st_mtime)
    with open(latest) as f:
        data = json.load(f)
    
    print("="*60)
    print("📊 中文变体对比结果")
    print("="*60)
    
    # 提取关键数据...
    if 'summary' in data:
        print(data['summary'])
EOF
```

### 方法3：打开交互式HTML
```bash
# Mac
open results/roleplay_multilingual/roleplay_ml_dashboard/interactive_language_comparison_*.html

# 或在浏览器中打开该文件
```

---

## ⏱️ 时间和成本估算

### 时间估算
| 阶段 | 时间 | 说明 |
|------|------|------|
| 访谈 | 15-30分钟 | 取决于API速度 |
| 数据合并 | <1分钟 | 本地处理 |
| 重新分析 | 2-5分钟 | PCA和可视化 |
| **总计** | **20-40分钟** | 全自动 |

### 成本估算（以API调用计）
| 模型 | 单次成本 | 总调用 | 总成本 |
|------|---------|--------|--------|
| GPT-4o-mini | $0.00015 | 150 | $0.02 |
| Claude-3.7 | $0.003 | 150 | $0.45 |
| Gemini-2.0 | $0.0001 | 150 | $0.02 |
| 其他4个 | ~$0.001 | 600 | $0.60 |
| **预计总计** | - | **1050** | **$1-2** |

---

## ❓ 故障排除

### 问题1：API错误
**症状**：某些模型访谈失败
**解决**：
```bash
# 检查API密钥
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
# ...

# 重新运行选项4会跳过已完成的部分
```

### 问题2：数据合并失败
**症状**：提示找不到processed文件
**解决**：
```bash
# 检查现有数据
ls data/roleplay_multilingual/roleplay_ml_processed_*.pkl

# 如果没有，先运行选项3处理现有数据
python src/run/run_roleplay_multilingual_analysis.py
# 选择：3
```

### 问题3：繁体中文问题显示乱码
**症状**：问题或回答显示为方块
**解决**：
- 这是显示问题，不影响实际数据
- 数据文件是UTF-8编码，正确保存了繁体字
- 查看JSON文件或使用支持UTF-8的编辑器

---

## 🎓 预期发现

### 如果假设成立
```
地区         中文距离    英语距离    英语优势
─────────────────────────────────────────
🇨🇳 大陆     2.0         1.9         +5%   ← 基准
🇹🇼 台湾     2.1         2.0         +5%   ← 接近大陆
🇲🇴 澳门     2.0         1.8         +10%  ← 中等
🇭🇰 香港     2.5         1.2         +52%  ← 远超其他！
```

**结论**：✅ 殖民历史显著影响LLM的知识建构

### 如果假设不成立
```
地区         中文距离    英语距离    英语优势
─────────────────────────────────────────
🇨🇳 大陆     2.0         1.9         +5%
🇹🇼 台湾     2.0         1.9         +5%
🇲🇴 澳门     2.0         1.9         +5%
🇭🇰 香港     2.0         1.9         +5%   ← 没有特别优势
```

**结论**：❌ 需要重新思考"他者"理论的适用性

**无论哪种结果都有学术价值！** 🎓

---

## 📚 相关文档

- `Stage3_中文变体测试_使用指南.md` - 详细说明
- `Stage3_他者理论与模型分析_综合报告.md` - 理论背景
- `✅繁体中文问卷创建完成.md` - 技术实现
- `Stage3_重大Bug修复报告.md` - 数据可靠性保证

---

## 🎉 准备好了吗？

**现在就开始！只需一个命令：**

```bash
cd "/Users/yxy/code/LLM's values"
python src/run/run_roleplay_multilingual_analysis.py
```

**然后选择：`4`**

**祝你的理论验证之旅顺利！** 🚀🎓✨















