"""
LLM国家角色扮演可视化模块
参考llm_visualization的功能，处理llm_country_roleplay_pca_analysis得到的数据
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import os
from pathlib import Path
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")


class LLMCountryRoleplayVisualizer:
    """LLM国家角色扮演可视化器"""
    
    def __init__(self, data_dir: str = None, results_dir: str = None):
        """初始化可视化器
        
        Args:
            data_dir: 数据目录路径
            results_dir: 结果保存目录路径
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        if results_dir is None:
            results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # 文化区域颜色映射
        self.cultural_region_colors = {
            'African-Islamic': '#cc79a7',
            'Orthodox Europe': '#0072b2',
            'Catholic Europe': '#e69f00',
            'Latin America': '#999999',
            'West & South Asia': '#f0e442',
            'Confucian': '#d55e00',
            'Protestant Europe': '#56b4e9',
            'English-Speaking': '#009e73',
            'Unknown': '#cccccc'
        }
        
        # 模型区域颜色映射
        self.model_region_colors = {
            'US': '#1f77b4',
            'CN': '#ff7f0e',
            'EU': '#2ca02c',
            'Unknown': '#d62728'
        }
        
        # 模型形状映射
        self.model_markers = {
            'US': 'o',      # 圆形
            'CN': 's',      # 方形
            'EU': '^',      # 三角形
            'Unknown': 'D'  # 菱形
        }
    
    def load_roleplay_results(self) -> pd.DataFrame:
        """加载角色扮演PCA分析结果"""
        try:
            # 尝试加载角色扮演实体分数
            entity_scores_path = self.data_dir / "roleplay_entity_scores_pca.pkl"
            if entity_scores_path.exists():
                return pd.read_pickle(entity_scores_path)
            
            # 备选：加载详细PCA结果
            pca_results_path = self.data_dir / "roleplay_pca_results.pkl"
            if pca_results_path.exists():
                return pd.read_pickle(pca_results_path)
            
            raise FileNotFoundError("未找到角色扮演分析结果文件")
            
        except Exception as e:
            print(f"加载角色扮演结果失败: {e}")
            return pd.DataFrame()
    
    def prepare_visualization_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """准备可视化数据，分离真实国家和角色扮演实体"""
        if data.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # 分离真实国家和角色扮演实体
        if 'is_roleplay' in data.columns:
            real_countries = data[data['is_roleplay'] == False].copy()
            roleplay_entities = data[data['is_roleplay'] == True].copy()
        else:
            # 备选方案：根据Country列判断
            real_countries = data[~data['Country'].str.contains('_as_', na=False)].copy()
            roleplay_entities = data[data['Country'].str.contains('_as_', na=False)].copy()
        
        print(f"Real countries: {len(real_countries)}, Roleplay entities: {len(roleplay_entities)}")
        return real_countries, roleplay_entities
    
    def plot_cultural_map_overview(self, data: pd.DataFrame = None, figsize: Tuple[int, int] = (20, 14), 
                                  save_path: str = None, show_labels: bool = False) -> None:
        """绘制文化地图总览，显示真实国家和角色扮演实体"""
            if data is None:
                data = self.load_roleplay_results()
            
            if data.empty:
            print("没有数据可以可视化")
            return
        
        real_countries, roleplay_entities = self.prepare_visualization_data(data)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 1. 绘制真实国家（背景）
        for region, color in self.cultural_region_colors.items():
            subset = real_countries[real_countries['Cultural Region'] == region]
            if len(subset) > 0:
                ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                          label=f'{region} (Real Countries)', color=color, s=60, alpha=0.6, 
                          marker='o', edgecolors='white', linewidth=1)
                
                if show_labels:
                    for _, row in subset.iterrows():
                        ax.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                               fontsize=8, ha='center', va='bottom', alpha=0.7)
        
        # 2. 绘制角色扮演实体（前景）
        if not roleplay_entities.empty:
            for model_region, marker in self.model_markers.items():
                model_subset = roleplay_entities[roleplay_entities['model_region'] == model_region]
                if len(model_subset) > 0:
                    # 按文化区域着色
                    for cultural_region, color in self.cultural_region_colors.items():
                        culture_subset = model_subset[model_subset['Cultural Region'] == cultural_region]
                        if len(culture_subset) > 0:
                            ax.scatter(culture_subset['PC1_rescaled'], culture_subset['PC2_rescaled'],
                                     label=f'{model_region} Model as {cultural_region}', 
                                     color=color, s=100, alpha=0.9, marker=marker,
                                     edgecolors='black', linewidth=1.5)
        
        ax.set_xlabel('Survival vs Self-Expression Values (PC1)', fontsize=14)
        ax.set_ylabel('Traditional vs Secular-Rational Values (PC2)', fontsize=14)
        ax.set_title('LLM Country Roleplay Cultural Map Overview', fontsize=16, fontweight='bold', pad=20)
        
        # 调整图例
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, ncol=1)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"文化地图总览已保存到: {save_path}")
        
        plt.show()
    
    def plot_model_comparison(self, data: pd.DataFrame = None, figsize: Tuple[int, int] = (18, 12), 
                             save_path: str = None) -> None:
        """绘制不同模型的比较图"""
        if data is None:
            data = self.load_roleplay_results()
        
        if data.empty:
            return
        
        _, roleplay_entities = self.prepare_visualization_data(data)
        
        if roleplay_entities.empty:
            print("No roleplay data available for comparison")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Model Comparison in Roleplay Performance', fontsize=16, fontweight='bold')
        
        # 1. 按模型区域分布
        ax1 = axes[0, 0]
        for model_region, color in self.model_region_colors.items():
            subset = roleplay_entities[roleplay_entities['model_region'] == model_region]
            if len(subset) > 0:
                ax1.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'],
                           label=f'{model_region} Models', color=color, s=60, alpha=0.7,
                           marker=self.model_markers.get(model_region, 'o'))
        
        ax1.set_xlabel('PC1 (Survival vs Self-Expression)')
        ax1.set_ylabel('PC2 (Traditional vs Secular-Rational)')
        ax1.set_title('Distribution by Model Origin Region')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 按文化区域分布
        ax2 = axes[0, 1]
        for region, color in self.cultural_region_colors.items():
            subset = roleplay_entities[roleplay_entities['Cultural Region'] == region]
            if len(subset) > 0:
                ax2.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'],
                           label=region, color=color, s=60, alpha=0.7)
        
        ax2.set_xlabel('PC1 (Survival vs Self-Expression)')
        ax2.set_ylabel('PC2 (Traditional vs Secular-Rational)')
        ax2.set_title('Distribution by Roleplayed Cultural Region')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # 3. PC1分布直方图
        ax3 = axes[1, 0]
        for model_region, color in self.model_region_colors.items():
            subset = roleplay_entities[roleplay_entities['model_region'] == model_region]
            if len(subset) > 0:
                ax3.hist(subset['PC1_rescaled'], bins=20, alpha=0.6, label=f'{model_region} Models',
                        color=color, density=True)
        
        ax3.set_xlabel('PC1 (Survival vs Self-Expression)')
        ax3.set_ylabel('Density')
        ax3.set_title('PC1 Distribution Comparison')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. PC2分布直方图
        ax4 = axes[1, 1]
        for model_region, color in self.model_region_colors.items():
            subset = roleplay_entities[roleplay_entities['model_region'] == model_region]
            if len(subset) > 0:
                ax4.hist(subset['PC2_rescaled'], bins=20, alpha=0.6, label=f'{model_region} Models',
                        color=color, density=True)
        
        ax4.set_xlabel('PC2 (Traditional vs Secular-Rational)')
        ax4.set_ylabel('Density')
        ax4.set_title('PC2 Distribution Comparison')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"模型比较图已保存到: {save_path}")
        
        plt.show()
    
    def plot_cultural_region_analysis(self, data: pd.DataFrame = None, figsize: Tuple[int, int] = (16, 20), 
                                     save_path: str = None) -> None:
        """绘制各文化区域的详细分析"""
        if data is None:
            data = self.load_roleplay_results()
        
        if data.empty:
            return
        
        real_countries, roleplay_entities = self.prepare_visualization_data(data)
        
        # 获取所有文化区域
        all_regions = set(data['Cultural Region'].dropna().unique())
        n_regions = len(all_regions)
        
        if n_regions == 0:
            print("No cultural region data available")
            return
        
        # 计算子图布局
        n_cols = 3
        n_rows = (n_regions + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        fig.suptitle('Model Roleplay Analysis by Cultural Region', fontsize=16, fontweight='bold')
        
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        for idx, region in enumerate(sorted(all_regions)):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col]
            
            # 该文化区域的真实国家
            real_subset = real_countries[real_countries['Cultural Region'] == region]
            # 扮演该文化区域的模型
            roleplay_subset = roleplay_entities[roleplay_entities['Cultural Region'] == region]
            
            # 绘制真实国家（背景）
            if len(real_subset) > 0:
                ax.scatter(real_subset['PC1_rescaled'], real_subset['PC2_rescaled'],
                          label='Real Countries', color=self.cultural_region_colors.get(region, '#cccccc'),
                          s=60, alpha=0.5, marker='o', edgecolors='white')
            
            # 绘制不同模型的扮演结果
            if len(roleplay_subset) > 0:
                for model_region, marker in self.model_markers.items():
                    model_subset = roleplay_subset[roleplay_subset['model_region'] == model_region]
                    if len(model_subset) > 0:
                        ax.scatter(model_subset['PC1_rescaled'], model_subset['PC2_rescaled'],
                                  label=f'{model_region} Models', 
                                  color=self.model_region_colors.get(model_region, '#d62728'),
                                  s=80, alpha=0.8, marker=marker, edgecolors='black')
            
            ax.set_title(f'{region}\n(Real:{len(real_subset)}, Roleplay:{len(roleplay_subset)})', 
                        fontsize=11)
            ax.set_xlabel('PC1')
            ax.set_ylabel('PC2')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        # 隐藏多余的子图
        for idx in range(n_regions, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            axes[row, col].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"文化区域分析图已保存到: {save_path}")
        
        plt.show()
    
    def create_distance_analysis(self, data: pd.DataFrame = None) -> pd.DataFrame:
        """分析角色扮演实体与真实国家的距离"""
        if data is None:
            data = self.load_roleplay_results()
        
        if data.empty:
            return pd.DataFrame()
        
        real_countries, roleplay_entities = self.prepare_visualization_data(data)
        
        if real_countries.empty or roleplay_entities.empty:
            print("Missing real countries or roleplay data")
            return pd.DataFrame()
        
        distance_results = []
        
        for _, roleplay_row in roleplay_entities.iterrows():
            # 提取扮演的国家名
            country_name = roleplay_row['Country'].split('_as_')[-1] if '_as_' in roleplay_row['Country'] else None
            cultural_region = roleplay_row['Cultural Region']
            
            if country_name:
                # 找到对应的真实国家
                real_country = real_countries[real_countries['Country'] == country_name]
                if not real_country.empty:
                    real_row = real_country.iloc[0]
                    
                    # 计算欧几里得距离
                    distance = np.sqrt((roleplay_row['PC1_rescaled'] - real_row['PC1_rescaled'])**2 + 
                                     (roleplay_row['PC2_rescaled'] - real_row['PC2_rescaled'])**2)
                    
                    distance_results.append({
                        'model_name': roleplay_row.get('model_name', 'Unknown'),
                        'model_region': roleplay_row.get('model_region', 'Unknown'),
                        'country_name': country_name,
                        'cultural_region': cultural_region,
                        'distance': distance,
                        'roleplay_pc1': roleplay_row['PC1_rescaled'],
                        'roleplay_pc2': roleplay_row['PC2_rescaled'],
                        'real_pc1': real_row['PC1_rescaled'],
                        'real_pc2': real_row['PC2_rescaled']
                    })
            else:
                # 如果无法提取国家名，计算与同文化区域真实国家的平均距离
                same_region_countries = real_countries[real_countries['Cultural Region'] == cultural_region]
                if not same_region_countries.empty:
                    avg_pc1 = same_region_countries['PC1_rescaled'].mean()
                    avg_pc2 = same_region_countries['PC2_rescaled'].mean()
                    
                    distance = np.sqrt((roleplay_row['PC1_rescaled'] - avg_pc1)**2 + 
                                     (roleplay_row['PC2_rescaled'] - avg_pc2)**2)
                    
                    distance_results.append({
                        'model_name': roleplay_row.get('model_name', 'Unknown'),
                        'model_region': roleplay_row.get('model_region', 'Unknown'),
                        'country_name': 'Region_Average',
                        'cultural_region': cultural_region,
                        'distance': distance,
                        'roleplay_pc1': roleplay_row['PC1_rescaled'],
                        'roleplay_pc2': roleplay_row['PC2_rescaled'],
                        'real_pc1': avg_pc1,
                        'real_pc2': avg_pc2
                    })
        
        return pd.DataFrame(distance_results)
    
    def plot_distance_analysis(self, data: pd.DataFrame = None, figsize: Tuple[int, int] = (16, 10), 
                              save_path: str = None) -> None:
        """绘制距离分析图"""
        distance_df = self.create_distance_analysis(data)
        
        if distance_df.empty:
            print("No distance analysis data available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Distance Analysis: Roleplay vs Real Countries', fontsize=16, fontweight='bold')
        
        # 1. 按模型区域的距离分布
        ax1 = axes[0, 0]
        model_distances = []
        model_labels = []
        for model_region in distance_df['model_region'].unique():
            subset = distance_df[distance_df['model_region'] == model_region]
            model_distances.append(subset['distance'].values)
            model_labels.append(f'{model_region} (n={len(subset)})')
        
        ax1.boxplot(model_distances, labels=model_labels)
        ax1.set_title('Distance Distribution by Model Region')
        ax1.set_ylabel('Euclidean Distance')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # 2. 按文化区域的距离分布
        ax2 = axes[0, 1]
        cultural_distances = []
        cultural_labels = []
        for cultural_region in distance_df['cultural_region'].unique():
            subset = distance_df[distance_df['cultural_region'] == cultural_region]
            if len(subset) > 0:
                cultural_distances.append(subset['distance'].values)
                cultural_labels.append(f'{cultural_region[:10]}... (n={len(subset)})')
        
        ax2.boxplot(cultural_distances, labels=cultural_labels)
        ax2.set_title('Distance Distribution by Cultural Region')
        ax2.set_ylabel('Euclidean Distance')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # 3. 距离散点图
        ax3 = axes[1, 0]
        for model_region, color in self.model_region_colors.items():
            subset = distance_df[distance_df['model_region'] == model_region]
            if len(subset) > 0:
                ax3.scatter(subset['real_pc1'], subset['real_pc2'], 
                           label=f'{model_region} Real Position', color=color, s=30, alpha=0.6)
                ax3.scatter(subset['roleplay_pc1'], subset['roleplay_pc2'], 
                           label=f'{model_region} Roleplay Position', color=color, s=60, 
                           marker='x', alpha=0.8)
                
                # 连线显示距离
                for _, row in subset.head(10).iterrows():  # 只显示前10个以避免过于拥挤
                    ax3.plot([row['real_pc1'], row['roleplay_pc1']], 
                            [row['real_pc2'], row['roleplay_pc2']], 
                            color=color, alpha=0.3, linewidth=1)
        
        ax3.set_xlabel('PC1')
        ax3.set_ylabel('PC2')
        ax3.set_title('Real Position vs Roleplay Position')
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 4. 平均距离比较
        ax4 = axes[1, 1]
        avg_distances = distance_df.groupby(['model_region', 'cultural_region'])['distance'].mean().reset_index()
        
        # 创建热力图数据
        heatmap_data = avg_distances.pivot(index='cultural_region', columns='model_region', values='distance')
        
        im = ax4.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
        ax4.set_xticks(range(len(heatmap_data.columns)))
        ax4.set_yticks(range(len(heatmap_data.index)))
        ax4.set_xticklabels(heatmap_data.columns)
        ax4.set_yticklabels(heatmap_data.index)
        ax4.set_title('Average Distance Heatmap')
        
        # 添加数值标注
        for i in range(len(heatmap_data.index)):
            for j in range(len(heatmap_data.columns)):
                if not np.isnan(heatmap_data.iloc[i, j]):
                    ax4.text(j, i, f'{heatmap_data.iloc[i, j]:.2f}', 
                            ha='center', va='center', fontsize=8)
        
        plt.colorbar(im, ax=ax4, shrink=0.8)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"距离分析图已保存到: {save_path}")
        
        plt.show()
        
        return distance_df
    
    def create_interactive_html_map(self, data: pd.DataFrame = None, save_path: str = None) -> None:
        """创建交互式HTML地图，支持鼠标悬停"""
        if data is None:
            data = self.load_roleplay_results()
        
        if data.empty:
            print("No data available for interactive map")
            return
        
        real_countries, roleplay_entities = self.prepare_visualization_data(data)
        
        # 创建交互式散点图
        fig = go.Figure()
        
        # 添加真实国家数据
        for region, color in self.cultural_region_colors.items():
                subset = real_countries[real_countries['Cultural Region'] == region]
            if len(subset) > 0:
                fig.add_trace(go.Scatter(
                    x=subset['PC1_rescaled'],
                    y=subset['PC2_rescaled'],
                    mode='markers',
                    name=f'{region} (Real Countries)',
                    marker=dict(
                        color=color,
                        size=8,
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate=(
                        '<b>%{text}</b><br>' +
                        'Cultural Region: ' + region + '<br>' +
                        'Type: Real Country<br>' +
                        'PC1: %{x:.3f}<br>' +
                        'PC2: %{y:.3f}<br>' +
                        '<extra></extra>'
                    ),
                    text=subset['Country'],
                    showlegend=True
                ))
        
        # 添加角色扮演实体数据
        for model_region in self.model_region_colors.keys():
            model_subset = roleplay_entities[roleplay_entities['model_region'] == model_region]
            if len(model_subset) > 0:
                for cultural_region, color in self.cultural_region_colors.items():
                    culture_subset = model_subset[model_subset['Cultural Region'] == cultural_region]
                    if len(culture_subset) > 0:
                        # 创建悬停文本
                        hover_text = []
                        for _, row in culture_subset.iterrows():
                            country_played = row['Country'].split('_as_')[-1] if '_as_' in row['Country'] else 'Unknown'
                            hover_text.append(
                                f"<b>{row['model_name']} as {country_played}</b><br>" +
                                f"Model Region: {row['model_region']}<br>" +
                                f"Cultural Region: {row['Cultural Region']}<br>" +
                                f"PC1: {row['PC1_rescaled']:.3f}<br>" +
                                f"PC2: {row['PC2_rescaled']:.3f}"
                            )
                
                fig.add_trace(go.Scatter(
                            x=culture_subset['PC1_rescaled'],
                            y=culture_subset['PC2_rescaled'],
                    mode='markers',
                            name=f'{model_region} Model as {cultural_region}',
                    marker=dict(
                                color=color,
                                size=10,
                                opacity=0.9,
                                symbol=self._get_plotly_marker(model_region),
                        line=dict(width=2, color='black')
                    ),
                            hovertemplate='%{text}<extra></extra>',
                            text=hover_text,
                    showlegend=True
                ))
        
        # 更新布局
        fig.update_layout(
            title={
                'text': 'Interactive LLM Country Roleplay Cultural Map',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Survival vs Self-Expression Values (PC1)',
            yaxis_title='Traditional vs Secular-Rational Values (PC2)',
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
            margin=dict(l=50, r=150, t=100, b=50)
        )
        
        # 保存HTML文件
        if save_path is None:
            save_path = self.results_dir / "interactive_roleplay_map.html"
        
        pyo.plot(fig, filename=str(save_path), auto_open=False)
        print(f"Interactive map saved to: {save_path}")
    
    def create_cultural_region_html_maps(self, data: pd.DataFrame = None) -> None:
        """为每个文化区域创建单独的交互式HTML地图"""
        if data is None:
            data = self.load_roleplay_results()
        
        if data.empty:
            print("No data available for cultural region maps")
            return
        
        real_countries, roleplay_entities = self.prepare_visualization_data(data)
        
        # 获取所有文化区域
        all_regions = set(data['Cultural Region'].dropna().unique())
        
        for region in sorted(all_regions):
            # 该文化区域的真实国家
            real_subset = real_countries[real_countries['Cultural Region'] == region]
            # 扮演该文化区域的模型
            roleplay_subset = roleplay_entities[roleplay_entities['Cultural Region'] == region]
            
            if real_subset.empty and roleplay_subset.empty:
                continue
            
            # 创建单独的图表
            fig = go.Figure()
            
            # 添加真实国家
            if len(real_subset) > 0:
                fig.add_trace(go.Scatter(
                    x=real_subset['PC1_rescaled'],
                    y=real_subset['PC2_rescaled'],
                    mode='markers',
                    name='Real Countries',
                    marker=dict(
                        color=self.cultural_region_colors.get(region, '#cccccc'),
                        size=12,
                        opacity=0.7,
                        line=dict(width=2, color='white')
                    ),
                    hovertemplate=(
                        '<b>%{text}</b><br>' +
                        'Type: Real Country<br>' +
                        'Cultural Region: ' + region + '<br>' +
                        'PC1: %{x:.3f}<br>' +
                        'PC2: %{y:.3f}<br>' +
                        '<extra></extra>'
                    ),
                    text=real_subset['Country'],
                    showlegend=True
                ))
            
            # 添加不同模型的扮演结果
            if len(roleplay_subset) > 0:
                for model_region in self.model_region_colors.keys():
                    model_subset = roleplay_subset[roleplay_subset['model_region'] == model_region]
                    if len(model_subset) > 0:
                        # 创建悬停文本
                        hover_text = []
                        for _, row in model_subset.iterrows():
                            country_played = row['Country'].split('_as_')[-1] if '_as_' in row['Country'] else 'Unknown'
                            hover_text.append(
                                f"<b>{row['model_name']} as {country_played}</b><br>" +
                                f"Model Region: {row['model_region']}<br>" +
                                f"Cultural Region: {row['Cultural Region']}<br>" +
                                f"PC1: {row['PC1_rescaled']:.3f}<br>" +
                                f"PC2: {row['PC2_rescaled']:.3f}"
                            )
                        
                        fig.add_trace(go.Scatter(
                            x=model_subset['PC1_rescaled'],
                            y=model_subset['PC2_rescaled'],
                            mode='markers',
                            name=f'{model_region} Models',
                            marker=dict(
                                color=self.model_region_colors.get(model_region, '#d62728'),
                                size=14,
                                opacity=0.9,
                                symbol=self._get_plotly_marker(model_region),
                                line=dict(width=2, color='black')
                            ),
                            hovertemplate='%{text}<extra></extra>',
                            text=hover_text,
                            showlegend=True
                        ))
            
            # 更新布局
            fig.update_layout(
                title={
                    'text': f'Cultural Region: {region}<br>(Real Countries: {len(real_subset)}, Roleplay Entities: {len(roleplay_subset)})',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18}
                },
                xaxis_title='Survival vs Self-Expression Values (PC1)',
                yaxis_title='Traditional vs Secular-Rational Values (PC2)',
                width=1000,
                height=700,
                hovermode='closest',
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                ),
                margin=dict(l=50, r=150, t=100, b=50)
            )
            
            # 保存HTML文件
            safe_region_name = region.replace('/', '_').replace(' ', '_').replace('&', 'and')
            save_path = self.results_dir / f"interactive_map_{safe_region_name}.html"
            
            pyo.plot(fig, filename=str(save_path), auto_open=False)
            print(f"Cultural region map for {region} saved to: {save_path}")
    
    def _get_plotly_marker(self, model_region: str) -> str:
        """获取Plotly标记符号"""
        marker_map = {
            'US': 'circle',
            'CN': 'square',
            'EU': 'triangle-up',
            'Unknown': 'diamond'
        }
        return marker_map.get(model_region, 'circle')
    
    def create_all_interactive_maps(self, data: pd.DataFrame = None) -> None:
        """创建所有交互式地图"""
        print("=== Creating Interactive HTML Maps ===")
        
        if data is None:
            data = self.load_roleplay_results()
        
        if data.empty:
            print("No data available for interactive maps")
            return
        
        try:
            # 1. 创建总览地图
            print("\n1. Creating overview interactive map...")
            overview_path = self.results_dir / "interactive_roleplay_overview.html"
            self.create_interactive_html_map(data, str(overview_path))
            
            # 2. 创建各文化区域的单独地图
            print("\n2. Creating individual cultural region maps...")
            self.create_cultural_region_html_maps(data)
            
            print("\n=== Interactive Maps Creation Completed ===")
            
        except Exception as e:
            print(f"Error creating interactive maps: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_summary_statistics(self, data: pd.DataFrame = None) -> Dict[str, Any]:
        """生成汇总统计信息"""
        if data is None:
            data = self.load_roleplay_results()
        
        if data.empty:
            return {}
        
        real_countries, roleplay_entities = self.prepare_visualization_data(data)
        
        stats = {
            "total_entities": len(data),
            "real_countries": len(real_countries),
            "roleplay_entities": len(roleplay_entities),
            "cultural_regions": len(data['Cultural Region'].unique()),
            "pc1_range": [data['PC1_rescaled'].min(), data['PC1_rescaled'].max()],
            "pc2_range": [data['PC2_rescaled'].min(), data['PC2_rescaled'].max()]
        }
        
        if not roleplay_entities.empty:
            stats["model_regions"] = roleplay_entities['model_region'].value_counts().to_dict()
            stats["models_count"] = len(roleplay_entities['model_name'].unique())
        
        if not real_countries.empty:
            stats["countries_by_cultural_region"] = real_countries['Cultural Region'].value_counts().to_dict()
        
        # 距离分析统计
        distance_df = self.create_distance_analysis(data)
        if not distance_df.empty:
            stats["average_distance"] = distance_df['distance'].mean()
            stats["distance_by_model_region"] = distance_df.groupby('model_region')['distance'].mean().to_dict()
        
        return stats
    
    def run_full_visualization(self, data: pd.DataFrame = None) -> None:
        """运行完整的可视化流程"""
        print("=== Starting LLM Country Roleplay Visualization ===")
        
        if data is None:
            data = self.load_roleplay_results()
        
        if data.empty:
            print("No data available for visualization")
            return
        
        try:
            # 1. 文化地图总览
            print("\n1. Generating cultural map overview...")
            overview_path = self.results_dir / "roleplay_cultural_map_overview.png"
            self.plot_cultural_map_overview(data, save_path=str(overview_path))
            
            # 2. 模型比较
            print("\n2. Generating model comparison...")
            comparison_path = self.results_dir / "roleplay_model_comparison.png"
            self.plot_model_comparison(data, save_path=str(comparison_path))
            
            # 3. 文化区域分析
            print("\n3. Generating cultural region analysis...")
            cultural_analysis_path = self.results_dir / "roleplay_cultural_region_analysis.png"
            self.plot_cultural_region_analysis(data, save_path=str(cultural_analysis_path))
            
            # 4. 距离分析
            print("\n4. Generating distance analysis...")
            distance_path = self.results_dir / "roleplay_distance_analysis.png"
            distance_df = self.plot_distance_analysis(data, save_path=str(distance_path))
            
            # 保存距离分析数据
            if not distance_df.empty:
                distance_csv_path = self.results_dir / "roleplay_distance_analysis.csv"
                distance_df.to_csv(distance_csv_path, index=False, encoding='utf-8')
                print(f"Distance analysis data saved to: {distance_csv_path}")
            
            # 5. 生成汇总统计
            print("\n5. Generating summary statistics...")
            stats = self.generate_summary_statistics(data)
            self._print_summary_statistics(stats)
            
            # 6. 创建交互式HTML地图
            print("\n6. Creating interactive HTML maps...")
            self.create_all_interactive_maps(data)
            
            print("\n=== Visualization Completed ===")
            
        except Exception as e:
            print(f"Error during visualization: {e}")
            import traceback
            traceback.print_exc()
    
    def _print_summary_statistics(self, stats: Dict[str, Any]) -> None:
        """打印汇总统计信息"""
        print("\n=== Visualization Summary Statistics ===")
        print(f"Total entities: {stats.get('total_entities', 0)}")
        print(f"Real countries: {stats.get('real_countries', 0)}")
        print(f"Roleplay entities: {stats.get('roleplay_entities', 0)}")
        print(f"Cultural regions: {stats.get('cultural_regions', 0)}")
        print(f"Number of models: {stats.get('models_count', 0)}")
        
        if 'pc1_range' in stats:
            pc1_min, pc1_max = stats['pc1_range']
            print(f"PC1 range: [{pc1_min:.2f}, {pc1_max:.2f}]")
        
        if 'pc2_range' in stats:
            pc2_min, pc2_max = stats['pc2_range']
            print(f"PC2 range: [{pc2_min:.2f}, {pc2_max:.2f}]")
        
        if 'model_regions' in stats:
            print("\nModel region distribution:")
            for region, count in stats['model_regions'].items():
                print(f"  {region}: {count}")
        
        if 'average_distance' in stats:
            print(f"\nAverage distance: {stats['average_distance']:.3f}")
        
        if 'distance_by_model_region' in stats:
            print("Average distance by model region:")
            for region, distance in stats['distance_by_model_region'].items():
                print(f"  {region}: {distance:.3f}")


def main():
    """主函数"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    
    # 创建可视化器
    visualizer = LLMCountryRoleplayVisualizer(data_dir=data_dir, results_dir=results_dir)
    
    try:
        # 运行完整可视化
        visualizer.run_full_visualization()
        
        print("\n=== Roleplay Visualization Completed Successfully ===")
        
    except Exception as e:
        print(f"Visualization failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
