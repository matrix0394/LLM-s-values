#!/usr/bin/env python3
"""
从头复现完整流程脚本
====================
从原始访谈数据 -> IVS格式 -> PCA投影 -> 英语优势 + 法语优势计算

完整流程:
1. 加载原始访谈数据 (data/roleplay_multilingual/llm_responses_roleplay_ml/*.json)
2. 转换为IVS格式 (10个IVS问题: A008, A165, E018, E025, F063, F118, F120, G006, Y002, Y003)
3. 使用固定PCA模型投影 (data/country_values/pca_model_fixed.pkl)
   - PPCA投影 + Varimax旋转 + Rescale
4. 计算英语优势 (与参考项目model_cultural_comp-main对比验证，0误差)
5. 计算法语优势 (12个阿拉伯语国家)

重要说明（与参考项目对比验证）:
- IVS问题列表: 完全一致
- Y002/Y003处理: 完全一致 (参考notebook 9-pca-llm.ipynb)
- PCA模型: 使用相同的pca_model_fixed.pkl (包含ppca_C, means, stds, rotation_matrix)
- Rescale参数: PC1=(1.81, 0.38), PC2=(1.61, -0.01) - 完全一致
- 距离计算: 先平均所有模型的距离，再计算优势 (正确方法)

关键发现:
- 原始Table_S7中的PC1/PC2列实际存储的是rescaled后的值
- 英语优势可0误差复现论文结果
- 法语优势为-6.8% (阿拉伯语优势)
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime

# 添加项目根目录到路径
project_root = Path("/Users/yxy/code/LLM's values/LLM's values")
sys.path.append(str(project_root))

from src.roleplay_multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
from src.roleplay_multilingual.multilingual_roleplay_pca_analysis import MultilingualRoleplayPCAAnalysis


# ==================== 配置 ====================

# 排除的模型（与论文一致：21模型，排除qwen3-1.7b）
EXCLUDED_MODELS = ['qwen3-1.7b']

# 12个阿拉伯语国家（法语优势分析用）
ARABIC_COUNTRIES_12 = [
    'Tunisia', 'Jordan', 'Palestine', 'Lebanon', 'Morocco', 'Kuwait',
    'Egypt', 'Iraq', 'Algeria', 'Qatar', 'Yemen', 'Bahrain'
]

# 英语母语国家（香港母语为zh-hk，不算英语母语）
EN_NATIVE_COUNTRIES = [
    'Australia', 'Canada', 'Ghana', 'Ireland', 'Kenya',
    'Malaysia', 'Malta', 'New Zealand', 'Nigeria', 'Pakistan',
    'Philippines', 'Puerto Rico', 'Rwanda', 'Singapore',
    'South Africa', 'Trinidad and Tobago', 'United Kingdom',
    'United States of America', 'Zambia', 'Zimbabwe'
]

# 46个非英语国家的母语映射
NATIVE_LANG_MAP = {
    'China': 'zh-cn', 'Taiwan, Province of China': 'zh-tw', 'Japan': 'ja', 
    'Korea, Republic of': 'ko', 'Germany': 'de', 'France': 'fr', 'Italy': 'it', 
    'Spain': 'es', 'Portugal': 'pt', 'Tunisia': 'ar', 'Jordan': 'ar', 'Palestine': 'ar', 
    'Lebanon': 'ar', 'Hong Kong': 'zh-hk', 'Haiti': 'fr', 'Bolivia': 'es', 'Morocco': 'ar', 
    'Kuwait': 'ar', 'Mali': 'fr', 'Switzerland': 'fr', 
    'Austria': 'de', 'Belgium': 'fr',
    'Luxembourg': 'fr', 'Russia': 'ru', 'Belarus': 'ru', 'Kyrgyzstan': 'ru',
    'Argentina': 'es', 'Chile': 'es', 'Colombia': 'es', 'Ecuador': 'es', 'Guatemala': 'es',
    'Mexico': 'es', 'Nicaragua': 'es', 'Peru': 'es', 'Uruguay': 'es', 'Venezuela': 'es',
    'Egypt': 'ar', 'Iraq': 'ar', 'Algeria': 'ar', 'Qatar': 'ar', 'Yemen': 'ar',
    'Kazakhstan': 'ru', 'Russian Federation': 'ru', 'Brazil': 'pt', 'Macao': 'zh-hk',
    'Bahrain': 'ar'
}

# 论文中的英语优势结果（用于验证）
PAPER_RESULTS = {
    'Tunisia': 27.3, 'Jordan': 25.2, 'Palestine': 24.2, 'Lebanon': 20.9,
    'Taiwan, Province of China': 27.1, 'Hong Kong': 24.8, 'Haiti': 20.4,
    'Bolivia': 19.8, 'Morocco': 18.0, 'Kuwait': 17.7, 'Mali': 17.6,
    'Portugal': 17.6, 'Switzerland': -33.5, 'Germany': -26.1, 'Italy': -24.5,
    'Spain': -12.1, 'France': -13.3, 'China': 0.1, 'Japan': 3.3, 'Korea, Republic of': 3.0
}


# ==================== 步骤1: 加载原始访谈数据 ====================

def step1_load_raw_interview_data():
    """步骤1: 加载原始访谈数据"""
    print("\n" + "="*80)
    print("步骤1: 加载原始访谈数据")
    print("="*80)
    
    raw_dir = project_root / 'data' / 'llm_values' / 'interview_raw'
    
    # 统计文件
    all_files = list(raw_dir.glob('*.json'))
    print(f"找到 {len(all_files)} 个原始访谈文件")
    
    # 统计语言分布
    languages = {}
    models = {}
    countries = {}
    
    for f in all_files:
        # 解析文件名: model_language_timestamp.json
        name = f.stem
        parts = name.split('_')
        
        # 尝试解析模型名（可能包含多个下划线）
        # 格式: anthropic_claude-sonnet-4.5_ar_20251227_215834
        if len(parts) >= 3:
            # 找到语言代码位置（通常是倒数第二个或第三个）
            for i, p in enumerate(parts):
                if p in ['en', 'ar', 'zh-cn', 'zh-tw', 'fr', 'es', 'ru', 'ja', 'ko', 'pt', 'de']:
                    lang = p
                    # 模型名是到语言之前的部分
                    model = '_'.join(parts[:i])
                    break
            else:
                lang = parts[-3] if len(parts) >= 3 else 'unknown'
                model = '_'.join(parts[:-2])
        else:
            lang = 'unknown'
            model = name
        
        languages[lang] = languages.get(lang, 0) + 1
        models[model] = models.get(model, 0) + 1
    
    print(f"\n语言分布: {dict(sorted(languages.items()))}")
    print(f"模型数量: {len(models)}")
    print(f"模型列表: {list(models.keys())}")
    
    return all_files


# ==================== 步骤2: 转换为IVS格式 ====================

def step2_convert_to_ivs_format():
    """步骤2: 转换为IVS格式"""
    print("\n" + "="*80)
    print("步骤2: 转换为IVS格式")
    print("="*80)
    
    data_path = project_root / 'data'
    
    # 创建处理器
    processor = MultilingualRoleplayDataProcessor(data_path=str(data_path))
    
    # 处理数据 - 自动查找最新的原始数据文件
    print("处理多语言数据...")
    ivs_df = processor.process_multilingual_data_to_ivs_format()
    
    print(f"\n✅ IVS格式数据:")
    print(f"   - 行数: {len(ivs_df)}")
    print(f"   - 列: {ivs_df.columns.tolist()}")
    
    # 统计
    print(f"\n语言分布:")
    print(ivs_df['language'].value_counts())
    
    # 保存
    output_path = project_root / 'data' / 'roleplay_multilingual' / 'llm_roleplay_ml_processed_ivs_format_reproduced.pkl'
    ivs_df.to_pickle(output_path)
    print(f"\n💾 保存到: {output_path}")
    
    return ivs_df


# ==================== 步骤3: PCA投影 ====================

def step3_pca_projection(ivs_df):
    """步骤3: 使用固定PCA模型投影"""
    print("\n" + "="*80)
    print("步骤3: PCA投影 (使用固定PCA模型)")
    print("="*80)
    
    # 加载PCA模型
    pca_model_path = project_root / 'data' / 'country_values' / 'pca_model_fixed.pkl'
    print(f"加载PCA模型: {pca_model_path}")
    with open(pca_model_path, 'rb') as f:
        pca_model = pickle.load(f)
    print("✅ PCA模型加载成功")
    
    # IVS问题列表
    iv_qns = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
    
    # 准备LLM多语言数据 - 只处理多语言数据
    multilingual_data = ivs_df.copy()
    multilingual_data['data_source'] = 'Multilingual'
    
    # 确保必要的列存在
    if 'model_name' not in multilingual_data.columns:
        if 'model' in multilingual_data.columns:
            multilingual_data['model_name'] = multilingual_data['model']
    
    # 确保country列存在
    if 'country' not in multilingual_data.columns:
        if 'Country' in multilingual_data.columns:
            multilingual_data['country'] = multilingual_data['Country']
    
    print(f"LLM多语言数据行数: {len(multilingual_data)}")
    
    # 执行PCA转换（使用固定模型）
    print("使用固定PCA模型转换...")
    data_for_pca = multilingual_data[iv_qns].to_numpy()
    
    # 标准化
    data_standardized = (data_for_pca - pca_model['ppca_means']) / pca_model['ppca_stds']
    data_standardized = np.nan_to_num(data_standardized, nan=0.0)
    
    # PPCA投影
    principal_components = np.dot(data_standardized, pca_model['ppca_C'])
    
    # Varimax旋转
    rotated_components = np.dot(principal_components, pca_model['rotation_matrix'])
    
    # 创建结果
    pca_results = pd.DataFrame(rotated_components, columns=["PC1", "PC2"])
    
    # 重缩放
    pca_results['PC1_rescaled'] = (
        pca_model['pc_rescale_params']['PC1'][0] * pca_results['PC1'] + 
        pca_model['pc_rescale_params']['PC1'][1]
    )
    pca_results['PC2_rescaled'] = (
        pca_model['pc_rescale_params']['PC2'][0] * pca_results['PC2'] + 
        pca_model['pc_rescale_params']['PC2'][1]
    )
    
    # 合并结果
    result_df = pd.concat([
        multilingual_data[['model_name', 'Country', 'country_code', 'language', 'data_source']].reset_index(drop=True),
        pca_results.reset_index(drop=True)
    ], axis=1)
    
    # 重命名Country为country
    result_df = result_df.rename(columns={'Country': 'country'})
    
    print(f"\n✅ PCA投影完成:")
    print(f"   - LLM数据行数: {len(result_df)}")
    print(f"   - 国家数: {result_df['country'].nunique()}")
    print(f"   - 语言数: {result_df['language'].nunique()}")
    
    # 排除模型
    for model in EXCLUDED_MODELS:
        result_df = result_df[result_df['model_name'] != model]
    print(f"   - 排除模型后: {result_df['model_name'].nunique()} 个模型")
    
    # 保存
    output_path = project_root / 'SI' / 'pca' / 'Table_S7_LLM_roleplay_PCA_coordinates_reproduced.csv'
    result_df.to_csv(output_path, index=False)
    print(f"\n💾 保存到: {output_path}")
    
    return result_df


# ==================== 步骤4: 计算英语优势 ====================

def step4_calculate_english_advantage(pca_df):
    """步骤4: 计算英语优势"""
    print("\n" + "="*80)
    print("步骤4: 计算英语优势")
    print("="*80)
    
    # 加载IVS基准
    ivs_file = project_root / 'data' / 'country_values' / 'country_scores_pca.json'
    ivs_json = pd.read_json(ivs_file)
    ivs_json = ivs_json.drop_duplicates(subset=['Country'])
    
    ivs_coords = {}
    for _, row in ivs_json[ivs_json['data_source'] == 'IVS'].iterrows():
        ivs_coords[row['Country']] = {
            'PC1_rescaled': row['PC1_rescaled'],
            'PC2_rescaled': row['PC2_rescaled'],
            'Cultural Region': row['Cultural Region']
        }
    
    print(f"IVS基准国家数: {len(ivs_coords)}")
    
    # 计算英语优势 - 使用PC1_rescaled和PC2_rescaled！
    results = []
    
    for country in pca_df['country'].unique():
        if country not in NATIVE_LANG_MAP or country not in ivs_coords:
            continue
        
        native_lang = NATIVE_LANG_MAP[country]
        ivs_pc1 = ivs_coords[country]['PC1_rescaled']
        ivs_pc2 = ivs_coords[country]['PC2_rescaled']
        
        # 英语类型
        en_lang = 'en-native' if country in EN_NATIVE_COUNTRIES else 'en'
        
        # 获取数据
        en_rows = pca_df[(pca_df['country'] == country) & (pca_df['language'] == en_lang)]
        native_rows = pca_df[(pca_df['country'] == country) & (pca_df['language'] == native_lang)]
        
        if len(en_rows) == 0 or len(native_rows) == 0:
            continue
        
        # 逐模型计算距离
        en_distances = []
        native_distances = []
        
        for model in en_rows['model_name'].unique():
            en_model = en_rows[en_rows['model_name'] == model]
            native_model = native_rows[native_rows['model_name'] == model]
            
            if len(en_model) == 0 or len(native_model) == 0:
                continue
            
            # 使用PC1_rescaled和PC2_rescaled！（关键！）
            en_pc1, en_pc2 = en_model['PC1_rescaled'].mean(), en_model['PC2_rescaled'].mean()
            native_pc1, native_pc2 = native_model['PC1_rescaled'].mean(), native_model['PC2_rescaled'].mean()
            
            d_en = np.sqrt((en_pc1 - ivs_pc1)**2 + (en_pc2 - ivs_pc2)**2)
            d_native = np.sqrt((native_pc1 - ivs_pc1)**2 + (native_pc2 - ivs_pc2)**2)
            
            en_distances.append(d_en)
            native_distances.append(d_native)
        
        if len(en_distances) > 0 and len(native_distances) > 0:
            avg_en = np.mean(en_distances)
            avg_native = np.mean(native_distances)
            
            if avg_native > 0:
                advantage = (avg_native - avg_en) / avg_native * 100
                results.append({
                    'country': country,
                    'native_language': native_lang,
                    'd_en': avg_en,
                    'd_native': avg_native,
                    'advantage': advantage
                })
    
    results_df = pd.DataFrame(results)
    
    # 与论文对比
    print("\n" + "="*60)
    print("与论文对比")
    print("="*60)
    
    print(f"\n{'国家':<30} {'论文':>10} {'复现':>10} {'差异':>10}")
    print("-"*65)
    
    diffs = []
    for country in PAPER_RESULTS.keys():
        paper_val = PAPER_RESULTS[country]
        repro_val = results_df[results_df['country'] == country]['advantage'].values
        
        if len(repro_val) > 0:
            repro_val = repro_val[0]
            diff = repro_val - paper_val
            diffs.append(diff)
            print(f"{country:<30} {paper_val:>+9.1f}% {repro_val:>+9.1f}% {diff:>+9.1f}%")
    
    print(f"\n平均差异: {np.mean(diffs):.2f}%")
    
    return results_df


# ==================== 步骤5: 计算法语优势 ====================

def step5_calculate_french_advantage(pca_df):
    """步骤5: 计算12个阿拉伯语国家的法语优势"""
    print("\n" + "="*80)
    print("步骤5: 计算法语优势 (12个阿拉伯语国家)")
    print("="*80)
    
    # 加载IVS基准
    ivs_file = project_root / 'data' / 'country_values' / 'country_scores_pca.json'
    ivs_json = pd.read_json(ivs_file)
    ivs_json = ivs_json.drop_duplicates(subset=['Country'])
    
    ivs_coords = {}
    for _, row in ivs_json[ivs_json['data_source'] == 'IVS'].iterrows():
        ivs_coords[row['Country']] = {
            'PC1_rescaled': row['PC1_rescaled'],
            'PC2_rescaled': row['PC2_rescaled'],
            'Cultural Region': row['Cultural Region']
        }
    
    print(f"IVS基准国家数: {len(ivs_coords)}")
    print(f"阿拉伯语国家: {ARABIC_COUNTRIES_12}")
    
    # 排除模型
    df = pca_df[~pca_df['model_name'].isin(EXCLUDED_MODELS)]
    df = df[df['country'].isin(ARABIC_COUNTRIES_12)]
    
    print(f"\n筛选后数据: {len(df)} 行")
    
    # 计算法语优势
    results = []
    
    for country in ARABIC_COUNTRIES_12:
        cdata = df[df['country'] == country]
        
        # 匹配IVS坐标
        country_match = country
        if country not in ivs_coords or country not in df['country'].values:
            for ivs_c in ivs_coords.keys():
                if ivs_c is None:
                    continue
                if country.lower() in ivs_c.lower():
                    country_match = ivs_c
                    break
        
        if country_match not in ivs_coords:
            print(f"⚠️ 找不到 {country} 的IVS坐标")
            continue
        
        ivs_pc1 = ivs_coords[country_match]['PC1_rescaled']
        ivs_pc2 = ivs_coords[country_match]['PC2_rescaled']
        
        fr_data = cdata[cdata['language'] == 'fr']
        ar_data = cdata[cdata['language'] == 'ar']
        
        if len(fr_data) == 0 or len(ar_data) == 0:
            print(f"⚠️ {country}: 缺少法语或阿拉伯语数据 (fr={len(fr_data)}, ar={len(ar_data)})")
            continue
        
        # 逐模型计算距离（收集所有距离后再平均）
        fr_distances = []
        ar_distances = []
        
        for model in fr_data['model_name'].unique():
            frm = fr_data[fr_data['model_name'] == model]
            arm = ar_data[ar_data['model_name'] == model]
            
            if len(frm) > 0 and len(arm) > 0:
                # 使用PC1_rescaled和PC2_rescaled！
                fr_pc1, fr_pc2 = frm['PC1_rescaled'].mean(), frm['PC2_rescaled'].mean()
                ar_pc1, ar_pc2 = arm['PC1_rescaled'].mean(), arm['PC2_rescaled'].mean()
                
                d_fr = np.sqrt((fr_pc1 - ivs_pc1)**2 + (fr_pc2 - ivs_pc2)**2)
                d_ar = np.sqrt((ar_pc1 - ivs_pc1)**2 + (ar_pc2 - ivs_pc2)**2)
                
                fr_distances.append(d_fr)
                ar_distances.append(d_ar)
        
        # 先平均距离，再计算优势（正确方法！）
        if len(fr_distances) > 0 and len(ar_distances) > 0:
            avg_fr = np.mean(fr_distances)
            avg_ar = np.mean(ar_distances)
            
            if avg_ar > 0:
                advantage = (avg_ar - avg_fr) / avg_ar * 100
                results.append({
                    'country': country,
                    'model': 'average',  # 标记为平均结果
                    'fr_distance': avg_fr,
                    'ar_distance': avg_ar,
                    'french_advantage': advantage
                })
                
                print(f"  {country}: 法语距离={avg_fr:.3f}, 阿拉伯语距离={avg_ar:.3f}, 法语优势={advantage:+.1f}%")
    
    results_df = pd.DataFrame(results)
    
    # 计算总体法语优势
    if len(results_df) > 0:
        country_avg = results_df.groupby('country')['french_advantage'].mean()
        overall_french_advantage = country_avg.mean()
        
        print("\n" + "="*60)
        print("法语优势结果 (12个阿拉伯语国家)")
        print("="*60)
        
        print(f"\n各国家法语优势:")
        for country in ARABIC_COUNTRIES_12:
            if country in country_avg.index:
                print(f"  {country}: {country_avg[country]:+.1f}%")
        
        print(f"\n总体法语优势: {overall_french_advantage:+.1f}%")
        print(f"正值表示法语比阿拉伯语更好（法语优势）")
        print(f"负值表示阿拉伯语比法语更好（阿拉伯语优势）")
    
    return results_df


# ==================== 主函数 ====================

def main():
    print("="*80)
    print("从头复现完整流程")
    print("原始访谈数据 -> IVS格式 -> PCA投影 -> 英语优势 + 法语优势")
    print("="*80)
    
    # 步骤1: 加载原始访谈数据
    all_files = step1_load_raw_interview_data()
    
    # 步骤2: 转换为IVS格式
    ivs_df = step2_convert_to_ivs_format()
    
    # 步骤3: PCA投影
    pca_df = step3_pca_projection(ivs_df)
    
    # 步骤4: 计算英语优势
    english_results = step4_calculate_english_advantage(pca_df)
    
    # 步骤5: 计算法语优势（12个阿拉伯语国家）
    french_results = step5_calculate_french_advantage(pca_df)
    
    print("\n" + "="*80)
    print("✅ 完整流程复现完成!")
    print("="*80)
    
    return english_results, french_results


if __name__ == '__main__':
    english_results, french_results = main()
