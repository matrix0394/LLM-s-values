#!/usr/bin/env python3
"""
Generate FigS5: English Advantage and Orientalism Analysis figures.

This script generates all S5 figures directly from SI/pca data,
without depending on external analysis results.

Output: SI/figures/S5_English_advantage_and_orientalism/

Figures:
- S5A: Cultural regions language effect (bar chart)
- S5B: Orientalism theory validation (histogram + top/bottom)
- S5C: Islamic vs Western comparison
- S5D: Geographic gradient trend (line chart)

Data Sources (SI/pca only):
- Table_S5_IVS_PCA_coordinates.csv
- Table_S7_LLM_roleplay_PCA_coordinates.csv
"""

import sys
from pathlib import Path
import json

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from si_config import (
    PROJECT_ROOT, SI_DIR, FIGURES_DIR, PCA_DIR,
    load_ivs_data, load_roleplay_data, save_figure
)

# Set publication-quality style
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 9,
    'figure.dpi': 300,
})


# =============================================================================
# Data Processing Functions (compute from SI/pca data)
# =============================================================================

def load_country_config():
    """Load country configuration for cultural regions and Islamic status."""
    config_path = PROJECT_ROOT / 'config' / 'country_codes.json'
    if not config_path.exists():
        print(f"Warning: {config_path} not found, using IVS data for regions")
        return {}, {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        country_codes = json.load(f)
    
    country_to_region = {item['Country']: item.get('Cultural Region', 'Other') 
                        for item in country_codes}
    country_to_islamic = {item['Country']: item.get('Islamic', False) 
                         for item in country_codes}
    
    return country_to_region, country_to_islamic


def compute_distances_and_advantage(ivs_df: pd.DataFrame, roleplay_df: pd.DataFrame) -> tuple:
    """
    Compute cultural distances and English advantage directly from PCA data.
    
    Returns:
        distances_df: Detailed distance data for each (model, country, language)
        advantage_df: English advantage summary by country
    """
    # Create IVS lookup
    ivs_lookup = ivs_df.set_index('country')[['PC1', 'PC2', 'cultural_region']].to_dict('index')
    
    # Calculate distances
    results = []
    for _, row in roleplay_df.iterrows():
        country = row['country']
        if country not in ivs_lookup:
            continue
        
        ivs_coords = ivs_lookup[country]
        distance = np.sqrt(
            (row['PC1'] - ivs_coords['PC1'])**2 + 
            (row['PC2'] - ivs_coords['PC2'])**2
        )
        
        results.append({
            'model_name': row['model_name'],
            'country': country,
            'language': row['language'],
            'llm_PC1': row['PC1'],
            'llm_PC2': row['PC2'],
            'real_PC1': ivs_coords['PC1'],
            'real_PC2': ivs_coords['PC2'],
            'cultural_region': ivs_coords['cultural_region'],
            'distance': distance
        })
    
    distances_df = pd.DataFrame(results)
    
    # Calculate English advantage
    # Group by country and language, average across models
    lang_avg = distances_df.groupby(['country', 'language', 'cultural_region'])['distance'].mean().reset_index()
    
    # Separate English and native language distances
    advantage_results = []
    
    for country in lang_avg['country'].unique():
        country_data = lang_avg[lang_avg['country'] == country]
        
        # Get English distance (en or en-native)
        en_data = country_data[country_data['language'].isin(['en', 'en-native'])]
        if len(en_data) == 0:
            continue
        en_distance = en_data['distance'].min()  # Use best English result
        
        # Get native language distance (non-English)
        native_data = country_data[~country_data['language'].isin(['en', 'en-native'])]
        if len(native_data) == 0:
            continue
        
        # Find the primary native language (lowest distance among non-English)
        native_row = native_data.loc[native_data['distance'].idxmin()]
        native_distance = native_row['distance']
        native_language = native_row['language']
        cultural_region = native_row['cultural_region']
        
        # Calculate English advantage (positive = English better)
        if native_distance > 0:
            english_advantage = ((native_distance - en_distance) / native_distance) * 100
        else:
            english_advantage = 0
        
        advantage_results.append({
            'country': country,
            'native_language': native_language,
            'cultural_region': cultural_region,
            'en_distance': en_distance,
            'native_distance': native_distance,
            'english_advantage': english_advantage
        })
    
    advantage_df = pd.DataFrame(advantage_results)
    
    print(f"Computed distances: {len(distances_df)} rows")
    print(f"Computed English advantage: {len(advantage_df)} countries")
    
    return distances_df, advantage_df


# =============================================================================
# Figure Generation Functions
# =============================================================================

def generate_s5a_cultural_regions(advantage_df: pd.DataFrame, output_dir: Path):
    """Generate FigS5A: Cultural regions language effect."""
    print("Generating FigS5A: Cultural regions language effect...")
    
    # Filter valid regions
    valid_data = advantage_df[
        (advantage_df['cultural_region'].notna()) & 
        (advantage_df['cultural_region'] != 'Other')
    ]
    
    if len(valid_data) == 0:
        print("  ⚠️ No valid cultural region data")
        return
    
    # Calculate statistics by region
    region_stats = valid_data.groupby('cultural_region').agg({
        'english_advantage': ['mean', 'std', 'count']
    }).reset_index()
    region_stats.columns = ['region', 'mean', 'std', 'count']
    region_stats['se'] = region_stats['std'] / np.sqrt(region_stats['count'])
    region_stats = region_stats.sort_values('mean', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#E74C3C' if x > 0 else '#27AE60' for x in region_stats['mean']]
    bars = ax.barh(range(len(region_stats)), region_stats['mean'], 
                  xerr=region_stats['se'] * 1.96,
                  color=colors, alpha=0.75, edgecolor='black', linewidth=1.5, capsize=3)
    
    ax.set_yticks(range(len(region_stats)))
    ax.set_yticklabels(region_stats['region'], fontsize=11)
    ax.set_xlabel('Language Effect (English Advantage, %)', fontsize=12, fontweight='bold')
    ax.set_title('FigS5A: Geographic Gradient - Language Effect by Cultural Region\n'
                '(Positive=English better, Negative=Native better, 95% CI)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.axvline(0, color='black', linestyle='-', linewidth=2)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()
    
    for i, row in enumerate(region_stats.itertuples()):
        x_pos = row.mean + (3 if row.mean > 0 else -3)
        ha = 'left' if row.mean > 0 else 'right'
        ax.text(x_pos, i, f'{row.mean:+.1f}% (n={int(row.count)})',
               va='center', ha=ha, fontsize=10, fontweight='bold')
    
    legend_elements = [
        mpatches.Patch(facecolor='#E74C3C', alpha=0.75, label='English Advantage', edgecolor='black'),
        mpatches.Patch(facecolor='#27AE60', alpha=0.75, label='Native Advantage', edgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)
    
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigS5A_cultural_regions_language_effect')
    print("  ✅ Saved: FigS5A_cultural_regions_language_effect")


def generate_s5b_orientalism_validation(advantage_df: pd.DataFrame, output_dir: Path):
    """Generate FigS5B: Orientalism theory validation."""
    print("Generating FigS5B: Orientalism theory validation...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Distribution histogram
    ax1.hist(advantage_df['english_advantage'], bins=30, 
            edgecolor='black', alpha=0.7, color='#3498DB')
    ax1.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero')
    ax1.axvline(advantage_df['english_advantage'].mean(), 
               color='green', linestyle='--', linewidth=2,
               label=f'Mean: {advantage_df["english_advantage"].mean():.1f}%')
    ax1.set_xlabel('English Advantage (%)', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('English Advantage Distribution\n(Positive=English better, Negative=Native better)', 
                 fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    # Right: Top 10 vs Bottom 10
    sorted_adv = advantage_df.sort_values('english_advantage', ascending=False)
    top10 = sorted_adv.head(10)
    bottom10 = sorted_adv.tail(10)
    
    combined = pd.concat([top10, bottom10])
    labels = [f"{row['country'][:15]}\n({row['native_language']})" 
             for _, row in combined.iterrows()]
    
    colors = ['#E74C3C' if x > 0 else '#27AE60' for x in combined['english_advantage']]
    
    bars = ax2.barh(range(len(combined)), combined['english_advantage'],
                   color=colors, alpha=0.7, edgecolor='black')
    ax2.set_yticks(range(len(combined)))
    ax2.set_yticklabels(labels, fontsize=8)
    ax2.set_xlabel('English Advantage (%)', fontsize=12)
    ax2.set_title('Top 10 English Advantage vs Bottom 10\n(Othering Theory Validation)', 
                 fontsize=13, fontweight='bold')
    ax2.axvline(0, color='black', linestyle='-', linewidth=1)
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()
    
    for i, (bar, val) in enumerate(zip(bars, combined['english_advantage'])):
        ax2.text(val + (2 if val > 0 else -2), i, f'{val:+.1f}%',
                va='center', ha='left' if val > 0 else 'right',
                fontsize=8, fontweight='bold')
    
    plt.suptitle('FigS5B: Orientalism Theory Validation', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigS5B_orientalism_theory_validation')
    print("  ✅ Saved: FigS5B_orientalism_theory_validation")


def generate_s5c_islamic_vs_western(advantage_df: pd.DataFrame, output_dir: Path):
    """Generate FigS5C: Islamic vs Western comparison."""
    print("Generating FigS5C: Islamic vs Western comparison...")
    
    country_to_region, country_to_islamic = load_country_config()
    
    # Add Islamic flag
    advantage_df_copy = advantage_df.copy()
    advantage_df_copy['is_islamic'] = advantage_df_copy['country'].map(country_to_islamic)
    
    # Islamic countries
    islamic_data = advantage_df_copy[advantage_df_copy['is_islamic'] == True]
    
    # Western countries (Protestant Europe + Catholic Europe)
    western_regions = ['Protestant Europe', 'Catholic Europe']
    western_data = advantage_df_copy[advantage_df_copy['cultural_region'].isin(western_regions)]
    
    if len(islamic_data) == 0 or len(western_data) == 0:
        print("  ⚠️ Insufficient data for comparison")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left: Islamic countries
    islamic_sorted = islamic_data.sort_values('english_advantage', ascending=False)
    colors1 = ['#E74C3C' if x > 0 else '#27AE60' for x in islamic_sorted['english_advantage']]
    ax1.barh(range(len(islamic_sorted)), islamic_sorted['english_advantage'],
            color=colors1, alpha=0.7, edgecolor='black')
    ax1.set_yticks(range(len(islamic_sorted)))
    ax1.set_yticklabels([f"{row['country'][:20]}\n({row['native_language']})" 
                        for _, row in islamic_sorted.iterrows()], fontsize=9)
    ax1.set_xlabel('English Advantage (%)', fontsize=12)
    ax1.set_title(f'Islamic Countries (n={len(islamic_sorted)})\n'
                 f'Mean: {islamic_sorted["english_advantage"].mean():+.1f}%', 
                 fontsize=13, fontweight='bold')
    ax1.axvline(0, color='black', linestyle='-', linewidth=1)
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()
    
    # Right: Western countries
    western_sorted = western_data.sort_values('english_advantage', ascending=False)
    colors2 = ['#E74C3C' if x > 0 else '#27AE60' for x in western_sorted['english_advantage']]
    ax2.barh(range(len(western_sorted)), western_sorted['english_advantage'],
            color=colors2, alpha=0.7, edgecolor='black')
    ax2.set_yticks(range(len(western_sorted)))
    ax2.set_yticklabels([f"{row['country'][:20]}\n({row['native_language']})" 
                        for _, row in western_sorted.iterrows()], fontsize=9)
    ax2.set_xlabel('English Advantage (%)', fontsize=12)
    ax2.set_title(f'Western Europe (n={len(western_sorted)})\n'
                 f'Mean: {western_sorted["english_advantage"].mean():+.1f}%', 
                 fontsize=13, fontweight='bold')
    ax2.axvline(0, color='black', linestyle='-', linewidth=1)
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()
    
    # Statistical test
    t_stat, p_value = stats.ttest_ind(islamic_sorted['english_advantage'], 
                                       western_sorted['english_advantage'])
    cohen_d = (islamic_sorted['english_advantage'].mean() - western_sorted['english_advantage'].mean()) / \
              np.sqrt((islamic_sorted['english_advantage'].std()**2 + western_sorted['english_advantage'].std()**2) / 2)
    
    plt.suptitle(f'FigS5C: Islamic vs Western Europe English Advantage\n'
                f't={t_stat:.2f}, p={p_value:.4f}, Cohen\'s d={cohen_d:.2f}', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigS5C_islamic_vs_western_comparison')
    print("  ✅ Saved: FigS5C_islamic_vs_western_comparison")


def generate_s5d_geographic_gradient(advantage_df: pd.DataFrame, output_dir: Path):
    """Generate FigS5D: Geographic gradient trend."""
    print("Generating FigS5D: Geographic gradient trend...")
    
    # Define cultural region order (from West to East)
    region_order = [
        'Protestant Europe',
        'Catholic Europe', 
        'Orthodox Europe',
        'Latin America',
        'African-Islamic',
        'West & South Asia',
        'Confucian'
    ]
    
    regions = []
    advantages = []
    counts = []
    
    for region in region_order:
        region_data = advantage_df[advantage_df['cultural_region'] == region]
        if len(region_data) > 0:
            mean_adv = region_data['english_advantage'].mean()
            regions.append(region)
            advantages.append(mean_adv)
            counts.append(len(region_data))
    
    if len(regions) == 0:
        print("  ⚠️ No gradient data")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x_pos = range(len(regions))
    ax.plot(x_pos, advantages, marker='o', markersize=12, linewidth=3,
           color='#3498DB', markerfacecolor='#3498DB', markeredgecolor='black',
           markeredgewidth=2, label='Language Effect Trend')
    
    ax.axhline(0, color='black', linestyle='-', linewidth=2, alpha=0.5)
    
    ax.fill_between(x_pos, 0, advantages, where=[a >= 0 for a in advantages],
                    color='#E74C3C', alpha=0.2, label='English Advantage Zone')
    ax.fill_between(x_pos, 0, advantages, where=[a < 0 for a in advantages],
                    color='#27AE60', alpha=0.2, label='Native Advantage Zone')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(regions, fontsize=11, rotation=15, ha='right')
    ax.set_ylabel('Language Effect (English Advantage, %)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Cultural Region (ordered by distance from West)', fontsize=13, fontweight='bold')
    ax.set_title('FigS5D: Geographic Gradient of English Effect', fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (region, adv, count) in enumerate(zip(regions, advantages, counts)):
        y_offset = 3 if adv > 0 else -3
        va = 'bottom' if adv > 0 else 'top'
        ax.text(i, adv + y_offset, f'{adv:+.1f}%\n(n={count})',
               ha='center', va=va, fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    ax.text(0.02, 0.98, '← Closer to West', transform=ax.transAxes,
           fontsize=10, va='top', ha='left', style='italic', color='gray')
    ax.text(0.98, 0.98, 'Further from West →', transform=ax.transAxes,
           fontsize=10, va='top', ha='right', style='italic', color='gray')
    
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigS5D_geographic_gradient_trend')
    print("  ✅ Saved: FigS5D_geographic_gradient_trend")


# =============================================================================
# Main
# =============================================================================

def main():
    """Main function to generate all S5 figures."""
    print("=" * 60)
    print("Generating FigS5: English Advantage and Orientalism")
    print("Data source: SI/pca/ (self-contained)")
    print("=" * 60)
    
    # Output directory
    output_dir = FIGURES_DIR / 'S5_English_advantage_and_orientalism'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data from SI/pca
    print("\nLoading data from SI/pca...")
    ivs_df = load_ivs_data()
    roleplay_df = load_roleplay_data()
    
    print(f"  IVS: {len(ivs_df)} countries")
    print(f"  Roleplay: {len(roleplay_df)} records")
    
    # Compute distances and English advantage
    print("\nComputing distances and English advantage...")
    distances_df, advantage_df = compute_distances_and_advantage(ivs_df, roleplay_df)
    
    # Generate all S5 figures
    print("\nGenerating figures...")
    generate_s5a_cultural_regions(advantage_df, output_dir)
    generate_s5b_orientalism_validation(advantage_df, output_dir)
    generate_s5c_islamic_vs_western(advantage_df, output_dir)
    generate_s5d_geographic_gradient(advantage_df, output_dir)
    
    print("\n" + "=" * 60)
    print(f"✅ All S5 figures saved to: {output_dir}")
    print("   Generated: FigS5A, FigS5B, FigS5C, FigS5D")
    print("=" * 60)


if __name__ == '__main__':
    main()
