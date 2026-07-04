#!/usr/bin/env python3
"""
Generate FigS2 (Updated): Baseline Intrinsic Values figures - 20 Models

S2-A1: Per model, showing language stability (color = language)
S2-A2: Per language, showing model distribution (color = model)

修改：排除 qwen3-1.7b, glm-4.6, qwq-32b 三个模型，使用20个模型
运行：python analysis/generate_figure2_baseline_20models.py
"""

import sys
from pathlib import Path

# 添加路径
script_dir = Path(__file__).parent
PROJECT_ROOT = script_dir.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 设置非交互式后端
import matplotlib
matplotlib.use('Agg')

import math
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


import pandas as pd

from analysis.si.si_config import (
    PROJECT_ROOT,
    load_ivs_data, get_global_axis_limits,
    plot_ivs_background, get_model_color,
    REGION_COLORS, LANGUAGE_COLORS, LANGUAGE_NAMES, MODEL_COLORS,
    POINT_SIZE_MEDIUM, POINT_SIZE_BG, ALPHA_BG, PCA_DIR
)

# 排除的模型（20个模型）
EXCLUDED_MODELS = ['qwen3-1.7b', 'z-ai/glm-4.6', 'qwen/qwq-32b']


def load_baseline_data_20models():
    """加载baseline数据（20模型）"""
    baseline_path = PCA_DIR / 'Table_S6_LLM_baseline_PCA_coordinates.csv'
    df = pd.read_csv(baseline_path)
    # 排除3个模型
    df = df[~df['model_name'].isin(EXCLUDED_MODELS)]
    print(f"Baseline data: {len(df)} records, {df['model_name'].nunique()} models")
    return df


def plot_s2a1_panel(ax, model, baseline_data, ivs_data, xlim, ylim, show_title=True):
    """Plot S2-A1 panel: One model, multiple languages. Color = Language"""
    plot_ivs_background(ax, ivs_data, alpha=ALPHA_BG)
    
    model_data = baseline_data[baseline_data['model_name'] == model]
    
    for lang in model_data['language'].unique():
        lang_data = model_data[model_data['language'] == lang]
        color = LANGUAGE_COLORS.get(lang, '#888888')
        ax.scatter(lang_data['PC1'], lang_data['PC2'],
                   c=color, s=POINT_SIZE_MEDIUM, marker='o', alpha=0.9,
                   edgecolors='black', linewidths=0.8, zorder=3)
    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.tick_params(labelsize=7)
    
    if show_title:
        short_name = model.split('/')[-1] if '/' in model else model
        ax.set_title(short_name, fontsize=8, pad=3)


def plot_s2a2_panel(ax, language, baseline_data, ivs_data, xlim, ylim, show_title=True):
    """Plot S2-A2 panel: One language, multiple models. Color = Model"""
    plot_ivs_background(ax, ivs_data, alpha=ALPHA_BG)
    
    lang_data = baseline_data[baseline_data['language'] == language]
    
    for model in lang_data['model_name'].unique():
        model_subset = lang_data[lang_data['model_name'] == model]
        color = get_model_color(model)
        ax.scatter(model_subset['PC1'], model_subset['PC2'],
                   c=color, s=POINT_SIZE_MEDIUM, marker='o', alpha=0.9,
                   edgecolors='black', linewidths=0.8, zorder=3)
    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.tick_params(labelsize=7)
    
    if show_title:
        lang_name = LANGUAGE_NAMES.get(language, language)
        ax.set_title(lang_name, fontsize=9, pad=3)


def create_language_legend():
    """Create legend handles for languages."""
    handles = []
    for lang, color in LANGUAGE_COLORS.items():
        name = LANGUAGE_NAMES.get(lang, lang)
        handles.append(Line2D([0], [0], marker='o', color='w', 
                             markerfacecolor=color, markersize=10,
                             markeredgecolor='black', markeredgewidth=0.8,
                             label=name))
    return handles


def create_model_legend(models):
    """Create legend handles for models."""
    handles = []
    for model in sorted(models):
        color = get_model_color(model)
        short_name = model.split('/')[-1] if '/' in model else model
        handles.append(Line2D([0], [0], marker='o', color='w',
                             markerfacecolor=color, markersize=8,
                             markeredgecolor='black', markeredgewidth=0.6,
                             label=short_name))
    return handles


def generate_s2a1_grid(baseline_data, ivs_data, xlim, ylim, output_dir):
    """Generate S2-A1 grid: All models, color by language."""
    models = sorted(baseline_data['model_name'].unique())
    n_models = len(models)
    n_cols = 5
    n_rows = math.ceil(n_models / n_cols)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 2.5))
    axes = axes.flatten()
    
    for i, model in enumerate(models):
        plot_s2a1_panel(axes[i], model, baseline_data, ivs_data, xlim, ylim)
    
    for i in range(n_models, len(axes)):
        axes[i].set_visible(False)
    
    legend_handles = create_language_legend()
    fig.legend(handles=legend_handles, loc='lower center', ncol=6,
               fontsize=9, framealpha=0.95, title='Language',
               bbox_to_anchor=(0.5, -0.02))
    
    fig.text(0.5, 0.02, 'PC1 (Traditional → Secular-Rational)', ha='center', fontsize=11)
    fig.text(0.02, 0.5, 'PC2 (Survival → Self-Expression)', va='center', 
             rotation='vertical', fontsize=11)
    
    fig.suptitle('S2-A1: LLM Baseline Values by Model (Language Stability) - 20 Models', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout(rect=[0.03, 0.08, 1, 0.98])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存PNG和PDF
    fig.savefig(output_dir / 'FigS2A1_all_models_grid_20models.png', dpi=150, bbox_inches='tight')
    fig.savefig(output_dir / 'FigS2A1_all_models_grid_20models.pdf', bbox_inches='tight')
    plt.close(fig)
    
    print(f"✅ Generated: FigS2A1_all_models_grid_20models ({n_models} models)")


def generate_s2a2_grid(baseline_data, ivs_data, xlim, ylim, output_dir):
    """Generate S2-A2 grid: All languages, color by model."""
    languages = sorted(baseline_data['language'].unique())
    n_langs = len(languages)
    n_cols = 3
    n_rows = 2
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 4, n_rows * 3.5))
    axes = axes.flatten()
    
    for i, lang in enumerate(languages):
        plot_s2a2_panel(axes[i], lang, baseline_data, ivs_data, xlim, ylim)
    
    for i in range(n_langs, len(axes)):
        axes[i].set_visible(False)
    
    models = baseline_data['model_name'].unique()
    legend_handles = create_model_legend(models)
    fig.legend(handles=legend_handles, loc='center right', 
               fontsize=7, framealpha=0.95, title='Model',
               bbox_to_anchor=(1.15, 0.5))
    
    fig.text(0.5, 0.02, 'PC1 (Traditional → Secular-Rational)', ha='center', fontsize=11)
    fig.text(0.02, 0.5, 'PC2 (Survival → Self-Expression)', va='center',
             rotation='vertical', fontsize=11)
    
    fig.suptitle('S2-A2: LLM Baseline Values by Language (Model Distribution) - 20 Models',
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout(rect=[0.03, 0.05, 0.88, 0.98])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig.savefig(output_dir / 'FigS2A2_all_languages_grid_20models.png', dpi=150, bbox_inches='tight')
    fig.savefig(output_dir / 'FigS2A2_all_languages_grid_20models.pdf', bbox_inches='tight')
    plt.close(fig)
    
    print(f"✅ Generated: FigS2A2_all_languages_grid_20models ({n_langs} languages)")


def main():
    print("=" * 60)
    print("Generating FigS2 (Updated): Baseline Intrinsic Values - 20 Models")
    print("=" * 60)
    
    ivs_data = load_ivs_data()
    baseline_data = load_baseline_data_20models()
    
    print(f"IVS: {len(ivs_data)} countries")
    print(f"Baseline: {len(baseline_data)} records, {baseline_data['model_name'].nunique()} models")
    
    xlim, ylim = get_global_axis_limits(ivs_data, baseline_data)
    
    # 输出到results/figures
    output_dir = PROJECT_ROOT / 'results/figures' / 'S2_Baseline_intrinsic_values_20models'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\nGenerating S2-A1 (per model, color by language)...")
    generate_s2a1_grid(baseline_data, ivs_data, xlim, ylim, output_dir / 'A1_per_model')
    
    print("\nGenerating S2-A2 (per language, color by model)...")
    generate_s2a2_grid(baseline_data, ivs_data, xlim, ylim, output_dir / 'A2_per_language')
    
    print("\n" + "=" * 60)
    print(f"Done! Output: {output_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
