# Requirements Document

## Introduction

本功能旨在扩展Stage 1（LLM原生价值观访谈）的能力，使其支持使用联合国6种官方语言（英语、法语、西班牙语、俄语、阿拉伯语、中文）对所有配置的LLM模型进行访谈。这将帮助研究人员分析不同语言提问对LLM价值观表达的影响，揭示语言对模型价值观的潜在影响。

## Glossary

- **Stage 1**: LLM原生价值观访谈阶段，直接向模型提问IVS问题，不进行角色扮演
- **IVS**: Integrated Values Survey，综合价值观调查问卷
- **UN Official Languages**: 联合国6种官方语言：英语(en)、法语(fr)、西班牙语(es)、俄语(ru)、阿拉伯语(ar)、中文(zh-cn)
- **Multilingual Questions Config**: 存储在`config/multilingual_questions_complete.json`中的多语言问题配置
- **LLM Interview**: 对大语言模型进行的价值观访谈
- **Consensus Count**: 每个问题重复访谈的次数，用于取众数以提高结果稳定性
- **PCA Analysis**: 主成分分析，用于将访谈结果映射到文化价值观坐标系

## Requirements

### Requirement 1

**User Story:** As a researcher, I want to interview LLM models using UN official languages, so that I can analyze how different languages affect the expression of model values.

#### Acceptance Criteria

1. WHEN a user initiates a Stage 1 multilingual interview THEN the System SHALL load questions from the multilingual questions configuration file for all 6 UN official languages (en, fr, es, ru, ar, zh-cn)
2. WHEN the System conducts an interview in a specific language THEN the System SHALL use the corresponding language's question text from the configuration
3. WHEN the System interviews a model THEN the System SHALL use a language-appropriate system prompt that instructs the model to respond with numbers only
4. WHEN the System completes interviews for all languages THEN the System SHALL save results with clear language identifiers for each response set

### Requirement 2

**User Story:** As a researcher, I want to run multilingual interviews for all configured models, so that I can compare value expressions across different models and languages.

#### Acceptance Criteria

1. WHEN a user starts a batch multilingual interview THEN the System SHALL iterate through all models defined in the model configuration file
2. WHEN the System interviews each model THEN the System SHALL conduct separate interviews for each of the 6 UN official languages
3. WHEN the System encounters an API error during interview THEN the System SHALL retry up to the configured maximum retry count before marking the question as failed
4. WHEN the System completes a model-language combination THEN the System SHALL save the individual result immediately to prevent data loss

### Requirement 3

**User Story:** As a researcher, I want to use consensus-based responses for reliability, so that I can obtain stable and reproducible results.

#### Acceptance Criteria

1. WHEN the consensus count is greater than 1 THEN the System SHALL repeat the complete questionnaire for the specified number of rounds
2. WHEN multiple rounds are completed THEN the System SHALL calculate the mode (most frequent response) for each question
3. WHEN calculating the mode THEN the System SHALL compute and record the consistency rate (confidence) for each question
4. WHEN the System saves results THEN the System SHALL include both the final consensus response and all intermediate round data

### Requirement 4

**User Story:** As a researcher, I want to process and analyze the multilingual interview results, so that I can visualize and compare model values across languages.

#### Acceptance Criteria

1. WHEN the System processes raw interview data THEN the System SHALL convert responses to IVS-compatible format for PCA analysis
2. WHEN the System performs PCA analysis THEN the System SHALL generate cultural coordinates (Traditional-Secular and Survival-Expression dimensions) for each model-language combination
3. WHEN the System generates output THEN the System SHALL create both JSON and pickle format files for compatibility with existing analysis pipelines
4. WHEN the System completes analysis THEN the System SHALL produce a summary report showing value differences across languages for each model

### Requirement 5

**User Story:** As a researcher, I want to resume interrupted interviews, so that I can continue from where I left off without losing progress.

#### Acceptance Criteria

1. WHEN a user starts an interview with skip_existing enabled THEN the System SHALL scan for previously completed model-language combinations
2. WHEN previously completed data is found THEN the System SHALL skip those combinations and only interview remaining ones
3. WHEN the System merges new and existing data THEN the System SHALL produce a unified result set without duplicates
4. WHEN the System saves incremental results THEN the System SHALL use timestamped filenames to prevent overwriting previous data
