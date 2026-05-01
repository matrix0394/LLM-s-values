"""
完整的Stage3分析 - 包含所有10个问题和文化坐标距离
"""

import sys
import io
from pathlib import Path

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(str(Path(__file__).parent.parent.parent))

import pickle
import pandas as pd
import numpy as np
from collections import defaultdict
import math

# 注意：不再硬编码国家列表，而是从PCA数据中动态获取


def load_stage3_pca_data():
    """加载Stage3已计算的PCA坐标数据"""
    pca_file = Path("data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl")
    
    if not pca_file.exists():
        print(f"[ERROR] PCA data file not found: {pca_file}")
        return None
    
    pca_df = pickle.load(open(pca_file, 'rb'))
    print(f"Loaded PCA data: {len(pca_df)} records")
    
    # 筛选出Multilingual数据（模型角色扮演数据）
    model_data = pca_df[pca_df['data_source'] == 'Multilingual'].copy()
    print(f"Multilingual model data: {len(model_data)} records")
    
    # 筛选出IVS真实数据
    real_data = pca_df[pca_df['data_source'] == 'IVS'].copy()
    print(f"Real IVS data: {len(real_data)} records")
    
    return model_data, real_data


def calculate_cultural_distance(model_coords, real_coords):
    """计算文化坐标的欧几里得距离"""
    if model_coords is None or real_coords is None:
        return None
    
    pc1_diff = model_coords[0] - real_coords[0]
    pc2_diff = model_coords[1] - real_coords[1]
    
    distance = math.sqrt(pc1_diff**2 + pc2_diff**2)
    return distance

def analyze_with_pca_coords(model_name, country, language, model_coords, real_coords):
    """使用Stage3计算的PCA坐标进行分析"""
    print(f"\n{'='*80}")
    print(f"Analysis: {model_name} -> {country} ({language})")
    print(f"{'='*80}")
    
    # 计算文化坐标距离
    coord_distance = calculate_cultural_distance(model_coords, real_coords)
    
    print(f"\nCultural Coordinates (from Stage3 PCA):")
    print(f"{'-'*80}")
    if model_coords:
        print(f"Model coordinates:")
        print(f"  PC1 (Survival-Expression): {model_coords[0]:.2f}")
        print(f"  PC2 (Traditional-Secular): {model_coords[1]:.2f}")
    
    if real_coords:
        print(f"\nReal coordinates:")
        print(f"  PC1 (Survival-Expression): {real_coords[0]:.2f}")
        print(f"  PC2 (Traditional-Secular): {real_coords[1]:.2f}")
    
    if coord_distance is not None:
        print(f"\nEuclidean distance: {coord_distance:.2f}")
        
        if coord_distance <= 1.0:
            print(f"  ✅ [EXCELLENT] Very close on cultural map")
        elif coord_distance <= 2.0:
            print(f"  ⚠️  [GOOD] Moderate distance on cultural map")
        else:
            print(f"  ❌ [POOR] Far from real position on cultural map")
    
    return {
        'coord_distance': coord_distance,
        'model_coords': model_coords,
        'real_coords': real_coords
    }

def main():
    """主函数 - 分析Stage3计算的文化坐标数据"""
    print("\n" + "="*80)
    print("Stage3 Cultural Coordinates Analysis")
    print("="*80)
    print("\n📊 数据来源: Stage3 PCA计算结果")
    print("  文件: roleplay_ml_pca_entity_scores_latest.pkl")
    print("  - 真实国家坐标 (IVS数据)")
    print("  - 模型模仿坐标 (Multilingual角色扮演数据)")
    print("\n✅ 数据质量:")
    print("  每个模型-国家-语言组合进行了5轮访谈")
    print("  PCA坐标基于5轮访谈的共识结果（consensus）")
    print("  提高了结果的稳定性和可靠性")
    print("="*80)
    
    # 加载Stage3 PCA数据
    print("\nLoading Stage3 PCA data...")
    result = load_stage3_pca_data()
    if result is None:
        print("[ERROR] Failed to load PCA data")
        return
    
    model_data, real_data = result
    print(f"✅ 模型数据: {len(model_data)} 条记录")
    print(f"✅ 真实国家数据: {len(real_data)} 条记录")
    
    # 获取所有被测试的国家（从模型数据中）
    tested_countries = sorted(model_data['country_code'].unique())
    print(f"\n📍 测试的国家数量: {len(tested_countries)}")
    print(f"   国家列表: {', '.join(tested_countries[:10])}{'...' if len(tested_countries) > 10 else ''}")
    
    # 提取真实国家坐标（为所有被测试的国家建立映射）
    print("\nExtracting real country coordinates...")
    real_country_coords = {}
    countries_without_ivs = []
    
    for country_name in tested_countries:
        country_real = real_data[real_data['country_code'] == country_name]
        if len(country_real) > 0:
            pc1 = country_real.iloc[0]['PC1_rescaled']
            pc2 = country_real.iloc[0]['PC2_rescaled']
            real_country_coords[country_name] = (pc1, pc2)
        else:
            countries_without_ivs.append(country_name)
    
    print(f"✅ 找到真实坐标的国家: {len(real_country_coords)}")
    if countries_without_ivs:
        print(f"⚠️  没有IVS数据的国家 ({len(countries_without_ivs)}): {', '.join(countries_without_ivs[:5])}{'...' if len(countries_without_ivs) > 5 else ''}")
    
    # 分析每个模型-国家-语言组合
    print("\n" + "="*80)
    print("Analyzing Model Performance by Country and Language")
    print("="*80)
    print("(详细输出已省略，仅显示汇总结果)\n")
    
    all_results = defaultdict(list)
    country_results = defaultdict(lambda: defaultdict(list))  # country -> model -> distances
    
    # 遍历所有有真实坐标的国家
    for country_name in real_country_coords.keys():
        real_coords = real_country_coords[country_name]
        
        # 获取该国家的所有模型数据
        country_models = model_data[model_data['country_code'] == country_name]
        
        for _, row in country_models.iterrows():
            model_name = row['model_name']
            language = row.get('language', 'unknown')
            model_coords = (row['PC1_rescaled'], row['PC2_rescaled'])
            
            # 计算距离（不打印详细信息）
            coord_distance = calculate_cultural_distance(model_coords, real_coords)
            
            if coord_distance is not None:
                result = {
                    'coord_distance': coord_distance,
                    'model_coords': model_coords,
                    'real_coords': real_coords,
                    'country': country_name,
                    'language': language
                }
                all_results[model_name].append(result)
                country_results[country_name][model_name].append(coord_distance)
    
    print(f"✅ 分析完成: {sum(len(v) for v in all_results.values())} 个模型-国家-语言组合")
    
    # 总结排名
    print(f"\n{'='*80}")
    print(f"Overall Model Ranking by Average Cultural Distance")
    print(f"{'='*80}")
    
    model_scores = {}
    for model, results in all_results.items():
        distances = [r['coord_distance'] for r in results]
        if distances:
            avg_distance = np.mean(distances)
            std_distance = np.std(distances)
            min_distance = np.min(distances)
            max_distance = np.max(distances)
            
            # 计算优秀/良好/差的比例
            excellent = sum(1 for d in distances if d <= 1.0)
            good = sum(1 for d in distances if 1.0 < d <= 2.0)
            poor = sum(1 for d in distances if d > 2.0)
            
            model_scores[model] = {
                'avg_distance': avg_distance,
                'std_distance': std_distance,
                'min_distance': min_distance,
                'max_distance': max_distance,
                'count': len(distances),
                'excellent': excellent,
                'good': good,
                'poor': poor
            }
    
    sorted_models = sorted(model_scores.items(), key=lambda x: x[1]['avg_distance'])
    
    for i, (model, stats) in enumerate(sorted_models, 1):
        avg_dist = stats['avg_distance']
        std_dist = stats['std_distance']
        count = stats['count']
        excellent = stats['excellent']
        good = stats['good']
        poor = stats['poor']
        
        if avg_dist <= 1.0:
            status = "✅ Excellent"
        elif avg_dist <= 2.0:
            status = "⚠️  Good"
        else:
            status = "❌ Poor"
        
        print(f"\n[{i}] {model}")
        print(f"    平均距离: {avg_dist:.2f} ± {std_dist:.2f} | 样本数: {count} | {status}")
        print(f"    表现分布: ✅{excellent} ({excellent/count*100:.1f}%) | ⚠️{good} ({good/count*100:.1f}%) | ❌{poor} ({poor/count*100:.1f}%)")
        print(f"    距离范围: [{stats['min_distance']:.2f}, {stats['max_distance']:.2f}]")
    
    # 按国家分析
    print(f"\n{'='*80}")
    print(f"Top 10 Countries by Model Performance (Lowest Average Distance)")
    print(f"{'='*80}")
    
    country_avg_distances = {}
    for country, models_dict in country_results.items():
        all_distances = []
        for distances in models_dict.values():
            all_distances.extend(distances)
        if all_distances:
            country_avg_distances[country] = np.mean(all_distances)
    
    sorted_countries = sorted(country_avg_distances.items(), key=lambda x: x[1])[:10]
    
    for i, (country, avg_dist) in enumerate(sorted_countries, 1):
        print(f"[{i}] {country}: {avg_dist:.2f}")
    
    print(f"\n{'='*80}")
    print(f"Bottom 10 Countries by Model Performance (Highest Average Distance)")
    print(f"{'='*80}")
    
    sorted_countries_worst = sorted(country_avg_distances.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for i, (country, avg_dist) in enumerate(sorted_countries_worst, 1):
        print(f"[{i}] {country}: {avg_dist:.2f}")
    
    print("\n" + "="*80)
    print("Analysis Complete")
    print("="*80)

if __name__ == "__main__":
    main()
