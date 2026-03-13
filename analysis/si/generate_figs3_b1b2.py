"""
Generate FigS3 B1 and B2 figures.

B1: Per model (language-averaged) - shows model's imitation across all countries/regions
    Color: Cultural region
    Labels: Country/region names
    
B2: Per country/region (model-averaged) - shows how country/region is imitated by all models
    Color: Model
    Feature: Gold star for real IVS coordinates
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import pandas as pd
import matplotlib.pyplot as plt

from si_config import (
    PROJECT_ROOT, load_ivs_data, load_roleplay_data, get_global_axis_limits,
    get_country_region, get_model_color, plot_ivs_background, plot_country_star,
    setup_axes, save_figure, safe_filename, add_jitter,
    create_region_legend, create_model_legend, generate_grid,
    REGION_COLORS, ADJUSTTEXT_AVAILABLE, ADJUST_TEXT_PARAMS,
    POINT_SIZE_SMALL, POINT_SIZE_MEDIUM, FONT_SIZE_COUNTRY_LABEL_SMALL, ALPHA_FG
)

if ADJUSTTEXT_AVAILABLE:
    from adjustText import adjust_text


def plot_b1_panel(ax, model: str, roleplay_data: pd.DataFrame, ivs_data: pd.DataFrame,
                  xlim: tuple, ylim: tuple, add_labels: bool = True):
    """Plot B1 panel: One model, all countries/regions (language-averaged) with labels."""
    plot_ivs_background(ax, ivs_data, alpha=0.12)
    
    model_data = roleplay_data[roleplay_data['model_name'] == model]
    country_avg = model_data.groupby('country').agg({'PC1': 'mean', 'PC2': 'mean'}).reset_index()
    
    texts = []
    for _, row in country_avg.iterrows():
        region = get_country_region(row['country'], ivs_data)
        color = REGION_COLORS.get(region, '#DDDDDD')
        ax.scatter(row['PC1'], row['PC2'], c=color, s=POINT_SIZE_SMALL, marker='o', 
                   alpha=ALPHA_FG, edgecolors='black', linewidths=0.4, zorder=3)
        
        if add_labels:
            text = ax.text(row['PC1'], row['PC2'], row['country'],
                          fontsize=FONT_SIZE_COUNTRY_LABEL_SMALL, 
                          ha='center', va='bottom', alpha=0.7, zorder=4)
            texts.append(text)
    
    if add_labels and ADJUSTTEXT_AVAILABLE and len(texts) > 0:
        adjust_text(texts, ax=ax, **ADJUST_TEXT_PARAMS)
    
    short_name = model.split('/')[-1] if '/' in model else model
    setup_axes(ax, xlim, ylim, title=short_name)


def plot_b2_panel(ax, country: str, roleplay_data: pd.DataFrame, ivs_data: pd.DataFrame,
                  xlim: tuple, ylim: tuple):
    """Plot B2 panel: One country/region, all models (language-averaged per model)."""
    plot_ivs_background(ax, ivs_data, alpha=0.12)
    
    # Mark target country in IVS with gold star
    plot_country_star(ax, country, ivs_data)
    
    country_data = roleplay_data[roleplay_data['country'] == country]
    model_avg = country_data.groupby('model_name').agg({'PC1': 'mean', 'PC2': 'mean'}).reset_index()
    
    for _, row in model_avg.iterrows():
        color = get_model_color(row['model_name'])
        # Add jitter to reduce overlap
        jx, jy = add_jitter(row['PC1'], row['PC2'])
        ax.scatter(jx, jy, c=color, s=POINT_SIZE_MEDIUM, marker='o', 
                   alpha=ALPHA_FG, edgecolors='black', linewidths=0.5, zorder=3)
    
    setup_axes(ax, xlim, ylim, title=country)


def main():
    print("=" * 60)
    print("Generating FigS3 B1 & B2")
    print("=" * 60)
    
    ivs_data = load_ivs_data()
    roleplay_data = load_roleplay_data()
    xlim, ylim = get_global_axis_limits(ivs_data, roleplay_data)
    
    base_dir = PROJECT_ROOT / 'SI' / 'figures' / 'S3_Imitated_contextual_values'
    
    # B1: Per Model
    print("\n--- B1: Per Model (Language-Averaged) ---")
    b1_dir = base_dir / 'B1_per_model_languageAvg'
    panels_dir = b1_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    
    models = sorted(roleplay_data['model_name'].unique())
    for model in models:
        fig, ax = plt.subplots(figsize=(6, 5))
        plot_b1_panel(ax, model, roleplay_data, ivs_data, xlim, ylim, add_labels=True)
        ax.set_xlabel('PC1', fontsize=9)
        ax.set_ylabel('PC2', fontsize=9)
        save_figure(fig, panels_dir / f'FigS3B1_{safe_filename(model)}')
    print(f"Generated {len(models)} B1 panels")
    
    generate_grid(
        models,
        lambda ax, m: plot_b1_panel(ax, m, roleplay_data, ivs_data, xlim, ylim, add_labels=False),
        b1_dir / 'FigS3B1_grid',
        'B1: Per Model (Language-Averaged)',
        legend_handles=create_region_legend(),
        legend_title='Cultural Region'
    )
    
    # B2: Per Country/Region
    print("\n--- B2: Per Country/Region (Model-Averaged) ---")
    b2_dir = base_dir / 'B2_per_country_modelAvg'
    panels_dir = b2_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    
    countries = sorted(roleplay_data['country'].unique())
    for country in countries:
        fig, ax = plt.subplots(figsize=(5, 4))
        plot_b2_panel(ax, country, roleplay_data, ivs_data, xlim, ylim)
        ax.set_xlabel('PC1', fontsize=9)
        ax.set_ylabel('PC2', fontsize=9)
        save_figure(fig, panels_dir / f'FigS3B2_{safe_filename(country)}')
    print(f"Generated {len(countries)} B2 panels")
    
    generate_grid(
        countries,
        lambda ax, c: plot_b2_panel(ax, c, roleplay_data, ivs_data, xlim, ylim),
        b2_dir / 'FigS3B2_grid',
        'B2: Per Country/Region (Model-Averaged)',
        legend_handles=create_model_legend(models),
        legend_title='Model',
        legend_loc='right'
    )
    
    print("\nDone!")


if __name__ == '__main__':
    main()
