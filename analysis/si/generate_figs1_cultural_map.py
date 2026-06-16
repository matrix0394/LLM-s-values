"""
Generate FigS1: IVS Cultural Map with non-overlapping labels.

This script generates the IVS reference cultural map with:
- All countries plotted by cultural region
- Non-overlapping country labels using adjustText
- Clear legend for cultural regions
- Consistent axis ranges

Output: SI/figures/S1_IVS_cultural_map/FigS1_IVS_cultural_map.png/pdf
"""

import sys
from pathlib import Path

# Add paths for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import pandas as pd
import matplotlib.pyplot as plt

from si_config import (
    PROJECT_ROOT, FIGURES_DIR,
    load_ivs_data, get_region_color, save_figure,
    REGION_COLORS, ADJUSTTEXT_AVAILABLE,
    POINT_SIZE_S1, FONT_SIZE_COUNTRY_LABEL
)

if ADJUSTTEXT_AVAILABLE:
    from adjustText import adjust_text

# Regions to exclude from the plot
EXCLUDED_REGIONS = {'Other', 'Baltic'}


def should_include_region(region: str) -> bool:
    """Check if a region should be included in the plot."""
    if pd.isna(region):
        return False
    return region not in EXCLUDED_REGIONS


def generate_figs1_cultural_map(ivs_data: pd.DataFrame, output_dir: Path):
    """
    Generate FigS1 IVS Cultural Map with non-overlapping labels.
    
    Args:
        ivs_data: DataFrame with IVS PCA coordinates
        output_dir: Directory to save output files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Get unique regions and sort for consistent legend order (exclude Other and Baltic)
    regions = sorted([r for r in ivs_data['cultural_region'].unique() 
                      if pd.notna(r) and should_include_region(r)])
    
    # Plot each region
    texts = []
    for region in regions:
        subset = ivs_data[ivs_data['cultural_region'] == region]
        color = get_region_color(region)
        
        # Plot points
        ax.scatter(
            subset['PC1'], subset['PC2'],
            c=color, s=POINT_SIZE_S1, marker='o', alpha=0.85,
            edgecolors='black', linewidths=0.6,
            label=region, zorder=2
        )
        
        # Add country labels
        for _, row in subset.iterrows():
            country = row['country']
            if pd.notna(country) and not str(country).startswith('Code_'):
                text = ax.text(
                    row['PC1'], row['PC2'],
                    country,
                    fontsize=FONT_SIZE_COUNTRY_LABEL,
                    ha='center', va='bottom',
                    zorder=3
                )
                texts.append(text)
    
    # Apply adjustText to prevent label overlap
    if ADJUSTTEXT_AVAILABLE and len(texts) > 0:
        print(f"Adjusting {len(texts)} labels to prevent overlap...")
        adjust_text(
            texts,
            ax=ax,
            arrowprops=dict(arrowstyle='-', color='gray', lw=0.5, alpha=0.5),
            expand_points=(1.5, 1.5),
            force_points=(0.5, 0.5),
            force_text=(0.3, 0.3),
            only_move={'points': 'y', 'texts': 'xy'}
        )
    
    # Setup axes
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.4, zorder=0)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.4, zorder=0)
    
    # Calculate axis limits from data with padding
    pc1_min, pc1_max = ivs_data['PC1'].min(), ivs_data['PC1'].max()
    pc2_min, pc2_max = ivs_data['PC2'].min(), ivs_data['PC2'].max()
    padding = 0.3
    ax.set_xlim(pc1_min - padding, pc1_max + padding)
    ax.set_ylim(pc2_min - padding, pc2_max + padding)
    
    # Labels and title
    ax.set_xlabel('PC1 (Survival → Self-Expression)', fontsize=11)
    ax.set_ylabel('PC2 (Traditional → Secular-Rational)', fontsize=11)
    ax.set_title('IVS/WVS Cultural Map (Reference)', fontsize=14, fontweight='bold', pad=15)
    
    # Legend
    ax.legend(
        loc='upper left',
        framealpha=0.95,
        fontsize=9,
        title='Cultural Region',
        title_fontsize=10
    )
    
    # Grid
    ax.grid(True, alpha=0.2, zorder=0)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    save_figure(fig, output_dir / 'FigS1_IVS_cultural_map')
    
    print(f"✅ Generated: FigS1_IVS_cultural_map")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Generating FigS1: IVS Cultural Map")
    print("=" * 60)
    
    # Load data
    ivs_data = load_ivs_data()
    print(f"Loaded {len(ivs_data)} countries from IVS data")
    
    # Output directory
    output_dir = FIGURES_DIR / 'S1_IVS_cultural_map'
    
    # Generate figure
    generate_figs1_cultural_map(ivs_data, output_dir)
    
    print()
    print("=" * 60)
    print(f"Done! Output: {output_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
