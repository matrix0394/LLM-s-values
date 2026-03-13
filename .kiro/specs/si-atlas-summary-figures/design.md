# Design Document: SI Atlas and Summary Figures

## Overview

This feature implements a batch figure compilation system for Supporting Information (SI) materials. It consists of two main components:

1. **Atlas Generator**: Assembles individual cultural map figures into multi-page PDF documents with 3×3 grid layouts, page headers, and figure labels
2. **Summary Figure Generator**: Creates statistical overview visualizations (heatmaps, variance decomposition, rankings, correlations) from PCA entity scores

The system processes ~1,800 existing figures and generates 4 Atlas PDFs plus 6 summary figures with accompanying index tables and documentation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SI Figure Pipeline                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Input Data   │    │ Generators   │    │ Output       │      │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤      │
│  │ SI/figures/  │───▶│ AtlasGen     │───▶│ atlas/*.pdf  │      │
│  │ ├─ S2/A1/    │    │              │    │ atlas_index  │      │
│  │ ├─ S3/B3/    │    ├──────────────┤    ├──────────────┤      │
│  │ ├─ S3/B4/    │    │ SummaryGen   │───▶│ summary/     │      │
│  │ └─ S3/B5/    │    │              │    │ ├─ FigSx*.pdf│      │
│  ├──────────────┤    └──────────────┘    │ └─ README.md │      │
│  │ SI/pca/      │                        └──────────────┘      │
│  │ └─ Table_S7  │                                              │
│  ├──────────────┤    ┌──────────────┐                          │
│  │ figures/     │    │ Style System │                          │
│  │ derived_data/│    ├──────────────┤                          │
│  │ └─ consist.  │    │ colors.json  │◀─── All generators       │
│  └──────────────┘    │ paper.mplstyle│    read from here       │
│                      └──────────────┘                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Global Style System (SI/figures/style/)                  │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • colors.json: 3 color dictionaries                      │  │
│  │   - cultural_zone_colors (9 zones)                       │  │
│  │   - language_colors (13 languages)                       │  │
│  │   - model_colors (44 models, grouped by vendor)          │  │
│  │ • paper.mplstyle: matplotlib RC params                   │  │
│  │   - fonts, sizes, line widths, transparency              │  │
│  │   - axis ranges, grid styles, legend formatting          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 0. StyleManager Class (NEW)

```python
class StyleManager:
    """
    Manage global style settings for all figures in the project.
    
    Loads and provides access to:
    - Color dictionaries (cultural zones, languages, models grouped by vendor)
    - Matplotlib style parameters
    - Labeling policies and thresholds
    - Common visual parameters (alpha, line widths, marker sizes)
    """
    
    def __init__(self, style_dir: Path):
        self.style_dir = style_dir
        self.colors: Dict[str, Dict[str, str]] = {}
        self.mplstyle_path: Path = style_dir / 'paper.mplstyle'
        
        # Common visual parameters
        self.alpha_bg = 0.12  # Background IVS points transparency
        self.lw_axis = 1.2    # Axis line width
        self.lw_marker_edge = 0.8  # Marker edge line width
        self.marker_size_focal = 120  # Focal object marker size
        self.marker_size_regular = 60  # Regular point marker size
        
        self._load_colors()
        self._apply_mplstyle()
        self._verify_no_hardcoded_colors()
    
    def _load_colors(self) -> None:
        """Load colors.json with three dictionaries."""
        pass
    
    def _apply_mplstyle(self) -> None:
        """Apply paper.mplstyle to matplotlib."""
        pass
    
    def _verify_no_hardcoded_colors(self) -> None:
        """
        Verify no hardcoded color values in scripts (except gray for grid/axis).
        
        Scans all .py files in figures/ and SI/figures/ for color strings.
        """
        pass
    
    def get_cultural_zone_color(self, zone: str) -> str:
        """Get color for a cultural zone (9 zones)."""
        pass
    
    def get_language_color(self, language: str) -> str:
        """Get color for a language (13 languages)."""
        pass
    
    def get_model_color(self, model: str) -> str:
        """
        Get color for a model (grouped by vendor family).
        
        Vendor families:
        - OpenAI: blue family (#1f77b4 base)
        - Anthropic: purple family (#9467bd base)
        - Google: green family (#2ca02c base)
        - Meta: orange family (#ff7f0e base)
        - Mistral: red family (#d62728 base)
        - DeepSeek: cyan family (#17becf base)
        - Qwen: yellow family (#bcbd22 base)
        - Grok: gray family (#7f7f7f base)
        
        Within each family, different models get different brightness levels.
        """
        pass
    
    def get_labeling_policy(self, panel_type: str) -> Dict:
        """
        Get labeling policy for a panel type.
        
        Returns dict with:
        - label_background: bool (whether to label IVS background points)
        - label_foreground: str ('all', 'focal_only', 'top_k')
        - top_k: int (number of extreme points to label if 'top_k')
        - background_alpha: float (transparency for IVS points)
        """
        pass
```

### 0.1 Template Functions for S3 Panels (NEW)

```python
def plot_focus_country(ax: plt.Axes, 
                       style_mgr: StyleManager,
                       model: str, 
                       country: str, 
                       language: str,
                       ivs_data: pd.DataFrame,
                       llm_data: pd.DataFrame,
                       top_k: int = 5) -> None:
    """
    Template for country-focused cultural map panel.
    
    Visual encoding:
    - Background: IVS points colored by cultural zone, alpha ≤ 0.15
    - Focal: Target country as star with black edge
    - Foreground: Model point in model_color (circle marker)
    - Labels: Focal country + Top-K nearest/furthest countries
    
    Args:
        ax: Matplotlib axes to plot on
        style_mgr: StyleManager instance for colors
        model: Model name
        country: Target country name (focal object)
        language: Language code
        ivs_data: IVS reference data with PC1, PC2, cultural_zone
        llm_data: LLM data with PC1, PC2 for this model-country-language
        top_k: Number of extreme points to label (default 5)
    
    Requirements: 14.1, 14.4, 14.5
    """
    pass


def plot_focus_language(ax: plt.Axes,
                        style_mgr: StyleManager,
                        country: str,
                        language: str,
                        ivs_data: pd.DataFrame,
                        llm_data: pd.DataFrame,
                        show_other_languages: bool = False,
                        top_k: int = 5) -> None:
    """
    Template for language-focused cultural map panel.
    
    Visual encoding:
    - Background: IVS points colored by cultural zone, alpha ≤ 0.15
    - Focal: Target language as square in language_color
    - Optional: Other languages for same country in lighter shades (same hue)
    - Labels: Focal language + Top-K extreme languages
    
    Args:
        ax: Matplotlib axes to plot on
        style_mgr: StyleManager instance for colors
        country: Country name
        language: Target language code (focal object)
        ivs_data: IVS reference data
        llm_data: LLM data for this country across languages
        show_other_languages: Whether to show other languages in lighter shades
        top_k: Number of extreme points to label (default 5)
    
    Requirements: 14.2, 14.4, 14.5
    """
    pass


def plot_focus_model(ax: plt.Axes,
                     style_mgr: StyleManager,
                     model: str,
                     language: str,
                     ivs_data: pd.DataFrame,
                     llm_data: pd.DataFrame,
                     show_connections: bool = False,
                     top_k: int = 5) -> None:
    """
    Template for model-focused cultural map panel.
    
    Visual encoding:
    - Background: IVS points colored by cultural zone, alpha ≤ 0.15
    - Foreground: All country points for this model-language in model_color (circles)
    - Optional: Gray dashed lines from IVS country to LLM point, alpha 0.3
    - Labels: Top-K countries with largest/smallest deviation
    
    Args:
        ax: Matplotlib axes to plot on
        style_mgr: StyleManager instance for colors
        model: Target model name (focal object)
        language: Language code
        ivs_data: IVS reference data
        llm_data: LLM data for this model-language across countries
        show_connections: Whether to draw connection lines from IVS to LLM points
        top_k: Number of extreme points to label (default 5)
    
    Requirements: 14.3, 14.4, 14.5
    """
    pass
```

### 0.2 FigureValidator Class (NEW)

```python
class FigureValidator:
    """
    Automated validation of generated figures for style compliance.
    
    Checks:
    - Color consistency (all colors from StyleManager)
    - Atlas legend absence
    - Index completeness (source_table_row_id)
    - Axis range consistency
    - Output format consistency
    """
    
    def __init__(self, project_root: Path, style_mgr: StyleManager):
        self.project_root = project_root
        self.style_mgr = style_mgr
        self.violations: List[Dict[str, str]] = []
    
    def validate_all(self) -> bool:
        """
        Run all validation checks.
        
        Returns:
            True if all checks pass, False otherwise
        
        Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7
        """
        pass
    
    def check_no_hardcoded_colors(self) -> bool:
        """Verify no hardcoded colors in scripts (except gray)."""
        pass
    
    def check_atlas_no_legends(self) -> bool:
        """Verify atlas panels contain no legend boxes."""
        pass
    
    def check_index_completeness(self) -> bool:
        """Verify atlas_index.csv has source_table_row_id for all entries."""
        pass
    
    def check_axis_consistency(self) -> bool:
        """Verify all cultural maps use identical xlim/ylim."""
        pass
    
    def check_output_formats(self) -> bool:
        """Verify output formats are consistent (summary=PDF+PNG, atlas=PNG)."""
        pass
    
    def generate_report(self) -> str:
        """Generate validation report with all violations."""
        pass
```

### 1. AtlasGenerator Class

### 1. AtlasGenerator Class

```python
class AtlasGenerator:
    """Generate multi-page Atlas PDFs from figure directories."""
    
    def __init__(self, project_root: Path, style_manager: StyleManager):
        self.project_root = project_root
        self.style_manager = style_manager  # NEW: use global style
        self.si_dir = project_root / 'SI'
        self.output_dir = self.si_dir / 'figures' / 'atlas'
        self.grid_size = (3, 3)  # 3×3 grid per page
        self.max_pages_per_file = 50
    
    def create_cover_page(self, atlas_name: str, total_figures: int) -> plt.Figure:
        """
        Create atlas cover page with title, figure count, and unified legends.
        
        NEW: Cover page includes:
        - Atlas title and metadata
        - Complete color legends (cultural zones, languages, models)
        - Labeling policy explanation
        - Link to atlas_index.csv for entity identification
        
        Args:
            atlas_name: Display name for the atlas
            total_figures: Total number of figures in this atlas
        
        Returns:
            matplotlib Figure object for the cover page
        """
        pass
    
    def generate_atlas(self, 
                       source_dir: Path, 
                       atlas_name: str,
                       output_filename: str) -> Tuple[List[Path], pd.DataFrame]:
        """
        Generate Atlas PDF(s) from a directory of figures.
        
        MODIFIED: Now includes cover page as page 0 before grid pages.
        
        Args:
            source_dir: Directory containing figure files (PDF/PNG)
            atlas_name: Display name for page headers
            output_filename: Base filename for output (e.g., 'FigS2A1_Atlas')
        
        Returns:
            Tuple of (list of generated PDF paths, index DataFrame)
        """
        pass
    
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """
        Parse figure filename to extract model, country, language.
        
        Returns dict with keys: model, country, language, or None values if not parseable.
        """
        pass
    
    def create_page(self, 
                    figures: List[Path], 
                    page_num: int, 
                    total_pages: int,
                    atlas_name: str) -> plt.Figure:
        """
        Create a single Atlas page with 3×3 grid.
        
        MODIFIED: No longer includes legends in panels.
        """
        pass
```

### 2. SummaryFigureGenerator Class

```python
class SummaryFigureGenerator:
    """Generate summary heatmaps and statistical figures."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / 'SI' / 'figures' / 'summary'
        self.pca_data = None
        self.consistency_data = None
        self.ivs_data = None
        self._load_data()
    
    def generate_model_country_heatmap(self) -> Path:
        """Generate Fig Sx1: 21×66 model×country heatmap with clustering."""
        pass
    
    def generate_country_language_heatmap(self) -> Path:
        """Generate Fig Sx2: country×language heatmap."""
        pass
    
    def generate_model_language_heatmap(self) -> Path:
        """Generate Fig Sx3: model×language heatmap."""
        pass
    
    def generate_variance_decomposition(self) -> Path:
        """Generate Fig Sx4: variance decomposition bar chart."""
        pass
    
    def generate_top_bottom_rankings(self) -> Path:
        """Generate Fig Sx5: top/bottom countries per model small multiples."""
        pass
    
    def generate_score_consistency_scatter(self) -> Path:
        """Generate Fig Sx6: entity_score vs consistency scatter with regression."""
        pass
    
    def generate_readme_with_captions(self, figure_paths: Dict[str, Path]) -> Path:
        """Generate README.md with all figure captions."""
        pass
```

### 3. IndexGenerator Class

```python
class IndexGenerator:
    """Generate searchable index tables for Atlas figures."""
    
    def __init__(self, pca_data_path: Path):
        self.pca_data = pd.read_csv(pca_data_path)
    
    def create_index(self, 
                     atlas_entries: List[Dict],
                     output_path: Path) -> pd.DataFrame:
        """
        Create atlas_index.csv with all figure metadata.
        
        MODIFIED: Now includes source_table_row_id column.
        
        Columns: atlas, page, row, col, model, country, language, filename, 
                 PC1, PC2, source_table_row_id
        """
        pass
    
    def enrich_with_entity_scores(self, 
                                   index_df: pd.DataFrame) -> pd.DataFrame:
        """Add PC1, PC2 values from PCA data where available."""
        pass
    
    def add_source_row_ids(self, index_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add source_table_row_id column linking to Table_S7 rows.
        
        NEW: For auditability, links each figure to its source data row(s).
        
        Args:
            index_df: DataFrame with atlas index entries
        
        Returns:
            DataFrame with added source_table_row_id column
        """
        pass
```

## Data Models

### Input Data Structures

```python
# PCA Coordinates (from Table_S7_LLM_roleplay_PCA_coordinates.csv)
@dataclass
class PCACoordinate:
    model_name: str
    country: str
    country_code: int
    language: str
    condition: str  # 'imitation'
    PC1: float
    PC2: float
    data_source: str  # 'LLM'

# Consistency Data (from model_consistency_summary.csv)
@dataclass
class ConsistencyRecord:
    model: str
    baseline_consistency: float
    roleplay_consistency: float

# Atlas Index Entry
@dataclass
class AtlasIndexEntry:
    atlas: str           # e.g., 'FigS3B3_Atlas'
    page: int            # 1-indexed page number (0 = cover page)
    row: int             # 0-2 (row in 3×3 grid)
    col: int             # 0-2 (column in 3×3 grid)
    model: Optional[str]
    country: Optional[str]
    language: Optional[str]
    filename: str
    PC1: Optional[float]
    PC2: Optional[float]
    source_table_row_id: Optional[str]  # NEW: link to Table_S7 row(s)

# Color Dictionary Structure (NEW)
@dataclass
class ColorDictionaries:
    """
    Global color mappings loaded from SI/figures/style/colors.json
    """
    cultural_zone_colors: Dict[str, str]  # 9 zones -> hex colors
    language_colors: Dict[str, str]       # 13 languages -> hex colors
    model_colors: Dict[str, str]          # 44 models -> hex colors
    
    # Example structure:
    # {
    #   "cultural_zone_colors": {
    #     "Confucian": "#1f77b4",
    #     "Protestant Europe": "#ff7f0e",
    #     "Latin America": "#2ca02c",
    #     ...
    #   },
    #   "language_colors": {
    #     "en": "#e41a1c",
    #     "zh-cn": "#377eb8",
    #     "ja": "#4daf4a",
    #     ...
    #   },
    #   "model_colors": {
    #     "gpt-4o": "#8c564b",
    #     "gpt-4o-mini": "#a67c52",  # same hue, different brightness
    #     "claude-3-7-sonnet": "#9467bd",
    #     ...
    #   }
    # }

# Labeling Policy (NEW)
@dataclass
class LabelingPolicy:
    """
    Policy for labeling points in cultural map panels.
    """
    panel_type: str  # 'FigS1', 'S2-A1', 'S2-A2', 'S3-B1', etc.
    label_background: bool  # Whether to label IVS background points
    label_foreground: str  # 'all', 'focal_only', 'top_k'
    top_k: int  # Number of extreme points to label if 'top_k'
    background_alpha: float  # Transparency for IVS background points
    use_repel: bool  # Whether to use adjustText for label positioning
    max_title_length: int  # Maximum characters in panel title
```

### Output File Structure

```
SI/figures/
├── style/                              # NEW: Global style system
│   ├── colors.json                     # Color dictionaries (zones, languages, models)
│   ├── paper.mplstyle                  # Matplotlib style parameters
│   └── README.md                       # Style system documentation
├── atlas/
│   ├── FigS2A1_Atlas.pdf               # 23 figures → 3 pages + cover
│   ├── FigS3B3_Atlas_part01.pdf        # 1386 figures → split into parts + covers
│   ├── FigS3B3_Atlas_part02.pdf
│   ├── ...
│   ├── FigS3B4_Atlas.pdf               # 122 figures → 14 pages + cover
│   ├── FigS3B5_Atlas.pdf               # 294 figures → 33 pages + cover
│   ├── atlas_index.csv                 # MODIFIED: now includes source_table_row_id
│   └── README.md
└── summary/
    ├── FigSx1_heatmap_model_country.pdf
    ├── FigSx2_heatmap_country_language.pdf
    ├── FigSx3_heatmap_model_language.pdf
    ├── FigSx4_variance_decomposition.pdf
    ├── FigSx5_top_bottom_rankings.pdf
    ├── FigSx6_score_vs_consistency.pdf
    └── README.md
```

### Color Dictionary File Format (NEW)

`SI/figures/style/colors.json`:
```json
{
  "cultural_zone_colors": {
    "Confucian": "#1f77b4",
    "Protestant Europe": "#ff7f0e",
    "Latin America": "#2ca02c",
    "Catholic Europe": "#d62728",
    "English Speaking": "#9467bd",
    "African-Islamic": "#8c564b",
    "Baltic": "#e377c2",
    "South Asia": "#7f7f7f",
    "Orthodox": "#bcbd22"
  },
  "language_colors": {
    "en": "#e41a1c",
    "zh-cn": "#377eb8",
    "zh-tw": "#4daf4a",
    "zh-hk": "#984ea3",
    "ja": "#ff7f00",
    "ko": "#ffff33",
    "ar": "#a65628",
    "de": "#f781bf",
    "es": "#999999",
    "fr": "#66c2a5",
    "it": "#fc8d62",
    "pt": "#8da0cb",
    "ru": "#e78ac3"
  },
  "model_colors": {
    "gpt-4o": "#8c564b",
    "gpt-4o-mini": "#a67c52",
    "gpt-4-turbo": "#c09259",
    "claude-3-7-sonnet-20250219": "#9467bd",
    "claude-3-5-sonnet-20241022": "#a87dc4",
    "claude-3-5-sonnet-20240620": "#bc93cb",
    "gemini-2.0-flash-exp": "#1f77b4",
    "gemini-1.5-pro-002": "#3a8bc4",
    "gemini-1.5-flash-002": "#559fd4",
    "...": "..."
  }
}
```

### Matplotlib Style File Format (NEW)

`SI/figures/style/paper.mplstyle`:
```
# Font settings
font.family: Arial
font.size: 9
axes.labelsize: 10
axes.titlesize: 11
xtick.labelsize: 8
ytick.labelsize: 8
legend.fontsize: 8

# Figure settings
figure.dpi: 300
savefig.dpi: 300
savefig.bbox: tight
figure.facecolor: white

# Axes settings
axes.spines.top: False
axes.spines.right: False
axes.linewidth: 0.8
axes.grid: False

# Line and marker settings
lines.linewidth: 1.5
lines.markersize: 6
patch.linewidth: 0.5

# Legend settings
legend.frameon: False
legend.loc: best

# Grid settings (when enabled)
grid.alpha: 0.3
grid.linestyle: --
grid.linewidth: 0.5

# Color cycle (color-blind safe)
axes.prop_cycle: cycler('color', ['1f77b4', 'ff7f0e', '2ca02c', 'd62728', '9467bd', '8c564b', 'e377c2', '7f7f7f', 'bcbd22', '17becf'])
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Atlas Grid Layout Consistency
*For any* set of N figures processed by the Atlas generator, the output PDF(s) SHALL contain exactly ceil(N/9) pages, with each page containing at most 9 figures arranged in a 3×3 grid.
**Validates: Requirements 1.1**

### Property 2: Page Header Format
*For any* Atlas page generated, the page header SHALL match the format "{AtlasName} - Page {x} / {N}" where x is the current page number (1-indexed) and N is the total page count.
**Validates: Requirements 1.2**

### Property 3: Filename Parsing Consistency
*For any* valid figure filename following the pattern `FigS*_{model}_{country}_{language}.*`, parsing SHALL extract the correct model, country, and language components, and re-parsing the same filename SHALL produce identical results.
**Validates: Requirements 1.3, 2.2**

### Property 4: PDF Splitting Threshold
*For any* Atlas with more than 50 pages, the output SHALL be split into multiple PDF files where each part contains at most 50 pages, and the union of all parts SHALL contain all input figures exactly once.
**Validates: Requirements 1.4**

### Property 5: Index File Completeness
*For any* generated Atlas, the atlas_index.csv SHALL contain exactly one row per figure, with all required columns (atlas, page, row, col, model, country, language, filename) populated, and PC1/PC2 values present when matching PCA data exists.
**Validates: Requirements 2.1, 2.3**

### Property 6: Heatmap Rendering Consistency
*For any* set of heatmaps generated (model×country, country×language, model×language), all heatmaps SHALL use identical colormap parameters (vmin, vmax, cmap) and each heatmap SHALL have a non-empty title string.
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 7: Variance Decomposition Completeness
*For any* variance decomposition figure generated, the bar chart SHALL contain exactly three bars (model, country, language) with values that sum to approximately 100% (within floating-point tolerance), and error bars SHALL be present if standard errors are calculable.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 8: Ranking Figure Structure
*For any* ranking figure generated, each model panel SHALL display exactly 10 countries (5 top + 5 bottom by cultural distance), and all panels SHALL use identical axis scales.
**Validates: Requirements 5.1, 5.2, 5.3**

### Property 9: Scatter Plot Completeness
*For any* score-vs-consistency scatter plot generated, the plot SHALL contain a regression line with R² annotation, a legend, and points styled consistently.
**Validates: Requirements 6.1, 6.2, 6.3**

### Property 10: Caption Generation
*For any* summary figure generated, a corresponding caption entry SHALL exist in the README.md following the format "Fig Sx{n}: {description}" where description is 1-2 sentences.
**Validates: Requirements 7.1, 7.2**

### Property 11: Graceful Error Handling
*For any* missing or corrupted input file, the system SHALL skip that file, log a warning, and continue processing remaining files. The final summary SHALL report the count of processed vs skipped items.
**Validates: Requirements 8.1, 8.2, 8.3**

### Property 12: Color Dictionary Consistency
*For any* two figures generated in the same execution, if both figures display the same entity (cultural zone, language, or model), then both figures SHALL use the identical color from the global color dictionary.
**Validates: Requirements 9.1, 9.2**

### Property 13: No Hardcoded Colors
*For any* plotting function in any generator class, the function SHALL NOT contain hardcoded color strings (e.g., '#FF0000', 'red') and SHALL instead retrieve colors from StyleManager.
**Validates: Requirements 9.2**

### Property 14: Color-Blind Safety
*For any* set of colors assigned to a category (cultural zones, languages, or models), the colors SHALL remain distinguishable in simulated color-blind vision using CIELAB ΔE distance metrics. Cultural zones require ΔE ≥ 10 (protanopia), ΔE ≥ 7 (deuteranopia), and ΔE ≥ 7.5 (tritanopia). Languages require ΔE ≥ 8 (protanopia), ΔE ≥ 6 (deuteranopia), and ΔE ≥ 6 (tritanopia). Models from different vendor families require ΔE ≥ 2.5 (protanopia) and ΔE ≥ 6 (deuteranopia), while same-vendor models may have similar colors. Grayscale distinguishability is a secondary goal (warning only, not failure condition).
**Validates: Requirements 9.4, 9.5, 9.6**

### Property 15: Background Transparency
*For any* atlas panel displaying IVS background points, the alpha transparency SHALL be ≤ 0.15, and by default no country name labels SHALL be rendered on background points.
**Validates: Requirements 10.1**

### Property 16: Focal Object Labeling
*For any* atlas panel, exactly one focal object (target country, language, or model) SHALL be labeled with a distinctive marker and text label.
**Validates: Requirements 10.2**

### Property 17: Top-K Labeling Constraint
*For any* atlas panel with more than 10 foreground points, at most K extreme points (default K=5) plus the focal object SHALL have text labels, where K is configurable.
**Validates: Requirements 10.3**

### Property 18: FigS1 Special Handling
*For any* generation of FigS1 IVS reference map, the output SHALL be a single full-page PDF (not a 3×3 atlas panel), and SHALL label 10-15 representative countries.
**Validates: Requirements 10.5**

### Property 19: No Panel Legends
*For any* atlas panel in S2-A1, S2-A2, S3-B1 through S3-B5, the panel SHALL NOT contain a legend box; legends SHALL only appear on atlas cover pages.
**Validates: Requirements 10.6, 11.4**

### Property 20: Cover Page Presence
*For any* generated atlas PDF, page 0 SHALL be a cover page containing the atlas title, total figure count, complete color legends, and labeling policy explanation.
**Validates: Requirements 11.1, 11.2, 11.3**

### Property 21: Multi-Part Cover Pages
*For any* atlas split into multiple parts (e.g., part01, part02), each part SHALL include its own cover page with identical legend information.
**Validates: Requirements 11.5**

### Property 22: Source Row ID Completeness
*For any* entry in atlas_index.csv, the source_table_row_id column SHALL contain either a valid row ID from Table_S7, a semicolon-separated list of row IDs, or "N/A" if not determinable.
**Validates: Requirements 12.1, 12.2, 12.3**

### Property 23: README Accuracy
*For any* update to SI/figures/README.md, the document SHALL contain the exact phrases "color-blind safe + grayscale-robust (shape/edge differentiation)" and "Foreground (LLM) ≤ 50; IVS background shown with transparency ≤ 0.15".
**Validates: Requirements 13.1, 13.2**

## Error Handling

| Error Condition | Handling Strategy |
|-----------------|-------------------|
| Missing figure file | Skip, log warning, continue |
| Corrupted PDF/PNG | Skip, log warning, continue |
| Missing PCA data for entity | Use NaN in index, mark as missing |
| Missing consistency data | Exclude from scatter plot, note in caption |
| PDF write permission error | Retry once, then fail with clear message |
| Memory overflow (large Atlas) | Split into smaller parts proactively |

## Testing Strategy

### Unit Testing
- Test filename parsing with various filename formats
- Test grid layout calculation for different figure counts
- Test page header formatting
- Test index CSV structure validation

### Property-Based Testing
The following property-based tests will be implemented using `hypothesis` (Python PBT library):

1. **Grid Layout Property Test**: Generate random figure counts (1-2000), verify page count = ceil(N/9)
2. **Filename Parsing Round-Trip**: Generate random model/country/language strings, create filename, parse back, verify equality
3. **Index Completeness Test**: Generate random Atlas entries, verify all required columns present
4. **Heatmap Consistency Test**: Generate multiple heatmaps, verify colormap parameters match
5. **Variance Sum Test**: Generate random variance values, verify sum ≈ 100%

Each property-based test will run a minimum of 100 iterations.

Test files will be tagged with the format: `**Feature: si-atlas-summary-figures, Property {number}: {property_text}**`
