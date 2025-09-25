import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

def load_real_country_data():
    """加载真实国家数据"""
    print("=== 加载真实国家数据 ===")
    
    try:
        # 加载真实国家的PCA结果
        country_scores_path = "data/country_scores_pca.pkl"
        if os.path.exists(country_scores_path):
            real_data = pd.read_pickle(country_scores_path)
            real_data['roleplay'] = False
            real_data['model_name'] = 'Real Country'
            print(f"✅ 加载真实国家数据: {real_data.shape}")
            return real_data
        else:
            print(f"❌ 真实国家数据文件不存在: {country_scores_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ 加载真实国家数据失败: {e}")
        return pd.DataFrame()

def load_ai_roleplay_data():
    """加载AI角色扮演数据"""
    print("\n=== 加载AI角色扮演数据 ===")
    
    try:
        # 加载AI角色扮演的PCA结果
        roleplay_path = "data/llm_responses_roleplay/correct_pca_results.pkl"
        if os.path.exists(roleplay_path):
            ai_data = pd.read_pickle(roleplay_path)
            ai_data['roleplay'] = True
            print(f"✅ 加载AI角色扮演数据: {ai_data.shape}")
            return ai_data
        else:
            print(f"❌ AI角色扮演数据文件不存在: {roleplay_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ 加载AI角色扮演数据失败: {e}")
        return pd.DataFrame()

def create_combined_cultural_map(real_data, ai_data, save_path=None):
    """创建包含真实国家和AI角色扮演的文化地图"""
    plt.figure(figsize=(20, 16))
    
    # 绘制真实国家数据
    if not real_data.empty:
        plt.scatter(real_data['PC1_rescaled'], real_data['PC2_rescaled'], 
                   c='lightblue', s=80, alpha=0.8, label='Real Countries', 
                   marker='o', edgecolors='black', linewidth=0.8)
        
        # 添加重要国家标签
        important_countries = ['United States', 'China', 'Germany', 'Japan', 'India', 'Brazil', 'Russia', 'France', 'United Kingdom', 'Italy']
        for _, row in real_data.iterrows():
            if row['Country'] in important_countries:
                plt.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                        fontsize=9, ha='center', va='bottom', color='blue', fontweight='bold')
    
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
                       c=color, marker=marker, s=120, alpha=0.7, 
                       label=f'AI: {model}', edgecolors='black', linewidth=0.5)
    
    plt.xlabel('Survival vs. Self-Expression Values', fontsize=16, fontweight='bold')
    plt.ylabel('Traditional vs. Secular Values', fontsize=16, fontweight='bold')
    plt.title('Inglehart-Welzel Cultural Map: Real Countries vs AI Roleplay', fontsize=18, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ 文化地图已保存: {save_path}")
    
    plt.show()

def create_interactive_combined_map(real_data, ai_data, save_path=None):
    """创建交互式合并地图"""
    fig = go.Figure()
    
    # 绘制真实国家数据
    if not real_data.empty:
        fig.add_trace(go.Scatter(
            x=real_data['PC1_rescaled'],
            y=real_data['PC2_rescaled'],
            mode='markers',
            name='Real Countries',
            marker=dict(
                size=12,
                color='lightblue',
                symbol='circle',
                line=dict(width=2, color='black')
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
                    size=14,
                    color=color,
                    symbol=marker,
                    line=dict(width=2, color='black')
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
            font=dict(size=18, family='Arial Black')
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

def analyze_ai_vs_real(real_data, ai_data):
    """分析AI角色扮演与真实国家的差异"""
    print("\n=== AI角色扮演与真实国家对比分析 ===")
    
    if real_data.empty:
        print("⚠️  没有真实国家数据可供对比")
        return
    
    if ai_data.empty:
        print("⚠️  没有AI角色扮演数据可供对比")
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
    print("=== 开始创建完整的文化地图分析 ===")
    
    # 创建结果目录
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    try:
        # 1. 加载数据
        real_data = load_real_country_data()
        ai_data = load_ai_roleplay_data()
        
        if real_data.empty and ai_data.empty:
            print("❌ 没有可用的数据")
            return
        
        # 2. 绘制静态文化地图
        print("\n=== 绘制静态文化地图 ===")
        static_map_path = os.path.join(results_dir, "combined_cultural_map.png")
        create_combined_cultural_map(real_data, ai_data, save_path=static_map_path)
        
        # 3. 创建交互式地图
        print("\n=== 创建交互式地图 ===")
        interactive_map_path = os.path.join(results_dir, "combined_cultural_map_interactive.html")
        create_interactive_combined_map(real_data, ai_data, save_path=interactive_map_path)
        
        # 4. 分析对比
        print("\n=== 分析对比 ===")
        analyze_ai_vs_real(real_data, ai_data)
        
        # 5. 保存合并数据
        print("\n=== 保存合并数据 ===")
        if not real_data.empty and not ai_data.empty:
            combined_data = pd.concat([real_data, ai_data], ignore_index=True)
        elif not real_data.empty:
            combined_data = real_data
        else:
            combined_data = ai_data
        
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


