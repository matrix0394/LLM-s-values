"""
对比 Stage 2 和 Stage 3 中相同国家、相同模型在英文提问时的坐标
"""

import pickle
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr
from scipy.spatial.distance import euclidean

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_stage2_data():
    """加载 Stage 2 的数据"""
    data_path = Path("/Users/yxy/code/LLM's values/data/roleplay_English")
    
    # 加载 PCA 坐标数据
    pca_file = data_path / "roleplay_pca_entity_scores_latest.pkl"
    with open(pca_file, 'rb') as f:
        pca_data = pickle.load(f)
    
    # 确保是 DataFrame，并筛选出 LLM 角色扮演数据
    if isinstance(pca_data, pd.DataFrame):
        pca_data = pca_data[pca_data['data_source'] == 'llm_roleplay'].copy()
    
    return pca_data

def load_stage3_data():
    """加载 Stage 3 的数据"""
    data_path = Path("/Users/yxy/code/LLM's values/data/roleplay_multilingual")
    
    # 找到最新的数据文件
    pca_file = data_path / "multilingual_entity_scores_pca_fixed_20251019_151819.pkl"
    with open(pca_file, 'rb') as f:
        pca_data = pickle.load(f)
    
    # 确保是 DataFrame，并筛选出多语言角色扮演数据
    if isinstance(pca_data, pd.DataFrame):
        pca_data = pca_data[pca_data['data_source'] == 'Multilingual'].copy()
    
    return pca_data

def normalize_model_name(model_name):
    """标准化模型名称"""
    # 移除可能的前缀
    if '/' in model_name:
        model_name = model_name.split('/')[-1]
    
    # 标准化常见模型名
    mappings = {
        'claude-3.7-sonnet': 'claude-3.7-sonnet',
        'claude-3-7-sonnet': 'claude-3.7-sonnet',
        'deepseek-chat-v3-0324': 'deepseek-chat',
        'deepseek-chat': 'deepseek-chat',
        'gemini-2.0-flash-001': 'gemini-2.0-flash',
        'gemini-2-0-flash': 'gemini-2.0-flash',
        'llama-3.3-70b-instruct': 'llama-3.3-70b',
        'llama-3-3-70b': 'llama-3.3-70b',
        'mistral-nemo': 'mistral-nemo',
        'gpt-4o-mini': 'gpt-4o-mini',
        'qwq-32b': 'qwq-32b',
    }
    
    for key, value in mappings.items():
        if key in model_name.lower():
            return value
    
    return model_name

def main():
    """主函数"""
    print("=" * 80)
    print("Stage 2 vs Stage 3 英文提问坐标对比分析")
    print("=" * 80)
    
    # 加载数据
    print("\n正在加载数据...")
    stage2_df = load_stage2_data()
    stage3_df = load_stage3_data()
    
    print(f"Stage 2 数据类型: {type(stage2_df)}")
    print(f"Stage 3 数据类型: {type(stage3_df)}")
    print(f"Stage 2 数据行数: {len(stage2_df)}")
    print(f"Stage 3 数据行数: {len(stage3_df)}")
    
    print(f"\nStage 2 列名: {stage2_df.columns.tolist()}")
    print(f"Stage 3 列名: {stage3_df.columns.tolist()}")
    
    print(f"\nStage 2 前5行:")
    print(stage2_df.head())
    
    print(f"\nStage 3 前5行:")
    print(stage3_df.head())
    
    # 筛选 Stage 3 的英文数据
    if 'language' in stage3_df.columns:
        # Stage 3 使用语言代码 'en' 表示英语
        stage3_english = stage3_df[stage3_df['language'] == 'en'].copy()
        print(f"\nStage 3 英文数据行数: {len(stage3_english)}")
    else:
        print("\n警告: Stage 3 数据没有 'language' 列")
        return
    
    # 标准化列名
    # Stage 2: 使用 PC1_rescaled, PC2_rescaled
    # Stage 3: 使用 PC1_rescaled, PC2_rescaled
    # 国家: country_code (不是 Country，因为 Country 列是空的)
    # 模型: model_name
    
    # 确认必要的列存在
    required_cols_s2 = ['country_code', 'model_name', 'PC1_rescaled', 'PC2_rescaled']
    required_cols_s3 = ['country_code', 'model_name', 'PC1_rescaled', 'PC2_rescaled']
    
    missing_s2 = [col for col in required_cols_s2 if col not in stage2_df.columns]
    missing_s3 = [col for col in required_cols_s3 if col not in stage3_english.columns]
    
    if missing_s2:
        print(f"\nStage 2 缺少列: {missing_s2}")
        return
    if missing_s3:
        print(f"\nStage 3 缺少列: {missing_s3}")
        return
    
    # 删除空值
    stage2_clean = stage2_df.dropna(subset=['country_code', 'model_name', 'PC1_rescaled', 'PC2_rescaled']).copy()
    stage3_english_clean = stage3_english.dropna(subset=['country_code', 'model_name', 'PC1_rescaled', 'PC2_rescaled']).copy()
    
    print(f"\nStage 2 清理后行数: {len(stage2_clean)}")
    print(f"Stage 3 英文清理后行数: {len(stage3_english_clean)}")
    
    # 标准化模型名
    stage2_clean['model_normalized'] = stage2_clean['model_name'].apply(normalize_model_name)
    stage3_english_clean['model_normalized'] = stage3_english_clean['model_name'].apply(normalize_model_name)
    
    print(f"\nStage 2 模型: {sorted(stage2_clean['model_normalized'].unique())}")
    print(f"Stage 3 英文模型: {sorted(stage3_english_clean['model_normalized'].unique())}")
    
    print(f"\nStage 2 国家数: {stage2_clean['country_code'].nunique()}")
    print(f"Stage 3 英文国家数: {stage3_english_clean['country_code'].nunique()}")
    
    # 标准化国家名称（处理一些差异）
    def normalize_country(name):
        name = str(name).strip()
        # 处理一些已知的差异
        if name.lower().startswith('russian federation'):
            return 'Russian Federation'
        if name.lower().startswith('taiwan'):
            return 'Taiwan'
        return name
    
    stage2_clean['country_normalized'] = stage2_clean['country_code'].apply(normalize_country)
    stage3_english_clean['country_normalized'] = stage3_english_clean['country_code'].apply(normalize_country)
    
    # 准备合并
    stage2_clean['key'] = stage2_clean['country_normalized'] + '_' + stage2_clean['model_normalized']
    stage3_english_clean['key'] = stage3_english_clean['country_normalized'] + '_' + stage3_english_clean['model_normalized']
    
    # 检查共同的 key
    stage2_keys = set(stage2_clean['key'].unique())
    stage3_keys = set(stage3_english_clean['key'].unique())
    common_keys = stage2_keys & stage3_keys
    
    print(f"\n共同的国家-模型组合: {len(common_keys)}")
    
    if not common_keys:
        print("\n警告: 没有找到共同的实体！")
        print(f"\nStage 2 唯一 keys 数量: {len(stage2_keys)}")
        print("Stage 2 keys 示例 (前10个):")
        for key in sorted(list(stage2_keys))[:10]:
            print(f"  {key}")
        print(f"\nStage 3 唯一 keys 数量: {len(stage3_keys)}")
        print("Stage 3 keys 示例 (前10个):")
        for key in sorted(list(stage3_keys))[:10]:
            print(f"  {key}")
        
        # 检查国家和模型的交集
        stage2_countries = set(stage2_clean['country_normalized'].unique())
        stage3_countries = set(stage3_english_clean['country_normalized'].unique())
        common_countries = stage2_countries & stage3_countries
        print(f"\n共同国家数: {len(common_countries)}")
        print(f"共同国家: {sorted(common_countries)}")
        
        stage2_models = set(stage2_clean['model_normalized'].unique())
        stage3_models = set(stage3_english_clean['model_normalized'].unique())
        common_models = stage2_models & stage3_models
        print(f"\n共同模型数: {len(common_models)}")
        print(f"共同模型: {sorted(common_models)}")
        
        return
    
    # 筛选共同的 key
    stage2_common = stage2_clean[stage2_clean['key'].isin(common_keys)].copy()
    stage3_common = stage3_english_clean[stage3_english_clean['key'].isin(common_keys)].copy()
    
    # 合并数据
    comparison_df = stage2_common.merge(
        stage3_common,
        on='key',
        suffixes=('_s2', '_s3')
    )
    
    # 计算差异
    comparison_df['PC1_diff'] = comparison_df['PC1_rescaled_s3'] - comparison_df['PC1_rescaled_s2']
    comparison_df['PC2_diff'] = comparison_df['PC2_rescaled_s3'] - comparison_df['PC2_rescaled_s2']
    comparison_df['distance'] = comparison_df.apply(
        lambda row: euclidean(
            [row['PC1_rescaled_s2'], row['PC2_rescaled_s2']], 
            [row['PC1_rescaled_s3'], row['PC2_rescaled_s3']]
        ), 
        axis=1
    )
    
    # 整理输出数据
    df = pd.DataFrame({
        'country': comparison_df['country_normalized_s2'],
        'model': comparison_df['model_normalized_s2'],
        'stage2_PC1': comparison_df['PC1_rescaled_s2'],
        'stage2_PC2': comparison_df['PC2_rescaled_s2'],
        'stage3_PC1': comparison_df['PC1_rescaled_s3'],
        'stage3_PC2': comparison_df['PC2_rescaled_s3'],
        'PC1_diff': comparison_df['PC1_diff'],
        'PC2_diff': comparison_df['PC2_diff'],
        'distance': comparison_df['distance']
    })
    
    # 统计分析
    print("\n" + "=" * 80)
    print("统计分析")
    print("=" * 80)
    
    print(f"\n共同实体数量: {len(df)}")
    print(f"涉及国家数量: {df['country'].nunique()}")
    print(f"涉及模型数量: {df['model'].nunique()}")
    
    print("\n国家列表:")
    for country in sorted(df['country'].unique()):
        count = len(df[df['country'] == country])
        print(f"  {country}: {count} 个模型")
    
    print("\n模型列表:")
    for model in sorted(df['model'].unique()):
        count = len(df[df['model'] == model])
        print(f"  {model}: {count} 个国家")
    
    # 计算相关系数
    pc1_corr, pc1_pval = pearsonr(df['stage2_PC1'], df['stage3_PC1'])
    pc2_corr, pc2_pval = pearsonr(df['stage2_PC2'], df['stage3_PC2'])
    
    print(f"\n坐标相关性分析:")
    print(f"  PC1 相关系数: {pc1_corr:.4f} (p={pc1_pval:.4e})")
    print(f"  PC2 相关系数: {pc2_corr:.4f} (p={pc2_pval:.4e})")
    
    print(f"\n坐标差异统计:")
    print(f"  PC1 平均差异: {df['PC1_diff'].mean():.4f} ± {df['PC1_diff'].std():.4f}")
    print(f"  PC2 平均差异: {df['PC2_diff'].mean():.4f} ± {df['PC2_diff'].std():.4f}")
    print(f"  欧氏距离: {df['distance'].mean():.4f} ± {df['distance'].std():.4f}")
    print(f"  最大距离: {df['distance'].max():.4f}")
    print(f"  最小距离: {df['distance'].min():.4f}")
    
    # 按模型分组统计
    print(f"\n按模型分组的平均距离:")
    model_stats = df.groupby('model')['distance'].agg(['mean', 'std', 'count'])
    model_stats = model_stats.sort_values('mean')
    for model, row in model_stats.iterrows():
        print(f"  {model}: {row['mean']:.4f} ± {row['std']:.4f} (n={int(row['count'])})")
    
    # 按国家分组统计
    print(f"\n按国家分组的平均距离 (前10):")
    country_stats = df.groupby('country')['distance'].agg(['mean', 'std', 'count'])
    country_stats = country_stats.sort_values('mean', ascending=False).head(10)
    for country, row in country_stats.iterrows():
        print(f"  {country}: {row['mean']:.4f} ± {row['std']:.4f} (n={int(row['count'])})")
    
    # 找出差异最大的案例
    print(f"\n差异最大的10个案例:")
    top_diff = df.nlargest(10, 'distance')[['country', 'model', 'distance', 'PC1_diff', 'PC2_diff']]
    for idx, row in top_diff.iterrows():
        print(f"  {row['country']}_{row['model']}: 距离={row['distance']:.4f}, "
              f"ΔPC1={row['PC1_diff']:.4f}, ΔPC2={row['PC2_diff']:.4f}")
    
    # 保存详细数据
    output_dir = Path("/Users/yxy/code/LLM's values/results/deep_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = output_dir / "stage2_vs_stage3_english_comparison.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n详细数据已保存到: {csv_file}")
    
    # 生成可视化
    create_visualizations(df, output_dir)
    
    # 生成分析报告
    generate_report(df, output_dir)

def create_visualizations(df, output_dir):
    """创建可视化图表"""
    print("\n正在生成可视化...")
    
    # 1. 散点图对比
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # PC1 对比
    axes[0].scatter(df['stage2_PC1'], df['stage3_PC1'], alpha=0.6, s=50)
    axes[0].plot([df['stage2_PC1'].min(), df['stage2_PC1'].max()],
                 [df['stage2_PC1'].min(), df['stage2_PC1'].max()],
                 'r--', lw=2, label='y=x')
    axes[0].set_xlabel('Stage 2 PC1', fontsize=12)
    axes[0].set_ylabel('Stage 3 PC1 (English)', fontsize=12)
    axes[0].set_title(f'PC1 Comparison (r={pearsonr(df["stage2_PC1"], df["stage3_PC1"])[0]:.3f})', 
                      fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # PC2 对比
    axes[1].scatter(df['stage2_PC2'], df['stage3_PC2'], alpha=0.6, s=50)
    axes[1].plot([df['stage2_PC2'].min(), df['stage2_PC2'].max()],
                 [df['stage2_PC2'].min(), df['stage2_PC2'].max()],
                 'r--', lw=2, label='y=x')
    axes[1].set_xlabel('Stage 2 PC2', fontsize=12)
    axes[1].set_ylabel('Stage 3 PC2 (English)', fontsize=12)
    axes[1].set_title(f'PC2 Comparison (r={pearsonr(df["stage2_PC2"], df["stage3_PC2"])[0]:.3f})', 
                      fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'stage2_vs_stage3_pc_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. 文化地图对比
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    
    # Stage 2
    axes[0].scatter(df['stage2_PC1'], df['stage2_PC2'], alpha=0.6, s=100, c='blue', label='Stage 2')
    axes[0].set_xlabel('PC1: Traditional vs. Secular-Rational', fontsize=12)
    axes[0].set_ylabel('PC2: Survival vs. Self-Expression', fontsize=12)
    axes[0].set_title('Stage 2: English Roleplay', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    axes[0].axvline(x=0, color='k', linestyle='-', linewidth=0.5)
    
    # Stage 3
    axes[1].scatter(df['stage3_PC1'], df['stage3_PC2'], alpha=0.6, s=100, c='red', label='Stage 3 English')
    axes[1].set_xlabel('PC1: Traditional vs. Secular-Rational', fontsize=12)
    axes[1].set_ylabel('PC2: Survival vs. Self-Expression', fontsize=12)
    axes[1].set_title('Stage 3: Multilingual (English)', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    axes[1].axvline(x=0, color='k', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'stage2_vs_stage3_cultural_maps.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. 移动向量图
    fig, ax = plt.subplots(figsize=(14, 10))
    
    for idx, row in df.iterrows():
        ax.arrow(row['stage2_PC1'], row['stage2_PC2'],
                row['PC1_diff'], row['PC2_diff'],
                head_width=0.1, head_length=0.1, fc='blue', ec='blue', alpha=0.3, linewidth=0.5)
    
    ax.scatter(df['stage2_PC1'], df['stage2_PC2'], c='green', s=50, alpha=0.6, label='Stage 2', zorder=5)
    ax.scatter(df['stage3_PC1'], df['stage3_PC2'], c='red', s=50, alpha=0.6, label='Stage 3 English', zorder=5)
    
    ax.set_xlabel('PC1: Traditional vs. Secular-Rational', fontsize=12)
    ax.set_ylabel('PC2: Survival vs. Self-Expression', fontsize=12)
    ax.set_title('Stage 2 → Stage 3 坐标变化 (箭头方向)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'stage2_vs_stage3_movement_vectors.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. 距离分布
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 总体距离分布
    axes[0, 0].hist(df['distance'], bins=30, alpha=0.7, edgecolor='black')
    axes[0, 0].axvline(df['distance'].mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {df["distance"].mean():.3f}')
    axes[0, 0].set_xlabel('Euclidean Distance', fontsize=11)
    axes[0, 0].set_ylabel('Frequency', fontsize=11)
    axes[0, 0].set_title('Overall Distance Distribution', fontsize=12, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 按模型的距离
    model_distances = df.groupby('model')['distance'].mean().sort_values()
    axes[0, 1].barh(range(len(model_distances)), model_distances.values)
    axes[0, 1].set_yticks(range(len(model_distances)))
    axes[0, 1].set_yticklabels(model_distances.index, fontsize=9)
    axes[0, 1].set_xlabel('Mean Distance', fontsize=11)
    axes[0, 1].set_title('Average Distance by Model', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3, axis='x')
    
    # PC1差异分布
    axes[1, 0].hist(df['PC1_diff'], bins=30, alpha=0.7, color='green', edgecolor='black')
    axes[1, 0].axvline(df['PC1_diff'].mean(), color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {df["PC1_diff"].mean():.3f}')
    axes[1, 0].axvline(0, color='black', linestyle='-', linewidth=1)
    axes[1, 0].set_xlabel('PC1 Difference (Stage3 - Stage2)', fontsize=11)
    axes[1, 0].set_ylabel('Frequency', fontsize=11)
    axes[1, 0].set_title('PC1 Difference Distribution', fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # PC2差异分布
    axes[1, 1].hist(df['PC2_diff'], bins=30, alpha=0.7, color='orange', edgecolor='black')
    axes[1, 1].axvline(df['PC2_diff'].mean(), color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {df["PC2_diff"].mean():.3f}')
    axes[1, 1].axvline(0, color='black', linestyle='-', linewidth=1)
    axes[1, 1].set_xlabel('PC2 Difference (Stage3 - Stage2)', fontsize=11)
    axes[1, 1].set_ylabel('Frequency', fontsize=11)
    axes[1, 1].set_title('PC2 Difference Distribution', fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'stage2_vs_stage3_distance_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"可视化已保存到: {output_dir}")

def generate_report(df, output_dir):
    """生成分析报告"""
    print("\n正在生成分析报告...")
    
    report = []
    report.append("# Stage 2 vs Stage 3 英文提问坐标对比分析报告\n")
    report.append(f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("=" * 80 + "\n\n")
    
    report.append("## 1. 数据概览\n\n")
    report.append(f"- 共同实体数量: {len(df)}\n")
    report.append(f"- 涉及国家数量: {df['country'].nunique()}\n")
    report.append(f"- 涉及模型数量: {df['model'].nunique()}\n\n")
    
    report.append("### 国家列表\n\n")
    for country in sorted(df['country'].unique()):
        count = len(df[df['country'] == country])
        report.append(f"- {country}: {count} 个模型\n")
    report.append("\n")
    
    report.append("### 模型列表\n\n")
    for model in sorted(df['model'].unique()):
        count = len(df[df['model'] == model])
        report.append(f"- {model}: {count} 个国家\n")
    report.append("\n")
    
    report.append("## 2. 坐标一致性分析\n\n")
    pc1_corr, pc1_pval = pearsonr(df['stage2_PC1'], df['stage3_PC1'])
    pc2_corr, pc2_pval = pearsonr(df['stage2_PC2'], df['stage3_PC2'])
    
    report.append(f"### Pearson 相关系数\n\n")
    report.append(f"- **PC1 相关系数**: {pc1_corr:.4f} (p={pc1_pval:.4e})\n")
    report.append(f"- **PC2 相关系数**: {pc2_corr:.4f} (p={pc2_pval:.4e})\n\n")
    
    if pc1_corr > 0.9 and pc2_corr > 0.9:
        report.append("✅ **结论**: PC1 和 PC2 在两个阶段之间高度一致 (r>0.9)\n\n")
    elif pc1_corr > 0.7 and pc2_corr > 0.7:
        report.append("⚠️ **结论**: PC1 和 PC2 在两个阶段之间较为一致 (r>0.7)\n\n")
    else:
        report.append("❌ **结论**: PC1 和 PC2 在两个阶段之间一致性较低 (r<0.7)\n\n")
    
    report.append("## 3. 坐标差异统计\n\n")
    report.append(f"- **PC1 平均差异**: {df['PC1_diff'].mean():.4f} ± {df['PC1_diff'].std():.4f}\n")
    report.append(f"- **PC2 平均差异**: {df['PC2_diff'].mean():.4f} ± {df['PC2_diff'].std():.4f}\n")
    report.append(f"- **欧氏距离**: {df['distance'].mean():.4f} ± {df['distance'].std():.4f}\n")
    report.append(f"  - 最大距离: {df['distance'].max():.4f}\n")
    report.append(f"  - 最小距离: {df['distance'].min():.4f}\n\n")
    
    report.append("## 4. 按模型分组分析\n\n")
    model_stats = df.groupby('model')['distance'].agg(['mean', 'std', 'count']).sort_values('mean')
    report.append("| 模型 | 平均距离 | 标准差 | 样本数 |\n")
    report.append("|------|----------|--------|--------|\n")
    for model, row in model_stats.iterrows():
        report.append(f"| {model} | {row['mean']:.4f} | {row['std']:.4f} | {int(row['count'])} |\n")
    report.append("\n")
    
    report.append("## 5. 按国家分组分析 (差异最大的前10个)\n\n")
    country_stats = df.groupby('country')['distance'].agg(['mean', 'std', 'count']).sort_values('mean', ascending=False).head(10)
    report.append("| 国家 | 平均距离 | 标准差 | 样本数 |\n")
    report.append("|------|----------|--------|--------|\n")
    for country, row in country_stats.iterrows():
        report.append(f"| {country} | {row['mean']:.4f} | {row['std']:.4f} | {int(row['count'])} |\n")
    report.append("\n")
    
    report.append("## 6. 差异最大的案例\n\n")
    report.append("| 国家 | 模型 | 距离 | ΔPC1 | ΔPC2 |\n")
    report.append("|------|------|------|------|------|\n")
    top_diff = df.nlargest(10, 'distance')
    for idx, row in top_diff.iterrows():
        report.append(f"| {row['country']} | {row['model']} | {row['distance']:.4f} | "
                     f"{row['PC1_diff']:.4f} | {row['PC2_diff']:.4f} |\n")
    report.append("\n")
    
    report.append("## 7. 结论与讨论\n\n")
    
    avg_distance = df['distance'].mean()
    if avg_distance < 0.5:
        consistency_level = "非常高"
        emoji = "✅"
    elif avg_distance < 1.0:
        consistency_level = "较高"
        emoji = "✅"
    elif avg_distance < 2.0:
        consistency_level = "中等"
        emoji = "⚠️"
    else:
        consistency_level = "较低"
        emoji = "❌"
    
    report.append(f"{emoji} **总体一致性**: {consistency_level}\n\n")
    report.append(f"- Stage 2 和 Stage 3 在英文提问时的平均距离为 {avg_distance:.4f}\n")
    report.append(f"- PC1 相关系数 {pc1_corr:.4f}，PC2 相关系数 {pc2_corr:.4f}\n\n")
    
    if pc1_corr > 0.8:
        report.append("**PC1 (传统-世俗理性) 维度**: 两个阶段高度一致，说明模型在这个维度上的表现稳定。\n\n")
    else:
        report.append("**PC1 (传统-世俗理性) 维度**: 两个阶段存在一定差异，可能受到实验设计或数据采集方式的影响。\n\n")
    
    if pc2_corr > 0.8:
        report.append("**PC2 (生存-自我表达) 维度**: 两个阶段高度一致，说明模型在这个维度上的表现稳定。\n\n")
    else:
        report.append("**PC2 (生存-自我表达) 维度**: 两个阶段存在一定差异，可能受到实验设计或数据采集方式的影响。\n\n")
    
    report.append("### 可能的差异来源\n\n")
    report.append("1. **实验时间差异**: Stage 2 和 Stage 3 可能在不同时间点进行，模型可能已更新\n")
    report.append("2. **采样随机性**: 即使温度参数固定，模型输出仍可能存在一定随机性\n")
    report.append("3. **问卷版本**: 可能使用了不同版本的问卷或提示词\n")
    report.append("4. **数据处理**: PCA 投影可能在两个阶段使用了不同的参考点\n\n")
    
    # 保存报告
    report_file = output_dir / "stage2_vs_stage3_comparison_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    print(f"分析报告已保存到: {report_file}")

if __name__ == "__main__":
    main()
    print("\n分析完成！")

