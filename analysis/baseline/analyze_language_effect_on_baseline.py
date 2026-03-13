#!/usr/bin/env python3
"""
Analyze language effect on LLM baseline (intrinsic) values.

This script analyzes how different prompt languages affect LLM's expressed values
in the baseline condition (Stage 1, no roleplay).

Key questions:
1. Which languages induce more secular vs traditional values?
2. Which languages induce more self-expression vs survival values?
3. How much do individual models vary across languages?
4. Are there systematic patterns (e.g., Arabic → traditional, German → secular)?

Input:
- SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv

Output:
- results/analysis/baseline_language_effect/language_effect_summary.csv
- results/analysis/baseline_language_effect/model_language_stability.csv
- results/analysis/baseline_language_effect/language_effect_stats.txt
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_FILE = PROJECT_ROOT / "SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv"
OUTPUT_DIR = PROJECT_ROOT / "results/analysis/baseline_language_effect"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load baseline PCA coordinates."""
    df = pd.read_csv(DATA_FILE)
    print(f"Loaded {len(df)} data points")
    print(f"Models: {df['model_name'].nunique()}")
    print(f"Languages: {df['language'].nunique()}")
    print(f"Languages: {sorted(df['language'].unique())}")
    return df

def analyze_language_effect(df):
    """Analyze how each language affects value distribution."""
    
    # Group by language
    lang_stats = df.groupby('language').agg({
        'PC1': ['mean', 'std', 'min', 'max', 'count'],
        'PC2': ['mean', 'std', 'min', 'max']
    }).round(3)
    
    # Flatten column names
    lang_stats.columns = ['_'.join(col).strip() for col in lang_stats.columns.values]
    lang_stats = lang_stats.reset_index()
    
    # Sort by PC1 mean (Traditional to Secular)
    lang_stats = lang_stats.sort_values('PC1_mean', ascending=False)
    
    # Add interpretation
    def interpret_pc1(val):
        if val > 2:
            return "Very Secular"
        elif val > 0:
            return "Secular"
        elif val > -2:
            return "Traditional"
        else:
            return "Very Traditional"
    
    def interpret_pc2(val):
        if val > 2:
            return "Strong Self-expression"
        elif val > 0:
            return "Self-expression"
        elif val > -2:
            return "Survival"
        else:
            return "Strong Survival"
    
    lang_stats['PC1_interpretation'] = lang_stats['PC1_mean'].apply(interpret_pc1)
    lang_stats['PC2_interpretation'] = lang_stats['PC2_mean'].apply(interpret_pc2)
    
    # Calculate range (max - min) for each language
    lang_stats['PC1_range'] = lang_stats['PC1_max'] - lang_stats['PC1_min']
    lang_stats['PC2_range'] = lang_stats['PC2_max'] - lang_stats['PC2_min']
    
    return lang_stats

def analyze_model_stability(df):
    """Analyze how stable each model is across languages."""
    
    model_stats = []
    
    for model in df['model_name'].unique():
        model_data = df[df['model_name'] == model]
        
        if len(model_data) < 2:
            continue
        
        pc1_range = model_data['PC1'].max() - model_data['PC1'].min()
        pc2_range = model_data['PC2'].max() - model_data['PC2'].min()
        pc1_std = model_data['PC1'].std()
        pc2_std = model_data['PC2'].std()
        
        # Euclidean distance from centroid
        centroid_pc1 = model_data['PC1'].mean()
        centroid_pc2 = model_data['PC2'].mean()
        model_data_copy = model_data.copy()
        model_data_copy['distance_from_centroid'] = np.sqrt(
            (model_data_copy['PC1'] - centroid_pc1)**2 + 
            (model_data_copy['PC2'] - centroid_pc2)**2
        )
        mean_distance = model_data_copy['distance_from_centroid'].mean()
        max_distance = model_data_copy['distance_from_centroid'].max()
        
        model_stats.append({
            'model_name': model,
            'n_languages': len(model_data),
            'PC1_mean': model_data['PC1'].mean(),
            'PC1_std': pc1_std,
            'PC1_range': pc1_range,
            'PC2_mean': model_data['PC2'].mean(),
            'PC2_std': pc2_std,
            'PC2_range': pc2_range,
            'mean_distance_from_centroid': mean_distance,
            'max_distance_from_centroid': max_distance
        })
    
    model_df = pd.DataFrame(model_stats)
    
    # Sort by stability (lower range = more stable)
    model_df = model_df.sort_values('PC1_range')
    
    # Add stability rating
    def stability_rating(range_val):
        if range_val < 1:
            return "Very Stable"
        elif range_val < 2:
            return "Stable"
        elif range_val < 3:
            return "Moderate"
        elif range_val < 4:
            return "Unstable"
        else:
            return "Very Unstable"
    
    model_df['stability_rating'] = model_df['PC1_range'].apply(stability_rating)
    
    return model_df.round(3)

def calculate_language_distances(df):
    """Calculate pairwise distances between languages."""
    
    # Get mean coordinates for each language
    lang_means = df.groupby('language')[['PC1', 'PC2']].mean()
    
    # Calculate pairwise Euclidean distances
    languages = lang_means.index.tolist()
    n_langs = len(languages)
    
    distance_matrix = np.zeros((n_langs, n_langs))
    
    for i, lang1 in enumerate(languages):
        for j, lang2 in enumerate(languages):
            if i != j:
                pc1_diff = lang_means.loc[lang1, 'PC1'] - lang_means.loc[lang2, 'PC1']
                pc2_diff = lang_means.loc[lang1, 'PC2'] - lang_means.loc[lang2, 'PC2']
                distance_matrix[i, j] = np.sqrt(pc1_diff**2 + pc2_diff**2)
    
    # Create DataFrame
    distance_df = pd.DataFrame(distance_matrix, index=languages, columns=languages)
    
    # Get top 10 most distant pairs
    distances = []
    for i, lang1 in enumerate(languages):
        for j, lang2 in enumerate(languages):
            if i < j:  # Only upper triangle
                distances.append({
                    'language_1': lang1,
                    'language_2': lang2,
                    'distance': distance_matrix[i, j]
                })
    
    distance_pairs = pd.DataFrame(distances).sort_values('distance', ascending=False)
    
    return distance_df.round(3), distance_pairs.round(3)

def statistical_tests(df):
    """Perform statistical tests on language effects."""
    
    results = []
    
    # ANOVA: Does language significantly affect PC1?
    languages = df['language'].unique()
    pc1_groups = [df[df['language'] == lang]['PC1'].values for lang in languages]
    f_stat_pc1, p_val_pc1 = stats.f_oneway(*pc1_groups)
    
    results.append({
        'test': 'ANOVA on PC1 (Traditional-Secular)',
        'statistic': f'F={f_stat_pc1:.3f}',
        'p_value': f'{p_val_pc1:.6f}',
        'interpretation': 'Significant' if p_val_pc1 < 0.05 else 'Not significant'
    })
    
    # ANOVA: Does language significantly affect PC2?
    pc2_groups = [df[df['language'] == lang]['PC2'].values for lang in languages]
    f_stat_pc2, p_val_pc2 = stats.f_oneway(*pc2_groups)
    
    results.append({
        'test': 'ANOVA on PC2 (Survival-Self-expression)',
        'statistic': f'F={f_stat_pc2:.3f}',
        'p_value': f'{p_val_pc2:.6f}',
        'interpretation': 'Significant' if p_val_pc2 < 0.05 else 'Not significant'
    })
    
    # Pairwise comparisons: Arabic vs others
    if 'ar' in languages:
        ar_pc1 = df[df['language'] == 'ar']['PC1'].values
        
        for lang in ['en', 'fr', 'es', 'ru', 'zh-cn']:
            if lang in languages:
                lang_pc1 = df[df['language'] == lang]['PC1'].values
                t_stat, p_val = stats.ttest_ind(ar_pc1, lang_pc1)
                
                results.append({
                    'test': f'Arabic vs {lang.upper()} on PC1',
                    'statistic': f't={t_stat:.3f}',
                    'p_value': f'{p_val:.6f}',
                    'interpretation': 'Significant' if p_val < 0.05 else 'Not significant'
                })
    
    return pd.DataFrame(results)

def generate_summary_report(lang_stats, model_stats, distance_pairs, stat_tests):
    """Generate a text summary report."""
    
    report = []
    report.append("=" * 80)
    report.append("BASELINE LANGUAGE EFFECT ANALYSIS")
    report.append("=" * 80)
    report.append("")
    
    # Language effect summary
    report.append("1. LANGUAGE EFFECT ON VALUE DISTRIBUTION")
    report.append("-" * 80)
    report.append("")
    report.append("Languages ranked by PC1 (Traditional → Secular):")
    report.append("")
    
    for _, row in lang_stats.iterrows():
        report.append(f"  {row['language']:6s}: PC1={row['PC1_mean']:+6.2f} (±{row['PC1_std']:.2f}), "
                     f"PC2={row['PC2_mean']:+6.2f} (±{row['PC2_std']:.2f}) - "
                     f"{row['PC1_interpretation']}, {row['PC2_interpretation']}")
    
    report.append("")
    report.append(f"PC1 range across languages: {lang_stats['PC1_mean'].max() - lang_stats['PC1_mean'].min():.2f} units")
    report.append(f"PC2 range across languages: {lang_stats['PC2_mean'].max() - lang_stats['PC2_mean'].min():.2f} units")
    report.append("")
    
    # Most/least secular languages
    most_secular = lang_stats.iloc[0]
    most_traditional = lang_stats.iloc[-1]
    report.append(f"Most Secular: {most_secular['language']} (PC1={most_secular['PC1_mean']:+.2f})")
    report.append(f"Most Traditional: {most_traditional['language']} (PC1={most_traditional['PC1_mean']:+.2f})")
    report.append("")
    
    # Model stability
    report.append("2. MODEL LANGUAGE STABILITY")
    report.append("-" * 80)
    report.append("")
    report.append("Models ranked by stability (PC1 range across languages):")
    report.append("")
    
    for _, row in model_stats.head(10).iterrows():
        report.append(f"  {row['model_name']:40s}: Range={row['PC1_range']:.2f}, "
                     f"Std={row['PC1_std']:.2f} - {row['stability_rating']}")
    
    report.append("")
    report.append("Most unstable models:")
    report.append("")
    
    for _, row in model_stats.tail(5).iterrows():
        report.append(f"  {row['model_name']:40s}: Range={row['PC1_range']:.2f}, "
                     f"Std={row['PC1_std']:.2f} - {row['stability_rating']}")
    
    report.append("")
    
    # Language distances
    report.append("3. LANGUAGE PAIRWISE DISTANCES")
    report.append("-" * 80)
    report.append("")
    report.append("Top 10 most distant language pairs:")
    report.append("")
    
    for _, row in distance_pairs.head(10).iterrows():
        report.append(f"  {row['language_1']:6s} ↔ {row['language_2']:6s}: {row['distance']:.2f} units")
    
    report.append("")
    
    # Statistical tests
    report.append("4. STATISTICAL TESTS")
    report.append("-" * 80)
    report.append("")
    
    for _, row in stat_tests.iterrows():
        report.append(f"  {row['test']:40s}: {row['statistic']:12s}, p={row['p_value']:10s} - {row['interpretation']}")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    print("Loading data...")
    df = load_data()
    
    print("\nAnalyzing language effect...")
    lang_stats = analyze_language_effect(df)
    print(f"Analyzed {len(lang_stats)} languages")
    
    print("\nAnalyzing model stability...")
    model_stats = analyze_model_stability(df)
    print(f"Analyzed {len(model_stats)} models")
    
    print("\nCalculating language distances...")
    distance_matrix, distance_pairs = calculate_language_distances(df)
    
    print("\nPerforming statistical tests...")
    stat_tests = statistical_tests(df)
    
    print("\nGenerating summary report...")
    report = generate_summary_report(lang_stats, model_stats, distance_pairs, stat_tests)
    
    # Save outputs
    print("\nSaving results...")
    lang_stats.to_csv(OUTPUT_DIR / "language_effect_summary.csv", index=False)
    model_stats.to_csv(OUTPUT_DIR / "model_language_stability.csv", index=False)
    distance_matrix.to_csv(OUTPUT_DIR / "language_distance_matrix.csv")
    distance_pairs.to_csv(OUTPUT_DIR / "language_pairwise_distances.csv", index=False)
    stat_tests.to_csv(OUTPUT_DIR / "statistical_tests.csv", index=False)
    
    with open(OUTPUT_DIR / "language_effect_stats.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print("\nFiles created:")
    print("  - language_effect_summary.csv")
    print("  - model_language_stability.csv")
    print("  - language_distance_matrix.csv")
    print("  - language_pairwise_distances.csv")
    print("  - statistical_tests.csv")
    print("  - language_effect_stats.txt")

if __name__ == "__main__":
    main()
