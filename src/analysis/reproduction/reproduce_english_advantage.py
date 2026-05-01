"""
英语优势分析复现脚本
========================
从原始数据开始，计算英语优势并与论文对比

数据流程:
1. 原始访谈数据: data/llm_interviews/multilingual/interview_raw/*.json
2. 处理后IVS格式: data/llm_interviews/multilingual/processed/*.pkl
3. PCA坐标: data/llm_pca/imitation/Table_S7_LLM_roleplay_PCA_coordinates.csv
4. IVS基准: data/country_values/country_scores_pca.json
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# 项目根目录 (src/analysis/reproduction/ → 项目根目录)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# ==================== 配置 ====================

# 排除的模型（保持与论文一致：21个模型，排除qwen3-1.7b）
EXCLUDED_MODELS = ['qwen3-1.7b']

# 英语母语国家（这些国家使用en-native；香港母语为zh-hk，不算英语母语）
EN_NATIVE_COUNTRIES = [
    'Australia', 'Canada', 'Ghana', 'Ireland', 'Kenya',
    'Malaysia', 'Malta', 'New Zealand', 'Nigeria', 'Pakistan',
    'Philippines', 'Puerto Rico', 'Rwanda', 'Singapore',
    'South Africa', 'Trinidad and Tobago', 'United Kingdom',
    'United States of America', 'Zambia', 'Zimbabwe'
]

# 46个非英语国家的母语映射（论文使用的语言映射）
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
    'Kazakhstan': 'ru', 'Russian Federation': 'ru', 'Brazil': 'pt', 'Macao': 'zh-hk'
}

# 论文中的英语优势结果（用于验证）
PAPER_RESULTS = {
    'Tunisia': 27.3, 'Jordan': 25.2, 'Palestine': 24.2, 'Lebanon': 20.9,
    'Taiwan, Province of China': 27.1, 'Hong Kong': 24.8, 'Haiti': 20.4,
    'Bolivia': 19.8, 'Morocco': 18.0, 'Kuwait': 17.7, 'Mali': 17.6,
    'Portugal': 17.6, 'Switzerland': -33.5, 'Germany': -26.1, 'Italy': -24.5,
    'Spain': -12.1, 'France': -13.3, 'China': 0.1, 'Japan': 3.3, 'Korea, Republic of': 3.0
}

PAPER_REGION_RESULTS = {
    'African-Islamic': 16.2,
    'Protestant Europe': -20.3,
    'Catholic Europe': -12.4,
    'Confucian': 3.6,
    'Latin America': 6.4,
    'Orthodox Europe': 4.2
}


# ==================== 数据加载函数 ====================

def load_pca_data():
    """加载PCA坐标数据"""
    pca_file = PROJECT_ROOT / 'data/llm_pca/imitation/Table_S7_LLM_roleplay_PCA_coordinates.csv'
    df = pd.read_csv(pca_file)
    
    # 排除指定模型
    df = df[df['model_name'].notna()]
    for model in EXCLUDED_MODELS:
        df = df[df['model_name'] != model]
    
    print(f"✅ 加载PCA数据: {len(df)} 行, {df['model_name'].nunique()} 个模型")
    return df


def load_ivs_data():
    """加载IVS基准数据"""
    ivs_file = PROJECT_ROOT / 'data/country_values/country_scores_pca.json'
    ivs_json = pd.read_json(ivs_file)
    ivs_json = ivs_json.drop_duplicates(subset=['Country'])
    
    # 创建字典便于查询
    ivs_coords = {}
    for _, row in ivs_json[ivs_json['data_source'] == 'IVS'].iterrows():
        ivs_coords[row['Country']] = {
            'PC1_rescaled': row['PC1_rescaled'],
            'PC2_rescaled': row['PC2_rescaled'],
            'Cultural Region': row['Cultural Region'],
            'Islamic': row.get('Islamic', False)
        }
    
    print(f"✅ 加载IVS数据: {len(ivs_coords)} 个国家")
    return ivs_coords


def get_english_language(country):
    """获取国家的英语类型"""
    if country in EN_NATIVE_COUNTRIES:
        return 'en-native'
    return 'en'


# ==================== 核心计算函数 ====================

def calculate_english_advantage(pca_df, ivs_coords):
    """
    计算英语优势
    
    方法：先对每个模型计算距离，然后平均，再计算优势
    advantage = (d_native - d_english) / d_native * 100%
    """
    results = []
    
    for country in pca_df['country'].unique():
        # 只分析有母语映射的国家
        if country not in NATIVE_LANG_MAP or country not in ivs_coords:
            continue
        
        native_lang = NATIVE_LANG_MAP[country]
        ivs_pc1 = ivs_coords[country]['PC1_rescaled']
        ivs_pc2 = ivs_coords[country]['PC2_rescaled']
        region = ivs_coords[country]['Cultural Region']
        
        # 获取英语和母语数据
        en_lang = get_english_language(country)
        en_rows = pca_df[(pca_df['country'] == country) & (pca_df['language'] == en_lang)]
        native_rows = pca_df[(pca_df['country'] == country) & (pca_df['language'] == native_lang)]
        
        if len(en_rows) == 0 or len(native_rows) == 0:
            continue
        
        # 逐模型计算距离
        en_distances = []
        native_distances = []
        
        for model in en_rows['model_name'].unique():
            en_model_data = en_rows[en_rows['model_name'] == model]
            native_model_data = native_rows[native_rows['model_name'] == model]
            
            if len(en_model_data) == 0 or len(native_model_data) == 0:
                continue
            
            # 取该模型该语言的平均坐标
            en_pc1 = en_model_data['PC1'].mean()
            en_pc2 = en_model_data['PC2'].mean()
            native_pc1 = native_model_data['PC1'].mean()
            native_pc2 = native_model_data['PC2'].mean()
            
            # 计算到IVS基准的欧氏距离
            d_en = np.sqrt((en_pc1 - ivs_pc1)**2 + (en_pc2 - ivs_pc2)**2)
            d_native = np.sqrt((native_pc1 - ivs_pc1)**2 + (native_pc2 - ivs_pc2)**2)
            
            en_distances.append(d_en)
            native_distances.append(d_native)
        
        # 计算平均距离
        if len(en_distances) > 0 and len(native_distances) > 0:
            avg_en = np.mean(en_distances)
            avg_native = np.mean(native_distances)
            
            # 计算英语优势
            if avg_native > 0:
                advantage = (avg_native - avg_en) / avg_native * 100
                
                results.append({
                    'country': country,
                    'native_language': native_lang,
                    'english_distance': avg_en,
                    'native_distance': avg_native,
                    'advantage': advantage,
                    'region': region
                })
    
    return pd.DataFrame(results)


def compare_with_paper(results_df):
    """与论文结果对比"""
    print("\n" + "="*80)
    print("与论文结果对比")
    print("="*80)
    
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
    
    return diffs


def calculate_regional_summary(results_df):
    """计算区域汇总"""
    print("\n" + "="*80)
    print("区域英语优势汇总")
    print("="*80)
    
    region_avg = results_df.groupby('region')['advantage'].mean()
    
    print(f"\n{'区域':<25} {'论文':>10} {'复现':>10} {'差异':>10}")
    print("-"*60)
    
    for region in PAPER_REGION_RESULTS.keys():
        if region in region_avg.index:
            paper_val = PAPER_REGION_RESULTS[region]
            repro_val = region_avg[region]
            diff = repro_val - paper_val
            print(f"{region:<25} {paper_val:>+9.1f}% {repro_val:>+9.1f}% {diff:>+9.1f}%")


# ==================== 主函数 ====================

def main():
    print("="*80)
    print("英语优势分析复现脚本")
    print("="*80)
    
    # 1. 加载数据
    print("\n【步骤1】加载数据...")
    pca_df = load_pca_data()
    ivs_coords = load_ivs_data()
    
    # 2. 计算英语优势
    print("\n【步骤2】计算英语优势...")
    results_df = calculate_english_advantage(pca_df, ivs_coords)
    print(f"✅ 计算完成: {len(results_df)} 个国家")
    
    # 3. 与论文对比
    print("\n【步骤3】与论文对比...")
    compare_with_paper(results_df)
    
    # 4. 区域汇总
    print("\n【步骤4】区域汇总...")
    calculate_regional_summary(results_df)
    
    # 5. 保存结果
    output_file = PROJECT_ROOT / 'results/metrics/english_advantage_reproduced.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_file, index=False)
    print(f"\n✅ 结果已保存到: {output_file}")
    
    return results_df


if __name__ == '__main__':
    results = main()
