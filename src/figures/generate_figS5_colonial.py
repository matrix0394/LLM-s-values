#!/usr/bin/env python3
"""
Generate FigS5: Colonial History Analysis figures.

This script lives under ``src/figures`` and generates colonial history analysis
figures (Study 4) for the Supplementary Materials, integrating with the SI
figure utilities in ``analysis/si``.

Output: ``Supplementary Materials/figures/FigS5/``

Figures:
- S5A: East Asian colonial gradient (Hong Kong, Macao, China, Japan, Korea)
- S5B: Hong Kong vs Macao comparison
- S5C: Latin American language variants (Spanish, Portuguese, French)
- S5D: African colonial history limitation report

Data Sources (SI/pca only):
- Table_S5_IVS_PCA_coordinates.csv
- Table_S7_LLM_roleplay_PCA_coordinates.csv
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'analysis' / 'si'))
sys.path.insert(0, str(PROJECT_ROOT / 'analysis' / 'language'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from si_config import (
    load_ivs_data, load_roleplay_data, save_figure
)

from colonial_utils import (
    calculate_cultural_distance,
    filter_low_quality_models,
    add_cultural_distance_column,
    load_ivs_coordinates,
    COLONIAL_HISTORY,
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

# Output directory
OUTPUT_DIR = PROJECT_ROOT / 'Supplementary Materials' / 'figures' / 'FigS5'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Color Scheme (matching SI system)
# =============================================================================

COLOR_RED = '#E74C3C'     # Strong advantage
COLOR_ORANGE = '#F39C12'  # Moderate advantage
COLOR_GREEN = '#27AE60'   # Weak advantage
COLOR_BLUE = '#3498DB'    # Native advantage


def get_advantage_color(advantage: float) -> str:
    """Get color for English advantage value."""
    if advantage > 20:
        return COLOR_RED
    elif advantage > 10:
        return COLOR_ORANGE
    elif advantage > 0:
        return COLOR_GREEN
    else:
        return COLOR_BLUE


# =============================================================================
# Data Processing
# =============================================================================

def compute_english_advantage_data(ivs_df: pd.DataFrame, roleplay_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute English advantage for all countries from PCA data.
    
    Returns:
        DataFrame with columns: country, native_language, english_advantage,
                               english_distance, native_distance
    """
    print("Computing English advantage data...")
    
    # Filter low-quality models
    roleplay_df = filter_low_quality_models(
        roleplay_df, 
        ['llama-3.2-3b-instruct', 'qwen3-1.7b']
    )
    
    # Create IVS lookup
    ivs_df_raw = load_ivs_data()
    ivs_dict = {row['country']: (row['PC1'], row['PC2']) for _, row in ivs_df_raw.iterrows()}
    
    # Calculate cultural distances
    roleplay_df = add_cultural_distance_column(roleplay_df, ivs_dict)
    
    # Compute English advantage for each country
    results = []
    for country in roleplay_df['country'].unique():
        country_data = roleplay_df[roleplay_df['country'] == country]
        
        # Get English distance
        en_data = country_data[country_data['language'].isin(['en', 'en-native'])]
        if len(en_data) == 0:
            continue
        en_distance = en_data['cultural_distance'].mean()
        
        # Get native language distances
        native_langs = country_data[
            ~country_data['language'].isin(['en', 'en-native'])
        ]['language'].unique()
        
        for native_lang in native_langs:
            native_data = country_data[country_data['language'] == native_lang]
            if len(native_data) == 0:
                continue
            
            native_distance = native_data['cultural_distance'].mean()
            
            # Calculate advantage
            if native_distance > 0:
                advantage = 100 * (native_distance - en_distance) / native_distance
            else:
                advantage = 0.0
            
            results.append({
                'country': country,
                'native_language': native_lang,
                'english_distance': en_distance,
                'native_distance': native_distance,
                'english_advantage': advantage
            })
    
    advantage_df = pd.DataFrame(results)
    print(f"  Computed advantage for {len(advantage_df)} country-language pairs")
    
    return advantage_df


# =============================================================================
# Figure S5A: East Asian Colonial Gradient
# =============================================================================

def generate_s5a_east_asian_gradient(advantage_df: pd.DataFrame):
    """Generate S5A: East Asian colonial gradient."""
    print("\nGenerating FigS5A: East Asian Colonial Gradient...")
    
    # Define East Asian countries
    east_asian_countries = {
        'Hong Kong': 'zh-cn',
        'Macao': 'zh-cn',
        'China': 'zh-cn',
        'Japan': 'ja',
        'Korea, Republic of': 'ko'
    }
    
    # Extract data
    data_points = []
    for country, native_lang in east_asian_countries.items():
        country_data = advantage_df[
            (advantage_df['country'].str.contains(country, case=False, na=False)) &
            (advantage_df['native_language'] == native_lang)
        ]
        
        if len(country_data) > 0:
            advantage = country_data['english_advantage'].iloc[0]
            data_points.append({
                'country': country,
                'english_advantage': advantage
            })
    
    if len(data_points) == 0:
        print("  No data found")
        return
    
    # Sort by advantage
    data_points = sorted(data_points, key=lambda x: x['english_advantage'], reverse=True)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    countries = [d['country'] for d in data_points]
    advantages = [d['english_advantage'] for d in data_points]
    colors = [get_advantage_color(adv) for adv in advantages]
    
    # Horizontal bar chart
    y_pos = np.arange(len(countries))
    bars = ax.barh(y_pos, advantages, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=1)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(countries)
    ax.set_xlabel('English Advantage (%)', fontweight='bold')
    ax.set_title('East Asian Colonial Gradient', fontweight='bold', pad=15)
    
    # Add vertical line at 0
    ax.axvline(x=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Add value labels
    for i, (bar, adv) in enumerate(zip(bars, advantages)):
        label_x = adv + (1.5 if adv > 0 else -1.5)
        ha = 'left' if adv > 0 else 'right'
        ax.text(label_x, i, f'{adv:.1f}%', 
                va='center', ha=ha, fontsize=9, fontweight='bold')
    
    # Add colonial annotations
    for i, d in enumerate(data_points):
        if d['country'] == 'Hong Kong':
            ax.text(0.02, i, 'British 1842-1997', 
                   transform=ax.get_yaxis_transform(),
                   ha='left', va='center', fontsize=7, 
                   style='italic', color='gray')
        elif d['country'] == 'Macao':
            ax.text(0.02, i, 'Portuguese 1557-1999', 
                   transform=ax.get_yaxis_transform(),
                   ha='left', va='center', fontsize=7, 
                   style='italic', color='gray')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'S5A_east_asian_gradient'
    save_figure(fig, output_path)
    print(f"  Saved: S5A_east_asian_gradient")


# =============================================================================
# Figure S5B: Hong Kong vs Macao Comparison
# =============================================================================

def generate_s5b_hk_macao_comparison(advantage_df: pd.DataFrame, roleplay_df: pd.DataFrame):
    """Generate S5B: Hong Kong vs Macao comparison."""
    print("\nGenerating FigS5B: Hong Kong vs Macao Comparison...")
    
    # Get Hong Kong English advantage
    hk_data = advantage_df[
        (advantage_df['country'] == 'Hong Kong') &
        (advantage_df['native_language'] == 'zh-cn')
    ]
    
    # Get Macao Portuguese advantage (need to calculate)
    macao_zhcn = advantage_df[
        (advantage_df['country'] == 'Macao') &
        (advantage_df['native_language'] == 'zh-cn')
    ]
    macao_pt = advantage_df[
        (advantage_df['country'] == 'Macao') &
        (advantage_df['native_language'] == 'pt')
    ]
    
    if len(hk_data) == 0 or len(macao_zhcn) == 0 or len(macao_pt) == 0:
        print("  Insufficient data")
        return
    
    hk_advantage = hk_data['english_advantage'].iloc[0]
    
    # Calculate Portuguese advantage: (zh-cn distance - pt distance) / zh-cn distance
    macao_pt_advantage = (
        (macao_zhcn['native_distance'].iloc[0] - macao_pt['native_distance'].iloc[0]) /
        macao_zhcn['native_distance'].iloc[0] * 100
    )
    
    # Create figure
    fig, ax = plt.subplots(figsize=(7, 5))
    
    groups = ['Hong Kong\n(English)', 'Macao\n(Portuguese)']
    means = [hk_advantage, macao_pt_advantage]
    colors = [get_advantage_color(hk_advantage), get_advantage_color(macao_pt_advantage)]
    
    x_pos = np.arange(len(groups))
    bars = ax.bar(x_pos, means, color=colors, alpha=0.8, 
                  edgecolor='black', linewidth=1)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(groups, fontweight='bold')
    ax.set_ylabel('Colonial Language Advantage (%)', fontweight='bold')
    ax.set_title('Hong Kong vs Macao: Colonial Language Effects', 
                 fontweight='bold', pad=15)
    
    # Add horizontal line at 0
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Add value labels
    for i, (bar, mean) in enumerate(zip(bars, means)):
        label_y = mean + 1.5
        ax.text(i, label_y, f'{mean:.1f}%', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'S5B_hk_macao_comparison'
    save_figure(fig, output_path)
    print(f"  Saved: S5B_hk_macao_comparison")


# =============================================================================
# Figure S5C: Latin American Language Variants
# =============================================================================

def generate_s5c_latin_america_variants(advantage_df: pd.DataFrame):
    """Generate S5C: Latin American language variants."""
    print("\nGenerating FigS5C: Latin American Language Variants...")
    
    # Define country groups
    spanish_countries = ['Argentina', 'Bolivia', 'Chile', 'Colombia', 'Ecuador',
                        'Guatemala', 'Mexico', 'Nicaragua', 'Peru', 'Uruguay', 'Venezuela']
    portuguese_countries = ['Brazil']
    french_countries = ['Haiti']
    
    # Collect advantages
    spanish_advantages = []
    for country in spanish_countries:
        country_data = advantage_df[
            (advantage_df['country'].str.contains(country, case=False, na=False)) &
            (advantage_df['native_language'] == 'es')
        ]
        if len(country_data) > 0:
            spanish_advantages.append(country_data['english_advantage'].iloc[0])
    
    portuguese_advantages = []
    for country in portuguese_countries:
        country_data = advantage_df[
            (advantage_df['country'].str.contains(country, case=False, na=False)) &
            (advantage_df['native_language'] == 'pt')
        ]
        if len(country_data) > 0:
            portuguese_advantages.append(country_data['english_advantage'].iloc[0])
    
    french_advantages = []
    for country in french_countries:
        country_data = advantage_df[
            (advantage_df['country'].str.contains(country, case=False, na=False)) &
            (advantage_df['native_language'] == 'fr')
        ]
        if len(country_data) > 0:
            french_advantages.append(country_data['english_advantage'].iloc[0])
    
    if not spanish_advantages or not portuguese_advantages or not french_advantages:
        print("  Insufficient data")
        return
    
    # Calculate means
    spanish_mean = np.mean(spanish_advantages)
    portuguese_mean = np.mean(portuguese_advantages)
    french_mean = np.mean(french_advantages)
    
    # ANOVA
    f_stat, p_value = stats.f_oneway(spanish_advantages, portuguese_advantages, french_advantages)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    groups = ['Spanish', 'Portuguese', 'French']
    means = [spanish_mean, portuguese_mean, french_mean]
    colors = [get_advantage_color(m) for m in means]
    
    x_pos = np.arange(len(groups))
    bars = ax.bar(x_pos, means, color=colors, alpha=0.8, 
                  edgecolor='black', linewidth=1)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(groups, fontweight='bold')
    ax.set_ylabel('English Advantage (%)', fontweight='bold')
    ax.set_title('Latin American Colonial Language Variants', 
                 fontweight='bold', pad=15)
    
    # Add horizontal line at 0
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Add value labels
    for i, (bar, mean) in enumerate(zip(bars, means)):
        label_y = mean + 1
        ax.text(i, label_y, f'{mean:.1f}%', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add sample sizes
    ns = [len(spanish_advantages), len(portuguese_advantages), len(french_advantages)]
    for i, n in enumerate(ns):
        ax.text(i, -1, f'n={n}', 
                ha='center', va='top', fontsize=8, style='italic', color='gray')
    
    # Add ANOVA results
    anova_text = f"ANOVA: F={f_stat:.3f}, p={p_value:.4f}"
    ax.text(0.02, 0.98, anova_text, 
            transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', 
            facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'S5C_latin_america_variants'
    save_figure(fig, output_path)
    print(f"  Saved: S5C_latin_america_variants")


# =============================================================================
# Figure S5D: African Colonial History Limitation
# =============================================================================

def generate_s5d_african_limitation(roleplay_df: pd.DataFrame):
    """Generate S5D: African colonial history data limitation report."""
    print("\nGenerating FigS5D: African Colonial History Limitation...")
    
    # Check British-colonized African countries
    british_african = ['Kenya', 'Nigeria', 'Ghana', 'South Africa', 'Zimbabwe', 'Zambia']
    
    # Check data availability
    data_status = []
    for country in british_african:
        country_data = roleplay_df[
            roleplay_df['country'].str.contains(country, case=False, na=False)
        ]
        
        if len(country_data) > 0:
            languages = country_data['language'].unique().tolist()
            has_native = any(lang not in ['en', 'en-native'] for lang in languages)
            data_status.append({
                'country': country,
                'has_data': True,
                'has_native': has_native,
                'languages': ', '.join(languages)
            })
        else:
            data_status.append({
                'country': country,
                'has_data': False,
                'has_native': False,
                'languages': 'None'
            })
    
    # Create text figure
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')
    
    # Title
    title_text = "African Colonial History Analysis: Data Limitation"
    ax.text(0.5, 0.95, title_text, ha='center', va='top', 
            fontsize=14, fontweight='bold', transform=ax.transAxes)
    
    # Limitation explanation
    limitation_text = """
CRITICAL DATA LIMITATION:

All British-colonized African countries in our dataset only have English 
(en-native) language data. They lack native language data (Swahili, Yoruba, 
Akan, Zulu, Shona, Bemba, etc.).

IMPACT:
The English advantage metric requires BOTH English and native language data:
    English Advantage (%) = 100 × (Distance_native - Distance_english) / Distance_native

Without native language data, we CANNOT calculate English advantage for 
British-colonized African countries, preventing us from testing the colonial 
hypothesis in the African context.

RECOMMENDATION:
This should be acknowledged as a methodological limitation. Future work should 
collect native language data for these countries to enable proper colonial 
history analysis in Africa.
"""
    
    ax.text(0.05, 0.85, limitation_text, ha='left', va='top', 
            fontsize=9, family='monospace', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Data availability table
    table_y = 0.25
    ax.text(0.05, table_y, "Data Availability for British-Colonized African Countries:", 
            ha='left', va='top', fontsize=10, fontweight='bold', transform=ax.transAxes)
    
    table_text = "\n".join([
        f"  {d['country']}: {'[OK]' if d['has_data'] else '[X]'} Data found, "
        f"{'[OK]' if d['has_native'] else '[X]'} Native language"
        for d in data_status
    ])
    
    ax.text(0.05, table_y - 0.03, table_text, ha='left', va='top', 
            fontsize=8, family='monospace', transform=ax.transAxes)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'S5D_african_limitation'
    save_figure(fig, output_path)
    print(f"  Saved: S5D_african_limitation")


# =============================================================================
# Main Function
# =============================================================================

def main():
    """Generate all S5 figures."""
    print("="*80)
    print("Generating FigS5: Colonial History Analysis")
    print("="*80)
    
    # Load data
    print("\nLoading data from project data...")
    ivs_df = load_ivs_data()
    roleplay_df = load_roleplay_data()
    print(f"  IVS: {len(ivs_df)} countries")
    print(f"  Roleplay: {len(roleplay_df)} observations")
    
    # Compute English advantage
    advantage_df = compute_english_advantage_data(ivs_df, roleplay_df)
    
    # Generate figures
    generate_s5a_east_asian_gradient(advantage_df)
    generate_s5b_hk_macao_comparison(advantage_df, roleplay_df)
    generate_s5c_latin_america_variants(advantage_df)
    generate_s5d_african_limitation(roleplay_df)
    
    print("\n" + "="*80)
    print("FigS5 generation complete")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()
