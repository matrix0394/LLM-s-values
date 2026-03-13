#!/usr/bin/env python3
"""
Stage2 vs Stage3 英语坐标对比
对比Stage2（纯英语角色扮演）和Stage3中的英语部分
验证：两个Stage的英语数据是否一致
"""

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.spatial.distance import euclidean
from scipy.stats import pearsonr

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_stage2_english():
    """加载Stage2英语角色扮演坐标"""
    stage2_path = Path('data/roleplay_English')
    pca_files = list(stage2_path.glob('roleplay_pca_*_latest.pkl'))
    
    if not pca_files:
        pca_files = list(stage2_path.glob('roleplay_pca_*.pkl'))
    
    if pca_files:
        latest_file = max(pca_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'rb') as f:
            df = pickle.load(f)
        print(f"✅ 加载Stage2数据: {len(df)} 行")
        return df
    return pd.DataFrame()

def load_stage3_english():
    """加载Stage3中的英语部分"""
    with open('data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl', 'rb') as f:
        df = pickle.load(f)
    
    # 只保留英语部分
    df_en = df[df['language'].isin(['en', 'en-native'])].copy()
    print(f"✅ 加载Stage3英语数据: {len(df_en)} 行")
    return df_en

def compare_english_coordinates():
    """对比Stage2和Stage3的英语坐标"""
    print("=" * 80)
    print("Stage2 vs Stage3 英语坐标对比分析")
    print("=" * 80)
    
    # 加载数据
    print("\n1. 加载数据...")
    stage2_df = load_stage2_english()
    stage3_df = load_stage3_english()
    
    if len(stage2_df) == 0:
        print("⚠️ Stage2数据为空，跳过分析")
        return None, None
    
    # 统一列名
    stage2_df = stage2_df.rename(columns={
        'Country': 'country',
        'model_name': 'model'
    })
    stage3_df = stage3_df.rename(columns={
        'Country': 'country',
        'model_name': 'model'
    })
    
    # 2. 匹配相同的国家-模型组合
    print("\n2. 匹配国家-模型组合...")
    
    # 提取共同的国家和模型
    common_countries = set(stage2_df['country'].unique()) & set(stage3_df['country'].unique())
    common_models = set(stage2_df['model'].unique()) & set(stage3_df['model'].unique())
    
    print(f"   共同国家/地区数: {len(common_countries)}")
    print(f"   共同模型数: {len(common_models)}")
    
    # 匹配数据
    comparisons = []
    
    for country in common_countries:
        for model in common_models:
            stage2_row = stage2_df[(stage2_df['country'] == country) & 
                                  (stage2_df['model'] == model)]
            stage3_row = stage3_df[(stage3_df['country'] == country) & 
                                  (stage3_df['model'] == model)]
            
            if len(stage2_row) > 0 and len(stage3_row) > 0:
                s2_pc1 = stage2_row['PC1_rescaled'].iloc[0]
                s2_pc2 = stage2_row['PC2_rescaled'].iloc[0]
                s3_pc1 = stage3_row['PC1_rescaled'].iloc[0]
                s3_pc2 = stage3_row['PC2_rescaled'].iloc[0]
                
                # 计算差异
                diff_pc1 = s3_pc1 - s2_pc1
                diff_pc2 = s3_pc2 - s2_pc2
                distance = euclidean([s2_pc1, s2_pc2], [s3_pc1, s3_pc2])
                
                comparisons.append({
                    'country': country,
                    'model': model,
                    'stage2_PC1': s2_pc1,
                    'stage2_PC2': s2_pc2,
                    'stage3_PC1': s3_pc1,
                    'stage3_PC2': s3_pc2,
                    'diff_PC1': diff_pc1,
                    'diff_PC2': diff_pc2,
                    'distance': distance
                })
    
    comp_df = pd.DataFrame(comparisons)
    
    # 3. 统计分析
    print("\n3. 统计分析...")
    print(f"   匹配的组合数: {len(comp_df)}")
    print(f"   平均距离: {comp_df['distance'].mean():.4f}")
    print(f"   距离标准差: {comp_df['distance'].std():.4f}")
    print(f"   最大距离: {comp_df['distance'].max():.4f}")
    print(f"   最小距离: {comp_df['distance'].min():.4f}")
    
    # PC1和PC2的相关性
    corr_pc1, p_pc1 = pearsonr(comp_df['stage2_PC1'], comp_df['stage3_PC1'])
    corr_pc2, p_pc2 = pearsonr(comp_df['stage2_PC2'], comp_df['stage3_PC2'])
    
    print(f"\n   PC1相关性: r={corr_pc1:.4f}, p={p_pc1:.4e}")
    print(f"   PC2相关性: r={corr_pc2:.4f}, p={p_pc2:.4e}")
    
    # 按国家/地区统计
    country_stats = comp_df.groupby('country')['distance'].agg(['mean', 'std', 'count'])
    country_stats = country_stats.sort_values('mean', ascending=False)
    
    print("\n4. 差异最大的国家（Top 10）:")
    for i, (country, row) in enumerate(country_stats.head(10).iterrows(), 1):
        print(f"   {i:2d}. {country:30s}: {row['mean']:.4f} ± {row['std']:.4f}")
    
    # 按模型统计
    model_stats = comp_df.groupby('model')['distance'].agg(['mean', 'std', 'count'])
    model_stats = model_stats.sort_values('mean', ascending=False)
    
    print("\n5. 按模型统计:")
    for model, row in model_stats.iterrows():
        print(f"   {model:20s}: {row['mean']:.4f} ± {row['std']:.4f}")
    
    # 保存结果
    output_dir = Path('results/analysis/stage2_vs_stage3')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    comp_df.to_csv(output_dir / 'english_comparison.csv', index=False)
    comp_df.to_excel(output_dir / 'english_comparison.xlsx', index=False)
    country_stats.to_csv(output_dir / 'country_differences.csv')
    model_stats.to_csv(output_dir / 'model_differences.csv')
    
    print(f"\n✅ 结果已保存到: {output_dir}")
    
    return comp_df, country_stats

def visualize_comparison(comp_df, country_stats):
    """可视化对比结果"""
    print("\n6. 生成可视化图表...")
    
    output_dir = Path('results/analysis/stage2_vs_stage3')
    
    # 1. 散点图：Stage2 vs Stage3坐标
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # PC1对比
    axes[0].scatter(comp_df['stage2_PC1'], comp_df['stage3_PC1'], alpha=0.5, s=50)
    axes[0].plot([comp_df['stage2_PC1'].min(), comp_df['stage2_PC1'].max()],
                [comp_df['stage2_PC1'].min(), comp_df['stage2_PC1'].max()],
                'r--', label='y=x (完全一致)')
    axes[0].set_xlabel('Stage2 PC1')
    axes[0].set_ylabel('Stage3 PC1')
    axes[0].set_title(f'PC1对比 (r={pearsonr(comp_df["stage2_PC1"], comp_df["stage3_PC1"])[0]:.3f})')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # PC2对比
    axes[1].scatter(comp_df['stage2_PC2'], comp_df['stage3_PC2'], alpha=0.5, s=50)
    axes[1].plot([comp_df['stage2_PC2'].min(), comp_df['stage2_PC2'].max()],
                [comp_df['stage2_PC2'].min(), comp_df['stage2_PC2'].max()],
                'r--', label='y=x (完全一致)')
    axes[1].set_xlabel('Stage2 PC2')
    axes[1].set_ylabel('Stage3 PC2')
    axes[1].set_title(f'PC2对比 (r={pearsonr(comp_df["stage2_PC2"], comp_df["stage3_PC2"])[0]:.3f})')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'coordinate_correlation.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: coordinate_correlation.png")
    plt.close()
    
    # 2. 距离分布和差异分析
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 2.1 距离分布
    axes[0, 0].hist(comp_df['distance'], bins=30, edgecolor='black', alpha=0.7)
    axes[0, 0].set_xlabel('欧氏距离')
    axes[0, 0].set_ylabel('频数')
    axes[0, 0].set_title('Stage2 vs Stage3 英语坐标距离分布')
    axes[0, 0].axvline(comp_df['distance'].mean(), color='red', linestyle='--',
                      label=f'平均: {comp_df["distance"].mean():.3f}')
    axes[0, 0].legend()
    
    # 2.2 PC1差异分布
    axes[0, 1].hist(comp_df['diff_PC1'], bins=30, edgecolor='black', alpha=0.7)
    axes[0, 1].set_xlabel('PC1差异 (Stage3 - Stage2)')
    axes[0, 1].set_ylabel('频数')
    axes[0, 1].set_title('PC1差异分布')
    axes[0, 1].axvline(0, color='red', linestyle='--')
    axes[0, 1].axvline(comp_df['diff_PC1'].mean(), color='blue', linestyle='--',
                      label=f'平均: {comp_df["diff_PC1"].mean():.3f}')
    axes[0, 1].legend()
    
    # 2.3 PC2差异分布
    axes[1, 0].hist(comp_df['diff_PC2'], bins=30, edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('PC2差异 (Stage3 - Stage2)')
    axes[1, 0].set_ylabel('频数')
    axes[1, 0].set_title('PC2差异分布')
    axes[1, 0].axvline(0, color='red', linestyle='--')
    axes[1, 0].axvline(comp_df['diff_PC2'].mean(), color='blue', linestyle='--',
                      label=f'平均: {comp_df["diff_PC2"].mean():.3f}')
    axes[1, 0].legend()
    
    # 2.4 按国家/地区的平均距离（Top 15）
    top15 = country_stats.head(15)
    axes[1, 1].barh(range(len(top15)), top15['mean'])
    axes[1, 1].set_yticks(range(len(top15)))
    axes[1, 1].set_yticklabels(top15.index, fontsize=9)
    axes[1, 1].set_xlabel('平均距离')
    axes[1, 1].set_title('差异最大的国家 (Top 15)')
    axes[1, 1].invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'difference_analysis.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: difference_analysis.png")
    plt.close()
    
    # 3. 2D坐标对比图
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 绘制Stage2和Stage3的点
    ax.scatter(comp_df['stage2_PC1'], comp_df['stage2_PC2'], 
              c='blue', s=50, alpha=0.5, label='Stage2', marker='o')
    ax.scatter(comp_df['stage3_PC1'], comp_df['stage3_PC2'], 
              c='red', s=50, alpha=0.5, label='Stage3', marker='s')
    
    # 连线显示差异
    for _, row in comp_df.iterrows():
        ax.plot([row['stage2_PC1'], row['stage3_PC1']], 
               [row['stage2_PC2'], row['stage3_PC2']], 
               'gray', alpha=0.2, linewidth=0.5)
    
    ax.set_xlabel('PC1 (Rescaled)')
    ax.set_ylabel('PC2 (Rescaled)')
    ax.set_title('Stage2 vs Stage3 英语坐标分布对比\n(蓝圆=Stage2, 红方=Stage3, 灰线=差异)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'coordinate_distribution.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: coordinate_distribution.png")
    plt.close()
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")

if __name__ == '__main__':
    comp_df, country_stats = compare_english_coordinates()
    
    if comp_df is not None:
        visualize_comparison(comp_df, country_stats)
        
        print("\n" + "=" * 80)
        print("✅ Stage2 vs Stage3 英语对比完成！")
        print("=" * 80)
        print("\n核心发现:")
        print(f"  - 平均坐标距离: {comp_df['distance'].mean():.4f}")
        print(f"  - PC1相关性: {pearsonr(comp_df['stage2_PC1'], comp_df['stage3_PC1'])[0]:.4f}")
        print(f"  - PC2相关性: {pearsonr(comp_df['stage2_PC2'], comp_df['stage3_PC2'])[0]:.4f}")
        print(f"  - 结论: {'高度一致' if comp_df['distance'].mean() < 0.5 else '存在差异'}")
