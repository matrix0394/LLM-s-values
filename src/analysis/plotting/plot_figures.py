#!/usr/bin/env python3
"""
四张图的绘图脚本
================
图1: 45个国家英语PC1/PC2 + WVS对照 (4个小图: PC1地图+对照, PC2地图+对照)
图2: 6种语言大模型自身价值观 (bar chart)
图3: Digital Orientalism - 中东和东亚distance地图
图4: 撒哈拉以南非洲和拉丁美洲distance地图
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 项目根目录
PROJECT_ROOT = Path("/Users/yxy/code/LLM's values/LLM's values")
OUTPUT_DIR = PROJECT_ROOT / 'results' / 'figures'

def plot_figure1():
    """图1: 45个国家英语PC1/PC2 + WVS对照"""
    print("绘制图1...")
    
    df = pd.read_csv(OUTPUT_DIR / 'figure1_data_45countries.csv')
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 按文化区域分组
    regions = df['cultural_region'].unique()
    colors = plt.cm.Set1(np.linspace(0, 1, len(regions)))
    region_colors = dict(zip(regions, colors))
    
    # PC1: LLM英语
    ax1 = axes[0, 0]
    for _, row in df.iterrows():
        color = region_colors.get(row['cultural_region'], 'gray')
        ax1.scatter(row['LLM_EN_PC1'], row['LLM_EN_PC2'], c=[color], s=80, alpha=0.7)
        ax1.annotate(row['country'], (row['LLM_EN_PC1'], row['LLM_EN_PC2']), 
                    fontsize=6, alpha=0.7)
    ax1.set_xlabel('PC1 (LLM English)', fontsize=12)
    ax1.set_ylabel('PC2', fontsize=12)
    ax1.set_title('LLM English Roleplay PC1 vs PC2', fontsize=14)
    ax1.grid(True, alpha=0.3)
    
    # PC1: WVS基准
    ax2 = axes[0, 1]
    for _, row in df.iterrows():
        color = region_colors.get(row['cultural_region'], 'gray')
        ax2.scatter(row['WVS_PC1'], row['WVS_PC2'], c=[color], s=80, alpha=0.7)
        ax2.annotate(row['country'], (row['WVS_PC1'], row['WVS_PC2']), 
                    fontsize=6, alpha=0.7)
    ax2.set_xlabel('PC1 (WVS)', fontsize=12)
    ax2.set_ylabel('PC2', fontsize=12)
    ax2.set_title('WVS Benchmark PC1 vs PC2', fontsize=14)
    ax2.grid(True, alpha=0.3)
    
    # PC2: LLM英语 (单独显示)
    ax3 = axes[1, 0]
    for _, row in df.iterrows():
        color = region_colors.get(row['cultural_region'], 'gray')
        ax3.scatter(row['LLM_EN_PC1'], row['LLM_EN_PC2'], c=[color], s=80, alpha=0.7)
    ax3.set_xlabel('PC1 (LLM English)', fontsize=12)
    ax3.set_ylabel('PC2', fontsize=12)
    ax3.set_title('LLM English Roleplay (colored by region)', fontsize=14)
    ax3.grid(True, alpha=0.3)
    
    # 添加图例
    patches = [mpatches.Patch(color=region_colors[r], label=r) for r in regions]
    ax3.legend(handles=patches, loc='best', fontsize=8)
    
    # PC2: WVS基准 (单独显示)
    ax4 = axes[1, 1]
    for _, row in df.iterrows():
        color = region_colors.get(row['cultural_region'], 'gray')
        ax4.scatter(row['WVS_PC1'], row['WVS_PC2'], c=[color], s=80, alpha=0.7)
    ax4.set_xlabel('PC1 (WVS)', fontsize=12)
    ax4.set_ylabel('PC2', fontsize=12)
    ax4.set_title('WVS Benchmark (colored by region)', fontsize=14)
    ax4.grid(True, alpha=0.3)
    ax4.legend(handles=patches, loc='best', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure1_45countries.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 图1已保存: {OUTPUT_DIR / 'figure1_45countries.png'}")


def plot_figure2():
    """图2: 6种语言大模型自身价值观 (bar chart)"""
    print("绘制图2...")
    
    df = pd.read_csv(OUTPUT_DIR / 'figure2_language_data.csv')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    languages = df['language'].tolist()
    language_names = df['language_name'].tolist()
    x = np.arange(len(languages))
    width = 0.35
    
    # PC1
    ax1 = axes[0]
    bars1 = ax1.bar(x - width/2, df['PC1_mean'], width, 
                    yerr=df['PC1_std'], capsize=5, 
                    color=['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f39c12', '#1abc9c'],
                    alpha=0.8)
    ax1.set_xlabel('Language', fontsize=12)
    ax1.set_ylabel('PC1 (Survival vs Self-Expression)', fontsize=12)
    ax1.set_title('LLM Intrinsic Values - PC1 by Language', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels(language_names, rotation=45, ha='right')
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # PC2
    ax2 = axes[1]
    bars2 = ax2.bar(x - width/2, df['PC2_mean'], width, 
                    yerr=df['PC2_std'], capsize=5,
                    color=['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f39c12', '#1abc9c'],
                    alpha=0.8)
    ax2.set_xlabel('Language', fontsize=12)
    ax2.set_ylabel('PC2 (Traditional vs Secular)', fontsize=12)
    ax2.set_title('LLM Intrinsic Values - PC2 by Language', fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels(language_names, rotation=45, ha='right')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure2_language_values.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 图2已保存: {OUTPUT_DIR / 'figure2_language_values.png'}")


def plot_figure3():
    """图3: Digital Orientalism - 中东和东亚distance地图"""
    print("绘制图3...")
    
    df = pd.read_csv(OUTPUT_DIR / 'figure3_distance_middleeast_eastasia.csv')
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 按region分组
    me_df = df[df['region'] == 'Middle East']
    ea_df = df[df['region'] == 'East Asia']
    
    # 中东 - native distance
    ax1 = axes[0]
    y_pos = np.arange(len(me_df))
    ax1.barh(y_pos, me_df['native_distance_mean'], color='#e74c3c', alpha=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(me_df['country'])
    ax1.set_xlabel('Distance to IVS', fontsize=12)
    ax1.set_title('Middle East - Native Language Distance', fontsize=14)
    ax1.grid(True, alpha=0.3, axis='x')
    
    # 中东 - 英语distance + advantage
    ax2 = axes[1]
    width = 0.35
    ax2.barh(y_pos - width/2, me_df['native_distance_mean'], width, 
             label='Native', color='#e74c3c', alpha=0.8)
    ax2.barh(y_pos + width/2, me_df['en_distance_mean'], width, 
             label='English', color='#3498db', alpha=0.8)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(me_df['country'])
    ax2.set_xlabel('Distance to IVS', fontsize=12)
    ax2.set_title('Middle East - Native vs English Distance', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 东亚
    ax3 = axes[2]
    y_pos = np.arange(len(ea_df))
    width = 0.35
    ax3.barh(y_pos - width/2, ea_df['native_distance_mean'], width, 
             label='Native', color='#e74c3c', alpha=0.8)
    ax3.barh(y_pos + width/2, ea_df['en_distance_mean'], width, 
             label='English', color='#3498db', alpha=0.8)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(ea_df['country'])
    ax3.set_xlabel('Distance to IVS', fontsize=12)
    ax3.set_title('East Asia - Native vs English Distance', fontsize=14)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure3_digital_orientalism.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 图3已保存: {OUTPUT_DIR / 'figure3_digital_orientalism.png'}")


def plot_figure4():
    """图4: 撒哈拉以南非洲和拉丁美洲distance地图"""
    print("绘制图4...")
    
    df = pd.read_csv(OUTPUT_DIR / 'figure4_distance_africa_latam.csv')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    
    # 撒哈拉以南非洲
    afr_df = df[df['region'] == 'Sub-Saharan Africa']
    ax1 = axes[0]
    y_pos = np.arange(len(afr_df))
    width = 0.35
    ax1.barh(y_pos - width/2, afr_df['native_distance_mean'], width, 
             label='Native', color='#e74c3c', alpha=0.8)
    ax1.barh(y_pos + width/2, afr_df['en_distance_mean'], width, 
             label='English', color='#3498db', alpha=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(afr_df['country'])
    ax1.set_xlabel('Distance to IVS', fontsize=12)
    ax1.set_title('Sub-Saharan Africa - Native vs English', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='x')
    
    # 拉丁美洲
    latam_df = df[df['region'] == 'Latin America']
    ax2 = axes[1]
    y_pos = np.arange(len(latam_df))
    ax2.barh(y_pos - width/2, latam_df['native_distance_mean'], width, 
             label='Native', color='#e74c3c', alpha=0.8)
    ax2.barh(y_pos + width/2, latam_df['en_distance_mean'], width, 
             label='English', color='#3498db', alpha=0.8)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(latam_df['country'])
    ax2.set_xlabel('Distance to IVS', fontsize=12)
    ax2.set_title('Latin America - Native vs English', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure4_africa_latam.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 图4已保存: {OUTPUT_DIR / 'figure4_africa_latam.png'}")


if __name__ == '__main__':
    print("="*70)
    print("生成四张图")
    print("="*70)
    
    plot_figure1()
    plot_figure2()
    plot_figure3()
    plot_figure4()
    
    print("\n" + "="*70)
    print("✅ 所有图已生成完成!")
    print("="*70)
