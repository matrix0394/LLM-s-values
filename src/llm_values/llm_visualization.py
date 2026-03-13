"""
LLM文化地图可视化器
继承country_values的可视化器以保持完全一致的风格
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.country_values.visualization import CulturalMapVisualizer


class LLMCulturalMapVisualizer(CulturalMapVisualizer):
    """LLM文化地图可视化器 - 继承基类，专注于LLM特定功能"""
    
    def __init__(self, data_path: str = "data", results_path: str = "results"):
        """初始化LLM可视化器
        
        Args:
            data_path: 数据根目录（默认"data"）
            results_path: 结果根目录（默认"results"）
        """
        super().__init__(data_path)
        
        # 配置Stage1专用的子目录
        self.llm_data_dir = Path(data_path) / "llm_values"  # data/llm_values/
        self.llm_results_dir = Path(results_path) / "llm_values" / "llm_dashboard"  # results/llm_values/llm_dashboard/
        
        # 创建结果目录
        self.llm_results_dir.mkdir(parents=True, exist_ok=True)
        
        # 兼容性：保留results_path属性
        self.results_path = self.llm_results_dir
        
        # 颜色映射已在BaseCulturalMapVisualizer中定义（llm_model_colors）
        # 通过get_color_for_model()方法统一获取 ✅
    
    def load_data(self) -> pd.DataFrame:
        """
        加载LLM+IVS的PCA结果数据（Stage1专用路径）
        
        期望文件：data/llm_values/llm_pca_entity_scores.pkl
        由llm_pca_analysis.py生成
        """
        # Stage1专用路径
        standard_path = self.llm_data_dir / "llm_pca_entity_scores.pkl"
        
        if standard_path.exists():
            data = pd.read_pickle(standard_path)
            print(f"✅ 加载PCA结果数据: {standard_path}")
            print(f"   - 实体数量: {len(data)}")
            
            # 检查LLM数据
            if 'is_llm' in data.columns:
                llm_count = data['is_llm'].sum()
                print(f"   - LLM模型数量: {llm_count}")
            elif 'data_source' in data.columns:
                llm_count = (data['data_source'] == 'LLM').sum()
                print(f"   - LLM模型数量: {llm_count}")
            
            return data
        else:
            raise FileNotFoundError(
                f"未找到PCA结果文件: {standard_path}\n"
                f"提示：请先运行 llm_pca_analysis.py 生成PCA结果"
            )
    
    def _split_llm_and_country_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """分离LLM和国家数据
        
        Args:
            data: 包含LLM和国家数据的DataFrame
            
        Returns:
            (country_data, llm_data)
        """
        if 'data_source' in data.columns:
            country_data = data[data['data_source'] == 'IVS']
            llm_data = data[data['data_source'] == 'LLM']
        elif 'is_llm' in data.columns:
            country_data = data[data['is_llm'] == False]
            llm_data = data[data['is_llm'] == True]
        else:
            country_data = data[data['Cultural Region'] != 'AI Model']
            llm_data = data[data['Cultural Region'] == 'AI Model']
        
        return country_data, llm_data
    
    def _get_point_label(self, row: pd.Series) -> str:
        """获取数据点的标签文本 - 重写以支持LLM"""
        # 优先使用Country，然后是model_name，最后是提取的模型名
        if 'Country' in row.index and pd.notna(row['Country']):
            return str(row['Country'])
        elif 'model_name' in row.index and pd.notna(row['model_name']):
            return str(row['model_name'])
        elif 'extracted_model' in row.index and pd.notna(row['extracted_model']):
            return str(row['extracted_model'])
        elif 'country_code' in row.index and str(row['country_code']).startswith('LLM_'):
            return str(row['country_code']).replace('LLM_', '')
        else:
            return ""
    
    def plot_llm_vs_countries(self, data: pd.DataFrame = None,
                             figsize: Tuple[int, int] = (14, 10),
                             save_path: Optional[str] = None) -> plt.Figure:
        """绘制LLM与国家的对比图 - 完全按照country_values的风格
        
        Args:
            data: 数据，如果为None则自动加载
            figsize: 图形大小
            save_path: 保存路径
            
        Returns:
            matplotlib Figure对象
        """
        if data is None:
            data = self.load_data()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 分离LLM和国家数据
        country_data, llm_data = self._split_llm_and_country_data(data)
        
        # 绘制国家数据 - 完全按照country_values的风格
        for region, color in self.cultural_region_colors.items():
            subset = country_data[country_data['Cultural Region'] == region]
            if len(subset) > 0:
                # 添加国家名称标签 - 完全按照country_values的方式
                for i, row in subset.iterrows():
                    country_name = self._get_point_label(row)
                    if country_name:
                        if 'Islamic' in subset.columns and row['Islamic']:
                            ax.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                    color=color, fontsize=10, fontstyle='italic')
                        else:
                            ax.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                    color=color, fontsize=10)
                
                # 创建基于文化区域的散点图 - 完全按照country_values的方式
                ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                           label=region, color=color, s=50, alpha=0.7)
        
        # 绘制LLM数据（使用不同的标记和颜色）
        if not llm_data.empty:
            print(f"  🤖 绘制{len(llm_data)}个LLM模型...")
            for _, row in llm_data.iterrows():
                model_name = self._get_point_label(row)
                # 使用base的统一颜色方法
                color = self.get_color_for_model(model_name)
                
                # 使用星形标记区分LLM
                ax.scatter(row['PC1_rescaled'], row['PC2_rescaled'], 
                           color=color, s=200, alpha=0.9, marker='*', 
                           edgecolors='black', linewidth=1.5,
                           label=f"LLM: {model_name}" if len(llm_data) <= 10 else None)
                
                # 添加模型标签
                ax.text(row['PC1_rescaled'], row['PC2_rescaled'], model_name, 
                        color=color, fontsize=10, fontweight='bold',
                        ha='center', va='bottom')
                print(f"    ✓ {model_name}: ({row['PC1_rescaled']:.2f}, {row['PC2_rescaled']:.2f})")
        else:
            print(f"  ⚠️ 没有LLM数据可绘制！")
        
        ax.set_xlabel('Survival vs. Self-Expression Values')
        ax.set_ylabel('Traditional vs. Secular Values')
        ax.set_title('Inglehart-Welzel Cultural Map with LLM Models')
        
        # 添加图例 - 完全按照country_values的方式
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 LLM对比图已保存到: {save_path}")
        
        return fig
    
    def plot_model_comparison(self, data: pd.DataFrame = None,
                             figsize: Tuple[int, int] = (14, 10),
                             save_path: Optional[str] = None) -> plt.Figure:
        """绘制不同LLM模型的对比
        
        Args:
            data: 数据
            figsize: 图形大小
            save_path: 保存路径
            
        Returns:
            matplotlib Figure对象
        """
        if data is None:
            data = self.load_data()
        
        # 筛选LLM数据
        _, llm_data = self._split_llm_and_country_data(data)
        
        if llm_data.empty:
            print("⚠️ 未找到LLM数据")
            return plt.figure()
        
        return self.create_comparison_plot(
            llm_data, 
            'extracted_model' if 'extracted_model' in llm_data.columns else 'model_name',
            figsize=figsize,
            save_path=save_path
        )
    
    def create_llm_dashboard(self, data: pd.DataFrame = None,
                           save_dir: Optional[str] = None) -> Dict[str, str]:
        """创建LLM分析仪表板（Stage1专用）
        
        Args:
            data: 数据，如果为None则自动加载
            save_dir: 保存目录，如果为None则使用results/llm_values/
            
        Returns:
            保存的文件路径字典
        """
        if data is None:
            data = self.load_data()
        
        # 使用Stage1专用结果目录
        if save_dir is None:
            save_dir = self.llm_results_dir  # results/llm_values/
        else:
            save_dir = Path(save_dir)
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        print(f"\n🎨 开始生成Stage1可视化图表...")
        print(f"📁 保存目录: {save_dir}")
        
        # 1. LLM vs 国家对比图（用星形标记区分LLM，最直观）
        print(f"\n1️⃣ 生成LLM vs 国家对比图...")
        fig1 = self.plot_llm_vs_countries(data, figsize=(16, 12))
        path1 = save_dir / "llm_vs_countries.png"
        fig1.savefig(path1, dpi=300, bbox_inches='tight')
        saved_files['llm_vs_countries'] = str(path1)
        plt.close(fig1)
        
        # 2. 基础文化地图（包含所有Cultural Region，包括AI Model）
        print(f"2️⃣ 生成完整文化地图...")
        fig2 = self.plot_basic_cultural_map(
            data, 
            title="Inglehart-Welzel Cultural Map with LLM Models",
            figsize=(16, 12)
        )
        path2 = save_dir / "cultural_map_with_llm.png"
        fig2.savefig(path2, dpi=300, bbox_inches='tight')
        saved_files['cultural_map'] = str(path2)
        plt.close(fig2)
        
        # 3. 模型对比分析
        print(f"3️⃣ 生成模型对比分析...")
        fig3 = self.plot_model_comparison(data, figsize=(14, 10))
        path3 = save_dir / "model_comparison.png"
        fig3.savefig(path3, dpi=300, bbox_inches='tight')
        saved_files['model_comparison'] = str(path3)
        plt.close(fig3)
        
        print(f"\n✅ Stage1可视化完成！共保存 {len(saved_files)} 个图形到: {save_dir}")
        return saved_files


def main():
    """主函数 - 运行LLM可视化"""
    data_path = "data"
    results_path = "results"
    
    print("🔄 使用新架构运行LLM可视化...")
    
    # 创建可视化器
    visualizer = LLMCulturalMapVisualizer(data_path, results_path)
    
    try:
        # 创建仪表板
        saved_files = visualizer.create_llm_dashboard()
        
        print(f"\n🎉 LLM可视化完成！")
        print("📊 生成的图形:")
        for name, path in saved_files.items():
            print(f"   - {name}: {path}")
        
        return saved_files
        
    except Exception as e:
        print(f"❌ 可视化失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
