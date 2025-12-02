# 统一数据格式规范 (Unified Data Format Standard)

## 📋 概述

本文档定义了三个研究阶段（Stage 1/2/3）的统一数据格式标准，确保数据互用性和一致性。

---

## 🎯 设计原则

1. **一致性**: 所有阶段使用相同的数据结构
2. **可扩展性**: 支持未来添加新字段
3. **向后兼容**: 保留旧数据的读取能力
4. **分层清晰**: 明确区分原始数据、处理数据、PCA结果

---

## 📦 数据层级结构

```
访谈数据
├── 原始访谈数据 (Raw Interview Data)
│   └── 每个模型-实体组合的问答记录
├── 处理后数据 (Processed Data)
│   └── 转换为IVS兼容格式的宽表数据
└── PCA分析结果 (PCA Results)
    └── 包含主成分坐标的实体分数
```

---

## 1️⃣ 原始访谈数据格式 (Raw Interview Data)

### 文件命名规范

```
{stage_name}_interview_raw_{timestamp}.pkl
{stage_name}_interview_raw_{timestamp}.json
```

**示例**:
- `llm_values_interview_raw_20241030_120000.pkl`
- `roleplay_english_interview_raw_20241030_120000.pkl`
- `roleplay_multilingual_interview_raw_20241030_120000.pkl`

### 数据结构

```python
{
    "metadata": {
        "stage": "stage1|stage2|stage3",  # 阶段标识
        "timestamp": "20241030_120000",
        "version": "1.0",
        "consensus_count": 5,  # 每个问题重复次数
        "total_entities": 7,  # 总实体数（Stage1是模型，Stage2/3是模型×国家）
        "total_questions": 10,  # 问题数
        "total_api_calls": 350  # 总API调用次数
    },
    "results": [
        {
            # 实体标识 (Entity Identification)
            "entity_id": "unique_identifier",  # 唯一标识
            "entity_type": "llm|roleplay_english|roleplay_multilingual",
            
            # Stage 1 特有字段
            "model_name": "openai/gpt-4o-mini",  # 模型名称
            "model_region": "US",  # 模型区域
            
            # Stage 2 特有字段
            "country_name": "China",  # 国家名称 (Stage 2/3)
            "country_code": "CN",  # 国家代码 (Stage 2/3)
            "cultural_region": "Confucian",  # 文化区域 (Stage 2/3)
            
            # Stage 3 特有字段
            "language": "zh-cn",  # 语言 (Stage 3)
            "language_family": "Sino-Tibetan",  # 语系 (Stage 3)
            
            # 访谈信息
            "timestamp": "2024-10-30T12:00:00",
            "total_questions": 10,
            "valid_responses": 9,
            "success_rate": 90.0,
            
            # 问答详情
            "responses": [
                {
                    "question_id": "A008",
                    "question_text": "...",  # 可选：问题文本
                    "raw_response": "2",
                    "processed_response": 2,
                    "is_valid": true,
                    "error_message": null,
                    "attempt_count": 1,  # 重试次数
                    "response_time": 1.23  # 响应时间(秒)
                },
                # ... 其他问题
            ]
        },
        # ... 其他实体
    ]
}
```

---

## 2️⃣ 处理后数据格式 (Processed Data)

### 文件命名规范

```
{stage_name}_processed_{timestamp}.pkl
{stage_name}_processed_{timestamp}.csv
```

### 数据结构 (DataFrame)

每行代表一个实体，列包括：

#### 通用列 (All Stages)

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `entity_id` | str | 唯一实体ID | `llm_openai-gpt-4o-mini` |
| `entity_type` | str | 实体类型 | `llm\|roleplay_english\|roleplay_multilingual` |
| `data_source` | str | 数据来源 | `LLM\|llm_roleplay\|IVS` |
| `stage` | str | 研究阶段 | `stage1\|stage2\|stage3` |
| `timestamp` | str | 时间戳 | `2024-10-30T12:00:00` |

#### Stage 1 特有列

| 列名 | 类型 | 说明 |
|------|------|------|
| `model_name` | str | 模型名称 |
| `model_region` | str | 模型区域 (US/CN/EU) |
| `model_company` | str | 模型公司 |

#### Stage 2 特有列

| 列名 | 类型 | 说明 |
|------|------|------|
| `model_name` | str | 模型名称 |
| `model_region` | str | 模型区域 |
| `country_name` | str | 国家名称 |
| `country_code` | str | ISO国家代码 |
| `cultural_region` | str | 文化区域 |

#### Stage 3 特有列

| 列名 | 类型 | 说明 |
|------|------|------|
| `model_name` | str | 模型名称 |
| `model_region` | str | 模型区域 |
| `country_name` | str | 国家名称 |
| `country_code` | str | ISO国家代码 |
| `language` | str | 语言代码 |
| `language_family` | str | 语系 |
| `cultural_region` | str | 文化区域 |

#### IVS问题列 (All Stages)

| 列名 | 类型 | 说明 |
|------|------|------|
| `A008` | int | 宗教重要性 (1-4) |
| `A165` | int | 家庭重要性 (1-4) |
| `E018` | int | 工作重要性 (1-4) |
| `E025` | int | 闲暇重要性 (1-4) |
| `F063` | int | 自主性 vs 服从 (1-3) |
| `F118` | int | 想象力 vs 礼貌 (1-2) |
| `F120` | int | 独立性 vs 勤奋 (1-2) |
| `G006` | int | 性别平等 (1-10) |
| `Y002_materialist` | int | 物质主义倾向 (0-2) |
| `Y003_1` ~ `Y003_11` | int | Y003各选项 (0/1) |

---

## 3️⃣ PCA结果格式 (PCA Results)

### 文件命名规范

```
{stage_name}_pca_results_{timestamp}.pkl
{stage_name}_pca_results_{timestamp}.csv
```

### 数据结构 (DataFrame)

继承处理后数据的所有列，额外添加：

| 列名 | 类型 | 说明 |
|------|------|------|
| `PC1` | float | 主成分1原始分数 |
| `PC2` | float | 主成分2原始分数 |
| `PC1_rescaled` | float | PC1重标定到[-100, 100] |
| `PC2_rescaled` | float | PC2重标定到[-100, 100] |
| `PC1_variance` | float | PC1解释方差比例 |
| `PC2_variance` | float | PC2解释方差比例 |
| `pca_method` | str | PCA方法 | `inglehart\|custom` |

---

## 🔧 实现指南

### 保存函数标准接口

```python
def save_interview_results(
    results: Dict,
    stage: str,  # "stage1", "stage2", "stage3"
    output_dir: Path,
    format: str = "both"  # "pkl", "json", "both"
) -> Dict[str, Path]:
    """
    保存访谈结果的统一接口
    
    Returns:
        {
            "pkl": Path,
            "json": Path
        }
    """
    pass

def save_processed_data(
    data: pd.DataFrame,
    stage: str,
    output_dir: Path,
    format: str = "both"  # "pkl", "csv", "both"
) -> Dict[str, Path]:
    """
    保存处理后数据的统一接口
    """
    pass

def save_pca_results(
    data: pd.DataFrame,
    stage: str,
    output_dir: Path,
    format: str = "both"
) -> Dict[str, Path]:
    """
    保存PCA结果的统一接口
    """
    pass
```

### 数据验证

```python
def validate_raw_interview_data(data: Dict) -> bool:
    """验证原始访谈数据格式"""
    required_fields = ["metadata", "results"]
    required_metadata = ["stage", "timestamp", "version"]
    # ...
    
def validate_processed_data(df: pd.DataFrame, stage: str) -> bool:
    """验证处理后数据格式"""
    common_cols = ["entity_id", "entity_type", "data_source", "stage"]
    ivs_cols = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006"]
    # ...
    
def validate_pca_results(df: pd.DataFrame) -> bool:
    """验证PCA结果格式"""
    required_cols = ["PC1", "PC2", "PC1_rescaled", "PC2_rescaled"]
    # ...
```

---

## 📂 目录结构

```
data/
├── llm_values/                   # Stage 1
│   ├── interview_raw/
│   │   ├── llm_values_interview_raw_20241030_120000.pkl
│   │   └── llm_values_interview_raw_20241030_120000.json
│   ├── processed/
│   │   ├── llm_values_processed_20241030_120000.pkl
│   │   └── llm_values_processed_20241030_120000.csv
│   └── pca_results/
│       ├── llm_values_pca_results_20241030_120000.pkl
│       └── llm_values_pca_results_20241030_120000.csv
│
├── roleplay_English/              # Stage 2
│   ├── interview_raw/
│   ├── processed/
│   └── pca_results/
│
└── roleplay_multilingual/         # Stage 3
    ├── interview_raw/
    ├── processed/
    └── pca_results/
```

---

## 🔄 迁移计划

### 阶段1: 创建统一工具
- [ ] 创建 `src/core/unified_data_manager.py`
- [ ] 实现保存、加载、验证函数

### 阶段2: 适配各Stage
- [ ] 修改Stage 1访谈类
- [ ] 修改Stage 2访谈类
- [ ] 修改Stage 3访谈类

### 阶段3: 测试验证
- [ ] 单元测试
- [ ] 集成测试
- [ ] 数据迁移脚本

---

## ✅ 兼容性保证

1. **读取旧格式**: 保留旧格式的读取函数
2. **自动转换**: 提供旧→新格式转换工具
3. **版本标记**: 所有数据包含version字段

---

## 📝 变更日志

- **v1.0** (2024-10-30): 初始版本，定义统一格式标准






