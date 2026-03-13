#!/usr/bin/env python3
"""
四张图的绘图脚本（更新版）
================
图1: 4张世界地图热力图 (LLM英语PC1/PC2 + WVS PC1/PC2)
图2: 6种语言大模型自身价值观 (类似FigS2A2条形图)
图3: Digital Orientalism地图 (中东+东亚distance)
图4: 撒哈拉以南非洲和拉丁美洲地图
"""

import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# 设置
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

PROJECT_ROOT = Path("/Users/yxy/code/LLM's values/LLM's values")
OUTPUT_DIR = PROJECT_ROOT / 'results' / 'figures'


def plot_figure1_maps():
    """图1: 4张世界地图热力图"""
    print("绘制图1 (4张地图)...")
    
    # 加载数据
    df = pd.read_csv(OUTPUT_DIR / 'figure1_data_45countries.csv')
    
    # 国家名称映射 (我们的名称 -> ISO3代码)
    country_to_iso = {
        'Algeria': 'DZA', 'Burkina Faso': 'BFA', 'Egypt': 'EGY', 'Iraq': 'IRQ',
        'Jordan': 'JOR', 'Kazakhstan': 'KAZ', 'Kuwait': 'KWT', 'Lebanon': 'LBN',
        'Libya': 'LBY', 'Mali': 'MLI', 'Morocco': 'MAR', 'Palestine': 'PSE',
        'Qatar': 'QAT', 'Tunisia': 'TUN', 'Yemen': 'YEM', 'Austria': 'AUT',
        'Belgium': 'BEL', 'France': 'FRA', 'Italy': 'ITA', 'Luxembourg': 'LUX',
        'Portugal': 'PRT', 'Spain': 'ESP', 'China': 'CHN', 'Japan': 'JPN',
        'Korea, Republic of': 'KOR', 'Macao': 'MAC', 'Taiwan, Province of China': 'TWN',
        'Argentina': 'ARG', 'Bolivia': 'BOL', 'Brazil': 'BRA', 'Chile': 'CHL',
        'Colombia': 'COL', 'Ecuador': 'ECU', 'Guatemala': 'GTM', 'Haiti': 'HTI',
        'Mexico': 'MEX', 'Nicaragua': 'NIC', 'Peru': 'PER', 'Uruguay': 'URY',
        'Venezuela': 'VEN', 'Belarus': 'BLR', 'Russian Federation': 'RUS',
        'Germany': 'DEU', 'Switzerland': 'CHE', 'Kyrgyzstan': 'KGZ'
    }
    
    # 添加ISO代码
    df['iso_a3'] = df['country'].map(country_to_iso)
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 12))
    
    # 找全局范围
    vmin_pc1 = min(df['LLM_EN_PC1'].min(), df['WVS_PC1'].min())
    vmax_pc1 = max(df['LLM_EN_PC1'].max(), df['WVS_PC1'].max())
    vmin_pc2 = min(df['LLM_EN_PC2'].min(), df['WVS_PC2'].min())
    vmax_pc2 = max(df['LLM_EN_PC2'].max(), df['WVS_PC2'].max())
    
    # 由于没有shapefile，我们用简化方式：散点图代替地图
    # 实际使用时可以用geopandas绑定shapefile
    
    # PC1: LLM英语 (左上)
    ax1 = axes[0, 0]
    scatter1 = ax1.scatter(df['LLM_EN_PC1'], df['LLM_EN_PC2'], 
                          c=df['LLM_EN_PC1'], cmap='RdYlBu_r', s=100, alpha=0.8)
    for _, row in df.iterrows():
        ax1.annotate(row['country'], (row['LLM_EN_PC1'], row['LLM_EN_PC2']), 
                    fontsize=6, alpha=0.7)
    ax1.set_xlabel('PC1 (LLM English)', fontsize=12)
    ax1.set_ylabel('PC2', fontsize=12)
    ax1.set_title('LLM English Roleplay - PC1', fontsize=14)
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, label='PC1')
    
    # PC1: WVS基准 (右上)
    ax2 = axes[0, 1]
    scatter2 = ax2.scatter(df['WVS_PC1'], df['WVS_PC2'], 
                          c=df['WVS_PC1'], cmap='RdYlBu_r', s=100, alpha=0.8)
    for _, row in df.iterrows():
        ax2.annotate(row['country'], (row['WVS_PC1'], row['WVS_PC2']), 
                    fontsize=6, alpha=0.7)
    ax2.set_xlabel('PC1 (WVS)', fontsize=12)
    ax2.set_ylabel('PC2', fontsize=12)
    ax2.set_title('WVS Benchmark - PC1', fontsize=14)
    ax2.grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=ax2, label='PC1')
    
    # PC2: LLM英语 (左下)
    ax3 = axes[1, 0]
    scatter3 = ax3.scatter(df['LLM_EN_PC1'], df['LLM_EN_PC2'], 
                          c=df['LLM_EN_PC2'], cmap='RdYlBu_r', s=100, alpha=0.8)
    for _, row in df.iterrows():
        ax3.annotate(row['country'], (row['LLM_EN_PC1'], row['LLM_EN_PC2']), 
                    fontsize=6, alpha=0.7)
    ax3.set_xlabel('PC1 (LLM English)', fontsize=12)
    ax3.set_ylabel('PC2', fontsize=12)
    ax3.set_title('LLM English Roleplay - PC2', fontsize=14)
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter3, ax=ax3, label='PC2')
    
    # PC2: WVS基准 (右下)
    ax4 = axes[1, 1]
    scatter4 = ax4.scatter(df['WVS_PC1'], df['WVS_PC2'], 
                          c=df['WVS_PC2'], cmap='RdYlBu_r', s=100, alpha=0.8)
    for _, row in df.iterrows():
        ax4.annotate(row['country'], (row['WVS_PC1'], row['WVS_PC2']), 
                    fontsize=6, alpha=0.7)
    ax4.set_xlabel('PC1 (WVS)', fontsize=12)
    ax4.set_ylabel('PC2', fontsize=12)
    ax4.set_title('WVS Benchmark - PC2', fontsize=14)
    ax4.grid(True, alpha=0.3)
    plt.colorbar(scatter4, ax=ax4, label='PC2')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure1_45countries_maps.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 图1已保存")
    
    # 提示：需要shapefile才能画真正的地图
    print("  ⚠️ 注意：当前为散点图，需要geopandas+shapefile才能画真正的地图")


def plot_figure2_language():
    """图2: 6种语言intrinsic values (类似FigS2A2条形图)"""
    print("绘制图2...")
    
    df = pd.read_csv(OUTPUT_DIR / 'figure2_language_data.csv')
    
    # 参考FigS2A2的样式
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    languages = df['language'].tolist()
    language_names = df['language_name'].tolist()
    x = np.arange(len(languages))
    width = 0.6
    
    # 颜色
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6', '#F39C12', '#1ABC9C']
    
    # PC1
    ax1 = axes[0]
    bars1 = ax1.bar(x, df['PC1_mean'], width, 
                    yerr=df['PC1_std'], capsize=8,
                    color=colors, alpha=0.85, edgecolor='black', linewidth=1)
    ax1.set_ylabel('PC1 (Survival vs Self-Expression)', fontsize=12)
    ax1.set_title('LLM Intrinsic Values by Language - PC1', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'{ln}\n({l})' for l, ln in zip(languages, language_names)], fontsize=10)
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(-5, 6)
    
    # 添加数值标签
    for bar, mean, std in zip(bars1, df['PC1_mean'], df['PC1_std']):
        height = bar.get_height()
        ax1.annotate(f'{mean:.2f}',
                   xy=(bar.get_x() + bar.get_width() / 2, height + std + 0.2),
                   ha='center', va='bottom', fontsize=9)
    
    # PC2
    ax2 = axes[1]
    bars2 = ax2.bar(x, df['PC2_mean'], width, 
                    yerr=df['PC2_std'], capsize=8,
                    color=colors, alpha=0.85, edgecolor='black', linewidth=1)
    ax2.set_ylabel('PC2 (Traditional vs Secular)', fontsize=12)
    ax2.set_title('LLM Intrinsic Values by Language - PC2', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'{ln}\n({l})' for l, ln in zip(languages, language_names)], fontsize=10)
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(-4, 5)
    
    # 添加数值标签
    for bar, mean, std in zip(bars2, df['PC2_mean'], df['PC2_std']):
        height = bar.get_height()
        ax2.annotate(f'{mean:.2f}',
                   xy=(bar.get_x() + bar.get_width() / 2, height + std + 0.2),
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure2_language_values_grid.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 图2已保存")


def plot_figure3_orientalism():
    """图3: Digital Orientalism地图"""
    print("绘制图3...")
    
    df = pd.read_csv(OUTPUT_DIR / 'figure3_distance_middleeast_eastasia.csv')
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 中东
    me_df = df[df['region'] == 'Middle East'].sort_values('advantage_mean')
    ax1 = axes[0]
    colors = ['#E74C3C' if x < 0 else '#2ECC71' for x in me_df['advantage_mean']]
    ax1.barh(me_df['country'], me_df['advantage_mean'], color=colors, alpha=0.8)
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax1.set_xlabel('English Advantage (%)', fontsize=12)
    ax1.set_title('Middle East\n(English Advantage)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # 添加数值
    for i, (v, c) in enumerate(zip(me_df['advantage_mean'], colors)):
        ax1.text(v + 1 if v >= 0 else v - 1, i, f'{v:.1f}%', 
                va='center', ha='left' if v >= 0 else 'right', fontsize=9)
    
    # 东亚
    ea_df = df[df['region'] == 'East Asia'].sort_values('advantage_mean')
    ax2 = axes[1]
    colors = ['#E74C3C' if x < 0 else '#2ECC71' for x in ea_df['advantage_mean']]
    ax2.barh(ea_df['country'], ea_df['advantage_mean'], color=colors, alpha=0.8)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_xlabel('English Advantage (%)', fontsize=12)
    ax2.set_title('East Asia\n(English Advantage)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    for i, (v, c) in enumerate(zip(ea_df['advantage_mean'], colors)):
        ax2.text(v + 1 if v >= 0 else v - 1, i, f'{v:.1f}%', 
                va='center', ha='left' if v >= 0 else 'right', fontsize=9)
    
    # 距离对比
    ax3 = axes[2]
    all_df = df.copy()
    x = np.arange(len(all_df))
    width = 0.35
    ax3.barh(x - width/2, all_df['native_distance_mean'], width, 
             label='Native Language', color='#3498DB', alpha=0.8)
    ax3.barh(x + width/2, all_df['en_distance_mean'], width, 
             label='English', color='#E74C3C', alpha=0.8)
    ax3.set_yticks(x)
    ax3.set_yticklabels(all_df['country'], fontsize=8)
    ax3.set_xlabel('Distance to IVS', fontsize=12)
    ax3.set_title('Native vs English Distance', fontsize=14, fontweight='bold')
    ax3.legend(loc='lower right')
    ax3.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure3_digital_orientalism_maps.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 图3已保存")


def plot_figure4_regions():
    """图4: 撒哈拉以南非洲和拉丁美洲"""
    print("绘制图4...")
    
    df = pd.read_csv(OUTPUT_DIR / 'figure4_distance_africa_latam.csv')
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # 撒哈拉以南非洲
    afr_df = df[df['region'] == 'Sub-Saharan Africa'].sort_values('advantage_mean')
    ax1 = axes[0]
    colors = ['#E74C3C' if x < 0 else '#2ECC71' for x in afr_df['advantage_mean']]
    ax1.barh(afr_df['country'], afr_df['advantage_mean'], color=colors, alpha=0.8)
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax1.set_xlabel('English Advantage (%)', fontsize=12)
    ax1.set_title('Sub-Saharan Africa\n(English Advantage)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    
    for i, v in enumerate(afr_df['advantage_mean']):
        ax1.text(v + 1 if v >= 0 else v - 1, i, f'{v:.1f}%', 
                va='center', ha='left' if v >= 0 else 'right', fontsize=9)
    
    # 拉丁美洲
    latam_df = df[df['region'] == 'Latin America'].sort_values('advantage_mean')
    ax2 = axes[1]
    colors = ['#E74C3C' if x < 0 else '#2ECC71' for x in latam_df['advantage_mean']]
    ax2.barh(latam_df['country'], latam_df['advantage_mean'], color=colors, alpha=0.8)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_xlabel('English Advantage (%)', fontsize=12)
    ax2.set_title('Latin America\n(English Advantage)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    for i, v in enumerate(latam_df['advantage_mean']):
        ax2.text(v + 1 if v >= 0 else v - 1, i, f'{v:.1f}%', 
                va='center', ha='left' if v >= 0 else 'right', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure4_africa_latam_maps.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 图4已保存")


if __name__ == '__main__':
    print("="*70)
    print("生成四张图（地图版）")
    print("="*70)
    
    plot_figure1_maps()
    plot_figure2_language()
    plot_figure3_orientalism()
    plot_figure4_regions()
    
    print("\n" + "="*70)
    print("✅ 所有图已生成完成!")
    print("="*70)
    print("\n⚠️ 图1需要shapefile才能画真正的世界地图")
    print("   当前使用散点图作为占位符")
