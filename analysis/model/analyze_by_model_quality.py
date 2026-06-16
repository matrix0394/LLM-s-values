"""按模型质量分层分析语言效应"""
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('results/roleplay_multilingual/cultural_distance_analysis.csv')

print("="*60)
print("📊 按模型质量分层分析")
print("="*60)

# 非英语国家数据
non_english = df[~df['is_english_native_country']]

# 1. 按模型分组看语言效应
print("\n--- 1. 每个模型的语言效应 ---")
model_effects = []
for model in non_english['model'].unique():
    model_data = non_english[non_english['model'] == model]
    
    native_dist = model_data[model_data['is_using_native_language']]['cultural_distance'].mean()
    english_dist = model_data[model_data['is_english']]['cultural_distance'].mean()
    overall_dist = model_data['cultural_distance'].mean()
    
    if pd.notna(native_dist) and pd.notna(english_dist):
        diff = english_dist - native_dist  # 负值=英语更好
        model_effects.append({
            'model': model,
            'overall_dist': overall_dist,
            'native_dist': native_dist,
            'english_dist': english_dist,
            'diff': diff,
            'english_better': diff < 0
        })

effects_df = pd.DataFrame(model_effects).sort_values('overall_dist')
print(effects_df.to_string(index=False))

# 2. 排除表现差的模型（整体距离>3）
print("\n--- 2. 排除低质量模型后的分析 ---")
good_models = effects_df[effects_df['overall_dist'] < 3]['model'].tolist()
bad_models = effects_df[effects_df['overall_dist'] >= 3]['model'].tolist()

print(f"高质量模型 (距离<3): {len(good_models)}个")
print(f"低质量模型 (距离>=3): {bad_models}")

# 高质量模型的语言效应
good_effects = effects_df[effects_df['overall_dist'] < 3]
english_better_count = good_effects['english_better'].sum()
native_better_count = len(good_effects) - english_better_count

print(f"\n高质量模型中:")
print(f"  英语更好: {english_better_count}个 ({english_better_count/len(good_effects)*100:.1f}%)")
print(f"  官方语言更好: {native_better_count}个 ({native_better_count/len(good_effects)*100:.1f}%)")
print(f"  平均差异 (英语-官方语言): {good_effects['diff'].mean():.4f}")

# 3. 用高质量模型数据做配对t检验
print("\n--- 3. 高质量模型的统计检验 ---")
good_data = non_english[non_english['model'].isin(good_models)]

paired_data = []
for country in good_data['country'].unique():
    country_data = good_data[good_data['country'] == country]
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

english_better = (differences > 0).sum()
native_better = (differences < 0).sum()
print(f"\n英语更好的配对: {english_better} ({english_better/len(differences)*100:.1f}%)")
print(f"官方语言更好的配对: {native_better} ({native_better/len(differences)*100:.1f}%)")

t_stat, p_value = stats.ttest_rel(native_dists, english_dists)
print(f"\n配对t检验: t={t_stat:.4f}, p={p_value:.6f}")

w_stat, w_pvalue = stats.wilcoxon(native_dists, english_dists)
print(f"Wilcoxon检验: W={w_stat:.2f}, p={w_pvalue:.6f}")

if p_value < 0.05:
    if english_dists.mean() < native_dists.mean():
        print("→ 英语显著更好 *")
    else:
        print("→ 官方语言显著更好 *")
else:
    print("→ 无显著差异")

# 4. 按模型能力分层（前50%最好的模型）
print("\n--- 4. 按模型能力分层分析 ---")
median_dist = effects_df['overall_dist'].median()
top_models = effects_df[effects_df['overall_dist'] <= median_dist]['model'].tolist()
bottom_models = effects_df[effects_df['overall_dist'] > median_dist]['model'].tolist()

print(f"Top 50% 模型 (距离<={median_dist:.2f}): {len(top_models)}个")
print(f"Bottom 50% 模型: {len(bottom_models)}个")

for group_name, models in [("Top 50%", top_models), ("Bottom 50%", bottom_models)]:
    group_effects = effects_df[effects_df['model'].isin(models)]
    eng_better = group_effects['english_better'].sum()
    print(f"\n{group_name}:")
    print(f"  英语更好: {eng_better}/{len(group_effects)} ({eng_better/len(group_effects)*100:.1f}%)")
    print(f"  平均差异: {group_effects['diff'].mean():.4f}")

# 5. 只看"正常"模型（排除qwen3-1.7b和llama-3.2-3b）
print("\n--- 5. 排除异常模型后的分析 ---")
outlier_models = ['qwen3-1.7b', 'llama-3.2-3b-instruct']
normal_models = [m for m in effects_df['model'].tolist() if m not in outlier_models]

normal_effects = effects_df[effects_df['model'].isin(normal_models)]
eng_better = normal_effects['english_better'].sum()
print(f"正常模型数: {len(normal_models)}")
print(f"英语更好: {eng_better}/{len(normal_effects)} ({eng_better/len(normal_effects)*100:.1f}%)")
print(f"平均差异 (英语-官方语言): {normal_effects['diff'].mean():.4f}")

# 对正常模型做统计检验
normal_data = non_english[non_english['model'].isin(normal_models)]
paired_normal = []
for country in normal_data['country'].unique():
    country_data = normal_data[normal_data['country'] == country]
    native_lang = country_data['native_language'].iloc[0]
    
    for model in country_data['model'].unique():
        model_data = country_data[country_data['model'] == model]
        native_dist = model_data[model_data['language'] == native_lang]['cultural_distance'].values
        english_dist = model_data[model_data['is_english']]['cultural_distance'].values
        
        if len(native_dist) > 0 and len(english_dist) > 0:
            paired_normal.append((native_dist[0], english_dist[0]))

if paired_normal:
    native_arr = np.array([p[0] for p in paired_normal])
    english_arr = np.array([p[1] for p in paired_normal])
    diff_arr = native_arr - english_arr
    
    t_stat, p_value = stats.ttest_rel(native_arr, english_arr)
    print(f"\n配对样本数: {len(paired_normal)}")
    print(f"官方语言平均: {native_arr.mean():.4f}, 英语平均: {english_arr.mean():.4f}")
    print(f"配对t检验: t={t_stat:.4f}, p={p_value:.6f}")
    
    eng_better = (diff_arr > 0).sum()
    print(f"英语更好的配对: {eng_better}/{len(diff_arr)} ({eng_better/len(diff_arr)*100:.1f}%)")

print("\n" + "="*60)
