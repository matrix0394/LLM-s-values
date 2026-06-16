"""
补充分析：为论文提供更多支撑证据
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr, mannwhitneyu
import warnings
warnings.filterwarnings('ignore')

# 加载数据
df = pd.read_csv('results/roleplay_multilingual/cultural_distance_analysis.csv')
bad_models = ['qwen3-1.7b', 'llama-3.2-3b-instruct']
df = df[~df['model'].isin(bad_models)]
non_english = df[~df['is_english_native_country']]

print("="*70)
print("📊 补充分析：论文支撑材料")
print("="*70)

# ============================================================
# 1. 混合效应模型分析
# ============================================================
print("\n" + "="*70)
print("1. 混合效应模型分析 (控制国家和模型随机效应)")
print("="*70)

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import mixedlm
    
    # 准备数据
    model_data = []
    for _, row in non_english.iterrows():
        if row['is_using_native_language'] or row['is_english']:
            lang_type = 'english' if row['is_english'] else 'native'
            model_data.append({
                'distance': row['cultural_distance'],
                'lang_type': lang_type,
                'country': row['country'],
                'model': row['model'],
                'native_lang': row['native_language']
            })
    
    model_df = pd.DataFrame(model_data)
    model_df['is_english'] = (model_df['lang_type'] == 'english').astype(int)
    
    # 混合效应模型
    md = mixedlm("distance ~ is_english", model_df, groups=model_df["country"])
    mdf = md.fit()
    print("\n混合效应模型 (随机效应: 国家):")
    print(f"  英语效应系数: {mdf.fe_params['is_english']:.4f}")
    print(f"  标准误: {mdf.bse['is_english']:.4f}")
    print(f"  z值: {mdf.tvalues['is_english']:.4f}")
    print(f"  p值: {mdf.pvalues['is_english']:.6f}")
    
except ImportError:
    print("需要安装 statsmodels: pip install statsmodels")

# ============================================================
# 2. 伊斯兰国家 vs 非伊斯兰国家的详细对比
# ============================================================
print("\n" + "="*70)
print("2. 伊斯兰国家 vs 非伊斯兰国家详细对比")
print("="*70)

# 使用数据中的Islamic标记
islamic_data = df[df['country'].isin(['Algeria', 'Palestine', 'Iraq', 'Jordan', 'Kuwait', 
                                       'Lebanon', 'Libya', 'Morocco', 'Qatar', 'Tunisia', 
                                       'Egypt', 'Yemen', 'Azerbaijan', 'Bangladesh', 'Indonesia',
                                       'Iran', 'Malaysia', 'Pakistan', 'Turkey'])]
non_islamic_data = df[~df['country'].isin(['Algeria', 'Palestine', 'Iraq', 'Jordan', 'Kuwait', 
                                            'Lebanon', 'Libya', 'Morocco', 'Qatar', 'Tunisia', 
                                            'Egypt', 'Yemen', 'Azerbaijan', 'Bangladesh', 'Indonesia',
                                            'Iran', 'Malaysia', 'Pakistan', 'Turkey'])]

print(f"\n伊斯兰国家数据: {len(islamic_data)} 条")
print(f"非伊斯兰国家数据: {len(non_islamic_data)} 条")

# 计算英语优势
def calc_english_advantage(data):
    advantages = []
    for country in data['country'].unique():
        c_data = data[data['country'] == country]
        if c_data['is_english_native_country'].iloc[0]:
            continue
        native_lang = c_data['native_language'].iloc[0]
        native_dist = c_data[c_data['language'] == native_lang]['cultural_distance'].mean()
        english_dist = c_data[c_data['is_english']]['cultural_distance'].mean()
        if pd.notna(native_dist) and pd.notna(english_dist) and native_dist > 0:
            advantages.append((native_dist - english_dist) / native_dist * 100)
    return advantages

islamic_adv = calc_english_advantage(islamic_data)
non_islamic_adv = calc_english_advantage(non_islamic_data)

if islamic_adv and non_islamic_adv:
    print(f"\n伊斯兰国家英语优势: {np.mean(islamic_adv):+.2f}% (n={len(islamic_adv)})")
    print(f"非伊斯兰国家英语优势: {np.mean(non_islamic_adv):+.2f}% (n={len(non_islamic_adv)})")
    
    t_stat, p_value = stats.ttest_ind(islamic_adv, non_islamic_adv)
    print(f"独立样本t检验: t={t_stat:.2f}, p={p_value:.6f}")
    
    # Mann-Whitney U检验（非参数）
    u_stat, u_pvalue = mannwhitneyu(islamic_adv, non_islamic_adv, alternative='two-sided')
    print(f"Mann-Whitney U检验: U={u_stat:.0f}, p={u_pvalue:.6f}")

# ============================================================
# 3. 模型规模与东方主义效应的关系
# ============================================================
print("\n" + "="*70)
print("3. 模型规模与东方主义效应")
print("="*70)

# 模型规模估计（参数量）
model_sizes = {
    'claude-3-7-sonnet-20250219': 70,  # 估计
    'claude-sonnet-4.5': 70,
    'gpt-4o': 200,  # 估计
    'gpt-4o-mini': 8,
    'gpt-5.1': 200,
    'deepseek-chat': 67,
    'deepseek-chat-v3.1': 67,
    'qwen3-max': 72,
    'kimi-k2': 70,
    'gemini-2.5-flash': 50,
    'gemini-2.5-pro': 100,
    'gemini-3-pro-preview': 100,
    'gemma-3-4b-it': 4,
    'llama-3.3-70b-instruct': 70,
    'grok-4.1-fast': 50,
    'mistral-medium-3.1': 22,
    'mistral-nemo': 12,
    'phi-3-mini-128k-instruct': 3.8,
}

# 计算每个模型的东方主义效应（阿拉伯国家）
arabic_data = non_english[non_english['native_language'] == 'ar']
model_orientalism = []

for model in arabic_data['model'].unique():
    if model not in model_sizes:
        continue
    m_data = arabic_data[arabic_data['model'] == model]
    native_dist = m_data[m_data['language'] == 'ar']['cultural_distance'].mean()
    english_dist = m_data[m_data['is_english']]['cultural_distance'].mean()
    
    if pd.notna(native_dist) and pd.notna(english_dist) and native_dist > 0:
        adv = (native_dist - english_dist) / native_dist * 100
        model_orientalism.append({
            'model': model,
            'size': model_sizes[model],
            'orientalism': adv
        })

if model_orientalism:
    orient_df = pd.DataFrame(model_orientalism)
    corr, p = pearsonr(orient_df['size'], orient_df['orientalism'])
    print(f"\n模型规模 vs 东方主义效应:")
    print(f"  Pearson相关: r={corr:.3f}, p={p:.4f}")
    
    # 按规模分组
    small_models = orient_df[orient_df['size'] < 20]
    large_models = orient_df[orient_df['size'] >= 20]
    print(f"\n小模型 (<20B): 平均东方主义 = {small_models['orientalism'].mean():+.1f}%")
    print(f"大模型 (>=20B): 平均东方主义 = {large_models['orientalism'].mean():+.1f}%")

# ============================================================
# 4. PC1 vs PC2 维度分析
# ============================================================
print("\n" + "="*70)
print("4. PC1 vs PC2 维度分析")
print("="*70)

# 分别计算PC1和PC2的距离
def calc_dimension_distances(data):
    results = []
    for country in data['country'].unique():
        c_data = data[data['country'] == country]
        if c_data['is_english_native_country'].iloc[0]:
            continue
        native_lang = c_data['native_language'].iloc[0]
        
        native_rows = c_data[c_data['language'] == native_lang]
        english_rows = c_data[c_data['is_english']]
        
        if len(native_rows) == 0 or len(english_rows) == 0:
            continue
        
        real_pc1 = c_data['stage0_pc1'].iloc[0]
        real_pc2 = c_data['stage0_pc2'].iloc[0]
        
        native_pc1_dist = abs(native_rows['stage3_pc1'].mean() - real_pc1)
        native_pc2_dist = abs(native_rows['stage3_pc2'].mean() - real_pc2)
        english_pc1_dist = abs(english_rows['stage3_pc1'].mean() - real_pc1)
        english_pc2_dist = abs(english_rows['stage3_pc2'].mean() - real_pc2)
        
        results.append({
            'country': country,
            'native_lang': native_lang,
            'pc1_english_adv': (native_pc1_dist - english_pc1_dist) / native_pc1_dist * 100 if native_pc1_dist > 0 else 0,
            'pc2_english_adv': (native_pc2_dist - english_pc2_dist) / native_pc2_dist * 100 if native_pc2_dist > 0 else 0
        })
    return pd.DataFrame(results)

dim_df = calc_dimension_distances(non_english)

print(f"\nPC1 (Survival vs Self-expression) 英语优势: {dim_df['pc1_english_adv'].mean():+.1f}%")
print(f"PC2 (Traditional vs Secular) 英语优势: {dim_df['pc2_english_adv'].mean():+.1f}%")

# 按区域分析
arabic_countries = ['Algeria', 'Palestine', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
                    'Libya', 'Morocco', 'Qatar', 'Tunisia', 'Egypt', 'Yemen']
arabic_dim = dim_df[dim_df['country'].isin(arabic_countries)]
print(f"\n阿拉伯国家:")
print(f"  PC1英语优势: {arabic_dim['pc1_english_adv'].mean():+.1f}%")
print(f"  PC2英语优势: {arabic_dim['pc2_english_adv'].mean():+.1f}%")

# ============================================================
# 5. 稳健性检验：不同距离度量
# ============================================================
print("\n" + "="*70)
print("5. 稳健性检验：不同距离度量")
print("="*70)

def calc_manhattan_distance(row):
    return abs(row['stage3_pc1'] - row['stage0_pc1']) + abs(row['stage3_pc2'] - row['stage0_pc2'])

def calc_chebyshev_distance(row):
    return max(abs(row['stage3_pc1'] - row['stage0_pc1']), abs(row['stage3_pc2'] - row['stage0_pc2']))

# 添加其他距离度量
non_english_copy = non_english.copy()
non_english_copy['manhattan_dist'] = non_english_copy.apply(calc_manhattan_distance, axis=1)
non_english_copy['chebyshev_dist'] = non_english_copy.apply(calc_chebyshev_distance, axis=1)

for dist_name, dist_col in [('Euclidean', 'cultural_distance'), 
                             ('Manhattan', 'manhattan_dist'), 
                             ('Chebyshev', 'chebyshev_dist')]:
    # 计算阿拉伯国家的英语优势
    arabic_data = non_english_copy[non_english_copy['native_language'] == 'ar']
    native_dist = arabic_data[arabic_data['language'] == 'ar'][dist_col].mean()
    english_dist = arabic_data[arabic_data['is_english']][dist_col].mean()
    adv = (native_dist - english_dist) / native_dist * 100 if native_dist > 0 else 0
    print(f"{dist_name}距离 - 阿拉伯国家英语优势: {adv:+.1f}%")

# ============================================================
# 6. 时间效应：新模型 vs 旧模型
# ============================================================
print("\n" + "="*70)
print("6. 模型代际分析")
print("="*70)

# 按发布时间分组
older_models = ['gpt-4o', 'gpt-4o-mini', 'claude-3-7-sonnet-20250219', 'deepseek-chat',
                'gemini-2.5-flash', 'llama-3.3-70b-instruct', 'mistral-nemo']
newer_models = ['claude-sonnet-4.5', 'gpt-5.1', 'deepseek-chat-v3.1', 'qwen3-max',
                'gemini-2.5-pro', 'gemini-3-pro-preview', 'kimi-k2', 'grok-4.1-fast']

def calc_model_group_orientalism(models, data):
    group_data = data[data['model'].isin(models)]
    arabic_group = group_data[group_data['native_language'] == 'ar']
    native_dist = arabic_group[arabic_group['language'] == 'ar']['cultural_distance'].mean()
    english_dist = arabic_group[arabic_group['is_english']]['cultural_distance'].mean()
    return (native_dist - english_dist) / native_dist * 100 if native_dist > 0 else 0

older_orient = calc_model_group_orientalism(older_models, non_english)
newer_orient = calc_model_group_orientalism(newer_models, non_english)

print(f"较早模型东方主义效应: {older_orient:+.1f}%")
print(f"较新模型东方主义效应: {newer_orient:+.1f}%")
print(f"变化: {newer_orient - older_orient:+.1f}%")

# ============================================================
# 7. Bootstrap置信区间
# ============================================================
print("\n" + "="*70)
print("7. Bootstrap置信区间 (95% CI)")
print("="*70)

def bootstrap_english_advantage(data, n_bootstrap=1000):
    """Bootstrap计算英语优势的置信区间"""
    advantages = []
    
    for country in data['country'].unique():
        c_data = data[data['country'] == country]
        native_lang = c_data['native_language'].iloc[0]
        
        for model in c_data['model'].unique():
            m_data = c_data[c_data['model'] == model]
            native_dist = m_data[m_data['language'] == native_lang]['cultural_distance'].values
            english_dist = m_data[m_data['is_english']]['cultural_distance'].values
            
            if len(native_dist) > 0 and len(english_dist) > 0:
                adv = (native_dist[0] - english_dist[0]) / native_dist[0] * 100 if native_dist[0] > 0 else 0
                advantages.append(adv)
    
    advantages = np.array(advantages)
    
    # Bootstrap
    boot_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(advantages, size=len(advantages), replace=True)
        boot_means.append(np.mean(sample))
    
    ci_low = np.percentile(boot_means, 2.5)
    ci_high = np.percentile(boot_means, 97.5)
    
    return np.mean(advantages), ci_low, ci_high

# 阿拉伯国家
arabic_data = non_english[non_english['native_language'] == 'ar']
mean, ci_low, ci_high = bootstrap_english_advantage(arabic_data)
print(f"阿拉伯国家英语优势: {mean:+.1f}% [95% CI: {ci_low:+.1f}%, {ci_high:+.1f}%]")

# 西欧国家
western_countries = ['Austria', 'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg',
                     'Portugal', 'Spain', 'Switzerland']
western_data = non_english[non_english['country'].isin(western_countries)]
mean, ci_low, ci_high = bootstrap_english_advantage(western_data)
print(f"西欧国家英语优势: {mean:+.1f}% [95% CI: {ci_low:+.1f}%, {ci_high:+.1f}%]")

# ============================================================
# 8. 多重比较校正
# ============================================================
print("\n" + "="*70)
print("8. 多重比较校正 (Bonferroni)")
print("="*70)

# 收集所有语言家族的p值
lang_families = {
    'Arabic': ['ar'],
    'Russian': ['ru'],
    'Romance': ['es', 'fr', 'it', 'pt'],
    'Germanic': ['de'],
    'CJK': ['zh-cn', 'ja', 'ko']
}

p_values = []
for family, langs in lang_families.items():
    family_data = non_english[non_english['native_language'].isin(langs)]
    
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
    
    if len(paired) >= 5:
        native_arr = np.array([p[0] for p in paired])
        english_arr = np.array([p[1] for p in paired])
        t_stat, p_value = stats.ttest_rel(native_arr, english_arr)
        p_values.append((family, p_value))

# Bonferroni校正
n_tests = len(p_values)
alpha = 0.05
bonferroni_alpha = alpha / n_tests

print(f"测试数量: {n_tests}")
print(f"Bonferroni校正后α: {bonferroni_alpha:.4f}")
print("\n校正后结果:")
for family, p in p_values:
    sig = "***" if p < bonferroni_alpha/10 else ("**" if p < bonferroni_alpha/2 else ("*" if p < bonferroni_alpha else ""))
    print(f"  {family}: p={p:.6f} {sig}")

# ============================================================
# 9. 效应量汇总表
# ============================================================
print("\n" + "="*70)
print("9. 效应量汇总表 (Table for Paper)")
print("="*70)

print("\n| Region | N | English Adv (%) | 95% CI | Cohen's d | p-value |")
print("|--------|---|-----------------|--------|-----------|---------|")

regions = {
    'Islamic/Arab': ['Algeria', 'Palestine', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
                     'Libya', 'Morocco', 'Qatar', 'Tunisia', 'Egypt', 'Yemen'],
    'Orthodox': ['Russian Federation', 'Belarus', 'Kazakhstan', 'Kyrgyzstan'],
    'Latin America': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador',
                      'Guatemala', 'Haiti', 'Mexico', 'Nicaragua', 'Peru', 'Uruguay', 'Venezuela'],
    'Western Europe': ['Austria', 'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg',
                       'Portugal', 'Spain', 'Switzerland'],
    'East Asia': ['China', 'Japan', 'Korea, Republic of', 'Macao']
}

for region, countries in regions.items():
    region_data = non_english[non_english['country'].isin(countries)]
    
    paired = []
    for country in region_data['country'].unique():
        c_data = region_data[region_data['country'] == country]
        native_lang = c_data['native_language'].iloc[0]
        
        for model in c_data['model'].unique():
            m_data = c_data[c_data['model'] == model]
            native_dist = m_data[m_data['language'] == native_lang]['cultural_distance'].values
            english_dist = m_data[m_data['is_english']]['cultural_distance'].values
            
            if len(native_dist) > 0 and len(english_dist) > 0:
                paired.append((native_dist[0], english_dist[0]))
    
    if len(paired) >= 5:
        native_arr = np.array([p[0] for p in paired])
        english_arr = np.array([p[1] for p in paired])
        diff = native_arr - english_arr
        
        mean_adv = diff.mean() / native_arr.mean() * 100
        se = diff.std() / np.sqrt(len(diff))
        ci_low = (diff.mean() - 1.96*se) / native_arr.mean() * 100
        ci_high = (diff.mean() + 1.96*se) / native_arr.mean() * 100
        
        pooled_std = np.sqrt((native_arr.std()**2 + english_arr.std()**2) / 2)
        cohens_d = diff.mean() / pooled_std
        
        t_stat, p_value = stats.ttest_rel(native_arr, english_arr)
        
        p_str = f"{p_value:.4f}" if p_value >= 0.0001 else "<0.0001"
        print(f"| {region} | {len(paired)} | {mean_adv:+.1f} | [{ci_low:+.1f}, {ci_high:+.1f}] | {cohens_d:.2f} | {p_str} |")

print("\n" + "="*70)
print("✅ 补充分析完成")
print("="*70)
