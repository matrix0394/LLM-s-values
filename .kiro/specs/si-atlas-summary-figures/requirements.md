# Requirements Document

## Introduction

This feature establishes a unified visual style system for ALL figure generation scripts in the project (both `figures/` and `SI/figures/` directories), then generates comprehensive Supporting Information (SI) materials including Atlas compilations and summary figures. The style system ensures color consistency, minimal labeling, unified legends, and cross-figure comparability across all 1,900+ cultural map visualizations. The Atlas provides auditable access to all individual figures, while summary figures provide statistical overviews.

## Glossary

- **Atlas**: A multi-page PDF document containing batch-assembled individual figures in a grid layout (3×3 per page)
- **Entity Score**: PCA-derived coordinates (PC1, PC2) representing cultural value positions for model-country-language combinations
- **Consistency Rate**: The proportion of survey responses where the modal answer was consistent across 5 repeated trials
- **IVS**: Integrated Values Survey - the reference dataset for cultural value positions
- **Cultural Map**: A 2D scatter plot showing PC1 (Survival vs Self-Expression) and PC2 (Traditional vs Secular-Rational) coordinates
- **Variance Decomposition**: Statistical analysis showing the relative contribution of model, country, and language factors to observed variance
- **Cultural Zone**: One of 9 IVS-defined cultural regions (e.g., Confucian, Protestant Europe, Latin America)
- **Color-blind Safe**: Color palettes that remain distinguishable for individuals with color vision deficiencies
- **Foreground Points**: LLM-generated data points (models, languages) displayed prominently in cultural maps
- **Background Points**: IVS reference country points displayed with low opacity for context
- **Atlas Panel**: A single cultural map figure within the 3×3 grid of an Atlas page
- **Focal Object**: The primary entity being highlighted in a panel (target country, language, or model)
- **Top-K Extreme Points**: The K points with highest/lowest values on a metric (e.g., distance from origin, distance from focal object)
- **Vendor Color Family**: A color hue assigned to all models from the same vendor (e.g., OpenAI=blue family, Anthropic=purple family)
- **Single Color Channel**: Using color to encode only one dimension (model OR language OR zone) per panel, not multiple simultaneously
- **Template Function**: A standardized plotting function for a specific panel type (focus_country, focus_language, focus_model)

## Requirements

### Requirement 1

**User Story:** As a reviewer, I want to access all individual cultural map figures in a structured Atlas format, so that I can audit any specific model-country-language combination without searching through thousands of files.

#### Acceptance Criteria

1. WHEN the Atlas generator processes a figure directory THEN the System SHALL create a PDF with figures arranged in a 3×3 grid layout
2. WHEN generating each Atlas page THEN the System SHALL include a page header showing "{AtlasName} - Page {x} / {N}"
3. WHEN placing each figure in the grid THEN the System SHALL add a label below showing the parsed model/country/language from the filename
4. WHEN the total page count exceeds 50 pages THEN the System SHALL split the output into multiple PDF parts (part01, part02, etc.)
5. WHEN processing the A1_per_model_language_stability directory THEN the System SHALL generate FigS2A1_Atlas.pdf containing all 23 figures
6. WHEN processing the B3_per_model_per_country directory THEN the System SHALL generate FigS3B3_Atlas.pdf containing all 1,386 figures
7. WHEN processing the B4_per_country_per_language directory THEN the System SHALL generate FigS3B4_Atlas.pdf containing all 122 figures
8. WHEN processing the B5_per_model_per_language directory THEN the System SHALL generate FigS3B5_Atlas.pdf containing all 294 figures

### Requirement 2

**User Story:** As a researcher, I want a searchable index table for all Atlas figures, so that I can quickly locate specific figures by model, country, or language.

#### Acceptance Criteria

1. WHEN generating the Atlas THEN the System SHALL create an atlas_index.csv file with columns: atlas, page, row, col, model, country, language, filename
2. WHEN parsing figure filenames THEN the System SHALL extract model, country, and language identifiers using consistent parsing rules
3. WHEN the index is complete THEN the System SHALL include entity_score values (PC1, PC2) if available from the PCA data tables
4. WHEN generating the index THEN the System SHALL create a README.md explaining how to use the index for navigation

### Requirement 3

**User Story:** As a reader, I want summary heatmap visualizations showing model-country-language relationships, so that I can understand the overall patterns without examining individual figures.

#### Acceptance Criteria

1. WHEN generating the model×country heatmap THEN the System SHALL create a 21×66 matrix visualization with hierarchical clustering
2. WHEN generating the country×language heatmap THEN the System SHALL show all country-language combinations with consistent color scaling
3. WHEN generating the model×language heatmap THEN the System SHALL show all model-language combinations with consistent color scaling
4. WHEN rendering any heatmap THEN the System SHALL use a unified colormap and color bar range across all heatmaps
5. WHEN rendering any heatmap THEN the System SHALL include a clear, concise title describing the content

### Requirement 4

**User Story:** As a statistician, I want to see variance decomposition analysis, so that I can understand the relative contributions of model, country, and language factors.

#### Acceptance Criteria

1. WHEN generating the variance decomposition figure THEN the System SHALL show a bar chart with model, country, and language contribution percentages
2. WHEN calculating variance contributions THEN the System SHALL use the entity_score (PC1, PC2) data from the PCA tables
3. WHEN rendering the bar chart THEN the System SHALL include error bars or confidence intervals if calculable

### Requirement 5

**User Story:** As an analyst, I want to see top/bottom country rankings per model, so that I can identify which countries each model represents best and worst.

#### Acceptance Criteria

1. WHEN generating the ranking figure THEN the System SHALL create small multiples showing top 5 and bottom 5 countries for each model
2. WHEN ranking countries THEN the System SHALL use cultural distance from IVS reference as the ranking metric
3. WHEN rendering the small multiples THEN the System SHALL maintain consistent axis scales across all panels

### Requirement 6

**User Story:** As a researcher, I want to see the relationship between entity scores and consistency, so that I can understand if model reliability correlates with cultural positioning.

#### Acceptance Criteria

1. WHEN generating the scatter plot THEN the System SHALL plot entity_score (or cultural distance) against consistency rate
2. WHEN rendering the scatter plot THEN the System SHALL include a regression line with R² value
3. WHEN rendering the scatter plot THEN the System SHALL use consistent point styling and include a legend

### Requirement 7

**User Story:** As a publication author, I want caption drafts for all summary figures, so that I can quickly prepare the SI documentation.

#### Acceptance Criteria

1. WHEN generating each summary figure THEN the System SHALL write a 1-2 sentence caption draft to the README.md
2. WHEN writing captions THEN the System SHALL include the figure identifier (Fig Sx1, Sx2, etc.) and a brief description
3. WHEN all figures are complete THEN the System SHALL compile all captions into SI/figures/summary/README.md

### Requirement 8

**User Story:** As a developer, I want the Atlas and summary figure generators to be robust and handle missing data gracefully, so that partial data does not cause failures.

#### Acceptance Criteria

1. WHEN a figure file is missing or corrupted THEN the System SHALL skip that figure and log a warning
2. WHEN entity_score data is unavailable for a combination THEN the System SHALL use NaN and indicate missing data in visualizations
3. WHEN processing is complete THEN the System SHALL report a summary of processed vs skipped items

### Requirement 9

**User Story:** As a publication author, I want all figures across the entire project to follow a unified visual style with consistent colors and formatting, so that the paper and Supporting Information appear professional and cohesive.

#### Acceptance Criteria

1. WHEN the System initializes THEN the System SHALL load color mappings from figures/style/colors.json for cultural zones, languages, and models
2. WHEN generating any figure in figures/ or SI/figures/ THEN the System SHALL apply colors from the global color dictionary and SHALL NOT use hardcoded colors in scripts
3. WHEN generating any figure THEN the System SHALL apply the matplotlib style from figures/style/paper.mplstyle
4. WHEN assigning colors to cultural zones THEN the System SHALL use exactly 9 color-blind safe colors that remain distinguishable in protanopia (ΔE ≥ 10), deuteranopia (ΔE ≥ 7), and tritanopia (ΔE ≥ 7.5) simulations
5. WHEN assigning colors to languages THEN the System SHALL use exactly 13 color-blind safe colors that remain distinguishable in protanopia (ΔE ≥ 8), deuteranopia (ΔE ≥ 6), and tritanopia (ΔE ≥ 6) simulations
6. WHEN assigning colors to models from different vendor families THEN the System SHALL ensure cross-vendor colors remain distinguishable in protanopia (ΔE ≥ 2.5) and deuteranopia (ΔE ≥ 6) simulations, and models from the same vendor family MAY use similar colors with different brightness levels
7. WHEN the System completes initialization THEN the System SHALL verify no hardcoded color values exist in any script (except gray for grid/axis lines)

### Requirement 10

**User Story:** As a reviewer examining atlas panels, I want minimal labeling that highlights only focal objects, so that I can quickly identify key entities without visual clutter obscuring the data points.

#### Acceptance Criteria

1. WHEN rendering IVS background points THEN the System SHALL set alpha transparency to 0.15 or less and SHALL NOT label country names by default
2. WHEN rendering focal objects (target country, language, or model) THEN the System SHALL use distinctive markers (stars for countries) and SHALL label only the focal object
3. WHEN a panel contains more than 10 foreground points THEN the System SHALL label at most the Top-K extreme points (configurable, default K=5) plus the focal object
4. WHEN applying text labels THEN the System SHALL use adjustText or equivalent repel algorithm ONLY on the subset of points requiring labels
5. WHEN generating FigS1 IVS reference map THEN the System SHALL output a single full-page PDF with 10-15 representative country labels, not a 3×3 atlas panel
6. WHEN generating atlas panels (S2-A1, S2-A2, S3-B1 through B5) THEN the System SHALL NOT place complete legends inside panels
7. WHEN generating atlas panels THEN the System SHALL use short-format titles: "{model_short} | {country_short} | {lang_short}" with maximum 40 characters total

### Requirement 11

**User Story:** As a reader of the atlas PDF, I want a unified legend on the cover page or page footer, so that I can understand color meanings without legends cluttering every individual panel.

#### Acceptance Criteria

1. WHEN generating an atlas PDF THEN the System SHALL create a cover page (page 0) before the first 3×3 grid page
2. WHEN creating the atlas cover page THEN the System SHALL display the atlas title, total figure count, and complete color legends for cultural zones, languages, and models
3. WHEN creating the atlas cover page THEN the System SHALL explain the labeling policy: "Atlas panels show minimal labels; use atlas_index.csv for complete entity identification"
4. WHEN generating atlas grid pages (pages 1+) THEN the System SHALL NOT include legends within individual panels
5. WHERE an atlas has multiple parts THEN each part SHALL include its own cover page with the same legend information

### Requirement 12

**User Story:** As a data analyst, I want the atlas_index.csv to include source table row identifiers, so that I can trace any figure back to its exact source data row for auditability.

#### Acceptance Criteria

1. WHEN creating atlas_index.csv entries THEN the System SHALL include a column "source_table_row_id" linking to the row in Table_S7_LLM_roleplay_PCA_coordinates.csv
2. WHEN a figure corresponds to multiple source rows (aggregated data) THEN the System SHALL store a semicolon-separated list of row IDs
3. WHEN source row ID cannot be determined THEN the System SHALL use "N/A" in the source_table_row_id column

### Requirement 13

**User Story:** As a publication author, I want the README.md to accurately describe the color-blind safe and grayscale-robust design, so that reviewers understand the accessibility considerations.

#### Acceptance Criteria

1. WHEN updating SI/figures/README.md THEN the System SHALL replace "black-white print compatible" with "color-blind safe + grayscale-robust (shape/edge differentiation)"
2. WHEN updating SI/figures/README.md THEN the System SHALL replace "Point Density ≤ 50" with "Foreground (LLM) ≤ 50; IVS background shown with transparency ≤ 0.15"
3. WHEN updating SI/figures/README.md THEN the System SHALL add a section "Labeling Policy" explaining that atlas panels use minimal labels and readers should use atlas_index.csv for entity identification
4. WHEN updating SI/figures/README.md THEN the System SHALL add a section "Color System" explaining the three color dictionaries (cultural zones, languages, models) and their design rationale

### Requirement 14

**User Story:** As a developer, I want standardized template functions for the three S3 panel types, so that I can generate consistent cultural maps without ad-hoc if-else logic.

#### Acceptance Criteria

1. WHEN generating a country-focused panel THEN the System SHALL use plot_focus_country(model, country, language) which displays IVS background, target country as star with black edge, and model point in model_color
2. WHEN generating a language-focused panel THEN the System SHALL use plot_focus_language(country, language) which displays IVS background, focal language as square in language_color, and optionally other languages in lighter shades
3. WHEN generating a model-focused panel THEN the System SHALL use plot_focus_model(model, language) which displays IVS background, all country points for that model-language in model_color, and optional gray connection lines with alpha 0.3
4. WHEN any template function renders a panel THEN the System SHALL use color to encode only ONE dimension (model OR language OR zone) per panel
5. WHEN any template function labels points THEN the System SHALL label only the focal object plus Top-K extreme points (default K=3 or K=5)

### Requirement 15

**User Story:** As a reviewer, I want S2 baseline figures to use color semantically and consistently, so that I can interpret the visual encoding without confusion.

#### Acceptance Criteria

1. WHEN S2 figures use color to encode language THEN the System SHALL use language_colors for all language points and SHALL NOT use color for any other dimension
2. WHEN S2 figures use color to encode model THEN the System SHALL use model_colors for all model points and SHALL NOT use color for any other dimension
3. WHEN S2 figures need to encode two dimensions THEN the System SHALL use color for one dimension and marker shape for the other (e.g., language=square, model=circle)
4. WHEN S2 figures display multiple models or languages THEN the System SHALL include a legend explaining the color-to-entity mapping

### Requirement 16

**User Story:** As a reviewer, I want summary heatmaps to include both PC1 and PC2 analyses, so that I can verify the analysis does not ignore the second principal component.

#### Acceptance Criteria

1. WHEN generating model×country heatmap THEN the System SHALL generate both FigSx1_PC1 and FigSx1_PC2 versions with identical layout
2. WHEN generating country×language heatmap THEN the System SHALL generate both FigSx2_PC1 and FigSx2_PC2 versions with identical layout
3. WHEN generating model×language heatmap THEN the System SHALL generate both FigSx3_PC1 and FigSx3_PC2 versions with identical layout
4. WHEN generating distance-based heatmaps THEN the System SHALL provide a 2D Euclidean distance version combining PC1 and PC2
5. WHEN generating score vs consistency scatter THEN the System SHALL provide both 1D (cultural distance) and 2D (PC1, PC2 separately) versions

### Requirement 17

**User Story:** As a quality assurance engineer, I want automated validation of all generated figures, so that style violations are caught before publication.

#### Acceptance Criteria

1. WHEN the System completes figure generation THEN the System SHALL run validate_figures.py to check all outputs
2. WHEN validate_figures.py runs THEN the System SHALL verify all colors come from StyleManager (no hardcoded values except gray grid/axis)
3. WHEN validate_figures.py runs THEN the System SHALL verify atlas panels contain no legends
4. WHEN validate_figures.py runs THEN the System SHALL verify atlas_index.csv contains source_table_row_id for all entries with no missing values
5. WHEN validate_figures.py runs THEN the System SHALL verify all cultural maps use identical xlim and ylim ranges
6. WHEN validate_figures.py runs THEN the System SHALL verify output formats are consistent (summary=PDF+PNG, atlas=PNG or PDF)
7. WHEN validate_figures.py finds violations THEN the System SHALL fail with a clear error report listing all issues

### Requirement 18

**User Story:** As a publication author, I want FigS1 IVS reference map in two versions, so that I have a clean version for SI and a fully-labeled version for reference.

#### Acceptance Criteria

1. WHEN generating FigS1 THEN the System SHALL create FigS1_IVS_reference_minlabel.pdf with 10-15 representative country labels (1-2 per cultural zone)
2. WHEN generating FigS1 THEN the System SHALL create FigS1_IVS_reference_fulllabel.pdf with all country labels using adjustText for positioning
3. WHEN generating both FigS1 versions THEN the System SHALL use identical zone colors, axis ranges, grid styles, and 0-axis dashed lines
4. WHEN generating FigS1 THEN the System SHALL output as single full-page PDF (not 3×3 atlas panel)
