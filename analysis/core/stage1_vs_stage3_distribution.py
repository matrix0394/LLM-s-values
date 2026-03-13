#!/usr/bin/env python3
"""
Stage1 vs Stage3 坐标分布分析 - 更新版
使用CSV/JSON格式数据，兼容最新numpy版本

分析大模型原生坐标（Stage1）和模仿国家坐标（Stage3）的分布是否集中
验证：模型的角色扮演是否偏离其原生文化倾向
"""

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

# 排除的低质量模型（只排除qwen3-1.7b）
EXCLUDED_MODELS = ['qwen3-1.7b']

def load_stage1_coordinates():
    """加载Stage1 LLM原生坐标"""
    json_file = Path('data/llm_values/llm_pca_entity_scores.json')
    
    if json_file.exists():
        with open(json_file, encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        raise FileNotFoundError("未找到Stage1数据文件")
    
    # 只保留 LLM 数据，过滤掉 IVS 真实国家数据
    if 'is_llm' in df.columns:
        df = df[df['is_llm'] == True].copy()
    elif 'data_source' in df.columns:
        df = df[df['data_source'] != 'IVS'].copy()
    
    # 使用 extracted_model 字段作为模型名称（更准确）
    if 'extracted_model' in df.columns:
        df['model_name'] = df['extracted_model']
    
    # 排除低质量模型
    if 'model_name' in df.columns:
        df = df[~df['model_name'].str.contains('|'.join(EXCLUDED_MODELS), case=False, na=False)]
    
    print(f"✅ 加载Stage1数据: {len(df)} 个LLM模型")
    return df

def load_stage3_coordinates():
    """加载Stage3多语言角色扮演坐标"""
    csv_file = Path('data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.csv')
    
    if csv_file.exists():
        df = pd.read_csv(csv_file)
    else:
        json_file = Path('data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.json')
        with open(json_file, encoding='utf-8') as f:
            df = pd.DataFrame(json.load(f))
    
    # 排除低质量模型
    if 'model_name' in df.columns:
        df = df[~df['model_name'].str.contains('|'.join(EXCLUDED_MODELS), case=False, na=False)]
    
    print(f"✅ 加载Stage3数据: {len(df)} 行")
    return df

def extract_model_name(name):
    """提取模型名称"""
    if name is None or pd.isna(name):
        return 'Unknown'
    return str(name)

def analyze_distribution():
    """分析坐标分布集中度"""
    print("=" * 80)
    print("Stage1 vs Stage3 坐标分布集中度分析（更新版）")
    print("=" * 80)
    
    # 加载数据
    print("\n1. 加载数据...")
    stage1_df = load_stage1_coordinates()
    stage3_df = load_stage3_coordinates()
    
    # 统一模型名称 - 提取基础名称（去掉路径前缀）
    def normalize_model_name(name):
        if name is None or pd.isna(name) or str(name) == 'Unknown':
            return None
        name = str(name)
        # 去掉路径前缀
        base = name.split('/')[-1]
        return base
    
    if 'model_name' in stage1_df.columns:
        stage1_df['model'] = stage1_df['model_name'].apply(normalize_model_name)
    elif 'entity_name' in stage1_df.columns:
        stage1_df['model'] = stage1_df['entity_name'].apply(normalize_model_name)
    
    if 'model_name' in stage3_df.columns:
        stage3_df['model'] = stage3_df['model_name'].apply(normalize_model_name)
    else:
        stage3_df['model'] = stage3_df.get('model', '').apply(normalize_model_name)
    
    # 过滤掉无效模型
    stage1_df = stage1_df[stage1_df['model'].notna()].copy()
    stage3_df = stage3_df[stage3_df['model'].notna()].copy()
    
    # 2. 计算每个模型的原生坐标到角色扮演坐标的距离
    print("\n2. 计算原生坐标到角色扮演坐标的距离...")
    
    results = []
    
    # 获取模型列表
    stage1_models = set(stage1_df['model'].unique())
    stage3_models = set(stage3_df['model'].unique())
    
    # 直接匹配（基础名称已经统一）
    common_models = stage1_models & stage3_models
    
    print(f"   Stage1模型数: {len(stage1_models)}")
    print(f"   Stage3模型数: {len(stage3_models)}")
    print(f"   共同模型数: {len(common_models)}")
    
    # 显示匹配的模型
    if len(common_models) > 0:
        print(f"   匹配的模型: {sorted(common_models)}")
    
    # 显示未匹配的模型
    unmatched_s1 = stage1_models - common_models
    unmatched_s3 = stage3_models - common_models
    
    if unmatched_s1:
        print(f"   Stage1未匹配: {sorted(unmatched_s1)}")
    if unmatched_s3:
        print(f"   Stage3未匹配: {sorted(unmatched_s3)}")
    
    for model in common_models:
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
    
    if len(results_df) == 0:
        print("⚠️ 没有找到匹配的模型数据")
        return None, None, None
    
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
        model_short = model.split('/')[-1][:20]
        print(f"   {model_short:20s}: {row['mean']:.4f} ± {row['std']:.4f} "
              f"(范围: {row['min']:.4f}-{row['max']:.4f}, N={int(row['count'])})")
    
    # 按语言类型统计
    results_df['is_english'] = results_df['language'].isin(['en', 'en-native'])
    lang_stats = results_df.groupby('is_english')['distance_to_native'].agg(['mean', 'std', 'count'])
    
    print("\n   按语言类型统计:")
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
    if results_df is None or len(results_df) == 0:
        print("⚠️ 没有数据可视化")
        return
    
    print("\n4. 生成可视化图表...")
    
    output_dir = Path('results/analysis/stage1_vs_stage3')
    
    # 1. 每个模型的原生坐标和角色扮演分布
    models = list(model_stats.index)[:6]  # 只绘制前6个模型
    
    if len(models) > 0:
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
            
            # 英语模仿
            stage3_en = roleplay[roleplay['is_english']]
            if len(stage3_en) > 0:
                ax.scatter(stage3_en['roleplay_PC1'], stage3_en['roleplay_PC2'], 
                          c='cyan', s=30, alpha=0.5, marker='s', label='英语模仿')
            
            # 母语模仿
            stage3_native = roleplay[~roleplay['is_english']]
            if len(stage3_native) > 0:
                ax.scatter(stage3_native['roleplay_PC1'], stage3_native['roleplay_PC2'], 
                          c='orange', s=30, alpha=0.5, marker='o', label='母语模仿')
            
            model_short = model.split('/')[-1][:20]
            ax.set_xlabel('PC1')
            ax.set_ylabel('PC2')
            ax.set_title(f'{model_short}\n平均偏离: {model_stats.loc[model, "mean"]:.3f}')
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
    model_labels = [m.split('/')[-1][:12] for m in model_stats.index]
    axes[0, 1].boxplot(model_distances, tick_labels=model_labels)
    axes[0, 1].set_xticklabels(model_labels, rotation=45, ha='right', fontsize=8)
    axes[0, 1].set_ylabel('偏离距离')
    axes[0, 1].set_title('按模型的偏离距离分布')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # 2.3 英语 vs 母语
    lang_data = [results_df[results_df['is_english']]['distance_to_native'].values,
                 results_df[~results_df['is_english']]['distance_to_native'].values]
    axes[1, 0].boxplot(lang_data, tick_labels=['英语', '母语'])
    axes[1, 0].set_ylabel('偏离距离')
    axes[1, 0].set_title('英语 vs 母语偏离距离')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 2.4 模型灵活性排名
    model_flexibility = model_stats['mean'].sort_values(ascending=False)
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(model_flexibility)))
    bars = axes[1, 1].barh(range(len(model_flexibility)), model_flexibility.values, color=colors)
    axes[1, 1].set_yticks(range(len(model_flexibility)))
    axes[1, 1].set_yticklabels([m.split('/')[-1][:15] for m in model_flexibility.index], fontsize=8)
    axes[1, 1].set_xlabel('平均偏离距离')
    axes[1, 1].set_title('模型灵活性排名\n(偏离越大=越灵活)')
    axes[1, 1].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'deviation_analysis.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: deviation_analysis.png")
    plt.close()
    
    # 3. 集中度热力图
    fig, ax = plt.subplots(figsize=(12, 8))
    
    results_df['lang_type'] = results_df['is_english'].map({True: '英语', False: '母语'})
    pivot_data = results_df.groupby(['model', 'lang_type'])['distance_to_native'].mean().unstack(fill_value=0)
    
    # 简化模型名称
    pivot_data.index = [m.split('/')[-1][:20] for m in pivot_data.index]
    
    sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax, 
               cbar_kws={'label': '平均偏离距离'})
    ax.set_xlabel('语言类型')
    ax.set_ylabel('模型')
    ax.set_title('模型角色扮演集中度热力图\n(数值越小越集中在原生坐标附近)')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'concentration_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: concentration_heatmap.png")
    plt.close()
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")


if __name__ == '__main__':
    results_df, model_stats, stage1_df = analyze_distribution()
    
    if results_df is not None:
        visualize_distribution(results_df, model_stats, stage1_df)
        
        print("\n" + "=" * 80)
        print("✅ Stage1 vs Stage3 分布分析完成！")
        print("=" * 80)
        print("\n核心发现:")
        print(f"  - 平均偏离距离: {results_df['distance_to_native'].mean():.4f}")
        print(f"  - 最集中的模型: {model_stats.index[0].split('/')[-1]} ({model_stats.iloc[0]['mean']:.4f})")
        print(f"  - 最分散的模型: {model_stats.index[-1].split('/')[-1]} ({model_stats.iloc[-1]['mean']:.4f})")
