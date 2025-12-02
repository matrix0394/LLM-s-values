#!/usr/bin/env python3
"""
Stage0 vs Stage2 距离分析
对比真实国家坐标（Stage0）和大模型英语模仿坐标（Stage2）的文化距离
"""

import pickle
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_stage0_coordinates():
    """加载Stage0真实国家坐标"""
    with open('data/country_values/country_scores_pca.json') as f:
        data = json.load(f)
    
    coords = {}
    for item in data:
        country = item.get('Country')
        if country:
            coords[country] = {
                'PC1': item.get('PC1_rescaled'),
                'PC2': item.get('PC2_rescaled')
            }
    return coords

def load_stage2_coordinates():
    """加载Stage2英语模仿坐标（从Stage3数据中提取）"""
    # Stage2的旧pickle文件有兼容性问题，直接从Stage3提取英语数据
    print("⚠️ 从Stage3数据中提取英语部分作为Stage2数据")
    
    stage3_file = Path('data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl')
    
    if not stage3_file.exists():
        raise FileNotFoundError(f"未找到Stage3数据文件: {stage3_file}")
    
    # 加载Stage3数据
    stage3_data = pd.read_pickle(stage3_file)
    
    # 过滤出英语数据（data_source == 'Multilingual' 且 language == 'en'）
    stage2_data = stage3_data[
        (stage3_data['data_source'] == 'Multilingual') & 
        (stage3_data['language'] == 'en')
    ].copy()
    
    print(f"✅ 从Stage3提取Stage2英语数据: {len(stage2_data)} 行")
    return stage2_data

def calculate_distances():
    """计算Stage0和Stage2之间的距离"""
    print("=" * 80)
    print("Stage0 vs Stage2 文化距离分析")
    print("=" * 80)
    
    # 加载数据
    print("\n1. 加载数据...")
    stage0_coords = load_stage0_coordinates()
    stage2_data = load_stage2_coordinates()
    
    # 过滤出英语模仿数据
    if 'language' in stage2_data.columns:
        stage2_en = stage2_data[stage2_data['language'] == 'en'].copy()
    else:
        stage2_en = stage2_data.copy()
    
    print(f"   Stage0国家/地区数: {len(stage0_coords)}")
    print(f"   Stage2英语模仿数: {len(stage2_en)}")
    
    # 计算距离
    print("\n2. 计算文化距离...")
    results = []
    
    for _, row in stage2_en.iterrows():
        country = row.get('Country') or row.get('country')
        model = row.get('model_name') or row.get('model')
        
        if country not in stage0_coords:
            continue
        
        real_pc1 = stage0_coords[country]['PC1']
        real_pc2 = stage0_coords[country]['PC2']
        llm_pc1 = row['PC1_rescaled']
        llm_pc2 = row['PC2_rescaled']
        
        distance = np.sqrt((llm_pc1 - real_pc1)**2 + (llm_pc2 - real_pc2)**2)
        
        results.append({
            'country': country,
            'model': model,
            'real_PC1': real_pc1,
            'real_PC2': real_pc2,
            'llm_PC1': llm_pc1,
            'llm_PC2': llm_pc2,
            'distance': distance
        })
    
    results_df = pd.DataFrame(results)
    
    # 统计分析
    print("\n3. 统计分析...")
    print(f"   总计算组合数: {len(results_df)}")
    print(f"   平均距离: {results_df['distance'].mean():.4f}")
    print(f"   距离标准差: {results_df['distance'].std():.4f}")
    print(f"   最小距离: {results_df['distance'].min():.4f}")
    print(f"   最大距离: {results_df['distance'].max():.4f}")
    
    # 按国家/地区统计
    country_stats = results_df.groupby('country')['distance'].agg(['mean', 'std', 'count'])
    country_stats = country_stats.sort_values('mean')
    
    print("\n4. 按国家/地区统计（平均距离最小的前10个）:")
    for i, (country, row) in enumerate(country_stats.head(10).iterrows(), 1):
        print(f"   {i:2d}. {country:30s}: {row['mean']:.4f} ± {row['std']:.4f} (N={int(row['count'])})")
    
    # 按模型统计
    model_stats = results_df.groupby('model')['distance'].agg(['mean', 'std', 'count'])
    model_stats = model_stats.sort_values('mean')
    
    print("\n5. 按模型统计:")
    for model, row in model_stats.iterrows():
        print(f"   {model:20s}: {row['mean']:.4f} ± {row['std']:.4f} (N={int(row['count'])})")
    
    # 保存结果
    output_dir = Path('results/analysis/stage0_vs_stage2')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_df.to_csv(output_dir / 'distances_detailed.csv', index=False)
    results_df.to_excel(output_dir / 'distances_detailed.xlsx', index=False)
    country_stats.to_csv(output_dir / 'distances_by_country.csv')
    model_stats.to_csv(output_dir / 'distances_by_model.csv')
    
    print(f"\n✅ 结果已保存到: {output_dir}")
    
    return results_df, country_stats, model_stats

def visualize_results(results_df, country_stats, model_stats):
    """生成可视化图表"""
    print("\n6. 生成可视化图表...")
    
    output_dir = Path('results/analysis/stage0_vs_stage2')
    
    # 1. 距离分布直方图
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1.1 整体距离分布
    axes[0, 0].hist(results_df['distance'], bins=30, edgecolor='black', alpha=0.7)
    axes[0, 0].set_xlabel('文化距离')
    axes[0, 0].set_ylabel('频数')
    axes[0, 0].set_title('Stage0 vs Stage2 距离分布')
    axes[0, 0].axvline(results_df['distance'].mean(), color='red', linestyle='--', 
                       label=f'平均值: {results_df["distance"].mean():.3f}')
    axes[0, 0].legend()
    
    # 1.2 按国家的平均距离（Top 15）
    top_countries = country_stats.head(15)
    axes[0, 1].barh(range(len(top_countries)), top_countries['mean'])
    axes[0, 1].set_yticks(range(len(top_countries)))
    axes[0, 1].set_yticklabels(top_countries.index)
    axes[0, 1].set_xlabel('平均文化距离')
    axes[0, 1].set_title('按国家/地区的平均距离（Top 15最接近）')
    axes[0, 1].invert_yaxis()
    
    # 1.3 按模型的平均距离
    axes[1, 0].bar(range(len(model_stats)), model_stats['mean'])
    axes[1, 0].set_xticks(range(len(model_stats)))
    axes[1, 0].set_xticklabels(model_stats.index, rotation=45, ha='right')
    axes[1, 0].set_ylabel('平均文化距离')
    axes[1, 0].set_title('按模型的平均距离')
    
    # 1.4 距离箱线图（按模型）
    model_distances = [results_df[results_df['model'] == m]['distance'].values 
                      for m in model_stats.index]
    axes[1, 1].boxplot(model_distances, labels=model_stats.index)
    axes[1, 1].set_xticklabels(model_stats.index, rotation=45, ha='right')
    axes[1, 1].set_ylabel('文化距离')
    axes[1, 1].set_title('模型距离分布（箱线图）')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'distance_analysis.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: distance_analysis.png")
    plt.close()
    
    # 2. 散点图：真实坐标 vs LLM模仿坐标
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 绘制真实国家
    unique_countries = results_df['country'].unique()
    for country in unique_countries:
        country_data = results_df[results_df['country'] == country]
        real_pc1 = country_data['real_PC1'].iloc[0]
        real_pc2 = country_data['real_PC2'].iloc[0]
        
        # 真实国家点
        ax.scatter(real_pc1, real_pc2, c='red', s=100, marker='*', 
                  alpha=0.6, edgecolors='darkred', linewidths=1.5)
        
        # LLM模仿点
        ax.scatter(country_data['llm_PC1'], country_data['llm_PC2'], 
                  c='blue', s=30, alpha=0.3)
        
        # 连线（只连接平均点）
        avg_llm_pc1 = country_data['llm_PC1'].mean()
        avg_llm_pc2 = country_data['llm_PC2'].mean()
        ax.plot([real_pc1, avg_llm_pc1], [real_pc2, avg_llm_pc2], 
               'gray', alpha=0.3, linewidth=0.5)
    
    ax.set_xlabel('PC1 (Rescaled)')
    ax.set_ylabel('PC2 (Rescaled)')
    ax.set_title('Stage0真实坐标 vs Stage2英语模仿坐标\n(红星=真实国家, 蓝点=LLM模仿)')
    ax.grid(True, alpha=0.3)
    ax.legend(['真实国家', 'LLM模仿', '连线'], loc='best')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'coordinates_scatter.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: coordinates_scatter.png")
    plt.close()
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")

if __name__ == '__main__':
    results_df, country_stats, model_stats = calculate_distances()
    visualize_results(results_df, country_stats, model_stats)
    
    print("\n" + "=" * 80)
    print("✅ Stage0 vs Stage2 分析完成！")
    print("=" * 80)
