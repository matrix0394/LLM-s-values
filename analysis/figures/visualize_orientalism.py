#!/usr/bin/env python3
"""
生成"他者理论/东方主义"验证相关图表 - 更新版
使用CSV/JSON格式数据，兼容最新numpy版本

理论背景：
- 他者理论（The Other）：LLM对非英语国家的刻板印象
- 东方主义：西方视角下对东方的简化和刻板化
- 发现：英语优势在东亚地区最强，尤其是港台澳
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from pathlib import Path
from scipy import stats

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 输出目录
output_dir = Path('results/analysis/orientalism_analysis')
output_dir.mkdir(parents=True, exist_ok=True)

def load_latest_data():
    """加载已计算好的Stage0 vs Stage3分析结果"""
    print("=" * 80)
    print("加载Stage0 vs Stage3分析结果...")
    print("=" * 80)
    
    stage0_vs_stage3_dir = Path('results/analysis/stage0_vs_stage3')
    
    if not stage0_vs_stage3_dir.exists():
        print("⚠️ 未找到 stage0_vs_stage3 分析结果")
        print("请先运行: python analysis/stage0_vs_stage3_distance.py")
        raise FileNotFoundError("请先运行 stage0_vs_stage3_distance.py 生成数据")
    
    # 1. 加载详细距离数据
    distances_file = stage0_vs_stage3_dir / 'distances_detailed.csv'
    if distances_file.exists():
        results_df = pd.read_csv(distances_file)
    else:
        distances_file = stage0_vs_stage3_dir / 'distances_detailed.xlsx'
        results_df = pd.read_excel(distances_file)
    print(f"✅ 加载距离数据: {len(results_df)} 行")
    
    # 2. 加载英语优势数据
    advantage_file = stage0_vs_stage3_dir / 'english_advantage_average.csv'
    if advantage_file.exists():
        advantage_df = pd.read_csv(advantage_file)
    else:
        advantage_file = stage0_vs_stage3_dir / 'english_advantage_average.xlsx'
        advantage_df = pd.read_excel(advantage_file)
    print(f"✅ 加载英语优势数据: {len(advantage_df)} 行")
    
    return results_df, advantage_df

def load_country_regions():
    """加载国家文化区域映射"""
    with open('config/country_codes.json', 'r', encoding='utf-8') as f:
        country_codes = json.load(f)
    
    country_to_region = {item['Country']: item.get('Cultural Region', 'Other') 
                        for item in country_codes}
    country_to_islamic = {item['Country']: item.get('Islamic', False) 
                         for item in country_codes}
    
    return country_to_region, country_to_islamic

def create_east_asia_complete_chart(advantage_df):
    """图表1: 东亚完整梯度（包括日韩）"""
    print("\n生成图表1: 东亚完整梯度...")
    
    east_asian_keywords = ['Hong Kong', 'Singapore', 'China', 'Taiwan', 'Macao', 'Japan', 'Korea']
    
    ea_data = advantage_df[advantage_df['country'].str.contains('|'.join(east_asian_keywords), case=False, na=False)].copy()
    ea_data = ea_data.sort_values('english_advantage', ascending=False)
    
    if len(ea_data) == 0:
        print("⚠️ 没有东亚数据")
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    labels = []
    for _, row in ea_data.iterrows():
        country_short = row['country'][:25]
        lang_short = row['native_language']
        labels.append(f"{country_short}\n({lang_short})")
    
    colors = ['#E74C3C' if x > 20 else '#F39C12' if x > 10 else '#27AE60' if x > 0 else '#3498DB'
              for x in ea_data['english_advantage']]
    
    bars = ax.barh(range(len(ea_data)), ea_data['english_advantage'], 
                   color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_yticks(range(len(ea_data)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('英语优势 (%)', fontsize=12, fontweight='bold')
    ax.set_title('东亚完整梯度：英语 vs 母语模仿效果\n(包括日韩，所有模型平均)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()
    
    for i, (bar, val) in enumerate(zip(bars, ea_data['english_advantage'])):
        ax.text(val + 1, i, f'{val:+.1f}%', va='center', fontsize=10, fontweight='bold')
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#E74C3C', alpha=0.8, label='强英语优势 (>20%)'),
        Patch(facecolor='#F39C12', alpha=0.8, label='中等英语优势 (10-20%)'),
        Patch(facecolor='#27AE60', alpha=0.8, label='弱英语优势 (0-10%)'),
        Patch(facecolor='#3498DB', alpha=0.8, label='母语优势 (<0%)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'east_asia_complete_gradient.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: east_asia_complete_gradient.png")
    plt.close()

def create_cultural_regions_chart(advantage_df):
    """图表2: 各文化区域的语言效应"""
    print("\n生成图表2: 各文化区域的语言效应...")
    
    # 直接使用CSV中已有的cultural_region列，而不是重新映射
    advantage_df_with_region = advantage_df.copy()
    advantage_df_with_region = advantage_df_with_region[advantage_df_with_region['cultural_region'].notna()]
    advantage_df_with_region = advantage_df_with_region[advantage_df_with_region['cultural_region'] != 'Other']
    
    if len(advantage_df_with_region) == 0:
        print("⚠️ 没有文化区域数据")
        return
    
    region_stats = advantage_df_with_region.groupby('cultural_region').agg({
        'english_advantage': ['mean', 'std', 'count']
    }).reset_index()
    region_stats.columns = ['region', 'mean', 'std', 'count']
    region_stats['se'] = region_stats['std'] / np.sqrt(region_stats['count'])
    region_stats = region_stats.sort_values('mean', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#E74C3C' if x > 0 else '#27AE60' for x in region_stats['mean']]
    bars = ax.barh(range(len(region_stats)), region_stats['mean'], 
                  xerr=region_stats['se'] * 1.96,  # 95% CI
                  color=colors, alpha=0.75, edgecolor='black', linewidth=1.5, capsize=3)
    
    ax.set_yticks(range(len(region_stats)))
    ax.set_yticklabels(region_stats['region'], fontsize=11)
    ax.set_xlabel('语言效应 (英语优势, %)', fontsize=12, fontweight='bold')
    ax.set_title('地理梯度验证：各文化区域的语言效应\n(正值=英语更优, 负值=母语更优, 含95%置信区间)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.axvline(0, color='black', linestyle='-', linewidth=2)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()
    
    for i, row in enumerate(region_stats.itertuples()):
        x_pos = row.mean + (3 if row.mean > 0 else -3)
        ha = 'left' if row.mean > 0 else 'right'
        ax.text(x_pos, i, f'{row.mean:+.1f}% (n={int(row.count)})',
               va='center', ha=ha, fontsize=10, fontweight='bold')
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#E74C3C', alpha=0.75, label='英语优势', edgecolor='black'),
        Patch(facecolor='#27AE60', alpha=0.75, label='母语优势', edgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cultural_regions_language_effect.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: cultural_regions_language_effect.png")
    plt.close()

def create_orientalism_theory_chart(advantage_df):
    """图表3: 他者理论验证 - 英语优势分布"""
    print("\n生成图表3: 他者理论验证...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 左图：英语优势分布直方图
    ax1.hist(advantage_df['english_advantage'], bins=30, 
            edgecolor='black', alpha=0.7, color='#3498DB')
    ax1.axvline(0, color='red', linestyle='--', linewidth=2, label='零点')
    ax1.axvline(advantage_df['english_advantage'].mean(), 
               color='green', linestyle='--', linewidth=2,
               label=f'平均值: {advantage_df["english_advantage"].mean():.1f}%')
    ax1.set_xlabel('英语优势 (%)', fontsize=12)
    ax1.set_ylabel('频数', fontsize=12)
    ax1.set_title('英语优势分布\n(正值=英语更好, 负值=母语更好)', 
                 fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    # 右图：Top 10 vs Bottom 10
    sorted_adv = advantage_df.sort_values('english_advantage', ascending=False)
    top10 = sorted_adv.head(10)
    bottom10 = sorted_adv.tail(10)
    
    combined = pd.concat([top10, bottom10])
    labels = [f"{row['country'][:15]}\n({row['native_language']})" 
             for _, row in combined.iterrows()]
    
    colors = ['#E74C3C' if x > 0 else '#27AE60' for x in combined['english_advantage']]
    
    bars = ax2.barh(range(len(combined)), combined['english_advantage'],
                   color=colors, alpha=0.7, edgecolor='black')
    ax2.set_yticks(range(len(combined)))
    ax2.set_yticklabels(labels, fontsize=8)
    ax2.set_xlabel('英语优势 (%)', fontsize=12)
    ax2.set_title('Top 10 英语优势 vs Bottom 10\n(他者理论验证)', 
                 fontsize=13, fontweight='bold')
    ax2.axvline(0, color='black', linestyle='-', linewidth=1)
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()
    
    for i, (bar, val) in enumerate(zip(bars, combined['english_advantage'])):
        ax2.text(val + (2 if val > 0 else -2), i, f'{val:+.1f}%',
                va='center', ha='left' if val > 0 else 'right',
                fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'orientalism_theory_validation.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: orientalism_theory_validation.png")
    plt.close()

def create_islamic_vs_western_chart(advantage_df):
    """图表4: 伊斯兰 vs 西方国家对比"""
    print("\n生成图表4: 伊斯兰 vs 西方国家对比...")
    
    country_to_region, country_to_islamic = load_country_regions()
    
    advantage_df_copy = advantage_df.copy()
    advantage_df_copy['cultural_region'] = advantage_df_copy['country'].map(country_to_region)
    advantage_df_copy['is_islamic'] = advantage_df_copy['country'].map(country_to_islamic)
    
    # 伊斯兰国家
    islamic_data = advantage_df_copy[advantage_df_copy['is_islamic'] == True]
    
    # 西方国家（Protestant Europe + Catholic Europe）
    western_regions = ['Protestant Europe', 'Catholic Europe']
    western_data = advantage_df_copy[advantage_df_copy['cultural_region'].isin(western_regions)]
    
    if len(islamic_data) == 0 or len(western_data) == 0:
        print("⚠️ 数据不足")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左图：伊斯兰国家
    islamic_sorted = islamic_data.sort_values('english_advantage', ascending=False)
    colors1 = ['#E74C3C' if x > 0 else '#27AE60' for x in islamic_sorted['english_advantage']]
    bars1 = ax1.barh(range(len(islamic_sorted)), islamic_sorted['english_advantage'],
                    color=colors1, alpha=0.7, edgecolor='black')
    ax1.set_yticks(range(len(islamic_sorted)))
    ax1.set_yticklabels([f"{row['country'][:20]}\n({row['native_language']})" 
                        for _, row in islamic_sorted.iterrows()], fontsize=9)
    ax1.set_xlabel('英语优势 (%)', fontsize=12)
    ax1.set_title(f'伊斯兰国家 (n={len(islamic_sorted)})\n平均: {islamic_sorted["english_advantage"].mean():+.1f}%', 
                 fontsize=13, fontweight='bold')
    ax1.axvline(0, color='black', linestyle='-', linewidth=1)
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()
    
    # 右图：西方国家
    western_sorted = western_data.sort_values('english_advantage', ascending=False)
    colors2 = ['#E74C3C' if x > 0 else '#27AE60' for x in western_sorted['english_advantage']]
    bars2 = ax2.barh(range(len(western_sorted)), western_sorted['english_advantage'],
                    color=colors2, alpha=0.7, edgecolor='black')
    ax2.set_yticks(range(len(western_sorted)))
    ax2.set_yticklabels([f"{row['country'][:20]}\n({row['native_language']})" 
                        for _, row in western_sorted.iterrows()], fontsize=9)
    ax2.set_xlabel('英语优势 (%)', fontsize=12)
    ax2.set_title(f'西欧国家 (n={len(western_sorted)})\n平均: {western_sorted["english_advantage"].mean():+.1f}%', 
                 fontsize=13, fontweight='bold')
    ax2.axvline(0, color='black', linestyle='-', linewidth=1)
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()
    
    # 统计检验
    t_stat, p_value = stats.ttest_ind(islamic_sorted['english_advantage'], 
                                       western_sorted['english_advantage'])
    cohen_d = (islamic_sorted['english_advantage'].mean() - western_sorted['english_advantage'].mean()) / \
              np.sqrt((islamic_sorted['english_advantage'].std()**2 + western_sorted['english_advantage'].std()**2) / 2)
    
    plt.suptitle(f'伊斯兰 vs 西欧国家英语优势对比\nt={t_stat:.2f}, p={p_value:.4f}, Cohen\'s d={cohen_d:.2f}', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'islamic_vs_western_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: islamic_vs_western_comparison.png")
    plt.close()
    
    # 打印统计结果
    print(f"\n   统计检验结果:")
    print(f"   伊斯兰国家平均: {islamic_sorted['english_advantage'].mean():+.1f}%")
    print(f"   西欧国家平均: {western_sorted['english_advantage'].mean():+.1f}%")
    print(f"   t = {t_stat:.2f}, p = {p_value:.4f}")
    print(f"   Cohen's d = {cohen_d:.2f}")

def create_geographic_gradient_chart(advantage_df):
    """图表5: 地理梯度趋势"""
    print("\n生成图表5: 地理梯度趋势...")
    
    # 直接使用CSV中已有的cultural_region列
    advantage_df_with_region = advantage_df.copy()
    
    # 定义文化区域的地理梯度顺序
    region_order = [
        'Protestant Europe',
        'Catholic Europe', 
        'Orthodox Europe',
        'Latin America',
        'African-Islamic',
        'West & South Asia',
        'Confucian'
    ]
    
    regions = []
    advantages = []
    counts = []
    
    for region in region_order:
        region_data = advantage_df_with_region[advantage_df_with_region['cultural_region'] == region]
        if len(region_data) > 0:
            mean_adv = region_data['english_advantage'].mean()
            regions.append(region)
            advantages.append(mean_adv)
            counts.append(len(region_data))
    
    if len(regions) == 0:
        print("⚠️ 没有梯度数据")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x_pos = range(len(regions))
    line = ax.plot(x_pos, advantages, marker='o', markersize=12, linewidth=3,
                   color='#3498DB', markerfacecolor='#3498DB', markeredgecolor='black',
                   markeredgewidth=2, label='语言效应趋势')
    
    ax.axhline(0, color='black', linestyle='-', linewidth=2, alpha=0.5)
    
    ax.fill_between(x_pos, 0, advantages, where=[a >= 0 for a in advantages],
                    color='#E74C3C', alpha=0.2, label='英语优势区')
    ax.fill_between(x_pos, 0, advantages, where=[a < 0 for a in advantages],
                    color='#27AE60', alpha=0.2, label='母语优势区')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(regions, fontsize=11, rotation=15, ha='right')
    ax.set_ylabel('语言效应 (英语优势, %)', fontsize=13, fontweight='bold')
    ax.set_xlabel('文化区域（按与西方的距离排序）', fontsize=13, fontweight='bold')
    ax.set_title('从近到远：英语效应的文化梯度', fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (region, adv, count) in enumerate(zip(regions, advantages, counts)):
        y_offset = 3 if adv > 0 else -3
        va = 'bottom' if adv > 0 else 'top'
        ax.text(i, adv + y_offset, f'{adv:+.1f}%\n(n={count})',
               ha='center', va=va, fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    ax.text(0.02, 0.98, '← 更接近西方', transform=ax.transAxes,
           fontsize=10, va='top', ha='left', style='italic', color='gray')
    ax.text(0.98, 0.98, '更远离西方 →', transform=ax.transAxes,
           fontsize=10, va='top', ha='right', style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'geographic_gradient_trend.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: geographic_gradient_trend.png")
    plt.close()


def create_language_family_chart(advantage_df):
    """图表6: 语系的英语优势分布（使用正确的语言学分类）"""
    print("\n生成图表6: 语系的英语优势分布...")
    
    # 定义语言到语系的映射（基于语言学标准）
    language_to_family = {
        'ar': '闪米特语系',           # Semitic (亚非语系)
        'zh-cn': '汉藏语系',          # Sino-Tibetan
        'zh-tw': '汉藏语系',          # Sino-Tibetan
        'zh-hk': '汉藏语系',          # Sino-Tibetan
        'ja': '日本语系',             # Japonic (孤立语言)
        'ko': '韩语系',               # Koreanic (孤立语言)
        'ru': '斯拉夫语系',           # Slavic (印欧语系)
        'es': '罗曼语系',             # Romance (印欧语系)
        'fr': '罗曼语系',             # Romance (印欧语系)
        'it': '罗曼语系',             # Romance (印欧语系)
        'pt': '罗曼语系',             # Romance (印欧语系)
        'de': '日耳曼语系',           # Germanic (印欧语系)
    }
    
    # 添加语系列
    advantage_df_copy = advantage_df.copy()
    advantage_df_copy['language_family'] = advantage_df_copy['native_language'].map(language_to_family)
    
    # 过滤掉没有语系映射的数据
    advantage_df_with_family = advantage_df_copy[advantage_df_copy['language_family'].notna()]
    
    if len(advantage_df_with_family) == 0:
        print("⚠️ 没有语系数据")
        return
    
    # 按语系分组统计
    family_stats = advantage_df_with_family.groupby('language_family').agg({
        'english_advantage': ['mean', 'std', 'count']
    }).reset_index()
    family_stats.columns = ['family', 'mean', 'std', 'count']
    family_stats['se'] = family_stats['std'] / np.sqrt(family_stats['count'])
    family_stats = family_stats.sort_values('mean', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#E74C3C' if x > 0 else '#27AE60' for x in family_stats['mean']]
    bars = ax.barh(range(len(family_stats)), family_stats['mean'], 
                  xerr=family_stats['se'] * 1.96,  # 95% CI
                  color=colors, alpha=0.75, edgecolor='black', linewidth=1.5, capsize=5)
    
    ax.set_yticks(range(len(family_stats)))
    ax.set_yticklabels(family_stats['family'], fontsize=12)
    ax.set_xlabel('语言效应 (英语优势, %)', fontsize=13, fontweight='bold')
    ax.set_title('语系差异：各语系的英语优势分布\n(正值=英语更优, 负值=官方语言更优, 含95%置信区间)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.axvline(0, color='black', linestyle='-', linewidth=2)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()
    
    for i, row in enumerate(family_stats.itertuples()):
        x_pos = row.mean + (3 if row.mean > 0 else -3)
        ha = 'left' if row.mean > 0 else 'right'
        ax.text(x_pos, i, f'{row.mean:+.1f}% (n={int(row.count)})',
               va='center', ha=ha, fontsize=11, fontweight='bold')
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#E74C3C', alpha=0.75, label='英语优势', edgecolor='black'),
        Patch(facecolor='#27AE60', alpha=0.75, label='官方语言优势', edgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'language_family_effect.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: language_family_effect.png")
    plt.close()

def print_summary_statistics(advantage_df):
    """打印统计摘要"""
    print("\n" + "=" * 80)
    print("统计摘要")
    print("=" * 80)
    
    print(f"总国家-语言组合数: {len(advantage_df)}")
    print(f"平均英语优势: {advantage_df['english_advantage'].mean():+.1f}%")
    print(f"英语优势标准差: {advantage_df['english_advantage'].std():.1f}%")
    
    max_idx = advantage_df['english_advantage'].idxmax()
    min_idx = advantage_df['english_advantage'].idxmin()
    
    print(f"\n英语优势最强: {advantage_df.loc[max_idx, 'country']} "
          f"({advantage_df.loc[max_idx, 'native_language']}): "
          f"{advantage_df['english_advantage'].max():+.1f}%")
    print(f"母语优势最强: {advantage_df.loc[min_idx, 'country']} "
          f"({advantage_df.loc[min_idx, 'native_language']}): "
          f"{advantage_df['english_advantage'].min():+.1f}%")
    
    # 统计正负比例
    positive = (advantage_df['english_advantage'] > 0).sum()
    negative = (advantage_df['english_advantage'] < 0).sum()
    print(f"\n英语优势国家数: {positive} ({positive/len(advantage_df)*100:.1f}%)")
    print(f"母语优势国家数: {negative} ({negative/len(advantage_df)*100:.1f}%)")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("东方主义/他者理论可视化分析（更新版）")
    print("使用CSV/JSON格式数据")
    print("=" * 80)
    
    # 加载数据
    results_df, advantage_df = load_latest_data()
    
    # 生成所有图表
    create_east_asia_complete_chart(advantage_df)
    create_cultural_regions_chart(advantage_df)
    create_orientalism_theory_chart(advantage_df)
    create_islamic_vs_western_chart(advantage_df)
    create_geographic_gradient_chart(advantage_df)
    create_language_family_chart(advantage_df)  # 新增：语系图表
    
    # 打印统计摘要
    print_summary_statistics(advantage_df)
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")
    print("=" * 80)


if __name__ == '__main__':
    main()
