"""
新的LLM国家角色扮演可视化器 - 基于BaseCulturalMapVisualizer
替换原有的复杂LLMCountryRoleplayVisualizer类
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import seaborn as sns

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_cultural_map_visualizer import BaseCulturalMapVisualizer


class LLMCountryRoleplayVisualizer(BaseCulturalMapVisualizer):
    """LLM国家角色扮演可视化器 - 继承基类，专注于角色扮演特定功能"""
    
    def __init__(self, data_path: str = "data", results_path: str = "results"):
        """初始化角色扮演可视化器"""
        super().__init__(data_path, results_path)
        
        # 创建角色扮演专用的结果子目录（统一命名为roleplay_dashboard）
        self.roleplay_results_path = self.results_path / "roleplay_dashboard"
        self.roleplay_results_path.mkdir(exist_ok=True)
        
        # 角色扮演特有的颜色映射
        self.model_region_colors = {
            'US': '#1f77b4',
            'CN': '#ff7f0e',
            'EU': '#2ca02c',
            'Unknown': '#d62728'
        }
        
        # 模型标记映射
        self.model_markers = {
            'US': 'o',      # 圆形
            'CN': 's',      # 方形
            'EU': '^',      # 三角形
            'Unknown': 'D'  # 菱形
        }
    
        # 合并到扩展颜色中
        self.extended_colors.update(self.model_region_colors)
        
        # 📊 统一的可视化格式标准（继承自base）
        # matplotlib格式
        self.REAL_COUNTRY_SIZE = 50      # 真实国家点大小（base标准）
        self.REAL_COUNTRY_ALPHA = 0.7    # 真实国家透明度（base标准）
        self.ROLEPLAY_SIZE = 100         # 角色扮演点大小
        self.ROLEPLAY_ALPHA = 0.8        # 角色扮演透明度
        
        # plotly格式（HTML交互式图表）
        self.PLOTLY_REAL_SIZE = 8        # 真实国家点大小
        self.PLOTLY_REAL_OPACITY = 0.7   # 真实国家透明度（与base一致）
        self.PLOTLY_ROLEPLAY_SIZE = 12   # 角色扮演点大小
        self.PLOTLY_ROLEPLAY_OPACITY = 0.8  # 角色扮演透明度
        
        # 设置样式
        sns.set_style("whitegrid")
    
    def load_data(self) -> pd.DataFrame:
        """加载角色扮演PCA结果数据（从标准路径）"""
        # 标准路径：data/roleplay_English/roleplay_pca_entity_scores_latest.pkl
        roleplay_dir = self.data_path / "roleplay_English"
        
        data_paths = [
            # 1. 优先：最新版本（标准路径）
            roleplay_dir / "roleplay_pca_entity_scores_latest.pkl",
            # 2. 带时间戳的最新文件
            *sorted(roleplay_dir.glob("roleplay_pca_entity_scores_*.pkl"), 
                   key=lambda x: x.stat().st_mtime, reverse=True),
            # 3. 兼容旧路径
            self.data_path / "roleplay_pca_entity_scores.pkl",
            self.data_path / "llm_roleplay_entity_scores.pkl"
        ]
        
        for data_path in data_paths:
            if data_path.exists():
                data = pd.read_pickle(data_path)
                print(f"✅ 加载角色扮演数据: {data_path} - {data.shape}")
                return data
        
        raise FileNotFoundError(
            f"未找到角色扮演数据文件\n"
            f"期望路径: {roleplay_dir / 'roleplay_pca_entity_scores_latest.pkl'}\n"
            f"请先运行PCA分析生成数据"
        )
    
    def _get_point_label(self, row: pd.Series) -> str:
        """获取数据点标签 - 角色扮演特定实现"""
        # 优先使用国家名称
        if 'Country' in row and pd.notna(row['Country']):
            return row['Country']
        elif 'country_name' in row and pd.notna(row['country_name']):
            return row['country_name']
        elif 'model_name' in row and pd.notna(row['model_name']):
            # 对于模型，显示简化名称
            model_name = str(row['model_name'])
            if 'gpt' in model_name.lower():
                return 'GPT'
            elif 'claude' in model_name.lower():
                return 'Claude'
            elif 'gemini' in model_name.lower():
                return 'Gemini'
            elif 'llama' in model_name.lower():
                return 'LLaMA'
            else:
                return model_name[:8]  # 截断长名称
        elif 'country_code' in row and pd.notna(row['country_code']):
            return str(row['country_code'])
        else:
            return ""
    
    def prepare_visualization_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """准备可视化数据，分离真实国家和角色扮演数据"""
        # 分离真实国家数据和角色扮演数据
        if 'data_source' in data.columns:
            real_countries = data[data['data_source'] == 'IVS'].copy()
            # 支持多种角色扮演数据标识
            roleplay_mask = (data['data_source'] == 'Roleplay') | (data['data_source'] == 'llm_roleplay')
            roleplay_data = data[roleplay_mask].copy()
        else:
            # 如果没有data_source列，尝试其他方法区分
            real_countries = data[~data.get('model_name', '').notna()].copy()
            roleplay_data = data[data.get('model_name', '').notna()].copy()
        
        # 为角色扮演数据分配文化区域（如果缺失）
        if not roleplay_data.empty and 'Cultural Region' in roleplay_data.columns:
            missing_regions = roleplay_data['Cultural Region'].isna().sum()
            if missing_regions > 0:
                print(f"🔧 为 {missing_regions} 个角色扮演数据分配文化区域...")
                roleplay_data = self._assign_cultural_regions(roleplay_data)
        
        # 为角色扮演数据添加model_region（如果缺失）
        if not roleplay_data.empty and 'model_region' not in roleplay_data.columns:
            print("🔧 为角色扮演数据添加model_region...")
            roleplay_data = self._assign_model_regions(roleplay_data)
        
        print(f"📊 数据分离完成:")
        print(f"   - 真实国家: {len(real_countries)} 个")
        print(f"   - 角色扮演: {len(roleplay_data)} 个")
        
        return real_countries, roleplay_data
    
    def _assign_cultural_regions(self, roleplay_data: pd.DataFrame) -> pd.DataFrame:
        """为角色扮演数据分配文化区域 - 从配置文件自动加载"""
        # 尝试从配置文件加载完整映射
        country_to_region = self._load_country_cultural_mapping()
        
        # 为缺失的Cultural Region分配值
        for idx, row in roleplay_data.iterrows():
            if pd.isna(row['Cultural Region']) and 'country_code' in row:
                country = row['country_code']
                if country in country_to_region:
                    roleplay_data.at[idx, 'Cultural Region'] = country_to_region[country]
                else:
                    # 如果在配置文件中也找不到，标记为Unknown而不是Other
                    roleplay_data.at[idx, 'Cultural Region'] = 'Unknown'
                    print(f"⚠️ 未找到国家'{country}'的文化区域映射")
        
        return roleplay_data
    
    def _load_country_cultural_mapping(self) -> dict:
        """从配置文件加载国家到文化区域的完整映射"""
        try:
            import json
            from pathlib import Path
            
            # 找到配置文件路径 - 需要到项目根目录
            # data_path = .../data/roleplay_English, parent = .../data, parent.parent = 项目根
            config_path = self.data_path.parent.parent / 'config' / 'country' / 'cultural_regions.json'
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                mapping = config.get('country_cultural_mapping', {})
                print(f"✅ 从配置文件加载了 {len(mapping)} 个国家的文化区域映射")
                return mapping
        except Exception as e:
            print(f"⚠️ 加载文化区域配置失败: {e}，使用默认映射")
            # 返回基本映射作为后备
            return {
                'United States': 'English-Speaking',
                'Brazil': 'Latin America',
                'China': 'Confucian',
                'Spain': 'Catholic Europe',
                'Egypt': 'African-Islamic',
                'France': 'Catholic Europe',
                'Germany': 'Protestant Europe',
                'India': 'West & South Asia',
                'Russian Federation': 'Orthodox Europe'
            }
    
    def _assign_model_regions(self, roleplay_data: pd.DataFrame) -> pd.DataFrame:
        """为角色扮演数据分配模型区域"""
        # 模型到区域的映射
        model_to_region = {
            'openai/gpt-4o-mini': 'US',
            'anthropic/claude-3.7-sonnet': 'US',
            'google/gemini-2.0-flash-001': 'US',
            'meta-llama/llama-3.3-70b-instruct': 'US',
            'deepseek/deepseek-chat-v3-0324': 'CN',
            'mistralai/mistral-nemo': 'EU'
        }
        
        # 添加model_region列
        roleplay_data['model_region'] = roleplay_data['model_name'].map(model_to_region).fillna('Unknown')
        
        return roleplay_data
    
    def _get_display_text(self, data_subset: pd.DataFrame) -> list:
        """获取用于显示的文本标签"""
        display_texts = []
        for _, row in data_subset.iterrows():
            # 优先使用非空的Country列，然后是country_code
            if 'Country' in row and pd.notna(row['Country']) and str(row['Country']).strip():
                display_texts.append(str(row['Country']))
            elif 'country_code' in row and pd.notna(row['country_code']):
                display_texts.append(str(row['country_code']))
            else:
                display_texts.append('Unknown')
        return display_texts
    
    def plot_roleplay_overview(self, data: pd.DataFrame = None, 
                              figsize: Tuple[int, int] = (16, 12),
                              save_path: Optional[str] = None) -> plt.Figure:
        """绘制角色扮演总览图"""
        if data is None:
            data = self.load_data()
        
        real_countries, roleplay_data = self.prepare_visualization_data(data)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制真实国家（背景）- 使用base中的标准格式
        if not real_countries.empty:
            for region in real_countries['Cultural Region'].unique():
                if pd.isna(region):
                    continue
                subset = real_countries[real_countries['Cultural Region'] == region]
                color = self.get_color_for_region(region)
                
                # 先添加国家名称标签（像Stage1一样）
                for _, row in subset.iterrows():
                    country_name = self._get_point_label(row)
                    if country_name:
                        # 检查是否为伊斯兰国家（使用较小的字体）
                        if 'Islamic' in subset.columns and row.get('Islamic', False):
                            ax.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                   color=color, fontsize=8, fontstyle='italic', ha='center', va='bottom')
                        else:
                            ax.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                   color=color, fontsize=8, ha='center', va='bottom')
                
                # 再绘制散点
                ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                          label=f"{region} (Real)", color=color, 
                          s=self.REAL_COUNTRY_SIZE, alpha=self.REAL_COUNTRY_ALPHA)
        
        # 绘制角色扮演数据（前景）
        if not roleplay_data.empty:
            for region in roleplay_data['Cultural Region'].unique():
                if pd.isna(region):
                    continue
                subset = roleplay_data[roleplay_data['Cultural Region'] == region]
                color = self.get_color_for_region(region)
                
                # 根据模型区域使用不同标记
                if 'model_region' in subset.columns:
                    model_regions = subset['model_region'].fillna('Unknown').unique()
                else:
                    model_regions = ['Unknown']
                
                for model_region in model_regions:
                    if pd.isna(model_region):
                        model_region = 'Unknown'
                    
                    if 'model_region' in subset.columns:
                        model_subset = subset[subset['model_region'].fillna('Unknown') == model_region]
                    else:
                        model_subset = subset
                    if not model_subset.empty:
                        marker = self.model_markers.get(model_region, 'o')
                        ax.scatter(model_subset['PC1_rescaled'], model_subset['PC2_rescaled'],
                                  label=f"{region} ({model_region})", color=color, 
                                  s=self.ROLEPLAY_SIZE, alpha=self.ROLEPLAY_ALPHA, 
                                  marker=marker, edgecolors='black', linewidth=1)
                        
                        # 添加标签
                        for _, row in model_subset.iterrows():
                            label_text = self._get_point_label(row)
                            if label_text:
                                ax.text(row['PC1_rescaled'], row['PC2_rescaled'], 
                                       label_text, fontsize=8, ha='center', va='bottom')
        
        # 设置图形属性
        ax.set_xlabel('Survival vs. Self-Expression Values', fontsize=12)
        ax.set_ylabel('Traditional vs. Secular Values', fontsize=12)
        ax.set_title('LLM Country Roleplay Cultural Map Overview', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
        plt.tight_layout()
        
        # 保存图形
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 角色扮演总览图已保存到: {save_path}")
        
        return fig
    
    def plot_model_comparison(self, data: pd.DataFrame = None,
                             figsize: Tuple[int, int] = (18, 12),
                             save_path: Optional[str] = None) -> plt.Figure:
        """绘制模型比较图"""
        if data is None:
            data = self.load_data()
        
        real_countries, roleplay_data = self.prepare_visualization_data(data)
        
        if roleplay_data.empty:
            print("⚠️ 没有角色扮演数据可用于模型比较")
            return plt.figure()
        
        # 按模型分组
        models = roleplay_data.get('model_name', pd.Series()).unique()
        n_models = len(models)
        
        if n_models == 0:
            print("⚠️ 没有找到模型信息")
            return plt.figure()
        
        # 计算子图布局
        cols = min(3, n_models)
        rows = (n_models + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        if n_models == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes.reshape(1, -1)
        
        for i, model in enumerate(models):
            row, col = i // cols, i % cols
            ax = axes[row, col] if rows > 1 else axes[col]
            
            # 绘制真实国家背景 - 使用base中的标准格式（按区域上色）
            if not real_countries.empty:
                for region in real_countries['Cultural Region'].unique():
                    if pd.isna(region):
                        continue
                    subset = real_countries[real_countries['Cultural Region'] == region]
                    color = self.get_color_for_region(region)
                    
                    # 添加国家标签（使用更小字体，因为子图较小）
                    for _, row in subset.iterrows():
                        country_name = self._get_point_label(row)
                        if country_name:
                            ax.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                   color=color, fontsize=6, ha='center', va='bottom', alpha=0.6)
                    
                    # 绘制散点（略微降低透明度作为背景）
                    ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'],
                              color=color, s=self.REAL_COUNTRY_SIZE, alpha=0.4, 
                              label=f'{region} (Real)')
            
            # 绘制该模型的角色扮演数据
            model_data = roleplay_data[roleplay_data.get('model_name', '') == model]
            
            for region in model_data['Cultural Region'].unique():
                if pd.isna(region):
                    continue
                subset = model_data[model_data['Cultural Region'] == region]
                color = self.get_color_for_region(region)
                # 使用统一的角色扮演格式
                ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'],
                          label=region, color=color, 
                          s=self.ROLEPLAY_SIZE, alpha=self.ROLEPLAY_ALPHA)
                
                # 添加国家标签
                for _, row in subset.iterrows():
                    label_text = self._get_point_label(row)
                    if label_text:
                        ax.text(row['PC1_rescaled'], row['PC2_rescaled'], 
                               label_text, fontsize=7, ha='center', va='bottom')
            
            ax.set_title(f"{model}", fontsize=10, fontweight='bold')
            ax.set_xlabel('Survival vs. Self-Expression')
            ax.set_ylabel('Traditional vs. Secular')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8)
        
        # 隐藏多余的子图
        for i in range(n_models, rows * cols):
            row, col = i // cols, i % cols
            ax = axes[row, col] if rows > 1 else axes[col]
            ax.set_visible(False)
        
        plt.suptitle('Model Comparison: Cultural Value Positioning', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 保存图形
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 模型比较图已保存到: {save_path}")
        
        return fig
    
    def create_distance_analysis(self, data: pd.DataFrame = None) -> pd.DataFrame:
        """创建距离分析"""
        if data is None:
            data = self.load_data()
        
        real_countries, roleplay_data = self.prepare_visualization_data(data)
        
        if real_countries.empty or roleplay_data.empty:
            print("⚠️ 缺少真实国家或角色扮演数据，无法进行距离分析")
            return pd.DataFrame()
        
        distance_results = []
        
        for _, roleplay_row in roleplay_data.iterrows():
            roleplay_country = roleplay_row.get('country_name', roleplay_row.get('Country', ''))
            if not roleplay_country:
                continue
            
            # 查找对应的真实国家数据
            real_match = real_countries[
                (real_countries.get('Country', '') == roleplay_country) |
                (real_countries.get('country_name', '') == roleplay_country)
            ]
            
            if not real_match.empty:
                real_row = real_match.iloc[0]
                    
                    # 计算欧几里得距离
                distance = np.sqrt(
                    (roleplay_row['PC1_rescaled'] - real_row['PC1_rescaled'])**2 +
                    (roleplay_row['PC2_rescaled'] - real_row['PC2_rescaled'])**2
                )
                
                distance_results.append({
                    'country': roleplay_country,
                    'model_name': roleplay_row.get('model_name', ''),
                    'model_region': roleplay_row.get('model_region', 'Unknown'),
                    'cultural_region': roleplay_row.get('Cultural Region', ''),
                    'distance': distance,
                    'real_pc1': real_row['PC1_rescaled'],
                    'real_pc2': real_row['PC2_rescaled'],
                    'roleplay_pc1': roleplay_row['PC1_rescaled'],
                    'roleplay_pc2': roleplay_row['PC2_rescaled']
                })
        
        distance_df = pd.DataFrame(distance_results)
        
        if not distance_df.empty:
            print(f"📊 距离分析完成: {len(distance_df)} 个比较")
            print(f"   平均距离: {distance_df['distance'].mean():.3f}")
            print(f"   距离范围: [{distance_df['distance'].min():.3f}, {distance_df['distance'].max():.3f}]")
        
        return distance_df
    
    def create_interactive_html_map(self, data: pd.DataFrame = None, save_path: str = None) -> None:
        """创建交互式HTML地图，支持鼠标悬停"""
        if data is None:
            try:
                data = self.load_data()
            except FileNotFoundError as e:
                print(f"❌ 无法加载数据: {e}")
                return
        
        if data.empty:
            print("❌ 数据为空，无法创建交互式地图")
            return
        
        # 使用统一的数据准备方法（包含文化区域分配）
        real_countries, roleplay_entities = self.prepare_visualization_data(data)
        
        # 创建交互式散点图
        fig = go.Figure()
        
        # 添加真实国家数据
        if not real_countries.empty:
            for region in real_countries['Cultural Region'].unique():
                if pd.isna(region):
                    continue
                subset = real_countries[real_countries['Cultural Region'] == region]
                color = self.cultural_region_colors.get(region, '#cccccc')
                
                fig.add_trace(go.Scatter(
                    x=subset['PC1_rescaled'],
                    y=subset['PC2_rescaled'],
                    mode='markers',
                    name=f'{region} (Real Countries)',
                    marker=dict(
                        color=color,
                        size=self.PLOTLY_REAL_SIZE,          # 使用统一标准
                        opacity=self.PLOTLY_REAL_OPACITY,    # 使用统一标准
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate=(
                        '<b>%{text}</b><br>' +
                        'Cultural Region: ' + str(region) + '<br>' +
                        'Type: Real Country<br>' +
                        'PC1: %{x:.3f}<br>' +
                        'PC2: %{y:.3f}<br>' +
                        '<extra></extra>'
                    ),
                    text=self._get_display_text(subset),
                    showlegend=True
                ))
        
        # 添加角色扮演实体数据
        if not roleplay_entities.empty and 'model_name' in roleplay_entities.columns:
            for model in roleplay_entities['model_name'].unique():
                if pd.isna(model):
                    continue
                model_subset = roleplay_entities[roleplay_entities['model_name'] == model]
                
                for region in model_subset['Cultural Region'].unique():
                    if pd.isna(region):
                        continue
                    culture_subset = model_subset[model_subset['Cultural Region'] == region]
                    
                    if len(culture_subset) > 0:
                        base_color = self.cultural_region_colors.get(region, '#cccccc')
                        
                        fig.add_trace(go.Scatter(
                            x=culture_subset['PC1_rescaled'],
                            y=culture_subset['PC2_rescaled'],
                            mode='markers',
                            name=f'{region} ({model})',
                            marker=dict(
                                color=base_color,
                                size=self.PLOTLY_ROLEPLAY_SIZE,        # 使用统一标准
                                opacity=self.PLOTLY_ROLEPLAY_OPACITY,  # 使用统一标准
                                symbol='diamond',
                                line=dict(width=1, color='black')
                            ),
                            hovertemplate=(
                                '<b>%{text}</b><br>' +
                                'Cultural Region: ' + str(region) + '<br>' +
                                'Model: ' + str(model) + '<br>' +
                                'Type: Roleplay<br>' +
                                'PC1: %{x:.3f}<br>' +
                                'PC2: %{y:.3f}<br>' +
                                '<extra></extra>'
                            ),
                            text=self._get_display_text(culture_subset),
                            showlegend=True
                        ))
        
        # 设置布局
        fig.update_layout(
            title="Interactive LLM Country Roleplay Cultural Map",
            xaxis_title="PC1 (Rescaled)",
            yaxis_title="PC2 (Rescaled)",
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
            save_path = self.roleplay_results_path / "interactive_roleplay_map.html"
        
        pyo.plot(fig, filename=str(save_path), auto_open=False)
        print(f"📊 交互式地图已保存到: {save_path}")
    
    def create_cultural_region_html_maps(self, data: pd.DataFrame = None) -> None:
        """为每个文化区域创建单独的交互式HTML地图"""
        if data is None:
            try:
                data = self.load_data()
            except FileNotFoundError as e:
                print(f"❌ 无法加载数据: {e}")
                return
        
        if data.empty:
            print("❌ 数据为空，无法创建文化区域地图")
            return
        
        # 使用统一的数据准备方法（包含文化区域分配）
        real_countries, roleplay_entities = self.prepare_visualization_data(data)
        
        # 获取所有文化区域
        all_regions = set()
        if not real_countries.empty:
            all_regions.update(real_countries['Cultural Region'].dropna().unique())
        if not roleplay_entities.empty:
            all_regions.update(roleplay_entities['Cultural Region'].dropna().unique())
        
        for region in all_regions:
            print(f"📊 创建 {region} 区域的交互式地图...")
            
            # 创建单个区域的图表
            fig = go.Figure()
            
            # 添加该区域的真实国家
            if not real_countries.empty:
                region_real = real_countries[real_countries['Cultural Region'] == region]
                if len(region_real) > 0:
                    color = self.cultural_region_colors.get(region, '#cccccc')
                    fig.add_trace(go.Scatter(
                        x=region_real['PC1_rescaled'],
                        y=region_real['PC2_rescaled'],
                        mode='markers',
                        name=f'{region} (Real Countries)',
                        marker=dict(
                            color=color, 
                            size=self.PLOTLY_REAL_SIZE,        # 使用统一标准
                            opacity=self.PLOTLY_REAL_OPACITY   # 使用统一标准
                        ),
                        text=self._get_display_text(region_real),
                        hovertemplate='<b>%{text}</b><br>Type: Real Country<br>PC1: %{x:.3f}<br>PC2: %{y:.3f}<extra></extra>'
                    ))
            
            # 添加该区域的角色扮演数据
            if not roleplay_entities.empty:
                region_roleplay = roleplay_entities[roleplay_entities['Cultural Region'] == region]
                if len(region_roleplay) > 0 and 'model_name' in region_roleplay.columns:
                    for model in region_roleplay['model_name'].unique():
                        if pd.isna(model):
                            continue
                        model_data = region_roleplay[region_roleplay['model_name'] == model]
                        color = self.cultural_region_colors.get(region, '#cccccc')
                        
                        fig.add_trace(go.Scatter(
                            x=model_data['PC1_rescaled'],
                            y=model_data['PC2_rescaled'],
                            mode='markers',
                            name=f'{region} ({model})',
                            marker=dict(
                                color=color, 
                                size=self.PLOTLY_ROLEPLAY_SIZE,        # 使用统一标准
                                opacity=self.PLOTLY_ROLEPLAY_OPACITY,  # 使用统一标准
                                symbol='diamond'
                            ),
                            text=self._get_display_text(model_data),
                            hovertemplate=f'<b>%{{text}}</b><br>Model: {model}<br>Type: Roleplay<br>PC1: %{{x:.3f}}<br>PC2: %{{y:.3f}}<extra></extra>'
                        ))
            
            # 设置布局
            safe_region_name = region.replace('/', '_').replace(' ', '_')
            fig.update_layout(
                title=f"Interactive Cultural Map - {region}",
                xaxis_title="PC1 (Rescaled)",
                yaxis_title="PC2 (Rescaled)",
                width=1000,
                height=700,
                hovermode='closest'
            )
            
            # 保存文件
            save_path = self.roleplay_results_path / f"interactive_map_{safe_region_name}.html"
            pyo.plot(fig, filename=str(save_path), auto_open=False)
            print(f"   ✅ 已保存到: {save_path.name}")
    
    def create_all_interactive_maps(self, data: pd.DataFrame = None) -> None:
        """创建所有交互式地图"""
        print("🌐 创建交互式HTML地图...")
        
        if data is None:
            try:
                data = self.load_data()
            except FileNotFoundError as e:
                print(f"❌ 无法加载数据: {e}")
                return
        
        # 1. 创建总览交互式地图
        print("\n1️⃣ 创建总览交互式地图...")
        overview_path = self.roleplay_results_path / "interactive_roleplay_overview.html"
        self.create_interactive_html_map(data, save_path=str(overview_path))
        
        # 2. 创建各文化区域的交互式地图
        print("\n2️⃣ 创建各文化区域交互式地图...")
        self.create_cultural_region_html_maps(data)
        
        print("\n✅ 所有交互式HTML地图创建完成！")
    
    def run_full_visualization(self, data: pd.DataFrame = None) -> None:
        """运行完整的可视化流程"""
        print("🚀 开始LLM国家角色扮演可视化...")
        
        if data is None:
            try:
                data = self.load_data()
            except FileNotFoundError as e:
                print(f"❌ 无法加载数据: {e}")
                return
        
        if data.empty:
            print("❌ 数据为空，无法进行可视化")
            return
        
        try:
            # 1. 角色扮演总览
            print("\n1. 生成角色扮演总览图...")
            overview_path = self.roleplay_results_path / "roleplay_cultural_map_overview.png"
            self.plot_roleplay_overview(data, save_path=str(overview_path))
            
            # 2. 模型比较
            print("\n2. 生成模型比较图...")
            comparison_path = self.roleplay_results_path / "roleplay_model_comparison.png"
            self.plot_model_comparison(data, save_path=str(comparison_path))
            
            # 3. 基础文化地图（使用基类方法）
            print("\n3. 生成基础文化地图...")
            basic_map_path = self.roleplay_results_path / "roleplay_basic_cultural_map.png"
            self.plot_basic_cultural_map(data, title="Roleplay Cultural Map", save_path=str(basic_map_path))
            
            # 4. 距离分析
            print("\n4. 进行距离分析...")
            distance_df = self.create_distance_analysis(data)
            if not distance_df.empty:
                distance_csv_path = self.roleplay_results_path / "roleplay_distance_analysis.csv"
                distance_df.to_csv(distance_csv_path, index=False, encoding='utf-8')
                print(f"📊 距离分析数据已保存到: {distance_csv_path}")
            
            # 5. 创建交互式HTML地图
            print("\n5. 创建交互式HTML地图...")
            self.create_all_interactive_maps(data)
            
            print("\n✅ 角色扮演可视化完成！")
            print(f"📁 结果保存在: {self.roleplay_results_path}")
            print(f"📊 包含PNG图片和交互式HTML地图")
            
        except Exception as e:
            print(f"❌ 可视化过程中出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数 - 测试新架构的角色扮演可视化"""
    print("🔄 使用新架构运行角色扮演可视化...")
    
    # 创建可视化器
    visualizer = LLMCountryRoleplayVisualizer()
    
    try:
        # 运行完整可视化
        visualizer.run_full_visualization()
        
        print(f"\n✅ 新架构角色扮演可视化完成！")
        
    except Exception as e:
        print(f"❌ 可视化失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
