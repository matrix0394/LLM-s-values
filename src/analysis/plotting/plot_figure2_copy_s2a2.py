#!/usr/bin/env python3
"""
完全照搬 generate_figs2_baseline.py 的逻辑
图2: 6种语言intrinsic values - S2A2风格 (20模型)
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import math
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np

# ===== 路径配置 =====
PROJECT_ROOT = Path("/Users/yxy/code/LLM's values/LLM's values")
OUTPUT_DIR = PROJECT_ROOT / 'results' / 'figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===== 颜色定义 (完全照搬si_config.py) =====
REGION_COLORS = {
    'Confucian': '#4477AA', 'Protestant Europe': '#EE6677', 'Latin America': '#228833',
    'Catholic Europe': '#CCBB44', 'English-Spepeaking': '#66CCEE', 'African-Islamic': '#AA3377',
    'Baltic': '#BBBBBB', 'West & South Asia': '#EE99AA', 'Orthodox Europe': '#009988', 'Other': '#DDDDDD'
}

LANGUAGE_COLORS = {
    'ar': '#FF7F00', 'en': '#E41A1C', 'es': '#4DAF4A', 'fr': '#984EA3', 'ru': '#A65628', 'zh-cn': '#377EB8'
}

LANGUAGE_NAMES = {
    'ar': 'Arabic', 'en': 'English', 'es': 'Spanish', 'fr': 'French', 'ru': 'Russian', 'zh-cn': 'Chinese'
}

MODEL_COLORS = {
    'gpt-4o': '#1E3A8A', 'gpt-4o-mini': '#3B82F6',
    'claude-3-7-sonnet-20250219': '#7C3AED', 'claude-sonnet-4.5': '#A78BFA',
    'gemini-2.5-flash': '#047857', 'gemini-2.5-pro': '#10B981', 'gemma-3-4b-it': '#6EE7B7',
    'llama-3.2-3b-instruct': '#DC2626', 'llama-3.3-70b-instruct': '#F87171',
    'mistral-medium-3.1': '#EA580C', 'mistral-nemo': '#FB923C',
    'deepseek-chat': '#0891B2',
    'qwen3-max': '#FACC15', 'qwq-32b': '#FDE047',
    'grok-4.1-fast': '#6B7280',
    'doubao-1-5-pro-32k-250115': '#DB2777',
    'yi-1.5-34b-chat': '#0D9488',
    'abab6.5s-chat': '#8B5CF6',
    'GLM-4': '#EC4899',
    'Command R+': '#14B8A6'
}

POINT_SIZE_MEDIUM = 60
POINT_SIZE_BG = 20
ALPHA_BG = 0.15


# ===== 工具函数 (完全照搬) =====
def load_ivs_data():
    """Load IVS PCA coordinates"""
    ivs_path = PROJECT_ROOT / 'SI/pca/Table_S5_IVS_PCA_coordinates.csv'
    return pd.read_csv(ivs_path)

def load_baseline_data():
    """Load LLM baseline PCA coordinates"""
    baseline_path = PROJECT_ROOT / 'SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv'
    df = pd.read_csv(baseline_path)
    # 排除3个模型
    EXCLUDED = ['qwen3-1.7b', 'z-ai/glm-4.6', 'qwen/qwq-32b']
    df = df[~df['model_name'].isin(EXCLUDED)]
    # 只保留6种语言
    languages = ['ar', 'en', 'es', 'fr', 'ru', 'zh-cn']
    df = df[df['language'].isin(languages)]
    return df

def get_global_axis_limits(*dataframes, padding=0.5):
    pc1_min = min(df['PC1'].min() for df in dataframes)
    pc1_max = max(df['PC1'].max() for df in dataframes)
    pc2_min = min(df['PC2'].min() for df in dataframes)
    pc2_max = max(df['PC2'].max() for df in dataframes)
    return (pc1_min - padding, pc1_max + padding), (pc2_min - padding, pc2_max + padding)

def plot_ivs_background(ax, ivs_data, alpha=ALPHA_BG):
    for region in ivs_data['cultural_region'].dropna().unique():
        subset = ivs_data[ivs_data['cultural_region'] == region]
        color = REGION_COLORS.get(region, '#DDDDDD')
        ax.scatter(subset['PC1'], subset['PC2'], c=color, s=POINT_SIZE_BG, marker='o', alpha=alpha, edgecolors='none', zorder=1)

def get_model_color(model):
    if model in MODEL_COLORS:
        return MODEL_COLORS[model]
    short_name = model.split('/')[-1] if '/' in model else model
    return MODEL_COLORS.get(short_name, '#888888')

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

def create_model_legend(models):
    handles = []
    for model in sorted(set(models)):
        color = get_model_color(model)
        short_name = model.split('/')[-1] if '/' in model else model
        handles.append(Line2D([0], [0], marker='o', color='w',
                             markerfacecolor=color, markersize=8,
                             markeredgecolor='black', markeredgewidth=0.6,
                             label=short_name))
    return handles


# ===== 主函数 =====
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
    
    fig.text(0.5, 0.02, 'PC1 (Survival → Self-Expression)', ha='center', fontsize=11)
    fig.text(0.02, 0.5, 'PC2 (Traditional → Secular-Rational)', va='center',
             rotation='vertical', fontsize=11)
    
    fig.suptitle('S2-A2: LLM Baseline Values by Language (Model Distribution)',
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout(rect=[0.03, 0.05, 0.88, 0.98])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存PNG和PDF
    fig.savefig(output_dir / 'FigS2A2_all_languages_grid.png', dpi=300, bbox_inches='tight')
    fig.savefig(output_dir / 'FigS2A2_all_languages_grid.pdf', bbox_inches='tight')
    plt.close()
    print(f"✅ Generated: FigS2A2_all_languages_grid ({n_langs} languages)")


def main():
    print("=" * 60)
    print("Generating FigS2-A2 (照搬原脚本逻辑)")
    print("=" * 60)
    
    ivs_data = load_ivs_data()
    baseline_data = load_baseline_data()
    
    print(f"IVS: {len(ivs_data)} countries")
    print(f"Baseline: {len(baseline_data)} records, {baseline_data['model_name'].nunique()} models")
    print(f"Languages: {baseline_data['language'].unique().tolist()}")
    
    xlim, ylim = get_global_axis_limits(ivs_data, baseline_data)
    
    print("\nGenerating S2-A2 grid...")
    generate_s2a2_grid(baseline_data, ivs_data, xlim, ylim, OUTPUT_DIR)
    
    print("\n" + "=" * 60)
    print(f"Done! Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
