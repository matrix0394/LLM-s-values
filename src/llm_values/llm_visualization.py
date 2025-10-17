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
        """初始化LLM可视化器"""
        super().__init__(data_path)
        self.results_path = Path(results_path)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        # 添加LLM特定的颜色映射
        self.llm_colors = {
            'anthropic': '#ff1493',    # 深粉色
            'openai': '#ff4500',       # 橙红色
            'google': '#4285f4',       # 谷歌蓝
            'meta-llama': '#1877f2',   # Facebook蓝
            'deepseek': '#8b00ff',     # 紫色
            'qwen': '#ff6b35',         # 橙色
            'mistralai': '#ff69b4',    # 热粉色
        }
    
    def load_data(self) -> pd.DataFrame:
        """加载LLM+IVS的PCA结果数据"""
        # 尝试多个可能的数据路径
        data_path = Path(self.data_path)
        data_paths = [
            data_path / "llm_pca_entity_scores.pkl",
            data_path / "entity_scores_pca.pkl", 
            data_path / "pca_results_with_llm.pkl",
            data_path / "country_scores_pca.pkl"
        ]
        
        for file_path in data_paths:
            if file_path.exists():
                data = pd.read_pickle(file_path)
                print(f"✅ 加载数据: {file_path} - {data.shape}")
                return data
        
        raise FileNotFoundError(f"未找到数据文件，尝试的路径: {[str(p) for p in data_paths]}")
    
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
        
        plt.figure(figsize=figsize)
        
        # 分离LLM和国家数据
        if 'data_source' in data.columns:
            country_data = data[data['data_source'] == 'IVS']
            llm_data = data[data['data_source'] == 'LLM']
        else:
            # 根据Cultural Region判断
            country_data = data[data['Cultural Region'] != 'AI Model']
            llm_data = data[data['Cultural Region'] == 'AI Model']
        
        # 绘制国家数据 - 完全按照country_values的风格
        for region, color in self.cultural_region_colors.items():
            subset = country_data[country_data['Cultural Region'] == region]
            if len(subset) > 0:
                # 添加国家名称标签 - 完全按照country_values的方式
                for i, row in subset.iterrows():
                    country_name = self._get_point_label(row)
                    if country_name:
                        if 'Islamic' in subset.columns and row['Islamic']:
                            plt.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                    color=color, fontsize=10, fontstyle='italic')
                        else:
                            plt.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                    color=color, fontsize=10)
                
                # 创建基于文化区域的散点图 - 完全按照country_values的方式
                plt.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                           label=region, color=color, s=50, alpha=0.7)
        
        # 绘制LLM数据（使用不同的标记和颜色）
        if not llm_data.empty:
            for _, row in llm_data.iterrows():
                model_name = self._get_point_label(row)
                # 根据模型提供商选择颜色
                provider = model_name.split('/')[0] if '/' in model_name else model_name.split('-')[0]
                color = self.llm_colors.get(provider, '#ff1493')
                
                # 使用星形标记区分LLM
                plt.scatter(row['PC1_rescaled'], row['PC2_rescaled'], 
                           color=color, s=200, alpha=0.9, marker='*', 
                           edgecolors='black', linewidth=1.5,
                           label=f"LLM: {model_name}" if len(llm_data) <= 10 else None)
                
                # 添加模型标签
                plt.text(row['PC1_rescaled'], row['PC2_rescaled'], model_name, 
                        color=color, fontsize=10, fontweight='bold',
                        ha='center', va='bottom')
        
        plt.xlabel('Survival vs. Self-Expression Values')
        plt.ylabel('Traditional vs. Secular Values')
        plt.title('Inglehart-Welzel Cultural Map with LLM Models')
        
        # 添加图例 - 完全按照country_values的方式
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 LLM对比图已保存到: {save_path}")
        
        plt.show()
        return plt.gcf()
    
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
        if 'is_llm' in data.columns:
            llm_data = data[data['is_llm'] == True]
        elif 'data_source' in data.columns:
            llm_data = data[data['data_source'] == 'LLM']
        else:
            llm_data = data[data['Cultural Region'] == 'AI Model']
        
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
        """创建LLM分析仪表板
        
        Args:
            data: 数据
            save_dir: 保存目录
            
        Returns:
            保存的文件路径字典
        """
        if data is None:
            data = self.load_data()
        
        if save_dir is None:
            save_dir = self.results_path / "llm_dashboard"
        else:
            save_dir = Path(save_dir)
        
        save_dir.mkdir(exist_ok=True)
        
        saved_files = {}
        
        # 1. 基础文化地图
        fig1 = self.plot_basic_cultural_map(
            data, 
            title="Cultural Map with LLM Models",
            figsize=(16, 12)
        )
        path1 = save_dir / "cultural_map_with_llm.png"
        fig1.savefig(path1, dpi=300, bbox_inches='tight')
        saved_files['cultural_map'] = str(path1)
        plt.close(fig1)
        
        # 2. LLM vs 国家对比
        fig2 = self.plot_llm_vs_countries(data, figsize=(16, 12))
        path2 = save_dir / "llm_vs_countries.png"
        fig2.savefig(path2, dpi=300, bbox_inches='tight')
        saved_files['llm_comparison'] = str(path2)
        plt.close(fig2)
        
        # 3. 模型对比分析
        fig3 = self.plot_model_comparison(data, figsize=(14, 10))
        path3 = save_dir / "model_comparison.png"
        fig3.savefig(path3, dpi=300, bbox_inches='tight')
        saved_files['model_analysis'] = str(path3)
        plt.close(fig3)
        
        # 4. 决策边界 - 暂时注释掉，避免NaN值问题
        # if 'Cultural Region' in data.columns:
        #     fig4 = self.plot_decision_boundary(data, figsize=(14, 10))
        #     path4 = save_dir / "decision_boundaries.png"
        #     fig4.savefig(path4, dpi=300, bbox_inches='tight')
        #     saved_files['decision_boundary'] = str(path4)
        #     plt.close(fig4)
        
        print(f"📊 LLM仪表板已创建，共保存 {len(saved_files)} 个图形到: {save_dir}")
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
