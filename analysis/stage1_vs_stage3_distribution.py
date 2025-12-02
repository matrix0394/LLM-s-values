#!/usr/bin/env python3
"""
Stage1 vs Stage3 坐标分布分析
分析大模型原生坐标（Stage1）和模仿国家/地区坐标（Stage3）的分布是否集中
验证：模型的角色扮演是否偏离其原生文化倾向
"""

import pickle
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.spatial.distance import euclidean

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_stage1_coordinates():
    """加载Stage1 LLM原生坐标"""
    # 尝试JSON格式
    json_file = Path('data/llm_values/llm_pca_entity_scores.json')
    if json_file.exists():
        with open(json_file) as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        # 尝试PKL格式
        pkl_file = Path('data/llm_values/llm_pca_entity_scores.pkl')
        with open(pkl_file, 'rb') as f:
            df = pickle.load(f)
    
    # 只保留 LLM 数据，过滤掉 IVS 真实国家数据
    if 'data_source' in df.columns:
        df = df[df['data_source'] != 'IVS'].copy()
    
    # 或者使用 is_llm 标记
    if 'is_llm' in df.columns:
        df = df[df['is_llm'] == True].copy()
    
    print(f"✅ 加载Stage1数据: {len(df)} 个LLM模型")
    return df

def load_stage3_coordinates():
    """加载Stage3多语言角色扮演坐标"""
    with open('data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl', 'rb') as f:
        df = pickle.load(f)
    print(f"✅ 加载Stage3数据: {len(df)} 行")
    return df

def analyze_distribution():
    """分析坐标分布集中度"""
    print("=" * 80)
    print("Stage1 vs Stage3 坐标分布集中度分析")
    print("=" * 80)
    
    # 加载数据
    print("\n1. 加载数据...")
    stage1_df = load_stage1_coordinates()
    stage3_df = load_stage3_coordinates()
    
    # 提取模型名称（保留完整名称）
    def extract_model_name(name):
        # 处理 None 值
        if name is None or pd.isna(name):
            return 'Unknown'
        return str(name)
    
    # 统一模型名称（保留完整名称）
    if 'model_name' in stage1_df.columns:
        stage1_df['model'] = stage1_df['model_name'].apply(extract_model_name)
    elif 'entity_name' in stage1_df.columns:
        stage1_df['model'] = stage1_df['entity_name'].apply(extract_model_name)
    
    stage3_df['model'] = stage3_df.get('model_name', stage3_df.get('model', '')).apply(extract_model_name)
    
    # 2. 计算每个模型的原生坐标到角色扮演坐标的距离
    print("\n2. 计算原生坐标到角色扮演坐标的距离...")
    
    results = []
    
    for model in stage1_df['model'].unique():
        # Stage1原生坐标
        stage1_model = stage1_df[stage1_df['model'] == model]
        if len(stage1_model) == 0:
            continue
        
        native_pc1 = stage1_model['PC1_rescaled'].iloc[0]
        native_pc2 = stage1_model['PC2_rescaled'].iloc[0]
        
        # Stage3角色扮演
        stage3_model = stage3_df[stage3_df['model'] == model]
        for _, row in stage3_model.iterrows():
            dist = euclidean([native_pc1, native_pc2], 
                           [row['PC1_rescaled'], row['PC2_rescaled']])
            results.append({
                'model': model,
                'stage': 'Stage3',
                'country': row.get('Country', ''),
                'language': row.get('language', ''),
                'native_PC1': native_pc1,
                'native_PC2': native_pc2,
                'roleplay_PC1': row['PC1_rescaled'],
                'roleplay_PC2': row['PC2_rescaled'],
                'distance_to_native': dist
            })
    
    results_df = pd.DataFrame(results)
    
    # 3. 统计分析
    print("\n3. 集中度统计分析...")
    
    # 按模型统计
    model_stats = results_df.groupby('model')['distance_to_native'].agg([
        ('mean', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max'),
        ('count', 'count')
    ]).sort_values('mean')
    
    print("\n   按模型的平均偏离距离（越小越集中）:")
    for model, row in model_stats.iterrows():
        print(f"   {model:15s}: {row['mean']:.4f} ± {row['std']:.4f} "
              f"(范围: {row['min']:.4f}-{row['max']:.4f}, N={int(row['count'])})")
    
    # 按Stage统计
    stage_stats = results_df.groupby('stage')['distance_to_native'].agg(['mean', 'std', 'count'])
    print("\n   按Stage统计:")
    for stage, row in stage_stats.iterrows():
        print(f"   {stage}: {row['mean']:.4f} ± {row['std']:.4f} (N={int(row['count'])})")
    
    # 按语言类型统计（Stage3）
    stage3_results = results_df[results_df['stage'] == 'Stage3']
    stage3_results['is_english'] = stage3_results['language'].isin(['en', 'en-native'])
    lang_stats = stage3_results.groupby('is_english')['distance_to_native'].agg(['mean', 'std', 'count'])
    
    print("\n   Stage3按语言类型统计:")
    if True in lang_stats.index:
        print(f"   英语模仿: {lang_stats.loc[True, 'mean']:.4f} ± {lang_stats.loc[True, 'std']:.4f}")
    if False in lang_stats.index:
        print(f"   母语模仿: {lang_stats.loc[False, 'mean']:.4f} ± {lang_stats.loc[False, 'std']:.4f}")
    
    # 保存结果
    output_dir = Path('results/analysis/stage1_vs_stage3')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_df.to_csv(output_dir / 'distribution_analysis.csv', index=False)
    results_df.to_excel(output_dir / 'distribution_analysis.xlsx', index=False)
    model_stats.to_csv(output_dir / 'model_concentration.csv')
    
    print(f"\n✅ 结果已保存到: {output_dir}")
    
    return results_df, model_stats, stage1_df

def visualize_distribution(results_df, model_stats, stage1_df):
    """可视化坐标分布"""
    print("\n4. 生成可视化图表...")
    
    output_dir = Path('results/analysis/stage1_vs_stage3')
    
    # 1. 每个模型的原生坐标和角色扮演分布
    models = results_df['model'].unique()[:6]  # 只绘制前6个模型
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, model in enumerate(models):
        ax = axes[idx]
        
        # 原生坐标
        native = stage1_df[stage1_df['model'] == model]
        if len(native) > 0:
            ax.scatter(native['PC1_rescaled'], native['PC2_rescaled'], 
                      c='red', s=300, marker='*', label='原生坐标',
                      edgecolors='darkred', linewidths=2, zorder=3)
        
        # 角色扮演坐标
        roleplay = results_df[results_df['model'] == model]
        
        # Stage3
        stage3 = roleplay
        stage3_en = stage3[stage3['language'].isin(['en', 'en-native'])]
        stage3_native = stage3[~stage3['language'].isin(['en', 'en-native'])]
        
        if len(stage3_en) > 0:
            ax.scatter(stage3_en['roleplay_PC1'], stage3_en['roleplay_PC2'], 
                      c='cyan', s=30, alpha=0.5, marker='s', label='Stage3(英语)')
        
        if len(stage3_native) > 0:
            ax.scatter(stage3_native['roleplay_PC1'], stage3_native['roleplay_PC2'], 
                      c='orange', s=30, alpha=0.5, marker='o', label='Stage3(母语)')
        
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.set_title(f'{model}\n平均偏离: {model_stats.loc[model, "mean"]:.3f}')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'distribution_by_model.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: distribution_by_model.png")
    plt.close()
    
    # 2. 偏离距离分布
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 2.1 整体分布
    axes[0, 0].hist(results_df['distance_to_native'], bins=40, edgecolor='black', alpha=0.7)
    axes[0, 0].set_xlabel('偏离距离（到原生坐标）')
    axes[0, 0].set_ylabel('频数')
    axes[0, 0].set_title('角色扮演偏离原生坐标的距离分布')
    axes[0, 0].axvline(results_df['distance_to_native'].mean(), color='red', 
                      linestyle='--', label=f'平均: {results_df["distance_to_native"].mean():.3f}')
    axes[0, 0].legend()
    
    # 2.2 按模型的箱线图
    model_distances = [results_df[results_df['model'] == m]['distance_to_native'].values 
                      for m in model_stats.index]
    axes[0, 1].boxplot(model_distances, labels=model_stats.index)
    axes[0, 1].set_xticklabels(model_stats.index, rotation=45, ha='right')
    axes[0, 1].set_ylabel('偏离距离')
    axes[0, 1].set_title('按模型的偏离距离分布')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # 2.3 Stage3: 英语 vs 母语
    stage3_results = results_df[results_df['stage'] == 'Stage3']
    stage3_results['lang_type'] = stage3_results['language'].apply(
        lambda x: '英语' if x in ['en', 'en-native'] else '母语'
    )
    lang_data = [stage3_results[stage3_results['lang_type'] == t]['distance_to_native'].values 
                for t in ['英语', '母语']]
    axes[1, 0].boxplot(lang_data, labels=['英语', '母语'])
    axes[1, 0].set_ylabel('偏离距离')
    axes[1, 0].set_title('Stage3: 英语 vs 母语偏离距离')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 隐藏未使用的子图
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'deviation_analysis.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: deviation_analysis.png")
    plt.close()
    
    # 3. 集中度热力图（按模型和语言类型）
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 创建模型×语言类型的集中度矩阵
    stage3_results['lang_type'] = stage3_results['language'].apply(
        lambda x: '英语' if x in ['en', 'en-native'] else '母语'
    )
    pivot_data = stage3_results.groupby(['model', 'lang_type'])['distance_to_native'].mean().unstack(fill_value=0)
    
    sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax, 
               cbar_kws={'label': '平均偏离距离'})
    ax.set_xlabel('语言类型')
    ax.set_ylabel('模型')
    ax.set_title('Stage3 模型角色扮演集中度热力图\n(数值越小越集中在原生坐标附近)')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'concentration_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: concentration_heatmap.png")
    plt.close()
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")

if __name__ == '__main__':
    results_df, model_stats, stage1_df = analyze_distribution()
    visualize_distribution(results_df, model_stats, stage1_df)
    
    print("\n" + "=" * 80)
    print("✅ Stage1 vs Stage3 分布分析完成！")
    print("=" * 80)
    print("\n核心发现:")
    print(f"  - 平均偏离距离: {results_df['distance_to_native'].mean():.4f}")
    print(f"  - 最集中的模型: {model_stats.index[0]} ({model_stats.iloc[0]['mean']:.4f})")
    print(f"  - 最分散的模型: {model_stats.index[-1]} ({model_stats.iloc[-1]['mean']:.4f})")
