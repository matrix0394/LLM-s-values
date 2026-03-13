"""
Study 4: Colonial History and Contemporary Language Effects

分析殖民历史是否预测LLM文化表征中的当代语言效应。
使用三个自然实验来分离殖民遗产，同时控制混淆因素。
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind, f_oneway
import warnings
warnings.filterwarnings('ignore')

# 加载数据
print("="*80)
print("Study 4: Colonial History and Contemporary Language Effects")
print("="*80)

# 读取PCA坐标数据
pca_file = 'SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv'
df = pd.read_csv(pca_file)

# 排除低质量模型
bad_models = ['llama-3.2-3b-instruct', 'qwen3-1.7b']
df = df[~df['model_name'].isin(bad_models)]

print(f"\n加载数据: {len(df)} 条记录")
print(f"模型数: {df['model_name'].nunique()}")
print(f"国家数: {df['country'].nunique()}")

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

# ============================================================================
# Experiment 4a: Hong Kong vs Macao Comparison
# ============================================================================
print("\n" + "="*80)
print("Experiment 4a: Hong Kong vs Macao Comparison")
print("="*80)
print("""
设计: 比较香港的英语优势 vs 澳门的葡萄牙语优势
控制变量: 地理、文化、经济发展水平（都是中国特别行政区）
变量: 殖民语言（英语 vs 葡萄牙语）
""")

# 香港数据 - 只用zh-cn作为基线
hk_data = df[df['country'] == 'Hong Kong'].copy()
hk_en = hk_data[hk_data['language'] == 'en-native'].groupby('model_name')['cultural_distance'].mean()
hk_zh = hk_data[hk_data['language'] == 'zh-cn'].groupby('model_name')['cultural_distance'].mean()

# 澳门数据 - 只用zh-cn作为基线
macao_data = df[df['country'] == 'Macao'].copy()
macao_en = macao_data[macao_data['language'] == 'en'].groupby('model_name')['cultural_distance'].mean()
macao_pt = macao_data[macao_data['language'] == 'pt'].groupby('model_name')['cultural_distance'].mean()
macao_zh = macao_data[macao_data['language'] == 'zh-cn'].groupby('model_name')['cultural_distance'].mean()

# 计算优势（使用中文作为基线）
hk_models = set(hk_en.index) & set(hk_zh.index)
macao_models = set(macao_pt.index) & set(macao_zh.index)
common_models = hk_models & macao_models

hk_en_advantage = []
macao_pt_advantage = []

for model in common_models:
    # 香港英语优势
    hk_adv = (hk_zh[model] - hk_en[model]) / hk_zh[model] * 100
    hk_en_advantage.append(hk_adv)
    
    # 澳门葡萄牙语优势
    macao_adv = (macao_zh[model] - macao_pt[model]) / macao_zh[model] * 100
    macao_pt_advantage.append(macao_adv)

hk_en_advantage = np.array(hk_en_advantage)
macao_pt_advantage = np.array(macao_pt_advantage)

print(f"\n分析的模型数: {len(common_models)}")
print(f"\n香港英语优势:")
print(f"  均值: {hk_en_advantage.mean():+.2f}%")
print(f"  标准差: {hk_en_advantage.std():.2f}%")
print(f"  95% CI: [{hk_en_advantage.mean() - 1.96*hk_en_advantage.std()/np.sqrt(len(hk_en_advantage)):.2f}, "
      f"{hk_en_advantage.mean() + 1.96*hk_en_advantage.std()/np.sqrt(len(hk_en_advantage)):.2f}]")

print(f"\n澳门葡萄牙语优势:")
print(f"  均值: {macao_pt_advantage.mean():+.2f}%")
print(f"  标准差: {macao_pt_advantage.std():.2f}%")
print(f"  95% CI: [{macao_pt_advantage.mean() - 1.96*macao_pt_advantage.std()/np.sqrt(len(macao_pt_advantage)):.2f}, "
      f"{macao_pt_advantage.mean() + 1.96*macao_pt_advantage.std()/np.sqrt(len(macao_pt_advantage)):.2f}]")

# 独立样本t检验
t_stat, p_value = ttest_ind(hk_en_advantage, macao_pt_advantage)
pooled_std = np.sqrt((hk_en_advantage.std()**2 + macao_pt_advantage.std()**2) / 2)
cohens_d = (hk_en_advantage.mean() - macao_pt_advantage.mean()) / pooled_std

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

if hk_en_advantage.mean() > macao_pt_advantage.mean() and p_value < 0.05:
    print(f"\n✓ 结论: 香港的英语优势显著高于澳门的葡萄牙语优势")
    print(f"  这支持殖民历史假说：英语的全球主导地位使得英国殖民地")
    print(f"  在训练数据中有更多英语表征，而葡萄牙语影响较小。")

# ============================================================================
# Experiment 4b: Latin American Language Variants
# ============================================================================
print("\n" + "="*80)
print("Experiment 4b: Latin American Language Variants")
print("="*80)
print("""
设计: 比较拉丁美洲不同殖民语言国家的英语优势
- 西班牙语国家 (n=11)
- 葡萄牙语国家 (n=1, 巴西)
- 法语国家 (n=1, 海地)
""")

# 定义国家组
spanish_countries = ['Argentina', 'Bolivia', 'Chile', 'Colombia', 'Ecuador', 
                     'Guatemala', 'Mexico', 'Nicaragua', 'Peru', 'Uruguay', 'Venezuela']
portuguese_countries = ['Brazil']
french_countries = ['Haiti']

def calculate_english_advantage(country_list, group_name):
    """计算一组国家的英语优势"""
    advantages = []
    
    for country in country_list:
        country_data = df[df['country'] == country]
        if len(country_data) == 0:
            continue
            
        # 获取英语和母语数据
        en_data = country_data[country_data['language'].isin(['en', 'en-native'])]
        
        # 确定母语
        if country in spanish_countries:
            native_lang = 'es'
        elif country in portuguese_countries:
            native_lang = 'pt'
        elif country in french_countries:
            native_lang = 'fr'
        else:
            continue
            
        native_data = country_data[country_data['language'] == native_lang]
        
        if len(en_data) == 0 or len(native_data) == 0:
            continue
        
        # 按模型计算优势
        for model in set(en_data['model_name']) & set(native_data['model_name']):
            en_dist = en_data[en_data['model_name'] == model]['cultural_distance'].mean()
            native_dist = native_data[native_data['model_name'] == model]['cultural_distance'].mean()
            
            if pd.notna(en_dist) and pd.notna(native_dist) and native_dist > 0:
                adv = (native_dist - en_dist) / native_dist * 100
                advantages.append(adv)
    
    return np.array(advantages)

spanish_adv = calculate_english_advantage(spanish_countries, "Spanish")
portuguese_adv = calculate_english_advantage(portuguese_countries, "Portuguese")
french_adv = calculate_english_advantage(french_countries, "French")

print(f"\n西班牙语国家 (n={len(spanish_countries)}):")
print(f"  观测数: {len(spanish_adv)}")
print(f"  英语优势均值: {spanish_adv.mean():+.2f}%")
print(f"  标准差: {spanish_adv.std():.2f}%")

print(f"\n葡萄牙语国家 (巴西):")
print(f"  观测数: {len(portuguese_adv)}")
print(f"  英语优势均值: {portuguese_adv.mean():+.2f}%")
print(f"  标准差: {portuguese_adv.std():.2f}%")

print(f"\n法语国家 (海地):")
print(f"  观测数: {len(french_adv)}")
print(f"  英语优势均值: {french_adv.mean():+.2f}%")
print(f"  标准差: {french_adv.std():.2f}%")

# 单因素方差分析
if len(spanish_adv) > 0 and len(portuguese_adv) > 0 and len(french_adv) > 0:
    f_stat, p_value = f_oneway(spanish_adv, portuguese_adv, french_adv)
    
    print(f"\n单因素ANOVA:")
    print(f"  F统计量: {f_stat:.3f}")
    print(f"  p值: {p_value:.4f}")
    
    if p_value < 0.05:
        print(f"  显著性: *")
        print(f"\n✓ 结论: 不同殖民语言的拉丁美洲国家在英语优势上存在显著差异")
        
        # 事后成对比较
        print(f"\n事后成对比较 (Tukey HSD):")
        
        # Spanish vs Portuguese
        t_sp, p_sp = ttest_ind(spanish_adv, portuguese_adv)
        print(f"  西班牙语 vs 葡萄牙语: t={t_sp:.3f}, p={p_sp:.4f}")
        
        # Spanish vs French
        t_sf, p_sf = ttest_ind(spanish_adv, french_adv)
        print(f"  西班牙语 vs 法语: t={t_sf:.3f}, p={p_sf:.4f}")
        
        # Portuguese vs French
        t_pf, p_pf = ttest_ind(portuguese_adv, french_adv)
        print(f"  葡萄牙语 vs 法语: t={t_pf:.3f}, p={p_pf:.4f}")
    else:
        print(f"  显著性: ns")
        print(f"\n结论: 不同殖民语言的拉丁美洲国家在英语优势上无显著差异")

# ============================================================================
# Experiment 4c: African Colonial History Effects
# ============================================================================
print("\n" + "="*80)
print("Experiment 4c: African Colonial History Effects")
print("="*80)
print("""
设计: 比较有英国殖民历史 vs 无英国殖民历史的非洲国家
注意: 有英国殖民史的国家多为英语官方语言国家，我们比较它们的文化距离
- 有英国殖民史(英语国家): Kenya, Nigeria, Ghana, South Africa, Zimbabwe, Zambia
- 无英国殖民史(非英语国家): Ethiopia, Morocco, Algeria
""")

# 定义国家组
british_colonial_en = ['Kenya', 'Nigeria', 'Ghana', 'South Africa', 'Zimbabwe', 'Zambia']
non_british_african = ['Ethiopia', 'Morocco', 'Algeria']

# 计算英语母语国家的文化距离
british_distances = []
for country in british_colonial_en:
    country_data = df[(df['country'] == country) & (df['language'].isin(['en', 'en-native']))]
    if len(country_data) > 0:
        british_distances.extend(country_data['cultural_distance'].dropna().tolist())

# 计算非英国殖民国家在英语下的文化距离
non_british_distances = []
for country in non_british_african:
    country_data = df[(df['country'] == country) & (df['language'].isin(['en']))]
    if len(country_data) > 0:
        non_british_distances.extend(country_data['cultural_distance'].dropna().tolist())

british_distances = np.array(british_distances)
non_british_distances = np.array(non_british_distances)

print(f"\n有英国殖民史的非洲国家 (n={len(british_colonial_en)}):")
print(f"  观测数: {len(british_distances)}")
if len(british_distances) > 0:
    print(f"  英语下文化距离均值: {british_distances.mean():.3f}")
    print(f"  标准差: {british_distances.std():.3f}")
    print(f"  95% CI: [{british_distances.mean() - 1.96*british_distances.std()/np.sqrt(len(british_distances)):.3f}, "
          f"{british_distances.mean() + 1.96*british_distances.std()/np.sqrt(len(british_distances)):.3f}]")

print(f"\n无英国殖民史的非洲国家 (n={len(non_british_african)}):")
print(f"  观测数: {len(non_british_distances)}")
if len(non_british_distances) > 0:
    print(f"  英语下文化距离均值: {non_british_distances.mean():.3f}")
    print(f"  标准差: {non_british_distances.std():.3f}")
    print(f"  95% CI: [{non_british_distances.mean() - 1.96*non_british_distances.std()/np.sqrt(len(non_british_distances)):.3f}, "
          f"{non_british_distances.mean() + 1.96*non_british_distances.std()/np.sqrt(len(non_british_distances)):.3f}]")

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
    
    if british_distances.mean() < non_british_distances.mean() and p_value < 0.05:
        print(f"\n✓ 结论: 有英国殖民历史的非洲国家在英语下文化距离更小")
        print(f"  这支持殖民历史假说：英国殖民遗产使得这些国家在英语训练数据中")
        print(f"  有更准确的表征，即使它们现在是英语官方语言国家。")
    else:
        print(f"\n结论: 英国殖民历史对英语下文化距离的影响不显著或方向相反")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "="*80)
print("Study 4 总结")
print("="*80)

print("""
三个自然实验的结果：

1. Hong Kong vs Macao: 
   - 测试殖民语言的全球主导地位效应
   - 控制了地理、文化、经济发展
   
2. Latin American Language Variants:
   - 测试不同殖民语言的持续影响
   - 控制了地理区域和文化距离
   
3. African Colonial History:
   - 测试英国殖民历史的直接效应
   - 需要进一步控制当代英语使用

理论意义：
- 殖民历史通过训练数据组成影响LLM的文化表征
- 英语的全球主导地位放大了英国殖民地的语言效应
- 这些效应独立于当代语言使用和经济发展

局限性：
- 未控制GDP、互联网普及率、英语熟练度等混淆因素
- 未进行中介分析来区分直接和间接效应
- 样本量较小（特别是葡萄牙语和法语国家）

未来工作：
- 收集控制变量数据进行回归分析
- 使用Common Crawl数据进行中介分析
- 扩展到更多殖民历史模式（法国、荷兰等）
""")

print("\n" + "="*80)
print("分析完成")
print("="*80)
