"""
Study 4: Colonial History and Contemporary Language Effects (完整版)

核心思路：
1. 东亚比较：香港、澳门(有殖民史) vs 中国大陆、日本、韩国(无殖民史)
2. 拉美比较：不同殖民语言的影响
3. 非洲比较：英国殖民史的影响
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind, ttest_rel, f_oneway
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("Study 4: Colonial History and Contemporary Language Effects")
print("="*80)

# 读取数据
pca_file = 'SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv'
df = pd.read_csv(pca_file)

# 排除低质量模型
bad_models = ['llama-3.2-3b-instruct', 'qwen3-1.7b']
df = df[~df['model_name'].isin(bad_models)]

# 读取IVS真实坐标
ivs_file = 'SI/pca/Table_S5_IVS_PCA_coordinates.csv'
ivs_df = pd.read_csv(ivs_file)
ivs_dict = dict(zip(ivs_df['country'], zip(ivs_df['PC1'], ivs_df['PC2'])))

# 计算文化距离
def calculate_distance(row):
    if row['country'] in ivs_dict:
        ivs_pc1, ivs_pc2 = ivs_dict[row['country']]
        return np.sqrt((row['PC1'] - ivs_pc1)**2 + (row['PC2'] - ivs_pc2)**2)
    return np.nan

df['cultural_distance'] = df.apply(calculate_distance, axis=1)

print(f"\n加载数据: {len(df)} 条记录")
print(f"模型数: {df['model_name'].nunique()}")

# ============================================================================
# Experiment 4a: East Asian Colonial History Comparison
# ============================================================================
print("\n" + "="*80)
print("Experiment 4a: Hong Kong Colonial History Effect")
print("="*80)
print("""
设计: 比较香港(英国殖民) vs 其他东亚国家(无殖民史)
- 香港: 英国殖民(1842-1997)
- 对照组: 中国大陆、日本、韩国(无殖民史)

假设: 香港在英语下应该比其他东亚国家显示更强的优势
因为英国殖民历史导致香港在英语训练数据中有更多表征
""")

# 定义国家和语言
east_asian_countries = {
    'Hong Kong': {'colonial_lang': 'en-native', 'native_lang': 'zh-cn', 'colonial': True, 'colonizer': 'British'},
    'China': {'colonial_lang': 'en', 'native_lang': 'zh-cn', 'colonial': False, 'colonizer': None},
    'Japan': {'colonial_lang': 'en', 'native_lang': 'ja', 'colonial': False, 'colonizer': None},
    'Korea, Republic of': {'colonial_lang': 'en', 'native_lang': 'ko', 'colonial': False, 'colonizer': None}
}

# 收集数据
colonial_effects = []
non_colonial_effects = []

print("\n各国语言效应:")
for country, info in east_asian_countries.items():
    country_data = df[df['country'] == country]
    
    if len(country_data) == 0:
        continue
    
    # 获取殖民语言和母语的距离
    colonial_distances = []
    native_distances = []
    
    for model in country_data['model_name'].unique():
        model_data = country_data[country_data['model_name'] == model]
        
        colonial_dist = model_data[model_data['language'] == info['colonial_lang']]['cultural_distance']
        native_dist = model_data[model_data['language'] == info['native_lang']]['cultural_distance']
        
        if len(colonial_dist) > 0 and len(native_dist) > 0:
            colonial_distances.append(colonial_dist.iloc[0])
            native_distances.append(native_dist.iloc[0])
    
    if len(colonial_distances) > 0:
        colonial_distances = np.array(colonial_distances)
        native_distances = np.array(native_distances)
        
        # 计算效应（母语距离 - 殖民语言距离，正值表示殖民语言更好）
        effect = native_distances - colonial_distances
        
        print(f"\n{country} ({'有殖民史' if info['colonial'] else '无殖民史'}):")
        print(f"  殖民语言({info['colonial_lang']})距离: {colonial_distances.mean():.3f} ± {colonial_distances.std():.3f}")
        print(f"  母语({info['native_lang']})距离: {native_distances.mean():.3f} ± {native_distances.std():.3f}")
        print(f"  效应(母语-殖民语言): {effect.mean():+.3f} ± {effect.std():.3f}")
        print(f"  样本数: {len(effect)}")
        
        # 配对t检验
        t_stat, p_val = ttest_rel(colonial_distances, native_distances)
        if p_val < 0.05:
            if colonial_distances.mean() < native_distances.mean():
                print(f"  ✓ 殖民语言显著优于母语 (p={p_val:.4f})")
            else:
                print(f"  ✗ 母语显著优于殖民语言 (p={p_val:.4f})")
        else:
            print(f"  无显著差异 (p={p_val:.4f})")
        
        # 分组
        if info['colonial']:
            colonial_effects.extend(effect.tolist())
        else:
            non_colonial_effects.extend(effect.tolist())

colonial_effects = np.array(colonial_effects)
non_colonial_effects = np.array(non_colonial_effects)

# 组间比较
print(f"\n" + "="*60)
print("组间比较: 香港 vs 其他东亚国家")
print("="*60)

print(f"\n香港 (英国殖民):")
print(f"  英语效应: {colonial_effects.mean():+.3f} ± {colonial_effects.std():.3f}")
print(f"  样本数: {len(colonial_effects)}")

print(f"\n其他东亚国家 (中国+日本+韩国):")
print(f"  英语效应: {non_colonial_effects.mean():+.3f} ± {non_colonial_effects.std():.3f}")
print(f"  样本数: {len(non_colonial_effects)}")

t_stat, p_val = ttest_ind(colonial_effects, non_colonial_effects)
pooled_std = np.sqrt((colonial_effects.std()**2 + non_colonial_effects.std()**2) / 2)
cohens_d = (colonial_effects.mean() - non_colonial_effects.mean()) / pooled_std

print(f"\n独立样本t检验:")
print(f"  t统计量: {t_stat:.3f}")
print(f"  p值: {p_val:.4f}")
print(f"  Cohen's d: {cohens_d:.3f}")

if p_val < 0.001:
    sig = "***"
elif p_val < 0.01:
    sig = "**"
elif p_val < 0.05:
    sig = "*"
else:
    sig = "ns"

print(f"  显著性: {sig}")

if p_val < 0.05:
    if colonial_effects.mean() > non_colonial_effects.mean():
        print(f"\n✓ 结论: 香港显示显著更强的英语效应")
        print(f"  这支持殖民历史假说：英国殖民历史导致香港在英语")
        print(f"  训练数据中有更好的表征，反映了历史遗产的延续。")
    else:
        print(f"\n✗ 结论: 其他东亚国家反而显示更强的英语效应")
else:
    print(f"\n结论: 香港的殖民历史对英语效应的影响不显著")

# ============================================================================
# Experiment 4b: Latin American Language Variants
# ============================================================================
print("\n" + "="*80)
print("Experiment 4b: Latin American Language Variants")
print("="*80)
print("""
设计: 比较拉丁美洲不同殖民语言国家的英语效应
- 西班牙语国家 (n=11)
- 葡萄牙语国家 (n=1, 巴西)
- 法语国家 (n=1, 海地)

假设: 不同殖民语言的持续影响应该导致不同的英语效应
""")

# 定义国家组
spanish_countries = ['Argentina', 'Bolivia', 'Chile', 'Colombia', 'Ecuador', 
                     'Guatemala', 'Mexico', 'Nicaragua', 'Peru', 'Uruguay', 'Venezuela']
portuguese_countries = ['Brazil']
french_countries = ['Haiti']

def calculate_language_effect(country_list, group_name, colonial_lang):
    """计算一组国家的英语效应"""
    effects = []
    
    for country in country_list:
        country_data = df[df['country'] == country]
        if len(country_data) == 0:
            continue
        
        for model in country_data['model_name'].unique():
            model_data = country_data[country_data['model_name'] == model]
            
            en_dist = model_data[model_data['language'].isin(['en', 'en-native'])]['cultural_distance']
            native_dist = model_data[model_data['language'] == colonial_lang]['cultural_distance']
            
            if len(en_dist) > 0 and len(native_dist) > 0:
                # 效应 = 母语距离 - 英语距离（正值表示英语更好）
                effect = native_dist.iloc[0] - en_dist.iloc[0]
                effects.append(effect)
    
    return np.array(effects)

spanish_effects = calculate_language_effect(spanish_countries, "Spanish", 'es')
portuguese_effects = calculate_language_effect(portuguese_countries, "Portuguese", 'pt')
french_effects = calculate_language_effect(french_countries, "French", 'fr')

print(f"\n西班牙语国家 (n={len(spanish_countries)}):")
print(f"  英语效应: {spanish_effects.mean():+.3f} ± {spanish_effects.std():.3f}")
print(f"  样本数: {len(spanish_effects)}")

print(f"\n葡萄牙语国家 (巴西):")
print(f"  英语效应: {portuguese_effects.mean():+.3f} ± {portuguese_effects.std():.3f}")
print(f"  样本数: {len(portuguese_effects)}")

print(f"\n法语国家 (海地):")
print(f"  英语效应: {french_effects.mean():+.3f} ± {french_effects.std():.3f}")
print(f"  样本数: {len(french_effects)}")

# 单因素方差分析
if len(spanish_effects) > 0 and len(portuguese_effects) > 0 and len(french_effects) > 0:
    f_stat, p_value = f_oneway(spanish_effects, portuguese_effects, french_effects)
    
    print(f"\n单因素ANOVA:")
    print(f"  F统计量: {f_stat:.3f}")
    print(f"  p值: {p_value:.4f}")
    
    if p_value < 0.05:
        print(f"  显著性: *")
        print(f"\n✓ 结论: 不同殖民语言的拉丁美洲国家在英语效应上存在显著差异")
    else:
        print(f"  显著性: ns")
        print(f"\n结论: 不同殖民语言的拉丁美洲国家在英语效应上无显著差异")

# ============================================================================
# Experiment 4c: African Colonial History Effects
# ============================================================================
print("\n" + "="*80)
print("Experiment 4c: African Colonial History Effects")
print("="*80)
print("""
设计: 比较有英国殖民历史 vs 无英国殖民历史的非洲国家
- 有英国殖民史: Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia
- 无英国殖民史: Ethiopia, Morocco, Algeria

注意: 有英国殖民史的国家多为英语官方语言国家
我们比较它们在英语下的文化距离
""")

# 定义国家组
british_colonial = ['Kenya', 'Nigeria', 'Ghana', 'South Africa', 'Zimbabwe', 'Zambia']
non_british_colonial = ['Ethiopia', 'Morocco', 'Algeria']

# 计算英语下的文化距离
british_distances = []
for country in british_colonial:
    country_data = df[(df['country'] == country) & (df['language'].isin(['en', 'en-native']))]
    if len(country_data) > 0:
        british_distances.extend(country_data['cultural_distance'].dropna().tolist())

non_british_distances = []
for country in non_british_colonial:
    country_data = df[(df['country'] == country) & (df['language'] == 'en')]
    if len(country_data) > 0:
        non_british_distances.extend(country_data['cultural_distance'].dropna().tolist())

british_distances = np.array(british_distances)
non_british_distances = np.array(non_british_distances)

print(f"\n有英国殖民史的非洲国家 (n={len(british_colonial)}):")
print(f"  英语下文化距离: {british_distances.mean():.3f} ± {british_distances.std():.3f}")
print(f"  样本数: {len(british_distances)}")

print(f"\n无英国殖民史的非洲国家 (n={len(non_british_colonial)}):")
print(f"  英语下文化距离: {non_british_distances.mean():.3f} ± {non_british_distances.std():.3f}")
print(f"  样本数: {len(non_british_distances)}")

# 独立样本t检验
if len(british_distances) > 0 and len(non_british_distances) > 0:
    t_stat, p_value = ttest_ind(british_distances, non_british_distances)
    pooled_std = np.sqrt((british_distances.std()**2 + non_british_distances.std()**2) / 2)
    cohens_d = (british_distances.mean() - non_british_distances.mean()) / pooled_std
    
    print(f"\n独立样本t检验:")
    print(f"  t统计量: {t_stat:.3f}")
    print(f"  p值: {p_value:.4f}")
    print(f"  Cohen's d: {cohens_d:.3f}")
    
    if p_value < 0.001:
        sig = "***"
    elif p_value < 0.01:
        sig = "**"
    elif p_value < 0.05:
        sig = "*"
    else:
        sig = "ns"
    
    print(f"  显著性: {sig}")
    
    if p_value < 0.05:
        if british_distances.mean() < non_british_distances.mean():
            print(f"\n✓ 结论: 有英国殖民历史的非洲国家在英语下文化距离更小")
            print(f"  这支持殖民历史假说：英国殖民遗产使得这些国家在英语")
            print(f"  训练数据中有更准确的表征。")
        else:
            print(f"\n✗ 结论: 无英国殖民历史的国家反而在英语下距离更小")
    else:
        print(f"\n结论: 英国殖民历史对英语下文化距离的影响不显著")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "="*80)
print("Study 4 总结")
print("="*80)

print("""
三个自然实验的结果：

1. Hong Kong Colonial History:
   - 比较香港(英国殖民) vs 其他东亚国家(无殖民史)
   - 测试英国殖民历史是否导致更强的英语效应
   
2. Latin American Language Variants:
   - 比较不同殖民语言(西班牙语、葡萄牙语、法语)的持续影响
   - 测试殖民语言差异是否影响当代英语效应
   
3. African Colonial History:
   - 比较有英国殖民史 vs 无英国殖民史的非洲国家
   - 测试英国殖民历史对英语表征的直接效应

理论意义：
- 殖民历史通过训练数据组成影响LLM的文化表征
- 不同殖民语言的全球地位差异导致不同的语言效应
- 这些效应反映了历史权力关系在AI系统中的延续

局限性：
- 未控制GDP、互联网普及率、英语熟练度等混淆因素
- 未进行中介分析来区分直接和间接效应
- 某些国家组样本量较小（特别是葡萄牙语和法语国家）
""")

print("\n" + "="*80)
print("分析完成")
print("="*80)
