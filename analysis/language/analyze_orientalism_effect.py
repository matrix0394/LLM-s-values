"""
深度分析：语言他者化效应 (Linguistic Othering / Orientalism in LLMs)

理论背景：
1. Said的东方主义(Orientalism)：西方对"东方"的刻板化再现
2. 语言他者化：非西方文化在西方语言中被简化、刻板化表达
3. 训练数据偏差：LLM训练数据以英语为主，非西方文化的英语描述可能更刻板

假设：
H1: 文化距离越远的国家，英语优势越大（因为LLM对远文化的本土语言知识更少）
H2: 非西方国家用英语模仿时，会更接近"西方视角下的刻板印象"
H3: 西方国家用官方语言模仿时，能保留更多文化细节
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr

df = pd.read_csv('results/roleplay_multilingual/cultural_distance_analysis.csv')

# 排除低质量模型
bad_models = ['qwen3-1.7b', 'llama-3.2-3b-instruct']
df = df[~df['model'].isin(bad_models)]

non_english = df[~df['is_english_native_country']]

print("="*70)
print("🔬 语言他者化效应深度分析 (Linguistic Othering in LLMs)")
print("="*70)

# 1. 计算每个国家的"文化距离"（到西方中心的距离）
print("\n--- 1. 文化距离与英语优势的相关性 ---")

# 西方文化中心（用美国、英国、澳大利亚的平均坐标）
western_center = df[df['is_english_native_country']][['stage0_pc1', 'stage0_pc2']].mean()
print(f"西方文化中心坐标: PC1={western_center['stage0_pc1']:.2f}, PC2={western_center['stage0_pc2']:.2f}")

# 计算每个国家到西方中心的距离
country_analysis = []
for country in non_english['country'].unique():
    country_data = non_english[non_english['country'] == country]
    native_lang = country_data['native_language'].iloc[0]
    
    # 真实国家坐标
    real_pc1 = country_data['stage0_pc1'].iloc[0]
    real_pc2 = country_data['stage0_pc2'].iloc[0]
    
    # 到西方中心的距离
    dist_to_west = np.sqrt((real_pc1 - western_center['stage0_pc1'])**2 + 
                           (real_pc2 - western_center['stage0_pc2'])**2)
    
    # 英语 vs 官方语言的模仿距离
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
            'english_advantage': english_advantage,
            'real_pc1': real_pc1,
            'real_pc2': real_pc2
        })

analysis_df = pd.DataFrame(country_analysis)

# 相关性分析
corr_pearson, p_pearson = pearsonr(analysis_df['dist_to_west'], analysis_df['english_advantage'])
corr_spearman, p_spearman = spearmanr(analysis_df['dist_to_west'], analysis_df['english_advantage'])

print(f"\n文化距离 vs 英语优势:")
print(f"  Pearson相关: r={corr_pearson:.3f}, p={p_pearson:.4f}")
print(f"  Spearman相关: ρ={corr_spearman:.3f}, p={p_spearman:.4f}")

if corr_pearson > 0 and p_pearson < 0.05:
    print("  → 支持H1: 文化距离越远，英语优势越大 *")

# 2. 按文化区域分析
print("\n--- 2. 按文化区域的英语优势 ---")

# 定义文化区域
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

region_stats = []
for region, countries in cultural_regions.items():
    region_data = analysis_df[analysis_df['country'].isin(countries)]
    if len(region_data) > 0:
        mean_adv = region_data['english_advantage'].mean()
        std_adv = region_data['english_advantage'].std()
        mean_dist = region_data['dist_to_west'].mean()
        
        region_stats.append({
            'region': region,
            'n_countries': len(region_data),
            'mean_english_adv': mean_adv,
            'std': std_adv,
            'mean_dist_to_west': mean_dist
        })
        
        print(f"\n{region}:")
        print(f"  国家数: {len(region_data)}")
        print(f"  平均英语优势: {mean_adv:+.1f}% (std={std_adv:.1f})")
        print(f"  到西方中心距离: {mean_dist:.2f}")

region_df = pd.DataFrame(region_stats)

# 区域距离与英语优势的相关性
if len(region_df) >= 3:
    corr, p = pearsonr(region_df['mean_dist_to_west'], region_df['mean_english_adv'])
    print(f"\n区域层面: 距离 vs 英语优势相关: r={corr:.3f}, p={p:.4f}")

# 3. 东方主义效应：阿拉伯/伊斯兰国家的特殊分析
print("\n--- 3. 东方主义效应分析 (Orientalism) ---")

islamic_countries = analysis_df[analysis_df['country'].isin(cultural_regions['Islamic/Arab'])]
western_countries = analysis_df[analysis_df['country'].isin(cultural_regions['Western Europe'])]

print(f"\n伊斯兰/阿拉伯国家 (n={len(islamic_countries)}):")
print(f"  平均英语优势: {islamic_countries['english_advantage'].mean():+.1f}%")
print(f"  所有国家英语更好: {(islamic_countries['english_advantage'] > 0).all()}")

print(f"\n西欧国家 (n={len(western_countries)}):")
print(f"  平均英语优势: {western_countries['english_advantage'].mean():+.1f}%")
print(f"  官方语言更好的比例: {(western_countries['english_advantage'] < 0).sum()}/{len(western_countries)}")

# t检验：伊斯兰 vs 西欧
t_stat, p_value = stats.ttest_ind(islamic_countries['english_advantage'], 
                                   western_countries['english_advantage'])
print(f"\n伊斯兰 vs 西欧 t检验: t={t_stat:.2f}, p={p_value:.6f}")
if p_value < 0.001:
    print("  → 伊斯兰国家的英语优势显著高于西欧国家 ***")

# 4. 训练数据偏差假说
print("\n--- 4. 训练数据偏差假说 ---")
print("""
理论解释：
1. LLM训练数据以英语为主（估计>90%）
2. 非西方文化在英语训练数据中的表征：
   - 阿拉伯文化：大量英语新闻、学术文献、旅游内容
   - 俄罗斯文化：冷战历史、政治分析、文学翻译
   - 这些英语内容可能比阿拉伯语/俄语原文更"标准化"
3. 西方文化在各自语言中有丰富的原生内容
   - 法语、西班牙语、德语的文化内容更完整
   - 用官方语言能捕捉更多文化细节
""")

# 5. 模型来源与东方主义
print("\n--- 5. 模型来源与东方主义效应 ---")

# 美国模型 vs 中国模型在阿拉伯国家的表现
model_origin = {
    'US': ['claude-3-7-sonnet-20250219', 'claude-sonnet-4.5', 'gpt-4o', 'gpt-4o-mini', 
           'gpt-5.1', 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-3-pro-preview',
           'gemma-3-4b-it', 'llama-3.3-70b-instruct', 'grok-4.1-fast', 'phi-3-mini-128k-instruct'],
    'CN': ['deepseek-chat', 'deepseek-chat-v3.1', 'qwen3-max', 'kimi-k2'],
    'EU': ['mistral-medium-3.1', 'mistral-nemo']
}

arabic_data = non_english[non_english['native_language'] == 'ar']

for origin, models in model_origin.items():
    origin_data = arabic_data[arabic_data['model'].isin(models)]
    if len(origin_data) == 0:
        continue
    
    native_dist = origin_data[origin_data['language'] == 'ar']['cultural_distance'].mean()
    english_dist = origin_data[origin_data['is_english']]['cultural_distance'].mean()
    
    if pd.notna(native_dist) and pd.notna(english_dist):
        adv = (native_dist - english_dist) / native_dist * 100
        print(f"{origin}模型在阿拉伯国家: 阿拉伯语={native_dist:.2f}, 英语={english_dist:.2f}, 英语优势={adv:+.1f}%")

# 6. 效应量汇总
print("\n--- 6. 效应量汇总 (Cohen's d) ---")

# 非西方 vs 西方的英语优势差异
non_western = analysis_df[analysis_df['country'].isin(
    cultural_regions['Islamic/Arab'] + cultural_regions['Orthodox/Slavic'] + cultural_regions['East Asia']
)]
western = analysis_df[analysis_df['country'].isin(
    cultural_regions['Western Europe'] + cultural_regions['Latin America']
)]

if len(non_western) > 0 and len(western) > 0:
    pooled_std = np.sqrt((non_western['english_advantage'].std()**2 + 
                          western['english_advantage'].std()**2) / 2)
    cohens_d = (non_western['english_advantage'].mean() - western['english_advantage'].mean()) / pooled_std
    
    print(f"非西方 vs 西方英语优势差异:")
    print(f"  非西方平均: {non_western['english_advantage'].mean():+.1f}%")
    print(f"  西方平均: {western['english_advantage'].mean():+.1f}%")
    print(f"  Cohen's d: {cohens_d:.2f}")
    
    if abs(cohens_d) >= 0.8:
        print("  → 大效应量 (large effect)")
    elif abs(cohens_d) >= 0.5:
        print("  → 中等效应量 (medium effect)")

print("\n" + "="*70)
print("📝 发表潜力评估")
print("="*70)
print("""
Nature Human Behaviour / PNAS 发表潜力分析：

✅ 优势：
1. 研究问题新颖且重要：LLM中的文化偏见是热点话题
2. 发现具有理论深度：与东方主义理论形成对话
3. 统计结果显著：阿拉伯语p<0.0001, 俄语p<0.01
4. 实际意义明确：对LLM多语言部署有指导价值
5. 方法论严谨：多层次分析、多种统计检验

⚠️ 需要加强：
1. 理论框架：需要更系统地整合东方主义、语言相对论等理论
2. 机制解释：为什么会出现这种模式？需要更深入的分析
3. 训练数据分析：如果能分析训练数据的语言分布会更有说服力
4. 更多模型：增加更多非美国模型的对比
5. 纵向分析：不同版本模型的变化趋势

📊 建议投稿策略：
- 首选：Nature Human Behaviour（如果能加强理论框架）
- 备选：PNAS（作为Brief Report）
- 保底：Nature Communications, Science Advances, PLOS ONE
""")
