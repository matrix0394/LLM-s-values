#!/usr/bin/env python3
"""
Stage0 vs Stage3 距离分析（核心分析）
对比真实国家坐标（Stage0）和：
1. 大模型英语模仿坐标（Stage3-English）
2. 大模型母语模仿坐标（Stage3-Native）
3. 计算英语优势：哪个效果更好
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

def load_stage3_coordinates():
    """加载Stage3多语言模仿坐标"""
    with open('data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl', 'rb') as f:
        data = pickle.load(f)
    print(f"✅ 加载Stage3数据: {len(data)} 行")
    return data

def calculate_distances():
    """计算Stage0和Stage3之间的距离"""
    print("=" * 80)
    print("Stage0 vs Stage3 文化距离分析（核心）")
    print("=" * 80)
    
    # 加载数据
    print("\n1. 加载数据...")
    stage0_coords = load_stage0_coordinates()
    stage3_data = load_stage3_coordinates()
    
    print(f"   Stage0国家/地区数: {len(stage0_coords)}")
    print(f"   Stage3模仿数: {len(stage3_data)}")
    
    # 计算距离
    print("\n2. 计算文化距离...")
    results = []
    
    for _, row in stage3_data.iterrows():
        country = row.get('Country')
        language = row.get('language')
        model = row.get('model_name')
        
        if country not in stage0_coords:
            continue
        
        real_pc1 = stage0_coords[country]['PC1']
        real_pc2 = stage0_coords[country]['PC2']
        llm_pc1 = row['PC1_rescaled']
        llm_pc2 = row['PC2_rescaled']
        
        distance = np.sqrt((llm_pc1 - real_pc1)**2 + (llm_pc2 - real_pc2)**2)
        
        # 判断语言类型
        is_english = language in ['en', 'en-native']
        
        results.append({
            'country': country,
            'language': language,
            'model': model,
            'is_english': is_english,
            'real_PC1': real_pc1,
            'real_PC2': real_pc2,
            'llm_PC1': llm_pc1,
            'llm_PC2': llm_pc2,
            'distance': distance
        })
    
    results_df = pd.DataFrame(results)
    
    # 3. 计算英语优势
    print("\n3. 计算英语优势...")
    english_advantage = []
    
    for country in results_df['country'].unique():
        country_data = results_df[results_df['country'] == country]
        
        # 分离母语和英语
        native_data = country_data[~country_data['is_english']]
        english_data = country_data[country_data['is_english']]
        
        if len(native_data) == 0 or len(english_data) == 0:
            continue
        
        # 对每种母语计算
        for native_lang in native_data['language'].unique():
            native_lang_data = native_data[native_data['language'] == native_lang]
            
            # 按模型配对计算
            for model in native_lang_data['model'].unique():
                native_model = native_lang_data[native_lang_data['model'] == model]
                english_model = english_data[english_data['model'] == model]
                
                if len(native_model) > 0 and len(english_model) > 0:
                    native_dist = native_model['distance'].iloc[0]
                    english_dist = english_model['distance'].iloc[0]
                    
                    advantage = (native_dist - english_dist) / native_dist * 100
                    
                    english_advantage.append({
                        'country': country,
                        'native_language': native_lang,
                        'model': model,
                        'native_distance': native_dist,
                        'english_distance': english_dist,
                        'english_advantage': advantage
                    })
    
    advantage_df = pd.DataFrame(english_advantage)
    
    # 4. 统计分析
    print("\n4. 统计分析...")
    print(f"   总距离计算数: {len(results_df)}")
    print(f"   英语模仿数: {len(results_df[results_df['is_english']])}")
    print(f"   母语模仿数: {len(results_df[~results_df['is_english']])}")
    print(f"   英语优势计算数: {len(advantage_df)}")
    
    # 4.1 英语母语国家/地区基准分析
    print("\n4.1 英语母语国家/地区基准分析:")
    english_native_countries = ['United States', 'United Kingdom', 'Australia', 
                               'New Zealand', 'Canada']
    
    english_native_data = results_df[
        (results_df['country'].isin(english_native_countries)) & 
        (results_df['is_english'])
    ]
    
    if len(english_native_data) > 0:
        print(f"   英语母语国家/地区数: {english_native_data['country'].nunique()}")
        print(f"   平均距离: {english_native_data['distance'].mean():.4f} ± {english_native_data['distance'].std():.4f}")
        print(f"   最小距离: {english_native_data['distance'].min():.4f}")
        print(f"   最大距离: {english_native_data['distance'].max():.4f}")
        
        print("\n   各英语母语国家/地区详细:")
        for country in english_native_countries:
            country_data = english_native_data[english_native_data['country'] == country]
            if len(country_data) > 0:
                print(f"   - {country:20s}: {country_data['distance'].mean():.4f} ± {country_data['distance'].std():.4f} (N={len(country_data)})")
    else:
        print("   ⚠️ 未找到英语母语国家/地区数据")
    
    # 按语言类型统计
    print("\n5. 按语言类型统计:")
    lang_stats = results_df.groupby('is_english')['distance'].agg(['mean', 'std', 'count'])
    print(f"   英语模仿: {lang_stats.loc[True, 'mean']:.4f} ± {lang_stats.loc[True, 'std']:.4f}")
    print(f"   母语模仿: {lang_stats.loc[False, 'mean']:.4f} ± {lang_stats.loc[False, 'std']:.4f}")
    
    # 与英语母语国家基准对比
    if len(english_native_data) > 0:
        english_native_baseline = english_native_data['distance'].mean()
        all_english_mean = lang_stats.loc[True, 'mean']
        print(f"\n   英语母语国家/地区基准: {english_native_baseline:.4f}")
        print(f"   所有英语模仿平均: {all_english_mean:.4f}")
        print(f"   差异: {all_english_mean - english_native_baseline:+.4f}")
    
    # 英语优势排名
    print("\n6. 英语优势排名（所有模型平均）:")
    avg_advantage = advantage_df.groupby(['country', 'native_language'])['english_advantage'].mean().reset_index()
    avg_advantage = avg_advantage.sort_values('english_advantage', ascending=False)
    
    print("\n   Top 10 英语优势:")
    for i, (_, row) in enumerate(avg_advantage.head(10).iterrows(), 1):
        print(f"   {i:2d}. {row['country']:30s} ({row['native_language']:6s}): {row['english_advantage']:+6.1f}%")
    
    print("\n   母语优势（负值）:")
    native_adv = avg_advantage[avg_advantage['english_advantage'] < 0]
    for i, (_, row) in enumerate(native_adv.iterrows(), 1):
        print(f"   {i:2d}. {row['country']:30s} ({row['native_language']:6s}): {row['english_advantage']:+6.1f}%")
    
    # 保存结果
    output_dir = Path('results/analysis/stage0_vs_stage3')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_df.to_csv(output_dir / 'distances_detailed.csv', index=False)
    results_df.to_excel(output_dir / 'distances_detailed.xlsx', index=False)
    advantage_df.to_csv(output_dir / 'english_advantage_by_model.csv', index=False)
    advantage_df.to_excel(output_dir / 'english_advantage_by_model.xlsx', index=False)
    avg_advantage.to_csv(output_dir / 'english_advantage_average.csv', index=False)
    avg_advantage.to_excel(output_dir / 'english_advantage_average.xlsx', index=False)
    
    # 保存英语母语国家/地区基准数据
    if len(english_native_data) > 0:
        english_native_data.to_csv(output_dir / 'english_native_baseline.csv', index=False)
        english_native_data.to_excel(output_dir / 'english_native_baseline.xlsx', index=False)
        
        # 保存基准统计
        baseline_stats = pd.DataFrame({
            'metric': ['mean', 'std', 'min', 'max', 'count'],
            'value': [
                english_native_data['distance'].mean(),
                english_native_data['distance'].std(),
                english_native_data['distance'].min(),
                english_native_data['distance'].max(),
                len(english_native_data)
            ]
        })
        baseline_stats.to_csv(output_dir / 'english_native_baseline_stats.csv', index=False)
    
    print(f"\n✅ 结果已保存到: {output_dir}")
    
    return results_df, advantage_df, avg_advantage, english_native_data if len(english_native_data) > 0 else None

def visualize_results(results_df, advantage_df, avg_advantage):
    """生成可视化图表"""
    print("\n7. 生成可视化图表...")
    
    output_dir = Path('results/analysis/stage0_vs_stage3')
    
    # 1. 母语 vs 英语距离对比
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1.1 距离分布对比
    english_dist = results_df[results_df['is_english']]['distance']
    native_dist = results_df[~results_df['is_english']]['distance']
    
    axes[0, 0].hist([english_dist, native_dist], bins=30, label=['英语', '母语'], 
                    alpha=0.7, edgecolor='black')
    axes[0, 0].set_xlabel('文化距离')
    axes[0, 0].set_ylabel('频数')
    axes[0, 0].set_title('母语 vs 英语距离分布')
    axes[0, 0].legend()
    axes[0, 0].axvline(english_dist.mean(), color='blue', linestyle='--', alpha=0.7)
    axes[0, 0].axvline(native_dist.mean(), color='orange', linestyle='--', alpha=0.7)
    
    # 1.2 英语优势排名（Top 20）
    top20 = avg_advantage.head(20)
    colors = ['green' if x > 0 else 'red' for x in top20['english_advantage']]
    axes[0, 1].barh(range(len(top20)), top20['english_advantage'], color=colors, alpha=0.7)
    axes[0, 1].set_yticks(range(len(top20)))
    axes[0, 1].set_yticklabels([f"{row['country']} ({row['native_language']})" 
                                for _, row in top20.iterrows()], fontsize=8)
    axes[0, 1].set_xlabel('英语优势 (%)')
    axes[0, 1].set_title('英语优势排名 (Top 20)')
    axes[0, 1].axvline(0, color='black', linestyle='-', linewidth=0.5)
    axes[0, 1].invert_yaxis()
    
    # 1.3 按模型的英语优势
    model_avg = advantage_df.groupby('model')['english_advantage'].mean().sort_values()
    axes[1, 0].bar(range(len(model_avg)), model_avg.values)
    axes[1, 0].set_xticks(range(len(model_avg)))
    axes[1, 0].set_xticklabels(model_avg.index, rotation=45, ha='right')
    axes[1, 0].set_ylabel('平均英语优势 (%)')
    axes[1, 0].set_title('按模型的平均英语优势')
    axes[1, 0].axhline(0, color='black', linestyle='-', linewidth=0.5)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 1.4 英语优势分布
    axes[1, 1].hist(advantage_df['english_advantage'], bins=40, edgecolor='black', alpha=0.7)
    axes[1, 1].set_xlabel('英语优势 (%)')
    axes[1, 1].set_ylabel('频数')
    axes[1, 1].set_title('英语优势分布')
    axes[1, 1].axvline(0, color='red', linestyle='--', linewidth=2, label='零点')
    axes[1, 1].axvline(advantage_df['english_advantage'].mean(), color='blue', 
                      linestyle='--', linewidth=2, label=f'平均值: {advantage_df["english_advantage"].mean():.1f}%')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'english_advantage_analysis.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: english_advantage_analysis.png")
    plt.close()
    
    # 2. 全局散点图：Stage0 vs Stage3（所有国家/地区）
    fig, ax = plt.subplots(figsize=(16, 14))
    
    # 计算每个国家/地区的平均模仿坐标
    country_summary = []
    for country in results_df['country'].unique():
        country_data = results_df[results_df['country'] == country]
        
        # 真实坐标
        real_pc1 = country_data['real_PC1'].iloc[0]
        real_pc2 = country_data['real_PC2'].iloc[0]
        
        # 英语模仿平均坐标
        english = country_data[country_data['is_english']]
        eng_pc1 = english['llm_PC1'].mean() if len(english) > 0 else None
        eng_pc2 = english['llm_PC2'].mean() if len(english) > 0 else None
        
        # 母语模仿平均坐标
        native = country_data[~country_data['is_english']]
        nat_pc1 = native['llm_PC1'].mean() if len(native) > 0 else None
        nat_pc2 = native['llm_PC2'].mean() if len(native) > 0 else None
        
        country_summary.append({
            'country': country,
            'real_pc1': real_pc1,
            'real_pc2': real_pc2,
            'eng_pc1': eng_pc1,
            'eng_pc2': eng_pc2,
            'nat_pc1': nat_pc1,
            'nat_pc2': nat_pc2
        })
    
    # 绘制所有真实位置
    for item in country_summary:
        ax.scatter(item['real_pc1'], item['real_pc2'], c='gold', s=200, marker='*', 
                  alpha=0.8, edgecolors='black', linewidths=1.5, zorder=5)
    
    # 绘制英语模仿位置和箭头
    for item in country_summary:
        if item['eng_pc1'] is not None:
            ax.scatter(item['eng_pc1'], item['eng_pc2'], c='#27AE60', s=80, marker='o',
                      alpha=0.6, edgecolors='black', linewidths=0.8, zorder=4)
            # 绘制箭头：真实 → 英语
            ax.annotate('', xy=(item['eng_pc1'], item['eng_pc2']), 
                       xytext=(item['real_pc1'], item['real_pc2']),
                       arrowprops=dict(arrowstyle='->', lw=1, color='#27AE60', alpha=0.3))
    
    # 绘制母语模仿位置和箭头
    for item in country_summary:
        if item['nat_pc1'] is not None:
            ax.scatter(item['nat_pc1'], item['nat_pc2'], c='#E74C3C', s=80, marker='s',
                      alpha=0.6, edgecolors='black', linewidths=0.8, zorder=4)
            # 绘制箭头：真实 → 母语
            ax.annotate('', xy=(item['nat_pc1'], item['nat_pc2']), 
                       xytext=(item['real_pc1'], item['real_pc2']),
                       arrowprops=dict(arrowstyle='->', lw=1, color='#E74C3C', alpha=0.3, linestyle='--'))
    
    ax.set_xlabel('PC1 (生存 ← → 自我表达)', fontsize=13, fontweight='bold')
    ax.set_ylabel('PC2 (传统 ← → 现代)', fontsize=13, fontweight='bold')
    ax.set_title('全球文化坐标：Stage0真实位置 vs Stage3 LLM模仿位置\n(金星=真实, 绿圆=英语模仿, 红方=母语模仿)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(0, color='black', linewidth=1, alpha=0.5)
    ax.axvline(0, color='black', linewidth=1, alpha=0.5)
    
    # 添加图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', 
               markersize=15, label='真实位置 (Stage0)', markeredgecolor='black', markeredgewidth=1.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#27AE60', 
               markersize=10, label='英语模仿 (Stage3)', markeredgecolor='black', markeredgewidth=1),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#E74C3C', 
               markersize=10, label='母语模仿 (Stage3)', markeredgecolor='black', markeredgewidth=1),
        Line2D([0], [0], color='#27AE60', linewidth=2, label='英语偏移', alpha=0.5),
        Line2D([0], [0], color='#E74C3C', linewidth=2, linestyle='--', label='母语偏移', alpha=0.5)
    ]
    ax.legend(handles=legend_elements, loc='best', fontsize=12, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'global_coordinates_scatter.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: global_coordinates_scatter.png")
    plt.close()
    
    # 3. 东亚国家/地区详细分析
    east_asian = ['China', 'Japan', 'Korea (the Republic of)', 'Hong Kong', 
                  'Taiwan (Province of China)', 'Macao', 'Singapore']  # 包含国家和地区
    
    ea_advantage = avg_advantage[avg_advantage['country'].isin(east_asian)].copy()
    
    if len(ea_advantage) > 0:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = ['green' if x > 0 else 'red' for x in ea_advantage['english_advantage']]
        bars = ax.barh(range(len(ea_advantage)), ea_advantage['english_advantage'], 
                      color=colors, alpha=0.7, edgecolor='black')
        
        ax.set_yticks(range(len(ea_advantage)))
        ax.set_yticklabels([f"{row['country']}\n({row['native_language']})" 
                           for _, row in ea_advantage.iterrows()])
        ax.set_xlabel('英语优势 (%)', fontsize=12)
        ax.set_title('东亚国家/地区英语优势详细分析', fontsize=14)
        ax.axvline(0, color='black', linestyle='-', linewidth=1)
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()
        
        # 添加数值标签
        for i, (bar, val) in enumerate(zip(bars, ea_advantage['english_advantage'])):
            ax.text(val, i, f' {val:+.1f}%', va='center', 
                   ha='left' if val > 0 else 'right', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'east_asia_analysis.png', dpi=300, bbox_inches='tight')
        print(f"   ✅ 保存: east_asia_analysis.png")
        plt.close()
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")

if __name__ == '__main__':
    results_df, advantage_df, avg_advantage, english_native_baseline = calculate_distances()
    visualize_results(results_df, advantage_df, avg_advantage)
    
    print("\n" + "=" * 80)
    print("✅ Stage0 vs Stage3 分析完成！")
    print("=" * 80)
    print("\n核心发现:")
    print(f"  - 英语模仿平均距离: {results_df[results_df['is_english']]['distance'].mean():.4f}")
    print(f"  - 母语模仿平均距离: {results_df[~results_df['is_english']]['distance'].mean():.4f}")
    print(f"  - 平均英语优势: {advantage_df['english_advantage'].mean():+.1f}%")
    if english_native_baseline is not None:
        print(f"  - 英语母语国家/地区基准: {english_native_baseline['distance'].mean():.4f}")
