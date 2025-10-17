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

def load_working_data():
    """加载可以正常工作的数据文件"""
    # 使用我们已经生成的PCA结果
    pca_file = "data/llm_responses_roleplay/correct_pca_results.pkl"
    if os.path.exists(pca_file):
        data = pd.read_pickle(pca_file)
        print(f"✅ 成功加载PCA结果: {data.shape}")
        return data
    
    # 备用：使用其他正常文件
    backup_files = [
        "data/llm_responses_roleplay/simple_pca_results.pkl",
        "data/roleplay_entity_scores_pca.pkl",
        "data/country_codes.pkl"
    ]
    
    for file in backup_files:
        if os.path.exists(file):
            try:
                data = pd.read_pickle(file)
                print(f"✅ 成功加载备用文件 {file}: {data.shape}")
                return data
            except Exception as e:
                print(f"❌ 无法加载 {file}: {e}")
                continue
    
    raise FileNotFoundError("没有找到可用的数据文件")

def create_combined_analysis():
    """创建包含真实国家和AI角色扮演的完整分析"""
    print("=== 创建完整的文化地图分析 ===")
    
    # 1. 加载AI角色扮演数据
    print("\n1. 加载AI角色扮演数据...")
    roleplay_data = load_working_data()
    
    # 2. 尝试加载真实国家数据（如果可用）
    print("\n2. 尝试加载真实国家数据...")
    real_country_data = None
    
    # 尝试从JSON文件加载真实国家数据
    try:
        import json
        country_scores_file = "data/country_scores_pca.json"
        if os.path.exists(country_scores_file):
            with open(country_scores_file, 'r', encoding='utf-8') as f:
                real_data = json.load(f)
            
            # 转换为DataFrame
            real_country_data = pd.DataFrame(real_data)
            print(f"✅ 成功加载真实国家数据: {real_country_data.shape}")
        else:
            print("⚠️  未找到真实国家数据文件")
    except Exception as e:
        print(f"⚠️  无法加载真实国家数据: {e}")
    
    # 3. 合并数据
    print("\n3. 合并数据...")
    if real_country_data is not None:
        # 为真实国家数据添加标识
        real_country_data['roleplay'] = False
        real_country_data['model_name'] = 'Real Country'
        real_country_data['country_name'] = real_country_data['Country']
        
        # 为AI角色扮演数据添加标识
        roleplay_data['roleplay'] = True
        
        # 合并数据
        combined_data = pd.concat([real_country_data, roleplay_data], ignore_index=True)
        print(f"✅ 合并后数据: {combined_data.shape}")
    else:
        combined_data = roleplay_data
        combined_data['roleplay'] = True
        print(f"✅ 使用AI角色扮演数据: {combined_data.shape}")
    
    return combined_data

def plot_combined_cultural_map(data, save_path=None):
    """绘制包含真实国家和AI角色扮演的文化地图"""
    plt.figure(figsize=(20, 16))
    
    # 分离数据
    real_data = data[data['roleplay'] == False] if 'roleplay' in data.columns else pd.DataFrame()
    ai_data = data[data['roleplay'] == True] if 'roleplay' in data.columns else data
    
    # 绘制真实国家数据
    if not real_data.empty:
        plt.scatter(real_data['PC1_rescaled'], real_data['PC2_rescaled'], 
                   c='lightblue', s=60, alpha=0.7, label='Real Countries', 
                   marker='o', edgecolors='black', linewidth=0.5)
        
        # 添加国家标签（只显示部分重要国家）
        important_countries = ['United States', 'China', 'Germany', 'Japan', 'India', 'Brazil', 'Russia']
        for _, row in real_data.iterrows():
            if row['Country'] in important_countries:
                plt.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                        fontsize=8, ha='center', va='bottom', color='blue')
    
    # 绘制AI角色扮演数据
    if not ai_data.empty:
        # 为不同模型使用不同颜色和标记
        colors = ['#ff6347', '#4682b4', '#32cd32', '#ffd700', '#ff69b4', '#20b2aa', '#ff4500']
        markers = ['D', 's', '^', 'v', '<', '>', 'p']
        
        models = ai_data['model_name'].unique()
        for i, model in enumerate(models):
            model_data = ai_data[ai_data['model_name'] == model]
            color = colors[i % len(colors)]
            marker = markers[i % len(markers)]
            
            plt.scatter(model_data['PC1_rescaled'], model_data['PC2_rescaled'],
                       c=color, marker=marker, s=100, alpha=0.7, 
                       label=f'AI: {model}', edgecolors='black', linewidth=0.5)
    
    plt.xlabel('Survival vs. Self-Expression Values', fontsize=14)
    plt.ylabel('Traditional vs. Secular Values', fontsize=14)
    plt.title('Inglehart-Welzel Cultural Map: Real Countries vs AI Roleplay', fontsize=16, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ 文化地图已保存: {save_path}")
    
    plt.show()

def create_interactive_combined_map(data, save_path=None):
    """创建交互式合并地图"""
    fig = go.Figure()
    
    # 分离数据
    real_data = data[data['roleplay'] == False] if 'roleplay' in data.columns else pd.DataFrame()
    ai_data = data[data['roleplay'] == True] if 'roleplay' in data.columns else data
    
    # 绘制真实国家数据
    if not real_data.empty:
        fig.add_trace(go.Scatter(
            x=real_data['PC1_rescaled'],
            y=real_data['PC2_rescaled'],
            mode='markers',
            name='Real Countries',
            marker=dict(
                size=10,
                color='lightblue',
                symbol='circle',
                line=dict(width=1, color='black')
            ),
            text=real_data['Country'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Type: Real Country<br>' +
                         'PC1: %{x:.2f}<br>' +
                         'PC2: %{y:.2f}<br>' +
                         '<extra></extra>',
            showlegend=True
        ))
    
    # 绘制AI角色扮演数据
    if not ai_data.empty:
        colors = ['#ff6347', '#4682b4', '#32cd32', '#ffd700', '#ff69b4', '#20b2aa', '#ff4500']
        markers = ['diamond', 'square', 'triangle-up', 'star', 'hexagon', 'pentagon', 'cross']
        
        models = ai_data['model_name'].unique()
        for i, model in enumerate(models):
            model_data = ai_data[ai_data['model_name'] == model]
            color = colors[i % len(colors)]
            marker = markers[i % len(markers)]
            
            fig.add_trace(go.Scatter(
                x=model_data['PC1_rescaled'],
                y=model_data['PC2_rescaled'],
                mode='markers',
                name=f'AI: {model}',
                marker=dict(
                    size=12,
                    color=color,
                    symbol=marker,
                    line=dict(width=1, color='black')
                ),
                text=model_data['country_name'],
                hovertemplate='<b>%{text}</b><br>' +
                             f'Model: {model}<br>' +
                             'Type: AI Roleplay<br>' +
                             'PC1: %{x:.2f}<br>' +
                             'PC2: %{y:.2f}<br>' +
                             '<extra></extra>',
                showlegend=True
            ))
    
    # 设置图表布局
    fig.update_layout(
        title=dict(
            text='Interactive Cultural Map: Real Countries vs AI Roleplay',
            x=0.5,
            font=dict(size=16, family='Arial Black')
        ),
        xaxis_title='Survival vs. Self-Expression Values',
        yaxis_title='Traditional vs. Secular Values',
        width=1400,
        height=900,
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
        print(f"✅ 交互式地图已保存: {save_path}")
    
    fig.show()
    return fig

def analyze_ai_vs_real(data):
    """分析AI角色扮演与真实国家的差异"""
    print("\n=== AI角色扮演与真实国家对比分析 ===")
    
    real_data = data[data['roleplay'] == False] if 'roleplay' in data.columns else pd.DataFrame()
    ai_data = data[data['roleplay'] == True] if 'roleplay' in data.columns else data
    
    if real_data.empty:
        print("⚠️  没有真实国家数据可供对比")
        return
    
    print(f"真实国家数量: {len(real_data)}")
    print(f"AI角色扮演数量: {len(ai_data)}")
    
    # 计算覆盖范围
    print(f"\n真实国家PC坐标范围:")
    print(f"  PC1: {real_data['PC1_rescaled'].min():.3f} 到 {real_data['PC1_rescaled'].max():.3f}")
    print(f"  PC2: {real_data['PC2_rescaled'].min():.3f} 到 {real_data['PC2_rescaled'].max():.3f}")
    
    print(f"\nAI角色扮演PC坐标范围:")
    print(f"  PC1: {ai_data['PC1_rescaled'].min():.3f} 到 {ai_data['PC1_rescaled'].max():.3f}")
    print(f"  PC2: {ai_data['PC2_rescaled'].min():.3f} 到 {ai_data['PC2_rescaled'].max():.3f}")
    
    # 按模型分析
    if 'model_name' in ai_data.columns:
        print(f"\n各AI模型的覆盖范围:")
        for model in ai_data['model_name'].unique():
            model_data = ai_data[ai_data['model_name'] == model]
            pc1_range = model_data['PC1_rescaled'].max() - model_data['PC1_rescaled'].min()
            pc2_range = model_data['PC2_rescaled'].max() - model_data['PC2_rescaled'].min()
            print(f"  {model}: PC1范围={pc1_range:.3f}, PC2范围={pc2_range:.3f}")

def main():
    """主函数"""
    print("=== 开始完整的文化地图分析 ===")
    
    # 创建结果目录
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    try:
        # 1. 创建合并分析
        print("\n1. 创建合并分析...")
        combined_data = create_combined_analysis()
        
        # 2. 绘制静态文化地图
        print("\n2. 绘制静态文化地图...")
        static_map_path = os.path.join(results_dir, "combined_cultural_map.png")
        plot_combined_cultural_map(combined_data, save_path=static_map_path)
        
        # 3. 创建交互式地图
        print("\n3. 创建交互式地图...")
        interactive_map_path = os.path.join(results_dir, "combined_cultural_map_interactive.html")
        create_interactive_combined_map(combined_data, save_path=interactive_map_path)
        
        # 4. 分析对比
        print("\n4. 分析对比...")
        analyze_ai_vs_real(combined_data)
        
        # 5. 保存合并数据
        print("\n5. 保存合并数据...")
        combined_data_path = os.path.join(results_dir, "combined_analysis_data.pkl")
        combined_data.to_pickle(combined_data_path)
        print(f"✅ 合并数据已保存: {combined_data_path}")
        
        print("\n🎉 完整分析完成！")
        print(f"\n生成的文件:")
        print(f"  - {static_map_path}")
        print(f"  - {interactive_map_path}")
        print(f"  - {combined_data_path}")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
