#!/usr/bin/env python3
"""
Stage0 vs Stage3 距离分析（核心分析）- 更新版
使用CSV/JSON格式数据，兼容最新numpy版本

对比真实国家坐标（Stage0）和：
1. 大模型英语模仿坐标（Stage3-English）
2. 大模型母语模仿坐标（Stage3-Native）
3. 计算英语优势：哪个效果更好

关键：只分析非英语母语国家的英语优势
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 排除的低质量模型（只排除qwen3-1.7b）
EXCLUDED_MODELS = ['qwen3-1.7b']

# 国家名称映射（Stage3名称 -> Stage0名称）
COUNTRY_NAME_MAPPING = {
    'Korea (the Republic of)': 'Korea',
    'Korea, Republic of': 'Korea',
    'Russian Federation (the)': 'Russian Federation',
    'Taiwan (Province of China)': 'Taiwan',
    'Taiwan, Province of China': 'Taiwan',
    'United States of America (the)': 'United States',
    'United Kingdom of Great Britain and Northern Ireland (the)': 'United Kingdom',
    'Iran (Islamic Republic of)': 'Iran',
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Viet Nam': 'Vietnam',
    'Türkiye': 'Turkey',
}


def load_language_config():
    """加载语言配置，获取国家-语言映射
    
    改进：支持多语言国家，返回国家到语言列表的映射
    """
    config_path = Path('config/multilingual_questions_complete.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 构建国家到官方语言列表的映射（支持多语言）
    country_to_native_languages = {}  # 改为列表，支持多语言
    english_native_countries = set()
    
    # 多语言国家的完整映射（手动定义）
    MULTILINGUAL_COUNTRIES = {
        'Belgium': ['fr', 'de'],  # 法语、德语（荷兰语未测试）
        'Switzerland': ['fr', 'de', 'it'],  # 法语、德语、意大利语
        'Canada': ['en', 'fr'],  # 英语、法语
        'Luxembourg': ['fr', 'de'],  # 法语、德语
        'Singapore': ['en', 'zh-cn'],  # 英语、中文
        'Hong Kong': ['zh-hk', 'zh-cn'],  # 粤语、简体中文（官方语言）
        'Macao': ['zh-hk', 'zh-cn', 'pt'],  # 粤语、简体中文、葡萄牙语（官方语言）
    }
    
    # 先收集英语母语国家
    # 注意：香港和澳门虽然在en-native列表中，但应该作为多语言国家处理
    EXCLUDE_FROM_ENGLISH_NATIVE = {'Hong Kong', 'Macao'}  # 这些国家不应被视为英语母语国家
    
    if 'en-native' in config['languages']:
        english_native_countries = set(config['languages']['en-native'].get('countries', []))
        # 排除香港和澳门
        english_native_countries = english_native_countries - EXCLUDE_FROM_ENGLISH_NATIVE
    
    # 处理所有语言，收集每个国家的所有官方语言
    for lang_code, lang_info in config['languages'].items():
        if lang_code in ['en-native', 'en']:  # 跳过英语
            continue
        countries = lang_info.get('countries', [])
        for country in countries:
            if country not in country_to_native_languages:
                country_to_native_languages[country] = []
            if lang_code not in country_to_native_languages[country]:
                country_to_native_languages[country].append(lang_code)
    
    # 使用language_country_mapping补充
    if 'language_country_mapping' in config:
        for country, langs in config['language_country_mapping'].items():
            # langs可能是列表或字符串
            if isinstance(langs, str):
                langs = [langs]
            for lang in langs:
                if lang not in ['en', 'en-native']:
                    if country not in country_to_native_languages:
                        country_to_native_languages[country] = []
                    if lang not in country_to_native_languages[country]:
                        country_to_native_languages[country].append(lang)
                elif lang in ['en', 'en-native']:
                    # 排除香港和澳门，它们应该作为多语言国家处理
                    if country not in EXCLUDE_FROM_ENGLISH_NATIVE:
                        english_native_countries.add(country)
    
    # 应用多语言国家的完整映射
    for country, langs in MULTILINGUAL_COUNTRIES.items():
        if country in country_to_native_languages:
            for lang in langs:
                if lang not in country_to_native_languages[country]:
                    country_to_native_languages[country].append(lang)
        else:
            country_to_native_languages[country] = langs
    
    # 统计多语言国家
    multilingual_count = sum(1 for langs in country_to_native_languages.values() if len(langs) > 1)
    
    print(f"\n📊 语言配置:")
    print(f"   英语母语国家: {len(english_native_countries)} 个")
    print(f"   非英语国家（有官方语言映射）: {len(country_to_native_languages)} 个")
    print(f"   多语言国家: {multilingual_count} 个")
    
    # 显示多语言国家详情
    print(f"\n   多语言国家详情:")
    for country, langs in country_to_native_languages.items():
        if len(langs) > 1:
            print(f"     {country}: {langs}")
    
    return country_to_native_languages, english_native_countries


def simple_country_match(country_name, stage0_countries):
    """简单的国家名称匹配"""
    if country_name in stage0_countries:
        return country_name
    
    if country_name in COUNTRY_NAME_MAPPING:
        mapped = COUNTRY_NAME_MAPPING[country_name]
        if mapped in stage0_countries:
            return mapped
    
    country_base = country_name.split('(')[0].strip()
    country_base = country_base.replace(',', '').strip()
    for s0_country in stage0_countries:
        if country_base.lower() == s0_country.lower():
            return s0_country
        if country_base.lower() in s0_country.lower() or s0_country.lower() in country_base.lower():
            return s0_country
    
    return None


def match_country_to_config(country_name, config_countries):
    """匹配国家名到配置文件中的国家
    
    注意：避免错误的模糊匹配，如 'Taiwan, Province of China' 不应匹配到 'China'
    """
    # 精确匹配
    if country_name in config_countries:
        return country_name
    
    # 尝试映射表
    if country_name in COUNTRY_NAME_MAPPING:
        mapped = COUNTRY_NAME_MAPPING[country_name]
        if mapped in config_countries:
            return mapped
    
    # 精确匹配（忽略大小写）
    country_lower = country_name.lower()
    for config_country in config_countries:
        if country_lower == config_country.lower():
            return config_country
    
    # 只有当国家名完全包含在配置国家名中时才匹配（避免China匹配到Taiwan, Province of China）
    # 不再使用双向模糊匹配
    
    return None


def load_stage0_coordinates():
    """加载Stage0真实国家坐标"""
    with open('data/country_values/country_scores_pca.json', encoding='utf-8') as f:
        data = json.load(f)
    
    coords = {}
    for item in data:
        country = item.get('Country')
        if country:
            coords[country] = {
                'PC1': item.get('PC1_rescaled'),
                'PC2': item.get('PC2_rescaled'),
                'cultural_region': item.get('Cultural Region', ''),
                'is_islamic': item.get('Islamic', False)
            }
    print(f"✅ 加载Stage0数据: {len(coords)} 个国家")
    return coords


def load_stage3_coordinates():
    """加载Stage3多语言模仿坐标（使用CSV格式）"""
    csv_file = Path('data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.csv')
    
    if csv_file.exists():
        data = pd.read_csv(csv_file)
        print(f"✅ 加载Stage3数据(CSV): {len(data)} 行")
    else:
        json_file = Path('data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.json')
        with open(json_file, encoding='utf-8') as f:
            data = pd.DataFrame(json.load(f))
        print(f"✅ 加载Stage3数据(JSON): {len(data)} 行")
    
    return data


def calculate_distances():
    """计算Stage0和Stage3之间的距离"""
    print("=" * 80)
    print("Stage0 vs Stage3 文化距离分析（修正版 - 只分析非英语母语国家）")
    print("=" * 80)
    
    # 加载数据
    print("\n1. 加载数据...")
    stage0_coords = load_stage0_coordinates()
    stage3_data = load_stage3_coordinates()
    country_to_native_language, english_native_countries = load_language_config()
    
    # 排除低质量模型
    if 'model_name' in stage3_data.columns:
        original_count = len(stage3_data)
        stage3_data = stage3_data[~stage3_data['model_name'].str.contains('|'.join(EXCLUDED_MODELS), case=False, na=False)]
        print(f"   排除低质量模型后: {len(stage3_data)} 行 (排除 {original_count - len(stage3_data)} 行)")
    
    print(f"   Stage0国家数: {len(stage0_coords)}")
    print(f"   Stage3模仿数: {len(stage3_data)}")
    
    # 计算距离
    print("\n2. 计算文化距离...")
    results = []
    stage0_countries = list(stage0_coords.keys())
    all_config_countries = set(country_to_native_language.keys()) | english_native_countries
    
    for _, row in stage3_data.iterrows():
        country = row.get('Country')
        language = row.get('language')
        model = row.get('model_name')
        
        if pd.isna(country) or not country:
            continue
        if pd.isna(language) or language == '' or language == 'unknown':
            continue
        
        # 匹配Stage0国家
        matched_country = simple_country_match(country, stage0_countries)
        if not matched_country:
            continue
        
        # 匹配配置文件中的国家
        config_country = match_country_to_config(country, all_config_countries)
        
        real_pc1 = stage0_coords[matched_country]['PC1']
        real_pc2 = stage0_coords[matched_country]['PC2']
        cultural_region = stage0_coords[matched_country]['cultural_region']
        is_islamic = stage0_coords[matched_country]['is_islamic']
        
        llm_pc1 = row['PC1_rescaled']
        llm_pc2 = row['PC2_rescaled']
        
        distance = np.sqrt((llm_pc1 - real_pc1)**2 + (llm_pc2 - real_pc2)**2)
        
        # 判断语言类型
        is_english = language in ['en', 'en-native']
        
        # 判断是否是英语母语国家
        is_english_native_country = config_country in english_native_countries if config_country else False
        
        # 获取该国家的所有官方语言（支持多语言）
        native_languages = country_to_native_language.get(config_country, []) if config_country else []
        if isinstance(native_languages, str):
            native_languages = [native_languages]  # 兼容旧格式
        
        # 判断是否使用官方语言（任意一种）
        is_using_native_language = language in native_languages if native_languages else is_english
        
        # 主要官方语言（第一个）
        primary_native_language = native_languages[0] if native_languages else 'en'
        
        results.append({
            'country': matched_country,
            'original_country': country,
            'config_country': config_country,
            'language': language,
            'model': model,
            'is_english': is_english,
            'is_english_native_country': is_english_native_country,
            'native_language': primary_native_language,  # 主要官方语言
            'native_languages': native_languages,  # 所有官方语言（列表）
            'is_using_native_language': is_using_native_language,
            'cultural_region': cultural_region,
            'is_islamic': is_islamic,
            'real_PC1': real_pc1,
            'real_PC2': real_pc2,
            'llm_PC1': llm_pc1,
            'llm_PC2': llm_pc2,
            'distance': distance
        })
    
    results_df = pd.DataFrame(results)
    
    # 3. 计算英语优势（只针对非英语母语国家，支持多语言）
    print("\n3. 计算英语优势（只针对非英语母语国家，支持多语言）...")
    
    # 过滤出非英语母语国家
    non_english_native = results_df[~results_df['is_english_native_country']]
    print(f"   非英语母语国家记录数: {len(non_english_native)}")
    
    english_advantage = []
    multilingual_countries = []  # 记录多语言国家
    
    for country in non_english_native['country'].unique():
        country_data = non_english_native[non_english_native['country'] == country]
        
        # 获取该国家的所有官方语言
        native_languages_raw = country_data['native_languages'].iloc[0]
        if isinstance(native_languages_raw, str):
            native_languages = [native_languages_raw]
        elif isinstance(native_languages_raw, list):
            native_languages = native_languages_raw
        else:
            native_languages = [country_data['native_language'].iloc[0]]
        
        # 过滤掉英语（如果在列表中）
        native_languages = [lang for lang in native_languages if lang not in ['en', 'en-native']]
        
        if not native_languages:
            continue
        
        cultural_region = country_data['cultural_region'].iloc[0]
        is_islamic = country_data['is_islamic'].iloc[0]
        
        # 记录多语言国家
        if len(native_languages) > 1:
            multilingual_countries.append((country, native_languages))
        
        # 使用英语的数据
        english_data = country_data[country_data['is_english']]
        
        if len(english_data) == 0:
            continue
        
        # 为每种官方语言创建对比（方案A）
        for native_lang in native_languages:
            # 使用该官方语言的数据
            native_data = country_data[country_data['language'] == native_lang]
            
            if len(native_data) == 0:
                continue
            
            # 按模型配对计算
            for model in native_data['model'].unique():
                native_model = native_data[native_data['model'] == model]
                english_model = english_data[english_data['model'] == model]
                
                if len(native_model) > 0 and len(english_model) > 0:
                    native_dist = native_model['distance'].iloc[0]
                    english_dist = english_model['distance'].iloc[0]
                    
                    if native_dist > 0:
                        # 英语优势 = (母语距离 - 英语距离) / 母语距离 * 100%
                        # 正值 = 英语更好，负值 = 母语更好
                        advantage = (native_dist - english_dist) / native_dist * 100
                    else:
                        advantage = 0
                    
                    english_advantage.append({
                        'country': country,
                        'native_language': native_lang,
                        'is_multilingual': len(native_languages) > 1,  # 标记多语言国家
                        'model': model,
                        'cultural_region': cultural_region,
                        'is_islamic': is_islamic,
                        'native_distance': native_dist,
                        'english_distance': english_dist,
                        'english_advantage': advantage
                    })
    
    advantage_df = pd.DataFrame(english_advantage)
    
    # 显示多语言国家信息
    if multilingual_countries:
        print(f"\n   多语言国家对比数: {len(multilingual_countries)} 个")
        for country, langs in multilingual_countries:
            print(f"     {country}: 英语 vs {langs}")
    
    # 创建输出目录（提前定义）
    output_dir = Path('results/analysis/stage0_vs_stage3')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 4. 统计分析
    print("\n4. 统计分析...")
    print(f"   总距离计算数: {len(results_df)}")
    print(f"   英语母语国家记录数: {len(results_df[results_df['is_english_native_country']])}")
    print(f"   非英语母语国家记录数: {len(non_english_native)}")
    print(f"   英语优势计算数: {len(advantage_df)}")
    
    # 4.1 英语母语国家基准分析
    print("\n4.1 英语母语国家基准分析:")
    english_native_data = results_df[
        (results_df['is_english_native_country']) & 
        (results_df['is_english'])
    ]
    
    if len(english_native_data) > 0:
        print(f"   英语母语国家数: {english_native_data['country'].nunique()}")
        print(f"   平均距离: {english_native_data['distance'].mean():.4f} ± {english_native_data['distance'].std():.4f}")
        
        # 4.1.1 英语母语国家详细分析
        print("\n4.1.1 英语母语国家详细分析:")
        
        # 按国家计算平均距离
        english_native_by_country = english_native_data.groupby('country').agg({
            'distance': ['mean', 'std', 'count'],
            'cultural_region': 'first',
            'real_PC1': 'first',
            'real_PC2': 'first'
        }).reset_index()
        english_native_by_country.columns = ['country', 'mean_distance', 'std_distance', 'n_models', 'cultural_region', 'real_PC1', 'real_PC2']
        english_native_by_country = english_native_by_country.sort_values('mean_distance')
        
        print(f"\n   英语母语国家距离排名（从小到大）:")
        for i, (_, row) in enumerate(english_native_by_country.iterrows(), 1):
            print(f"   {i:2d}. {row['country']:25s}: {row['mean_distance']:.3f} ± {row['std_distance']:.3f} (n={int(row['n_models'])})")
        
        # 保存英语母语国家分析结果
        english_native_by_country.to_csv(output_dir / 'english_native_countries_analysis.csv', index=False)
        print(f"\n   英语母语国家分析已保存到: {output_dir / 'english_native_countries_analysis.csv'}")
        
        # 4.1.2 按模型分析英语母语国家表现
        print("\n4.1.2 按模型分析英语母语国家表现:")
        english_native_by_model = english_native_data.groupby('model').agg({
            'distance': ['mean', 'std', 'count']
        }).reset_index()
        english_native_by_model.columns = ['model', 'mean_distance', 'std_distance', 'n_countries']
        english_native_by_model = english_native_by_model.sort_values('mean_distance')
        
        print(f"\n   模型在英语母语国家的表现排名:")
        for i, (_, row) in enumerate(english_native_by_model.head(10).iterrows(), 1):
            model_short = row['model'].split('/')[-1][:25] if '/' in str(row['model']) else str(row['model'])[:25]
            print(f"   {i:2d}. {model_short:25s}: {row['mean_distance']:.3f} ± {row['std_distance']:.3f}")
        
        english_native_by_model.to_csv(output_dir / 'english_native_by_model.csv', index=False)
        
        # 4.1.3 英语母语国家模仿偏向分析
        print("\n4.1.3 英语母语国家模仿偏向分析:")
        
        # 计算每个国家的平均模仿坐标和偏向
        bias_analysis = []
        for country in english_native_data['country'].unique():
            country_data = english_native_data[english_native_data['country'] == country]
            
            real_pc1 = country_data['real_PC1'].iloc[0]
            real_pc2 = country_data['real_PC2'].iloc[0]
            llm_pc1_mean = country_data['llm_PC1'].mean()
            llm_pc2_mean = country_data['llm_PC2'].mean()
            
            # 计算偏向
            bias_pc1 = llm_pc1_mean - real_pc1  # 正值=更自我表达，负值=更生存
            bias_pc2 = llm_pc2_mean - real_pc2  # 正值=更现代/世俗，负值=更传统
            
            # 判断偏向方向
            pc1_direction = "→更自我表达" if bias_pc1 > 0.5 else ("←更生存" if bias_pc1 < -0.5 else "中性")
            pc2_direction = "↑更世俗" if bias_pc2 > 0.5 else ("↓更传统" if bias_pc2 < -0.5 else "中性")
            
            bias_analysis.append({
                'country': country,
                'real_PC1': real_pc1,
                'real_PC2': real_pc2,
                'llm_PC1': llm_pc1_mean,
                'llm_PC2': llm_pc2_mean,
                'bias_PC1': bias_pc1,
                'bias_PC2': bias_pc2,
                'pc1_direction': pc1_direction,
                'pc2_direction': pc2_direction,
                'mean_distance': country_data['distance'].mean()
            })
        
        bias_df = pd.DataFrame(bias_analysis)
        bias_df = bias_df.sort_values('mean_distance', ascending=False)  # 按距离从大到小排序
        
        print(f"\n   模仿偏向分析（按距离从大到小）:")
        print(f"   {'国家':20s} | {'真实PC1':>8s} | {'真实PC2':>8s} | {'LLM PC1':>8s} | {'LLM PC2':>8s} | {'PC1偏向':>10s} | {'PC2偏向':>10s} | {'距离':>6s}")
        print("   " + "-" * 100)
        for _, row in bias_df.iterrows():
            print(f"   {row['country']:20s} | {row['real_PC1']:8.2f} | {row['real_PC2']:8.2f} | {row['llm_PC1']:8.2f} | {row['llm_PC2']:8.2f} | {row['pc1_direction']:>10s} | {row['pc2_direction']:>10s} | {row['mean_distance']:6.2f}")
        
        # 分析传统英语国家的共同偏向
        traditional_english = ['United Kingdom', 'Canada', 'Australia', 'New Zealand', 'Ireland']
        trad_eng_data = bias_df[bias_df['country'].isin(traditional_english)]
        
        if len(trad_eng_data) > 0:
            print(f"\n   传统英语国家（UK/Canada/Australia/NZ/Ireland）共同偏向:")
            avg_bias_pc1 = trad_eng_data['bias_PC1'].mean()
            avg_bias_pc2 = trad_eng_data['bias_PC2'].mean()
            print(f"     平均PC1偏向: {avg_bias_pc1:+.2f} ({'更自我表达' if avg_bias_pc1 > 0 else '更生存'})")
            print(f"     平均PC2偏向: {avg_bias_pc2:+.2f} ({'更世俗' if avg_bias_pc2 > 0 else '更传统'})")
            print(f"     → 结论: LLM倾向于把传统英语国家模仿得{'更自我表达+更世俗' if avg_bias_pc1 > 0 and avg_bias_pc2 > 0 else '偏向不一致'}")
        
        # 保存偏向分析结果
        bias_df.to_csv(output_dir / 'english_native_bias_analysis.csv', index=False)
        print(f"\n   偏向分析已保存到: {output_dir / 'english_native_bias_analysis.csv'}")
    
    # 5. 非英语国家：官方语言 vs 英语
    print("\n5. 非英语国家：官方语言 vs 英语")
    native_lang_dist = non_english_native[non_english_native['is_using_native_language']]['distance']
    english_lang_dist = non_english_native[non_english_native['is_english']]['distance']
    
    print(f"   使用官方语言: {native_lang_dist.mean():.4f} ± {native_lang_dist.std():.4f} (N={len(native_lang_dist)})")
    print(f"   使用英语: {english_lang_dist.mean():.4f} ± {english_lang_dist.std():.4f} (N={len(english_lang_dist)})")
    
    # 6. 按语言家族统计英语优势（与之前分析一致）
    print("\n6. 按语言家族统计英语优势:")
    
    language_families = {
        'Arabic': ['ar'],
        'Russian': ['ru'],
        'Romance (es/fr/it/pt)': ['es', 'fr', 'it', 'pt'],
        'Germanic (de)': ['de'],
        'CJK': ['zh-cn', 'zh-tw', 'zh-hk', 'ja', 'ko']
    }
    
    lang_family_stats = []
    for family, langs in language_families.items():
        family_data = advantage_df[advantage_df['native_language'].isin(langs)]
        if len(family_data) == 0:
            continue
        
        native_arr = family_data['native_distance'].values
        english_arr = family_data['english_distance'].values
        diff = native_arr - english_arr  # 正值=英语更好
        
        t_stat, p_value = stats.ttest_rel(native_arr, english_arr)
        eng_better = (diff > 0).sum()
        
        # 【修正】用平均距离计算英语优势，避免极端值
        avg_native = native_arr.mean()
        avg_english = english_arr.mean()
        eng_adv_pct = (avg_native - avg_english) / avg_native * 100
        
        sig = "***" if p_value < 0.001 else ("**" if p_value < 0.01 else ("*" if p_value < 0.05 else ""))
        
        lang_family_stats.append({
            'family': family,
            'n': len(family_data),
            'native_mean': avg_native,
            'english_mean': avg_english,
            'english_advantage': eng_adv_pct,
            't_stat': t_stat,
            'p_value': p_value,
            'sig': sig
        })
        
        print(f"\n   {family}:")
        print(f"     配对数: {len(family_data)}")
        print(f"     官方语言: {avg_native:.3f}, 英语: {avg_english:.3f}")
        print(f"     英语优势: {eng_adv_pct:+.1f}%")
        print(f"     英语更好: {eng_better}/{len(family_data)} ({eng_better/len(family_data)*100:.1f}%)")
        print(f"     t={t_stat:.2f}, p={p_value:.4f} {sig}")
    
    # 保存语言家族统计
    if lang_family_stats:
        lang_family_df = pd.DataFrame(lang_family_stats)
        lang_family_df.to_csv(output_dir / 'language_family_stats.csv', index=False)
    
    # 6.2 非西方语言 vs 西方语言对比
    print("\n6.2 非西方语言 vs 西方语言对比:")
    
    non_western_langs = ['ar', 'ru', 'zh-cn', 'zh-tw', 'zh-hk', 'ja', 'ko']
    western_langs = ['es', 'fr', 'it', 'pt', 'de']
    
    for group_name, langs in [("非西方语言", non_western_langs), ("西方语言", western_langs)]:
        group_data = advantage_df[advantage_df['native_language'].isin(langs)]
        if len(group_data) < 5:
            continue
        
        native_arr = group_data['native_distance'].values
        english_arr = group_data['english_distance'].values
        diff = native_arr - english_arr
        
        t_stat, p_value = stats.ttest_rel(native_arr, english_arr)
        eng_better = (diff > 0).sum()
        
        # 【修正】用平均距离计算英语优势，避免极端值
        avg_native = native_arr.mean()
        avg_english = english_arr.mean()
        eng_adv_pct = (avg_native - avg_english) / avg_native * 100
        
        sig = "***" if p_value < 0.001 else ("**" if p_value < 0.01 else ("*" if p_value < 0.05 else ""))
        
        print(f"\n   {group_name}:")
        print(f"     配对数: {len(group_data)}")
        print(f"     官方语言: {avg_native:.3f}, 英语: {avg_english:.3f}")
        print(f"     英语优势: {eng_adv_pct:+.1f}%")
        print(f"     英语更好: {eng_better}/{len(group_data)} ({eng_better/len(group_data)*100:.1f}%)")
        print(f"     t={t_stat:.2f}, p={p_value:.4f} {sig}")
    
    # 6.3 阿拉伯语国家详细分析
    print("\n6.3 阿拉伯语国家详细分析:")
    arabic_data = advantage_df[advantage_df['native_language'] == 'ar']
    arabic_countries = arabic_data['country'].unique().tolist()
    print(f"   阿拉伯语国家: {arabic_countries}")
    
    for country in arabic_countries:
        country_data = arabic_data[arabic_data['country'] == country]
        native_dist = country_data['native_distance'].mean()
        english_dist = country_data['english_distance'].mean()
        # 【修正】用平均距离计算英语优势
        eng_adv = (native_dist - english_dist) / native_dist * 100
        print(f"   {country:20s}: 阿拉伯语={native_dist:.2f}, 英语={english_dist:.2f}, 英语优势={eng_adv:+.1f}%")
    
    # 6.4 多语言国家详细分析（新增）
    print("\n6.4 多语言国家详细分析:")
    if 'is_multilingual' in advantage_df.columns:
        multilingual_data = advantage_df[advantage_df['is_multilingual'] == True]
        if len(multilingual_data) > 0:
            multilingual_countries = multilingual_data['country'].unique()
            print(f"   多语言国家数: {len(multilingual_countries)}")
            
            for country in multilingual_countries:
                country_data = multilingual_data[multilingual_data['country'] == country]
                langs = country_data['native_language'].unique()
                print(f"\n   {country} (官方语言: {list(langs)}):")
                
                for lang in langs:
                    lang_data = country_data[country_data['native_language'] == lang]
                    native_dist = lang_data['native_distance'].mean()
                    english_dist = lang_data['english_distance'].mean()
                    # 【修正】用平均距离计算英语优势
                    eng_adv = (native_dist - english_dist) / native_dist * 100
                    n_pairs = len(lang_data)
                    print(f"     英语 vs {lang}: 母语={native_dist:.2f}, 英语={english_dist:.2f}, 英语优势={eng_adv:+.1f}% (n={n_pairs})")
            
            # 保存多语言国家分析结果
            multilingual_summary = []
            for country in multilingual_countries:
                country_data = multilingual_data[multilingual_data['country'] == country]
                for lang in country_data['native_language'].unique():
                    lang_data = country_data[country_data['native_language'] == lang]
                    native_dist = lang_data['native_distance'].mean()
                    english_dist = lang_data['english_distance'].mean()
                    # 【修正】用平均距离计算英语优势
                    eng_adv = (native_dist - english_dist) / native_dist * 100
                    multilingual_summary.append({
                        'country': country,
                        'native_language': lang,
                        'native_distance': native_dist,
                        'english_distance': english_dist,
                        'english_advantage': eng_adv,
                        'n_pairs': len(lang_data)
                    })
            if multilingual_summary:
                multilingual_df = pd.DataFrame(multilingual_summary)
                multilingual_df.to_csv(output_dir / 'multilingual_countries_analysis.csv', index=False)
                print(f"\n   多语言国家分析已保存到: {output_dir / 'multilingual_countries_analysis.csv'}")
        else:
            print("   无多语言国家数据")
    else:
        print("   无多语言标记数据")
    
    # 6.5 控制国家效应后的语言效应
    print("\n6.5 控制国家效应后的语言效应:")
    country_effects = []
    for country in advantage_df['country'].unique():
        country_data = advantage_df[advantage_df['country'] == country]
        native_lang = country_data['native_language'].iloc[0]
        
        native_dist = country_data['native_distance'].mean()
        english_dist = country_data['english_distance'].mean()
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
    print(f"   国家数: {len(effects_df)}")
    print(f"   英语相对效应平均: {effects_df['english_effect'].mean():.4f}")
    print(f"   官方语言相对效应平均: {effects_df['native_effect'].mean():.4f}")
    
    t_stat, p_value = stats.ttest_rel(effects_df['native_effect'], effects_df['english_effect'])
    print(f"   配对t检验: t={t_stat:.2f}, p={p_value:.4f}")
    
    eng_better = (effects_df['diff'] < 0).sum()
    print(f"   英语相对更好的国家: {eng_better}/{len(effects_df)} ({eng_better/len(effects_df)*100:.1f}%)")
    
    # 6.6 按文化区域统计
    print("\n6.6 按文化区域统计英语优势:")
    if len(advantage_df) > 0:
        # 【修正】先计算每个区域的平均距离，再计算英语优势
        region_stats = advantage_df.groupby('cultural_region').agg({
            'native_distance': ['mean', 'std'],
            'english_distance': ['mean', 'std'],
            'english_advantage': 'count'
        })
        region_stats.columns = ['mean_native_dist', 'std_native', 'mean_english_dist', 'std_english', 'count']
        # 用平均距离计算英语优势
        region_stats['mean_advantage'] = (region_stats['mean_native_dist'] - region_stats['mean_english_dist']) / region_stats['mean_native_dist'] * 100
        region_stats = region_stats.sort_values('mean_advantage', ascending=False)
        
        for region, row in region_stats.iterrows():
            print(f"   {region:25s}: {row['mean_advantage']:+6.1f}% (母语={row['mean_native_dist']:.2f}, 英语={row['mean_english_dist']:.2f}, N={int(row['count'])})")
    
    # 7. 英语优势排名
    print("\n7. 英语优势排名（所有模型平均）:")
    # 先计算每个国家的平均距离，再用平均距离计算英语优势（避免极端值）
    avg_advantage = advantage_df.groupby(['country', 'native_language']).agg({
        'native_distance': 'mean',
        'english_distance': 'mean',
        'cultural_region': 'first',
        'is_islamic': 'first'
    }).reset_index()
    # 用平均距离计算英语优势（正确方式）
    avg_advantage['english_advantage'] = (avg_advantage['native_distance'] - avg_advantage['english_distance']) / avg_advantage['native_distance'] * 100
    avg_advantage = avg_advantage.sort_values('english_advantage', ascending=False)
    
    print("\n   Top 10 英语优势（英语更好）:")
    for i, (_, row) in enumerate(avg_advantage.head(10).iterrows(), 1):
        print(f"   {i:2d}. {row['country']:30s} ({row['native_language']:6s}): {row['english_advantage']:+6.1f}%")
    
    print("\n   Top 10 母语优势（母语更好）:")
    native_adv = avg_advantage.nsmallest(10, 'english_advantage')
    for i, (_, row) in enumerate(native_adv.iterrows(), 1):
        print(f"   {i:2d}. {row['country']:30s} ({row['native_language']:6s}): {row['english_advantage']:+6.1f}%")
    
    # 8. 统计检验（完整版）
    # 8. 统计检验（完整版）
    print("\n8. 统计检验:")
    if len(advantage_df) > 0:
        native_dists = advantage_df['native_distance'].values
        english_dists = advantage_df['english_distance'].values
        
        differences = native_dists - english_dists  # 正值=英语更好
        english_better_count = (differences > 0).sum()
        native_better_count = (differences < 0).sum()
        
        # 【重要】用平均距离计算英语优势（正确方式，避免极端值）
        # 公式: (平均母语距离 - 平均英语距离) / 平均母语距离 * 100%
        avg_native = native_dists.mean()
        avg_english = english_dists.mean()
        english_advantage_pct = (avg_native - avg_english) / avg_native * 100
        
        print(f"   配对样本数: {len(advantage_df)}")
        print(f"   官方语言平均距离: {avg_native:.4f} ± {native_dists.std():.4f}")
        print(f"   英语平均距离: {avg_english:.4f} ± {english_dists.std():.4f}")
        print(f"   【修正】英语优势（基于平均距离）: {english_advantage_pct:+.1f}%")
        print(f"   英语更好的配对数: {english_better_count} ({english_better_count/len(differences)*100:.1f}%)")
        print(f"   官方语言更好的配对数: {native_better_count} ({native_better_count/len(differences)*100:.1f}%)")
        
        # 配对t检验
        t_stat, p_value = stats.ttest_rel(native_dists, english_dists)
        print(f"\n   配对t检验: t={t_stat:.4f}, p={p_value:.6f}")
        
        # Wilcoxon符号秩检验
        from scipy.stats import wilcoxon, binomtest
        w_stat, w_pvalue = wilcoxon(native_dists, english_dists)
        print(f"   Wilcoxon检验: W={w_stat:.2f}, p={w_pvalue:.6f}")
        
        # 符号检验
        n_total = english_better_count + native_better_count
        result = binomtest(english_better_count, n_total, 0.5, alternative='two-sided')
        print(f"   符号检验: p={result.pvalue:.6f}")
        
        # Cohen's d
        pooled_std = np.sqrt((native_dists.std()**2 + english_dists.std()**2) / 2)
        cohens_d = (native_dists.mean() - english_dists.mean()) / pooled_std
        print(f"   Cohen's d: {cohens_d:.4f}")
        
        # 结论
        print("\n   → 结论:")
        if p_value < 0.05:
            if native_dists.mean() > english_dists.mean():
                print(f"     存在英语优势：使用英语提问时，LLM的文化模仿距离更小")
                print(f"     英语优势幅度: {english_advantage_pct:+.1f}%")
                print(f"     配对t检验显著 (p={p_value:.4f})")
                if abs(cohens_d) >= 0.2:
                    print(f"     效应量: Cohen's d = {cohens_d:.2f} (小效应)")
                else:
                    print(f"     效应量: Cohen's d = {cohens_d:.2f} (效应量较小)")
            else:
                print(f"     存在母语优势：使用母语提问时，LLM的文化模仿距离更小")
                print(f"     配对t检验显著 (p={p_value:.4f})")
        else:
            print("     英语与官方语言无显著差异")
    
    # 9. 东方主义效应分析
    print("\n" + "=" * 70)
    print("9. 东方主义效应分析 (Linguistic Othering / Orientalism)")
    print("=" * 70)
    
    # 计算西方文化中心
    english_native_coords = results_df[results_df['is_english_native_country']][['real_PC1', 'real_PC2']].drop_duplicates()
    if len(english_native_coords) > 0:
        western_center_pc1 = english_native_coords['real_PC1'].mean()
        western_center_pc2 = english_native_coords['real_PC2'].mean()
        print(f"\n   西方文化中心坐标: PC1={western_center_pc1:.2f}, PC2={western_center_pc2:.2f}")
        
        # 计算每个国家到西方中心的距离
        country_orientalism = []
        for country in avg_advantage['country'].unique():
            country_row = avg_advantage[avg_advantage['country'] == country].iloc[0]
            country_results = results_df[results_df['country'] == country]
            
            if len(country_results) > 0:
                real_pc1 = country_results['real_PC1'].iloc[0]
                real_pc2 = country_results['real_PC2'].iloc[0]
                dist_to_west = np.sqrt((real_pc1 - western_center_pc1)**2 + (real_pc2 - western_center_pc2)**2)
                
                country_orientalism.append({
                    'country': country,
                    'native_language': country_row['native_language'],
                    'dist_to_west': dist_to_west,
                    'english_advantage': country_row['english_advantage']
                })
        
        orientalism_df = pd.DataFrame(country_orientalism)
        
        # 相关性分析
        if len(orientalism_df) > 5:
            from scipy.stats import pearsonr, spearmanr
            corr_pearson, p_pearson = pearsonr(orientalism_df['dist_to_west'], orientalism_df['english_advantage'])
            corr_spearman, p_spearman = spearmanr(orientalism_df['dist_to_west'], orientalism_df['english_advantage'])
            
            print(f"\n   文化距离与英语优势的相关性:")
            print(f"     Pearson相关: r={corr_pearson:.3f}, p={p_pearson:.4f}")
            print(f"     Spearman相关: ρ={corr_spearman:.3f}, p={p_spearman:.4f}")
            
            if corr_pearson > 0 and p_pearson < 0.05:
                print("     → 支持H1: 文化距离越远，英语优势越大 *")
        
        # 文化区域分析
        cultural_regions_def = {
            'Islamic/Arab': ['Algeria', 'Palestine', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
                             'Libya', 'Morocco', 'Qatar', 'Tunisia', 'Egypt', 'Yemen'],
            'Orthodox/Slavic': ['Russian Federation', 'Belarus', 'Kazakhstan', 'Kyrgyzstan'],
            'Latin America': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador',
                              'Guatemala', 'Haiti', 'Mexico', 'Nicaragua', 'Peru', 'Uruguay', 'Venezuela'],
            'Western Europe': ['Austria', 'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg',
                               'Portugal', 'Spain', 'Switzerland'],
            'East Asia': ['China', 'Japan', 'Korea', 'Macao', 'Hong Kong', 'Taiwan']
        }
        
        print(f"\n   按文化区域的英语优势:")
        for region, countries in cultural_regions_def.items():
            region_data = orientalism_df[orientalism_df['country'].isin(countries)]
            if len(region_data) > 0:
                print(f"     {region}: {region_data['english_advantage'].mean():+.1f}% (n={len(region_data)}, 到西方距离={region_data['dist_to_west'].mean():.2f})")
        
        # 伊斯兰 vs 西欧 t检验
        islamic = orientalism_df[orientalism_df['country'].isin(cultural_regions_def['Islamic/Arab'])]
        western_eu = orientalism_df[orientalism_df['country'].isin(cultural_regions_def['Western Europe'])]
        
        if len(islamic) > 0 and len(western_eu) > 0:
            t_stat_orient, p_orient = stats.ttest_ind(islamic['english_advantage'], western_eu['english_advantage'])
            print(f"\n   伊斯兰 vs 西欧 t检验:")
            print(f"     伊斯兰国家平均英语优势: {islamic['english_advantage'].mean():+.1f}%")
            print(f"     西欧国家平均英语优势: {western_eu['english_advantage'].mean():+.1f}%")
            print(f"     t={t_stat_orient:.2f}, p={p_orient:.6f}")
            
            if p_orient < 0.001:
                print("     → 伊斯兰国家的英语优势显著高于西欧国家 ***")
        
        # Cohen's d (非西方 vs 西方)
        non_western_regions = cultural_regions_def['Islamic/Arab'] + cultural_regions_def['Orthodox/Slavic'] + cultural_regions_def['East Asia']
        western_regions = cultural_regions_def['Western Europe'] + cultural_regions_def['Latin America']
        
        non_western_data = orientalism_df[orientalism_df['country'].isin(non_western_regions)]
        western_data = orientalism_df[orientalism_df['country'].isin(western_regions)]
        
        if len(non_western_data) > 0 and len(western_data) > 0:
            pooled_std_orient = np.sqrt((non_western_data['english_advantage'].std()**2 + 
                                         western_data['english_advantage'].std()**2) / 2)
            if pooled_std_orient > 0:
                cohens_d_orient = (non_western_data['english_advantage'].mean() - western_data['english_advantage'].mean()) / pooled_std_orient
                
                print(f"\n   效应量 (Cohen's d):")
                print(f"     非西方平均: {non_western_data['english_advantage'].mean():+.1f}%")
                print(f"     西方平均: {western_data['english_advantage'].mean():+.1f}%")
                print(f"     Cohen's d: {cohens_d_orient:.2f}")
                
                if abs(cohens_d_orient) >= 0.8:
                    print("     → 大效应量 (large effect)")
                elif abs(cohens_d_orient) >= 0.5:
                    print("     → 中等效应量 (medium effect)")
        
        # 保存东方主义分析结果
        orientalism_df.to_csv(output_dir / 'orientalism_analysis.csv', index=False)
    
    # 10. 按模型质量分析
    print("\n" + "=" * 70)
    print("10. 按模型质量分层分析")
    print("=" * 70)
    
    model_effects = []
    for model in advantage_df['model'].unique():
        model_data = advantage_df[advantage_df['model'] == model]
        
        native_dist_mean = model_data['native_distance'].mean()
        english_dist_mean = model_data['english_distance'].mean()
        overall_dist = (native_dist_mean + english_dist_mean) / 2
        
        diff = english_dist_mean - native_dist_mean
        model_effects.append({
            'model': model,
            'overall_dist': overall_dist,
            'native_dist': native_dist_mean,
            'english_dist': english_dist_mean,
            'diff': diff,
            'english_better': diff < 0
        })
    
    model_effects_df = pd.DataFrame(model_effects).sort_values('overall_dist')
    
    print("\n   每个模型的语言效应:")
    for _, row in model_effects_df.iterrows():
        model_short = row['model'].split('/')[-1][:20] if '/' in str(row['model']) else str(row['model'])[:20]
        better = "英语更好" if row['english_better'] else "母语更好"
        print(f"     {model_short:20s}: 整体={row['overall_dist']:.3f}, 母语={row['native_dist']:.3f}, 英语={row['english_dist']:.3f} ({better})")
    
    english_better_models = model_effects_df['english_better'].sum()
    print(f"\n   英语更好的模型: {english_better_models}/{len(model_effects_df)}")
    print(f"   平均差异 (英语-官方语言): {model_effects_df['diff'].mean():.4f}")
    
    # 保存模型效应结果
    model_effects_df.to_csv(output_dir / 'model_effects.csv', index=False)
    
    # 10.2 模型系列一致性分析
    print("\n10.2 模型系列一致性分析:")
    
    # 定义模型系列（更完整的匹配）
    model_families = {
        'GPT': ['gpt-4o', 'gpt-4o-mini', 'gpt-5', 'gpt-4', 'gpt-3'],
        'Claude': ['claude'],
        'Llama': ['llama'],
        'Qwen': ['qwen', 'qwq'],
        'Gemini': ['gemini'],
        'Gemma': ['gemma'],
        'Mistral': ['mistral', 'mixtral'],
        'DeepSeek': ['deepseek'],
        'GLM': ['glm'],
        'Grok': ['grok'],
        'Phi': ['phi-'],
        'Kimi': ['kimi'],
    }
    
    family_stats = []
    for family_name, keywords in model_families.items():
        # 匹配该系列的模型
        family_models = model_effects_df[
            model_effects_df['model'].str.lower().str.contains('|'.join(keywords), na=False)
        ]
        
        if len(family_models) == 0:
            continue
        
        # 计算系列统计
        avg_overall = family_models['overall_dist'].mean()
        avg_native = family_models['native_dist'].mean()
        avg_english = family_models['english_dist'].mean()
        eng_adv = (avg_native - avg_english) / avg_native * 100
        eng_better_count = family_models['english_better'].sum()
        consistency = eng_better_count / len(family_models) * 100 if len(family_models) > 0 else 0
        
        family_stats.append({
            'family': family_name,
            'n_models': len(family_models),
            'avg_overall_dist': avg_overall,
            'avg_native_dist': avg_native,
            'avg_english_dist': avg_english,
            'english_advantage': eng_adv,
            'eng_better_count': eng_better_count,
            'consistency': consistency
        })
        
        print(f"\n   {family_name} 系列 ({len(family_models)} 个模型):")
        print(f"     平均整体距离: {avg_overall:.3f}")
        print(f"     母语距离: {avg_native:.3f}, 英语距离: {avg_english:.3f}")
        print(f"     英语优势: {eng_adv:+.1f}%")
        print(f"     英语更好的模型: {eng_better_count}/{len(family_models)} ({consistency:.0f}%)")
        
        # 列出该系列的具体模型
        for _, m in family_models.iterrows():
            model_short = m['model'].split('/')[-1][:25] if '/' in str(m['model']) else str(m['model'])[:25]
            better = "英语↑" if m['english_better'] else "母语↑"
            print(f"       - {model_short}: 整体={m['overall_dist']:.2f} ({better})")
    
    if family_stats:
        family_df = pd.DataFrame(family_stats)
        family_df.to_csv(output_dir / 'model_family_stats.csv', index=False)
    
    # 10.2.1 模型系列偏向一致性分析（PC1/PC2方向）
    print("\n10.2.1 模型系列偏向一致性分析（相对于真实坐标的偏移方向）:")
    
    # 选择几个代表性国家进行分析
    representative_countries = ['China', 'Japan', 'Korea', 'Hong Kong', 'Russian Federation', 
                                'Germany', 'France', 'Brazil', 'Egypt', 'Iran']
    
    for family_name, keywords in model_families.items():
        # 获取该系列的模型名称
        family_model_names = model_effects_df[
            model_effects_df['model'].str.lower().str.contains('|'.join(keywords), na=False)
        ]['model'].tolist()
        
        if len(family_model_names) < 2:
            continue
        
        print(f"\n   {family_name} 系列偏向分析:")
        
        # 分析每个代表性国家
        country_bias_analysis = []
        for country in representative_countries:
            country_results = results_df[
                (results_df['country'] == country) & 
                (results_df['model'].isin(family_model_names))
            ]
            
            if len(country_results) == 0:
                continue
            
            # 获取真实坐标
            real_pc1 = country_results['real_PC1'].iloc[0]
            real_pc2 = country_results['real_PC2'].iloc[0]
            
            # 计算每个模型的偏移
            model_biases = []
            for model in family_model_names:
                model_country = country_results[country_results['model'] == model]
                if len(model_country) == 0:
                    continue
                
                # 使用英语数据（更一致）
                eng_data = model_country[model_country['is_english']]
                if len(eng_data) > 0:
                    llm_pc1 = eng_data['llm_PC1'].iloc[0]
                    llm_pc2 = eng_data['llm_PC2'].iloc[0]
                    bias_pc1 = llm_pc1 - real_pc1
                    bias_pc2 = llm_pc2 - real_pc2
                    model_biases.append({'model': model, 'bias_pc1': bias_pc1, 'bias_pc2': bias_pc2})
            
            if len(model_biases) < 2:
                continue
            
            bias_df = pd.DataFrame(model_biases)
            
            # 计算偏移的一致性（标准差越小越一致）
            pc1_mean = bias_df['bias_pc1'].mean()
            pc1_std = bias_df['bias_pc1'].std()
            pc2_mean = bias_df['bias_pc2'].mean()
            pc2_std = bias_df['bias_pc2'].std()
            
            # 判断偏向方向
            pc1_direction = "→自我表达" if pc1_mean > 0 else "←生存"
            pc2_direction = "↑现代" if pc2_mean > 0 else "↓传统"
            
            country_bias_analysis.append({
                'country': country,
                'pc1_mean': pc1_mean,
                'pc1_std': pc1_std,
                'pc2_mean': pc2_mean,
                'pc2_std': pc2_std,
                'pc1_direction': pc1_direction,
                'pc2_direction': pc2_direction
            })
        
        if country_bias_analysis:
            # 计算整体偏向
            overall_pc1 = np.mean([x['pc1_mean'] for x in country_bias_analysis])
            overall_pc2 = np.mean([x['pc2_mean'] for x in country_bias_analysis])
            overall_pc1_std = np.mean([x['pc1_std'] for x in country_bias_analysis])
            overall_pc2_std = np.mean([x['pc2_std'] for x in country_bias_analysis])
            
            pc1_dir = "→自我表达" if overall_pc1 > 0 else "←生存"
            pc2_dir = "↑现代" if overall_pc2 > 0 else "↓传统"
            
            print(f"     整体偏向: PC1={overall_pc1:+.2f} ({pc1_dir}), PC2={overall_pc2:+.2f} ({pc2_dir})")
            print(f"     一致性(std): PC1={overall_pc1_std:.2f}, PC2={overall_pc2_std:.2f}")
            
            # 显示几个典型国家
            print(f"     典型国家偏向:")
            for item in country_bias_analysis[:5]:
                print(f"       {item['country']:15s}: PC1={item['pc1_mean']:+.2f}({item['pc1_direction']}), PC2={item['pc2_mean']:+.2f}({item['pc2_direction']})")
    
    # 10.3 效果差的模型分析
    print("\n10.3 效果差的模型分析（整体距离最大的5个）:")
    worst_models = model_effects_df.nlargest(5, 'overall_dist')
    
    for _, row in worst_models.iterrows():
        model_name = row['model']
        model_short = model_name.split('/')[-1][:30] if '/' in str(model_name) else str(model_name)[:30]
        
        # 分析该模型在哪些国家/语言表现最差
        model_data = advantage_df[advantage_df['model'] == model_name]
        
        print(f"\n   {model_short}:")
        print(f"     整体距离: {row['overall_dist']:.3f} (母语={row['native_dist']:.3f}, 英语={row['english_dist']:.3f})")
        
        if len(model_data) > 0:
            # 找出该模型距离最大的国家
            worst_countries = model_data.nlargest(3, 'native_distance')
            print(f"     表现最差的国家（母语距离最大）:")
            for _, c in worst_countries.iterrows():
                print(f"       - {c['country']} ({c['native_language']}): 母语={c['native_distance']:.2f}, 英语={c['english_distance']:.2f}")
            
            # 按语言统计
            lang_stats = model_data.groupby('native_language').agg({
                'native_distance': 'mean',
                'english_distance': 'mean'
            }).reset_index()
            lang_stats['diff'] = lang_stats['native_distance'] - lang_stats['english_distance']
            worst_langs = lang_stats.nlargest(3, 'native_distance')
            print(f"     表现最差的语言:")
            for _, l in worst_langs.iterrows():
                print(f"       - {l['native_language']}: 母语={l['native_distance']:.2f}, 英语={l['english_distance']:.2f}")
    
    # 10.4 效果好的模型分析
    print("\n10.4 效果好的模型分析（整体距离最小的5个）:")
    best_models = model_effects_df.nsmallest(5, 'overall_dist')
    
    for _, row in best_models.iterrows():
        model_name = row['model']
        model_short = model_name.split('/')[-1][:30] if '/' in str(model_name) else str(model_name)[:30]
        print(f"   {model_short}: 整体={row['overall_dist']:.3f} (母语={row['native_dist']:.3f}, 英语={row['english_dist']:.3f})")
    
    # 11. 多语言国家最佳语言分析
    print("\n" + "=" * 70)
    print("11. 多语言国家最佳语言分析")
    print("=" * 70)
    
    if 'is_multilingual' in advantage_df.columns:
        multilingual_data = advantage_df[advantage_df['is_multilingual'] == True]
        if len(multilingual_data) > 0:
            multilingual_countries = multilingual_data['country'].unique()
            
            best_lang_summary = []
            for country in multilingual_countries:
                country_data = multilingual_data[multilingual_data['country'] == country]
                langs = country_data['native_language'].unique()
                
                print(f"\n   {country}:")
                
                # 计算每种语言的平均距离
                lang_performance = []
                for lang in langs:
                    lang_data = country_data[country_data['native_language'] == lang]
                    native_dist = lang_data['native_distance'].mean()
                    english_dist = lang_data['english_distance'].mean()
                    eng_adv = (native_dist - english_dist) / native_dist * 100
                    
                    lang_performance.append({
                        'language': lang,
                        'native_dist': native_dist,
                        'english_dist': english_dist,
                        'english_advantage': eng_adv,
                        'best_dist': min(native_dist, english_dist),
                        'best_choice': 'English' if english_dist < native_dist else lang
                    })
                
                lang_perf_df = pd.DataFrame(lang_performance)
                
                # 找出最佳语言（距离最小）
                best_overall = lang_perf_df.loc[lang_perf_df['best_dist'].idxmin()]
                
                print(f"     可用语言: {list(langs)}")
                for _, lp in lang_perf_df.iterrows():
                    marker = "★" if lp['best_dist'] == best_overall['best_dist'] else " "
                    print(f"     {marker} {lp['language']}: 母语距离={lp['native_dist']:.2f}, 英语距离={lp['english_dist']:.2f}, 英语优势={lp['english_advantage']:+.1f}%")
                
                print(f"     → 最佳选择: {best_overall['best_choice']} (距离={best_overall['best_dist']:.2f})")
                
                # 比较：用英语 vs 用最好的母语
                best_native = lang_perf_df['native_dist'].min()
                english_dist_avg = lang_perf_df['english_dist'].mean()  # 英语距离应该相同
                
                if english_dist_avg < best_native:
                    conclusion = f"英语优于所有母语 (英语={english_dist_avg:.2f} < 最佳母语={best_native:.2f})"
                else:
                    best_native_lang = lang_perf_df.loc[lang_perf_df['native_dist'].idxmin(), 'language']
                    conclusion = f"母语{best_native_lang}最佳 (={best_native:.2f} < 英语={english_dist_avg:.2f})"
                print(f"     → 结论: {conclusion}")
                
                best_lang_summary.append({
                    'country': country,
                    'languages': list(langs),
                    'best_choice': best_overall['best_choice'],
                    'best_distance': best_overall['best_dist'],
                    'english_distance': english_dist_avg,
                    'best_native_distance': best_native,
                    'conclusion': 'English' if english_dist_avg < best_native else 'Native'
                })
            
            if best_lang_summary:
                best_lang_df = pd.DataFrame(best_lang_summary)
                best_lang_df.to_csv(output_dir / 'multilingual_best_language.csv', index=False)
                
                # 总结
                english_wins = sum(1 for x in best_lang_summary if x['conclusion'] == 'English')
                native_wins = len(best_lang_summary) - english_wins
                print(f"\n   多语言国家总结:")
                print(f"     英语最佳: {english_wins}/{len(best_lang_summary)} 个国家")
                print(f"     母语最佳: {native_wins}/{len(best_lang_summary)} 个国家")
    
    # 保存结果
    results_df.to_csv(output_dir / 'distances_detailed.csv', index=False)
    results_df.to_excel(output_dir / 'distances_detailed.xlsx', index=False)
    advantage_df.to_csv(output_dir / 'english_advantage_by_model.csv', index=False)
    advantage_df.to_excel(output_dir / 'english_advantage_by_model.xlsx', index=False)
    avg_advantage.to_csv(output_dir / 'english_advantage_average.csv', index=False)
    avg_advantage.to_excel(output_dir / 'english_advantage_average.xlsx', index=False)
    
    if len(english_native_data) > 0:
        english_native_data.to_csv(output_dir / 'english_native_baseline.csv', index=False)
    
    print(f"\n✅ 结果已保存到: {output_dir}")
    
    return results_df, advantage_df, avg_advantage, english_native_data


def visualize_results(results_df, advantage_df, avg_advantage):
    """生成可视化图表"""
    print("\n9. 生成可视化图表...")
    
    output_dir = Path('results/analysis/stage0_vs_stage3')
    
    if len(advantage_df) == 0:
        print("⚠️ 没有英语优势数据可视化")
        return
    
    # 1. 英语优势分析图
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1.1 英语优势分布
    # 【修正】用平均距离计算整体英语优势
    overall_native = advantage_df['native_distance'].mean()
    overall_english = advantage_df['english_distance'].mean()
    overall_advantage = (overall_native - overall_english) / overall_native * 100
    
    axes[0, 0].hist(advantage_df['english_advantage'], bins=40, edgecolor='black', alpha=0.7)
    axes[0, 0].set_xlabel('英语优势 (%)')
    axes[0, 0].set_ylabel('频数')
    axes[0, 0].set_title('英语优势分布（非英语母语国家）')
    axes[0, 0].axvline(0, color='red', linestyle='--', linewidth=2, label='零点')
    axes[0, 0].axvline(overall_advantage, color='blue', 
                      linestyle='--', linewidth=2, label=f'整体英语优势: {overall_advantage:.1f}%')
    axes[0, 0].legend()
    
    # 1.2 英语优势排名（Top 20）
    top20 = avg_advantage.head(20)
    colors = ['green' if x > 0 else 'red' for x in top20['english_advantage']]
    axes[0, 1].barh(range(len(top20)), top20['english_advantage'], color=colors, alpha=0.7)
    axes[0, 1].set_yticks(range(len(top20)))
    axes[0, 1].set_yticklabels([f"{row['country'][:20]} ({row['native_language']})" 
                                for _, row in top20.iterrows()], fontsize=8)
    axes[0, 1].set_xlabel('英语优势 (%)')
    axes[0, 1].set_title('英语优势排名 (Top 20)')
    axes[0, 1].axvline(0, color='black', linestyle='-', linewidth=0.5)
    axes[0, 1].invert_yaxis()
    
    # 1.3 按模型的英语优势
    # 【修正】用平均距离计算每个模型的英语优势
    model_stats = advantage_df.groupby('model').agg({
        'native_distance': 'mean',
        'english_distance': 'mean'
    })
    model_stats['english_advantage'] = (model_stats['native_distance'] - model_stats['english_distance']) / model_stats['native_distance'] * 100
    model_avg = model_stats['english_advantage'].sort_values()
    
    axes[1, 0].bar(range(len(model_avg)), model_avg.values)
    axes[1, 0].set_xticks(range(len(model_avg)))
    axes[1, 0].set_xticklabels([m.split('/')[-1][:15] for m in model_avg.index], rotation=45, ha='right', fontsize=8)
    axes[1, 0].set_ylabel('平均英语优势 (%)')
    axes[1, 0].set_title('按模型的平均英语优势')
    axes[1, 0].axhline(0, color='black', linestyle='-', linewidth=0.5)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 1.4 官方语言 vs 英语距离对比
    native_dist = advantage_df['native_distance']
    english_dist = advantage_df['english_distance']
    axes[1, 1].scatter(native_dist, english_dist, alpha=0.5, s=20)
    max_val = max(native_dist.max(), english_dist.max())
    axes[1, 1].plot([0, max_val], [0, max_val], 'r--', label='y=x (相等线)')
    axes[1, 1].set_xlabel('官方语言距离')
    axes[1, 1].set_ylabel('英语距离')
    axes[1, 1].set_title('官方语言 vs 英语距离对比\n(点在线下方=英语更好)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'english_advantage_analysis.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: english_advantage_analysis.png")
    plt.close()
    
    # 2. 按文化区域的英语优势
    fig, ax = plt.subplots(figsize=(12, 8))
    
    region_stats = avg_advantage.groupby('cultural_region')['english_advantage'].agg(['mean', 'std', 'count']).reset_index()
    region_stats = region_stats.sort_values('mean', ascending=False)
    region_stats['se'] = region_stats['std'] / np.sqrt(region_stats['count'])
    
    colors = ['#E74C3C' if x > 0 else '#27AE60' for x in region_stats['mean']]
    bars = ax.barh(range(len(region_stats)), region_stats['mean'], 
                  xerr=region_stats['se'] * 1.96,
                  color=colors, alpha=0.7, edgecolor='black', capsize=3)
    
    ax.set_yticks(range(len(region_stats)))
    ax.set_yticklabels(region_stats['cultural_region'], fontsize=10)
    ax.set_xlabel('英语优势 (%)', fontsize=12)
    ax.set_title('按文化区域的英语优势（非英语母语国家，含95%置信区间）', fontsize=14)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()
    
    for i, (_, row) in enumerate(region_stats.iterrows()):
        ax.text(row['mean'] + 2, i, f'{row["mean"]:+.1f}% (n={int(row["count"])})', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cultural_regions_english_advantage.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: cultural_regions_english_advantage.png")
    plt.close()
    
    # 3. 全局散点图
    fig, ax = plt.subplots(figsize=(16, 14))
    
    country_summary = []
    for country in results_df['country'].unique():
        country_data = results_df[results_df['country'] == country]
        
        real_pc1 = country_data['real_PC1'].iloc[0]
        real_pc2 = country_data['real_PC2'].iloc[0]
        
        english = country_data[country_data['is_english']]
        eng_pc1 = english['llm_PC1'].mean() if len(english) > 0 else None
        eng_pc2 = english['llm_PC2'].mean() if len(english) > 0 else None
        
        native = country_data[country_data['is_using_native_language'] & ~country_data['is_english']]
        nat_pc1 = native['llm_PC1'].mean() if len(native) > 0 else None
        nat_pc2 = native['llm_PC2'].mean() if len(native) > 0 else None
        
        country_summary.append({
            'country': country,
            'real_pc1': real_pc1,
            'real_pc2': real_pc2,
            'eng_pc1': eng_pc1,
            'eng_pc2': eng_pc2,
            'nat_pc1': nat_pc1,
            'nat_pc2': nat_pc2
        })
    
    for item in country_summary:
        ax.scatter(item['real_pc1'], item['real_pc2'], c='gold', s=200, marker='*', 
                  alpha=0.8, edgecolors='black', linewidths=1.5, zorder=5)
    
    for item in country_summary:
        if item['eng_pc1'] is not None:
            ax.scatter(item['eng_pc1'], item['eng_pc2'], c='#27AE60', s=80, marker='o',
                      alpha=0.6, edgecolors='black', linewidths=0.8, zorder=4)
            ax.annotate('', xy=(item['eng_pc1'], item['eng_pc2']), 
                       xytext=(item['real_pc1'], item['real_pc2']),
                       arrowprops=dict(arrowstyle='->', lw=1, color='#27AE60', alpha=0.3))
    
    for item in country_summary:
        if item['nat_pc1'] is not None:
            ax.scatter(item['nat_pc1'], item['nat_pc2'], c='#E74C3C', s=80, marker='s',
                      alpha=0.6, edgecolors='black', linewidths=0.8, zorder=4)
            ax.annotate('', xy=(item['nat_pc1'], item['nat_pc2']), 
                       xytext=(item['real_pc1'], item['real_pc2']),
                       arrowprops=dict(arrowstyle='->', lw=1, color='#E74C3C', alpha=0.3, linestyle='--'))
    
    ax.set_xlabel('PC1 (生存 ← → 自我表达)', fontsize=13, fontweight='bold')
    ax.set_ylabel('PC2 (传统 ← → 现代)', fontsize=13, fontweight='bold')
    ax.set_title('全球文化坐标：Stage0真实位置 vs Stage3 LLM模仿位置\n(金星=真实, 绿圆=英语模仿, 红方=母语模仿)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(0, color='black', linewidth=1, alpha=0.5)
    ax.axvline(0, color='black', linewidth=1, alpha=0.5)
    
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', 
               markersize=15, label='真实位置 (Stage0)', markeredgecolor='black', markeredgewidth=1.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#27AE60', 
               markersize=10, label='英语模仿 (Stage3)', markeredgecolor='black', markeredgewidth=1),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#E74C3C', 
               markersize=10, label='母语模仿 (Stage3)', markeredgecolor='black', markeredgewidth=1),
    ]
    ax.legend(handles=legend_elements, loc='best', fontsize=12, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'global_coordinates_scatter.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ 保存: global_coordinates_scatter.png")
    plt.close()
    
    # 4. 东亚国家详细分析
    east_asian = ['China', 'Japan', 'Korea', 'Hong Kong', 'Taiwan', 'Macao', 'Singapore']
    
    ea_advantage = avg_advantage[avg_advantage['country'].str.contains('|'.join(east_asian), case=False, na=False)].copy()
    
    if len(ea_advantage) > 0:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        ea_advantage = ea_advantage.sort_values('english_advantage', ascending=False)
        colors = ['green' if x > 0 else 'red' for x in ea_advantage['english_advantage']]
        bars = ax.barh(range(len(ea_advantage)), ea_advantage['english_advantage'], 
                      color=colors, alpha=0.7, edgecolor='black')
        
        ax.set_yticks(range(len(ea_advantage)))
        ax.set_yticklabels([f"{row['country'][:25]}\n({row['native_language']})" 
                           for _, row in ea_advantage.iterrows()])
        ax.set_xlabel('英语优势 (%)', fontsize=12)
        ax.set_title('东亚国家/地区英语优势详细分析', fontsize=14)
        ax.axvline(0, color='black', linestyle='-', linewidth=1)
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()
        
        for i, (bar, val) in enumerate(zip(bars, ea_advantage['english_advantage'])):
            ax.text(val, i, f' {val:+.1f}%', va='center', 
                   ha='left' if val > 0 else 'right', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'east_asia_analysis.png', dpi=300, bbox_inches='tight')
        print(f"   ✅ 保存: east_asia_analysis.png")
        plt.close()
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")


if __name__ == '__main__':
    results_df, advantage_df, avg_advantage, english_native_baseline = calculate_distances()
    visualize_results(results_df, advantage_df, avg_advantage)
    
    print("\n" + "=" * 80)
    print("✅ Stage0 vs Stage3 分析完成！")
    print("=" * 80)
    print("\n核心发现（非英语母语国家）:")
    if len(advantage_df) > 0:
        avg_native = advantage_df['native_distance'].mean()
        avg_english = advantage_df['english_distance'].mean()
        # 使用平均距离计算英语优势（更稳健，不受极端值影响）
        english_advantage_robust = (avg_native - avg_english) / avg_native * 100
        
        print(f"  - 官方语言平均距离: {avg_native:.4f}")
        print(f"  - 英语平均距离: {avg_english:.4f}")
        print(f"  - 英语优势（基于平均距离）: {english_advantage_robust:+.1f}%")
        print(f"  - 英语优势（中位数）: {advantage_df['english_advantage'].median():+.1f}%")
        
        english_better = (advantage_df['english_advantage'] > 0).sum()
        native_better = (advantage_df['english_advantage'] < 0).sum()
        print(f"  - 英语更好的配对数: {english_better} ({english_better/len(advantage_df)*100:.1f}%)")
        print(f"  - 母语更好的配对数: {native_better} ({native_better/len(advantage_df)*100:.1f}%)")
    
    if english_native_baseline is not None and len(english_native_baseline) > 0:
        print(f"  - 英语母语国家基准: {english_native_baseline['distance'].mean():.4f}")
