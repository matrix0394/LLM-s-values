#!/usr/bin/env python3
"""
生成"他者理论/东方主义"验证相关图表
使用最新的Stage3数据（包括日韩和10个模型）

理论背景：
- 他者理论（The Other）：LLM对非英语国家/地区的刻板印象
- 东方主义：西方视角下对东方的简化和刻板化
- 发现：英语优势在东亚地区最强，尤其是港台澳
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import json
from pathlib import Path

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
    
    # 检查是否存在预计算的结果
    stage0_vs_stage3_dir = Path('results/analysis/stage0_vs_stage3')
    
    if not stage0_vs_stage3_dir.exists():
        print("⚠️ 未找到 stage0_vs_stage3 分析结果")
        print("请先运行: python analysis/stage0_vs_stage3_distance.py")
        raise FileNotFoundError("请先运行 stage0_vs_stage3_distance.py 生成数据")
    
    # 1. 加载详细距离数据
    distances_file = stage0_vs_stage3_dir / 'distances_detailed.xlsx'
    if distances_file.exists():
        results_df = pd.read_excel(distances_file)
        print(f"✅ 加载距离数据: {len(results_df)} 行")
    else:
        # 尝试CSV格式
        distances_file = stage0_vs_stage3_dir / 'distances_detailed.csv'
        results_df = pd.read_csv(distances_file)
        print(f"✅ 加载距离数据: {len(results_df)} 行")
    
    # 2. 加载英语优势数据
    advantage_file = stage0_vs_stage3_dir / 'english_advantage_average.xlsx'
    if advantage_file.exists():
        advantage_df = pd.read_excel(advantage_file)
        print(f"✅ 加载英语优势数据: {len(advantage_df)} 行")
    else:
        # 尝试CSV格式
        advantage_file = stage0_vs_stage3_dir / 'english_advantage_average.csv'
        advantage_df = pd.read_csv(advantage_file)
        print(f"✅ 加载英语优势数据: {len(advantage_df)} 行")
    
    print(f"✅ 数据加载完成")
    
    return results_df, advantage_df

def create_east_asia_complete_chart(advantage_df):
    """图表1: 东亚完整梯度（包括日韩）"""
    print("\n生成图表1: 东亚完整梯度...")
    
    # 东亚国家/地区
    east_asian_countries = [
        'Hong Kong', 'Singapore', 'China', 
        'Taiwan (Province of China)', 'Macao',
        'Japan', 'Korea (the Republic of)'
    ]
    
    ea_data = advantage_df[advantage_df['country'].isin(east_asian_countries)].copy()
    ea_data = ea_data.sort_values('english_advantage', ascending=False)
    
    if len(ea_data) == 0:
        print("⚠️ 没有东亚数据")
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 创建标签
    labels = []
    for _, row in ea_data.iterrows():
        country_short = row['country'].replace('(Province of China)', '').replace('(the Republic of)', '').strip()
        lang_short = row['native_language'].replace('zh-', '')
        labels.append(f"{country_short}\n({lang_short})")
    
    colors = ['#E74C3C' if x > 20 else '#F39C12' if x > 10 else '#27AE60' 
              for x in ea_data['english_advantage']]
    
    bars = ax.barh(range(len(ea_data)), ea_data['english_advantage'], 
                   color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_yticks(range(len(ea_data)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('英语优势 (%)', fontsize=12, fontweight='bold')
    ax.set_title('东亚完整梯度：英语 vs 母语模仿效果\n(包括日韩，10个模型平均，国家/地区)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, ea_data['english_advantage'])):
        ax.text(val + 1, i, f'{val:+.1f}%', 
               va='center', fontsize=10, fontweight='bold')
    
    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#E74C3C', alpha=0.8, label='强英语优势 (>20%)'),
        Patch(facecolor='#F39C12', alpha=0.8, label='中等英语优势 (10-20%)'),
        Patch(facecolor='#27AE60', alpha=0.8, label='弱英语优势 (<10%)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'east_asia_complete_gradient.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: east_asia_complete_gradient.png")
    plt.close()

def create_hk_tw_mo_detail_chart(advantage_df, results_df):
    """图表2: 东亚地区文化坐标轨迹图（港澳台日韩）"""
    print("\n生成图表2: 东亚地区文化坐标轨迹图...")
    
    import numpy as np
    
    # 加载Stage0真实坐标
    import json
    with open('data/country_values/country_scores_pca.json') as f:
        stage0_data = json.load(f)
    
    stage0_coords = {}
    for item in stage0_data:
        country = item.get('Country')
        if country:
            stage0_coords[country] = {
                'PC1': item.get('PC1_rescaled'),
                'PC2': item.get('PC2_rescaled')
            }
    
    # 东亚国家/地区
    east_asia = ['Hong Kong', 'Taiwan (Province of China)', 'Macao', 
                 'Japan', 'Korea (the Republic of)']
    
    # 为每个国家/地区分配颜色
    colors_map = {
        'Hong Kong': '#E74C3C',
        'Taiwan (Province of China)': '#3498DB',
        'Macao': '#2ECC71',
        'Japan': '#F39C12',
        'Korea (the Republic of)': '#9B59B6'
    }
    
    # 语言代码映射（用于区分不同母语）
    lang_labels = {
        'zh-cn': '简中',
        'zh-tw': '繁中',
        'zh-hk': '粤语',
        'ja': '日语',
        'ko': '韩语'
    }
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # 第一步：绘制背景散点（10个模型的原始数据，浅色）
    for country in east_asia:
        if country not in stage0_coords:
            continue
        
        country_data = results_df[results_df['country'] == country]
        if len(country_data) == 0:
            continue
        
        color = colors_map.get(country, '#95A5A6')
        
        # 绘制所有模型的英语模仿散点（浅色）
        english_data = country_data[country_data['is_english']]
        if len(english_data) > 0:
            ax.scatter(english_data['llm_PC1'], english_data['llm_PC2'], 
                      c=color, s=30, alpha=0.15, marker='o', zorder=1)
        
        # 绘制所有模型的母语模仿散点（浅色）
        native_data = country_data[~country_data['is_english']]
        if len(native_data) > 0:
            ax.scatter(native_data['llm_PC1'], native_data['llm_PC2'], 
                      c=color, s=30, alpha=0.15, marker='s', zorder=1)
    
    # 第二步：绘制主要轨迹（真实位置、平均模仿位置、箭头和距离标注）
    for country in east_asia:
        if country not in stage0_coords:
            continue
        
        # 真实坐标
        real_pc1 = stage0_coords[country]['PC1']
        real_pc2 = stage0_coords[country]['PC2']
        
        country_short = country.replace('(Province of China)', '').replace('(the Republic of)', '').strip()
        color = colors_map.get(country, '#95A5A6')
        
        # 绘制真实位置
        ax.scatter(real_pc1, real_pc2, s=400, c=color, marker='*', 
                  edgecolors='black', linewidths=2.5, zorder=5, alpha=0.9)
        
        # 添加国家/地区标签
        ax.text(real_pc1, real_pc2 + 0.18, country_short, 
               fontsize=11, fontweight='bold', ha='center', va='bottom', zorder=6)
        
        # 获取该国家的模仿数据
        country_data = results_df[results_df['country'] == country]
        
        if len(country_data) == 0:
            continue
        
        # 英语模仿位置（平均）
        english_data = country_data[country_data['is_english']]
        if len(english_data) > 0:
            eng_pc1 = english_data['llm_PC1'].mean()
            eng_pc2 = english_data['llm_PC2'].mean()
            
            # 计算距离
            eng_dist = np.sqrt((eng_pc1 - real_pc1)**2 + (eng_pc2 - real_pc2)**2)
            
            ax.scatter(eng_pc1, eng_pc2, s=180, c=color, marker='o',
                      edgecolors='black', linewidths=1.8, alpha=0.85, zorder=4)
            
            # 绘制箭头：真实 → 英语
            ax.annotate('', xy=(eng_pc1, eng_pc2), xytext=(real_pc1, real_pc2),
                       arrowprops=dict(arrowstyle='->', lw=2.5, color=color, alpha=0.6))
            
            # 在箭头中点标注距离
            mid_x = (real_pc1 + eng_pc1) / 2
            mid_y = (real_pc2 + eng_pc2) / 2
            ax.text(mid_x, mid_y, f'{eng_dist:.2f}', fontsize=9, fontweight='bold',
                   ha='center', va='bottom', color=color,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=color))
            
            # 标注语言
            ax.text(eng_pc1, eng_pc2 - 0.13, 'EN', fontsize=8, ha='center', va='top',
                   bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.8))
        
        # 母语模仿位置（按语言代码分组）
        native_data = country_data[~country_data['is_english']]
        
        if len(native_data) > 0:
            # 按语言代码分组
            for lang_code in native_data['language'].unique():
                lang_subset = native_data[native_data['language'] == lang_code]
                
                if len(lang_subset) == 0:
                    continue
                
                nat_pc1 = lang_subset['llm_PC1'].mean()
                nat_pc2 = lang_subset['llm_PC2'].mean()
                
                # 计算距离
                nat_dist = np.sqrt((nat_pc1 - real_pc1)**2 + (nat_pc2 - real_pc2)**2)
                
                # 根据语言代码选择不同的标记样式
                if lang_code == 'zh-cn':
                    marker_style = 's'  # 方形
                    linestyle = '--'
                elif lang_code in ['zh-tw', 'zh-hk']:
                    marker_style = 'D'  # 菱形
                    linestyle = ':'
                else:
                    marker_style = 's'  # 默认方形
                    linestyle = '--'
                
                ax.scatter(nat_pc1, nat_pc2, s=180, c=color, marker=marker_style,
                          edgecolors='black', linewidths=1.8, alpha=0.85, zorder=4)
                
                # 绘制箭头：真实 → 母语
                ax.annotate('', xy=(nat_pc1, nat_pc2), xytext=(real_pc1, real_pc2),
                           arrowprops=dict(arrowstyle='->', lw=2.5, color=color, 
                                         alpha=0.6, linestyle=linestyle))
                
                # 在箭头中点标注距离
                mid_x = (real_pc1 + nat_pc1) / 2
                mid_y = (real_pc2 + nat_pc2) / 2
                ax.text(mid_x, mid_y, f'{nat_dist:.2f}', fontsize=9, fontweight='bold',
                       ha='center', va='top', color=color,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=color))
                
                # 标注语言
                lang_label = lang_labels.get(lang_code, lang_code)
                ax.text(nat_pc1, nat_pc2 - 0.13, lang_label, fontsize=8, ha='center', va='top',
                       bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('PC1 (生存 ← → 自我表达)', fontsize=13, fontweight='bold')
    ax.set_ylabel('PC2 (传统 ← → 现代)', fontsize=13, fontweight='bold')
    ax.set_title('东亚地区文化坐标轨迹：真实位置 vs LLM模仿位置\n(港澳台日韩，10个模型，箭头标注欧氏距离)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(0, color='black', linewidth=1, alpha=0.5)
    ax.axvline(0, color='black', linewidth=1, alpha=0.5)
    
    # 添加图例说明
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='gray', 
               markersize=15, label='真实位置', markeredgecolor='black', markeredgewidth=1.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
               markersize=10, label='英语模仿（平均）', markeredgecolor='black', markeredgewidth=1),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='gray', 
               markersize=10, label='母语模仿-简中（平均）', markeredgecolor='black', markeredgewidth=1),
        Line2D([0], [0], marker='D', color='w', markerfacecolor='gray', 
               markersize=9, label='母语模仿-繁中/粤语（平均）', markeredgecolor='black', markeredgewidth=1),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgray', 
               markersize=6, label='原始散点（10个模型）', alpha=0.5),
        Line2D([0], [0], color='gray', linewidth=2, label='英语偏移', alpha=0.5),
        Line2D([0], [0], color='gray', linewidth=2, linestyle='--', label='母语偏移-简中', alpha=0.5),
        Line2D([0], [0], color='gray', linewidth=2, linestyle=':', label='母语偏移-繁中/粤语', alpha=0.5)
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10, framealpha=0.95, ncol=2)
    
    # 调整坐标轴范围，聚焦右上区域（东亚国家集中区域）
    ax.set_xlim(-0.5, 3.2)
    ax.set_ylim(-0.5, 3.2)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'east_asia_trajectory.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: east_asia_trajectory.png")
    plt.close()

def create_global_language_regions_chart(advantage_df):
    """图表3: 地理梯度验证 - 各文化区域的语言效应"""
    print("\n生成图表3: 各文化区域的语言效应...")
    
    # 从项目配置文件加载文化区域映射
    import json
    with open('config/country_codes.json', 'r', encoding='utf-8') as f:
        country_codes = json.load(f)
    
    country_to_region = {item['Country']: item.get('Cultural Region', 'Other') 
                        for item in country_codes}
    
    # 为每个国家添加文化区域
    advantage_df_with_region = advantage_df.copy()
    advantage_df_with_region['cultural_region'] = advantage_df_with_region['country'].map(country_to_region)
    
    # 过滤掉 'Other' 区域
    advantage_df_with_region = advantage_df_with_region[advantage_df_with_region['cultural_region'] != 'Other']
    
    # 按文化区域统计
    region_stats = advantage_df_with_region.groupby('cultural_region').agg({
        'english_advantage': ['mean', 'std', 'count']
    }).reset_index()
    
    region_stats.columns = ['region', 'mean', 'std', 'count']
    
    if len(region_stats) == 0:
        print("⚠️ 没有文化区域数据")
        return
    
    region_stats = region_stats.sort_values('mean', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 使用红绿渐变色：正值（英语优势）用红色，负值（母语优势）用绿色
    colors = ['#E74C3C' if x > 0 else '#27AE60' for x in region_stats['mean']]
    bars = ax.barh(range(len(region_stats)), region_stats['mean'], 
                  color=colors, alpha=0.75, edgecolor='black', linewidth=1.5)
    
    ax.set_yticks(range(len(region_stats)))
    ax.set_yticklabels(region_stats['region'], fontsize=11)
    ax.set_xlabel('语言效应 (英语优势, %)', fontsize=12, fontweight='bold')
    ax.set_title('地理梯度验证：各文化区域的语言效应\n(正值=英语更优, 负值=母语更优, 10个模型平均)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.axvline(0, color='black', linestyle='-', linewidth=2)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()
    
    # 添加数值标签
    for i, row in enumerate(region_stats.itertuples()):
        x_pos = row.mean + (3 if row.mean > 0 else -3)
        ha = 'left' if row.mean > 0 else 'right'
        ax.text(x_pos, i, f'{row.mean:+.1f}%',
               va='center', ha=ha, fontsize=11, fontweight='bold')
    
    # 添加图例
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
    """图表4: 他者理论验证 - 英语优势分布"""
    print("\n生成图表4: 他者理论验证...")
    
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
    
    # 添加数值标签
    for i, (bar, val) in enumerate(zip(bars, combined['english_advantage'])):
        ax2.text(val + (2 if val > 0 else -2), i, f'{val:+.1f}%',
                va='center', ha='left' if val > 0 else 'right',
                fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'orientalism_theory_validation.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: orientalism_theory_validation.png")
    plt.close()

def create_japan_korea_focus_chart(advantage_df, results_df):
    """图表5: 日韩专项分析（新增）"""
    print("\n生成图表5: 日韩专项分析...")
    
    jp_kr_data = advantage_df[advantage_df['country'].isin([
        'Japan', 'Korea (the Republic of)'
    ])].copy()
    
    if len(jp_kr_data) == 0:
        print("⚠️ 没有日韩数据")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 左图：日韩英语优势对比
    jp_kr_data['country_short'] = jp_kr_data['country'].replace({
        'Japan': '日本',
        'Korea (the Republic of)': '韩国'
    })
    
    colors = ['#E74C3C', '#3498DB']
    bars = ax1.bar(range(len(jp_kr_data)), jp_kr_data['english_advantage'],
                  color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax1.set_xticks(range(len(jp_kr_data)))
    ax1.set_xticklabels(jp_kr_data['country_short'], fontsize=12)
    ax1.set_ylabel('英语优势 (%)', fontsize=12, fontweight='bold')
    ax1.set_title('日韩英语优势对比', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars, jp_kr_data['english_advantage']):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.3,
                f'{val:+.1f}%', ha='center', fontsize=11, fontweight='bold')
    
    # 右图：日韩母语vs英语距离对比
    jp_kr_countries = ['Japan', 'Korea (the Republic of)']
    
    for idx, country in enumerate(jp_kr_countries):
        country_data = results_df[results_df['country'] == country]
        
        native_dist = country_data[~country_data['is_english']]['distance'].mean()
        english_dist = country_data[country_data['is_english']]['distance'].mean()
        
        x_pos = idx * 2
        ax2.bar([x_pos, x_pos + 0.8], [native_dist, english_dist],
               width=0.7, color=['#E74C3C', '#27AE60'], alpha=0.7,
               edgecolor='black', linewidth=1.5)
        
        # 添加标签
        country_short = '日本' if country == 'Japan' else '韩国'
        ax2.text(x_pos + 0.4, max(native_dist, english_dist) + 0.1,
                country_short, ha='center', fontsize=11, fontweight='bold')
    
    ax2.set_xticks([0.4, 2.4])
    ax2.set_xticklabels(['母语', '英语'] * 1, fontsize=11)
    ax2.set_ylabel('文化距离', fontsize=12, fontweight='bold')
    ax2.set_title('日韩母语 vs 英语距离对比', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.legend(['母语', '英语'], loc='upper right', fontsize=10)
    
    plt.suptitle('日韩专项分析（10个模型平均）', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'japan_korea_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: japan_korea_analysis.png")
    plt.close()

def create_geographic_gradient_chart(advantage_df):
    """图表6: 从近到远的英语效应趋势（按文化区域）"""
    print("\n生成图表6: 地理梯度趋势...")
    
    # 从项目配置文件加载文化区域映射
    import json
    with open('config/country_codes.json', 'r', encoding='utf-8') as f:
        country_codes = json.load(f)
    
    country_to_region = {item['Country']: item.get('Cultural Region', 'Other') 
                        for item in country_codes}
    
    # 为每个国家添加文化区域
    advantage_df_with_region = advantage_df.copy()
    advantage_df_with_region['cultural_region'] = advantage_df_with_region['country'].map(country_to_region)
    
    # 定义文化区域的地理梯度顺序（从近到远）
    # 按照与西方的文化和地理距离排序
    region_order = [
        'Catholic Europe',
        'Protestant Europe', 
        'Orthodox Europe',
        'Latin America',
        'African-Islamic',
        'West & South Asia',
        'Confucian'
    ]
    
    regions = []
    advantages = []
    
    for region in region_order:
        region_data = advantage_df_with_region[advantage_df_with_region['cultural_region'] == region]
        if len(region_data) > 0:
            mean_adv = region_data['english_advantage'].mean()
            regions.append(region)
            advantages.append(mean_adv)
    
    if len(regions) == 0:
        print("⚠️ 没有梯度数据")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 绘制折线图
    x_pos = range(len(regions))
    line = ax.plot(x_pos, advantages, marker='o', markersize=10, linewidth=3,
                   color='#3498DB', markerfacecolor='#3498DB', markeredgecolor='black',
                   markeredgewidth=2, label='语言效应趋势')
    
    # 添加零线
    ax.axhline(0, color='black', linestyle='-', linewidth=2, alpha=0.5)
    
    # 填充背景色：正值区域（英语优势）用红色，负值区域（母语优势）用绿色
    ax.fill_between(x_pos, 0, advantages, where=[a >= 0 for a in advantages],
                    color='#E74C3C', alpha=0.2, label='英语优势区')
    ax.fill_between(x_pos, 0, advantages, where=[a < 0 for a in advantages],
                    color='#27AE60', alpha=0.2, label='母语优势区')
    
    # 设置坐标轴
    ax.set_xticks(x_pos)
    ax.set_xticklabels(regions, fontsize=11, rotation=15, ha='right')
    ax.set_ylabel('语言效应 (英语优势, %)', fontsize=13, fontweight='bold')
    ax.set_xlabel('文化区域（按与西方的距离排序）', fontsize=13, fontweight='bold')
    ax.set_title('从近到远：英语效应的文化梯度\n(按项目定义的文化区域，10个模型平均)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for i, (region, adv) in enumerate(zip(regions, advantages)):
        y_offset = 3 if adv > 0 else -3
        va = 'bottom' if adv > 0 else 'top'
        ax.text(i, adv + y_offset, f'{adv:+.1f}%',
               ha='center', va=va, fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    # 添加图例
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    # 添加注释
    ax.text(0.02, 0.98, '← 更接近西方', transform=ax.transAxes,
           fontsize=10, va='top', ha='left', style='italic', color='gray')
    ax.text(0.98, 0.98, '更远离西方 →', transform=ax.transAxes,
           fontsize=10, va='top', ha='right', style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'geographic_gradient_trend.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: geographic_gradient_trend.png")
    plt.close()

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("东方主义/他者理论可视化分析")
    print("使用最新Stage3数据（包括日韩和10个模型）")
    print("=" * 80)
    
    # 加载数据
    results_df, advantage_df = load_latest_data()
    
    # 生成所有图表
    create_east_asia_complete_chart(advantage_df)
    create_hk_tw_mo_detail_chart(advantage_df, results_df)
    create_global_language_regions_chart(advantage_df)
    create_orientalism_theory_chart(advantage_df)
    create_japan_korea_focus_chart(advantage_df, results_df)
    create_geographic_gradient_chart(advantage_df)
    
    # 打印统计摘要
    print("\n" + "=" * 80)
    print("统计摘要")
    print("=" * 80)
    print(f"总国家/地区-语言组合数: {len(advantage_df)}")
    print(f"平均英语优势: {advantage_df['english_advantage'].mean():+.1f}%")
    print(f"英语优势最强: {advantage_df.loc[advantage_df['english_advantage'].idxmax(), 'country']} "
          f"({advantage_df['english_advantage'].max():+.1f}%)")
    print(f"母语优势最强: {advantage_df.loc[advantage_df['english_advantage'].idxmin(), 'country']} "
          f"({advantage_df['english_advantage'].min():+.1f}%)")
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")
    print("=" * 80)

if __name__ == '__main__':
    main()
