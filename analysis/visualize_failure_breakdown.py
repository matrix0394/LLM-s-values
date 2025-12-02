#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Visualize and analyze the failure breakdown results.

This script reads the failure_breakdown_summary.csv and generates:
- Summary statistics tables
- Bar charts showing failure rates by model
- Stacked bar charts showing failure type distribution
- Stage-specific breakdowns
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 6)


def load_failure_data():
    """Load the failure breakdown summary CSV."""
    csv_path = PROJECT_ROOT / "results" / "analysis" / "failure_breakdown_summary.csv"
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        print("Please run compute_failure_breakdown.py first.")
        return None
    
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"✅ Loaded {len(df)} records from {csv_path.name}")
    return df


def print_overall_summary(df):
    """Print overall summary statistics."""
    print("\n" + "="*80)
    print("📊 OVERALL SUMMARY")
    print("="*80)
    
    # Group by stage and failure_type
    stage_summary = df.groupby(['stage', 'failure_type']).agg({
        'count': 'sum',
        'total': 'first'  # Total should be same within each stage-model group
    }).reset_index()
    
    # Calculate total questions per stage
    stage_totals = df.groupby('stage')['count'].sum().to_dict()
    
    for stage in sorted(df['stage'].unique()):
        stage_data = stage_summary[stage_summary['stage'] == stage]
        total = stage_totals.get(stage, 0)
        
        print(f"\n{stage.upper()}:")
        print(f"  Total responses: {total}")
        
        for _, row in stage_data.iterrows():
            ft = row['failure_type']
            count = row['count']
            rate = count / total * 100 if total > 0 else 0
            
            emoji = {
                'none': '✅',
                'api_failure': '🔴',
                'refusal': '🚫',
                'format_error': '⚠️'
            }.get(ft, '•')
            
            print(f"    {emoji} {ft:15s}: {count:6d} ({rate:5.1f}%)")


def print_model_summary(df):
    """Print per-model summary."""
    print("\n" + "="*80)
    print("🤖 PER-MODEL SUMMARY")
    print("="*80)
    
    # Group by model and failure_type
    model_summary = df.groupby(['model_name', 'failure_type']).agg({
        'count': 'sum'
    }).reset_index()
    
    # Pivot to get failure types as columns
    pivot = model_summary.pivot(index='model_name', columns='failure_type', values='count').fillna(0)
    
    # Calculate totals and rates
    pivot['total'] = pivot.sum(axis=1)
    
    for ft in ['api_failure', 'refusal', 'format_error']:
        if ft in pivot.columns:
            pivot[f'{ft}_rate'] = (pivot[ft] / pivot['total'] * 100).round(2)
    
    # Sort by total responses
    pivot = pivot.sort_values('total', ascending=False)
    
    print("\nFailure counts and rates:")
    print(pivot.to_string())
    
    return pivot


def plot_failure_distribution_by_model(df, output_dir):
    """Create stacked bar chart of failure types by model."""
    print("\n📊 Generating failure distribution chart...")
    
    # Aggregate by model and failure type
    model_summary = df.groupby(['model_name', 'failure_type'])['count'].sum().reset_index()
    
    # Pivot for plotting
    pivot = model_summary.pivot(index='model_name', columns='failure_type', values='count').fillna(0)
    
    # Calculate percentages
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Define colors
    colors = {
        'none': '#2ecc71',          # Green for valid
        'format_error': '#f39c12',  # Orange for format error
        'refusal': '#e74c3c',       # Red for refusal
        'api_failure': '#95a5a6'    # Gray for API failure
    }
    
    # Sort columns in desired order
    col_order = ['none', 'format_error', 'refusal', 'api_failure']
    col_order = [c for c in col_order if c in pivot.columns]
    
    # Plot 1: Absolute counts
    pivot[col_order].plot(kind='bar', stacked=True, ax=ax1, 
                          color=[colors.get(c, '#95a5a6') for c in col_order])
    ax1.set_title('Failure Type Distribution by Model (Counts)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Model', fontsize=12)
    ax1.set_ylabel('Number of Responses', fontsize=12)
    ax1.legend(title='Failure Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.tick_params(axis='x', rotation=45)
    
    # Plot 2: Percentages
    pivot_pct[col_order].plot(kind='bar', stacked=True, ax=ax2,
                              color=[colors.get(c, '#95a5a6') for c in col_order])
    ax2.set_title('Failure Type Distribution by Model (Percentage)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Model', fontsize=12)
    ax2.set_ylabel('Percentage (%)', fontsize=12)
    ax2.legend(title='Failure Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.tick_params(axis='x', rotation=45)
    ax2.set_ylim(0, 100)
    
    plt.tight_layout()
    
    output_path = output_dir / "failure_distribution_by_model.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def plot_failure_rates_comparison(df, output_dir):
    """Create grouped bar chart comparing failure rates across models."""
    print("\n📊 Generating failure rates comparison chart...")
    
    # Calculate rates by model
    model_summary = df.groupby(['model_name', 'failure_type'])['count'].sum().reset_index()
    pivot = model_summary.pivot(index='model_name', columns='failure_type', values='count').fillna(0)
    
    # Calculate total and rates
    pivot['total'] = pivot.sum(axis=1)
    rate_cols = []
    for ft in ['api_failure', 'refusal', 'format_error']:
        if ft in pivot.columns:
            col_name = f'{ft}_rate'
            pivot[col_name] = (pivot[ft] / pivot['total'] * 100)
            rate_cols.append(col_name)
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    pivot[rate_cols].plot(kind='bar', ax=ax, width=0.8)
    
    ax.set_title('Failure Rates by Model (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Failure Rate (%)', fontsize=12)
    ax.legend(['API Failure', 'Refusal', 'Format Error'], title='Failure Type')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    output_path = output_dir / "failure_rates_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def export_summary_tables(df, output_dir):
    """Export summary tables for paper."""
    print("\n📄 Exporting summary tables...")
    
    # Table 1: Overall by stage
    stage_summary = df.groupby(['stage', 'failure_type'])['count'].sum().reset_index()
    stage_totals = df.groupby('stage')['count'].sum()
    stage_summary = stage_summary.merge(
        stage_totals.rename('total'), 
        left_on='stage', 
        right_index=True
    )
    stage_summary['rate'] = (stage_summary['count'] / stage_summary['total'] * 100).round(2)
    
    output_path = output_dir / "summary_by_stage.csv"
    stage_summary.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Saved: {output_path}")
    
    # Table 2: By model
    model_summary = df.groupby(['model_name', 'failure_type'])['count'].sum().reset_index()
    pivot = model_summary.pivot(index='model_name', columns='failure_type', values='count').fillna(0)
    pivot['total'] = pivot.sum(axis=1)
    
    # Add rate columns
    for ft in ['none', 'api_failure', 'refusal', 'format_error']:
        if ft in pivot.columns:
            pivot[f'{ft}_rate'] = (pivot[ft] / pivot['total'] * 100).round(2)
    
    output_path = output_dir / "summary_by_model.csv"
    pivot.to_csv(output_path, encoding='utf-8-sig')
    print(f"✅ Saved: {output_path}")
    
    # Table 3: By stage and model (detailed)
    detailed = df.groupby(['stage', 'model_name', 'failure_type'])['count'].sum().reset_index()
    output_path = output_dir / "summary_detailed.csv"
    detailed.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Saved: {output_path}")


def main():
    """Main analysis workflow."""
    print("="*80)
    print("🔍 FAILURE BREAKDOWN ANALYSIS & VISUALIZATION")
    print("="*80)
    
    # Load data
    df = load_failure_data()
    if df is None:
        return
    
    # Print summaries
    print_overall_summary(df)
    model_summary = print_model_summary(df)
    
    # Create output directory
    output_dir = PROJECT_ROOT / "results" / "analysis" / "failure_breakdown_figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    plot_failure_distribution_by_model(df, output_dir)
    plot_failure_rates_comparison(df, output_dir)
    
    # Export tables
    export_summary_tables(df, output_dir)
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nOutput directory: {output_dir}")
    print("\nGenerated files:")
    print("  📊 failure_distribution_by_model.png")
    print("  📊 failure_rates_comparison.png")
    print("  📄 summary_by_stage.csv")
    print("  📄 summary_by_model.csv")
    print("  📄 summary_detailed.csv")


if __name__ == "__main__":
    main()
