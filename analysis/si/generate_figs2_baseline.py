"""
Generate FigS2: Baseline Intrinsic Values figures.

S2-A1: Per model, showing language stability (color = language)
S2-A2: Per language, showing model distribution (color = model)

Output:
- SI/figures/S2_Baseline_intrinsic_values/A1_per_model/
- SI/figures/S2_Baseline_intrinsic_values/A2_per_language/
"""

import sys
from pathlib import Path

# Add paths for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import math
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from si_config import (
    PROJECT_ROOT, FIGURES_DIR,
    load_ivs_data, load_baseline_data, get_global_axis_limits,
    plot_ivs_background, save_figure, get_model_color,
    REGION_COLORS, LANGUAGE_COLORS, LANGUAGE_NAMES, MODEL_COLORS,
    POINT_SIZE_MEDIUM, POINT_SIZE_BG, ALPHA_BG, ADJUSTTEXT_AVAILABLE
)


def plot_s2a1_panel(ax, model, baseline_data, ivs_data, xlim, ylim, show_title=True):
    """Plot S2-A1 panel: One model, multiple languages. Color = Language"""
    plot_ivs_background(ax, ivs_data, alpha=ALPHA_BG)
    
    model_data = baseline_data[baseline_data['model_name'] == model]
    
    for lang in model_data['language'].unique():
        lang_data = model_data[model_data['language'] == lang]
        color = LANGUAGE_COLORS.get(lang, '#888888')
        ax.scatter(lang_data['PC1'], lang_data['PC2'],
                   c=color, s=POINT_SIZE_MEDIUM, marker='o', alpha=0.9,
                   edgecolors='black', linewidths=0.8, zorder=3)
    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.tick_params(labelsize=7)
    
    if show_title:
        short_name = model.split('/')[-1] if '/' in model else model
        ax.set_title(short_name, fontsize=8, pad=3)


def plot_s2a2_panel(ax, language, baseline_data, ivs_data, xlim, ylim, show_title=True):
    """Plot S2-A2 panel: One language, multiple models. Color = Model"""
    plot_ivs_background(ax, ivs_data, alpha=ALPHA_BG)
    
    lang_data = baseline_data[baseline_data['language'] == language]
    
    for model in lang_data['model_name'].unique():
        model_subset = lang_data[lang_data['model_name'] == model]
        color = get_model_color(model)
        ax.scatter(model_subset['PC1'], model_subset['PC2'],
                   c=color, s=POINT_SIZE_MEDIUM, marker='o', alpha=0.9,
                   edgecolors='black', linewidths=0.8, zorder=3)
    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.tick_params(labelsize=7)
    
    if show_title:
        lang_name = LANGUAGE_NAMES.get(language, language)
        ax.set_title(lang_name, fontsize=9, pad=3)


def create_language_legend():
    """Create legend handles for languages."""
    handles = []
    for lang, color in LANGUAGE_COLORS.items():
        name = LANGUAGE_NAMES.get(lang, lang)
        handles.append(Line2D([0], [0], marker='o', color='w', 
                             markerfacecolor=color, markersize=10,
                             markeredgecolor='black', markeredgewidth=0.8,
                             label=name))
    return handles


def create_model_legend(models):
    """Create legend handles for models."""
    handles = []
    for model in sorted(models):
        color = get_model_color(model)
        short_name = model.split('/')[-1] if '/' in model else model
        handles.append(Line2D([0], [0], marker='o', color='w',
                             markerfacecolor=color, markersize=8,
                             markeredgecolor='black', markeredgewidth=0.6,
                             label=short_name))
    return handles


def generate_s2a1_panels(baseline_data, ivs_data, xlim, ylim, output_dir):
    """Generate individual S2-A1 panels."""
    panels_dir = output_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    
    models = sorted(baseline_data['model_name'].unique())
    
    for model in models:
        fig, ax = plt.subplots(figsize=(6, 5))
        plot_s2a1_panel(ax, model, baseline_data, ivs_data, xlim, ylim)
        ax.set_xlabel('PC1', fontsize=10)
        ax.set_ylabel('PC2', fontsize=10)
        
        safe_name = model.replace('/', '_').replace('\\', '_')
        plt.tight_layout()
        save_figure(fig, panels_dir / f'FigS2A1_{safe_name}')
    
    print(f"✅ Generated {len(models)} S2-A1 panels")


def generate_s2a2_panels(baseline_data, ivs_data, xlim, ylim, output_dir):
    """Generate individual S2-A2 panels."""
    panels_dir = output_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    
    languages = sorted(baseline_data['language'].unique())
    
    for lang in languages:
        fig, ax = plt.subplots(figsize=(6, 5))
        plot_s2a2_panel(ax, lang, baseline_data, ivs_data, xlim, ylim)
        ax.set_xlabel('PC1', fontsize=10)
        ax.set_ylabel('PC2', fontsize=10)
        
        plt.tight_layout()
        save_figure(fig, panels_dir / f'FigS2A2_{lang}')
    
    print(f"✅ Generated {len(languages)} S2-A2 panels")


def generate_s2a1_grid(baseline_data, ivs_data, xlim, ylim, output_dir):
    """Generate S2-A1 grid: All models, color by language."""
    models = sorted(baseline_data['model_name'].unique())
    n_models = len(models)
    n_cols = 5
    n_rows = math.ceil(n_models / n_cols)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 2.5))
    axes = axes.flatten()
    
    for i, model in enumerate(models):
        plot_s2a1_panel(axes[i], model, baseline_data, ivs_data, xlim, ylim)
    
    for i in range(n_models, len(axes)):
        axes[i].set_visible(False)
    
    legend_handles = create_language_legend()
    fig.legend(handles=legend_handles, loc='lower center', ncol=6,
               fontsize=9, framealpha=0.95, title='Language',
               bbox_to_anchor=(0.5, -0.02))
    
    fig.text(0.5, 0.02, 'PC1 (Survival → Self-Expression)', ha='center', fontsize=11)
    fig.text(0.02, 0.5, 'PC2 (Traditional → Secular-Rational)', va='center', 
             rotation='vertical', fontsize=11)
    
    fig.suptitle('S2-A1: LLM Baseline Values by Model (Language Stability)', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout(rect=[0.03, 0.08, 1, 0.98])
    output_dir.mkdir(parents=True, exist_ok=True)
    save_figure(fig, output_dir / 'FigS2A1_all_models_grid')
    print(f"✅ Generated: FigS2A1_all_models_grid ({n_models} models)")


def generate_s2a2_grid(baseline_data, ivs_data, xlim, ylim, output_dir):
    """Generate S2-A2 grid: All languages, color by model."""
    languages = sorted(baseline_data['language'].unique())
    n_langs = len(languages)
    n_cols = 3
    n_rows = 2
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 4, n_rows * 3.5))
    axes = axes.flatten()
    
    for i, lang in enumerate(languages):
        plot_s2a2_panel(axes[i], lang, baseline_data, ivs_data, xlim, ylim)
    
    for i in range(n_langs, len(axes)):
        axes[i].set_visible(False)
    
    models = baseline_data['model_name'].unique()
    legend_handles = create_model_legend(models)
    fig.legend(handles=legend_handles, loc='center right', 
               fontsize=7, framealpha=0.95, title='Model',
               bbox_to_anchor=(1.15, 0.5))
    
    fig.text(0.5, 0.02, 'PC1 (Survival → Self-Expression)', ha='center', fontsize=11)
    fig.text(0.02, 0.5, 'PC2 (Traditional → Secular-Rational)', va='center',
             rotation='vertical', fontsize=11)
    
    fig.suptitle('S2-A2: LLM Baseline Values by Language (Model Distribution)',
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout(rect=[0.03, 0.05, 0.88, 0.98])
    output_dir.mkdir(parents=True, exist_ok=True)
    save_figure(fig, output_dir / 'FigS2A2_all_languages_grid')
    print(f"✅ Generated: FigS2A2_all_languages_grid ({n_langs} languages)")


def generate_s2_overview(baseline_data, ivs_data, xlim, ylim, output_dir):
    """Generate S2 Overview: All models and all languages in one plot."""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot IVS background
    plot_ivs_background(ax, ivs_data, alpha=ALPHA_BG)
    
    # Plot all baseline data points, colored by language, and add labels for each point
    texts = []
    for _, row in baseline_data.iterrows():
        lang = row['language']
        color = LANGUAGE_COLORS.get(lang, '#888888')
        
        # Plot point
        ax.scatter(row['PC1'], row['PC2'],
                   c=color, s=POINT_SIZE_MEDIUM, marker='o', alpha=0.7,
                   edgecolors='black', linewidths=0.5, zorder=3)
        
        # Add model label for each point
        short_name = row['model_name'].split('/')[-1] if '/' in row['model_name'] else row['model_name']
        # Make label even shorter for better readability
        if len(short_name) > 15:
            short_name = short_name[:12] + '...'
        
        text = ax.text(row['PC1'], row['PC2'], short_name,
                      fontsize=5, ha='center', va='bottom', alpha=0.5, zorder=4)
        texts.append(text)
    
    # Adjust text positions to avoid overlap if adjustText is available
    if ADJUSTTEXT_AVAILABLE and len(texts) > 0:
        from adjustText import adjust_text
        adjust_text(texts, ax=ax,
                   arrowprops=dict(arrowstyle='-', color='gray', lw=0.2, alpha=0.2),
                   expand_points=(1.3, 1.3),
                   expand_text=(1.1, 1.1),
                   force_points=(0.3, 0.3),
                   force_text=(0.3, 0.3),
                   lim=800,
                   only_move={'points': 'y', 'texts': 'xy'})
    
    # Set axis limits and styling
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    
    # Labels and title
    ax.set_xlabel('PC1 (Survival → Self-Expression)', fontsize=12)
    ax.set_ylabel('PC2 (Traditional → Secular-Rational)', fontsize=12)
    ax.set_title('S2 Overview: All LLM Baseline Values (All Models × All Languages)', 
                 fontsize=14, fontweight='bold', pad=15)
    
    # Create two legends: one for languages, one for cultural regions
    language_handles = create_language_legend()
    
    # Create cultural region legend (exclude 'Other' and 'Baltic')
    region_handles = []
    excluded_regions = {'Other', 'Baltic'}
    for region, color in sorted(REGION_COLORS.items()):
        if region not in excluded_regions:
            region_handles.append(Line2D([0], [0], marker='o', color='w',
                                        markerfacecolor=color, markersize=8,
                                        markeredgecolor='black', markeredgewidth=0.5,
                                        label=region, alpha=0.6))
    
    # Add language legend on the right
    legend1 = ax.legend(handles=language_handles, loc='upper left', fontsize=8, 
                       framealpha=0.95, title='Language (LLM Baseline)', 
                       bbox_to_anchor=(1.02, 1.0))
    
    # Add cultural region legend below language legend
    ax.add_artist(legend1)  # Keep first legend
    ax.legend(handles=region_handles, loc='lower left', fontsize=8,
             framealpha=0.95, title='Cultural Region (IVS Background)',
             bbox_to_anchor=(1.02, 0.0))
    
    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    save_figure(fig, output_dir / 'FigS2_Overview_all_models_all_languages')
    
    n_models = baseline_data['model_name'].nunique()
    n_langs = baseline_data['language'].nunique()
    n_points = len(baseline_data)
    print(f"✅ Generated: FigS2_Overview ({n_models} models × {n_langs} languages = {n_points} points)")


def main():
    print("=" * 60)
    print("Generating FigS2: Baseline Intrinsic Values")
    print("=" * 60)
    
    ivs_data = load_ivs_data()
    baseline_data = load_baseline_data()
    
    print(f"IVS: {len(ivs_data)} countries")
    print(f"Baseline: {len(baseline_data)} records, {baseline_data['model_name'].nunique()} models")
    
    xlim, ylim = get_global_axis_limits(ivs_data, baseline_data)
    output_dir = FIGURES_DIR / 'S2_Baseline_intrinsic_values'
    
    print("\nGenerating S2 Overview (all models × all languages)...")
    generate_s2_overview(baseline_data, ivs_data, xlim, ylim, output_dir)
    
    print("\nGenerating S2-A1 (per model)...")
    generate_s2a1_panels(baseline_data, ivs_data, xlim, ylim, output_dir / 'A1_per_model')
    generate_s2a1_grid(baseline_data, ivs_data, xlim, ylim, output_dir / 'A1_per_model')
    
    print("\nGenerating S2-A2 (per language)...")
    generate_s2a2_panels(baseline_data, ivs_data, xlim, ylim, output_dir / 'A2_per_language')
    generate_s2a2_grid(baseline_data, ivs_data, xlim, ylim, output_dir / 'A2_per_language')
    
    print("\n" + "=" * 60)
    print(f"Done! Output: {output_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
