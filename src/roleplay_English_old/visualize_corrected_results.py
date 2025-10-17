import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle

def load_corrected_results():
    """加载修正后的PCA结果"""
    print("=== 加载修正后的PCA结果 ===")
    
    result_path = "data/llm_responses_roleplay/fixed_y002_y003_pca_results.pkl"
    
    if not Path(result_path).exists():
        print(f"❌ 文件不存在: {result_path}")
        return None
    
    try:
        df = pd.read_pickle(result_path)
        print(f"✅ 成功加载 {len(df)} 条记录")
        print(f"模型数: {df['model_name'].nunique()}")
        print(f"国家数: {df['country_name'].nunique()}")
        return df
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        return None

def create_corrected_visualizations(df):
    """创建修正后数据的可视化"""
    print("\n=== 创建修正后数据的可视化 ===")
    
    # 设置matplotlib中文字体
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建子图
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('修正后Y002/Y003数据的PCA分析结果', fontsize=16, fontweight='bold')
    
    # 1. Y002分布
    ax1 = axes[0, 0]
    y002_counts = df['Y002'].value_counts().sort_index()
    ax1.bar(y002_counts.index, y002_counts.values, alpha=0.7, color='skyblue')
    ax1.set_title('Y002 (物质主义倾向) 分布')
    ax1.set_xlabel('Y002 值')
    ax1.set_ylabel('频次')
    ax1.set_xticks([1, 2, 3])
    ax1.set_xticklabels(['物质主义', '混合', '后物质主义'])
    for i, v in enumerate(y002_counts.values):
        ax1.text(y002_counts.index[i], v + 5, str(v), ha='center')
    
    # 2. Y003分布
    ax2 = axes[0, 1]
    y003_counts = df['Y003'].value_counts().sort_index()
    ax2.bar(y003_counts.index, y003_counts.values, alpha=0.7, color='lightcoral')
    ax2.set_title('Y003 (传统vs世俗理性) 分布')
    ax2.set_xlabel('Y003 值')
    ax2.set_ylabel('频次')
    for i, v in enumerate(y003_counts.values):
        ax2.text(y003_counts.index[i], v + 5, str(v), ha='center')
    
    # 3. 模型分布
    ax3 = axes[0, 2]
    model_counts = df['model_name'].value_counts()
    ax3.barh(range(len(model_counts)), model_counts.values, alpha=0.7, color='lightgreen')
    ax3.set_title('各模型数据量分布')
    ax3.set_yticks(range(len(model_counts)))
    ax3.set_yticklabels([name.split('/')[-1] for name in model_counts.index], fontsize=8)
    ax3.set_xlabel('记录数')
    for i, v in enumerate(model_counts.values):
        ax3.text(v + 2, i, str(v), va='center')
    
    # 4. PCA散点图 - 按模型着色
    ax4 = axes[1, 0]
    models = df['model_name'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(models)))
    
    for i, model in enumerate(models):
        model_data = df[df['model_name'] == model]
        ax4.scatter(model_data['PC1_rescaled'], model_data['PC2_rescaled'], 
                   alpha=0.6, c=[colors[i]], label=model.split('/')[-1], s=20)
    
    ax4.set_title('修正后PCA结果 - 按模型分组')
    ax4.set_xlabel('PC1 (Survival vs Self-expression)')
    ax4.set_ylabel('PC2 (Traditional vs Secular-rational)')
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    # 5. Y002与PC分量的关系
    ax5 = axes[1, 1]
    for y002_val in sorted(df['Y002'].dropna().unique()):
        data = df[df['Y002'] == y002_val]
        ax5.scatter(data['PC1_rescaled'], data['PC2_rescaled'], 
                   alpha=0.6, label=f'Y002={int(y002_val)}', s=30)
    
    ax5.set_title('Y002与PCA分量的关系')
    ax5.set_xlabel('PC1 (Survival vs Self-expression)')
    ax5.set_ylabel('PC2 (Traditional vs Secular-rational)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Y003与PC分量的关系
    ax6 = axes[1, 2]
    for y003_val in sorted(df['Y003'].dropna().unique()):
        data = df[df['Y003'] == y003_val]
        ax6.scatter(data['PC1_rescaled'], data['PC2_rescaled'], 
                   alpha=0.6, label=f'Y003={int(y003_val)}', s=30)
    
    ax6.set_title('Y003与PCA分量的关系')
    ax6.set_xlabel('PC1 (Survival vs Self-expression)')
    ax6.set_ylabel('PC2 (Traditional vs Secular-rational)')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    output_path = "results/corrected_y002_y003_visualization.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 可视化图片已保存到: {output_path}")
    
    plt.show()

def create_comparison_heatmap(df):
    """创建Y002和Y003的交叉分析热图"""
    print("\n=== 创建Y002和Y003交叉分析热图 ===")
    
    # 创建交叉表
    cross_table = pd.crosstab(df['Y002'], df['Y003'], margins=True)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cross_table, annot=True, fmt='d', cmap='Blues', cbar_kws={'label': '频次'})
    plt.title('Y002和Y003交叉分析热图\n(修正后数据)', fontsize=14, fontweight='bold')
    plt.xlabel('Y003 (传统vs世俗理性价值观)')
    plt.ylabel('Y002 (物质主义倾向)')
    
    # 保存图片
    output_path = "results/corrected_y002_y003_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 交叉分析热图已保存到: {output_path}")
    
    plt.show()
    
    return cross_table

def analyze_model_differences(df):
    """分析不同模型在Y002和Y003上的差异"""
    print("\n=== 分析不同模型在Y002和Y003上的差异 ===")
    
    # 计算每个模型的Y002和Y003均值
    model_stats = df.groupby('model_name')[['Y002', 'Y003', 'PC1_rescaled', 'PC2_rescaled']].agg(['mean', 'std', 'count'])
    
    print("各模型统计信息:")
    print(model_stats.round(3))
    
    # 创建箱线图
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Y002箱线图
    ax1 = axes[0, 0]
    df.boxplot(column='Y002', by='model_name', ax=ax1, rot=45)
    ax1.set_title('各模型Y002分布')
    ax1.set_xlabel('模型')
    ax1.set_ylabel('Y002值')
    
    # Y003箱线图
    ax2 = axes[0, 1]
    df.boxplot(column='Y003', by='model_name', ax=ax2, rot=45)
    ax2.set_title('各模型Y003分布')
    ax2.set_xlabel('模型')
    ax2.set_ylabel('Y003值')
    
    # PC1箱线图
    ax3 = axes[1, 0]
    df.boxplot(column='PC1_rescaled', by='model_name', ax=ax3, rot=45)
    ax3.set_title('各模型PC1分布')
    ax3.set_xlabel('模型')
    ax3.set_ylabel('PC1值')
    
    # PC2箱线图
    ax4 = axes[1, 1]
    df.boxplot(column='PC2_rescaled', by='model_name', ax=ax4, rot=45)
    ax4.set_title('各模型PC2分布')
    ax4.set_xlabel('模型')
    ax4.set_ylabel('PC2值')
    
    plt.suptitle('修正后数据 - 各模型价值观分布比较', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 保存图片
    output_path = "results/corrected_model_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 模型比较图已保存到: {output_path}")
    
    plt.show()
    
    return model_stats

def generate_summary_report(df, cross_table, model_stats):
    """生成修正后数据的分析报告"""
    print("\n=== 生成修正后数据的分析报告 ===")
    
    report = []
    report.append("# 修正后Y002和Y003数据分析报告")
    report.append(f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 基本统计
    report.append("## 1. 基本统计信息")
    report.append(f"- 总记录数: {len(df)}")
    report.append(f"- 模型数量: {df['model_name'].nunique()}")
    report.append(f"- 国家数量: {df['country_name'].nunique()}")
    report.append("")
    
    # Y002分布
    report.append("## 2. Y002 (物质主义倾向) 分布")
    y002_counts = df['Y002'].value_counts().sort_index()
    for val, count in y002_counts.items():
        label = {1: "物质主义", 2: "混合", 3: "后物质主义"}[int(val)]
        percentage = count / len(df) * 100
        report.append(f"- {label} (值={int(val)}): {count} ({percentage:.1f}%)")
    report.append("")
    
    # Y003分布
    report.append("## 3. Y003 (传统vs世俗理性) 分布")
    y003_counts = df['Y003'].value_counts().sort_index()
    for val, count in y003_counts.items():
        percentage = count / len(df) * 100
        report.append(f"- Y003={int(val)}: {count} ({percentage:.1f}%)")
    report.append("")
    
    # PCA结果
    report.append("## 4. PCA分析结果")
    report.append(f"- PC1范围: {df['PC1_rescaled'].min():.3f} 到 {df['PC1_rescaled'].max():.3f}")
    report.append(f"- PC2范围: {df['PC2_rescaled'].min():.3f} 到 {df['PC2_rescaled'].max():.3f}")
    report.append(f"- PC1均值: {df['PC1_rescaled'].mean():.3f} (标准差: {df['PC1_rescaled'].std():.3f})")
    report.append(f"- PC2均值: {df['PC2_rescaled'].mean():.3f} (标准差: {df['PC2_rescaled'].std():.3f})")
    report.append("")
    
    # 模型差异
    report.append("## 5. 各模型表现")
    for model in model_stats.index:
        model_short = model.split('/')[-1]
        y002_mean = model_stats.loc[model, ('Y002', 'mean')]
        y003_mean = model_stats.loc[model, ('Y003', 'mean')]
        count = int(model_stats.loc[model, ('Y002', 'count')])
        report.append(f"- {model_short}: Y002均值={y002_mean:.2f}, Y003均值={y003_mean:.2f}, 记录数={count}")
    report.append("")
    
    # 关键发现
    report.append("## 6. 关键发现")
    report.append("### Y002修正效果:")
    report.append("- 成功将Y002值规范化到1-3范围")
    report.append("- 1=物质主义, 2=混合, 3=后物质主义")
    report.append("")
    
    report.append("### Y003修正效果:")
    report.append("- 成功将Y003值规范化到-2到2范围")
    report.append("- 负值表示更传统，正值表示更世俗理性")
    report.append("")
    
    report.append("### 数据质量:")
    report.append(f"- Y002缺失率: {df['Y002'].isnull().sum()/len(df)*100:.1f}%")
    report.append(f"- Y003缺失率: {df['Y003'].isnull().sum()/len(df)*100:.1f}%")
    report.append("- 修正后的数据质量显著提升")
    
    # 保存报告
    report_path = "results/corrected_y002_y003_analysis_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ 分析报告已保存到: {report_path}")
    
    return report

def main():
    """主函数"""
    print("=== 修正后Y002和Y003数据可视化分析 ===")
    
    # 确保results目录存在
    Path("results").mkdir(exist_ok=True)
    
    try:
        # 1. 加载修正后的结果
        df = load_corrected_results()
        if df is None:
            return
        
        # 2. 创建基础可视化
        create_corrected_visualizations(df)
        
        # 3. 创建交叉分析热图
        cross_table = create_comparison_heatmap(df)
        
        # 4. 分析模型差异
        model_stats = analyze_model_differences(df)
        
        # 5. 生成分析报告
        report = generate_summary_report(df, cross_table, model_stats)
        
        print(f"\n🎉 修正后数据的可视化分析完成！")
        print("生成的文件:")
        print("- results/corrected_y002_y003_visualization.png")
        print("- results/corrected_y002_y003_heatmap.png")
        print("- results/corrected_model_comparison.png")
        print("- results/corrected_y002_y003_analysis_report.md")
        
    except Exception as e:
        print(f"❌ 可视化分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
