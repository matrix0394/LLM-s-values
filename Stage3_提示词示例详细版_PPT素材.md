# Stage 3 角色扮演提示词示例 - PPT 制作素材

> 这份文档提供详细的提示词示例，可以直接用于制作 PPT

---

## 📋 Slide 4.5: 角色扮演提示词示例

### 🎯 Slide 标题
**如何让 LLM 扮演不同国家的公民？**

---

## 📐 布局建议

### 上半部分：提示词结构框图

```
┌───────────────────────────────────────────────────────────┐
│          系统提示词 (System Prompt) 四层结构              │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ① 任务说明 (Task Description)                           │
│     "您正在参与一项文化价值观调查"                       │
│                                                           │
│  ② 回答指导原则 (Guidelines)                             │
│     • 根据文化价值观和信念提供真诚回答                   │
│     • 选择最能反映您文化价值观的选项                     │
│     • 像来自您国家的真实人士一样回答                     │
│                                                           │
│  ③ 回答格式要求 (Response Format)                        │
│     • 单选题：仅回答一个数字                             │
│     • Y002（双选）：两个数字用空格分隔                    │
│     • Y003（多选）：1-5个数字用空格分隔                   │
│                                                           │
│  ④ 角色定位 + 文化背景 (Role + Cultural Context)        │
│     您是 {country} 的一位普通民众。                      │
│     {country_context}  ← 关键部分！                      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**视觉设计提示**：
- 用浅灰色或淡蓝色背景框
- 四个部分用渐进色或编号突出
- 第④部分用更深的颜色或加粗，因为这是关键
- 可以在框的左上角加一个 `</>` 代码图标

---

### 下半部分：多语言文化背景描述示例

#### 🇨🇳 中国 - 双语对照

**中文版本：**
```
您是中国的一位普通民众。

中国是一个有着悠久历史和深厚文化传统的国家，
重视集体主义、家庭观念、尊重权威和社会和谐。
```

**English Version:**
```
You are a typical citizen of China.

China is a country with a long history and deep 
cultural traditions, valuing collectivism, family 
values, respect for authority, and social harmony.
```

---

#### 🇷🇺 俄罗斯 - 俄语版本

**Русский:**
```
Вы обычный гражданин Russia.

Россия - это страна с богатой историей и 
культурными традициями, которая ценит 
коллективизм, семейные ценности, уважение 
к власти и социальную стабильность.
```

**关键词翻译：**
- коллективизм = collectivism (集体主义)
- семейные ценности = family values (家庭价值观)
- уважение к власти = respect for authority (尊重权威)
- социальную стабильность = social stability (社会稳定)

---

#### 🇪🇬 埃及 - 阿拉伯语版本

**العربية (Arabic):**
```
أنت مواطن عادي من Egypt.

مصر بلد له تاريخ عريق وتقاليد ثقافية غنية، 
يقدر الأسرة والمجتمع والتقاليد الدينية 
واحترام السلطة.
```

**关键词翻译：**
- الأسرة = family (家庭)
- المجتمع = community (社区/社会)
- التقاليد الدينية = religious traditions (宗教传统)
- احترام السلطة = respect for authority (尊重权威)

---

#### 🇲🇽 墨西哥 - 拉美西语版本

**Español (Spanish - Latin America):**
```
Usted es un ciudadano común de Mexico.

México es un país con rica historia y tradiciones 
culturales, que valora la familia, la comunidad, 
el respeto y las tradiciones religiosas.
```

**关键词翻译：**
- la familia = family (家庭)
- la comunidad = community (社区)
- el respeto = respect (尊重)
- las tradiciones religiosas = religious traditions (宗教传统)

---

## 🎨 PPT 视觉设计建议

### 配色方案
- **提示词框架**：浅蓝色背景 (#E3F2FD) + 深蓝色文字 (#1565C0)
- **中文**：红色系 (#D32F2F)
- **英文**：蓝色系 (#1976D2)
- **俄语**：蓝白红渐变 (#0D47A1)
- **阿拉伯语**：绿色系 (#388E3C)
- **西班牙语**：黄红色系 (#F57C00)

### 图标使用
- 🎭 = 角色扮演
- 🌍 = 全球/多国
- 💬 = 对话/提示词
- `</>` = 代码/技术实现
- 🇨🇳🇷🇺🇪🇬🇲🇽 = 国旗 emoji

### 字体建议
- **中文**：思源黑体 / 微软雅黑
- **英文**：Roboto / Arial
- **俄语**：保留 Arial / Roboto（支持西里尔字母）
- **阿拉伯语**：Arial / Traditional Arabic
- **西班牙语**：Roboto / Arial

### 排版建议
- 上半部分占 40%
- 下半部分占 55%
- 底部留 5% 放代码来源标注

---

## 📝 演讲说辞（详细版）

### 开场（5秒）
> "那么我们具体是如何让 LLM 扮演不同文化的呢？"

### 主体部分 1 - 提示词结构（30秒）
> "这是我们实际使用的提示词结构，基于 `controlled_multilingual_experiment.py` 代码实现。
> 
> 它包括四个部分：
> 
> **第一层**，明确任务：告诉 LLM 这是一项文化价值观调查。
> 
> **第二层**，设定规则：要求 LLM 根据特定国家的文化价值观回答，而不是用它自己内置的偏好。
> 
> **第三层**，规范格式：因为我们需要自动解析答案，所以要求 LLM 只回答数字。
> 
> **第四层，也是最关键的**——角色定位加文化背景。"

### 主体部分 2 - 文化背景描述（45秒）
> "我们为每个国家精心编写了文化背景描述。
> 
> 比如中国，我们用中文告诉 LLM：'中国重视集体主义、家庭观念、尊重权威和社会和谐'。
> 
> 同样的国家，用英文也描述相同的文化特征。
> 
> 你们看这些例子——
> - 俄语版本强调集体主义和社会稳定
> - 阿拉伯语版本强调宗教传统和社区
> - 西班牙语版本强调家庭和尊重
> 
> 每种语言都用该语言的文化表达方式来描述相同的核心概念。"

### 总结（20秒）
> "**这个设计非常关键**，因为它确保了控制变量原则——
> 
> 同一个国家，文化背景描述的**语义内容完全相同**，只有**语言不同**。
> 
> 所以如果结果有差异，那一定是**语言本身**的影响，而不是我们给的文化信息不同。
> 
> 这就是我们如何严格控制实验条件的。"

**总时长**：约 1 分 40 秒

---

## 📌 关键强调点（用于 PPT 动画或高亮）

1. **第四层是关键** - 可以用动画放大或变色
2. **集体主义、家庭、权威、和谐** - 这些关键词可以高亮
3. **相同语义，不同语言** - 可以用箭头连接中英文版本
4. **控制变量** - 底部用醒目颜色标注

---

## 🔍 代码来源标注

**在 Slide 底部用小字标注：**
```
基于实际代码: src/roleplay_multilingual/controlled_multilingual_experiment.py
提示词模板位于: _load_experiment_config() 方法
```

---

## 📚 完整代码示例（备用，可作为附录 slide）

如果需要展示更技术性的内容，可以准备一张附录 slide：

### 中国中文版完整提示词

```python
system_prompt = """您正在参与一项文化价值观调查。请基于您的文化背景和个人观点提供深思熟虑的回答。

请遵循以下指导原则：
- 根据您的文化价值观和信念，为每个问题提供真诚、经过深思熟虑的回答
- 选择最能反映您文化价值观和信念的选项
- 像来自您国家的真实人士一样回答

回答格式：
- 单选题：仅回答一个数字
- Y002（双选题）：回答两个用空格分隔的数字
- Y003（多选题）：回答1-5个用空格分隔的数字

您是China的一位普通民众。中国是一个有着悠久历史和深厚文化传统的国家，重视集体主义、家庭观念、尊重权威和社会和谐。"""
```

### 对应的英文版

```python
system_prompt = """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal views.

Please follow these guidelines:
- Provide sincere, thoughtful answers to each question based on your cultural values and beliefs
- Choose the option that best reflects your cultural values and beliefs
- Answer as a real person from your country would

Response format:
- Single choice: Answer with only one number
- Y002 (dual choice): Answer with two numbers separated by space
- Y003 (multiple choice): Answer with 1-5 numbers separated by spaces

You are a typical citizen of China. China is a country with a long history and deep cultural traditions, valuing collectivism, family values, respect for authority, and social harmony."""
```

---

## ✅ 检查清单

制作这张 Slide 时确保：

- [ ] 提示词结构清晰展示四层
- [ ] 至少展示 3-4 种语言的文化背景描述
- [ ] 使用国旗 emoji 或图标让视觉更生动
- [ ] 高亮关键文化概念（集体主义、家庭、权威等）
- [ ] 底部标注代码来源
- [ ] 文字大小合适（不要太小）
- [ ] 配色区分不同语言
- [ ] 预留足够演讲时间（1.5-2 分钟）

---

## 🎯 这张 Slide 的作用

1. **增强方法的可信度** - 展示我们的技术实现细节
2. **回答潜在质疑** - "你们怎么让 LLM 扮演不同文化的？"
3. **强调控制变量** - 相同语义，不同语言
4. **为后续结果铺垫** - 既然控制得这么严格，那结果的差异就更有说服力
5. **展示技术能力** - 不只是理论，我们有实际的代码实现

---

**祝汇报成功！** 🎉






