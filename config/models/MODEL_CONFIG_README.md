# 模型配置说明文档

## 概述

本项目支持22个大语言模型的访谈，通过两个API聚合平台访问：
- **OpenKey** (优先): 主要API平台，支持18个模型
- **OpenRouter** (备用): 用于OpenKey不支持的模型（待配置）

## 配置文件

配置文件位置: `config/llm_models.json`

## 已配置模型列表 (18个)

### OpenAI 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| GPT-4o | `gpt-4o` | OpenAI | US |
| GPT-4o-mini | `gpt-4o-mini` | OpenAI | US |
| o1 | `o1` | OpenAI | US |

### Anthropic 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| Claude 3.7 Sonnet | `claude-3-7-sonnet` | Anthropic | US |
| Claude 4.5 Sonnet | `claude-sonnet-4-5` | Anthropic | US |

### Google 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| Gemini 2.0 Flash | `gemini-2.0-flash-exp` | Google | US |
| Gemini 2.0 Flash Thinking | `gemini-2.0-flash-thinking-exp-01-21` | Google | US |
| Gemini Exp 1206 | `gemini-exp-1206` | Google | US |

### Meta 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| Llama 3.3 70B Instruct | `llama-3.3-70b-instruct` | Meta | US |

### xAI 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| Grok Beta | `grok-beta` | xAI | US |

### 深度求索 (DeepSeek) 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| DeepSeek V3 | `deepseek-chat` | DeepSeek | CN |
| DeepSeek V3 0324 | `deepseek-reasoner` | DeepSeek | CN |

### 阿里巴巴 (Alibaba) 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| Qwen-Max | `qwen-max` | Alibaba | CN |
| Qwen QwQ 32B | `qwq-32b-preview` | Alibaba | CN |

### Moonshot 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| Kimi-K2 | `moonshot-v1-128k` | Moonshot | CN |

### 智谱AI (Zhipu) 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| GLM-4+ | `glm-4-plus` | Zhipu | CN |

### Mistral AI 系列
| 显示名称 | API模型ID | 提供商 | 地区 |
|---------|----------|--------|------|
| Mistral Nemo | `mistral-nemo-2407` | Mistral | EU |
| Mistral Large | `mistral-large-2411` | Mistral | EU |

## 待配置模型 (4个)

以下模型在您提供的列表中，但需要确认OpenKey是否支持或需要通过OpenRouter访问：

1. **GPT-5.1** (OpenAI) - 需要确认模型ID
2. **Gemini 2.5 Flash** (Google) - 需要确认模型ID
3. **Gemini 2.5 Pro** (Google) - 需要确认模型ID  
4. **Gemini 3 Pro Preview** (Google) - 需要确认模型ID

> **注意**: 这些模型可能是未来版本或需要特殊访问权限。请确认OpenKey平台是否支持这些模型。

## 环境变量配置

在使用前，需要设置以下环境变量：

```bash
# Windows PowerShell
$env:OPENKEY_API_KEY = "your-openkey-api-key"
$env:OPENROUTER_API_KEY = "your-openrouter-api-key"  # 备用

# Linux/Mac
export OPENKEY_API_KEY="your-openkey-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"  # 备用
```

## 使用方法

### 1. 在代码中使用模型

```python
from src.base.base_interview import BaseInterview

# 使用API模型ID
interview = BaseInterview()
responses = interview.interview_entity("gpt-4o", "China")

# 或使用显示名称（需要通过model_mapping转换）
model_id = interview.model_configs["model_mapping"]["GPT-4o"]
responses = interview.interview_entity(model_id, "China")
```

### 2. 批量访谈多个模型

```python
# 使用API模型ID列表
model_list = [
    "gpt-4o",
    "claude-3-7-sonnet", 
    "gemini-2.0-flash-exp",
    "deepseek-chat"
]

results = interview.batch_interview(model_list, ["China", "USA"])
```

## API平台说明

### OpenKey 平台
- **Base URL**: `https://api.openkey.cloud/v1`
- **兼容性**: OpenAI API格式
- **支持模型**: 18个主流模型
- **优势**: 
  - 统一接口访问多个提供商
  - 国内访问速度快
  - 支持主流中文模型

### OpenRouter 平台 (备用)
- **Base URL**: `https://openrouter.ai/api/v1`
- **用途**: OpenKey不支持的模型
- **状态**: 待配置

## 模型名称映射

配置文件中的 `model_mapping` 字段提供了显示名称到API模型ID的映射：

```json
{
  "model_mapping": {
    "GPT-4o": "gpt-4o",
    "Claude 3.7 Sonnet": "claude-3-7-sonnet",
    ...
  }
}
```

## 配置文件结构

```json
{
  "models": {
    "模型ID": {
      "api_key": "环境变量名",
      "base_url": "API基础URL",
      "provider": "提供商名称",
      "region": "地区代码"
    }
  },
  "model_mapping": {
    "显示名称": "模型ID"
  },
  "notes": {
    "说明信息"
  }
}
```

## 注意事项

1. **模型ID准确性**: 当前配置的模型ID基于常见命名规范，实际使用前请确认OpenKey平台的准确模型ID

2. **API密钥安全**: 
   - 不要将API密钥硬编码在代码中
   - 使用环境变量管理密钥
   - 不要将包含密钥的配置文件提交到Git

3. **速率限制**: 
   - 不同模型有不同的速率限制
   - 建议使用并发控制避免触发限流

4. **成本控制**:
   - 不同模型的定价不同
   - 建议先用小规模测试
   - 监控API使用量

## 下一步工作

- [ ] 确认所有模型在OpenKey平台的准确模型ID
- [ ] 测试每个模型的API调用
- [ ] 配置OpenRouter作为备用平台
- [ ] 添加模型性能和成本对比
- [ ] 实现自动fallback机制（OpenKey失败时切换到OpenRouter）

## 更新日志

- **2024-12-06**: 初始配置，添加18个OpenKey支持的模型
