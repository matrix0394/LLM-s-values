"""
Visualization functions for Study 4: Colonial History Analysis

This module provides visualization functions for colonial history effects,
matching the style of visualize_orientalism.py.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Set up Chinese font support
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Output directory
OUTPUT_DIR = Path('results/analysis/colonial_history')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Color Scheme (matching orientalism visualizations)
# ============================================================================

def get_advantage_color(advantage: float) -> str:
    """
    Get color for English advantage value.
    
    Red = Strong English advantage (>20%)
    Orange = Moderate English advantage (10-20%)
    Green = Weak English advantage (0-10%)
    Blue = Native language advantage (<0%)
    
    Args:
        advantage: English advantage percentage
    
    Returns:
        Hex color code
    """
    if advantage > 20:
        return '#E74C3C'  # Red
    elif advantage > 10:
        return '#F39C12'  # Orange
    elif advantage > 0:
        return '#27AE60'  # Green
    else:
        return '#3498DB'  # Blue


# ============================================================================
# Figure 1: East Asian Colonial Gradient
# ============================================================================

def plot_east_asian_gradient(
    advantage_df: pd.DataFrame,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot East Asian colonial gradient showing Hong Kong, Macao, China, Japan, Korea.
    
    This visualization shows how colonial history affects English advantage in
    East Asian countries, with Hong Kong (British colony) showing the strongest
    English advantage.
    
    Args:
        advantage_df: DataFrame with columns 'country', 'native_language', 'english_advantage'
        save_path: Optional path to save figure (default: OUTPUT_DIR/east_asian_gradient.png)
        show: Whether to display the figure
    
    Returns:
        matplotlib Figure object
    """
    print("\n" + "="*60)
    print("Generating Figure 1: East Asian Colonial Gradient")
    print("="*60)
    
    # Define East Asian countries of interest
    east_asian_countries = {
        'Hong Kong': 'zh-cn',
        'Macao': 'zh-cn',  # Use zh-cn for comparison
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
                'native_language': native_lang,
                'english_advantage': advantage
            })
            print(f"  {country} ({native_lang}): {advantage:.2f}%")
    
    if len(data_points) == 0:
        print("  [!] No data found for East Asian countries")
        return None
    
    # Sort by English advantage (descending)
    data_points = sorted(data_points, key=lambda x: x['english_advantage'], reverse=True)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data for plotting
    countries = [d['country'] for d in data_points]
    advantages = [d['english_advantage'] for d in data_points]
    colors = [get_advantage_color(adv) for adv in advantages]
    
    # Create horizontal bar chart
    y_pos = np.arange(len(countries))
    bars = ax.barh(y_pos, advantages, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    
    # Customize axes
    ax.set_yticks(y_pos)
    ax.set_yticklabels(countries, fontsize=11)
    ax.set_xlabel('English Advantage (%)', fontsize=12, fontweight='bold')
    ax.set_title('East Asian Colonial Gradient\nEnglish Advantage by Country', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add vertical line at 0
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add value labels on bars
    for i, (bar, adv) in enumerate(zip(bars, advantages)):
        label_x = adv + (2 if adv > 0 else -2)
        ha = 'left' if adv > 0 else 'right'
        ax.text(label_x, i, f'{adv:.1f}%', 
                va='center', ha=ha, fontsize=10, fontweight='bold')
    
    # Add colonial history annotations
    for i, d in enumerate(data_points):
        if d['country'] == 'Hong Kong':
            ax.text(0.98, i, 'British colony 1842-1997', 
                   transform=ax.get_yaxis_transform(),
                   ha='right', va='center', fontsize=8, 
                   style='italic', color='gray')
        elif d['country'] == 'Macao':
            ax.text(0.98, i, 'Portuguese colony 1557-1999', 
                   transform=ax.get_yaxis_transform(),
                   ha='right', va='center', fontsize=8, 
                   style='italic', color='gray')
    
    # Add legend
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, fc='#E74C3C', alpha=0.8, label='Strong advantage (>20%)'),
        plt.Rectangle((0, 0), 1, 1, fc='#F39C12', alpha=0.8, label='Moderate (10-20%)'),
        plt.Rectangle((0, 0), 1, 1, fc='#27AE60', alpha=0.8, label='Weak (0-10%)'),
        plt.Rectangle((0, 0), 1, 1, fc='#3498DB', alpha=0.8, label='Native advantage (<0%)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    plt.tight_layout()
    
    # Save figure
    if save_path is None:
        save_path = OUTPUT_DIR / 'east_asian_gradient.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  [OK] Saved to: {save_path}")
    
    if show:
        plt.show()
    
    return fig


# ============================================================================
# Figure 2: Latin American Language Variants
# ============================================================================

def plot_latin_america_variants(
    exp4b_results: Dict,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot Latin American language variants with ANOVA results.
    
    Shows English advantage across Spanish, Portuguese, and French colonial
    language groups with error bars and significance markers.
    
    Args:
        exp4b_results: Results dictionary from experiment_4b_latin_america_variants()
        save_path: Optional path to save figure
        show: Whether to display the figure
    
    Returns:
        matplotlib Figure object
    """
    print("\n" + "="*60)
    print("Generating Figure 2: Latin American Language Variants")
    print("="*60)
    
    # Extract data
    groups = ['Spanish', 'Portuguese', 'French']
    means = [
        exp4b_results['spanish_advantage'],
        exp4b_results['portuguese_advantage'],
        exp4b_results['french_advantage']
    ]
    
    # Calculate standard errors
    spanish_se = exp4b_results['spanish_sd'] / np.sqrt(exp4b_results['spanish_n'])
    # For single observations, use 0 SE
    portuguese_se = 0
    french_se = 0
    
    errors = [spanish_se, portuguese_se, french_se]
    
    print(f"  Spanish (n={exp4b_results['spanish_n']}): {means[0]:.2f}% ± {errors[0]:.2f}%")
    print(f"  Portuguese (n={exp4b_results['portuguese_n']}): {means[1]:.2f}%")
    print(f"  French (n={exp4b_results['french_n']}): {means[2]:.2f}%")
    print(f"  ANOVA: F={exp4b_results['f_statistic']:.3f}, p={exp4b_results['p_value']:.4f}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Create bar chart
    x_pos = np.arange(len(groups))
    colors = [get_advantage_color(m) for m in means]
    
    bars = ax.bar(x_pos, means, yerr=errors, capsize=10,
                  color=colors, alpha=0.8, edgecolor='black', linewidth=1.5,
                  error_kw={'linewidth': 2, 'ecolor': 'black'})
    
    # Customize axes
    ax.set_xticks(x_pos)
    ax.set_xticklabels(groups, fontsize=12, fontweight='bold')
    ax.set_ylabel('English Advantage (%)', fontsize=12, fontweight='bold')
    ax.set_title('Latin American Colonial Language Variants\nEnglish Advantage by Colonial Language', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add horizontal line at 0
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add value labels on bars
    for i, (bar, mean, err) in enumerate(zip(bars, means, errors)):
        label_y = mean + err + 1
        ax.text(i, label_y, f'{mean:.1f}%', 
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add sample size labels
    for i, group in enumerate(groups):
        n = exp4b_results[f'{group.lower()}_n']
        ax.text(i, -2, f'n={n}', 
                ha='center', va='top', fontsize=9, style='italic', color='gray')
    
    # Add ANOVA results
    p_value = exp4b_results['p_value']
    sig_marker = exp4b_results['significance']
    eta_squared = exp4b_results['eta_squared']
    
    anova_text = f"One-Way ANOVA: F={exp4b_results['f_statistic']:.3f}, p={p_value:.4f} {sig_marker}\n"
    anova_text += f"Effect size: η² = {eta_squared:.3f} ({exp4b_results['effect_size_interpretation']})"
    
    ax.text(0.02, 0.98, anova_text, 
            transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', 
            facecolor='wheat', alpha=0.5))
    
    # Add significance markers if significant
    if p_value < 0.05 and exp4b_results['tukey_results'] is not None:
        # Add lines connecting significant pairs
        # (This would require parsing Tukey results - simplified for now)
        pass
    
    plt.tight_layout()
    
    # Save figure
    if save_path is None:
        save_path = OUTPUT_DIR / 'latin_america_variants.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  [OK] Saved to: {save_path}")
    
    if show:
        plt.show()
    
    return fig


# ============================================================================
# Figure 3: Hong Kong vs Macao Direct Comparison
# ============================================================================

def plot_hk_macao_comparison(
    exp4a_results: Dict,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot Hong Kong vs Macao direct comparison.
    
    Side-by-side comparison of Hong Kong's English advantage vs Macao's
    Portuguese advantage, with error bars and statistical test results.
    
    Args:
        exp4a_results: Results dictionary from experiment_4a_hk_macao_comparison()
        save_path: Optional path to save figure
        show: Whether to display the figure
    
    Returns:
        matplotlib Figure object
    """
    print("\n" + "="*60)
    print("Generating Figure 3: Hong Kong vs Macao Comparison")
    print("="*60)
    
    # Extract data
    hk_advantage = exp4a_results['hk_english_advantage']
    macao_advantage = exp4a_results['macao_portuguese_advantage']
    
    hk_advantages = np.array(exp4a_results['hk_advantages'])
    macao_advantages = np.array(exp4a_results['macao_advantages'])
    
    hk_se = hk_advantages.std(ddof=1) / np.sqrt(len(hk_advantages))
    macao_se = macao_advantages.std(ddof=1) / np.sqrt(len(macao_advantages))
    
    print(f"  Hong Kong English advantage: {hk_advantage:.2f}% ± {hk_se:.2f}%")
    print(f"  Macao Portuguese advantage: {macao_advantage:.2f}% ± {macao_se:.2f}%")
    print(f"  t-test: t={exp4a_results['t_statistic']:.3f}, p={exp4a_results['p_value']:.4f}")
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left panel: Bar comparison
    groups = ['Hong Kong\n(English)', 'Macao\n(Portuguese)']
    means = [hk_advantage, macao_advantage]
    errors = [hk_se, macao_se]
    colors = [get_advantage_color(hk_advantage), get_advantage_color(macao_advantage)]
    
    x_pos = np.arange(len(groups))
    bars = ax1.bar(x_pos, means, yerr=errors, capsize=10,
                   color=colors, alpha=0.8, edgecolor='black', linewidth=1.5,
                   error_kw={'linewidth': 2, 'ecolor': 'black'})
    
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(groups, fontsize=11, fontweight='bold')
    ax1.set_ylabel('Colonial Language Advantage (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Colonial Language Advantage Comparison', 
                  fontsize=13, fontweight='bold', pad=15)
    
    # Add horizontal line at 0
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add value labels
    for i, (bar, mean, err) in enumerate(zip(bars, means, errors)):
        label_y = mean + err + 2
        ax1.text(i, label_y, f'{mean:.1f}%', 
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add statistical test results
    p_value = exp4a_results['p_value']
    cohens_d = exp4a_results['cohens_d']
    sig_marker = exp4a_results['significance']
    
    test_text = f"Independent t-test:\n"
    test_text += f"t({exp4a_results['df']:.1f}) = {exp4a_results['t_statistic']:.3f}\n"
    test_text += f"p = {p_value:.4f} {sig_marker}\n"
    test_text += f"Cohen's d = {cohens_d:.3f}\n"
    test_text += f"({exp4a_results['effect_size_interpretation']} effect)"
    
    ax1.text(0.02, 0.98, test_text, 
            transform=ax1.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', 
            facecolor='wheat', alpha=0.5))
    
    # Right panel: Distribution comparison (violin plot or box plot)
    data_to_plot = [hk_advantages, macao_advantages]
    
    parts = ax2.violinplot(data_to_plot, positions=[0, 1], 
                           showmeans=True, showmedians=True)
    
    # Color the violin plots
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.6)
    
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(groups, fontsize=11, fontweight='bold')
    ax2.set_ylabel('Colonial Language Advantage (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Distribution Across Models', 
                  fontsize=13, fontweight='bold', pad=15)
    
    # Add horizontal line at 0
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add sample size
    ax2.text(0, ax2.get_ylim()[0], f'n={exp4a_results["hk_n_models"]}', 
            ha='center', va='top', fontsize=9, style='italic', color='gray')
    ax2.text(1, ax2.get_ylim()[0], f'n={exp4a_results["macao_n_models"]}', 
            ha='center', va='top', fontsize=9, style='italic', color='gray')
    
    plt.suptitle('Hong Kong vs Macao: Colonial Language Effects', 
                 fontsize=15, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Save figure
    if save_path is None:
        save_path = OUTPUT_DIR / 'hk_macao_comparison.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  [OK] Saved to: {save_path}")
    
    if show:
        plt.show()
    
    return fig


# ============================================================================
# Figure 4: Regression Coefficients (Forest Plot)
# ============================================================================

def plot_regression_coefficients(
    regression_results: Dict,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot regression coefficients as a forest plot.
    
    Shows β coefficients with 95% confidence intervals for colonial history
    variables and control variables.
    
    Args:
        regression_results: Results dictionary from regression analysis
        save_path: Optional path to save figure
        show: Whether to display the figure
    
    Returns:
        matplotlib Figure object
    """
    print("\n" + "="*60)
    print("Generating Figure 4: Regression Coefficients")
    print("="*60)
    
    # This function will be implemented when regression analysis is complete
    print("  [!] Regression analysis not yet implemented")
    print("  [!] Skipping regression coefficients plot")
    
    return None


# ============================================================================
# Main function for generating all figures
# ============================================================================

def generate_all_figures(
    advantage_df: pd.DataFrame,
    exp4a_results: Dict,
    exp4b_results: Dict,
    exp4c_results: Optional[Dict] = None,
    regression_results: Optional[Dict] = None,
    show: bool = False
) -> Dict[str, plt.Figure]:
    """
    Generate all colonial history visualization figures.
    
    Args:
        advantage_df: Pre-computed advantage data
        exp4a_results: Results from Experiment 4a
        exp4b_results: Results from Experiment 4b
        exp4c_results: Results from Experiment 4c (optional)
        regression_results: Results from regression analysis (optional)
        show: Whether to display figures
    
    Returns:
        Dictionary mapping figure names to Figure objects
    """
    print("\n" + "="*80)
    print("Generating All Colonial History Figures")
    print("="*80)
    
    figures = {}
    
    # Figure 1: East Asian gradient
    fig1 = plot_east_asian_gradient(advantage_df, show=show)
    if fig1 is not None:
        figures['east_asian_gradient'] = fig1
    
    # Figure 2: Latin American variants
    fig2 = plot_latin_america_variants(exp4b_results, show=show)
    if fig2 is not None:
        figures['latin_america_variants'] = fig2
    
    # Figure 3: Hong Kong vs Macao
    fig3 = plot_hk_macao_comparison(exp4a_results, show=show)
    if fig3 is not None:
        figures['hk_macao_comparison'] = fig3
    
    # Figure 4: Regression coefficients (if available)
    if regression_results is not None:
        fig4 = plot_regression_coefficients(regression_results, show=show)
        if fig4 is not None:
            figures['regression_coefficients'] = fig4
    
    print("\n" + "="*80)
    print(f"Generated {len(figures)} figures")
    print("="*80)
    
    return figures


if __name__ == "__main__":
    print("This module provides visualization functions for colonial history analysis.")
    print("Import and use the functions in your analysis scripts.")
