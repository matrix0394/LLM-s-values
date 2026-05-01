#!/usr/bin/env python3
"""
图2数据：6种语言baseline数据（20模型）
只生成数据，不画图
"""

import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path('/Users/yxy/code/LLM\'s values/LLM\'s values')

# 排除的模型
EXCLUDED_MODELS = ['qwen3-1.7b', 'z-ai/glm-4.6', 'qwen/qwq-32b']

# 语言名称映射
LANGUAGE_NAMES = {
    'ar': 'Arabic',
    'zh-cn': 'Chinese',
    'en': 'English',
    'fr': 'French',
    'ru': 'Russian',
    'es': 'Spanish'
}


def main():
    print("="*60)
    print("图2数据：6种语言baseline - 20模型")
    print("="*60)
    
    # 加载数据
    df = pd.read_csv(PROJECT_ROOT / 'SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv')
    df = df[~df['model_name'].isin(EXCLUDED_MODELS)]
    
    print(f"模型数: {df['model_name'].nunique()}")
    print(f"语言: {df['language'].unique()}")
    print(f"总记录: {len(df)}")
    
    # 按语言统计
    lang_stats = df.groupby('language').agg({
        'PC1': ['mean', 'std'],
        'PC2': ['mean', 'std']
    }).round(3)
    lang_stats.columns = ['PC1_mean', 'PC1_std', 'PC2_mean', 'PC2_std']
    lang_stats = lang_stats.reset_index()
    lang_stats['language_name'] = lang_stats['language'].map(LANGUAGE_NAMES)
    
    print("\n按语言统计:")
    print(lang_stats.to_string(index=False))
    
    # 保存
    output_dir = PROJECT_ROOT / 'results/figures'
    output_dir.mkdir(parents=True, exist_ok=True)
    lang_stats.to_csv(output_dir / 'figure2_language_data.csv', index=False)
    
    # 模型列表
    models = sorted(df['model_name'].unique())
    print(f"\n20个模型列表:")
    for i, m in enumerate(models, 1):
        print(f"  {i:2d}. {m}")
    
    print(f"\n已保存到: {output_dir}/figure2_language_data.csv")


if __name__ == '__main__':
    main()
