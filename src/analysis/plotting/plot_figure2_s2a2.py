#!/usr/bin/env python3
"""
图2: 6种语言intrinsic values (类似FigS2A2网格图) - 20模型版本
"""

import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path

PROJECT_ROOT = Path("/Users/yxy/code/LLM's values/LLM's values")
OUTPUT_DIR = PROJECT_ROOT / 'results' / 'figures'

# 颜色定义 (来自si_config.py)
LANGUAGE_COLORS = {
    'ar': '#FF7F00',   # Orange - Arabic
    'en': '#E41A1C',   # Red - English
    'es': '#4DAF4A',   # Green - Spanish
    'fr': '#984EA3',   # Purple - French
    'ru': '#A65628',   # Brown - Russian
    'zh-cn': '#377EB8', # Blue - Chinese
}

LANGUAGE_NAMES = {
    'ar': 'Arabic', 'en': 'English', 'es': 'Spanish', 
    'fr': 'French', 'ru': 'Russian', 'zh-cn': 'Chinese'
}

# 模型颜色 (20个模型)
MODEL_COLORS = {
    'gpt-4o': '#1E3A8A', 'gpt-4o-mini': '#3B82F6',
    'claude-3-7-sonnet-20250219': '#7C3AED', 'claude-sonnet-4.5': '#A78BFA',
    'gemini-2.5-flash': '#047857', 'gemini-2.5-pro': '#10B981',
    'gemma-3-4b-it': '#6EE7B7',
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

def get_model_color(model):
    if model in MODEL_COLORS:
        return MODEL_COLORS[model]
    short_name = model.split('/')[-1] if '/' in model else model
    return MODEL_COLORS.get(short_name, '#888888')

def plot_figure2_s2a2():
    """生成FigS2A2风格的图"""
    print("绘制图2 (S2A2风格)...")
    
    # 加载baseline数据 (Table_S6)
    baseline_df = pd.read_csv(PROJECT_ROOT / 'SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv')
    
    # 排除3个模型 (保留20个)
    EXCLUDED = ['qwen3-1.7b', 'z-ai/glm-4.6', 'qwen/qwq-32b']
    baseline_df = baseline_df[~baseline_df['model_name'].isin(EXCLUDED)]
    
    # 只保留6种语言
    languages = ['ar', 'en', 'es', 'fr', 'ru', 'zh-cn']
    baseline_df = baseline_df[baseline_df['language'].isin(languages)]
    
    # 加载IVS背景数据
    ivs_df = pd.read_csv(PROJECT_ROOT / 'SI/pca/Table_S5_IVS_PCA_coordinates.csv')
    
    # 设置坐标范围
    xlim = (baseline_df['PC1'].min() - 0.5, baseline_df['PC1'].max() + 0.5)
    ylim = (baseline_df['PC2'].min() - 0.5, baseline_df['PC2'].max() + 0.5)
    
    # 绘制网格图: 3列 x 2行
    n_cols = 3
    n_rows = 2
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 4, n_rows * 3.5))
    axes = axes.flatten()
    
    for i, lang in enumerate(languages):
        ax = axes[i]
        
        # 绘制IVS背景点 (灰色)
        for region in ivs_df['cultural_region'].dropna().unique():
            subset = ivs_df[ivs_df['cultural_region'] == region]
            ax.scatter(subset['PC1'], subset['PC2'], c='lightgray', s=20, alpha=0.3, zorder=0)
        
        # 绘制该语言的所有模型数据点
        lang_data = baseline_df[baseline_df['language'] == lang]
        
        for model in sorted(lang_data['model_name'].unique()):
            model_subset = lang_data[lang_data['model_name'] == model]
            color = get_model_color(model)
            ax.scatter(model_subset['PC1'], model_subset['PC2'],
                      c=color, s=60, marker='o', alpha=0.9,
                      edgecolors='black', linewidths=0.8, zorder=3)
        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
        ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
        ax.tick_params(labelsize=7)
        ax.set_title(LANGUAGE_NAMES.get(lang, lang), fontsize=10, pad=3)
        
        # 设置坐标轴标签
        if i % n_cols == 0:
            ax.set_ylabel('PC2', fontsize=10)
        if i >= (n_rows - 1) * n_cols:
            ax.set_xlabel('PC1', fontsize=10)
    
    # 隐藏多余的subplot
    for i in range(len(languages), len(axes)):
        axes[i].set_visible(False)
    
    # 添加模型图例 (右边)
    legend_handles = []
    for model in sorted(baseline_df['model_name'].unique()):
        color = get_model_color(model)
        short_name = model.split('/')[-1] if '/' in model else model
        legend_handles.append(Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor=color, markersize=8,
                                     markeredgecolor='black', markeredgewidth=0.6,
                                     label=short_name))
    
    fig.legend(handles=legend_handles, loc='center right', 
               fontsize=6, framealpha=0.95, title='Model',
               bbox_to_anchor=(1.12, 0.5))
    
    # 添加共享标签
    fig.text(0.5, 0.02, 'PC1 (Survival → Self-Expression)', ha='center', fontsize=11)
    fig.text(0.02, 0.5, 'PC2 (Traditional → Secular-Rational)', va='center',
             rotation='vertical', fontsize=11)
    
    fig.suptitle('S2-A2: LLM Baseline Values by Language (20 Models)', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout(rect=[0.03, 0.05, 0.88, 0.98])
    plt.savefig(OUTPUT_DIR / 'figure2_language_values_grid.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✅ 图2已保存: {OUTPUT_DIR / 'figure2_language_values_grid.png'}")


if __name__ == '__main__':
    print("="*60)
    print("生成图2 (FigS2A2风格)")
    print("="*60)
    plot_figure2_s2a2()
    print("\n✅ 完成!")
