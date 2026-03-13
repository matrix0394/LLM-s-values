"""
Study 4: Colonial History and Contemporary Language Effects (修正版)

关键insight: 我们应该直接比较文化距离，而不是计算"优势百分比"
因为距离越小越好，直接比较更直观
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind, ttest_rel, f_oneway
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("Study 4: Colonial History and Contemporary Language Effects (修正版)")
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
# Experiment 4a: Hong Kong vs Macao Comparison (修正版)
# ============================================================================
print("\n" + "="*80)
print("Experiment 4a: Hong Kong vs Macao Comparison (修正版)")
print("="*80)
print("""
假设: 如果殖民历史影响训练数据，那么：
- 香港在英语下应该比在中文下表现更好（距离更小）
- 澳门在葡萄牙语下应该比在中文下表现更好（距离更小）
- 但英语的全球主导地位应该使香港的英语优势 > 澳门的葡萄牙语优势

我们直接比较文化距离（距离越小越好）
""")

# 香港数据
hk_data = df[df['country'] == 'Hong Kong'].copy()
hk_models = set(hk_data['model_name'].unique())

# 澳门数据  
macao_data = df[df['country'] == 'Macao'].copy()
macao_models = set(macao_data['model_name'].unique())

# 找到共同模型
common_models = hk_models & macao_models
print(f"\n共同模型数: {len(common_models)}")

# 收集配对数据
hk_en_distances = []
hk_zh_distances = []
macao_pt_distances = []
macao_zh_distances = []

for model in common_models:
    # 香港
    hk_model = hk_data[hk_data['model_name'] == model]
    hk_en = hk_model[hk_model['language'] == 'en-native']['cultural_distance']
    hk_zh = hk_model[hk_model['language'] == 'zh-cn']['cultural_distance']
    
    if len(hk_en) > 0 and len(hk_zh) > 0:
        hk_en_distances.append(hk_en.iloc[0])
        hk_zh_distances.append(hk_zh.iloc[0])
    
    # 澳门
    macao_model = macao_data[macao_data['model_name'] == model]
    macao_pt = macao_model[macao_model['language'] == 'pt']['cultural_distance']
    macao_zh = macao_model[macao_model['language'] == 'zh-cn']['cultural_distance']
    
    if len(macao_pt) > 0 and len(macao_zh) > 0:
        macao_pt_distances.append(macao_pt.iloc[0])
        macao_zh_distances.append(macao_zh.iloc[0])

hk_en_distances = np.array(hk_en_distances)
hk_zh_distances = np.array(hk_zh_distances)
macao_pt_distances = np.array(macao_pt_distances)
macao_zh_distances = np.array(macao_zh_distances)

print(f"\n有效配对数: {len(hk_en_distances)}")

# 报告原始距离
print(f"\n香港:")
print(f"  英语距离: {hk_en_distances.mean():.3f} ± {hk_en_distances.std():.3f}")
print(f"  中文距离: {hk_zh_distances.mean():.3f} ± {hk_zh_distances.std():.3f}")
print(f"  差异(中文-英语): {(hk_zh_distances - hk_en_distances).mean():+.3f}")

print(f"\n澳门:")
print(f"  葡萄牙语距离: {macao_pt_distances.mean():.3f} ± {macao_pt_distances.std():.3f}")
print(f"  中文距离: {macao_zh_distances.mean():.3f} ± {macao_zh_distances.std():.3f}")
print(f"  差异(中文-葡萄牙语): {(macao_zh_distances - macao_pt_distances).mean():+.3f}")

# 配对t检验：香港英语 vs 中文
t_hk, p_hk = ttest_rel(hk_en_distances, hk_zh_distances)
d_hk = (hk_en_distances.mean() - hk_zh_distances.mean()) / hk_en_distances.std()

print(f"\n香港: 英语 vs 中文 (配对t检验)")
print(f"  t统计量: {t_hk:.3f}")
print(f"  p值: {p_hk:.4f}")
print(f"  Cohen's d: {d_hk:.3f}")

if p_hk < 0.05:
    if hk_en_distances.mean() < hk_zh_distances.mean():
        print(f"  ✓ 英语显著优于中文 (距离更小)")
    else:
        print(f"  ✗ 中文显著优于英语")
else:
    print(f"  无显著差异")

# 配对t检验：澳门葡萄牙语 vs 中文
t_macao, p_macao = ttest_rel(macao_pt_distances, macao_zh_distances)
d_macao = (macao_pt_distances.mean() - macao_zh_distances.mean()) / macao_pt_distances.std()

print(f"\n澳门: 葡萄牙语 vs 中文 (配对t检验)")
print(f"  t统计量: {t_macao:.3f}")
print(f"  p值: {p_macao:.4f}")
print(f"  Cohen's d: {d_macao:.3f}")

if p_macao < 0.05:
    if macao_pt_distances.mean() < macao_zh_distances.mean():
        print(f"  ✓ 葡萄牙语显著优于中文 (距离更小)")
    else:
        print(f"  ✗ 中文显著优于葡萄牙语")
else:
    print(f"  无显著差异")

# 关键比较：香港的英语效应 vs 澳门的葡萄牙语效应
hk_effect = hk_zh_distances - hk_en_distances  # 正值表示英语更好
macao_effect = macao_zh_distances - macao_pt_distances  # 正值表示葡萄牙语更好

print(f"\n关键比较: 殖民语言效应")
print(f"  香港英语效应: {hk_effect.mean():+.3f} ± {hk_effect.std():.3f}")
print(f"  澳门葡萄牙语效应: {macao_effect.mean():+.3f} ± {macao_effect.std():.3f}")

t_effect, p_effect = ttest_ind(hk_effect, macao_effect)
pooled_std = np.sqrt((hk_effect.std()**2 + macao_effect.std()**2) / 2)
d_effect = (hk_effect.mean() - macao_effect.mean()) / pooled_std

print(f"\n独立样本t检验 (香港英语效应 vs 澳门葡萄牙语效应):")
print(f"  t统计量: {t_effect:.3f}")
print(f"  p值: {p_effect:.4f}")
print(f"  Cohen's d: {d_effect:.3f}")

if p_effect < 0.05:
    if hk_effect.mean() > macao_effect.mean():
        print(f"  ✓ 香港的英语效应显著强于澳门的葡萄牙语效应")
        print(f"  这支持殖民历史假说：英语的全球主导地位使英国殖民地")
        print(f"  在训练数据中有更强的语言效应")
    else:
        print(f"  ✗ 澳门的葡萄牙语效应反而更强")
else:
    print(f"  两者效应无显著差异")

# 额外分析：有多少模型显示预期模式？
hk_better_in_en = (hk_effect > 0).sum()
macao_better_in_pt = (macao_effect > 0).sum()

print(f"\n一致性分析:")
print(f"  香港英语优于中文的模型: {hk_better_in_en}/{len(hk_effect)} ({hk_better_in_en/len(hk_effect)*100:.1f}%)")
print(f"  澳门葡萄牙语优于中文的模型: {macao_better_in_pt}/{len(macao_effect)} ({macao_better_in_pt/len(macao_effect)*100:.1f}%)")

print("\n" + "="*80)
print("分析完成")
print("="*80)
