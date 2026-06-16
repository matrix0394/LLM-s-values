"""
Generate FigS3 B4 figures.

B4: Per (country/region, language) - shows model variation for one country/region-language pair
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
    get_model_color, plot_ivs_background, plot_country_star,
    setup_axes, save_figure, safe_filename, add_jitter,
    create_model_legend, generate_grid,
    LANGUAGE_NAMES, POINT_SIZE_MEDIUM, ALPHA_FG
)


def plot_b4_panel(ax, country: str, language: str, roleplay_data: pd.DataFrame,
                  ivs_data: pd.DataFrame, xlim: tuple, ylim: tuple):
    """Plot B4 panel: One country/region, one language, multiple models."""
    plot_ivs_background(ax, ivs_data, alpha=0.12)
    
    # Mark target country in IVS with gold star
    plot_country_star(ax, country, ivs_data)
    
    subset = roleplay_data[(roleplay_data['country'] == country) &
                           (roleplay_data['language'] == language)]
    
    for _, row in subset.iterrows():
        color = get_model_color(row['model_name'])
        # Add jitter to reduce overlap
        jx, jy = add_jitter(row['PC1'], row['PC2'])
        ax.scatter(jx, jy, c=color, s=POINT_SIZE_MEDIUM, marker='o', 
                   alpha=ALPHA_FG, edgecolors='black', linewidths=0.5, zorder=3)
    
    lang_name = LANGUAGE_NAMES.get(language, language)
    setup_axes(ax, xlim, ylim, title=f'{country} | {lang_name}', fontsize=7)


def main():
    print("=" * 60)
    print("Generating FigS3 B4")
    print("=" * 60)
    
    ivs_data = load_ivs_data()
    roleplay_data = load_roleplay_data()
    xlim, ylim = get_global_axis_limits(ivs_data, roleplay_data)
    
    b4_dir = PROJECT_ROOT / 'SI' / 'figures' / 'S3_Imitated_contextual_values' / 'B4_per_country_per_language'
    panels_dir = b4_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    
    combinations = roleplay_data.groupby(['country', 'language']).size().reset_index(name='count')
    print(f"Total combinations: {len(combinations)}")
    
    all_models = roleplay_data['model_name'].unique()
    
    count = 0
    for _, row in combinations.iterrows():
        country, language = row['country'], row['language']
        
        fig, ax = plt.subplots(figsize=(5, 4))
        plot_b4_panel(ax, country, language, roleplay_data, ivs_data, xlim, ylim)
        ax.set_xlabel('PC1', fontsize=9)
        ax.set_ylabel('PC2', fontsize=9)
        
        save_figure(fig, panels_dir / f'FigS3B4_{safe_filename(country)}__{language}')
        count += 1
        
        if count % 50 == 0:
            print(f"  Generated {count} panels...")
    
    print(f"Generated {count} B4 panels")
    
    combo_list = list(combinations[['country', 'language']].itertuples(index=False))
    generate_grid(
        combo_list,
        lambda ax, cl: plot_b4_panel(ax, cl[0], cl[1], roleplay_data, ivs_data, xlim, ylim),
        b4_dir / 'FigS3B4_grid',
        'B4: Per (Country/Region, Language)',
        legend_handles=create_model_legend(all_models),
        legend_title='Model',
        legend_loc='right'
    )
    
    print("\nDone!")


if __name__ == '__main__':
    main()
