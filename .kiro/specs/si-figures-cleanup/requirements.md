# Requirements Document

## Introduction

本项目旨在整理SI/figures目录中的图片，删除重复和无用的图片，确保所有S3之后的分析图表都有对应的生成脚本，并重新生成所有图表以确保数据时效性。研究主题是多语言大模型文化价值观模仿效果分析。

## Glossary

- **SI**: Supporting Information，论文附录材料
- **IVS/WVS**: Integrated Values Survey / World Values Survey，世界价值观调查
- **PCA**: Principal Component Analysis，主成分分析
- **Cultural Distance**: 文化距离，LLM模仿结果与真实IVS坐标的欧氏距离
- **English Advantage**: 英语优势，使用英语vs母语进行角色扮演时的文化距离差异
- **Orientalism**: 东方主义/他者理论，西方视角对非西方文化的刻板印象
- **Roleplay**: 角色扮演，让LLM模仿特定国家公民回答价值观问卷

## Requirements

### Requirement 1: 图片清单审计

**User Story:** As a researcher, I want to audit all SI figures to identify duplicates and obsolete files, so that I can maintain a clean and organized figure repository.

#### Acceptance Criteria

1. WHEN the system scans SI/figures directory THEN the SI_Figure_Cleanup_System SHALL generate a complete inventory of all figure files with their metadata (size, date, path)
2. WHEN comparing figures across directories THEN the SI_Figure_Cleanup_System SHALL identify duplicate figures based on content similarity or naming patterns
3. WHEN analyzing figure relevance THEN the SI_Figure_Cleanup_System SHALL flag figures that are not referenced in any documentation or have outdated data sources
4. WHEN the audit completes THEN the SI_Figure_Cleanup_System SHALL produce a report categorizing figures as: essential, redundant, or obsolete

### Requirement 2: 脚本-图片映射

**User Story:** As a developer, I want to map each SI figure to its generation script, so that I can regenerate any figure when needed.

#### Acceptance Criteria

1. WHEN analyzing S4-S8 figures THEN the SI_Figure_Cleanup_System SHALL identify the corresponding generation script for each figure
2. WHEN a figure lacks a generation script THEN the SI_Figure_Cleanup_System SHALL flag it for manual review or script creation
3. WHEN organizing scripts THEN the SI_Figure_Cleanup_System SHALL consolidate all SI figure generation scripts into analysis/si/ directory
4. WHEN documenting mappings THEN the SI_Figure_Cleanup_System SHALL create a script-to-figure mapping table in SI/figures/README.md

### Requirement 3: 冗余图片识别与删除

**User Story:** As a researcher, I want to remove redundant figures that duplicate information, so that the SI is concise and focused.

#### Acceptance Criteria

1. WHEN S8B (heatmap_model_language) duplicates Sx3 content THEN the SI_Figure_Cleanup_System SHALL mark S8B for removal
2. WHEN S7 contains three East Asia figures (S7A, S7B, S7C) THEN the SI_Figure_Cleanup_System SHALL retain all three figures as they serve different analytical purposes
3. WHEN S8D (consistency_distribution) overlaps with Sx6 THEN the SI_Figure_Cleanup_System SHALL mark S8D for removal
4. WHEN S7 contains 3 East Asia figures THEN the SI_Figure_Cleanup_System SHALL retain all 3 figures (S7A, S7B, S7C)
5. WHEN removing figures THEN the SI_Figure_Cleanup_System SHALL update all documentation references accordingly

### Requirement 4: 图片重新生成

**User Story:** As a researcher, I want to regenerate all analysis figures (S4-S8) using the latest data, so that the SI reflects current research findings.

#### Acceptance Criteria

1. WHEN regenerating S4 figures THEN the SI_Figure_Cleanup_System SHALL use generate_modal_profile_figures.py with latest roleplay data
2. WHEN regenerating S5 figures THEN the SI_Figure_Cleanup_System SHALL use generate_publication_figures.py with updated cultural_distance_analysis.csv
3. WHEN regenerating S6 figures THEN the SI_Figure_Cleanup_System SHALL use visualize_orientalism.py with latest stage0_vs_stage3 results
4. WHEN regenerating S7 figures THEN the SI_Figure_Cleanup_System SHALL use visualize_orientalism.py focusing on East Asia gradient
5. WHEN regenerating S8 figures THEN the SI_Figure_Cleanup_System SHALL use generate_publication_figures.py for model analysis
6. WHEN regenerating summary figures THEN the SI_Figure_Cleanup_System SHALL use scripts/generate_si_figures.py for Sx1-Sx6

### Requirement 5: 脚本整合与标准化

**User Story:** As a developer, I want all SI figure generation scripts organized in analysis/si/, so that figure generation is centralized and maintainable.

#### Acceptance Criteria

1. WHEN a generation script exists outside analysis/si/ THEN the SI_Figure_Cleanup_System SHALL migrate or create a wrapper in analysis/si/
2. WHEN scripts use different style configurations THEN the SI_Figure_Cleanup_System SHALL ensure all scripts import from si_config.py
3. WHEN scripts output figures THEN the SI_Figure_Cleanup_System SHALL ensure consistent output paths to SI/figures/
4. WHEN scripts are organized THEN the SI_Figure_Cleanup_System SHALL follow naming convention: generate_figs{section}_{subsection}.py

### Requirement 6: 数据时效性验证

**User Story:** As a researcher, I want to verify that all figures use the latest data sources, so that the SI accurately represents current findings.

#### Acceptance Criteria

1. WHEN checking data sources THEN the SI_Figure_Cleanup_System SHALL verify Table_S5, S6, S7 PCA coordinates are from 2026-01-03 or later
2. WHEN checking analysis data THEN the SI_Figure_Cleanup_System SHALL verify cultural_distance_analysis.csv is regenerated if PCA data changed
3. WHEN checking stage0_vs_stage3 results THEN the SI_Figure_Cleanup_System SHALL verify distances_detailed.csv uses latest PCA coordinates
4. WHEN data is outdated THEN the SI_Figure_Cleanup_System SHALL trigger regeneration of dependent figures

### Requirement 7: 文档更新

**User Story:** As a researcher, I want updated documentation reflecting the final SI figure structure, so that the repository is well-documented.

#### Acceptance Criteria

1. WHEN figures are reorganized THEN the SI_Figure_Cleanup_System SHALL update SI/figures/README.md with current structure
2. WHEN scripts are consolidated THEN the SI_Figure_Cleanup_System SHALL update script-to-figure mapping table
3. WHEN redundant figures are removed THEN the SI_Figure_Cleanup_System SHALL update PNAS_RECOMMENDED_FIGURES.md
4. WHEN cleanup completes THEN the SI_Figure_Cleanup_System SHALL update PNAS_SI_FINAL_STRUCTURE.md with final counts
