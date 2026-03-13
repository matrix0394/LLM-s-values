"""
分析Stage3多语言角色扮演的文化距离计算方法

目标：
1. 对比官方语言不是英语的国家，分别用英语和官方语言模仿国家的坐标，和stage0真实国家的坐标计算文化距离
2. 官方语言本来就是英语的国家，计算和真实国家的文化距离作为英语基准
3. 计算每个国家、语言、模型的文化距离
"""

import pickle
import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def load_stage0_real_countries():
    """加载Stage0真实国家的PCA坐标"""
    # 优先使用JSON格式（避免pickle版本问题）
    json_path = PROJECT_ROOT / "data/country_values/country_scores_pca.json"
    
    if json_path.exists():
        print(f"✅ 加载Stage0真实国家数据 (JSON): {json_path.name}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换为DataFrame
        if isinstance(data, dict):
            # 如果是字典格式 {country: {pc1: x, pc2: y}}
            records = []
            for country, values in data.items():
                record = {'Country': country}
                record.update(values)
                records.append(record)
            df = pd.DataFrame(records)
        else:
            df = pd.DataFrame(data)
        
        print(f"   数据形状: {df.shape}")
        print(f"   列名: {list(df.columns)}")
        return df
    
    raise FileNotFoundError("未找到Stage0真实国家PCA数据 (JSON格式)")

def load_stage3_multilingual():
    """加载Stage3多语言角色扮演的PCA坐标"""
    # 优先使用CSV格式
    csv_path = PROJECT_ROOT / "data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.csv"
    json_path = PROJECT_ROOT / "data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.json"
    
    if csv_path.exists():
        print(f"✅ 加载Stage3多语言数据 (CSV): {csv_path.name}")
        data = pd.read_csv(csv_path)
        print(f"   数据形状: {data.shape}")
        print(f"   列名: {list(data.columns)}")
        return data
    
    if json_path.exists():
        print(f"✅ 加载Stage3多语言数据 (JSON): {json_path.name}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        print(f"   数据形状: {df.shape}")
        print(f"   列名: {list(df.columns)}")
        return df
    
    raise FileNotFoundError(f"未找到Stage3多语言PCA数据 (CSV/JSON格式)")

def load_language_config():
    """加载语言配置，获取国家-语言映射"""
    config_path = PROJECT_ROOT / "config/multilingual_questions_complete.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 构建国家到官方语言的映射（非英语国家）
    country_to_native_language = {}
    english_native_countries = set()
    
    # 先收集英语母语国家
    if 'en-native' in config['languages']:
        english_native_countries = set(config['languages']['en-native'].get('countries', []))
    
    # 再处理其他语言
    for lang_code, lang_info in config['languages'].items():
        if lang_code in ['en-native', 'en']:  # 跳过英语
            continue
        countries = lang_info.get('countries', [])
        for country in countries:
            # 非英语国家的官方语言（可能一个国家有多种语言，取第一个）
            if country not in country_to_native_language:
                country_to_native_language[country] = lang_code
    
    print(f"\n📊 语言配置:")
    print(f"   英语母语国家: {len(english_native_countries)} 个")
    print(f"   非英语国家（有官方语言映射）: {len(country_to_native_language)} 个")
    print(f"   非英语国家示例: {list(country_to_native_language.items())[:5]}")
    
    return country_to_native_language, english_native_countries

def calculate_euclidean_distance(coord1, coord2):
    """计算两点之间的欧几里得距离"""
    return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def analyze_data_structure():
    """分析数据结构"""
    print("\n" + "="*60)
    print("📊 数据结构分析")
    print("="*60)
    
    # 加载数据
    stage0_data = load_stage0_real_countries()
    stage3_data = load_stage3_multilingual()
    
    print("\n--- Stage0 真实国家数据 ---")
    print(f"数据类型: {type(stage0_data)}")
    if isinstance(stage0_data, pd.DataFrame):
        print(f"形状: {stage0_data.shape}")
        print(f"列名: {list(stage0_data.columns)}")
        print(f"\n前5行:")
        print(stage0_data.head())
        
        # 检查是否有国家名称列
        country_cols = [col for col in stage0_data.columns if 'country' in col.lower() or 'Country' in col]
        print(f"\n国家相关列: {country_cols}")
        
        # 检查PC坐标列
        pc_cols = [col for col in stage0_data.columns if 'PC' in col or 'pc' in col]
        print(f"PC坐标列: {pc_cols}")
    
    print("\n--- Stage3 多语言数据 ---")
    print(f"数据类型: {type(stage3_data)}")
    if isinstance(stage3_data, pd.DataFrame):
        print(f"形状: {stage3_data.shape}")
        print(f"列名: {list(stage3_data.columns)}")
        print(f"\n前5行:")
        print(stage3_data.head())
        
        # 检查语言列
        if 'language' in stage3_data.columns:
            print(f"\n语言分布:")
            print(stage3_data['language'].value_counts())
        
        # 检查国家列
        country_cols = [col for col in stage3_data.columns if 'country' in col.lower()]
        print(f"\n国家相关列: {country_cols}")
        
        # 检查模型列
        if 'model' in stage3_data.columns:
            print(f"\n模型分布:")
            print(stage3_data['model'].value_counts())
    
    return stage0_data, stage3_data

def calculate_cultural_distances(stage0_data, stage3_data):
    """计算文化距离"""
    print("\n" + "="*60)
    print("📏 计算文化距离")
    print("="*60)
    
    # 加载语言配置
    country_to_native_language, english_native_countries = load_language_config()
    
    # 确定Stage0数据中的国家名称列和坐标列
    # 根据数据结构调整
    stage0_country_col = None
    for col in ['Country', 'country', 'country_code', 'entity']:
        if col in stage0_data.columns:
            stage0_country_col = col
            break
    
    if stage0_country_col is None:
        # 如果没有国家列，可能国家名在索引中
        if stage0_data.index.name or isinstance(stage0_data.index, pd.Index):
            stage0_data = stage0_data.reset_index()
            stage0_country_col = stage0_data.columns[0]
    
    print(f"\nStage0 国家列: {stage0_country_col}")
    
    # 确定坐标列
    pc1_col_stage0 = None
    pc2_col_stage0 = None
    for col in stage0_data.columns:
        if 'PC1' in col or 'pc1' in col:
            pc1_col_stage0 = col
        if 'PC2' in col or 'pc2' in col:
            pc2_col_stage0 = col
    
    print(f"Stage0 PC1列: {pc1_col_stage0}, PC2列: {pc2_col_stage0}")
    
    # 构建Stage0国家坐标字典
    stage0_coords = {}
    for _, row in stage0_data.iterrows():
        country = row[stage0_country_col]
        if pd.notna(row[pc1_col_stage0]) and pd.notna(row[pc2_col_stage0]):
            stage0_coords[country] = (row[pc1_col_stage0], row[pc2_col_stage0])
    
    print(f"\nStage0 有效国家坐标: {len(stage0_coords)} 个")
    print(f"示例国家: {list(stage0_coords.keys())[:10]}")
    
    # 确定Stage3数据中的列
    stage3_country_col = 'country' if 'country' in stage3_data.columns else 'Country'
    pc1_col_stage3 = 'PC1' if 'PC1' in stage3_data.columns else 'PC1_rescaled'
    pc2_col_stage3 = 'PC2' if 'PC2' in stage3_data.columns else 'PC2_rescaled'
    
    print(f"\nStage3 国家列: {stage3_country_col}")
    print(f"Stage3 PC1列: {pc1_col_stage3}, PC2列: {pc2_col_stage3}")
    
    # 计算文化距离
    results = []
    
    # 统计跳过的行数
    skipped_no_language = 0
    skipped_no_model = 0
    
    for _, row in stage3_data.iterrows():
        country = row[stage3_country_col]
        language = row.get('language')
        model = row.get('model_name', row.get('model'))
        
        # 跳过无效的国家名
        if pd.isna(country) or not isinstance(country, str):
            continue
        
        # 跳过没有语言信息的行（这些是Stage0基准数据，不是Stage3模仿数据）
        if pd.isna(language) or language == '' or language == 'unknown':
            skipped_no_language += 1
            continue
        
        # 跳过没有模型信息的行
        if pd.isna(model) or model == '' or model == 'unknown':
            skipped_no_model += 1
            continue
        
        # 获取Stage3坐标
        pc1 = row.get(pc1_col_stage3)
        pc2 = row.get(pc2_col_stage3)
        
        if pd.isna(pc1) or pd.isna(pc2):
            continue
        
        stage3_coord = (pc1, pc2)
        
        # 查找对应的Stage0真实国家坐标
        # 需要处理国家名称匹配问题
        stage0_coord = None
        matched_country = None
        
        for s0_country in stage0_coords.keys():
            if not isinstance(s0_country, str):
                continue
            if country.lower() in s0_country.lower() or s0_country.lower() in country.lower():
                stage0_coord = stage0_coords[s0_country]
                matched_country = s0_country
                break
        
        if stage0_coord is None:
            continue
        
        # 计算欧几里得距离
        distance = calculate_euclidean_distance(stage3_coord, stage0_coord)
        
        # 判断语言类型：en 和 en-native 都算英语
        is_english = language in ['en', 'en-native']
        
        # 模糊匹配国家名来查找官方语言
        native_language = country_to_native_language.get(country)
        is_english_native = country in english_native_countries
        
        # 如果精确匹配失败，尝试模糊匹配
        if native_language is None and not is_english_native:
            for config_country in country_to_native_language.keys():
                if country.lower() in config_country.lower() or config_country.lower() in country.lower():
                    native_language = country_to_native_language[config_country]
                    break
            # 检查是否是英语母语国家
            for en_country in english_native_countries:
                if country.lower() in en_country.lower() or en_country.lower() in country.lower():
                    is_english_native = True
                    break
        
        # 判断是否使用官方语言
        if native_language:
            # 非英语国家：官方语言不是英语
            is_native_language = (language == native_language)
        else:
            # 英语母语国家或未知：英语就是官方语言
            is_native_language = is_english
        
        results.append({
            'country': country,
            'matched_stage0_country': matched_country,
            'language': language,
            'model': model,
            'stage3_pc1': pc1,
            'stage3_pc2': pc2,
            'stage0_pc1': stage0_coord[0],
            'stage0_pc2': stage0_coord[1],
            'cultural_distance': distance,
            'is_english_native_country': is_english_native,
            'native_language': native_language if native_language else 'en',
            'is_using_native_language': is_native_language,
            'is_english': is_english
        })
    
    results_df = pd.DataFrame(results)
    print(f"\n✅ 计算完成，共 {len(results_df)} 条记录")
    print(f"   跳过无语言信息的行: {skipped_no_language}")
    print(f"   跳过无模型信息的行: {skipped_no_model}")
    
    return results_df

def analyze_distance_results(results_df):
    """分析文化距离结果"""
    print("\n" + "="*60)
    print("📈 文化距离分析结果")
    print("="*60)
    
    if results_df.empty:
        print("⚠️ 没有有效的距离计算结果")
        return
    
    # 0. 异常值检测与处理
    print("\n--- 异常值分析 ---")
    distances = results_df['cultural_distance']
    
    # 方法1: IQR方法检测异常值
    Q1 = distances.quantile(0.25)
    Q3 = distances.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers_iqr = results_df[(distances < lower_bound) | (distances > upper_bound)]
    
    # 方法2: 3σ原则
    mean_dist = distances.mean()
    std_dist = distances.std()
    outliers_3sigma = results_df[(distances < mean_dist - 3*std_dist) | (distances > mean_dist + 3*std_dist)]
    
    print(f"IQR方法 (Q1={Q1:.2f}, Q3={Q3:.2f}, IQR={IQR:.2f}):")
    print(f"  异常值范围: <{lower_bound:.2f} 或 >{upper_bound:.2f}")
    print(f"  异常值数量: {len(outliers_iqr)} ({len(outliers_iqr)/len(results_df)*100:.1f}%)")
    
    print(f"\n3σ原则 (μ={mean_dist:.2f}, σ={std_dist:.2f}):")
    print(f"  异常值范围: <{mean_dist-3*std_dist:.2f} 或 >{mean_dist+3*std_dist:.2f}")
    print(f"  异常值数量: {len(outliers_3sigma)} ({len(outliers_3sigma)/len(results_df)*100:.1f}%)")
    
    # 创建去除异常值后的数据集
    results_trimmed = results_df[(distances >= lower_bound) & (distances <= upper_bound)].copy()
    print(f"\n去除IQR异常值后: {len(results_trimmed)} 条记录")
    
    # 1. 整体统计（原始 vs 去异常值）
    print("\n--- 整体统计 ---")
    print(f"{'指标':<15} {'原始数据':<15} {'去异常值后':<15}")
    print(f"{'记录数':<15} {len(results_df):<15} {len(results_trimmed):<15}")
    print(f"{'平均距离':<15} {results_df['cultural_distance'].mean():<15.4f} {results_trimmed['cultural_distance'].mean():<15.4f}")
    print(f"{'中位数':<15} {results_df['cultural_distance'].median():<15.4f} {results_trimmed['cultural_distance'].median():<15.4f}")
    print(f"{'标准差':<15} {results_df['cultural_distance'].std():<15.4f} {results_trimmed['cultural_distance'].std():<15.4f}")
    print(f"{'最小值':<15} {results_df['cultural_distance'].min():<15.4f} {results_trimmed['cultural_distance'].min():<15.4f}")
    print(f"{'最大值':<15} {results_df['cultural_distance'].max():<15.4f} {results_trimmed['cultural_distance'].max():<15.4f}")
    
    # 2. 按语言分组统计（使用中位数更稳健）
    print("\n--- 按语言分组的文化距离 ---")
    lang_stats = results_df.groupby('language')['cultural_distance'].agg(['mean', 'median', 'std', 'count'])
    lang_stats = lang_stats.sort_values('mean')
    print(lang_stats)
    
    # 3. 英语母语国家 vs 非英语母语国家
    print("\n--- 英语母语国家 vs 非英语母语国家 ---")
    english_native = results_df[results_df['is_english_native_country']]
    non_english_native = results_df[~results_df['is_english_native_country']]
    
    print(f"英语母语国家:")
    print(f"  记录数: {len(english_native)}")
    print(f"  平均距离: {english_native['cultural_distance'].mean():.4f}")
    
    print(f"\n非英语母语国家:")
    print(f"  记录数: {len(non_english_native)}")
    print(f"  平均距离: {non_english_native['cultural_distance'].mean():.4f}")
    
    # 4. 非英语国家：官方语言 vs 英语
    print("\n--- 非英语国家：官方语言 vs 英语 ---")
    non_english_countries = results_df[~results_df['is_english_native_country']]
    
    # 使用官方语言的记录
    using_native = non_english_countries[non_english_countries['is_using_native_language']]
    # 使用英语的记录 (en 或 en-native)
    using_english = non_english_countries[non_english_countries['is_english']]
    
    print(f"使用官方语言:")
    print(f"  记录数: {len(using_native)}")
    if len(using_native) > 0:
        print(f"  平均距离: {using_native['cultural_distance'].mean():.4f}")
    
    print(f"\n使用英语 (en/en-native):")
    print(f"  记录数: {len(using_english)}")
    if len(using_english) > 0:
        print(f"  平均距离: {using_english['cultural_distance'].mean():.4f}")
    
    # 5. 按国家对比官方语言和英语
    print("\n--- 按国家对比：官方语言 vs 英语 ---")
    country_comparison = []
    
    for country in non_english_countries['country'].unique():
        country_data = non_english_countries[non_english_countries['country'] == country]
        
        native_lang = country_data['native_language'].iloc[0]
        native_dist = country_data[country_data['language'] == native_lang]['cultural_distance'].mean()
        # 英语包括 en 和 en-native
        english_dist = country_data[country_data['is_english']]['cultural_distance'].mean()
        
        if pd.notna(native_dist) and pd.notna(english_dist) and native_dist > 0:
            # 计算两种指标
            abs_diff = english_dist - native_dist  # 绝对差异：正值=官方语言更好
            pct_advantage = (native_dist - english_dist) / native_dist * 100  # 百分比优势：正值=英语更好
            
            country_comparison.append({
                'country': country,
                'native_language': native_lang,
                'native_distance': native_dist,
                'english_distance': english_dist,
                'abs_difference': abs_diff,  # 绝对差异
                'english_advantage_pct': pct_advantage,  # 英语优势百分比
                'better_language': native_lang if native_dist < english_dist else 'en'
            })
    
    if country_comparison:
        comparison_df = pd.DataFrame(country_comparison)
        comparison_df = comparison_df.sort_values('english_advantage_pct', ascending=False)
        print(comparison_df.to_string())
        
        # 统计哪种语言更好
        native_better = (comparison_df['abs_difference'] > 0).sum()
        english_better = (comparison_df['abs_difference'] < 0).sum()
        tie = (comparison_df['abs_difference'] == 0).sum()
        print(f"\n官方语言更好的国家: {native_better}")
        print(f"英语更好的国家: {english_better}")
        if tie > 0:
            print(f"持平: {tie}")
        
        # 计算两种平均指标
        avg_abs_diff = comparison_df['abs_difference'].mean()
        avg_pct_adv = comparison_df['english_advantage_pct'].mean()
        
        print(f"\n=== 两种计算方法对比 ===")
        print(f"绝对差异 (英语距离 - 官方语言距离): {avg_abs_diff:.4f}")
        print(f"百分比优势 (英语优势%): {avg_pct_adv:+.2f}%")
        
        if avg_abs_diff > 0:
            print("→ 绝对差异：官方语言更好")
        else:
            print("→ 绝对差异：英语更好")
        
        if avg_pct_adv > 0:
            print("→ 百分比优势：英语更好")
        else:
            print("→ 百分比优势：官方语言更好")
        
        # 按语言分组统计百分比优势
        print("\n--- 按语言分组的英语优势 ---")
        lang_advantage = comparison_df.groupby('native_language')['english_advantage_pct'].agg(['mean', 'std', 'count'])
        lang_advantage = lang_advantage.sort_values('mean', ascending=False)
        print(lang_advantage)
    
    # 6. 按模型分组统计
    print("\n--- 按模型分组的文化距离 ---")
    model_stats = results_df.groupby('model')['cultural_distance'].agg(['mean', 'std', 'count'])
    model_stats = model_stats.sort_values('mean')
    print(model_stats)
    
    # 7. 按文化区域分析
    print("\n--- 按文化区域分析 ---")
    if 'Cultural Region' in results_df.columns or results_df['country'].notna().any():
        # 从Stage0数据获取文化区域信息
        region_stats = []
        for country in results_df['country'].unique():
            country_data = results_df[results_df['country'] == country]
            # 获取该国家用官方语言和英语的平均距离
            native_lang = country_data['native_language'].iloc[0]
            native_dist = country_data[country_data['language'] == native_lang]['cultural_distance'].mean()
            english_dist = country_data[country_data['is_english']]['cultural_distance'].mean()
            if pd.notna(native_dist) and pd.notna(english_dist):
                region_stats.append({
                    'country': country,
                    'native_distance': native_dist,
                    'english_distance': english_dist,
                    'diff': english_dist - native_dist
                })
        if region_stats:
            region_df = pd.DataFrame(region_stats)
            print(f"国家数: {len(region_df)}")
            print(f"官方语言平均距离: {region_df['native_distance'].mean():.4f}")
            print(f"英语平均距离: {region_df['english_distance'].mean():.4f}")
    
    # 8. 模型×语言交互分析
    print("\n--- 模型×语言交互分析 ---")
    model_lang_stats = results_df.groupby(['model', 'language'])['cultural_distance'].mean().unstack()
    print("各模型在不同语言下的平均文化距离:")
    print(model_lang_stats.round(3).to_string())
    
    # 9. 统计显著性检验（配对t检验）
    print("\n--- 统计显著性检验 ---")
    from scipy import stats
    
    # 对于有配对数据的国家，进行配对t检验
    paired_data = []
    for country in non_english_countries['country'].unique():
        country_data = non_english_countries[non_english_countries['country'] == country]
        native_lang = country_data['native_language'].iloc[0]
        
        # 获取每个模型的配对数据
        for model in country_data['model'].unique():
            model_data = country_data[country_data['model'] == model]
            native_dist = model_data[model_data['language'] == native_lang]['cultural_distance'].values
            english_dist = model_data[model_data['is_english']]['cultural_distance'].values
            
            if len(native_dist) > 0 and len(english_dist) > 0:
                paired_data.append({
                    'country': country,
                    'model': model,
                    'native_distance': native_dist[0],
                    'english_distance': english_dist[0]
                })
    
    if paired_data:
        paired_df = pd.DataFrame(paired_data)
        native_dists = paired_df['native_distance'].values
        english_dists = paired_df['english_distance'].values
        
        # 配对t检验
        t_stat, p_value = stats.ttest_rel(native_dists, english_dists)
        
        # 计算差异的详细统计
        differences = native_dists - english_dists  # 正值=英语更好
        
        print(f"配对样本数: {len(paired_df)}")
        print(f"官方语言平均距离: {native_dists.mean():.4f} (std={native_dists.std():.4f})")
        print(f"英语平均距离: {english_dists.mean():.4f} (std={english_dists.std():.4f})")
        print(f"平均差异 (官方语言-英语): {differences.mean():.4f} (std={differences.std():.4f})")
        print(f"差异范围: [{differences.min():.4f}, {differences.max():.4f}]")
        
        # 计算英语更好的比例
        english_better_count = (differences > 0).sum()
        native_better_count = (differences < 0).sum()
        print(f"\n英语更好的配对数: {english_better_count} ({english_better_count/len(differences)*100:.1f}%)")
        print(f"官方语言更好的配对数: {native_better_count} ({native_better_count/len(differences)*100:.1f}%)")
        
        print(f"\n配对t检验: t={t_stat:.4f}, p={p_value:.6f}")
        if p_value < 0.05:
            if native_dists.mean() > english_dists.mean():
                print("→ 英语显著优于官方语言 (p<0.05)")
            else:
                print("→ 官方语言显著优于英语 (p<0.05)")
        else:
            print("→ 两种语言无显著差异 (p>=0.05)")
            print(f"   注意：虽然英语平均更好 ({english_dists.mean():.4f} < {native_dists.mean():.4f})，")
            print(f"   但由于方差大 (std={differences.std():.4f})，差异不具统计显著性")
        
        # Wilcoxon符号秩检验（非参数检验，更稳健）
        try:
            w_stat, w_pvalue = stats.wilcoxon(native_dists, english_dists)
            print(f"\nWilcoxon符号秩检验: W={w_stat:.2f}, p={w_pvalue:.6f}")
            if w_pvalue < 0.05:
                print("→ 非参数检验显示显著差异 *")
        except Exception:
            pass
        
        # 符号检验（最简单：英语更好的次数是否显著多于50%）
        try:
            # 使用二项检验 (新版scipy用binomtest)
            from scipy.stats import binomtest
            n_total = english_better_count + native_better_count
            result = binomtest(english_better_count, n_total, 0.5, alternative='two-sided')
            sign_pvalue = result.pvalue
            print(f"\n符号检验 (英语更好 vs 官方语言更好): p={sign_pvalue:.6f}")
            if sign_pvalue < 0.05:
                if english_better_count > native_better_count:
                    print("→ 英语显著更常获胜 *")
                else:
                    print("→ 官方语言显著更常获胜 *")
        except Exception as e:
            print(f"符号检验失败: {e}")
    
    # 10. 按语言家族分析
    print("\n--- 按语言家族分析 ---")
    language_families = {
        'Romance': ['es', 'fr', 'it', 'pt'],
        'Germanic': ['de', 'en', 'en-native'],
        'Slavic': ['ru'],
        'Semitic': ['ar'],
        'Sino-Tibetan': ['zh-cn', 'zh-tw', 'zh-hk'],
        'Japonic': ['ja'],
        'Koreanic': ['ko']
    }
    
    family_stats = []
    for family, langs in language_families.items():
        family_data = results_df[results_df['language'].isin(langs)]
        if len(family_data) > 0:
            family_stats.append({
                'family': family,
                'mean_distance': family_data['cultural_distance'].mean(),
                'std': family_data['cultural_distance'].std(),
                'count': len(family_data)
            })
    
    if family_stats:
        family_df = pd.DataFrame(family_stats).sort_values('mean_distance')
        print(family_df.to_string(index=False))
    
    # 11. 模型×语言交互效应深度分析
    analyze_model_language_interaction(results_df)
    
    return results_df


def analyze_model_language_interaction(results_df):
    """深度分析模型×语言的交互效应"""
    print("\n" + "="*60)
    print("🔬 模型×语言交互效应深度分析")
    print("="*60)
    
    from scipy import stats
    
    # 只分析非英语母语国家的数据（有官方语言 vs 英语的对比）
    non_english_countries = results_df[~results_df['is_english_native_country']].copy()
    
    # 1. 每个模型的语言偏好分析
    print("\n--- 1. 每个模型的语言偏好 ---")
    print("(正值=官方语言更好，负值=英语更好)")
    
    model_lang_preference = []
    for model in non_english_countries['model'].unique():
        if pd.isna(model) or model == 'unknown':
            continue
        model_data = non_english_countries[non_english_countries['model'] == model]
        
        # 计算该模型下，官方语言 vs 英语的平均距离
        native_dist = model_data[model_data['is_using_native_language']]['cultural_distance'].mean()
        english_dist = model_data[model_data['is_english']]['cultural_distance'].mean()
        
        if pd.notna(native_dist) and pd.notna(english_dist):
            diff = english_dist - native_dist  # 正值=官方语言更好
            model_lang_preference.append({
                'model': model,
                'native_distance': native_dist,
                'english_distance': english_dist,
                'difference': diff,
                'better': 'native' if diff > 0 else 'english',
                'native_count': len(model_data[model_data['is_using_native_language']]),
                'english_count': len(model_data[model_data['is_english']])
            })
    
    if model_lang_preference:
        pref_df = pd.DataFrame(model_lang_preference).sort_values('difference', ascending=False)
        print(pref_df.to_string(index=False))
        
        # 统计
        native_better_models = (pref_df['difference'] > 0).sum()
        english_better_models = (pref_df['difference'] < 0).sum()
        print(f"\n官方语言更好的模型数: {native_better_models}")
        print(f"英语更好的模型数: {english_better_models}")
    
    # 2. 双因素方差分析 (Two-way ANOVA)
    print("\n--- 2. 双因素方差分析 (Model × Language Type) ---")
    
    # 准备数据：只保留有配对的数据
    anova_data = []
    for _, row in non_english_countries.iterrows():
        if pd.isna(row['model']) or row['model'] == 'unknown':
            continue
        lang_type = 'native' if row['is_using_native_language'] else ('english' if row['is_english'] else 'other')
        if lang_type != 'other':
            anova_data.append({
                'model': row['model'],
                'language_type': lang_type,
                'distance': row['cultural_distance']
            })
    
    if anova_data:
        anova_df = pd.DataFrame(anova_data)
        
        # 计算各组均值
        group_means = anova_df.groupby(['model', 'language_type'])['distance'].mean().unstack()
        print("\n各模型在不同语言类型下的平均距离:")
        print(group_means.round(3).to_string())
        
        # 计算主效应和交互效应
        # 模型主效应
        model_means = anova_df.groupby('model')['distance'].mean()
        model_var = model_means.var()
        
        # 语言类型主效应
        lang_means = anova_df.groupby('language_type')['distance'].mean()
        lang_var = lang_means.var()
        
        print(f"\n模型主效应 (方差): {model_var:.4f}")
        print(f"语言类型主效应 (方差): {lang_var:.4f}")
        print(f"模型效应 / 语言效应 比值: {model_var/lang_var:.2f}x")
        
        if model_var > lang_var * 10:
            print("→ 模型效应远大于语言效应")
        elif model_var > lang_var:
            print("→ 模型效应大于语言效应")
        else:
            print("→ 语言效应大于模型效应")
    
    # 3. 模型在特定语言上的表现差异
    print("\n--- 3. 模型在特定语言上的表现 ---")
    
    # 按语言分组，看哪个模型在该语言上表现最好
    languages_to_analyze = ['ar', 'es', 'fr', 'de', 'ru', 'zh-cn', 'ja', 'ko']
    
    for lang in languages_to_analyze:
        lang_data = results_df[results_df['language'] == lang]
        if len(lang_data) == 0:
            continue
        
        model_perf = lang_data.groupby('model')['cultural_distance'].agg(['mean', 'std', 'count'])
        model_perf = model_perf[model_perf['count'] >= 3]  # 至少3个样本
        if len(model_perf) > 0:
            model_perf = model_perf.sort_values('mean')
            best_model = model_perf.index[0]
            worst_model = model_perf.index[-1]
            print(f"\n{lang}: 最佳={best_model} ({model_perf.loc[best_model, 'mean']:.2f}), "
                  f"最差={worst_model} ({model_perf.loc[worst_model, 'mean']:.2f})")
    
    # 4. 模型的语言敏感度分析
    print("\n--- 4. 模型的语言敏感度 (跨语言表现一致性) ---")
    print("(标准差越小=跨语言表现越一致)")
    
    model_sensitivity = []
    for model in results_df['model'].unique():
        if pd.isna(model) or model == 'unknown':
            continue
        model_data = results_df[results_df['model'] == model]
        
        # 计算该模型在不同语言上的平均距离的标准差
        lang_means = model_data.groupby('language')['cultural_distance'].mean()
        if len(lang_means) >= 3:  # 至少3种语言
            model_sensitivity.append({
                'model': model,
                'mean_distance': model_data['cultural_distance'].mean(),
                'cross_lang_std': lang_means.std(),
                'num_languages': len(lang_means)
            })
    
    if model_sensitivity:
        sens_df = pd.DataFrame(model_sensitivity).sort_values('cross_lang_std')
        print(sens_df.to_string(index=False))
        
        # 找出最一致和最不一致的模型
        most_consistent = sens_df.iloc[0]['model']
        least_consistent = sens_df.iloc[-1]['model']
        print(f"\n跨语言最一致的模型: {most_consistent}")
        print(f"跨语言最不一致的模型: {least_consistent}")
    
    # 5. 特定语言对的配对分析
    print("\n--- 5. 官方语言 vs 英语：按模型的配对t检验 ---")
    
    # 过滤掉NaN值后再排序
    valid_models = [m for m in non_english_countries['model'].unique() if pd.notna(m) and m != 'unknown']
    for model in sorted(valid_models):
        model_data = non_english_countries[non_english_countries['model'] == model]
        
        # 收集配对数据
        paired = []
        for country in model_data['country'].unique():
            country_data = model_data[model_data['country'] == country]
            native_lang = country_data['native_language'].iloc[0]
            
            native_dist = country_data[country_data['language'] == native_lang]['cultural_distance'].values
            english_dist = country_data[country_data['is_english']]['cultural_distance'].values
            
            if len(native_dist) > 0 and len(english_dist) > 0:
                paired.append((native_dist[0], english_dist[0]))
        
        if len(paired) >= 5:  # 至少5个配对
            native_dists = [p[0] for p in paired]
            english_dists = [p[1] for p in paired]
            t_stat, p_value = stats.ttest_rel(native_dists, english_dists)
            
            diff = np.mean(english_dists) - np.mean(native_dists)
            sig = "*" if p_value < 0.05 else ""
            better = "native" if diff > 0 else "english"
            print(f"{model}: diff={diff:+.3f} ({better}), t={t_stat:.2f}, p={p_value:.3f} {sig}")
    
    # 6. 效应量分析 (Cohen's d)
    print("\n--- 6. 效应量分析 (Cohen's d) ---")
    
    native_all = non_english_countries[non_english_countries['is_using_native_language']]['cultural_distance']
    english_all = non_english_countries[non_english_countries['is_english']]['cultural_distance']
    
    if len(native_all) > 0 and len(english_all) > 0:
        # Cohen's d = (M1 - M2) / pooled_std
        pooled_std = np.sqrt((native_all.std()**2 + english_all.std()**2) / 2)
        cohens_d = (native_all.mean() - english_all.mean()) / pooled_std
        
        print(f"官方语言平均距离: {native_all.mean():.4f}")
        print(f"英语平均距离: {english_all.mean():.4f}")
        print(f"Cohen's d: {cohens_d:.4f}")
        
        if abs(cohens_d) < 0.2:
            print("→ 效应量极小 (negligible)")
        elif abs(cohens_d) < 0.5:
            print("→ 效应量小 (small)")
        elif abs(cohens_d) < 0.8:
            print("→ 效应量中等 (medium)")
        else:
            print("→ 效应量大 (large)")
    
    # 7. 模型来源国家分析 - 本土优势检验
    analyze_model_origin_effect(results_df)


def analyze_model_origin_effect(results_df):
    """分析模型来源国家是否存在本土优势"""
    print("\n" + "="*60)
    print("🌍 模型来源国家分析 - 本土优势检验")
    print("="*60)
    
    from scipy import stats
    
    # 模型来源国家/地区映射
    model_origin = {
        'claude-3-7-sonnet-20250219': ('Anthropic', 'US'),
        'claude-sonnet-4.5': ('Anthropic', 'US'),
        'gpt-4o': ('OpenAI', 'US'),
        'gpt-4o-mini': ('OpenAI', 'US'),
        'gpt-5.1': ('OpenAI', 'US'),
        'deepseek-chat': ('DeepSeek', 'CN'),
        'deepseek-chat-v3.1': ('DeepSeek', 'CN'),
        'kimi-k2': ('Moonshot', 'CN'),
        'qwen3-1.7b': ('Alibaba', 'CN'),
        'qwen3-max': ('Alibaba', 'CN'),
        'gemini-2.5-flash': ('Google', 'US'),
        'gemini-2.5-pro': ('Google', 'US'),
        'gemini-3-pro-preview': ('Google', 'US'),
        'gemma-3-4b-it': ('Google', 'US'),
        'llama-3.2-3b-instruct': ('Meta', 'US'),
        'llama-3.3-70b-instruct': ('Meta', 'US'),
        'grok-4.1-fast': ('xAI', 'US'),
        'mistral-nemo': ('Mistral', 'EU'),
        'mistral-medium-3.1': ('Mistral', 'EU'),
        'phi-3-mini-128k-instruct': ('Microsoft', 'US'),
    }
    
    # 国家/地区到语言的映射
    region_languages = {
        'US': ['en', 'en-native'],
        'CN': ['zh-cn', 'zh-tw', 'zh-hk'],
        'EU': ['fr', 'de', 'es', 'it', 'pt'],  # 欧洲语言
    }
    
    # 1. 按模型来源地区分组
    print("\n--- 1. 按模型来源地区分组 ---")
    
    region_stats = {'US': [], 'CN': [], 'EU': []}
    for model in results_df['model'].unique():
        if pd.isna(model) or model == 'unknown':
            continue
        if model in model_origin:
            _, region = model_origin[model]
            model_data = results_df[results_df['model'] == model]
            mean_dist = model_data['cultural_distance'].mean()
            region_stats[region].append({'model': model, 'mean_distance': mean_dist})
    
    for region, models in region_stats.items():
        if models:
            avg = np.mean([m['mean_distance'] for m in models])
            print(f"\n{region} 模型 ({len(models)}个):")
            for m in sorted(models, key=lambda x: x['mean_distance']):
                print(f"  {m['model']}: {m['mean_distance']:.3f}")
            print(f"  平均: {avg:.3f}")
    
    # 2. 本土优势检验：模型在本国语言上是否表现更好
    print("\n--- 2. 本土优势检验 ---")
    print("(检验模型在本国/本地区语言上是否有优势)")
    
    home_advantage = []
    for model in results_df['model'].unique():
        if pd.isna(model) or model == 'unknown' or model not in model_origin:
            continue
        
        _, region = model_origin[model]
        home_langs = region_languages.get(region, [])
        
        model_data = results_df[results_df['model'] == model]
        
        # 本土语言表现
        home_data = model_data[model_data['language'].isin(home_langs)]
        # 非本土语言表现
        away_data = model_data[~model_data['language'].isin(home_langs)]
        
        if len(home_data) > 0 and len(away_data) > 0:
            home_dist = home_data['cultural_distance'].mean()
            away_dist = away_data['cultural_distance'].mean()
            diff = away_dist - home_dist  # 正值=本土优势
            
            home_advantage.append({
                'model': model,
                'region': region,
                'home_distance': home_dist,
                'away_distance': away_dist,
                'advantage': diff,
                'has_advantage': diff > 0
            })
    
    if home_advantage:
        adv_df = pd.DataFrame(home_advantage).sort_values('advantage', ascending=False)
        print(adv_df.to_string(index=False))
        
        # 统计
        with_advantage = adv_df['has_advantage'].sum()
        without_advantage = len(adv_df) - with_advantage
        print(f"\n有本土优势的模型: {with_advantage}")
        print(f"无本土优势的模型: {without_advantage}")
        
        # 按地区统计
        for region in ['US', 'CN', 'EU']:
            region_data = adv_df[adv_df['region'] == region]
            if len(region_data) > 0:
                avg_adv = region_data['advantage'].mean()
                print(f"{region} 模型平均本土优势: {avg_adv:+.3f}")
    
    # 3. 中国模型在中文上的表现 vs 美国模型在中文上的表现
    print("\n--- 3. 中国模型 vs 美国模型：在中文上的表现 ---")
    
    cn_models = [m for m, (_, r) in model_origin.items() if r == 'CN']
    us_models = [m for m, (_, r) in model_origin.items() if r == 'US']
    
    chinese_langs = ['zh-cn', 'zh-tw', 'zh-hk']
    
    cn_on_chinese = results_df[(results_df['model'].isin(cn_models)) & 
                               (results_df['language'].isin(chinese_langs))]
    us_on_chinese = results_df[(results_df['model'].isin(us_models)) & 
                               (results_df['language'].isin(chinese_langs))]
    
    if len(cn_on_chinese) > 0 and len(us_on_chinese) > 0:
        cn_mean = cn_on_chinese['cultural_distance'].mean()
        us_mean = us_on_chinese['cultural_distance'].mean()
        
        print(f"中国模型在中文上的平均距离: {cn_mean:.3f}")
        print(f"美国模型在中文上的平均距离: {us_mean:.3f}")
        print(f"差异: {us_mean - cn_mean:+.3f}")
        
        # t检验
        t_stat, p_value = stats.ttest_ind(cn_on_chinese['cultural_distance'], 
                                          us_on_chinese['cultural_distance'])
        print(f"独立样本t检验: t={t_stat:.2f}, p={p_value:.4f}")
        if p_value < 0.05:
            if cn_mean < us_mean:
                print("→ 中国模型在中文上显著更好 *")
            else:
                print("→ 美国模型在中文上显著更好 *")
        else:
            print("→ 无显著差异")
    
    # 4. 美国模型在英语上的表现 vs 中国模型在英语上的表现
    print("\n--- 4. 美国模型 vs 中国模型：在英语上的表现 ---")
    
    english_langs = ['en', 'en-native']
    
    us_on_english = results_df[(results_df['model'].isin(us_models)) & 
                               (results_df['language'].isin(english_langs))]
    cn_on_english = results_df[(results_df['model'].isin(cn_models)) & 
                               (results_df['language'].isin(english_langs))]
    
    if len(us_on_english) > 0 and len(cn_on_english) > 0:
        us_mean = us_on_english['cultural_distance'].mean()
        cn_mean = cn_on_english['cultural_distance'].mean()
        
        print(f"美国模型在英语上的平均距离: {us_mean:.3f}")
        print(f"中国模型在英语上的平均距离: {cn_mean:.3f}")
        print(f"差异: {cn_mean - us_mean:+.3f}")
        
        # t检验
        t_stat, p_value = stats.ttest_ind(us_on_english['cultural_distance'], 
                                          cn_on_english['cultural_distance'])
        print(f"独立样本t检验: t={t_stat:.2f}, p={p_value:.4f}")
        if p_value < 0.05:
            if us_mean < cn_mean:
                print("→ 美国模型在英语上显著更好 *")
            else:
                print("→ 中国模型在英语上显著更好 *")
        else:
            print("→ 无显著差异")
    
    # 5. 欧洲模型在欧洲语言上的表现
    print("\n--- 5. 欧洲模型 vs 其他模型：在欧洲语言上的表现 ---")
    
    eu_models = [m for m, (_, r) in model_origin.items() if r == 'EU']
    non_eu_models = [m for m, (_, r) in model_origin.items() if r != 'EU']
    
    eu_langs = ['fr', 'de', 'es', 'it', 'pt']
    
    eu_on_eu = results_df[(results_df['model'].isin(eu_models)) & 
                          (results_df['language'].isin(eu_langs))]
    non_eu_on_eu = results_df[(results_df['model'].isin(non_eu_models)) & 
                              (results_df['language'].isin(eu_langs))]
    
    if len(eu_on_eu) > 0 and len(non_eu_on_eu) > 0:
        eu_mean = eu_on_eu['cultural_distance'].mean()
        non_eu_mean = non_eu_on_eu['cultural_distance'].mean()
        
        print(f"欧洲模型在欧洲语言上的平均距离: {eu_mean:.3f}")
        print(f"非欧洲模型在欧洲语言上的平均距离: {non_eu_mean:.3f}")
        print(f"差异: {non_eu_mean - eu_mean:+.3f}")
        
        # t检验
        t_stat, p_value = stats.ttest_ind(eu_on_eu['cultural_distance'], 
                                          non_eu_on_eu['cultural_distance'])
        print(f"独立样本t检验: t={t_stat:.2f}, p={p_value:.4f}")
        if p_value < 0.05:
            if eu_mean < non_eu_mean:
                print("→ 欧洲模型在欧洲语言上显著更好 *")
            else:
                print("→ 非欧洲模型在欧洲语言上显著更好 *")
        else:
            print("→ 无显著差异")
    
    # 6. 综合本土优势效应量
    print("\n--- 6. 综合本土优势效应量 ---")
    
    if home_advantage:
        all_home = []
        all_away = []
        for item in home_advantage:
            all_home.append(item['home_distance'])
            all_away.append(item['away_distance'])
        
        home_mean = np.mean(all_home)
        away_mean = np.mean(all_away)
        pooled_std = np.sqrt((np.std(all_home)**2 + np.std(all_away)**2) / 2)
        cohens_d = (away_mean - home_mean) / pooled_std if pooled_std > 0 else 0
        
        print(f"本土语言平均距离: {home_mean:.4f}")
        print(f"非本土语言平均距离: {away_mean:.4f}")
        print(f"Cohen's d (本土优势): {cohens_d:.4f}")
        
        if abs(cohens_d) < 0.2:
            print("→ 本土优势效应量极小")
        elif abs(cohens_d) < 0.5:
            print("→ 本土优势效应量小")
        elif abs(cohens_d) < 0.8:
            print("→ 本土优势效应量中等")
        else:
            print("→ 本土优势效应量大")
    
    # 7. 开源模型 vs 闭源模型对比分析
    analyze_open_vs_closed_source(results_df, model_origin)


def analyze_open_vs_closed_source(results_df, model_origin):
    """分析开源模型 vs 闭源模型的表现差异"""
    print("\n" + "="*60)
    print("🔓 开源模型 vs 闭源模型对比分析")
    print("="*60)
    
    from scipy import stats
    
    # 开源/闭源模型分类
    open_source_models = [
        'llama-3.2-3b-instruct',
        'llama-3.3-70b-instruct',
        'mistral-nemo',
        'phi-3-mini-128k-instruct',
        'gemma-3-4b-it',
        'deepseek-chat',
        'deepseek-chat-v3.1',
        'qwen3-max',
        'qwen3-1.7b',
    ]
    
    closed_source_models = [
        'gpt-4o',
        'gpt-4o-mini',
        'gpt-5.1',
        'claude-3-7-sonnet-20250219',
        'claude-sonnet-4.5',
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-3-pro-preview',
        'mistral-medium-3.1',
        'doubao-1-5-pro-32k-250115',
        'kimi-k2',
        'grok-4.1-fast',
    ]
    
    # 排除英语母语国家
    non_english = results_df[~results_df['is_english_native_country']].copy()
    
    # 1. 整体表现对比
    print("\n--- 1. 整体表现对比 ---")
    
    open_data = non_english[non_english['model'].isin(open_source_models)]
    closed_data = non_english[non_english['model'].isin(closed_source_models)]
    
    open_models_found = open_data['model'].unique().tolist()
    closed_models_found = closed_data['model'].unique().tolist()
    
    print(f"\n开源模型 ({len(open_models_found)}个): {', '.join(sorted(open_models_found))}")
    print(f"闭源模型 ({len(closed_models_found)}个): {', '.join(sorted(closed_models_found))}")
    
    if len(open_data) > 0 and len(closed_data) > 0:
        open_mean = open_data['cultural_distance'].mean()
        closed_mean = closed_data['cultural_distance'].mean()
        open_std = open_data['cultural_distance'].std()
        closed_std = closed_data['cultural_distance'].std()
        
        print(f"\n开源模型平均文化距离: {open_mean:.3f} (std={open_std:.3f})")
        print(f"闭源模型平均文化距离: {closed_mean:.3f} (std={closed_std:.3f})")
        print(f"差异: {open_mean - closed_mean:+.3f}")
        
        # t检验
        t_stat, p_value = stats.ttest_ind(open_data['cultural_distance'], 
                                          closed_data['cultural_distance'])
        print(f"\n独立样本t检验: t={t_stat:.2f}, p={p_value:.6f}")
        
        # 效应量
        pooled_std = np.sqrt((open_std**2 + closed_std**2) / 2)
        cohens_d = (open_mean - closed_mean) / pooled_std if pooled_std > 0 else 0
        print(f"Cohen's d: {cohens_d:.3f}")
        
        if p_value < 0.05:
            if open_mean < closed_mean:
                print("→ 开源模型显著更好 *")
            else:
                print("→ 闭源模型显著更好 *")
        else:
            print("→ 无显著差异")
    
    # 2. 英语优势对比
    print("\n--- 2. 英语优势对比 ---")
    
    def calc_english_advantage_by_type(data, model_list, type_name):
        type_data = data[data['model'].isin(model_list)]
        if len(type_data) == 0:
            return None
        
        advantages = []
        for model in type_data['model'].unique():
            model_data = type_data[type_data['model'] == model]
            native_dist = model_data[model_data['is_using_native_language']]['cultural_distance'].mean()
            english_dist = model_data[model_data['is_english']]['cultural_distance'].mean()
            
            if pd.notna(native_dist) and pd.notna(english_dist) and native_dist > 0:
                adv = (native_dist - english_dist) / native_dist * 100
                advantages.append({
                    'model': model,
                    'native_dist': native_dist,
                    'english_dist': english_dist,
                    'english_advantage': adv
                })
        
        if advantages:
            adv_df = pd.DataFrame(advantages)
            print(f"\n{type_name}模型英语优势:")
            for _, row in adv_df.sort_values('english_advantage', ascending=False).iterrows():
                print(f"  {row['model']}: {row['english_advantage']:+.1f}% (母语={row['native_dist']:.2f}, 英语={row['english_dist']:.2f})")
            
            avg_adv = adv_df['english_advantage'].mean()
            print(f"  平均英语优势: {avg_adv:+.1f}%")
            return adv_df
        return None
    
    open_adv_df = calc_english_advantage_by_type(non_english, open_source_models, "开源")
    closed_adv_df = calc_english_advantage_by_type(non_english, closed_source_models, "闭源")
    
    if open_adv_df is not None and closed_adv_df is not None:
        open_avg = open_adv_df['english_advantage'].mean()
        closed_avg = closed_adv_df['english_advantage'].mean()
        print(f"\n对比: 开源={open_avg:+.1f}%, 闭源={closed_avg:+.1f}%, 差异={open_avg-closed_avg:+.1f}%")
        
        # t检验
        t_stat, p_value = stats.ttest_ind(open_adv_df['english_advantage'], 
                                          closed_adv_df['english_advantage'])
        print(f"独立样本t检验: t={t_stat:.2f}, p={p_value:.4f}")
    
    # 3. 按模型规模分层对比
    print("\n--- 3. 按模型规模分层对比 ---")
    
    # 模型规模估计（参数量，单位B）
    model_sizes = {
        'llama-3.2-3b-instruct': 3,
        'phi-3-mini-128k-instruct': 3.8,
        'gemma-3-4b-it': 4,
        'qwen3-1.7b': 1.7,
        'mistral-nemo': 12,
        'llama-3.3-70b-instruct': 70,
        'deepseek-chat': 67,
        'deepseek-chat-v3.1': 67,
        'qwen3-max': 72,
        'gpt-4o-mini': 8,
        'mistral-medium-3.1': 22,
        'gemini-2.5-flash': 50,
        'grok-4.1-fast': 50,
        'kimi-k2': 70,
        'claude-3-7-sonnet-20250219': 70,
        'claude-sonnet-4.5': 70,
        'gemini-2.5-pro': 100,
        'gemini-3-pro-preview': 100,
        'gpt-4o': 200,
        'gpt-5.1': 200,
    }
    
    # 小型(<10B), 中型(10-70B), 大型(>70B)
    size_categories = {
        '小型(<10B)': [],
        '中型(10-70B)': [],
        '大型(>70B)': []
    }
    
    for model, size in model_sizes.items():
        if size < 10:
            size_categories['小型(<10B)'].append(model)
        elif size <= 70:
            size_categories['中型(10-70B)'].append(model)
        else:
            size_categories['大型(>70B)'].append(model)
    
    print("\n模型规模分类:")
    for cat, models in size_categories.items():
        cat_data = non_english[non_english['model'].isin(models)]
        if len(cat_data) > 0:
            mean_dist = cat_data['cultural_distance'].mean()
            
            # 计算开源/闭源比例
            open_count = len([m for m in models if m in open_source_models])
            closed_count = len([m for m in models if m in closed_source_models])
            
            print(f"\n{cat} ({len(models)}个模型, 开源{open_count}/闭源{closed_count}):")
            print(f"  平均文化距离: {mean_dist:.3f}")
            print(f"  模型: {', '.join(models)}")
    
    # 4. 各语系表现对比
    print("\n--- 4. 各语系表现对比 ---")
    
    lang_families = {
        '闪米特语系': ['ar'],
        '斯拉夫语系': ['ru'],
        '汉藏语系': ['zh-cn', 'zh-tw', 'zh-hk'],
        '罗曼语系': ['es', 'fr', 'it', 'pt'],
        '日耳曼语系': ['de'],
    }
    
    print("\n语系          开源距离  闭源距离  差异")
    print("-" * 45)
    
    for family, langs in lang_families.items():
        open_family = open_data[open_data['language'].isin(langs)]
        closed_family = closed_data[closed_data['language'].isin(langs)]
        
        if len(open_family) > 0 and len(closed_family) > 0:
            open_dist = open_family['cultural_distance'].mean()
            closed_dist = closed_family['cultural_distance'].mean()
            diff = open_dist - closed_dist
            
            print(f"{family:<10} {open_dist:>8.2f}  {closed_dist:>8.2f}  {diff:>+6.2f}")
    
    # 5. 单个模型排名
    print("\n--- 5. 模型整体表现排名 ---")
    
    model_stats = []
    for model in non_english['model'].unique():
        if pd.isna(model) or model == 'unknown':
            continue
        model_data = non_english[non_english['model'] == model]
        mean_dist = model_data['cultural_distance'].mean()
        
        source_type = '开源' if model in open_source_models else ('闭源' if model in closed_source_models else '未知')
        size = model_sizes.get(model, 0)
        
        model_stats.append({
            'model': model,
            'source_type': source_type,
            'size': size,
            'mean_distance': mean_dist
        })
    
    stats_df = pd.DataFrame(model_stats).sort_values('mean_distance')
    
    print("\n排名  模型                          类型    规模(B)  平均距离")
    print("-" * 65)
    for i, (_, row) in enumerate(stats_df.iterrows(), 1):
        marker = "🟢" if row['source_type'] == '开源' else "🔵"
        size_str = f"{row['size']:.0f}" if row['size'] > 0 else "?"
        print(f"{i:>2}.  {row['model']:<28} {marker}{row['source_type']:<4} {size_str:>6}   {row['mean_distance']:.2f}")
    
    # 6. 统计汇总
    print("\n--- 6. 统计汇总 ---")
    
    open_stats = stats_df[stats_df['source_type'] == '开源']
    closed_stats = stats_df[stats_df['source_type'] == '闭源']
    
    if len(open_stats) > 0 and len(closed_stats) > 0:
        print(f"\n开源模型 ({len(open_stats)}个):")
        print(f"  平均距离: {open_stats['mean_distance'].mean():.2f} (标准差: {open_stats['mean_distance'].std():.2f})")
        print(f"  最佳: {open_stats.iloc[0]['model']} ({open_stats.iloc[0]['mean_distance']:.2f})")
        print(f"  最差: {open_stats.iloc[-1]['model']} ({open_stats.iloc[-1]['mean_distance']:.2f})")
        
        print(f"\n闭源模型 ({len(closed_stats)}个):")
        print(f"  平均距离: {closed_stats['mean_distance'].mean():.2f} (标准差: {closed_stats['mean_distance'].std():.2f})")
        print(f"  最佳: {closed_stats.iloc[0]['model']} ({closed_stats.iloc[0]['mean_distance']:.2f})")
        print(f"  最差: {closed_stats.iloc[-1]['model']} ({closed_stats.iloc[-1]['mean_distance']:.2f})")
        
        # 差异分析
        diff = open_stats['mean_distance'].mean() - closed_stats['mean_distance'].mean()
        print(f"\n差异分析:")
        print(f"  开源 vs 闭源平均距离差: {diff:+.2f}")
        if diff > 0:
            print(f"  结论: 闭源模型平均表现更好（距离更小）")
        else:
            print(f"  结论: 开源模型平均表现更好（距离更小）")


def main():
    """主函数"""
    print("="*60)
    print("🔍 Stage3 多语言文化距离分析")
    print("="*60)
    
    # 1. 分析数据结构
    stage0_data, stage3_data = analyze_data_structure()
    
    # 2. 计算文化距离
    results_df = calculate_cultural_distances(stage0_data, stage3_data)
    
    # 3. 分析结果
    if not results_df.empty:
        analyze_distance_results(results_df)
        
        # 保存结果
        output_path = PROJECT_ROOT / "results/roleplay_multilingual/cultural_distance_analysis.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n✅ 结果已保存: {output_path}")

if __name__ == "__main__":
    main()
