# Implementation Plan

## Unified Style System for All Figures + SI Atlas Generation

**Goal**: Establish global style system (colors, fonts, labeling) for ALL scripts in `figures/` and `SI/figures/`, then generate SI atlas and summary figures with full auditability.

**Key Deliverables**:
1. Global style system (`figures/style/colors.json`, `paper.mplstyle`, `StyleManager`)
2. Three S3 template functions (`plot_focus_country`, `plot_focus_language`, `plot_focus_model`)
3. Updated all figure generation scripts to use StyleManager
4. SI atlas PDFs with cover pages and minimal labeling
5. Summary heatmaps for both PC1 and PC2
6. Automated validation (`validate_figures.py`)

---

- [x] 1. Establish global style system (MUST DO FIRST)








  - [x] 1.1 Create figures/style/ directory and placeholder files

    - Create `figures/style/` directory


    - Create empty `colors.json` and `paper.mplstyle`
    - _Requirements: 9.1_
  
  - [x] 1.2 Design and generate colors.json




    - Define 9 color-blind safe colors for cultural zones
    - Define 13 color-blind safe colors for languages
    - **Auto-discover models from data files, assign colors by vendor family (OpenAI=blue, Anthropic=purple, Google=green, Meta=orange, Mistral=red, DeepSeek=cyan, Qwen=yellow, Grok=gray), lock mapping in colors.json**
    - Within each family, assign different brightness levels to different models
    - Validate all colors for grayscale distinguishability (luminance diff ≥ 0.15)
    - Save to `figures/style/colors.json`
    - _Requirements: 9.1, 9.4, 9.5, 9.6_
  
  - [x] 1.3 Create paper.mplstyle





    - Define font family (Arial), sizes (9pt base)
    - Define line widths, marker sizes, axis settings, grid transparency
    - Define output dpi (300), tight_layout
    - Save to `figures/style/paper.mplstyle`
    - _Requirements: 9.3_
  
  - [x] 1.4 Implement StyleManager class





    - Load `colors.json` into three dictionaries
    - Apply `paper.mplstyle` to matplotlib
    - Implement `get_model_color()`, `get_language_color()`, `get_zone_color()`
    - Implement `get_labeling_policy()` for different panel types
    - Expose common parameters: `alpha_bg`, `lw_axis`, `lw_marker_edge`, marker sizes
    - Implement `_verify_no_hardcoded_colors()` to scan all scripts
    - _Requirements: 9.1, 9.2, 9.3, 9.7_
  
  - [x] 1.5 Write property test for color-blind safety









    - **Property 14: Color-Blind Safety**
    - **Grayscale check failures should be warnings, not errors**
    - **Validates: Requirements 9.4, 9.5, 9.6**
  
  - [x] 1.6 Write property test for no hardcoded colors






    - **Property 13: No Hardcoded Colors**
    - **Add whitelist for legitimate color strings (e.g., 'none', 'white', 'black', 'gray' for backgrounds/edges)**
    - **Validates: Requirements 9.2, 9.7**

- [x] 2. Implement S3 template functions (standardize panel generation)





  - [x] 2.1 Implement plot_focus_country() template


    - Background: IVS points by zone color, alpha ≤ 0.15
    - Focal: Target country as star with black edge
    - Foreground: Model point in model_color (circle)
    - Labels: Focal country + Top-K (default K=5) nearest/furthest
    - **Explicitly define Top-K selector: K nearest + K furthest by Euclidean distance**
    - Use adjustText only on labeled subset
    - Color encodes ONE dimension only (model)
    - _Requirements: 14.1, 14.4, 14.5_
  
  - [x] 2.2 Implement plot_focus_language() template

    - Background: IVS points by zone color, alpha ≤ 0.15
    - Focal: Target language as square in language_color
    - Optional: Other languages in lighter shades (same hue)
    - Labels: Focal language + Top-K extreme languages
    - **Explicitly define Top-K selector: K nearest + K furthest by Euclidean distance**
    - Color encodes ONE dimension only (language)
    - _Requirements: 14.2, 14.4, 14.5_
  
  - [x] 2.3 Implement plot_focus_model() template

    - Background: IVS points by zone color, alpha ≤ 0.15
    - Foreground: All country points for model-language in model_color (circles)
    - Optional: Gray dashed connection lines, alpha 0.3
    - Labels: Top-K countries with largest deviation
    - **Explicitly define Top-K selector: K countries with largest distance from IVS baseline**
    - Color encodes ONE dimension only (model)
    - _Requirements: 14.3, 14.4, 14.5_
  
  - [x] 2.4 Write property test for single color channel






    - **Property 24: Single Color Channel**
    - **Implement as code-level detection: scan template function calls to verify only one color dimension is passed**
    - **Validates: Requirements 14.4**
  
  - [x] 2.5 Write property test for Top-K labeling





    - **Property 17: Top-K Labeling Constraint**
    - **Validates: Requirements 14.5**

- [x] 3. Update all existing figure generation scripts to use StyleManager




  - [x] 3.1 Audit all scripts in figures/ and SI/figures/


    - List all Python scripts that generate cultural maps
    - Identify hardcoded colors, fonts, line widths
    - Document which scripts need template function migration
    - _Requirements: 9.2, 9.7_
  
  - [x] 3.2 Update S3-B1/B2/B3/B4/B5 scripts to use templates


    - Replace ad-hoc plotting code with template functions
    - Remove hardcoded colors, use StyleManager
    - Remove panel legends (legends only on atlas cover)
    - _Requirements: 14.1, 14.2, 14.3, 10.6_
  
  - [x] 3.3 Update S2 baseline scripts for semantic color use

    - If color encodes language: use `language_colors` only
    - If color encodes model: use `model_colors` only
    - Use marker shape as second channel if needed
    - Add legend explaining color-to-entity mapping
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [x] 3.4 Update all other scripts (main figures, analysis plots)


    - Replace hardcoded colors with StyleManager calls
    - Apply `paper.mplstyle` via StyleManager
    - Ensure consistent axis ranges for cultural maps
    - _Requirements: 9.2, 9.3_

- [x] 4. Generate FigS1 IVS reference map (two versions)




  - [x] 4.1 Implement FigS1 minimal label version

    - Single full-page PDF (not 3×3 atlas panel)
    - IVS points colored by cultural zone
    - Label 10-15 representative countries (1-2 per zone)
    - Use StyleManager zone colors
    - Output: `FigS1_IVS_reference_minlabel.pdf`
    - _Requirements: 18.1, 18.3, 18.4_
  
  - [x] 4.2 Implement FigS1 full label version

    - Single full-page PDF with larger canvas
    - All country labels using adjustText
    - Identical zone colors, axis ranges, grid styles
    - Output: `FigS1_IVS_reference_fulllabel.pdf`
    - _Requirements: 18.2, 18.3, 18.4_
  
  - [ ]* 4.3 Write property test for FigS1 special handling
    - **Property 18: FigS1 Special Handling**
    - **Validates: Requirements 18.4**

- [x] 5. Implement AtlasGenerator with cover pages







  - [x] 5.1 Create AtlasGenerator class with StyleManager integration


    - Initialize with project_root and StyleManager instance
    - Set up paths, grid size (3×3), max pages per file (50)
    - _Requirements: 1.1, 1.4, 9.2_
  
  - [x] 5.2 Implement create_cover_page() method


    - Create full-page layout with atlas title and metadata
    - Display complete color legends (zones, languages, models)
    - Add labeling policy explanation
    - Add link to atlas_index.csv
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [x] 5.3 Implement create_page() method for 3×3 grid


    - Create figure with 3×3 subplot grid
    - Add page header "{AtlasName} - Page {x} / {N}"
    - **Add panel cache rendering step: pre-render all panels before assembling grid**
    - Load and place each figure image
    - Add short-format label (max 40 chars)
    - Do NOT include legends in panels
    - _Requirements: 1.1, 1.2, 1.3, 10.6, 10.7_
  
  - [x] 5.4 Implement generate_atlas() method


    - Create cover page as page 0
    - Iterate through figures, create grid pages
    - **Split into multiple PDFs if > max_pages (parameterized, default 50)**
    - Each part gets its own cover page
    - _Requirements: 1.4, 1.5, 1.6, 1.7, 1.8, 11.5_
  
  - [x] 5.5 Write property tests for atlas






    - **Property 1, 2, 19, 20, 21**
    - **Validates: Requirements 1.1, 1.2, 10.6, 11.1, 11.5**

- [x] 6. Implement IndexGenerator with source row IDs





  - [x] 6.1 Create IndexGenerator class


    - Load Table_S7 with row IDs
    - Create lookup dict
    - _Requirements: 2.1, 2.3, 12.1_
  
  - [x] 6.2 Implement add_source_row_ids() method


    - Match entries to Table_S7 rows
    - Handle aggregated data (semicolon-separated)
    - Use "N/A" when not determinable
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [x] 6.3 Implement create_index() method


    - Build DataFrame with all columns including source_table_row_id
    - Enrich with PC1, PC2
    - Save to atlas_index.csv
    - _Requirements: 2.1, 2.2, 2.3, 12.1_
  
  - [ ]* 6.4 Write property tests
    - **Property 5, 22**
    - **Validates: Requirements 2.1, 12.1**
  
  - [x] 6.5 Generate atlas/README.md


    - Explain columns including source_table_row_id
    - Provide example queries
    - _Requirements: 2.4, 12.1_

- [ ] 7. Update SummaryFigureGenerator for PC1 AND PC2




  - [x] 7.1 Modify initialization to use StyleManager


    - Accept StyleManager instance
    - Use StyleManager.get_colormap_settings()
    - _Requirements: 3.1, 9.2_
  
  - [x] 7.2 Generate model×country heatmaps (PC1 and PC2)


    - FigSx1_PC1 and FigSx1_PC2
    - Identical layout, clustering, colormap
    - _Requirements: 3.1, 16.1_
  
  - [x] 7.3 Generate country×language heatmaps (PC1 and PC2)


    - FigSx2_PC1 and FigSx2_PC2
    - _Requirements: 3.2, 16.2_
  
  - [x] 7.4 Generate model×language heatmaps (PC1 and PC2)


    - FigSx3_PC1 and FigSx3_PC2
    - _Requirements: 3.3, 16.3_
  
  - [x] 7.5 Generate 2D distance heatmaps


    - Calculate Euclidean distance combining PC1 and PC2
    - FigSx1_2D, FigSx2_2D, FigSx3_2D
    - _Requirements: 16.4_
  
  - [x] 7.6 Update scatter plot for 2D version


    - FigSx6_PC1_vs_consistency
    - FigSx6_PC2_vs_consistency
    - _Requirements: 16.5_
  
  - [ ]* 7.7 Write property test for heatmap consistency
    - **Property 6**
    - **Validates: Requirements 3.1-3.5**

- [ ] 8. Implement remaining summary figures







  - [x] 8.1 Implement variance decomposition with StyleManager





    - Use StyleManager colors
    - _Requirements: 4.1, 9.2_
  

  - [x] 8.2 Update rankings to use StyleManager


    - _Requirements: 5.1, 9.2_
  
  - [ ]* 8.3 Write property tests
    - **Property 7, 8, 9**
    - **Validates: Requirements 4.1, 5.1, 6.1**

- [x] 9. Implement FigureValidator





  - [x] 9.1 Create FigureValidator class


    - _Requirements: 17.1_
  
  - [x] 9.2 Implement check_no_hardcoded_colors()


    - Scan all .py files
    - _Requirements: 17.2_
  
  - [x] 9.3 Implement check_atlas_no_legends()


    - _Requirements: 17.3_
  
  - [x] 9.4 Implement check_index_completeness()


    - _Requirements: 17.4_
  
  - [x] 9.5 Implement check_axis_consistency()


    - **Verify all cultural map panels have identical axis ranges as FigS1**
    - **Verify cover-only legends: atlas panels must not contain legends**
    - _Requirements: 17.5_
  
  - [x] 9.6 Implement check_output_formats()


    - _Requirements: 17.6_
  
  - [x] 9.7 Implement validate_all() and generate_report()


    - _Requirements: 17.7_

- [x] 10. Update documentation




  - [x] 10.1 Update SI/figures/README.md

    - Replace text as specified
    - Add Labeling Policy and Color System sections
    - _Requirements: 13.1, 13.2, 13.3, 13.4_
  
  - [x] 10.2 Create figures/style/README.md

    - Document colors.json and paper.mplstyle
    - Explain vendor grouping
    - _Requirements: 9.1, 9.4, 9.5, 9.6_
  
  - [x] 10.3 Update summary README with captions

    - Generate captions for all PC1, PC2, 2D versions
    - **Use templated explanations: PC1 = Traditional-Secular axis, PC2 = Survival-Self-expression axis, 2D = Euclidean distance combining both**
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [ ]* 10.4 Write property tests
    - **Property 10, 23**
    - **Validates: Requirements 7.1, 13.1**

- [x] 11. Main entry point and batch generation




  - [x] 11.1 Implement main() with StyleManager


    - Initialize StyleManager first
    - Parse CLI arguments
    - Instantiate generators
    - _Requirements: 9.1, 9.2_
  
  - [x] 11.2 Generate all 4 Atlas PDFs with covers


    - FigS2A1, FigS3B3, FigS3B4, FigS3B5
    - _Requirements: 1.5-1.8, 11.1, 11.5_
  
  - [x] 11.3 Generate all summary figures (PC1, PC2, 2D)


    - _Requirements: 3.1-3.3, 16.1-16.5_
  
  - [x] 11.4 Run FigureValidator at the end


    - _Requirements: 17.1-17.7_

- [x] 12. Error handling and reporting




  - [x] 12.1 Verify error handling with StyleManager


    - _Requirements: 8.1, 8.2, 9.1_
  
  - [x] 12.2 Verify summary reporting


    - _Requirements: 8.3_
  
  - [ ]* 12.3 Write property test
    - **Property 11**
    - **Validates: Requirements 8.1-8.3**

- [x] 13. Final validation




  - [x] 13.1 Random sample validation (30 panels)

    - Verify no label occlusion
    - Verify color consistency
    - Verify no legends in panels
    - Verify axis ranges match FigS1
    - _Requirements: 9.2, 10.3, 10.6_
  
  - [x] 13.2 Generate validation report

    - _Requirements: 8.3, 17.7_
  
  - [x] 13.3 Update all documentation

    - _Requirements: 7.1, 13.1-13.4_

- [ ] 14. Final Checkpoint
  - Ensure all tests pass
