"""
Unified configuration for all SI (Supplementary Information) figures.

This module provides:
- Unified color definitions for regions, languages, and models
- Unified point sizes, font sizes, and other styles
- Country name mappings
- Common data loading and plotting utilities

All S1, S2, S3 scripts should import from this module to ensure consistency.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math

# =============================================================================
# Project Paths
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
SI_DIR = PROJECT_ROOT / 'SI'
PCA_DIR = SI_DIR / 'pca'
FIGURES_DIR = SI_DIR / 'figures'
SM_FIGURES_DIR = PROJECT_ROOT / 'Supplementary Materials' / 'figures'

DATA_DIR = PROJECT_ROOT / 'data'
DATA_COUNTRY_VALUES = DATA_DIR / 'country_values'
DATA_LLM_PCA_INTRINSIC = DATA_DIR / 'llm_pca' / 'intrinsic'
DATA_LLM_PCA_MULTILINGUAL = DATA_DIR / 'llm_pca' / 'multilingual'

# Add project root to path
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# adjustText availability
# =============================================================================
try:
    from adjustText import adjust_text
    ADJUSTTEXT_AVAILABLE = True
except ImportError:
    ADJUSTTEXT_AVAILABLE = False
    print("Warning: adjustText not installed. Labels may overlap.")
    print("Install with: pip install adjustText")


# =============================================================================
# Color Definitions - Cultural Regions (Inglehart–Welzel style, vivid)
# =============================================================================
REGION_COLORS = {
    # 尽量贴近 WVS 官方地图的配色，整体更鲜艳，对比度强
    'Confucian':        '#E67E22',  # bright orange
    'Protestant Europe':'#F1C40F',  # bright yellow
    'Latin America':    '#1ABC9C',  # teal / turquoise
    'Catholic Europe':  '#27AE60',  # vivid green
    'English-Speaking': '#F4D03F',  # warm yellow
    'African-Islamic':  '#7F8C8D',  # medium gray
    'West & South Asia':'#D35400',  # deep orange
    'Orthodox Europe':  '#C0392B',  # deep red
    'Other':            '#BDC3C7',  # light gray
}

# =============================================================================
# Color Definitions - Languages
# =============================================================================
LANGUAGE_COLORS = {
    # Primary languages (6 UN languages)
    'en': '#E41A1C',        # Red - English
    'en-native': '#C41A1C', # Darker Red - English (native)
    'zh-cn': '#377EB8',     # Blue - Chinese (Simplified)
    'zh-tw': '#2E6A9E',     # Darker Blue - Chinese (Traditional)
    'zh-hk': '#5A9BD4',     # Lighter Blue - Chinese (HK)
    'es': '#4DAF4A',        # Green - Spanish
    'fr': '#984EA3',        # Purple - French
    'ar': '#FF7F00',        # Orange - Arabic
    'ru': '#A65628',        # Brown - Russian
    # Additional languages
    'de': '#66C2A5',        # Teal - German
    'ja': '#FC8D62',        # Salmon - Japanese
    'ko': '#8DA0CB',        # Light Purple - Korean
    'it': '#E78AC3',        # Pink - Italian
    'pt': '#B3DE69',        # Light Green - Portuguese
}

LANGUAGE_NAMES = {
    'en': 'English',
    'en-native': 'English (native)',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'zh-hk': 'Chinese (HK)',
    'es': 'Spanish',
    'fr': 'French',
    'ar': 'Arabic',
    'ru': 'Russian',
    'de': 'German',
    'ja': 'Japanese',
    'ko': 'Korean',
    'it': 'Italian',
    'pt': 'Portuguese',
}

# =============================================================================
# Color Definitions - Models (grouped by vendor)
# =============================================================================
MODEL_COLORS = {
    # OpenAI - Blue family
    'gpt-4o': '#1E3A8A',
    'gpt-4o-mini': '#3B82F6',
    'gpt-5.1': '#60A5FA',
    'openai/gpt-5.1': '#60A5FA',
    # Anthropic - Purple family
    'claude-3-7-sonnet-20250219': '#7C3AED',
    'claude-sonnet-4.5': '#A78BFA',
    'anthropic/claude-sonnet-4.5': '#A78BFA',
    # Google - Green family
    'gemini-2.5-flash': '#047857',
    'gemini-2.5-pro': '#10B981',
    'gemini-3-pro-preview': '#34D399',
    'gemma-3-4b-it': '#6EE7B7',
    'google/gemini-2.5-flash': '#047857',
    'google/gemini-2.5-pro': '#10B981',
    'google/gemini-3-pro-preview': '#34D399',
    'google/gemma-3-4b-it': '#6EE7B7',
    # Meta - Red family
    'llama-3.2-3b-instruct': '#DC2626',
    'llama-3.3-70b-instruct': '#F87171',
    'meta-llama/llama-3.2-3b-instruct': '#DC2626',
    'meta-llama/llama-3.3-70b-instruct': '#F87171',
    # Mistral - Orange family
    'mistral-medium-3.1': '#EA580C',
    'mistral-nemo': '#FB923C',
    'mistralai/mistral-medium-3.1': '#EA580C',
    'mistralai/mistral-nemo': '#FB923C',
    # DeepSeek - Cyan family
    'deepseek-chat': '#0891B2',
    'deepseek-chat-v3.1': '#22D3EE',
    'deepseek/deepseek-chat-v3.1': '#22D3EE',
    # Qwen - Yellow family
    'qwen3-1.7b': '#CA8A04',
    'qwen3-max': '#FACC15',
    'qwq-32b': '#FDE047',
    'qwen/qwen3-max': '#FACC15',
    'qwen/qwq-32b': '#FDE047',
    # Others
    'grok-4.1-fast': '#6B7280',
    'x-ai/grok-4.1-fast': '#6B7280',
    'doubao-1-5-pro-32k-250115': '#DB2777',
    'kimi-k2': '#92400E',
    'phi-3-mini-128k-instruct': '#65A30D',
    'microsoft/phi-3-mini-128k-instruct': '#65A30D',
    'glm-4.6': '#0EA5E9',
    'z-ai/glm-4.6': '#0EA5E9',
}


# =============================================================================
# Point Size Constants
# =============================================================================
POINT_SIZE_BG = 20        # IVS background points
POINT_SIZE_SMALL = 40     # Small foreground points (many points per panel)
POINT_SIZE_MEDIUM = 60    # Medium foreground points
POINT_SIZE_LARGE = 80     # Large foreground points (few points per panel)
POINT_SIZE_STAR = 150     # Gold star for focal country/region
POINT_SIZE_S1 = 80        # S1 main figure points

# Jitter amount for overlapping points
JITTER_AMOUNT = 0.08


# =============================================================================
# Font Size Constants
# =============================================================================
FONT_SIZE_TITLE = 14
FONT_SIZE_SUBTITLE = 12
FONT_SIZE_PANEL_TITLE = 8
FONT_SIZE_AXIS_LABEL = 11
FONT_SIZE_TICK = 7
FONT_SIZE_LEGEND = 9
FONT_SIZE_COUNTRY_LABEL = 7
FONT_SIZE_COUNTRY_LABEL_SMALL = 4


# =============================================================================
# Line Style Constants
# =============================================================================
LINE_WIDTH_EDGE = 0.5
LINE_WIDTH_EDGE_THIN = 0.4
LINE_WIDTH_DASHED = 1.0
LINE_WIDTH_ARROW = 0.3
ALPHA_BG = 0.15
ALPHA_FG = 0.85
ALPHA_DASHED_LINE = 0.6


# =============================================================================
# adjustText Parameters (optimized for label overlap reduction)
# =============================================================================
ADJUST_TEXT_PARAMS = {
    'arrowprops': dict(arrowstyle='-', color='gray', lw=0.3, alpha=0.4),
    'expand_points': (1.8, 1.8),
    'expand_text': (1.3, 1.3),
    'force_points': (0.8, 0.8),
    'force_text': (0.8, 0.8),
    'lim': 800,
    'only_move': {'points': 'y', 'texts': 'xy'}
}

ADJUST_TEXT_PARAMS_STRONG = {
    'arrowprops': dict(arrowstyle='-', color='gray', lw=0.5, alpha=0.5),
    'expand_points': (2.0, 2.0),
    'expand_text': (1.5, 1.5),
    'force_points': (1.0, 1.0),
    'force_text': (1.0, 1.0),
    'lim': 1000,
    'only_move': {'points': 'y', 'texts': 'xy'}
}


# =============================================================================
# Boundary Rendering Constants
# =============================================================================
# Visual styling for cultural region boundaries (WVS-style filled regions)
BOUNDARY_LINE_WIDTH = 2.5      # Width of boundary lines in points
BOUNDARY_LINE_ALPHA = 0.8      # Transparency of boundary lines (0-1)
BOUNDARY_FILL_ALPHA = 0.35     # Transparency of boundary fill (0-1) - increased for more visible colors
BOUNDARY_ZORDER = 1            # Z-order: below points (2) and labels (3), above grid (0)
BOUNDARY_MIN_POINTS = 3        # Minimum points needed to draw a boundary


# =============================================================================
# Model Exclusion Filter (unified 20-model set)
# =============================================================================
EXCLUDED_MODELS = {"qwen3-1.7b", "glm-4.6", "qwq-32b"}

def _exclude_models(df: pd.DataFrame, col: str = "model_name") -> pd.DataFrame:
    """Remove rows matching any excluded model (case-insensitive substring)."""
    if col not in df.columns:
        return df
    mask = df[col].str.lower().apply(
        lambda x: not any(ex in x for ex in EXCLUDED_MODELS)
    )
    return df[mask].reset_index(drop=True)


# =============================================================================
# Data Loading Functions
# =============================================================================

def _resolve_pca_path(filename: str, primary_dir: Path, fallback_dir: Path = None) -> Path:
    """Find a PCA CSV in project data first, then fall back to SI/pca."""
    primary = primary_dir / filename
    if primary.exists():
        return primary
    if fallback_dir:
        fallback = fallback_dir / filename
        if fallback.exists():
            return fallback
    raise FileNotFoundError(
        f"{filename} not found in {primary_dir} or {fallback_dir}")


def load_ivs_data() -> pd.DataFrame:
    """Load IVS PCA coordinates (data/country_values/ first, SI/pca/ fallback)."""
    ivs_path = _resolve_pca_path(
        'Table_S5_IVS_PCA_coordinates.csv', DATA_COUNTRY_VALUES, PCA_DIR)
    df = pd.read_csv(ivs_path)
    df = df.dropna(subset=['country']).drop_duplicates(subset=['country'])
    return df


def load_baseline_data() -> pd.DataFrame:
    """Load LLM baseline PCA coordinates, filtered to 20 models."""
    baseline_path = _resolve_pca_path(
        'Table_S6_LLM_baseline_PCA_coordinates.csv',
        DATA_LLM_PCA_INTRINSIC, PCA_DIR)
    df = pd.read_csv(baseline_path)
    return _exclude_models(df)


def load_roleplay_data() -> pd.DataFrame:
    """Load LLM roleplay PCA coordinates, filtered to 20 models."""
    roleplay_path = _resolve_pca_path(
        'Table_S7_LLM_roleplay_PCA_coordinates.csv',
        DATA_LLM_PCA_MULTILINGUAL, PCA_DIR)
    df = pd.read_csv(roleplay_path)
    return _exclude_models(df)


# =============================================================================
# Axis Limits Functions
# =============================================================================

def get_global_axis_limits(*dataframes, padding: float = 0.5) -> tuple:
    """Calculate global axis limits from multiple dataframes."""
    pc1_min = min(df['PC1'].min() for df in dataframes)
    pc1_max = max(df['PC1'].max() for df in dataframes)
    pc2_min = min(df['PC2'].min() for df in dataframes)
    pc2_max = max(df['PC2'].max() for df in dataframes)
    return (pc1_min - padding, pc1_max + padding), (pc2_min - padding, pc2_max + padding)


# =============================================================================
# Color Helper Functions
# =============================================================================

def get_region_color(region: str) -> str:
    """Get color for a cultural region."""
    if pd.isna(region):
        return REGION_COLORS.get('Other', '#DDDDDD')
    return REGION_COLORS.get(region, '#DDDDDD')


def get_country_region(country: str, ivs_data: pd.DataFrame) -> str:
    """Get cultural region for a country from IVS data."""
    match = ivs_data[ivs_data['country'] == country]
    if len(match) > 0:
        region = match.iloc[0]['cultural_region']
        return region if pd.notna(region) else 'Other'
    return 'Other'


def get_language_color(language: str) -> str:
    """Get color for a language."""
    return LANGUAGE_COLORS.get(language, '#888888')


def get_model_color(model: str) -> str:
    """Get color for a model, with fallback."""
    if model in MODEL_COLORS:
        return MODEL_COLORS[model]
    # Try without vendor prefix
    short_name = model.split('/')[-1] if '/' in model else model
    if short_name in MODEL_COLORS:
        return MODEL_COLORS[short_name]
    # Fallback based on vendor
    if 'gpt' in model.lower():
        return '#3B82F6'
    elif 'claude' in model.lower():
        return '#7C3AED'
    elif 'gemini' in model.lower() or 'gemma' in model.lower():
        return '#10B981'
    elif 'llama' in model.lower():
        return '#DC2626'
    elif 'mistral' in model.lower():
        return '#EA580C'
    elif 'deepseek' in model.lower():
        return '#0891B2'
    elif 'qwen' in model.lower():
        return '#CA8A04'
    return '#888888'


def get_language_name(language: str) -> str:
    """Get display name for a language."""
    return LANGUAGE_NAMES.get(language, language)


def get_short_model_name(model: str) -> str:
    """Get model name without vendor prefix for display."""
    return model.split('/')[-1] if '/' in model else model


def add_jitter(x: float, y: float, amount: float = JITTER_AMOUNT) -> tuple:
    """Add small random jitter to coordinates to reduce overlap."""
    jx = x + np.random.uniform(-amount, amount)
    jy = y + np.random.uniform(-amount, amount)
    return jx, jy


# =============================================================================
# Common Plotting Functions
# =============================================================================

def plot_ivs_background(ax, ivs_data: pd.DataFrame, alpha: float = ALPHA_BG, 
                        draw_boundaries: bool = True):
    """
    Plot IVS countries as subtle background with optional cultural region boundaries.
    
    Args:
        ax: Matplotlib axis
        ivs_data: DataFrame with IVS PCA coordinates
        alpha: Alpha transparency for country points
        draw_boundaries: Whether to draw cultural region boundaries (default: True)
    """
    # Import boundary functions (lazy import to avoid circular dependencies)
    if draw_boundaries:
        try:
            from boundary_utils_ml import generate_ml_boundaries, plot_decision_boundaries_masked
            
            # Regions to include (exclude Other and Baltic)
            excluded_regions = {'Other', 'Baltic'}
            regions = sorted([r for r in ivs_data['cultural_region'].unique() 
                            if pd.notna(r) and r not in excluded_regions])
            
            # Prepare data for ML classifier
            ml_data = ivs_data[ivs_data['cultural_region'].isin(regions)].copy()
            ml_data = ml_data[['PC1', 'PC2', 'cultural_region']].dropna()
            
            # Generate and plot ML boundaries
            clf, le, xx, yy = generate_ml_boundaries(
                ml_data,
                REGION_COLORS,
                method='svm',
                resolution=200
            )
            
            # Plot decision boundaries (masked to only show near data points)
            plot_decision_boundaries_masked(
                ax, clf, le, xx, yy,
                ml_data,
                REGION_COLORS,
                alpha=BOUNDARY_FILL_ALPHA,
                mask_padding=0.5
            )
        except Exception as e:
            # Silently fall back to no boundaries if there's an error
            pass
    
    # Plot country points
    for region in ivs_data['cultural_region'].dropna().unique():
        subset = ivs_data[ivs_data['cultural_region'] == region]
        color = REGION_COLORS.get(region, '#DDDDDD')
        ax.scatter(subset['PC1'], subset['PC2'],
                   c=color, s=POINT_SIZE_BG, marker='o', alpha=alpha,
                   edgecolors='none', zorder=1)


def plot_country_star(ax, country: str, ivs_data: pd.DataFrame):
    """Plot gold star marker for a specific country's real IVS coordinates."""
    ivs_country = ivs_data[ivs_data['country'] == country]
    if len(ivs_country) > 0:
        ax.scatter(ivs_country['PC1'].values[0], ivs_country['PC2'].values[0],
                   marker='*', s=POINT_SIZE_STAR, c='gold', 
                   edgecolors='black', linewidths=1, zorder=5)
        return ivs_country['PC1'].values[0], ivs_country['PC2'].values[0]
    return None, None


def plot_dashed_line(ax, x1: float, y1: float, x2: float, y2: float, 
                     color: str = 'gray', alpha: float = ALPHA_DASHED_LINE):
    """Plot dashed line connecting two points."""
    ax.plot([x1, x2], [y1, y2], linestyle='--', color=color, 
            linewidth=LINE_WIDTH_DASHED, alpha=alpha, zorder=2)


def setup_axes(ax, xlim: tuple, ylim: tuple, title: str = None, 
               fontsize: int = FONT_SIZE_PANEL_TITLE):
    """Setup axes with consistent styling."""
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.tick_params(labelsize=FONT_SIZE_TICK)
    if title:
        ax.set_title(title, fontsize=fontsize, pad=3)


def set_publication_style():
    """Apply seaborn/matplotlib defaults for SI figure scripts."""
    import seaborn as sns
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 100,
            "savefig.dpi": 300,
            "font.size": 11,
        }
    )


def save_figure(fig, output_path: Path, close: bool = True):
    """Save figure as both PNG and PDF (to SI/ and Supplementary Materials/)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    fig.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')

    # Mirror to Supplementary Materials/figures/
    try:
        rel = output_path.relative_to(FIGURES_DIR)
        sm_path = SM_FIGURES_DIR / rel
        sm_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(sm_path.with_suffix('.png'), dpi=300, bbox_inches='tight')
        fig.savefig(sm_path.with_suffix('.pdf'), bbox_inches='tight')
    except (ValueError, OSError):
        pass

    if close:
        plt.close(fig)


def safe_filename(name: str) -> str:
    """Convert name to safe filename by replacing problematic characters."""
    return name.replace('/', '_').replace('\\', '_').replace('.', '-').replace(' ', '_')


# =============================================================================
# Legend Creation Functions
# =============================================================================

def create_region_legend() -> list:
    """Create legend handles for cultural regions."""
    handles = []
    for region, color in REGION_COLORS.items():
        if region != 'Other':
            handles.append(Line2D([0], [0], marker='o', color='w',
                                 markerfacecolor=color, markersize=8,
                                 markeredgecolor='black', markeredgewidth=0.5,
                                 label=region))
    return handles


def create_language_legend(languages: list = None) -> list:
    """Create legend handles for languages."""
    handles = []
    if languages is None:
        # Include all languages with distinct colors
        languages = ['en', 'en-native', 'zh-cn', 'zh-tw', 'zh-hk', 
                     'es', 'fr', 'ar', 'ru', 'de', 'ja', 'ko', 'it', 'pt']
    
    for lang in languages:
        if lang in LANGUAGE_COLORS:
            color = LANGUAGE_COLORS[lang]
            name = LANGUAGE_NAMES.get(lang, lang)
            handles.append(Line2D([0], [0], marker='o', color='w',
                                 markerfacecolor=color, markersize=8,
                                 markeredgecolor='black', markeredgewidth=0.5,
                                 label=name))
    return handles


def create_model_legend(models: list) -> list:
    """Create legend handles for specific models."""
    handles = []
    for model in sorted(set(models)):
        color = get_model_color(model)
        short_name = get_short_model_name(model)
        handles.append(Line2D([0], [0], marker='o', color='w',
                             markerfacecolor=color, markersize=6,
                             markeredgecolor='black', markeredgewidth=0.4,
                             label=short_name))
    return handles


# =============================================================================
# Grid Generation Function
# =============================================================================

def generate_grid(items: list, plot_func, output_path: Path, title: str,
                  legend_handles: list = None, legend_title: str = None, 
                  legend_loc: str = 'bottom',
                  n_cols: int = 3, n_rows: int = 3):
    """
    Generate grid figures (9 per page) with shared axis labels and legend.
    
    Args:
        items: List of items to plot (one per panel)
        plot_func: Function(ax, item) to plot each panel
        output_path: Base path for output files
        title: Figure title
        legend_handles: Legend handles
        legend_title: Legend title
        legend_loc: 'bottom' or 'right'
        n_cols: Number of columns per page
        n_rows: Number of rows per page
    """
    items_per_page = n_cols * n_rows
    n_pages = math.ceil(len(items) / items_per_page)
    
    for page in range(n_pages):
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(items))
        page_items = items[start_idx:end_idx]
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3.5, n_rows * 3 + 1))
        axes = axes.flatten()
        
        for i, item in enumerate(page_items):
            plot_func(axes[i], item)
        
        # Hide empty subplots
        for i in range(len(page_items), len(axes)):
            axes[i].set_visible(False)
        
        # Add shared axis labels
        fig.text(0.5, 0.02, 'PC1 (Survival → Self-Expression)', ha='center', fontsize=FONT_SIZE_AXIS_LABEL)
        fig.text(0.02, 0.5, 'PC2 (Traditional → Secular-Rational)', va='center',
                 rotation='vertical', fontsize=FONT_SIZE_AXIS_LABEL)
        
        # Add legend
        if legend_handles:
            if legend_loc == 'bottom':
                ncol = min(len(legend_handles), 6)
                fig.legend(handles=legend_handles, loc='lower center', ncol=ncol,
                          fontsize=7, framealpha=0.95, title=legend_title,
                          bbox_to_anchor=(0.5, -0.02))
                rect = [0.04, 0.08, 1, 0.96]
            else:  # right
                fig.legend(handles=legend_handles, loc='center right', ncol=1,
                          fontsize=6, framealpha=0.95, title=legend_title,
                          bbox_to_anchor=(1.15, 0.5))
                rect = [0.04, 0.04, 0.88, 0.96]
        else:
            rect = [0.04, 0.04, 1, 0.96]
        
        fig.suptitle(f'{title} (Page {page + 1}/{n_pages})', fontsize=FONT_SIZE_SUBTITLE, fontweight='bold', y=0.98)
        plt.tight_layout(rect=rect)
        
        suffix = f'_page{page + 1:02d}' if n_pages > 1 else ''
        save_figure(fig, Path(str(output_path) + suffix))
    
    print(f"✅ Generated {n_pages} grid page(s) for {title}")
