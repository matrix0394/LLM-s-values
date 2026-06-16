"""快速分析cultural_distance_analysis.csv的结果"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import binomtest

# 读取数据
df = pd.read_csv('results/roleplay_multilingual/cultural_distance_analysis.csv')

print("="*60)
print("📊 文化距离分析结果汇总")
print("="*60)

print(f"\n总记录数: {len(df)}")
print(f"国家数: {df['country'].nunique()}")
print(f"模型数: {df['model'].nunique()}")
print(f"语言数: {df['language'].nunique()}")

# 1. 整体统计
print("\n--- 1. 整体统计 ---")
print(f"平均文化距离: {df['cultural_distance'].mean():.4f}")
print(f"中位数: {df['cultural_distance'].median():.4f}")
print(f"标准差: {df['cultural_distance'].std():.4f}")

# 2. 非英语国家：官方语言 vs 英语
print("\n--- 2. 非英语国家：官方语言 vs 英语 ---")
non_english = df[~df['is_english_native_country']]

using_native = non_english[non_english['is_using_native_language']]
using_english = non_english[non_english['is_english']]

print(f"使用官方语言: {len(using_native)} 条, 平均距离: {using_native['cultural_distance'].mean():.4f}")
print(f"使用英语: {len(using_english)} 条, 平均距离: {using_english['cultural_distance'].mean():.4f}")

# 3. 按国家对比
print("\n--- 3. 按国家对比 ---")
country_comparison = []
for country in non_english['country'].unique():
    country_data = non_english[non_english['country'] == country]
    native_lang = country_data['native_language'].iloc[0]
    
    native_dist = country_data[country_data['language'] == native_lang]['cultural_distance'].mean()
    english_dist = country_data[country_data['is_english']]['cultural_distance'].mean()
    
    if pd.notna(native_dist) and pd.notna(english_dist) and native_dist > 0:
        abs_diff = english_dist - native_dist
        pct_adv = (native_dist - english_dist) / native_dist * 100
        country_comparison.append({
            'country': country,
            'native_lang': native_lang,
            'native_dist': native_dist,
            'english_dist': english_dist,
            'abs_diff': abs_diff,
            'pct_adv': pct_adv,
            'better': 'native' if native_dist < english_dist else 'english'
        })

comp_df = pd.DataFrame(country_comparison)
native_better = (comp_df['abs_diff'] > 0).sum()
english_better = (comp_df['abs_diff'] < 0).sum()

print(f"官方语言更好的国家: {native_better}")
print(f"英语更好的国家: {english_better}")
print(f"\n平均绝对差异 (英语-官方语言): {comp_df['abs_diff'].mean():.4f}")
print(f"平均英语优势%: {comp_df['pct_adv'].mean():+.2f}%")

# 4. 配对t检验
print("\n--- 4. 统计显著性检验 ---")
paired_data = []
for country in non_english['country'].unique():
    country_data = non_english[non_english['country'] == country]
    native_lang = country_data['native_language'].iloc[0]
    
    for model in country_data['model'].unique():
        model_data = country_data[country_data['model'] == model]
        native_dist = model_data[model_data['language'] == native_lang]['cultural_distance'].values
        english_dist = model_data[model_data['is_english']]['cultural_distance'].values
        
        if len(native_dist) > 0 and len(english_dist) > 0:
            paired_data.append({
                'country': country,
                'model': model,
                'native_dist': native_dist[0],
                'english_dist': english_dist[0]
            })

paired_df = pd.DataFrame(paired_data)
native_dists = paired_df['native_dist'].values
english_dists = paired_df['english_dist'].values
differences = native_dists - english_dists

print(f"配对样本数: {len(paired_df)}")
print(f"官方语言平均距离: {native_dists.mean():.4f}")
print(f"英语平均距离: {english_dists.mean():.4f}")
print(f"平均差异 (官方语言-英语): {differences.mean():.4f}")

# 配对t检验
t_stat, p_value = stats.ttest_rel(native_dists, english_dists)
print(f"\n配对t检验: t={t_stat:.4f}, p={p_value:.6f}")

# Wilcoxon检验
w_stat, w_pvalue = stats.wilcoxon(native_dists, english_dists)
print(f"Wilcoxon检验: W={w_stat:.2f}, p={w_pvalue:.6f}")

# 符号检验
english_better_count = (differences > 0).sum()
native_better_count = (differences < 0).sum()
n_total = english_better_count + native_better_count
result = binomtest(english_better_count, n_total, 0.5, alternative='two-sided')
print(f"符号检验: 英语更好={english_better_count}, 官方语言更好={native_better_count}, p={result.pvalue:.6f}")

# Cohen's d
pooled_std = np.sqrt((native_dists.std()**2 + english_dists.std()**2) / 2)
cohens_d = (native_dists.mean() - english_dists.mean()) / pooled_std
print(f"\nCohen's d: {cohens_d:.4f}")

# 5. 按语言分组
print("\n--- 5. 按语言分组的英语优势 ---")
lang_adv = comp_df.groupby('native_lang')['pct_adv'].agg(['mean', 'count'])
lang_adv = lang_adv.sort_values('mean', ascending=False)
print(lang_adv)

# 6. 按模型分组
print("\n--- 6. 按模型分组 ---")
model_stats = df.groupby('model')['cultural_distance'].agg(['mean', 'std', 'count'])
model_stats = model_stats.sort_values('mean')
print(model_stats)

# 7. 模型效应 vs 语言效应
print("\n--- 7. 模型效应 vs 语言效应 ---")
model_means = df.groupby('model')['cultural_distance'].mean()
lang_means = df.groupby('language')['cultural_distance'].mean()
model_var = model_means.var()
lang_var = lang_means.var()
print(f"模型效应 (方差): {model_var:.4f}")
print(f"语言效应 (方差): {lang_var:.4f}")
print(f"模型/语言 比值: {model_var/lang_var:.2f}x")

print("\n" + "="*60)
print("✅ 分析完成")
print("="*60)
