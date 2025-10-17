import sys
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

def load_pca_results():
    """加载PCA结果数据"""
    pca_file = "data/llm_responses_roleplay/correct_pca_results.pkl"
    if not os.path.exists(pca_file):
        raise FileNotFoundError(f"未找到PCA结果文件: {pca_file}")
    
    data = pd.read_pickle(pca_file)
    print(f"✅ 成功加载PCA结果: {data.shape}")
    return data

def plot_model_comparison(data, save_path=None):
    """绘制不同模型的比较图"""
    plt.figure(figsize=(16, 12))
    
    # 定义颜色和标记
    colors = ['#ff6347', '#4682b4', '#32cd32', '#ffd700', '#ff69b4', '#20b2aa', '#ff4500']
    markers = ['o', 's', '^', 'D', 'v', '<', '>']
    
    # 按模型分组绘制
    models = data['model_name'].unique()
    for i, model in enumerate(models):
        model_data = data[data['model_name'] == model]
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]
        
        plt.scatter(model_data['PC1_rescaled'], model_data['PC2_rescaled'],
                   c=color, marker=marker, s=100, alpha=0.7, 
                   label=model, edgecolors='black', linewidth=0.5)
    
    plt.xlabel('Survival vs. Self-Expression Values', fontsize=12)
    plt.ylabel('Traditional vs. Secular Values', fontsize=12)
    plt.title('AI Model Country Roleplay Comparison on Cultural Map', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"模型比较图已保存: {save_path}")
    
    plt.show()

def plot_country_distribution(data, save_path=None):
    """绘制国家分布图"""
    plt.figure(figsize=(16, 12))
    
    # 按国家分组，每个国家用不同颜色
    countries = data['country_name'].unique()
    colors = plt.cm.tab20(np.linspace(0, 1, len(countries)))
    
    for i, country in enumerate(countries):
        country_data = data[data['country_name'] == country]
        color = colors[i]
        
        # 为每个国家绘制所有模型的结果
        plt.scatter(country_data['PC1_rescaled'], country_data['PC2_rescaled'],
                   c=[color], s=80, alpha=0.7, label=country, 
                   edgecolors='black', linewidth=0.3)
    
    plt.xlabel('Survival vs. Self-Expression Values', fontsize=12)
    plt.ylabel('Traditional vs. Secular Values', fontsize=12)
    plt.title('Country Distribution Across AI Models', fontsize=14, fontweight='bold')
    
    # 只显示前20个国家的图例，避免过于拥挤
    handles, labels = plt.gca().get_legend_handles_labels()
    if len(handles) > 20:
        plt.legend(handles[:20], labels[:20], bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    else:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"国家分布图已保存: {save_path}")
    
    plt.show()

def create_interactive_map(data, save_path=None):
    """创建交互式地图"""
    # 创建plotly图表
    fig = go.Figure()
    
    # 定义颜色和标记
    colors = ['#ff6347', '#4682b4', '#32cd32', '#ffd700', '#ff69b4', '#20b2aa', '#ff4500']
    markers = ['circle', 'square', 'diamond', 'triangle-up', 'star', 'hexagon', 'pentagon']
    
    # 按模型分组
    models = data['model_name'].unique()
    for i, model in enumerate(models):
        model_data = data[data['model_name'] == model]
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]
        
        fig.add_trace(go.Scatter(
            x=model_data['PC1_rescaled'],
            y=model_data['PC2_rescaled'],
            mode='markers',
            name=model,
            marker=dict(
                size=10,
                color=color,
                symbol=marker,
                line=dict(width=1, color='black')
            ),
            text=model_data['country_name'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Model: ' + model + '<br>' +
                         'PC1: %{x:.2f}<br>' +
                         'PC2: %{y:.2f}<br>' +
                         '<extra></extra>',
            showlegend=True
        ))
    
    # 设置图表布局
    fig.update_layout(
        title=dict(
            text='Interactive AI Model Country Roleplay Cultural Map',
            x=0.5,
            font=dict(size=16, family='Arial Black')
        ),
        xaxis_title='Survival vs. Self-Expression Values',
        yaxis_title='Traditional vs. Secular Values',
        width=1200,
        height=800,
        hovermode='closest',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=200),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # 添加网格
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    if save_path:
        if not save_path.endswith('.html'):
            save_path = save_path.replace('.png', '.html')
        fig.write_html(save_path)
        print(f"交互式地图已保存: {save_path}")
    
    fig.show()
    return fig

def analyze_model_performance(data):
    """分析模型性能"""
    print("\n=== 模型性能分析 ===")
    
    # 按模型统计
    model_stats = data.groupby('model_name').agg({
        'PC1_rescaled': ['mean', 'std', 'min', 'max'],
        'PC2_rescaled': ['mean', 'std', 'min', 'max']
    }).round(3)
    
    print("各模型PC坐标统计:")
    print(model_stats)
    
    # 计算每个模型的覆盖范围
    print("\n各模型覆盖范围:")
    for model in data['model_name'].unique():
        model_data = data[data['model_name'] == model]
        pc1_range = model_data['PC1_rescaled'].max() - model_data['PC1_rescaled'].min()
        pc2_range = model_data['PC2_rescaled'].max() - model_data['PC2_rescaled'].min()
        print(f"  {model}: PC1范围={pc1_range:.3f}, PC2范围={pc2_range:.3f}")
    
    # 分析国家一致性
    print("\n国家一致性分析:")
    country_consistency = []
    for country in data['country_name'].unique():
        country_data = data[data['country_name'] == country]
        if len(country_data) > 1:
            pc1_std = country_data['PC1_rescaled'].std()
            pc2_std = country_data['PC2_rescaled'].std()
            consistency = 1 / (1 + pc1_std + pc2_std)  # 一致性指标
            country_consistency.append({
                'country': country,
                'pc1_std': pc1_std,
                'pc2_std': pc2_std,
                'consistency': consistency,
                'model_count': len(country_data)
            })
    
    consistency_df = pd.DataFrame(country_consistency)
    consistency_df = consistency_df.sort_values('consistency', ascending=False)
    
    print("最一致的国家 (前10个):")
    for _, row in consistency_df.head(10).iterrows():
        print(f"  {row['country']}: 一致性={row['consistency']:.3f}, 模型数={row['model_count']}")
    
    print("\n最不一致的国家 (后10个):")
    for _, row in consistency_df.tail(10).iterrows():
        print(f"  {row['country']}: 一致性={row['consistency']:.3f}, 模型数={row['model_count']}")
    
    return consistency_df

def main():
    """主函数"""
    print("=== 开始Roleplay数据可视化分析 ===")
    
    # 创建结果目录
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    try:
        # 1. 加载数据
        print("\n1. 加载PCA结果数据...")
        data = load_pca_results()
        
        # 2. 绘制模型比较图
        print("\n2. 绘制模型比较图...")
        model_comparison_path = os.path.join(results_dir, "model_comparison.png")
        plot_model_comparison(data, save_path=model_comparison_path)
        
        # 3. 绘制国家分布图
        print("\n3. 绘制国家分布图...")
        country_distribution_path = os.path.join(results_dir, "country_distribution.png")
        plot_country_distribution(data, save_path=country_distribution_path)
        
        # 4. 创建交互式地图
        print("\n4. 创建交互式地图...")
        interactive_map_path = os.path.join(results_dir, "interactive_cultural_map.html")
        create_interactive_map(data, save_path=interactive_map_path)
        
        # 5. 分析模型性能
        print("\n5. 分析模型性能...")
        consistency_df = analyze_model_performance(data)
        
        # 6. 保存一致性分析结果
        consistency_path = os.path.join(results_dir, "country_consistency.csv")
        consistency_df.to_csv(consistency_path, index=False)
        print(f"\n一致性分析结果已保存: {consistency_path}")
        
        print("\n🎉 可视化分析完成！")
        print(f"\n生成的文件:")
        print(f"  - {model_comparison_path}")
        print(f"  - {country_distribution_path}")
        print(f"  - {interactive_map_path}")
        print(f"  - {consistency_path}")
        
    except Exception as e:
        print(f"❌ 可视化分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


