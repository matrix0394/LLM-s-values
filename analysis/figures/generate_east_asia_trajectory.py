#!/usr/bin/env python3
"""
生成东亚地区文化坐标轨迹图
- 显示每个国家的真实坐标位置
- 显示每种语言所有模型平均下来的坐标位置
- 用虚线连接真实位置和模拟位置，并标注语言
- 同一国家使用统一颜色，不同点形状
- 浅色显示所有模型所有语言的原始数据点
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 输出目录
output_dir = Path('results/analysis/orientalism_analysis')
output_dir.mkdir(parents=True, exist_ok=True)

def load_data():
    """加载详细距离数据"""
    distances_file = Path('results/analysis/stage0_vs_stage3/distances_detailed.csv')
    df = pd.read_csv(distances_file)
    print(f"✅ 加载数据: {len(df)} 行")
    return df

def remove_outliers(df, columns=['llm_PC1', 'llm_PC2'], n_std=2.5):
    """
    移除极端值（基于标准差）
    n_std: 超过多少个标准差视为极端值
    """
    df_clean = df.copy()
    for col in columns:
        mean = df_clean[col].mean()
        std = df_clean[col].std()
        lower = mean - n_std * std
        upper = mean + n_std * std
        before_count = len(df_clean)
        df_clean = df_clean[(df_clean[col] >= lower) & (df_clean[col] <= upper)]
        after_count = len(df_clean)
        if before_count != after_count:
            print(f"   移除 {col} 极端值: {before_count - after_count} 个")
    return df_clean


def create_east_asia_trajectory_chart(df):
    """生成东亚地区轨迹图"""
    print("\n生成东亚地区轨迹图...")
    
    # 东亚国家关键词
    east_asian_countries = {
        'Hong Kong': '香港',
        'Taiwan, Province of China': '台湾',
        'China': '中国大陆',
        'Japan': '日本',
        'Korea, Republic of': '韩国',
        'Macao': '澳门'
    }
    
    # 筛选东亚数据
    ea_data = df[df['country'].isin(east_asian_countries.keys())].copy()
    
    # 移除极端值（超过2.5个标准差的数据点）
    print(f"   原始数据: {len(ea_data)} 行")
    ea_data = remove_outliers(ea_data, columns=['llm_PC1', 'llm_PC2'], n_std=2.5)
    print(f"   过滤后数据: {len(ea_data)} 行")
    
    if len(ea_data) == 0:
        print("⚠️ 没有东亚数据")
        return
    
    print(f"   东亚数据: {len(ea_data)} 行")
    print(f"   国家: {ea_data['country'].unique()}")
    print(f"   语言: {ea_data['language'].unique()}")
    
    # 定义颜色方案（每个国家一个颜色）
    country_colors = {
        'Hong Kong': '#E74C3C',      # 红色
        'Taiwan, Province of China': '#F39C12',  # 橙色
        'China': '#E74C3C',          # 红色（与香港同色系）
        'Japan': '#3498DB',          # 蓝色
        'Korea, Republic of': '#9B59B6',  # 紫色
        'Macao': '#1ABC9C'           # 青色
    }
    
    # 语言标记形状
    language_markers = {
        'zh-cn': 's',    # 方形 - 简体中文
        'zh-tw': '^',    # 三角形 - 繁体中文
        'zh-hk': 'v',    # 倒三角 - 粤语
        'ja': 'D',       # 菱形 - 日语
        'ko': 'p',       # 五角星 - 韩语
        'pt': 'h',       # 六角形 - 葡萄牙语
        'en': 'o',       # 圆形 - 英语
    }
    
    language_names = {
        'zh-cn': '简体中文',
        'zh-tw': '繁体中文', 
        'zh-hk': '粤语',
        'ja': '日语',
        'ko': '韩语',
        'pt': '葡萄牙语',
        'en': '英语'
    }
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # 1. 首先绘制所有模型的浅色散点（背景层）
    for country in east_asian_countries.keys():
        country_data = ea_data[ea_data['country'] == country]
        if len(country_data) == 0:
            continue
        
        color = country_colors.get(country, '#95A5A6')
        # 浅色版本（alpha=0.15）
        ax.scatter(country_data['llm_PC1'], country_data['llm_PC2'],
                  c=color, alpha=0.15, s=30, edgecolors='none',
                  label=None)
    
    # 2. 绘制真实坐标点（大星形）
    real_coords = ea_data.groupby('country')[['real_PC1', 'real_PC2']].first().reset_index()
    
    for _, row in real_coords.iterrows():
        country = row['country']
        color = country_colors.get(country, '#95A5A6')
        chinese_name = east_asian_countries.get(country, country)
        
        ax.scatter(row['real_PC1'], row['real_PC2'],
                  c=color, s=300, marker='*', edgecolors='black', linewidths=1.5,
                  zorder=10, label=f'{chinese_name} (真实)')
        
        # 标注国家名称
        ax.annotate(chinese_name, (row['real_PC1'], row['real_PC2']),
                   xytext=(8, 8), textcoords='offset points',
                   fontsize=11, fontweight='bold', color=color,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # 3. 计算每个国家每种语言的平均坐标，并绘制连线
    for country in east_asian_countries.keys():
        country_data = ea_data[ea_data['country'] == country]
        if len(country_data) == 0:
            continue
        
        color = country_colors.get(country, '#95A5A6')
        real_pc1 = country_data['real_PC1'].iloc[0]
        real_pc2 = country_data['real_PC2'].iloc[0]
        
        # 按语言分组计算平均
        lang_avg = country_data.groupby('language').agg({
            'llm_PC1': 'mean',
            'llm_PC2': 'mean'
        }).reset_index()
        
        for _, lang_row in lang_avg.iterrows():
            lang = lang_row['language']
            llm_pc1 = lang_row['llm_PC1']
            llm_pc2 = lang_row['llm_PC2']
            
            marker = language_markers.get(lang, 'o')
            lang_name = language_names.get(lang, lang)
            
            # 绘制虚线连接
            ax.plot([real_pc1, llm_pc1], [real_pc2, llm_pc2],
                   linestyle='--', color=color, alpha=0.6, linewidth=1.5)
            
            # 绘制语言平均点
            ax.scatter(llm_pc1, llm_pc2,
                      c=color, s=120, marker=marker, edgecolors='black', linewidths=1,
                      zorder=8)
            
            # 直接在语言坐标点旁边标注语言名称
            ax.annotate(lang_name, (llm_pc1, llm_pc2),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, color=color, fontweight='bold',
                       ha='left', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    
    # 设置坐标轴
    ax.set_xlabel('PC1: 生存 ← → 自我表达', fontsize=13, fontweight='bold')
    ax.set_ylabel('PC2: 传统 ← → 世俗理性', fontsize=13, fontweight='bold')
    ax.set_title('东亚地区文化坐标轨迹：真实位置 vs LLM模拟位置\n(★=真实坐标, 其他形状=各语言模型平均, 浅色点=所有模型原始数据)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # 设置固定的坐标范围
    ax.set_xlim(-1, 3)
    ax.set_ylim(0, 3)
    
    # 添加参考线
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.axvline(0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 创建图例
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    
    # 国家颜色图例
    country_legend = [Line2D([0], [0], marker='*', color='w', markerfacecolor=color, 
                             markersize=15, markeredgecolor='black', label=f'{east_asian_countries[country]}')
                     for country, color in country_colors.items() if country in ea_data['country'].unique()]
    
    # 语言形状图例
    lang_legend = [Line2D([0], [0], marker=marker, color='w', markerfacecolor='gray',
                          markersize=10, markeredgecolor='black', label=f'{language_names[lang]}')
                  for lang, marker in language_markers.items() if lang in ea_data['language'].unique()]
    
    # 添加图例
    legend1 = ax.legend(handles=country_legend, loc='upper left', title='国家/地区', 
                       fontsize=9, title_fontsize=10, framealpha=0.9)
    ax.add_artist(legend1)
    ax.legend(handles=lang_legend, loc='lower right', title='语言', 
             fontsize=9, title_fontsize=10, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'east_asia_trajectory.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: east_asia_trajectory.png")
    plt.close()


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("生成东亚地区文化坐标轨迹图")
    print("=" * 80)
    
    # 加载数据
    df = load_data()
    
    # 生成轨迹图
    create_east_asia_trajectory_chart(df)
    
    print(f"\n✅ 图表已保存到: {output_dir}")
    print("=" * 80)


if __name__ == '__main__':
    main()
