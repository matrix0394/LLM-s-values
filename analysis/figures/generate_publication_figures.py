"""
生成发表级别的可视化图表
针对 Nature Human Behaviour / PNAS 风格
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import seaborn as sns
from pathlib import Path
from scipy import stats

# 设置发表级别的图表风格
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# 颜色方案 (Nature风格)
COLORS = {
    'islamic': '#E64B35',      # 红色
    'slavic': '#4DBBD5',       # 青色
    'latin': '#00A087',        # 绿色
    'western_eu': '#3C5488',   # 深蓝
    'east_asia': '#F39B7F',    # 橙色
    'english_native': '#8491B4', # 灰蓝
    'english': '#00A087',
    'native': '#E64B35',
}

# 加载数据
df = pd.read_csv('results/roleplay_multilingual/cultural_distance_analysis.csv')
bad_models = ['qwen3-1.7b', 'llama-3.2-3b-instruct']
df = df[~df['model'].isin(bad_models)]
non_english = df[~df['is_english_native_country']]

# 创建输出目录
output_dir = Path('results/figures')
output_dir.mkdir(parents=True, exist_ok=True)

print("生成发表级别图表...")

# ============================================================
# Figure 1: 主效应图 - 按文化区域的英语优势
# ============================================================
def create_figure1():
    """Figure 1: English advantage by cultural region"""
    
    # 定义文化区域
    cultural_regions = {
        'Islamic/Arab': ['Algeria', 'Palestine', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
                         'Libya', 'Morocco', 'Qatar', 'Tunisia', 'Egypt', 'Yemen'],
        'Orthodox': ['Russian Federation', 'Belarus', 'Kazakhstan', 'Kyrgyzstan'],
        'Latin America': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador',
                          'Guatemala', 'Haiti', 'Mexico', 'Nicaragua', 'Peru', 'Uruguay', 'Venezuela'],
        'Western Europe': ['Austria', 'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg',
                           'Portugal', 'Spain', 'Switzerland'],
        'East Asia': ['China', 'Japan', 'Korea, Republic of', 'Macao']
    }
    
    region_colors = {
        'Islamic/Arab': COLORS['islamic'],
        'Orthodox': COLORS['slavic'],
        'Latin America': COLORS['latin'],
        'Western Europe': COLORS['western_eu'],
        'East Asia': COLORS['east_asia']
    }
    
    # 计算每个国家的英语优势
    country_data = []
    for country in non_english['country'].unique():
        c_data = non_english[non_english['country'] == country]
        native_lang = c_data['native_language'].iloc[0]
        
        native_dist = c_data[c_data['language'] == native_lang]['cultural_distance'].mean()
        english_dist = c_data[c_data['is_english']]['cultural_distance'].mean()
        
        if pd.notna(native_dist) and pd.notna(english_dist) and native_dist > 0:
            adv = (native_dist - english_dist) / native_dist * 100
            
            # 找到所属区域
            region = 'Other'
            for r, countries in cultural_regions.items():
                if country in countries:
                    region = r
                    break
            
            if region != 'Other':
                country_data.append({
                    'country': country,
                    'region': region,
                    'english_advantage': adv
                })
    
    country_df = pd.DataFrame(country_data)
    
    # 计算区域统计
    region_stats = country_df.groupby('region')['english_advantage'].agg(['mean', 'std', 'count']).reset_index()
    region_stats['se'] = region_stats['std'] / np.sqrt(region_stats['count'])
    
    # 按均值排序
    region_order = ['Islamic/Arab', 'Orthodox', 'East Asia', 'Latin America', 'Western Europe']
    region_stats['order'] = region_stats['region'].map({r: i for i, r in enumerate(region_order)})
    region_stats = region_stats.sort_values('order')
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x = np.arange(len(region_stats))
    bars = ax.bar(x, region_stats['mean'], 
                  yerr=region_stats['se'] * 1.96,  # 95% CI
                  capsize=4,
                  color=[region_colors[r] for r in region_stats['region']],
                  edgecolor='black',
                  linewidth=0.5,
                  alpha=0.85)
    
    # 添加零线
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    # 添加显著性标记
    for i, (_, row) in enumerate(region_stats.iterrows()):
        # 单样本t检验
        region_data = country_df[country_df['region'] == row['region']]['english_advantage']
        t_stat, p_value = stats.ttest_1samp(region_data, 0)
        
        y_pos = row['mean'] + row['se'] * 1.96 + 2 if row['mean'] > 0 else row['mean'] - row['se'] * 1.96 - 4
        
        if p_value < 0.001:
            ax.text(i, y_pos, '***', ha='center', va='bottom' if row['mean'] > 0 else 'top', fontsize=12)
        elif p_value < 0.01:
            ax.text(i, y_pos, '**', ha='center', va='bottom' if row['mean'] > 0 else 'top', fontsize=12)
        elif p_value < 0.05:
            ax.text(i, y_pos, '*', ha='center', va='bottom' if row['mean'] > 0 else 'top', fontsize=12)
    
    ax.set_xticks(x)
    ax.set_xticklabels(region_stats['region'], rotation=15, ha='right')
    ax.set_ylabel('English Advantage (%)\n(positive = English better)')
    ax.set_xlabel('Cultural Region')
    ax.set_title('Language Effect on Cultural Roleplay Accuracy by Region', fontweight='bold', pad=15)
    
    # 添加注释
    ax.text(0.02, 0.98, 'Error bars: 95% CI\n*p<0.05, **p<0.01, ***p<0.001', 
            transform=ax.transAxes, fontsize=8, va='top', ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'fig1_english_advantage_by_region.png', dpi=300)
    plt.savefig(output_dir / 'fig1_english_advantage_by_region.pdf')
    print(f"✅ Figure 1 saved")
    plt.close()

# ============================================================
# Figure 2: 国家级别详细图 - 阿拉伯 vs 西欧对比
# ============================================================
def create_figure2():
    """Figure 2: Country-level comparison - Islamic vs Western Europe"""
    
    islamic_countries = ['Algeria', 'Palestine', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
                         'Libya', 'Morocco', 'Qatar', 'Tunisia', 'Egypt', 'Yemen']
    western_countries = ['Austria', 'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg',
                         'Portugal', 'Spain', 'Switzerland']
    
    # 计算每个国家的数据
    country_data = []
    for country in non_english['country'].unique():
        c_data = non_english[non_english['country'] == country]
        native_lang = c_data['native_language'].iloc[0]
        
        native_dist = c_data[c_data['language'] == native_lang]['cultural_distance'].mean()
        english_dist = c_data[c_data['is_english']]['cultural_distance'].mean()
        
        if pd.notna(native_dist) and pd.notna(english_dist) and native_dist > 0:
            adv = (native_dist - english_dist) / native_dist * 100
            
            if country in islamic_countries:
                group = 'Islamic/Arab'
            elif country in western_countries:
                group = 'Western Europe'
            else:
                continue
            
            country_data.append({
                'country': country,
                'group': group,
                'english_advantage': adv,
                'native_lang': native_lang
            })
    
    country_df = pd.DataFrame(country_data)
    
    # 创建图表
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    for idx, (group, color) in enumerate([('Islamic/Arab', COLORS['islamic']), 
                                           ('Western Europe', COLORS['western_eu'])]):
        ax = axes[idx]
        group_data = country_df[country_df['group'] == group].sort_values('english_advantage', ascending=True)
        
        y_pos = np.arange(len(group_data))
        bars = ax.barh(y_pos, group_data['english_advantage'], 
                       color=color, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # 颜色区分正负
        for bar, val in zip(bars, group_data['english_advantage']):
            if val < 0:
                bar.set_color(COLORS['western_eu'] if group == 'Islamic/Arab' else COLORS['islamic'])
        
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{row['country']} ({row['native_lang']})" 
                           for _, row in group_data.iterrows()], fontsize=9)
        ax.set_xlabel('English Advantage (%)')
        ax.set_title(f'{group}\n(n={len(group_data)} countries)', fontweight='bold')
        
        # 添加均值线
        mean_val = group_data['english_advantage'].mean()
        ax.axvline(x=mean_val, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(mean_val, len(group_data) - 0.5, f'Mean: {mean_val:+.1f}%', 
                color='red', fontsize=9, va='bottom', ha='center')
    
    plt.suptitle('English Advantage: Islamic/Arab vs Western European Countries', 
                 fontweight='bold', fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'fig2_islamic_vs_western_comparison.png', dpi=300)
    plt.savefig(output_dir / 'fig2_islamic_vs_western_comparison.pdf')
    print(f"✅ Figure 2 saved")
    plt.close()

# ============================================================
# Figure 3: 模型来源效应
# ============================================================
def create_figure3():
    """Figure 3: Model origin effect on Orientalism"""
    
    model_origin = {
        'US': ['claude-3-7-sonnet-20250219', 'claude-sonnet-4.5', 'gpt-4o', 'gpt-4o-mini', 
               'gpt-5.1', 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-3-pro-preview',
               'gemma-3-4b-it', 'llama-3.3-70b-instruct', 'grok-4.1-fast', 'phi-3-mini-128k-instruct'],
        'China': ['deepseek-chat', 'deepseek-chat-v3.1', 'qwen3-max', 'kimi-k2'],
        'EU': ['mistral-medium-3.1', 'mistral-nemo']
    }
    
    # 阿拉伯国家数据
    arabic_data = non_english[non_english['native_language'] == 'ar']
    
    origin_stats = []
    for origin, models in model_origin.items():
        origin_data = arabic_data[arabic_data['model'].isin(models)]
        
        native_dist = origin_data[origin_data['language'] == 'ar']['cultural_distance'].mean()
        english_dist = origin_data[origin_data['is_english']]['cultural_distance'].mean()
        
        if pd.notna(native_dist) and pd.notna(english_dist):
            adv = (native_dist - english_dist) / native_dist * 100
            origin_stats.append({
                'origin': origin,
                'native_dist': native_dist,
                'english_dist': english_dist,
                'english_advantage': adv,
                'n_models': len([m for m in models if m in arabic_data['model'].unique()])
            })
    
    origin_df = pd.DataFrame(origin_stats)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x = np.arange(len(origin_df))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, origin_df['native_dist'], width, 
                   label='Arabic', color=COLORS['islamic'], alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, origin_df['english_dist'], width, 
                   label='English', color=COLORS['english'], alpha=0.8, edgecolor='black')
    
    # 添加英语优势标注
    for i, (_, row) in enumerate(origin_df.iterrows()):
        y_max = max(row['native_dist'], row['english_dist'])
        ax.text(i, y_max + 0.15, f"+{row['english_advantage']:.1f}%", 
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='darkgreen')
    
    ax.set_xticks(x)
    ax.set_xticklabels([f"{row['origin']}\n(n={row['n_models']} models)" 
                        for _, row in origin_df.iterrows()])
    ax.set_ylabel('Cultural Distance to Real Country')
    ax.set_xlabel('Model Origin')
    ax.set_title('Orientalism Effect by Model Origin\n(Arabic Countries)', fontweight='bold', pad=15)
    ax.legend(title='Language Used')
    
    # 添加注释
    ax.text(0.98, 0.98, 'Lower distance = Better accuracy\nPercentage = English advantage', 
            transform=ax.transAxes, fontsize=8, va='top', ha='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'fig3_model_origin_orientalism.png', dpi=300)
    plt.savefig(output_dir / 'fig3_model_origin_orientalism.pdf')
    print(f"✅ Figure 3 saved")
    plt.close()

# ============================================================
# Figure 4: 综合热力图 - 模型×语言家族
# ============================================================
def create_figure4():
    """Figure 4: Heatmap of English advantage by model and language family"""
    
    # 语言家族
    lang_families = {
        'Arabic': 'ar',
        'Russian': 'ru', 
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Chinese': 'zh-cn',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Italian': 'it',
        'Portuguese': 'pt'
    }
    
    # 计算每个模型在每个语言上的英语优势
    models = sorted(non_english['model'].unique())
    
    heatmap_data = []
    for model in models:
        model_data = non_english[non_english['model'] == model]
        row = {'model': model}
        
        for family, lang in lang_families.items():
            lang_data = model_data[model_data['native_language'] == lang]
            if len(lang_data) == 0:
                row[family] = np.nan
                continue
            
            native_dist = lang_data[lang_data['language'] == lang]['cultural_distance'].mean()
            english_dist = lang_data[lang_data['is_english']]['cultural_distance'].mean()
            
            if pd.notna(native_dist) and pd.notna(english_dist) and native_dist > 0:
                row[family] = (native_dist - english_dist) / native_dist * 100
            else:
                row[family] = np.nan
        
        heatmap_data.append(row)
    
    heatmap_df = pd.DataFrame(heatmap_data).set_index('model')
    
    # 创建热力图
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 使用发散色图
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    
    sns.heatmap(heatmap_df, cmap=cmap, center=0, 
                annot=True, fmt='.0f', 
                linewidths=0.5, linecolor='white',
                cbar_kws={'label': 'English Advantage (%)', 'shrink': 0.8},
                ax=ax)
    
    ax.set_xlabel('Native Language', fontsize=11)
    ax.set_ylabel('Model', fontsize=11)
    ax.set_title('English Advantage by Model and Language\n(Positive = English better, Negative = Native better)', 
                 fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'fig4_heatmap_model_language.png', dpi=300)
    plt.savefig(output_dir / 'fig4_heatmap_model_language.pdf')
    print(f"✅ Figure 4 saved")
    plt.close()

# ============================================================
# Figure 5: 效应量森林图
# ============================================================
def create_figure5():
    """Figure 5: Forest plot of effect sizes by language family"""
    
    lang_families = {
        'Arabic': ['ar'],
        'Russian': ['ru'],
        'Romance': ['es', 'fr', 'it', 'pt'],
        'Germanic': ['de'],
        'CJK': ['zh-cn', 'ja', 'ko']
    }
    
    forest_data = []
    for family, langs in lang_families.items():
        family_data = non_english[non_english['native_language'].isin(langs)]
        
        # 收集配对数据
        paired = []
        for country in family_data['country'].unique():
            c_data = family_data[family_data['country'] == country]
            native_lang = c_data['native_language'].iloc[0]
            
            for model in c_data['model'].unique():
                m_data = c_data[c_data['model'] == model]
                native_dist = m_data[m_data['language'] == native_lang]['cultural_distance'].values
                english_dist = m_data[m_data['is_english']]['cultural_distance'].values
                
                if len(native_dist) > 0 and len(english_dist) > 0:
                    paired.append((native_dist[0], english_dist[0]))
        
        if len(paired) < 5:
            continue
        
        native_arr = np.array([p[0] for p in paired])
        english_arr = np.array([p[1] for p in paired])
        diff = native_arr - english_arr
        
        # Cohen's d
        pooled_std = np.sqrt((native_arr.std()**2 + english_arr.std()**2) / 2)
        cohens_d = diff.mean() / pooled_std if pooled_std > 0 else 0
        
        # 95% CI for Cohen's d (approximate)
        se_d = np.sqrt(2/len(paired) + cohens_d**2 / (2*len(paired)))
        ci_low = cohens_d - 1.96 * se_d
        ci_high = cohens_d + 1.96 * se_d
        
        forest_data.append({
            'family': family,
            'cohens_d': cohens_d,
            'ci_low': ci_low,
            'ci_high': ci_high,
            'n': len(paired)
        })
    
    forest_df = pd.DataFrame(forest_data)
    forest_df = forest_df.sort_values('cohens_d', ascending=True)
    
    # 创建森林图
    fig, ax = plt.subplots(figsize=(10, 6))
    
    y_pos = np.arange(len(forest_df))
    
    # 绘制置信区间
    for i, (_, row) in enumerate(forest_df.iterrows()):
        color = COLORS['islamic'] if row['cohens_d'] > 0 else COLORS['western_eu']
        ax.plot([row['ci_low'], row['ci_high']], [i, i], color=color, linewidth=2)
        ax.scatter(row['cohens_d'], i, color=color, s=100, zorder=5, edgecolor='black')
    
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
    ax.axvline(x=0.2, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.axvline(x=-0.2, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.axvline(x=0.5, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.axvline(x=-0.5, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{row['family']} (n={row['n']})" for _, row in forest_df.iterrows()])
    ax.set_xlabel("Cohen's d (English Advantage Effect Size)")
    ax.set_title('Effect Size of English Advantage by Language Family\n(Forest Plot with 95% CI)', 
                 fontweight='bold', pad=15)
    
    # 添加效应量参考线标签
    ax.text(0.2, len(forest_df) - 0.3, 'small', fontsize=8, color='gray', ha='center')
    ax.text(0.5, len(forest_df) - 0.3, 'medium', fontsize=8, color='gray', ha='center')
    ax.text(-0.2, len(forest_df) - 0.3, 'small', fontsize=8, color='gray', ha='center')
    ax.text(-0.5, len(forest_df) - 0.3, 'medium', fontsize=8, color='gray', ha='center')
    
    # 添加方向标注
    ax.text(0.95, 0.02, '← Native better | English better →', 
            transform=ax.transAxes, fontsize=9, ha='right', style='italic')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'fig5_forest_plot_effect_sizes.png', dpi=300)
    plt.savefig(output_dir / 'fig5_forest_plot_effect_sizes.pdf')
    print(f"✅ Figure 5 saved")
    plt.close()

# 生成所有图表
if __name__ == '__main__':
    create_figure1()
    create_figure2()
    create_figure3()
    create_figure4()
    create_figure5()
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")
    print("\n图表说明:")
    print("  Fig 1: 按文化区域的英语优势（主效应图）")
    print("  Fig 2: 伊斯兰 vs 西欧国家详细对比")
    print("  Fig 3: 模型来源对东方主义效应的影响")
    print("  Fig 4: 模型×语言热力图")
    print("  Fig 5: 效应量森林图")
