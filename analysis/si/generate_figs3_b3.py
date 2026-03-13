"""
Generate FigS3 B3 figures.

B3: Per (model, country/region) - shows language variation for one model-country/region pair
    Color: Language
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
    plot_ivs_background, plot_country_star, setup_axes, save_figure, safe_filename,
    create_language_legend, generate_grid, add_jitter,
    LANGUAGE_COLORS, POINT_SIZE_LARGE, ALPHA_FG
)


def plot_b3_panel(ax, model: str, country: str, roleplay_data: pd.DataFrame, 
                  ivs_data: pd.DataFrame, xlim: tuple, ylim: tuple):
    """Plot B3 panel: One model, one country/region, multiple languages."""
    plot_ivs_background(ax, ivs_data, alpha=0.12)
    
    # Mark target country in IVS with gold star
    plot_country_star(ax, country, ivs_data)
    
    subset = roleplay_data[(roleplay_data['model_name'] == model) & 
                           (roleplay_data['country'] == country)]
    
    for _, row in subset.iterrows():
        color = LANGUAGE_COLORS.get(row['language'], '#888888')
        # Add jitter to reduce overlap
        jx, jy = add_jitter(row['PC1'], row['PC2'])
        ax.scatter(jx, jy, c=color, s=POINT_SIZE_LARGE, marker='o', 
                   alpha=ALPHA_FG, edgecolors='black', linewidths=0.5, zorder=3)
    
    short_model = model.split('/')[-1] if '/' in model else model
    setup_axes(ax, xlim, ylim, title=f'{short_model} | {country}', fontsize=6)


def main():
    print("=" * 60)
    print("Generating FigS3 B3")
    print("=" * 60)
    
    ivs_data = load_ivs_data()
    roleplay_data = load_roleplay_data()
    xlim, ylim = get_global_axis_limits(ivs_data, roleplay_data)
    
    b3_dir = PROJECT_ROOT / 'SI' / 'figures' / 'S3_Imitated_contextual_values' / 'B3_per_model_per_country'
    panels_dir = b3_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    
    combinations = roleplay_data.groupby(['model_name', 'country']).size().reset_index(name='count')
    print(f"Total combinations: {len(combinations)}")
    
    count = 0
    for _, row in combinations.iterrows():
        model, country = row['model_name'], row['country']
        
        fig, ax = plt.subplots(figsize=(5, 4))
        plot_b3_panel(ax, model, country, roleplay_data, ivs_data, xlim, ylim)
        ax.set_xlabel('PC1', fontsize=9)
        ax.set_ylabel('PC2', fontsize=9)
        
        save_figure(fig, panels_dir / f'FigS3B3_{safe_filename(model)}__{safe_filename(country)}')
        count += 1
        
        if count % 100 == 0:
            print(f"  Generated {count} panels...")
    
    print(f"Generated {count} B3 panels")
    
    combo_list = list(combinations[['model_name', 'country']].itertuples(index=False))
    generate_grid(
        combo_list,
        lambda ax, mc: plot_b3_panel(ax, mc[0], mc[1], roleplay_data, ivs_data, xlim, ylim),
        b3_dir / 'FigS3B3_grid',
        'B3: Per (Model, Country/Region)',
        legend_handles=create_language_legend(),
        legend_title='Language'
    )
    
    print("\nDone!")


if __name__ == '__main__':
    main()
