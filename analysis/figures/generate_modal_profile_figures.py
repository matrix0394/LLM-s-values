#!/usr/bin/env python3
"""
Generate main and SI figures from modal profile tables.

Input:
- SI/model_responses/baseline_intrinsic_values/Table_S1_baseline_modal_profiles.csv
- SI/model_responses/imitated_contextual_values/Table_S3_roleplay_modal_profiles.csv

Output:
- figures/main/Fig_main_baseline_heatmap.pdf
- figures/main/Fig_main_delta_heatmap.pdf
- figures/si/FigS_consistency_distribution_by_model.pdf
- figures/si/FigS_response_distribution_by_question.pdf
- figures/si/FigS_imitation_country_shift_summary.pdf
- Various CSV files for source data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path for importing IVSQuestionProcessor
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.base.ivs_question_processor import IVSQuestionProcessor

# Set up matplotlib for publication quality
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.dpi'] = 300

# =============================================================================
# QUESTION METADATA - Fixed order and scale ranges
# =============================================================================
QUESTION_ORDER = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']

QUESTION_LABELS = {
    'A008': 'A008\nHappiness',
    'A165': 'A165\nTrust',
    'E018': 'E018\nRespect authority',
    'E025': 'E025\nPetition signing',
    'F063': 'F063\nImportance of God',
    'F118': 'F118\nJustifiable homosexuality',
    'F120': 'F120\nJustifiable abortion',
    'G006': 'G006\nNational pride',
    'Y002': 'Y002\nPost-materialist index',
    'Y003': 'Y003\nAutonomy index'
}

QUESTION_METADATA = {
    'A008': {'min': 1, 'max': 4, 'description': 'Feeling of happiness'},
    'A165': {'min': 1, 'max': 2, 'description': 'Most people can be trusted'},
    'E018': {'min': 1, 'max': 3, 'description': 'Greater respect for authority'},
    'E025': {'min': 1, 'max': 3, 'description': 'Signing a petition'},
    'F063': {'min': 1, 'max': 10, 'description': 'Importance of God'},
    'F118': {'min': 1, 'max': 10, 'description': 'Justifiable homosexuality'},
    'F120': {'min': 1, 'max': 10, 'description': 'Justifiable abortion'},
    'G006': {'min': 1, 'max': 4, 'description': 'National pride'},
    # Y002: materialist_score ranges 1-3 (1=Materialist, 2=Mixed, 3=Postmaterialist)
    'Y002': {'min': 1, 'max': 3, 'description': 'Post-materialist index'},
    # Y003: y003_score = traditional - secular_rational, ranges from -2 to 2
    'Y003': {'min': -2, 'max': 2, 'description': 'Autonomy index (traditional vs secular-rational)'}
}

# Simple questions (single numeric response)
SIMPLE_QUESTIONS = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']
# Complex questions (multiple choices - need special processing)
COMPLEX_QUESTIONS = ['Y002', 'Y003']


def parse_modal_response(response, question_id):
    """Parse modal_response, handling NA and complex responses.
    
    For Y002: Parse two choices and compute materialist_score (1-3)
    For Y003: Parse selected values and compute y003_score (-2 to 2)
    """
    if pd.isna(response) or response == 'NA' or response == '':
        return np.nan
    
    response_str = str(response).strip()
    
    if question_id == 'Y002':
        # Y002: Parse two choices and compute materialist_score
        # Format: "first_choice second_choice" (e.g., "3 1" or "2 4")
        parts = response_str.split()
        if len(parts) >= 2:
            try:
                first_choice = int(parts[0])
                second_choice = int(parts[1])
                # Use IVSQuestionProcessor to compute materialist_score
                return float(IVSQuestionProcessor.process_y002(first_choice, second_choice))
            except (ValueError, IndexError):
                return np.nan
        return np.nan
    
    elif question_id == 'Y003':
        # Y003: Parse selected values and compute y003_score
        # Format: "1 4 6 8 9" (selected value indices from 1-11)
        parts = response_str.split()
        if parts:
            try:
                selected_values = [int(p) for p in parts if 1 <= int(p) <= 11]
                if selected_values:
                    # Use IVSQuestionProcessor to compute y003_score
                    result = IVSQuestionProcessor.process_y003(selected_values)
                    return float(result['y003_score'])
            except (ValueError, IndexError):
                return np.nan
        return np.nan
    
    else:
        # Simple single-choice questions
        try:
            return float(response_str)
        except ValueError:
            return np.nan


def normalize_value(value, question_id):
    """Normalize value to 0-1 range based on question scale."""
    if pd.isna(value):
        return np.nan
    meta = QUESTION_METADATA[question_id]
    return (value - meta['min']) / (meta['max'] - meta['min'])


def normalize_delta(delta, question_id):
    """Normalize delta by question range."""
    if pd.isna(delta):
        return np.nan
    meta = QUESTION_METADATA[question_id]
    return delta / (meta['max'] - meta['min'])


def load_and_preprocess_data(baseline_path, roleplay_path):
    """Load and preprocess both datasets."""
    print("Loading data...")
    baseline_df = pd.read_csv(baseline_path)
    roleplay_df = pd.read_csv(roleplay_path)
    
    # Parse modal responses
    print("Parsing modal responses...")
    baseline_df['parsed_response'] = baseline_df.apply(
        lambda row: parse_modal_response(row['modal_response'], row['question_id']), axis=1
    )
    roleplay_df['parsed_response'] = roleplay_df.apply(
        lambda row: parse_modal_response(row['modal_response'], row['question_id']), axis=1
    )
    
    return baseline_df, roleplay_df


def create_baseline_heatmap(baseline_df, output_dir):
    """Create Fig_main_baseline_heatmap.pdf"""
    print("Creating baseline heatmap...")
    
    # Aggregate: for each model×question_id, take median across languages
    baseline_agg = baseline_df.groupby(['model', 'question_id'])['parsed_response'].median().reset_index()
    baseline_agg.columns = ['model', 'question_id', 'baseline_agg']
    
    # Pivot to matrix
    baseline_matrix = baseline_agg.pivot(index='model', columns='question_id', values='baseline_agg')
    baseline_matrix = baseline_matrix[QUESTION_ORDER]  # Fixed column order
    
    # Save raw matrix
    baseline_matrix.to_csv(output_dir / 'main_baseline_matrix_raw.csv')
    
    # Normalize within each question
    baseline_matrix_norm = baseline_matrix.copy()
    for q in QUESTION_ORDER:
        baseline_matrix_norm[q] = baseline_matrix[q].apply(lambda x: normalize_value(x, q))
    
    baseline_matrix_norm.to_csv(output_dir / 'main_baseline_matrix_norm.csv')
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Use normalized values for coloring
    sns.heatmap(baseline_matrix_norm, 
                annot=baseline_matrix.round(1),  # Show raw values
                fmt='g',
                cmap='RdYlBu_r',
                center=0.5,
                vmin=0, vmax=1,
                ax=ax,
                cbar_kws={'label': 'Normalized value (0-1)'})
    
    ax.set_xticklabels([QUESTION_LABELS[q] for q in QUESTION_ORDER], rotation=45, ha='right')
    ax.set_ylabel('Model')
    ax.set_xlabel('')
    ax.set_title('Baseline Intrinsic Values by Model\n(within-question normalized values for visualization; raw values in Table S1)')
    
    plt.tight_layout()
    fig.savefig(output_dir / 'Fig_main_baseline_heatmap.pdf', bbox_inches='tight')
    fig.savefig(output_dir / 'Fig_main_baseline_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    return baseline_matrix


def create_delta_heatmap(baseline_df, roleplay_df, output_dir):
    """Create Fig_main_delta_heatmap.pdf"""
    print("Creating delta heatmap...")
    
    # Baseline aggregation
    baseline_agg = baseline_df.groupby(['model', 'question_id'])['parsed_response'].median().reset_index()
    baseline_agg.columns = ['model', 'question_id', 'baseline_agg']
    
    # Roleplay aggregation: median across country×language
    roleplay_agg = roleplay_df.groupby(['model', 'question_id'])['parsed_response'].median().reset_index()
    roleplay_agg.columns = ['model', 'question_id', 'roleplay_agg']
    
    # Merge and compute delta
    merged = pd.merge(baseline_agg, roleplay_agg, on=['model', 'question_id'])
    merged['delta'] = merged['roleplay_agg'] - merged['baseline_agg']
    
    # Pivot to matrix
    delta_matrix = merged.pivot(index='model', columns='question_id', values='delta')
    delta_matrix = delta_matrix[QUESTION_ORDER]
    
    # Save raw delta matrix
    delta_matrix.to_csv(output_dir / 'main_delta_matrix_raw.csv')
    
    # Normalize delta by question range
    delta_matrix_norm = delta_matrix.copy()
    for q in QUESTION_ORDER:
        delta_matrix_norm[q] = delta_matrix[q].apply(lambda x: normalize_delta(x, q))
    
    delta_matrix_norm.to_csv(output_dir / 'main_delta_matrix_norm.csv')
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Find symmetric color range
    max_abs = max(abs(delta_matrix_norm.min().min()), abs(delta_matrix_norm.max().max()))
    
    sns.heatmap(delta_matrix_norm,
                annot=delta_matrix.round(2),  # Show raw delta values
                fmt='g',
                cmap='RdBu_r',
                center=0,
                vmin=-max_abs, vmax=max_abs,
                ax=ax,
                cbar_kws={'label': 'Normalized delta'})
    
    ax.set_xticklabels([QUESTION_LABELS[q] for q in QUESTION_ORDER], rotation=45, ha='right')
    ax.set_ylabel('Model')
    ax.set_xlabel('')
    ax.set_title('Cultural Imitation Effect (Roleplay - Baseline)\n(within-question normalized delta for visualization; raw values in Table S3)')
    
    plt.tight_layout()
    fig.savefig(output_dir / 'Fig_main_delta_heatmap.pdf', bbox_inches='tight')
    fig.savefig(output_dir / 'Fig_main_delta_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    return delta_matrix


def create_consistency_summary(baseline_df, roleplay_df, output_dir):
    """Create consistency summary and add to delta heatmap."""
    print("Creating consistency summary...")
    
    # Calculate mean consistency per model for baseline
    baseline_consistency = baseline_df.groupby('model')['consistency_rate'].mean().reset_index()
    baseline_consistency.columns = ['model', 'baseline_mean_consistency']
    
    # Calculate mean consistency per model for roleplay
    roleplay_consistency = roleplay_df.groupby('model')['consistency_rate'].mean().reset_index()
    roleplay_consistency.columns = ['model', 'roleplay_mean_consistency']
    
    # Merge
    consistency_summary = pd.merge(baseline_consistency, roleplay_consistency, on='model')
    consistency_summary.to_csv(output_dir / 'model_consistency_summary.csv', index=False)
    
    # Create paired dot plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    models = consistency_summary['model'].values
    y_pos = np.arange(len(models))
    
    # Plot lines connecting baseline and roleplay
    for i, (_, row) in enumerate(consistency_summary.iterrows()):
        ax.plot([row['baseline_mean_consistency'], row['roleplay_mean_consistency']], 
                [i, i], 'gray', alpha=0.5, linewidth=1)
    
    # Plot points
    ax.scatter(consistency_summary['baseline_mean_consistency'], y_pos, 
               c='blue', s=50, label='Baseline', zorder=5)
    ax.scatter(consistency_summary['roleplay_mean_consistency'], y_pos, 
               c='red', s=50, label='Roleplay', zorder=5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([m.split('/')[-1] for m in models], fontsize=8)
    ax.set_xlabel('Mean Consistency Rate')
    ax.set_title('Response Consistency: Baseline vs Roleplay')
    ax.legend(loc='lower right')
    ax.set_xlim(0.5, 1.05)
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(output_dir / 'Fig_main_consistency_comparison.pdf', bbox_inches='tight')
    fig.savefig(output_dir / 'Fig_main_consistency_comparison.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    return consistency_summary


def create_consistency_distribution(baseline_df, roleplay_df, output_dir):
    """Create FigS_consistency_distribution_by_model.pdf"""
    print("Creating consistency distribution figure...")
    
    # Prepare data - make copies to avoid modifying original
    baseline_copy = baseline_df.copy()
    roleplay_copy = roleplay_df.copy()
    baseline_copy['condition'] = 'Baseline'
    roleplay_copy['condition'] = 'Roleplay'
    
    combined = pd.concat([
        baseline_copy[['model', 'consistency_rate', 'condition']],
        roleplay_copy[['model', 'consistency_rate', 'condition']]
    ])
    
    # Get unique models
    models = sorted(combined['model'].unique())
    n_models = len(models)
    
    # Create figure with subplots
    n_cols = 4
    n_rows = (n_models + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 3 * n_rows))
    axes = axes.flatten()
    
    for i, model in enumerate(models):
        ax = axes[i]
        model_data = combined[combined['model'] == model]
        
        baseline_data = model_data[model_data['condition'] == 'Baseline']['consistency_rate'].dropna().values
        roleplay_data = model_data[model_data['condition'] == 'Roleplay']['consistency_rate'].dropna().values
        
        # Use box plot instead of violin to handle edge cases better
        box_data = []
        labels = []
        colors = []
        
        if len(baseline_data) > 0:
            box_data.append(baseline_data)
            labels.append('Baseline')
            colors.append('blue')
        if len(roleplay_data) > 0:
            box_data.append(roleplay_data)
            labels.append('Roleplay')
            colors.append('red')
        
        if len(box_data) > 0:
            bp = ax.boxplot(box_data, labels=labels, patch_artist=True)
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.5)
        
        ax.set_ylabel('Consistency Rate')
        ax.set_title(model.split('/')[-1], fontsize=9)
        ax.set_ylim(0, 1.1)
        ax.grid(axis='y', alpha=0.3)
    
    # Hide empty subplots
    for i in range(n_models, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle('Consistency Rate Distribution by Model', fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(output_dir / 'FigS_consistency_distribution_by_model.pdf', bbox_inches='tight')
    fig.savefig(output_dir / 'FigS_consistency_distribution_by_model.png', bbox_inches='tight', dpi=300)
    plt.close()


def create_response_distribution(baseline_df, roleplay_df, output_dir):
    """Create FigS_response_distribution_by_question.pdf"""
    print("Creating response distribution figure...")
    
    # Only use simple questions for this visualization
    questions_to_plot = SIMPLE_QUESTIONS
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    distribution_data = []
    
    for i, q in enumerate(questions_to_plot):
        ax = axes[i]
        meta = QUESTION_METADATA[q]
        
        # Get responses for this question
        baseline_responses = baseline_df[baseline_df['question_id'] == q]['parsed_response'].dropna()
        roleplay_responses = roleplay_df[roleplay_df['question_id'] == q]['parsed_response'].dropna()
        
        # Count frequencies
        all_values = list(range(meta['min'], meta['max'] + 1))
        
        baseline_counts = baseline_responses.value_counts().reindex(all_values, fill_value=0)
        roleplay_counts = roleplay_responses.value_counts().reindex(all_values, fill_value=0)
        
        # Normalize to proportions
        baseline_props = baseline_counts / baseline_counts.sum() if baseline_counts.sum() > 0 else baseline_counts
        roleplay_props = roleplay_counts / roleplay_counts.sum() if roleplay_counts.sum() > 0 else roleplay_counts
        
        # Store for CSV
        for val in all_values:
            distribution_data.append({
                'question_id': q,
                'value': val,
                'baseline_count': baseline_counts.get(val, 0),
                'baseline_proportion': baseline_props.get(val, 0),
                'roleplay_count': roleplay_counts.get(val, 0),
                'roleplay_proportion': roleplay_props.get(val, 0)
            })
        
        # Plot grouped bar chart
        x = np.arange(len(all_values))
        width = 0.35
        
        ax.bar(x - width/2, baseline_props.values, width, label='Baseline', color='blue', alpha=0.7)
        ax.bar(x + width/2, roleplay_props.values, width, label='Roleplay', color='red', alpha=0.7)
        
        ax.set_xlabel('Response Value')
        ax.set_ylabel('Proportion')
        ax.set_title(QUESTION_LABELS[q].replace('\n', ' '))
        ax.set_xticks(x)
        ax.set_xticklabels(all_values)
        ax.legend(fontsize=8)
        ax.grid(axis='y', alpha=0.3)
    
    # Save distribution data
    pd.DataFrame(distribution_data).to_csv(output_dir / 'question_response_distribution.csv', index=False)
    
    plt.suptitle('Response Distribution by Question (Baseline vs Roleplay)', fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(output_dir / 'FigS_response_distribution_by_question.pdf', bbox_inches='tight')
    fig.savefig(output_dir / 'FigS_response_distribution_by_question.png', bbox_inches='tight', dpi=300)
    plt.close()


def create_country_shift_summary(baseline_df, roleplay_df, output_dir):
    """Create FigS_imitation_country_shift_summary.pdf"""
    print("Creating country shift summary...")
    
    # Get baseline aggregated by model, language, question
    baseline_agg = baseline_df.groupby(['model', 'language', 'question_id'])['parsed_response'].median().reset_index()
    baseline_agg.columns = ['model', 'language', 'question_id', 'baseline_response']
    
    # Merge with roleplay
    roleplay_with_baseline = pd.merge(
        roleplay_df[['model', 'country', 'language', 'question_id', 'parsed_response']],
        baseline_agg,
        on=['model', 'language', 'question_id'],
        how='left'
    )
    
    # Calculate absolute shift
    roleplay_with_baseline['abs_shift'] = abs(
        roleplay_with_baseline['parsed_response'] - roleplay_with_baseline['baseline_response']
    )
    
    # Aggregate shift score per model×country×language
    shift_scores = roleplay_with_baseline.groupby(['model', 'country', 'language'])['abs_shift'].mean().reset_index()
    shift_scores.columns = ['model', 'country', 'language', 'shift_score']
    
    # Also aggregate per model×country (across languages)
    shift_by_model_country = shift_scores.groupby(['model', 'country'])['shift_score'].mean().reset_index()
    
    # Save shift scores
    shift_scores.to_csv(output_dir / 'country_shift_scores.csv', index=False)
    shift_by_model_country.to_csv(output_dir / 'country_shift_scores_by_model.csv', index=False)
    
    # Figure 1: Shift score distribution by model
    fig, ax = plt.subplots(figsize=(14, 8))
    
    models = sorted(shift_by_model_country['model'].unique())
    
    # Create box plot data
    box_data = [shift_by_model_country[shift_by_model_country['model'] == m]['shift_score'].values 
                for m in models]
    
    bp = ax.boxplot(box_data, labels=[m.split('/')[-1] for m in models], patch_artist=True)
    
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)
    
    ax.set_xticklabels([m.split('/')[-1] for m in models], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Mean Absolute Shift Score')
    ax.set_title('Cultural Imitation Shift by Model\n(Distribution across countries)')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(output_dir / 'FigS_imitation_shift_by_model.pdf', bbox_inches='tight')
    fig.savefig(output_dir / 'FigS_imitation_shift_by_model.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # Figure 2: Top/Bottom countries
    overall_country_shift = shift_by_model_country.groupby('country')['shift_score'].mean().reset_index()
    overall_country_shift = overall_country_shift.sort_values('shift_score', ascending=False)
    
    # Save overall country ranking
    overall_country_shift.to_csv(output_dir / 'country_shift_ranking.csv', index=False)
    
    # Plot top 15 and bottom 15
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    
    # Top 15
    top_15 = overall_country_shift.head(15)
    axes[0].barh(range(len(top_15)), top_15['shift_score'].values, color='coral')
    axes[0].set_yticks(range(len(top_15)))
    axes[0].set_yticklabels(top_15['country'].values)
    axes[0].set_xlabel('Mean Shift Score')
    axes[0].set_title('Top 15 Countries (Highest Shift)')
    axes[0].invert_yaxis()
    axes[0].grid(axis='x', alpha=0.3)
    
    # Bottom 15
    bottom_15 = overall_country_shift.tail(15)
    axes[1].barh(range(len(bottom_15)), bottom_15['shift_score'].values, color='lightgreen')
    axes[1].set_yticks(range(len(bottom_15)))
    axes[1].set_yticklabels(bottom_15['country'].values)
    axes[1].set_xlabel('Mean Shift Score')
    axes[1].set_title('Bottom 15 Countries (Lowest Shift)')
    axes[1].invert_yaxis()
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.suptitle('Countries by Cultural Imitation Shift', fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(output_dir / 'FigS_imitation_country_shift_summary.pdf', bbox_inches='tight')
    fig.savefig(output_dir / 'FigS_imitation_country_shift_summary.png', bbox_inches='tight', dpi=300)
    plt.close()


def main():
    """Main function to generate all figures."""
    # Paths
    baseline_path = Path('SI/model_responses/baseline_intrinsic_values/Table_S1_baseline_modal_profiles.csv')
    roleplay_path = Path('SI/model_responses/imitated_contextual_values/Table_S3_roleplay_modal_profiles.csv')
    
    # Create output directories
    main_output = Path('figures/main')
    si_output = Path('figures/si')
    main_output.mkdir(parents=True, exist_ok=True)
    si_output.mkdir(parents=True, exist_ok=True)
    
    # Load data
    baseline_df, roleplay_df = load_and_preprocess_data(baseline_path, roleplay_path)
    
    print(f"Baseline data: {len(baseline_df)} rows")
    print(f"Roleplay data: {len(roleplay_df)} rows")
    
    # Generate main figures
    print("\n=== Generating Main Figures ===")
    create_baseline_heatmap(baseline_df, main_output)
    create_delta_heatmap(baseline_df, roleplay_df, main_output)
    create_consistency_summary(baseline_df, roleplay_df, main_output)
    
    # Generate SI figures
    print("\n=== Generating SI Figures ===")
    create_consistency_distribution(baseline_df, roleplay_df, si_output)
    create_response_distribution(baseline_df, roleplay_df, si_output)
    create_country_shift_summary(baseline_df, roleplay_df, si_output)
    
    print("\n=== Done! ===")
    print(f"Main figures saved to: {main_output}")
    print(f"SI figures saved to: {si_output}")


if __name__ == '__main__':
    main()
