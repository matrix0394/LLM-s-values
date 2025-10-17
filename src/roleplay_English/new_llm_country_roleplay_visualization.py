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
import seaborn as sns

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_cultural_map_visualizer import BaseCulturalMapVisualizer


class LLMCountryRoleplayVisualizer(BaseCulturalMapVisualizer):
    """LLM国家角色扮演可视化器 - 继承基类，专注于角色扮演特定功能"""
    
    def __init__(self, data_path: str = "data", results_path: str = "results"):
        """初始化角色扮演可视化器"""
        super().__init__(data_path, results_path)
        
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
        
        # 设置样式
        sns.set_style("whitegrid")
    
    def load_data(self) -> pd.DataFrame:
        """加载角色扮演PCA结果数据"""
        # 尝试多个可能的数据路径
        data_paths = [
            self.data_path / "roleplay_pca_entity_scores.pkl",
            self.data_path / "llm_roleplay_entity_scores.pkl",
            self.data_path / "processed" / "roleplay_pca_results.pkl",
            self.data_path / "results" / "roleplay_entity_scores.pkl"
        ]
        
        for data_path in data_paths:
            if data_path.exists():
                data = pd.read_pickle(data_path)
                print(f"✅ 加载角色扮演数据: {data_path} - {data.shape}")
                return data
        
        raise FileNotFoundError(f"未找到角色扮演数据文件，尝试的路径: {[str(p) for p in data_paths]}")
    
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
            roleplay_data = data[data['data_source'] == 'Roleplay'].copy()
        else:
            # 如果没有data_source列，尝试其他方法区分
            real_countries = data[~data.get('model_name', '').notna()].copy()
            roleplay_data = data[data.get('model_name', '').notna()].copy()
        
        print(f"📊 数据分离完成:")
        print(f"   - 真实国家: {len(real_countries)} 个")
        print(f"   - 角色扮演: {len(roleplay_data)} 个")
        
        return real_countries, roleplay_data
    
    def plot_roleplay_overview(self, data: pd.DataFrame = None, 
                              figsize: Tuple[int, int] = (16, 12),
                              save_path: Optional[str] = None) -> plt.Figure:
        """绘制角色扮演总览图"""
        if data is None:
            data = self.load_data()
        
        real_countries, roleplay_data = self.prepare_visualization_data(data)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制真实国家（背景）
        if not real_countries.empty:
            for region in real_countries['Cultural Region'].unique():
                if pd.isna(region):
                    continue
                subset = real_countries[real_countries['Cultural Region'] == region]
                color = self.get_color_for_region(region)
                ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                          label=f"{region} (Real)", color=color, s=30, alpha=0.3)
        
        # 绘制角色扮演数据（前景）
        if not roleplay_data.empty:
            for region in roleplay_data['Cultural Region'].unique():
                if pd.isna(region):
                    continue
                subset = roleplay_data[roleplay_data['Cultural Region'] == region]
                color = self.get_color_for_region(region)
                
                # 根据模型区域使用不同标记
                for model_region in subset.get('model_region', ['Unknown']).unique():
                    if pd.isna(model_region):
                        model_region = 'Unknown'
                    
                    model_subset = subset[subset.get('model_region', 'Unknown') == model_region]
                    if not model_subset.empty:
                        marker = self.model_markers.get(model_region, 'o')
                        ax.scatter(model_subset['PC1_rescaled'], model_subset['PC2_rescaled'],
                                  label=f"{region} ({model_region})", color=color, 
                                  s=100, alpha=0.8, marker=marker, edgecolors='black', linewidth=1)
                        
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
            
            # 绘制真实国家背景
            if not real_countries.empty:
                ax.scatter(real_countries['PC1_rescaled'], real_countries['PC2_rescaled'],
                          c='lightgray', s=20, alpha=0.5, label='Real Countries')
            
            # 绘制该模型的角色扮演数据
            model_data = roleplay_data[roleplay_data.get('model_name', '') == model]
            
            for region in model_data['Cultural Region'].unique():
                if pd.isna(region):
                    continue
                subset = model_data[model_data['Cultural Region'] == region]
                color = self.get_color_for_region(region)
                ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'],
                          label=region, color=color, s=60, alpha=0.8)
                
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
            overview_path = self.results_path / "roleplay_cultural_map_overview.png"
            self.plot_roleplay_overview(data, save_path=str(overview_path))
            
            # 2. 模型比较
            print("\n2. 生成模型比较图...")
            comparison_path = self.results_path / "roleplay_model_comparison.png"
            self.plot_model_comparison(data, save_path=str(comparison_path))
            
            # 3. 基础文化地图（使用基类方法）
            print("\n3. 生成基础文化地图...")
            basic_map_path = self.results_path / "roleplay_basic_cultural_map.png"
            self.plot_basic_cultural_map(data, title="Roleplay Cultural Map", save_path=str(basic_map_path))
            
            # 4. 距离分析
            print("\n4. 进行距离分析...")
            distance_df = self.create_distance_analysis(data)
            if not distance_df.empty:
                distance_csv_path = self.results_path / "roleplay_distance_analysis.csv"
                distance_df.to_csv(distance_csv_path, index=False, encoding='utf-8')
                print(f"📊 距离分析数据已保存到: {distance_csv_path}")
            
            print("\n✅ 角色扮演可视化完成！")
            print(f"📁 结果保存在: {self.results_path}")
            
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














