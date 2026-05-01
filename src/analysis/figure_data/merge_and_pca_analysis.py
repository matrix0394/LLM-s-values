#!/usr/bin/env python3
"""
法语优势分析 - 完整版 + 验证
1. 合并原始访谈答案（法语 + 阿拉伯语 + 英语）
2. 统一计算PCA坐标
3. 计算英语优势和法语优势
4. 验证结果是否与论文一致
"""

import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
import glob
import sys

# 设置路径
PROJECT_ROOT = Path('/Users/yxy/code/LLM\'s values/LLM\'s values')
sys.path.insert(0, str(PROJECT_ROOT))

# 排除的低质量模型
EXCLUDED_MODELS = ['qwen3-1.7b']

# IVS问题列表
IV_QNS = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']

# 英语母语国家列表（香港母语为zh-hk，不算英语母语国家）
EN_NATIVE_COUNTRIES = [
    'Australia', 'Canada', 'Ghana', 'Ireland', 'Kenya',
    'Malaysia', 'Malta', 'New Zealand', 'Nigeria', 'Pakistan',
    'Philippines', 'Puerto Rico', 'Rwanda', 'Singapore',
    'South Africa', 'Trinidad and Tobago', 'United Kingdom',
    'United States of America', 'Zambia', 'Zimbabwe'
]

# 12个阿拉伯语国家（法语优势分析用）
ARABIC_COUNTRIES_12 = ['Algeria', 'Egypt', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
                       'Libya', 'Morocco', 'Palestine', 'Qatar', 'Tunisia', 'Yemen']

# 阿拉伯语国家
ARABIC_COUNTRIES = ['Algeria', 'Egypt', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
                    'Libya', 'Morocco', 'Palestine', 'Qatar', 'Tunisia', 'Yemen']


def load_pca_model():
    """加载固定PCA模型"""
    with open(PROJECT_ROOT / 'data/country_values/pca_model_fixed.pkl', 'rb') as f:
        return pickle.load(f)


def transform_with_fixed_pca(data, pca_model, iv_qns):
    """使用固定PCA模型转换数据"""
    ppca_C = pca_model['ppca_C']
    ppca_means = pca_model['ppca_means']
    ppca_stds = pca_model['ppca_stds']
    rotation_matrix = pca_model['rotation_matrix']
    pc_rescale_params = pca_model['pc_rescale_params']
    
    data_for_pca = data[iv_qns].to_numpy()
    data_standardized = (data_for_pca - ppca_means) / ppca_stds
    data_standardized = np.nan_to_num(data_standardized, nan=0.0)
    
    principal_components = np.dot(data_standardized, ppca_C)
    rotated_components = np.dot(principal_components, rotation_matrix)
    
    pc1 = pc_rescale_params['PC1'][0] * rotated_components[:, 0] + pc_rescale_params['PC1'][1]
    pc2 = pc_rescale_params['PC2'][0] * rotated_components[:, 1] + pc_rescale_params['PC2'][1]
    
    return pc1, pc2


def load_all_interview_data():
    """加载所有访谈数据（法语 + 阿拉伯语 + 英语）"""
    print("加载所有访谈数据...")
    
    data_dir = PROJECT_ROOT / 'data/roleplay_multilingual/llm_responses_roleplay_ml'
    
    # 1. 加载法语数据
    json_files = list(data_dir.glob("*_fr_*.json"))
    processed = {}
    for f in json_files:
        parts = f.stem.split('_')
        fr_idx = -1
        for i, p in enumerate(parts):
            if p == 'fr':
                fr_idx = i
                break
        if fr_idx < 2:
            continue
        model = '_'.join(parts[:fr_idx-1])
        country = parts[fr_idx-1]
        key = (model, country, 'fr')
        if key not in processed:
            processed[key] = f
    
    all_data = []
    for (model, country, lang), filepath in processed.items():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            row = {'country': country, 'model_name': model, 'language': lang}
            for q in IV_QNS:
                row[q] = np.nan
            
            for resp in data.get('responses', []):
                qid = resp.get('question_id')
                if qid in IV_QNS:
                    try:
                        row[qid] = float(resp.get('final_response', np.nan))
                    except:
                        row[qid] = np.nan
            
            all_data.append(row)
        except:
            pass
    
    french_df = pd.DataFrame(all_data)
    print(f"   法语: {len(french_df)} 条")
    
    # 2. 加载现有数据（阿拉伯语 + 英语）
    pkl_file = PROJECT_ROOT / 'data/roleplay_multilingual/llm_roleplay_ml_processed_responses_ivs_format_latest.pkl'
    with open(pkl_file, 'rb') as f:
        data = pickle.load(f)
    
    # 过滤掉法语（因为已经加载了）
    df = data[data['language'] != 'fr'].copy()
    df = df.reset_index(drop=True)
    if 'country' in df.columns:
        df = df.drop(columns=['country'])
    df = df.rename(columns={'Country': 'country'})
    
    cols = ['country', 'model_name', 'language'] + IV_QNS
    existing_df = df[cols]
    print(f"   阿拉伯语+英语: {len(existing_df)} 条")
    
    # 3. 合并
    combined = pd.concat([french_df, existing_df], axis=0, ignore_index=True)
    print(f"   总计: {len(combined)} 条")
    print(f"   语言分布: {combined['language'].value_counts().to_dict()}")
    
    return combined


def load_ivs_coordinates():
    """加载IVS真实坐标"""
    with open(PROJECT_ROOT / 'data/country_values/country_scores_pca.json', encoding='utf-8') as f:
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
    return coords


def calculate_english_advantage_all_countries(combined_df, ivs_coords):
    """计算所有非英语母语国家的英语优势"""
    
    # 排除低质量模型
    df = combined_df[~combined_df['model_name'].isin(EXCLUDED_MODELS)]
    
    # 只分析非英语母语国家
    df = df[~df['country'].isin(EN_NATIVE_COUNTRIES)]
    
    results = []
    
    # 获取所有有数据的国家
    all_countries = df['country'].unique()
    
    for country in all_countries:
        cdata = df[df['country'] == country]
        
        # 找IVS坐标
        country_match = country
        if country not in ivs_coords:
            for ivs_c in ivs_coords.keys():
                if country.lower() in ivs_c.lower():
                    country_match = ivs_c
                    break
        
        if country_match not in ivs_coords:
            continue
        
        real_pc1 = ivs_coords[country_match]['PC1']
        real_pc2 = ivs_coords[country_match]['PC2']
        cultural_region = ivs_coords[country_match].get('cultural_region', '')
        is_islamic = ivs_coords[country_match].get('is_islamic', False)
        
        # 获取该国家的所有非英语语言（官方语言）
        # 排除 en 和 en-native
        native_langs = cdata[~cdata['language'].isin(['en', 'en-native'])]['language'].unique()
        
        # 英语数据
        en_data = cdata[cdata['language'].isin(['en', 'en-native'])]
        
        if len(en_data) == 0:
            continue
        
        # 对每种官方语言计算
        for native_lang in native_langs:
            native_data = cdata[cdata['language'] == native_lang]
            
            if len(native_data) == 0:
                continue
            
            # 按模型配对
            for model in native_data['model_name'].unique():
                natm = native_data[native_data['model_name'] == model]
                enm = en_data[en_data['model_name'] == model]
                
                if len(natm) > 0 and len(enm) > 0:
                    nat_pc1, nat_pc2 = natm['PC1'].mean(), natm['PC2'].mean()
                    en_pc1, en_pc2 = enm['PC1'].mean(), enm['PC2'].mean()
                    
                    d_nat = np.sqrt((nat_pc1 - real_pc1)**2 + (nat_pc2 - real_pc2)**2)
                    d_en = np.sqrt((en_pc1 - real_pc1)**2 + (en_pc2 - real_pc2)**2)
                    
                    if d_nat > 0:
                        adv = (d_nat - d_en) / d_nat * 100
                        results.append({
                            'country': country,
                            'native_language': native_lang,
                            'model': model,
                            'native_distance': d_nat,
                            'en_distance': d_en,
                            'advantage': adv,
                            'cultural_region': cultural_region,
                            'is_islamic': is_islamic
                        })
    
    return pd.DataFrame(results)


def calculate_french_advantage_12_countries(combined_df, ivs_coords):
    """计算12个阿拉伯语国家的法语优势"""
    
    df = combined_df[~combined_df['model_name'].isin(EXCLUDED_MODELS)]
    df = df[df['country'].isin(ARABIC_COUNTRIES_12)]
    
    results = []
    
    for country in ARABIC_COUNTRIES_12:
        cdata = df[df['country'] == country]
        
        country_match = country
        if country not in ivs_coords:
            for ivs_c in ivs_coords.keys():
                if country.lower() in ivs_c.lower():
                    country_match = ivs_c
                    break
        
        if country_match not in ivs_coords:
            continue
        
        real_pc1 = ivs_coords[country_match]['PC1']
        real_pc2 = ivs_coords[country_match]['PC2']
        
        fr_data = cdata[cdata['language'] == 'fr']
        ar_data = cdata[cdata['language'] == 'ar']
        
        if len(fr_data) == 0 or len(ar_data) == 0:
            continue
        
        for model in fr_data['model_name'].unique():
            frm = fr_data[fr_data['model_name'] == model]
            arm = ar_data[ar_data['model_name'] == model]
            
            if len(frm) > 0 and len(arm) > 0:
                fr_pc1, fr_pc2 = frm['PC1'].mean(), frm['PC2'].mean()
                ar_pc1, ar_pc2 = arm['PC1'].mean(), arm['PC2'].mean()
                
                d_fr = np.sqrt((fr_pc1 - real_pc1)**2 + (fr_pc2 - real_pc2)**2)
                d_ar = np.sqrt((ar_pc1 - real_pc1)**2 + (ar_pc2 - real_pc2)**2)
                
                if d_ar > 0:
                    adv = (d_ar - d_fr) / d_ar * 100
                    results.append({
                        'country': country,
                        'model': model,
                        'fr_distance': d_fr,
                        'ar_distance': d_ar,
                        'advantage': adv
                    })
    
    return pd.DataFrame(results)


def validate_with_paper_results(english_results):
    """验证结果是否与论文一致"""
    
    print("\n" + "=" * 60)
    print("验证结果（与论文对比）")
    print("=" * 60)
    
    # 按文化区域计算
    region_stats = english_results.groupby('cultural_region').agg({
        'native_distance': 'mean',
        'en_distance': 'mean',
        'advantage': 'mean',
        'country': 'count'
    }).round(2)
    
    print("\n按文化区域统计:")
    print(region_stats.to_string())
    
    # 关键区域验证
    print("\n关键区域对比:")
    
    # 伊斯兰/阿拉伯
    islamic = english_results[english_results['cultural_region'].str.contains('Islamic', na=False)]
    if len(islamic) > 0:
        islamic_adv = (islamic['native_distance'].mean() - islamic['en_distance'].mean()) / islamic['native_distance'].mean() * 100
        print(f"   伊斯兰/阿拉伯: {islamic_adv:+.1f}% (论文预期: +17.0% ±2%)")
    
    # 天主教欧洲
    catholic = english_results[english_results['cultural_region'] == 'Catholic Europe']
    if len(catholic) > 0:
        catholic_adv = (catholic['native_distance'].mean() - catholic['en_distance'].mean()) / catholic['native_distance'].mean() * 100
        print(f"   天主教欧洲: {catholic_adv:+.1f}% (论文预期: -12.4% ±1%)")
    
    # 新教欧洲
    protestant = english_results[english_results['cultural_region'] == 'Protestant Europe']
    if len(protestant) > 0:
        protestant_adv = (protestant['native_distance'].mean() - protestant['en_distance'].mean()) / protestant['native_distance'].mean() * 100
        print(f"   新教欧洲: {protestant_adv:+.1f}% (论文预期: -20.3% ±1%)")
    
    # 总体
    overall_adv = (english_results['native_distance'].mean() - english_results['en_distance'].mean()) / english_results['native_distance'].mean() * 100
    print(f"   总体: {overall_adv:+.1f}% (论文预期: +5.9%)")
    
    return region_stats


def main():
    print("=" * 60)
    print("法语优势分析 + 论文验证")
    print("=" * 60)
    
    # 1. 加载所有数据
    combined = load_all_interview_data()
    
    # 2. 计算PCA
    print("\n计算PCA坐标...")
    pca_model = load_pca_model()
    pc1, pc2 = transform_with_fixed_pca(combined, pca_model, IV_QNS)
    combined['PC1'] = pc1
    combined['PC2'] = pc2
    
    # 3. 加载IVS坐标
    print("加载IVS坐标...")
    ivs_coords = load_ivs_coordinates()
    
    # 4. 计算英语优势（所有国家）
    print("\n计算英语优势（所有非英语母语国家）...")
    english_results = calculate_english_advantage_all_countries(combined, ivs_coords)
    print(f"   有效配对数: {len(english_results)}")
    
    # 5. 计算法语优势（12国）
    print("\n计算法语优势（12个阿拉伯语国家）...")
    french_results = calculate_french_advantage_12_countries(combined, ivs_coords)
    print(f"   有效配对数: {len(french_results)}")
    
    # 6. 验证
    region_stats = validate_with_paper_results(english_results)
    
    # 7. 法语优势摘要
    print("\n" + "=" * 60)
    print("法语优势摘要（12个阿拉伯语国家）")
    print("=" * 60)
    if len(french_results) > 0:
        fr_adv = (french_results['ar_distance'].mean() - french_results['fr_distance'].mean()) / french_results['ar_distance'].mean() * 100
        t_stat, p_val = stats.ttest_rel(french_results['ar_distance'], french_results['fr_distance'])
        print(f"   法语优势: {fr_adv:+.1f}% (p={p_val:.4f})")
    
    # 8. 保存结果
    output_dir = PROJECT_ROOT / 'results/analysis/french_advantage'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    combined.to_csv(output_dir / 'all_interview_with_pca.csv', index=False)
    english_results.to_csv(output_dir / 'english_advantage_all_countries.csv', index=False)
    french_results.to_csv(output_dir / 'french_advantage_12_countries.csv', index=False)
    region_stats.to_csv(output_dir / 'region_stats.csv')
    
    print(f"\n结果已保存到: {output_dir}")
    
    return combined, english_results, french_results


if __name__ == '__main__':
    combined, english_results, french_results = main()
