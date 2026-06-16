"""
Generate FigS3 B5 figures.

B5: Per (model, language) - shows country/region coverage for one model-language pair
    Color: Cultural region
    Labels: Country/region names (using adjustText)
    Feature: Dashed lines connecting real IVS coordinates to imitated coordinates
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import pandas as pd
import matplotlib.pyplot as plt

from si_config import (
    PROJECT_ROOT, load_ivs_data, load_roleplay_data, get_global_axis_limits,
    get_country_region, plot_ivs_background, plot_dashed_line,
    setup_axes, save_figure, safe_filename,
    create_region_legend, generate_grid, 
    REGION_COLORS, LANGUAGE_NAMES,
    ADJUSTTEXT_AVAILABLE, ADJUST_TEXT_PARAMS,
    POINT_SIZE_SMALL, FONT_SIZE_COUNTRY_LABEL_SMALL, ALPHA_FG
)

if ADJUSTTEXT_AVAILABLE:
    from adjustText import adjust_text


def plot_b5_panel(ax, model, language, roleplay_data, ivs_data, xlim, ylim,
                  add_labels=True, add_dashed_lines=True):
    """Plot B5 panel: One model, one language, all countries/regions."""
    plot_ivs_background(ax, ivs_data, alpha=0.12)
    
    subset = roleplay_data[(roleplay_data['model_name'] == model) &
                           (roleplay_data['language'] == language)]
    
    texts = []
    for _, row in subset.iterrows():
        country = row['country']
        region = get_country_region(country, ivs_data)
        color = REGION_COLORS.get(region, '#DDDDDD')
        
        ivs_match = ivs_data[ivs_data['country'] == country]
        
        if add_dashed_lines and len(ivs_match) > 0:
            real_pc1 = ivs_match['PC1'].values[0]
            real_pc2 = ivs_match['PC2'].values[0]
            plot_dashed_line(ax, real_pc1, real_pc2, row['PC1'], row['PC2'], 
                           color=color, alpha=0.4)
        
        ax.scatter(row['PC1'], row['PC2'], c=color, s=POINT_SIZE_SMALL, marker='o', 
                   alpha=ALPHA_FG, edgecolors='black', linewidths=0.4, zorder=3)
        
        if add_labels:
            text = ax.text(row['PC1'], row['PC2'], country,
                          fontsize=FONT_SIZE_COUNTRY_LABEL_SMALL, 
                          ha='center', va='bottom', alpha=0.7, zorder=4)
            texts.append(text)
    
    if add_labels and ADJUSTTEXT_AVAILABLE and len(texts) > 0:
        adjust_text(texts, ax=ax, **ADJUST_TEXT_PARAMS)
    
    short_model = model.split('/')[-1] if '/' in model else model
    lang_name = LANGUAGE_NAMES.get(language, language)
    setup_axes(ax, xlim, ylim, title=f'{short_model} | {lang_name}', fontsize=6)


def main():
    print("=" * 60)
    print("Generating FigS3 B5")
    print("=" * 60)
    
    ivs_data = load_ivs_data()
    roleplay_data = load_roleplay_data()
    xlim, ylim = get_global_axis_limits(ivs_data, roleplay_data)
    
    b5_dir = PROJECT_ROOT / 'SI' / 'figures' / 'S3_Imitated_contextual_values' / 'B5_per_model_per_language'
    panels_dir = b5_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    
    combinations = roleplay_data.groupby(['model_name', 'language']).size().reset_index(name='count')
    print(f"Total combinations: {len(combinations)}")
    
    count = 0
    for _, row in combinations.iterrows():
        model, language = row['model_name'], row['language']
        
        fig, ax = plt.subplots(figsize=(6, 5))
        plot_b5_panel(ax, model, language, roleplay_data, ivs_data, xlim, ylim, 
                     add_labels=True, add_dashed_lines=True)
        ax.set_xlabel('PC1', fontsize=9)
        ax.set_ylabel('PC2', fontsize=9)
        
        safe_model = safe_filename(model)
        save_figure(fig, panels_dir / f'FigS3B5_{safe_model}__{language}')
        count += 1
        
        if count % 20 == 0:
            print(f"  Generated {count} panels...")
    
    print(f"Generated {count} B5 panels")
    
    combo_list = list(combinations[['model_name', 'language']].itertuples(index=False))
    generate_grid(
        combo_list,
        lambda ax, ml: plot_b5_panel(ax, ml[0], ml[1], roleplay_data, ivs_data, xlim, ylim, 
                                     add_labels=False, add_dashed_lines=True),
        b5_dir / 'FigS3B5_grid',
        'B5: Per (Model, Language)',
        legend_handles=create_region_legend(),
        legend_title='Cultural Region'
    )
    
    print("\nDone!")


if __name__ == '__main__':
    main()
