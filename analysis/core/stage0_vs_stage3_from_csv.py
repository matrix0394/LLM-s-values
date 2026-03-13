#!/usr/bin/env python3
"""
Stage0 vs Stage3 文化距离分析 - 使用预计算的CSV数据
数据来源: results/roleplay_multilingual/cultural_distance_analysis.csv

这个脚本使用之前 scripts/analyze_cultural_distance.py 计算好的距离数据
与 stage0_vs_stage3_distance.py（重新计算版）对比，验证结果一致性
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.stats import pearsonr, spearmanr, binomtest
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 排除的低质量模型（只排除qwen3-1.7b）
EXCLUDED_MODELS = ['qwen3-1.7b']

# 输出目录
OUTPUT_DIR = Path('results/analysis/stage0_vs_stage3_csv')


def load_data():
    """加载预计算的文化距离数据"""
    csv_path = Path('results/roleplay_multilingual/cultural_distance_analysis.csv')
    
    if not csv_path.exists():
        raise FileNotFoundError(f"未找到预计算数据: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"✅ 加载预计算数据: {len(df)} 条记录")
    print(f"   国家数: {df['country'].nunique()}")
    print(f"   模型数: {df['model'].nunique()}")
    print(f"   语言数: {df['language'].nunique()}")
    
    # 排除低质量模型
    original_count = len(df)
    df = df[~df['model'].isin(EXCLUDED_MODELS)]
    print(f"   排除低质量模型后: {len(df)} 条 (排除 {original_count - len(df)} 条)")
    
    return df


def analyze_language_family(df):
    """按语言家族分析英语优势"""
    print("\n" + "=" * 70)
    print("📊 按语言家族分层分析")
    print("=" * 70)
    
    non_english = df[~df['is_english_native_country']]
    
    language_families = {
        'Arabic': ['ar'],
        'Russian': ['ru'],
        'Romance (es/fr/it/pt)': ['es', 'fr', 'it', 'pt'],
        'Germanic (de)': ['de'],
        'CJK': ['zh-cn', 'zh-tw', 'zh-hk', 'ja', 'ko']
    }
    
    print("\n--- 1. 按语言家族的英语优势 ---")
    family_stats = []
    
    for family, langs in language_families.items():
        family_data = non_english[non_english['native_language'].isin(langs)]
        if len(family_data) == 0:
            continue
        
        # 收集配对数据
        paired = []
        for country in family_data['country'].unique():
            country_data = family_data[family_data['country'] == country]
            native_lang = country_data['native_language'].iloc[0]
            
            for model in country_data['model'].unique():
                model_data = country_data[country_data['model'] == model]
                native_dist = model_data[model_data['language'] == native_lang]['cultural_distance'].values
                english_dist = model_data[model_data['is_english']]['cultural_distance'].values
                
                if len(native_dist) > 0 and len(english_dist) > 0:
                    paired.append((native_dist[0], english_dist[0]))
        
        if len(paired) < 5:
            continue
        
        native_arr = np.array([p[0] for p in paired])
        english_arr = np.array([p[1] for p in paired])
        diff = native_arr - english_arr  # 正值=英语更好
        
        t_stat, p_value = stats.ttest_rel(native_arr, english_arr)
        eng_better = (diff > 0).sum()
        eng_adv_pct = (diff / native_arr * 100).mean()
        
        sig = "***" if p_value < 0.001 else ("**" if p_value < 0.01 else ("*" if p_value < 0.05 else ""))
        
        family_stats.append({
            'family': family,
            'n': len(paired),
            'native_mean': native_arr.mean(),
            'english_mean': english_arr.mean(),
            'english_advantage': eng_adv_pct,
            't_stat': t_stat,
            'p_value': p_value,
            'sig': sig
        })
        
        print(f"\n   {family}:")
        print(f"     配对数: {len(paired)}")
        print(f"     官方语言: {native_arr.mean():.3f}, 英语: {english_arr.mean():.3f}")
        print(f"     英语优势: {eng_adv_pct:+.1f}%")
        print(f"     英语更好: {eng_better}/{len(paired)} ({eng_better/len(paired)*100:.1f}%)")
        print(f"     t={t_stat:.2f}, p={p_value:.4f} {sig}")
    
    return pd.DataFrame(family_stats)


def analyze_western_vs_non_western(df):
    """非西方语言 vs 西方语言对比"""
    print("\n--- 2. 非西方语言 vs 西方语言 ---")
    
    non_english = df[~df['is_english_native_country']]
    
    non_western_langs = ['ar', 'ru', 'zh-cn', 'zh-tw', 'zh-hk', 'ja', 'ko']
    western_langs = ['es', 'fr', 'it', 'pt', 'de']
    
    results = []
    for group_name, langs in [("非西方语言", non_western_langs), ("西方语言", western_langs)]:
        group_data = non_english[non_english['native_language'].isin(langs)]
        
        paired = []
        for country in group_data['country'].unique():
            country_data = group_data[group_data['country'] == country]
            native_lang = country_data['native_language'].iloc[0]
            
            for model in country_data['model'].unique():
                model_data = country_data[country_data['model'] == model]
                native_dist = model_data[model_data['language'] == native_lang]['cultural_distance'].values
                english_dist = model_data[model_data['is_english']]['cultural_distance'].values
                
                if len(native_dist) > 0 and len(english_dist) > 0:
                    paired.append((native_dist[0], english_dist[0]))
        
        if len(paired) < 5:
            continue
        
        native_arr = np.array([p[0] for p in paired])
        english_arr = np.array([p[1] for p in paired])
        diff = native_arr - english_arr
        
        t_stat, p_value = stats.ttest_rel(native_arr, english_arr)
        eng_better = (diff > 0).sum()
        eng_adv_pct = (diff / native_arr * 100).mean()
        
        sig = "***" if p_value < 0.001 else ("**" if p_value < 0.01 else ("*" if p_value < 0.05 else ""))
        
        results.append({
            'group': group_name,
            'n': len(paired),
            'native_mean': native_arr.mean(),
            'english_mean': english_arr.mean(),
            'english_advantage': eng_adv_pct,
            't_stat': t_stat,
            'p_value': p_value
        })
        
        print(f"\n   {group_name}:")
        print(f"     配对数: {len(paired)}")
        print(f"     官方语言: {native_arr.mean():.3f}, 英语: {english_arr.mean():.3f}")
        print(f"     英语优势: {eng_adv_pct:+.1f}%")
        print(f"     英语更好: {eng_better}/{len(paired)} ({eng_better/len(paired)*100:.1f}%)")
        print(f"     t={t_stat:.2f}, p={p_value:.4f} {sig}")
    
    return pd.DataFrame(results)


def analyze_arabic_countries(df):
    """阿拉伯语国家详细分析"""
    print("\n--- 3. 阿拉伯语国家详细分析 ---")
    
    non_english = df[~df['is_english_native_country']]
    arabic_data = non_english[non_english['native_language'] == 'ar']
    
    print(f"   阿拉伯语国家: {arabic_data['country'].unique().tolist()}")
    
    results = []
    for country in arabic_data['country'].unique():
        country_data = arabic_data[arabic_data['country'] == country]
        native_dist = country_data[country_data['language'] == 'ar']['cultural_distance'].mean()
        english_dist = country_data[country_data['is_english']]['cultural_distance'].mean()
        
        if pd.notna(native_dist) and pd.notna(english_dist):
            eng_adv = (native_dist - english_dist) / native_dist * 100
            results.append({
                'country': country,
                'arabic_dist': native_dist,
                'english_dist': english_dist,
                'english_advantage': eng_adv
            })
            print(f"   {country:20s}: 阿拉伯语={native_dist:.2f}, 英语={english_dist:.2f}, 英语优势={eng_adv:+.1f}%")
    
    return pd.DataFrame(results)


def analyze_orientalism_effect(df):
    """东方主义效应分析"""
    print("\n" + "=" * 70)
    print("🔬 语言他者化效应分析 (Linguistic Othering / Orientalism)")
    print("=" * 70)
    
    non_english = df[~df['is_english_native_country']]
    
    # 西方文化中心
    western_center = df[df['is_english_native_country']][['stage0_pc1', 'stage0_pc2']].mean()
    print(f"\n西方文化中心坐标: PC1={western_center['stage0_pc1']:.2f}, PC2={western_center['stage0_pc2']:.2f}")
    
    # 计算每个国家到西方中心的距离和英语优势
    country_analysis = []
    for country in non_english['country'].unique():
        country_data = non_english[non_english['country'] == country]
        native_lang = country_data['native_language'].iloc[0]
        
        real_pc1 = country_data['stage0_pc1'].iloc[0]
        real_pc2 = country_data['stage0_pc2'].iloc[0]
        
        dist_to_west = np.sqrt((real_pc1 - western_center['stage0_pc1'])**2 + 
                               (real_pc2 - western_center['stage0_pc2'])**2)
        
        native_dist = country_data[country_data['language'] == native_lang]['cultural_distance'].mean()
        english_dist = country_data[country_data['is_english']]['cultural_distance'].mean()
        
        if pd.notna(native_dist) and pd.notna(english_dist):
            english_advantage = (native_dist - english_dist) / native_dist * 100
            country_analysis.append({
                'country': country,
                'native_lang': native_lang,
                'dist_to_west': dist_to_west,
                'native_dist': native_dist,
                'english_dist': english_dist,
                'english_advantage': english_advantage
            })
    
    analysis_df = pd.DataFrame(country_analysis)
    
    # 相关性分析
    print("\n--- 1. 文化距离与英语优势的相关性 ---")
    corr_pearson, p_pearson = pearsonr(analysis_df['dist_to_west'], analysis_df['english_advantage'])
    corr_spearman, p_spearman = spearmanr(analysis_df['dist_to_west'], analysis_df['english_advantage'])
    
    print(f"   Pearson相关: r={corr_pearson:.3f}, p={p_pearson:.4f}")
    print(f"   Spearman相关: ρ={corr_spearman:.3f}, p={p_spearman:.4f}")
    
    if corr_pearson > 0 and p_pearson < 0.05:
        print("   → 支持H1: 文化距离越远，英语优势越大 *")
    
    # 文化区域分析
    print("\n--- 2. 按文化区域的英语优势 ---")
    cultural_regions = {
        'Islamic/Arab': ['Algeria', 'Palestine', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
                         'Libya', 'Morocco', 'Qatar', 'Tunisia', 'Egypt', 'Yemen'],
        'Orthodox/Slavic': ['Russian Federation', 'Belarus', 'Kazakhstan', 'Kyrgyzstan'],
        'Latin America': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador',
                          'Guatemala', 'Haiti', 'Mexico', 'Nicaragua', 'Peru', 'Uruguay', 'Venezuela'],
        'Western Europe': ['Austria', 'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg',
                           'Portugal', 'Spain', 'Switzerland'],
        'East Asia': ['China', 'Japan', 'Korea, Republic of', 'Macao']
    }
    
    for region, countries in cultural_regions.items():
        region_data = analysis_df[analysis_df['country'].isin(countries)]
        if len(region_data) > 0:
            print(f"\n   {region}:")
            print(f"     国家数: {len(region_data)}")
            print(f"     平均英语优势: {region_data['english_advantage'].mean():+.1f}%")
            print(f"     到西方中心距离: {region_data['dist_to_west'].mean():.2f}")
    
    # 伊斯兰 vs 西欧 t检验
    print("\n--- 3. 东方主义效应检验 ---")
    islamic = analysis_df[analysis_df['country'].isin(cultural_regions['Islamic/Arab'])]
    western = analysis_df[analysis_df['country'].isin(cultural_regions['Western Europe'])]
    
    if len(islamic) > 0 and len(western) > 0:
        t_stat, p_value = stats.ttest_ind(islamic['english_advantage'], western['english_advantage'])
        print(f"   伊斯兰国家平均英语优势: {islamic['english_advantage'].mean():+.1f}%")
        print(f"   西欧国家平均英语优势: {western['english_advantage'].mean():+.1f}%")
        print(f"   t检验: t={t_stat:.2f}, p={p_value:.6f}")
        
        if p_value < 0.001:
            print("   → 伊斯兰国家的英语优势显著高于西欧国家 ***")
    
    # Cohen's d
    print("\n--- 4. 效应量 (Cohen's d) ---")
    non_western_regions = cultural_regions['Islamic/Arab'] + cultural_regions['Orthodox/Slavic'] + cultural_regions['East Asia']
    western_regions = cultural_regions['Western Europe'] + cultural_regions['Latin America']
    
    non_western = analysis_df[analysis_df['country'].isin(non_western_regions)]
    western = analysis_df[analysis_df['country'].isin(western_regions)]
    
    if len(non_western) > 0 and len(western) > 0:
        pooled_std = np.sqrt((non_western['english_advantage'].std()**2 + 
                              western['english_advantage'].std()**2) / 2)
        cohens_d = (non_western['english_advantage'].mean() - western['english_advantage'].mean()) / pooled_std
        
        print(f"   非西方平均: {non_western['english_advantage'].mean():+.1f}%")
        print(f"   西方平均: {western['english_advantage'].mean():+.1f}%")
        print(f"   Cohen's d: {cohens_d:.2f}")
        
        if abs(cohens_d) >= 0.8:
            print("   → 大效应量 (large effect)")
        elif abs(cohens_d) >= 0.5:
            print("   → 中等效应量 (medium effect)")
    
    return analysis_df


def analyze_by_model(df):
    """按模型质量分析"""
    print("\n" + "=" * 70)
    print("📊 按模型质量分层分析")
    print("=" * 70)
    
    non_english = df[~df['is_english_native_country']]
    
    model_effects = []
    for model in non_english['model'].unique():
        model_data = non_english[non_english['model'] == model]
        
        native_dist = model_data[model_data['is_using_native_language']]['cultural_distance'].mean()
        english_dist = model_data[model_data['is_english']]['cultural_distance'].mean()
        overall_dist = model_data['cultural_distance'].mean()
        
        if pd.notna(native_dist) and pd.notna(english_dist):
            diff = english_dist - native_dist
            model_effects.append({
                'model': model,
                'overall_dist': overall_dist,
                'native_dist': native_dist,
                'english_dist': english_dist,
                'diff': diff,
                'english_better': diff < 0
            })
    
    effects_df = pd.DataFrame(model_effects).sort_values('overall_dist')
    
    print("\n--- 每个模型的语言效应 ---")
    print(effects_df.to_string(index=False))
    
    english_better_count = effects_df['english_better'].sum()
    print(f"\n英语更好的模型: {english_better_count}/{len(effects_df)}")
    print(f"平均差异 (英语-官方语言): {effects_df['diff'].mean():.4f}")
    
    return effects_df


def analyze_english_native_baseline(df):
    """英语母语国家基准分析"""
    print("\n" + "=" * 70)
    print("📊 英语母语国家基准分析")
    print("=" * 70)
    
    english_native_data = df[
        (df['is_english_native_country']) & 
        (df['is_english'])
    ]
    
    if len(english_native_data) > 0:
        print(f"\n   英语母语国家数: {english_native_data['country'].nunique()}")
        print(f"   英语母语国家: {english_native_data['country'].unique().tolist()}")
        print(f"   平均距离: {english_native_data['cultural_distance'].mean():.4f} ± {english_native_data['cultural_distance'].std():.4f}")
        
        # 按国家统计
        print("\n   按国家统计:")
        for country in english_native_data['country'].unique():
            country_data = english_native_data[english_native_data['country'] == country]
            print(f"     {country:20s}: {country_data['cultural_distance'].mean():.4f} ± {country_data['cultural_distance'].std():.4f} (N={len(country_data)})")
    else:
        print("   ⚠️ 无英语母语国家数据")
    
    return english_native_data


def analyze_native_vs_english_overall(df):
    """非英语国家：官方语言 vs 英语整体对比"""
    print("\n" + "=" * 70)
    print("📊 非英语国家：官方语言 vs 英语整体对比")
    print("=" * 70)
    
    non_english = df[~df['is_english_native_country']]
    
    native_lang_dist = non_english[non_english['is_using_native_language']]['cultural_distance']
    english_lang_dist = non_english[non_english['is_english']]['cultural_distance']
    
    print(f"\n   使用官方语言: {native_lang_dist.mean():.4f} ± {native_lang_dist.std():.4f} (N={len(native_lang_dist)})")
    print(f"   使用英语: {english_lang_dist.mean():.4f} ± {english_lang_dist.std():.4f} (N={len(english_lang_dist)})")
    
    # 简单t检验（非配对）
    t_stat, p_value = stats.ttest_ind(native_lang_dist, english_lang_dist)
    print(f"\n   独立样本t检验: t={t_stat:.4f}, p={p_value:.6f}")
    
    return native_lang_dist, english_lang_dist


def overall_statistics(df):
    """整体统计检验"""
    print("\n" + "=" * 70)
    print("📈 整体统计检验（配对分析）")
    print("=" * 70)
    
    non_english = df[~df['is_english_native_country']]
    
    # 收集配对数据
    paired_data = []
    for country in non_english['country'].unique():
        country_data = non_english[non_english['country'] == country]
        native_lang = country_data['native_language'].iloc[0]
        cultural_region = country_data.get('cultural_region', pd.Series(['Unknown'])).iloc[0] if 'cultural_region' in country_data.columns else 'Unknown'
        
        for model in country_data['model'].unique():
            model_data = country_data[country_data['model'] == model]
            native_dist = model_data[model_data['language'] == native_lang]['cultural_distance'].values
            english_dist = model_data[model_data['is_english']]['cultural_distance'].values
            
            if len(native_dist) > 0 and len(english_dist) > 0:
                eng_adv = (native_dist[0] - english_dist[0]) / native_dist[0] * 100 if native_dist[0] > 0 else 0
                paired_data.append({
                    'country': country,
                    'model': model,
                    'native_language': native_lang,
                    'cultural_region': cultural_region,
                    'native_dist': native_dist[0],
                    'english_dist': english_dist[0],
                    'english_advantage': eng_adv
                })
    
    paired_df = pd.DataFrame(paired_data)
    native_dists = paired_df['native_dist'].values
    english_dists = paired_df['english_dist'].values
    differences = native_dists - english_dists  # 正值=英语更好
    
    # 用平均距离计算英语优势（正确方式，避免极端值）
    avg_native = native_dists.mean()
    avg_english = english_dists.mean()
    english_advantage_pct = (avg_native - avg_english) / avg_native * 100
    
    print(f"\n配对样本数: {len(paired_df)}")
    print(f"官方语言平均距离: {avg_native:.4f} ± {native_dists.std():.4f}")
    print(f"英语平均距离: {avg_english:.4f} ± {english_dists.std():.4f}")
    print(f"英语优势（基于平均距离）: {english_advantage_pct:+.1f}%")
    
    english_better = (differences > 0).sum()
    native_better = (differences < 0).sum()
    print(f"\n英语更好的配对: {english_better} ({english_better/len(differences)*100:.1f}%)")
    print(f"官方语言更好的配对: {native_better} ({native_better/len(differences)*100:.1f}%)")
    
    # 统计检验
    print("\n--- 统计检验 ---")
    t_stat, p_value = stats.ttest_rel(native_dists, english_dists)
    print(f"配对t检验: t={t_stat:.4f}, p={p_value:.6f}")
    
    from scipy.stats import wilcoxon
    w_stat, w_pvalue = wilcoxon(native_dists, english_dists)
    print(f"Wilcoxon检验: W={w_stat:.2f}, p={w_pvalue:.6f}")
    
    n_total = english_better + native_better
    result = binomtest(english_better, n_total, 0.5, alternative='two-sided')
    print(f"符号检验: p={result.pvalue:.6f}")
    
    # Cohen's d
    pooled_std = np.sqrt((native_dists.std()**2 + english_dists.std()**2) / 2)
    cohens_d = (native_dists.mean() - english_dists.mean()) / pooled_std
    print(f"Cohen's d: {cohens_d:.4f}")
    
    if p_value < 0.05:
        if english_dists.mean() < native_dists.mean():
            print("\n→ 结论: 英语显著优于官方语言 *")
        else:
            print("\n→ 结论: 官方语言显著优于英语 *")
    else:
        print("\n→ 结论: 两种语言无显著差异")
    
    return paired_df


def analyze_english_advantage_ranking(paired_df):
    """英语优势排名分析"""
    print("\n" + "=" * 70)
    print("📊 英语优势排名")
    print("=" * 70)
    
    # 按国家平均（先算平均距离，再用平均距离计算英语优势，避免极端值）
    avg_advantage = paired_df.groupby(['country', 'native_language']).agg({
        'native_dist': 'mean',
        'english_dist': 'mean'
    }).reset_index()
    # 用平均距离计算英语优势（正确方式）
    avg_advantage['english_advantage'] = (avg_advantage['native_dist'] - avg_advantage['english_dist']) / avg_advantage['native_dist'] * 100
    avg_advantage = avg_advantage.sort_values('english_advantage', ascending=False)
    
    print("\n   Top 10 英语优势（英语更好）:")
    for i, (_, row) in enumerate(avg_advantage.head(10).iterrows(), 1):
        print(f"   {i:2d}. {row['country']:30s} ({row['native_language']:6s}): {row['english_advantage']:+6.1f}%")
    
    print("\n   Top 10 母语优势（母语更好）:")
    native_adv = avg_advantage.nsmallest(10, 'english_advantage')
    for i, (_, row) in enumerate(native_adv.iterrows(), 1):
        print(f"   {i:2d}. {row['country']:30s} ({row['native_language']:6s}): {row['english_advantage']:+6.1f}%")
    
    return avg_advantage


def analyze_country_controlled_effect(paired_df):
    """控制国家效应后的语言效应"""
    print("\n" + "=" * 70)
    print("📊 控制国家效应后的语言效应")
    print("=" * 70)
    
    country_effects = []
    for country in paired_df['country'].unique():
        country_data = paired_df[paired_df['country'] == country]
        native_lang = country_data['native_language'].iloc[0]
        
        native_dist = country_data['native_dist'].mean()
        english_dist = country_data['english_dist'].mean()
        country_mean = (native_dist + english_dist) / 2
        
        # 相对于国家平均的效应
        native_effect = native_dist - country_mean
        english_effect = english_dist - country_mean
        
        country_effects.append({
            'country': country,
            'native_lang': native_lang,
            'native_effect': native_effect,
            'english_effect': english_effect,
            'diff': english_effect - native_effect
        })
    
    effects_df = pd.DataFrame(country_effects)
    print(f"\n   国家数: {len(effects_df)}")
    print(f"   英语相对效应平均: {effects_df['english_effect'].mean():.4f}")
    print(f"   官方语言相对效应平均: {effects_df['native_effect'].mean():.4f}")
    
    t_stat, p_value = stats.ttest_rel(effects_df['native_effect'], effects_df['english_effect'])
    print(f"   配对t检验: t={t_stat:.2f}, p={p_value:.4f}")
    
    eng_better = (effects_df['diff'] < 0).sum()
    print(f"   英语相对更好的国家: {eng_better}/{len(effects_df)} ({eng_better/len(effects_df)*100:.1f}%)")
    
    return effects_df


def analyze_cultural_region_stats(paired_df):
    """按文化区域统计英语优势"""
    print("\n" + "=" * 70)
    print("📊 按文化区域统计英语优势")
    print("=" * 70)
    
    if 'cultural_region' not in paired_df.columns or paired_df['cultural_region'].isna().all():
        print("   ⚠️ 无文化区域数据")
        return None
    
    region_stats = paired_df.groupby('cultural_region').agg({
        'english_advantage': ['mean', 'std', 'count'],
        'native_dist': 'mean',
        'english_dist': 'mean'
    })
    region_stats.columns = ['mean_advantage', 'std_advantage', 'count', 'mean_native_dist', 'mean_english_dist']
    region_stats = region_stats.sort_values('mean_advantage', ascending=False)
    
    for region, row in region_stats.iterrows():
        if pd.notna(region) and region != 'Unknown':
            print(f"   {region:25s}: {row['mean_advantage']:+6.1f}% ± {row['std_advantage']:.1f}% (N={int(row['count'])})")
    
    return region_stats


def save_results(family_stats, western_stats, arabic_stats, orientalism_df, model_stats, paired_df, 
                 avg_advantage=None, country_effects=None, region_stats=None):
    """保存分析结果"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if len(family_stats) > 0:
        family_stats.to_csv(OUTPUT_DIR / 'language_family_stats.csv', index=False)
    if len(western_stats) > 0:
        western_stats.to_csv(OUTPUT_DIR / 'western_vs_non_western.csv', index=False)
    if len(arabic_stats) > 0:
        arabic_stats.to_csv(OUTPUT_DIR / 'arabic_countries_detail.csv', index=False)
    if len(orientalism_df) > 0:
        orientalism_df.to_csv(OUTPUT_DIR / 'orientalism_analysis.csv', index=False)
    if len(model_stats) > 0:
        model_stats.to_csv(OUTPUT_DIR / 'model_effects.csv', index=False)
    if len(paired_df) > 0:
        paired_df.to_csv(OUTPUT_DIR / 'paired_data.csv', index=False)
    if avg_advantage is not None and len(avg_advantage) > 0:
        avg_advantage.to_csv(OUTPUT_DIR / 'english_advantage_average.csv', index=False)
    if country_effects is not None and len(country_effects) > 0:
        country_effects.to_csv(OUTPUT_DIR / 'country_controlled_effects.csv', index=False)
    if region_stats is not None and len(region_stats) > 0:
        region_stats.to_csv(OUTPUT_DIR / 'cultural_region_stats.csv')
    
    print(f"\n✅ 结果已保存到: {OUTPUT_DIR}")


def main():
    print("=" * 70)
    print("Stage0 vs Stage3 文化距离分析 - 使用预计算CSV数据")
    print("=" * 70)
    
    # 加载数据
    df = load_data()
    
    # 英语母语国家基准分析
    english_native_baseline = analyze_english_native_baseline(df)
    
    # 非英语国家整体对比
    analyze_native_vs_english_overall(df)
    
    # 分析
    family_stats = analyze_language_family(df)
    western_stats = analyze_western_vs_non_western(df)
    arabic_stats = analyze_arabic_countries(df)
    orientalism_df = analyze_orientalism_effect(df)
    model_stats = analyze_by_model(df)
    paired_df = overall_statistics(df)
    
    # 新增分析
    avg_advantage = analyze_english_advantage_ranking(paired_df)
    country_effects = analyze_country_controlled_effect(paired_df)
    region_stats = analyze_cultural_region_stats(paired_df)
    
    # 保存结果
    save_results(family_stats, western_stats, arabic_stats, orientalism_df, model_stats, paired_df,
                 avg_advantage, country_effects, region_stats)
    
    # 核心发现汇总
    print("\n" + "=" * 70)
    print("✅ 分析完成！核心发现汇总:")
    print("=" * 70)
    if len(paired_df) > 0:
        native_dists = paired_df['native_dist'].values
        english_dists = paired_df['english_dist'].values
        differences = native_dists - english_dists
        english_better = (differences > 0).sum()
        native_better = (differences < 0).sum()
        
        # 使用平均距离计算英语优势（更稳健，不受极端值影响）
        avg_native = native_dists.mean()
        avg_english = english_dists.mean()
        english_advantage_robust = (avg_native - avg_english) / avg_native * 100
        
        print(f"  - 官方语言平均距离: {avg_native:.4f}")
        print(f"  - 英语平均距离: {avg_english:.4f}")
        print(f"  - 英语优势（基于平均距离）: {english_advantage_robust:+.1f}%")
        print(f"  - 英语优势（中位数）: {paired_df['english_advantage'].median():+.1f}%")
        print(f"  - 英语更好的配对数: {english_better} ({english_better/len(differences)*100:.1f}%)")
        print(f"  - 母语更好的配对数: {native_better} ({native_better/len(differences)*100:.1f}%)")


if __name__ == '__main__':
    main()
