#!/usr/bin/env python3
"""
Generate Summary figures (Sx1-Sx4).

Output: SI/figures/summary/

Generates:
- Sx1: Model × Country heatmap
- Sx2: Model × Language heatmap
- Sx3: Top/Bottom rankings
- Sx4: Score vs Consistency scatter

Requirements: 4.6, 5.1
"""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import linkage, dendrogram
import warnings
warnings.filterwarnings('ignore')

# Import si_config for style consistency
from si_config import (
    PROJECT_ROOT, SI_DIR, FIGURES_DIR,
    save_figure, PCA_DIR
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
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})


def load_roleplay_data():
    """Load LLM roleplay PCA coordinates."""
    roleplay_path = PCA_DIR / 'Table_S7_LLM_roleplay_PCA_coordinates.csv'
    
    if not roleplay_path.exists():
        raise FileNotFoundError(f"Roleplay data not found at {roleplay_path}")
    
    df = pd.read_csv(roleplay_path)
    print(f"Loaded roleplay data: {len(df)} rows")
    return df


def load_ivs_data():
    """Load IVS PCA coordinates."""
    ivs_path = PCA_DIR / 'Table_S5_IVS_PCA_coordinates.csv'
    
    if not ivs_path.exists():
        raise FileNotFoundError(f"IVS data not found at {ivs_path}")
    
    df = pd.read_csv(ivs_path)
    print(f"Loaded IVS data: {len(df)} rows")
    return df


def generate_sx1_model_country_heatmap(roleplay_df, ivs_df, output_dir):
    """Generate FigSx1: Model × Country heatmap."""
    print("Generating FigSx1: Model × Country heatmap...")
    
    # Calculate cultural distance for each model-country combination
    # Merge with IVS to get reference coordinates
    merged = roleplay_df.merge(
        ivs_df[['country', 'PC1', 'PC2']].rename(columns={'PC1': 'ivs_PC1', 'PC2': 'ivs_PC2'}),
        on='country',
        how='left'
    )
    
    # Calculate 2D Euclidean distance
    merged['distance'] = np.sqrt(
        (merged['PC1'] - merged['ivs_PC1'])**2 + 
        (merged['PC2'] - merged['ivs_PC2'])**2
    )
    
    # Aggregate by model and country (average across languages)
    pivot_data = merged.groupby(['model_name', 'country'])['distance'].mean().reset_index()
    heatmap_matrix = pivot_data.pivot(index='model_name', columns='country', values='distance')
    
    # Fill NaN with column mean
    heatmap_matrix = heatmap_matrix.fillna(heatmap_matrix.mean())
    
    fig, ax = plt.subplots(figsize=(20, 12))
    
    sns.heatmap(heatmap_matrix, cmap='RdYlBu_r', center=heatmap_matrix.values.mean(),
                ax=ax, cbar_kws={'label': 'Cultural Distance'})
    
    ax.set_xlabel('Country', fontsize=12)
    ax.set_ylabel('Model', fontsize=12)
    ax.set_title('FigSx1: Model × Country Cultural Distance Heatmap', fontsize=14, fontweight='bold')
    
    # Rotate x labels
    plt.xticks(rotation=45, ha='right', fontsize=6)
    plt.yticks(fontsize=8)
    
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigSx1_heatmap_model_country')
    print(f"  ✅ Saved: FigSx1_heatmap_model_country")


def generate_sx2_model_language_heatmap(roleplay_df, ivs_df, output_dir):
    """Generate FigSx2: Model × Language heatmap."""
    print("Generating FigSx2: Model × Language heatmap...")
    
    # Merge with IVS
    merged = roleplay_df.merge(
        ivs_df[['country', 'PC1', 'PC2']].rename(columns={'PC1': 'ivs_PC1', 'PC2': 'ivs_PC2'}),
        on='country',
        how='left'
    )
    
    merged['distance'] = np.sqrt(
        (merged['PC1'] - merged['ivs_PC1'])**2 + 
        (merged['PC2'] - merged['ivs_PC2'])**2
    )
    
    # Aggregate by model and language (average across countries)
    pivot_data = merged.groupby(['model_name', 'language'])['distance'].mean().reset_index()
    heatmap_matrix = pivot_data.pivot(index='model_name', columns='language', values='distance')
    heatmap_matrix = heatmap_matrix.fillna(heatmap_matrix.mean())
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    sns.heatmap(heatmap_matrix, cmap='RdYlBu_r', center=heatmap_matrix.values.mean(),
                ax=ax, cbar_kws={'label': 'Cultural Distance'}, annot=True, fmt='.2f')
    
    ax.set_xlabel('Language', fontsize=12)
    ax.set_ylabel('Model', fontsize=12)
    ax.set_title('FigSx2: Model × Language Cultural Distance Heatmap', fontsize=14, fontweight='bold')
    
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=8)
    
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigSx2_heatmap_model_language')
    print(f"  ✅ Saved: FigSx2_heatmap_model_language")


def generate_sx3_top_bottom_rankings(roleplay_df, ivs_df, output_dir):
    """Generate FigSx3: Top/Bottom country rankings."""
    print("Generating FigSx3: Top/Bottom rankings...")
    
    # Merge with IVS
    merged = roleplay_df.merge(
        ivs_df[['country', 'PC1', 'PC2']].rename(columns={'PC1': 'ivs_PC1', 'PC2': 'ivs_PC2'}),
        on='country',
        how='left'
    )
    
    merged['distance'] = np.sqrt(
        (merged['PC1'] - merged['ivs_PC1'])**2 + 
        (merged['PC2'] - merged['ivs_PC2'])**2
    )
    
    # Get unique models
    models = sorted(merged['model_name'].unique())
    n_models = len(models)
    
    n_cols = 4
    n_rows = (n_models + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 4 * n_rows))
    axes = axes.flatten()
    
    for i, model in enumerate(models):
        ax = axes[i]
        model_data = merged[merged['model_name'] == model]
        
        # Average distance per country
        country_dist = model_data.groupby('country')['distance'].mean().sort_values()
        
        # Top 5 (best) and Bottom 5 (worst)
        top5 = country_dist.head(5)
        bottom5 = country_dist.tail(5)
        
        combined = pd.concat([top5, bottom5])
        colors = ['#27AE60'] * 5 + ['#E74C3C'] * 5
        
        y_pos = np.arange(len(combined))
        ax.barh(y_pos, combined.values, color=colors, alpha=0.8, edgecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(combined.index, fontsize=7)
        ax.set_xlabel('Distance', fontsize=9)
        ax.set_title(model.split('/')[-1], fontsize=10, fontweight='bold')
        ax.axvline(x=combined.mean(), color='gray', linestyle='--', alpha=0.5)
    
    # Hide empty subplots
    for i in range(n_models, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle('FigSx3: Top 5 (Green) and Bottom 5 (Red) Countries by Model', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigSx3_top_bottom_rankings')
    print(f"  ✅ Saved: FigSx3_top_bottom_rankings")


def generate_sx4_score_vs_consistency(roleplay_df, ivs_df, output_dir):
    """Generate FigSx4: Score vs Consistency scatter."""
    print("Generating FigSx4: Score vs Consistency scatter...")
    
    # Merge with IVS
    merged = roleplay_df.merge(
        ivs_df[['country', 'PC1', 'PC2']].rename(columns={'PC1': 'ivs_PC1', 'PC2': 'ivs_PC2'}),
        on='country',
        how='left'
    )
    
    merged['distance'] = np.sqrt(
        (merged['PC1'] - merged['ivs_PC1'])**2 + 
        (merged['PC2'] - merged['ivs_PC2'])**2
    )
    
    # Calculate model-level statistics
    model_stats = merged.groupby('model_name').agg({
        'distance': 'mean',
        'PC1': 'std',  # Use PC1 std as proxy for consistency
        'PC2': 'std'
    }).reset_index()
    
    model_stats['consistency'] = 1 / (1 + model_stats['PC1'] + model_stats['PC2'])  # Higher = more consistent
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.scatter(model_stats['distance'], model_stats['consistency'], 
              s=100, alpha=0.7, edgecolors='black', c='#3498DB')
    
    # Add model labels
    for _, row in model_stats.iterrows():
        short_name = row['model_name'].split('/')[-1]
        ax.annotate(short_name, (row['distance'], row['consistency']),
                   xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Add regression line
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        model_stats['distance'], model_stats['consistency']
    )
    x_line = np.linspace(model_stats['distance'].min(), model_stats['distance'].max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'r--', alpha=0.7, label=f'R² = {r_value**2:.3f}')
    
    ax.set_xlabel('Mean Cultural Distance', fontsize=12)
    ax.set_ylabel('Consistency Score', fontsize=12)
    ax.set_title('FigSx4: Cultural Distance vs Model Consistency', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigSx4_score_vs_consistency')
    print(f"  ✅ Saved: FigSx4_score_vs_consistency")


def main():
    """Main function to generate all summary figures."""
    print("=" * 60)
    print("Generating Summary Figures (Sx1-Sx4)")
    print("=" * 60)
    
    # Output directory
    output_dir = FIGURES_DIR / 'summary'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    roleplay_df = load_roleplay_data()
    ivs_df = load_ivs_data()
    
    # Generate all summary figures (Sx1-Sx4)
    generate_sx1_model_country_heatmap(roleplay_df, ivs_df, output_dir)
    generate_sx2_model_language_heatmap(roleplay_df, ivs_df, output_dir)
    generate_sx3_top_bottom_rankings(roleplay_df, ivs_df, output_dir)
    generate_sx4_score_vs_consistency(roleplay_df, ivs_df, output_dir)
    
    print("\n" + "=" * 60)
    print(f"✅ All summary figures saved to: {output_dir}")
    print("   Generated: FigSx1, FigSx2, FigSx3, FigSx4")
    print("=" * 60)


if __name__ == '__main__':
    main()
