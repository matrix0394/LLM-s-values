#!/usr/bin/env python3
"""
图2脚本：6种语言大模型自身价值观（20模型）
生成bar chart展示PC1和PC2的均值差异

只生成数据，不画图
"""

import pandas as pd
import numpy as np
from scipy import stats
import json

PROJECT_ROOT = '/Users/yxy/code/LLM\'s values/LLM\'s values'

# 排除的模型（保持与Study 2/3一致）
EXCLUDED_MODELS = ['qwen3-1.7b', 'z-ai/glm-4.6', 'qwen/qwq-32b']

# 语言名称
LANGUAGE_NAMES = {
    'ar': 'Arabic',
    'zh-cn': 'Chinese',
    'en': 'English',
    'fr': 'French',
    'ru': 'Russian',
    'es': 'Spanish'
}

LANGUAGE_ORDER = ['en', 'fr', 'es', 'zh-cn', 'ru', 'ar']


def load_baseline_data():
    """加载baseline PCA数据"""
    df = pd.read_csv(f'{PROJECT_ROOT}/SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv')
    df = df[~df['model_name'].isin(EXCLUDED_MODELS)]
    return df


def main():
    """生成图2所需数据"""
    df = load_baseline_data()
    
    print("="*60)
    print("图2数据：6种语言大模型自身价值观（20模型）")
    print("="*60)
    
    # 按语言计算统计量
    lang_stats = df.groupby('language').agg({
        'PC1': ['mean', 'std', 'count'],
        'PC2': ['mean', 'std', 'count']
    }).round(3)
    
    lang_stats.columns = ['PC1_mean', 'PC1_std', 'PC1_n', 'PC2_mean', 'PC2_std', 'PC2_n']
    lang_stats = lang_stats.reindex(LANGUAGE_ORDER)
    
    # ANOVA检验
    pc1_groups = [df[df['language']==lang]['PC1'].values for lang in LANGUAGE_ORDER]
    pc1_f, pc1_p = stats.f_oneway(*pc1_groups)
    
    pc2_groups = [df[df['language']==lang]['PC2'].values for lang in LANGUAGE_ORDER]
    pc2_f, pc2_p = stats.f_oneway(*pc2_groups)
    
    # 打印数据
    print(f"\n模型数: {df['model_name'].nunique()}")
    print(f"语言: {LANGUAGE_ORDER}")
    
    print("\n=== PC1 (Traditional vs Secular-Rational) ===")
    print(f"ANOVA: F = {pc1_f:.3f}, p = {pc1_p:.4f}")
    for lang in LANGUAGE_ORDER:
        row = lang_stats.loc[lang]
        print(f"  {LANGUAGE_NAMES[lang]:10s}: mean = {row['PC1_mean']:.2f}, std = {row['PC1_std']:.2f}")
    
    print("\n=== PC2 (Survival vs Self-Expression) ===")
    print(f"ANOVA: F = {pc2_f:.3f}, p = {pc2_p:.4f}")
    for lang in LANGUAGE_ORDER:
        row = lang_stats.loc[lang]
        print(f"  {LANGUAGE_NAMES[lang]:10s}: mean = {row['PC2_mean']:.2f}, std = {row['PC2_std']:.2f}")
    
    # 保存为CSV
    lang_stats_export = lang_stats.reset_index()
    lang_stats_export['language_name'] = lang_stats_export['language'].map(LANGUAGE_NAMES)
    lang_stats_export = lang_stats_export[['language', 'language_name', 'PC1_mean', 'PC1_std', 'PC2_mean', 'PC2_std']]
    lang_stats_export.to_csv(f'{PROJECT_ROOT}/results/figures/figure2_language_data.csv', index=False)
    print(f"\n已保存到: results/figures/figure2_language_data.csv")
    
    # 保存ANOVA结果
    anova_results = {
        'pc1': {'f_statistic': round(pc1_f, 3), 'p_value': round(pc1_p, 4)},
        'pc2': {'f_statistic': round(pc2_f, 3), 'p_value': round(pc2_p, 4)},
        'models_count': df['model_name'].nunique()
    }
    with open(f'{PROJECT_ROOT}/results/figures/figure2_anova_results.json', 'w') as f:
        json.dump(anova_results, f, indent=2)
    print(f"已保存到: results/figures/figure2_anova_results.json")


if __name__ == '__main__':
    main()
