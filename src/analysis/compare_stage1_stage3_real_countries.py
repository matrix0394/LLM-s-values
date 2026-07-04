"""
对比Stage1和Stage3中真实国家PCA坐标的差异

Stage1: 基于原始IVS数据计算的真实国家坐标
Stage3: 在多语言角色扮演实验中重新计算的真实国家坐标
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
import matplotlib.pyplot as plt
import seaborn as sns

def normalize_country_name(name):
    """标准化国家名称"""
    if pd.isna(name):
        return None
    
    name = str(name).strip()
    
    # 处理数字代码（Stage1中的异常值）
    try:
        if float(name) == int(float(name)):
            return None
    except:
        pass
    
    # 标准化映射
    name_mapping = {
        'Bolivia (Plurinational State of)': 'Bolivia',
        'Iran (Islamic Republic of)': 'Iran',
        'Korea (the Republic of)': 'Korea, Republic of',
        'Moldova (the Republic of)': 'Moldova',
        'Netherlands (the)': 'Netherlands',
        'Palestine, State of': 'Palestine',
        'Philippines (the)': 'Philippines',
        'Russian Federation (the)': 'Russian Federation',
        'Taiwan (Province of China)': 'Taiwan, Province of China',
        'United Kingdom of Great Britain and Northern Ireland (the)': 'United Kingdom',
        'United States of America (the)': 'United States of America',
        'Venezuela (Bolivarian Republic of)': 'Venezuela',
    }
    
    # 应用映射
    if name in name_mapping:
        return name_mapping[name]
    
    return name

def load_stage1_coords():
    """加载Stage1的真实国家坐标"""
    # Stage1的PCA结果文件
    stage1_file = Path("data/country_values/pca_entity_scores.pkl")
    
    if not stage1_file.exists():
        print(f"[ERROR] Stage1 PCA文件不存在: {stage1_file}")
        return None
    
    try:
        import pickle5 as pickle
    except ImportError:
        import pickle
    
    try:
        with open(stage1_file, 'rb') as f:
            df = pickle.load(f, encoding='latin1')
    except Exception as e:
        try:
            # 尝试使用pandas读取
            df = pd.read_pickle(stage1_file)
        except Exception as e2:
            print(f"[ERROR] 加载Stage1数据失败: {e}, {e2}")
            print(f"[INFO] 尝试使用country_scores_pca.pkl...")
            # 尝试备用文件
            alt_file = Path("data/country_values/country_scores_pca.pkl")
            if alt_file.exists():
                try:
                    with open(alt_file, 'rb') as f:
                        df = pickle.load(f, encoding='latin1')
                except:
                    df = pd.read_pickle(alt_file)
            else:
                return None
    
    print(f"Stage1数据: {len(df)} 条记录")
    
    # 提取国家坐标（应用标准化）
    coords = {}
    for _, row in df.iterrows():
        country = row.get('Country') or row.get('country_code')
        normalized = normalize_country_name(country)
        if normalized:
            coords[normalized] = {
                'PC1': row['PC1_rescaled'],
                'PC2': row['PC2_rescaled']
            }
    
    print(f"Stage1国家数: {len(coords)}")
    return coords

def load_stage3_coords():
    """加载Stage3的真实国家坐标"""
    # Stage3的PCA结果文件
    stage3_file = Path("data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl")
    
    if not stage3_file.exists():
        print(f"[ERROR] Stage3 PCA文件不存在: {stage3_file}")
        return None
    
    try:
        df = pd.read_pickle(stage3_file)
    except Exception as e:
        print(f"[ERROR] 加载Stage3数据失败: {e}")
        return None
    
    # 只取IVS真实数据
    ivs_data = df[df['data_source'] == 'IVS'].copy()
    print(f"Stage3真实国家数据: {len(ivs_data)} 条记录")
    
    # 提取国家坐标（应用标准化）
    coords = {}
    for _, row in ivs_data.iterrows():
        country = row['country_code']
        normalized = normalize_country_name(country)
        if normalized:
            coords[normalized] = {
                'PC1': row['PC1_rescaled'],
                'PC2': row['PC2_rescaled']
            }
    
    print(f"Stage3国家数: {len(coords)}")
    return coords

def calculate_distance(coord1, coord2):
    """计算两个坐标之间的欧几里得距离"""
    pc1_diff = coord1['PC1'] - coord2['PC1']
    pc2_diff = coord1['PC2'] - coord2['PC2']
    return np.sqrt(pc1_diff**2 + pc2_diff**2)

def compare_coordinates(stage1_coords, stage3_coords):
    """对比两个阶段的坐标"""
    print("\n" + "="*80)
    print("坐标对比分析")
    print("="*80)
    
    # 找到共同的国家
    common_countries = set(stage1_coords.keys()) & set(stage3_coords.keys())
    stage1_only = set(stage1_coords.keys()) - set(stage3_coords.keys())
    stage3_only = set(stage3_coords.keys()) - set(stage1_coords.keys())
    
    print(f"\n共同国家数: {len(common_countries)}")
    print(f"仅在Stage1: {len(stage1_only)}")
    print(f"仅在Stage3: {len(stage3_only)}")
    
    if stage1_only:
        print(f"\n仅在Stage1的国家 (前10个): {', '.join([str(c) for c in list(stage1_only)[:10]])}")
    if stage3_only:
        print(f"仅在Stage3的国家 (前10个): {', '.join([str(c) for c in list(stage3_only)[:10]])}")
    
    # 计算共同国家的坐标差异
    differences = []
    for country in common_countries:
        s1_coord = stage1_coords[country]
        s3_coord = stage3_coords[country]
        
        distance = calculate_distance(s1_coord, s3_coord)
        pc1_diff = s3_coord['PC1'] - s1_coord['PC1']
        pc2_diff = s3_coord['PC2'] - s1_coord['PC2']
        
        differences.append({
            'country': country,
            'stage1_PC1': s1_coord['PC1'],
            'stage1_PC2': s1_coord['PC2'],
            'stage3_PC1': s3_coord['PC1'],
            'stage3_PC2': s3_coord['PC2'],
            'PC1_diff': pc1_diff,
            'PC2_diff': pc2_diff,
            'distance': distance
        })
    
    # 转换为DataFrame
    diff_df = pd.DataFrame(differences)
    
    # 统计信息
    print("\n" + "="*80)
    print("差异统计")
    print("="*80)
    print(f"\nPC1差异:")
    print(f"  平均: {diff_df['PC1_diff'].mean():.4f}")
    print(f"  标准差: {diff_df['PC1_diff'].std():.4f}")
    print(f"  范围: [{diff_df['PC1_diff'].min():.4f}, {diff_df['PC1_diff'].max():.4f}]")
    
    print(f"\nPC2差异:")
    print(f"  平均: {diff_df['PC2_diff'].mean():.4f}")
    print(f"  标准差: {diff_df['PC2_diff'].std():.4f}")
    print(f"  范围: [{diff_df['PC2_diff'].min():.4f}, {diff_df['PC2_diff'].max():.4f}]")
    
    print(f"\n欧几里得距离:")
    print(f"  平均: {diff_df['distance'].mean():.4f}")
    print(f"  标准差: {diff_df['distance'].std():.4f}")
    print(f"  范围: [{diff_df['distance'].min():.4f}, {diff_df['distance'].max():.4f}]")
    
    # 差异最大的国家
    print("\n" + "="*80)
    print("差异最大的10个国家")
    print("="*80)
    
    top_diff = diff_df.nlargest(10, 'distance')
    for i, row in top_diff.iterrows():
        print(f"\n{row['country']}:")
        print(f"  Stage1: PC1={row['stage1_PC1']:6.2f}, PC2={row['stage1_PC2']:6.2f}")
        print(f"  Stage3: PC1={row['stage3_PC1']:6.2f}, PC2={row['stage3_PC2']:6.2f}")
        print(f"  差异: ΔPC1={row['PC1_diff']:6.2f}, ΔPC2={row['PC2_diff']:6.2f}, 距离={row['distance']:.2f}")
    
    # 差异最小的国家
    print("\n" + "="*80)
    print("差异最小的10个国家")
    print("="*80)
    
    bottom_diff = diff_df.nsmallest(10, 'distance')
    for i, row in bottom_diff.iterrows():
        print(f"\n{row['country']}:")
        print(f"  Stage1: PC1={row['stage1_PC1']:6.2f}, PC2={row['stage1_PC2']:6.2f}")
        print(f"  Stage3: PC1={row['stage3_PC1']:6.2f}, PC2={row['stage3_PC2']:6.2f}")
        print(f"  差异: ΔPC1={row['PC1_diff']:6.2f}, ΔPC2={row['PC2_diff']:6.2f}, 距离={row['distance']:.2f}")
    
    return diff_df

def visualize_differences(diff_df):
    """可视化坐标差异"""
    print("\n" + "="*80)
    print("生成可视化图表...")
    print("="*80)
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 散点图：Stage1 vs Stage3 坐标对比
    ax1 = axes[0, 0]
    ax1.scatter(diff_df['stage1_PC1'], diff_df['stage1_PC2'], 
                alpha=0.5, label='Stage1', s=100, color='blue')
    ax1.scatter(diff_df['stage3_PC1'], diff_df['stage3_PC2'], 
                alpha=0.5, label='Stage3', s=100, color='red')
    
    # 绘制连线
    for _, row in diff_df.iterrows():
        ax1.plot([row['stage1_PC1'], row['stage3_PC1']], 
                [row['stage1_PC2'], row['stage3_PC2']], 
                'k-', alpha=0.2, linewidth=0.5)
    
    ax1.set_xlabel('PC1 (Survival-Expression)', fontsize=12)
    ax1.set_ylabel('PC2 (Traditional-Secular)', fontsize=12)
    ax1.set_title('Stage1 vs Stage3 Country Coordinates', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 距离分布直方图
    ax2 = axes[0, 1]
    ax2.hist(diff_df['distance'], bins=30, edgecolor='black', alpha=0.7)
    ax2.axvline(diff_df['distance'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {diff_df["distance"].mean():.2f}')
    ax2.set_xlabel('Euclidean Distance', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.set_title('Distribution of Coordinate Differences', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. PC1差异 vs PC2差异
    ax3 = axes[1, 0]
    scatter = ax3.scatter(diff_df['PC1_diff'], diff_df['PC2_diff'], 
                         c=diff_df['distance'], cmap='viridis', s=100, alpha=0.6)
    ax3.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax3.axvline(0, color='black', linestyle='-', linewidth=0.5)
    ax3.set_xlabel('ΔPC1 (Stage3 - Stage1)', fontsize=12)
    ax3.set_ylabel('ΔPC2 (Stage3 - Stage1)', fontsize=12)
    ax3.set_title('Coordinate Shifts (Stage3 - Stage1)', fontsize=14, fontweight='bold')
    plt.colorbar(scatter, ax=ax3, label='Distance')
    ax3.grid(True, alpha=0.3)
    
    # 4. 差异最大的国家
    ax4 = axes[1, 1]
    top_10 = diff_df.nlargest(15, 'distance')
    ax4.barh(range(len(top_10)), top_10['distance'])
    ax4.set_yticks(range(len(top_10)))
    ax4.set_yticklabels(top_10['country'], fontsize=9)
    ax4.set_xlabel('Distance', fontsize=12)
    ax4.set_title('Top 15 Countries by Coordinate Difference', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    # 保存图表
    output_file = Path("data/analysis/stage1_vs_stage3_real_countries_comparison.png")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ 图表已保存: {output_file}")
    
    # 保存CSV
    csv_file = Path("data/analysis/stage1_vs_stage3_real_countries_differences.csv")
    diff_df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✅ 差异数据已保存: {csv_file}")

def main():
    """主函数"""
    print("\n" + "="*80)
    print("Stage1 vs Stage3 真实国家坐标对比分析")
    print("="*80)
    
    # 加载数据
    print("\n[1/3] 加载Stage1坐标...")
    stage1_coords = load_stage1_coords()
    if stage1_coords is None:
        return
    
    print("\n[2/3] 加载Stage3坐标...")
    stage3_coords = load_stage3_coords()
    if stage3_coords is None:
        return
    
    # 对比分析
    print("\n[3/3] 对比分析...")
    diff_df = compare_coordinates(stage1_coords, stage3_coords)
    
    # 可视化
    visualize_differences(diff_df)
    
    print("\n" + "="*80)
    print("分析完成")
    print("="*80)

if __name__ == "__main__":
    main()
