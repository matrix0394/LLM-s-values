# IVS Questionnaire 移动说明

## 📅 日期
2025年11月1日

## 🎯 移动原因

### 原位置
```
src/llm_values/llm_questionnaire.py  ❌ 不合理
```

### 新位置
```
src/base/ivs_questionnaire.py  ✅ 合理
```

## 📋 为什么要移动？

### 1. **被base模块依赖**
```python
# base_interview.py 第21行
from src.base.ivs_questionnaire import IVSQuestions, LLMResponse, ResponseValidator
```

### 2. **被所有Stage共享**
- Stage0: 真实国家数据（虽然不直接访谈，但使用相同的问题定义）
- Stage1: LLM基础访谈
- Stage2: LLM角色扮演（英语）
- Stage3: LLM角色扮演（多语言）

### 3. **定义核心数据结构**
- `LLMResponse`: 所有访谈响应的标准格式
- `IVSQuestions`: IVS问题定义（从config加载）
- `ResponseValidator`: 统一的回答验证规则

### 4. **不是Stage1特有**
- 问题定义来自标准IVS调查
- 验证规则对所有Stage一致
- 是基础设施，不是业务逻辑

---

## ✅ 已更新的文件

### 核心文件
1. ✅ `src/base/base_interview.py`
2. ✅ `src/llm_values/__init__.py`
3. ✅ `src/llm_values/llm_interview.py`
4. ✅ `src/roleplay_English/llm_country_roleplay_interview.py`
5. ✅ `src/roleplay_multilingual/multilingual_roleplay_interview.py`

### 旧文件（不需要更新）
- `*_old.py` 文件保持原样（待删除）
- 旧路径的导入不影响新架构

---

## 📦 ivs_questionnaire.py 内容

### 1. LLMResponse (数据类)
```python
@dataclass
class LLMResponse:
    model_name: str
    question_id: str
    response: Any          # 处理后的回答
    raw_response: str      # 原始回答
    is_valid: bool         # 是否有效
    error_message: Optional[str] = None
```

**用途**：统一所有访谈的响应格式

### 2. IVSQuestions (问题管理)
```python
class IVSQuestions:
    @classmethod
    def get_question(cls, question_id: str) -> Dict
    
    @classmethod
    def get_all_questions(cls) -> Dict
    
    @classmethod
    def get_question_ids(cls) -> List[str]
```

**特点**：
- 从 `config/ivs_questions.json` 加载
- 懒加载（首次使用时加载）
- 类方法，无需实例化

### 3. ResponseValidator (验证器)
```python
class ResponseValidator:
    @staticmethod
    def validate_response(question_id: str, response: str) 
        -> tuple[bool, Any, str]
```

**验证规则**：
- A008, A165, E018, E025: 单选 1-4
- F063, F118, F120, G006: 单选 1-10
- Y002: 双选 1-6（选2个）
- Y003: 多选 1-11（选1-5个）

---

## 🔗 与config的关系

### 数据来源
```
config/ivs_questions.json  ← 问题定义
    ↓ 被加载
src/base/ivs_questionnaire.py  ← 问题管理和验证
    ↓ 被使用
src/base/base_interview.py  ← 访谈基类
    ↓ 被继承
Stage1/2/3的interview类  ← 具体实现
```

### 标准化流程
1. **问题定义**：config/ivs_questions.json（中心化配置）
2. **问题加载**：ivs_questionnaire.IVSQuestions
3. **回答验证**：ivs_questionnaire.ResponseValidator
4. **访谈实现**：base_interview.BaseInterview
5. **业务逻辑**：各stage的interview子类

---

## 📊 数据格式一致性

### Stage0 (Country Values)
```python
# 数据来源：IVS原始数据
# 格式：直接使用IVS的标准问题ID
ivs_df[['A008', 'A165', 'E018', ...]]  # 10个问题
```

### Stage1-3 (LLM)
```python
# 数据来源：LLM访谈
# 格式：使用相同的问题ID和验证规则
LLMResponse(
    question_id='A008',    # 与IVS一致
    response=2,            # 验证规则与IVS一致
    ...
)
```

### 关键点
✅ **所有Stage使用相同的10个问题ID**
✅ **所有Stage使用相同的验证规则**
✅ **所有Stage生成的数据格式一致**

---

## 🎯 下一步

### 继续审查Stage1
1. ✅ ivs_questionnaire.py 已移到base
2. ⏭️ llm_interview.py - 检查访谈逻辑
3. ⏭️ llm_data_processor.py - 检查数据处理
4. ⏭️ llm_pca_analysis.py - 检查PCA分析
5. ⏭️ llm_visualization.py - 检查可视化

### 确保一致性
- 数据保存格式一致
- 数据读取格式一致
- 计算方式一致（使用BasePCAAnalyzer）
- 可视化方案一致（使用BaseCulturalMapVisualizer）

---

## 💡 架构改进

### 改进前
```
src/llm_values/llm_questionnaire.py  
    ↑ 被base依赖（循环依赖风险）
src/base/base_interview.py
```

### 改进后
```
src/base/ivs_questionnaire.py  
    ↓ 被使用
src/base/base_interview.py
    ↓ 被继承
Stage1/2/3的interview类
```

**优势**：
- ✅ 依赖关系清晰（base不依赖stage）
- ✅ 共享代码在base（DRY原则）
- ✅ 易于维护和扩展

---

**ivs_questionnaire.py 移动完成！** 🎉
































