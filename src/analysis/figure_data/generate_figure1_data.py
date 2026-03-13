#!/usr/bin/env python3
"""
图1数据生成：45个国家英语角色扮演PC1/PC2 + WVS对照
用于画地图热力图
"""

import pandas as pd
import json
import os

PROJECT_ROOT = '/Users/yxy/code/LLM\'s values/LLM\'s values'

# 排除的模型
EXCLUDED_MODELS = ['qwen3-1.7b']


def load_llm_english_roleplay():
    """加载英语角色扮演PCA坐标（20模型均值）"""
    df = pd.read_csv(f'{PROJECT_ROOT}/SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv')
    
    # 排除低质量模型
    df = df[~df['model_name'].isin(EXCLUDED_MODELS)]
    
    # 只看英语
    df_en = df[df['language'] == 'en']
    
    # 按国家计算20个模型的均值
    country_means = df_en.groupby('country').agg({
        'PC1': 'mean',
        'PC2': 'mean'
    }).reset_index()
    
    country_means.columns = ['country', 'LLM_EN_PC1', 'LLM_EN_PC2']
    
    return country_means


def load_wvs_benchmarks():
    """加载WVS基准坐标"""
    with open(f'{PROJECT_ROOT}/data/country_values/country_scores_pca.json', 'r') as f:
        ivs_list = json.load(f)
    
    ivs = pd.DataFrame(ivs_list)
    ivs = ivs[ivs['data_source'] == 'IVS']
    ivs = ivs[['Country', 'PC1_rescaled', 'PC2_rescaled', 'Cultural Region', 'Islamic']]
    ivs.columns = ['country', 'WVS_PC1', 'WVS_PC2', 'cultural_region', 'is_islamic']
    
    return ivs


def main():
    print("="*70)
    print("图1数据：45个国家英语角色扮演 + WVS对照")
    print("="*70)
    
    # 加载数据
    llm_df = load_llm_english_roleplay()
    wvs_df = load_wvs_benchmarks()
    
    print(f"LLM英语角色扮演: {len(llm_df)} 个国家")
    print(f"WVS基准: {len(wvs_df)} 个国家")
    
    # 直接匹配（国家名称已经一致，不需要手动映射）
    merged = llm_df.merge(wvs_df, on='country', how='inner')
    print(f"直接匹配: {len(merged)} 个国家")
    
    # 选择需要的列
    merged_45 = merged[['country', 'LLM_EN_PC1', 'LLM_EN_PC2', 'WVS_PC1', 'WVS_PC2', 'cultural_region', 'is_islamic']]
    
    # 按文化区域排序
    merged_45 = merged_45.sort_values(['cultural_region', 'country'])
    
    print(f"最终数据: {len(merged_45)} 个国家")
    print(f"\n文化区域分布:")
    print(merged_45['cultural_region'].value_counts())
    
    # 保存
    output_dir = f'{PROJECT_ROOT}/results/figures'
    os.makedirs(output_dir, exist_ok=True)
    
    merged_45.to_csv(f'{output_dir}/figure1_data_45countries.csv', index=False)
    print(f"\n已保存到: {output_dir}/figure1_data_45countries.csv")
    
    # 打印数据预览
    print("\n数据预览:")
    print(merged_45.to_string(index=False))


if __name__ == '__main__':
    main()
