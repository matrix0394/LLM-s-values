import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import os
import sys
from pathlib import Path

# 添加项目路径以使用base模块
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_cultural_map_visualizer import BaseCulturalMapVisualizer


class CulturalMapVisualizer(BaseCulturalMapVisualizer):
    """Country Values可视化器 - 继承统一的base类"""
    
    def __init__(self, data_path="../data", results_path="../results"):
        """初始化可视化器"""
        super().__init__(data_path=data_path, results_path=results_path)
        # 使用继承自base的统一颜色方案
        # self.cultural_region_colors 已经由父类定义
    
    def load_data(self) -> pd.DataFrame:
        """实现抽象方法 - 加载国家分数数据"""
        return self.load_country_scores()
    
    def load_country_scores(self):
        """加载国家分数数据"""
        country_scores_path = os.path.join(str(self.data_path), "country_scores_pca.pkl")
        return pd.read_pickle(country_scores_path)
    
    def plot_cultural_map(self, country_scores_pca=None, figsize=(14, 10), save_path=None):
        """
        绘制文化地图 - 使用base的方法，添加伊斯兰国家标注
        """
        if country_scores_pca is None:
            country_scores_pca = self.load_country_scores()
        
        # 使用base的基础绘图方法
        fig = self.plot_basic_cultural_map(
            data=country_scores_pca,
            figsize=figsize,
            title='Inglehart-Welzel Cultural Map',
            show_labels=False,  # 我们自己添加标签以支持伊斯兰标注
            save_path=None  # 先不保存
        )
        
        # 添加国家名称标签（支持伊斯兰国家的斜体标注）
        ax = plt.gca()
        for region, color in self.cultural_region_colors.items():
            subset = country_scores_pca[country_scores_pca['Cultural Region'] == region]
            if len(subset) > 0:
                for _, row in subset.iterrows():
                    if 'Islamic' in country_scores_pca.columns and row['Islamic']:
                        ax.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                               color=color, fontsize=10, fontstyle='italic')
                    else:
                        ax.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                               color=color, fontsize=10)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Cultural map saved to {save_path}")
        
        plt.show()
        return fig
    
    def plot_decision_boundary(self, country_scores_pca=None, figsize=(14, 10), save_path=None):
        """
        绘制决策边界 - 直接使用base的方法
        """
        if country_scores_pca is None:
            country_scores_pca = self.load_country_scores()
        
        # 直接使用base类的决策边界方法
        fig = super().plot_decision_boundary(
            data=country_scores_pca,
            target_column='Cultural Region',
            figsize=figsize,
            save_path=save_path
        )
        
        plt.show()
        return fig
    
    def create_summary_statistics(self, country_scores_pca=None):
        """
        创建汇总统计信息
        """
        if country_scores_pca is None:
            country_scores_pca = self.load_country_scores()
        
        print("=== Cultural Map Summary Statistics ===")
        print(f"Total countries: {len(country_scores_pca)}")
        
        if 'Cultural Region' in country_scores_pca.columns:
            print("\nCountries by Cultural Region:")
            region_counts = country_scores_pca['Cultural Region'].value_counts()
            for region, count in region_counts.items():
                print(f"  {region}: {count}")
        
        print("\nPrincipal Component Statistics:")
        print(f"PC1 (Survival vs. Self-Expression) range: [{country_scores_pca['PC1_rescaled'].min():.2f}, {country_scores_pca['PC1_rescaled'].max():.2f}]")
        print(f"PC2 (Traditional vs. Secular) range: [{country_scores_pca['PC2_rescaled'].min():.2f}, {country_scores_pca['PC2_rescaled'].max():.2f}]")
        
        return country_scores_pca.describe()

def main():
    """
    测试可视化模块
    """
    print("=== 测试可视化模块 ===")
    
    # 确保results目录存在
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # 初始化可视化器
    visualizer = CulturalMapVisualizer()
    
    try:
        # 1. 加载国家分数数据
        print("\n1. 加载国家分数数据...")
        country_scores_path = os.path.join(visualizer.data_path, "country_scores_pca.pkl")
        if os.path.exists(country_scores_path):
            country_scores_pca = visualizer.load_country_scores()
            print(f"成功加载国家分数数据: {len(country_scores_pca)} 个国家")
        else:
            print("错误: country_scores_pca.pkl 不存在，请先运行pca_analysis.py")
            return
        
        # 2. 绘制文化地图
        print("\n2. 绘制文化地图...")
        cultural_map_path = os.path.join(results_dir, "cultural_map_test.png")
        visualizer.plot_cultural_map(save_path=cultural_map_path)
        print(f"文化地图已保存到: {cultural_map_path}")
        
        # 3. 绘制决策边界
        print("\n3. 绘制决策边界...")
        decision_boundary_path = os.path.join(results_dir, "decision_boundary_test.png")
        visualizer.plot_decision_boundary(save_path=decision_boundary_path)
        print(f"决策边界图已保存到: {decision_boundary_path}")
        
        # 4. 生成汇总统计
        print("\n4. 生成汇总统计...")
        summary_stats = visualizer.create_summary_statistics()
        print("\n汇总统计:")
        print(summary_stats)
        
        # 5. 显示文化区域分布
        if 'Cultural Region' in country_scores_pca.columns:
            print("\n5. 文化区域分布:")
            region_counts = country_scores_pca['Cultural Region'].value_counts()
            for region, count in region_counts.items():
                color = visualizer.cultural_region_colors.get(region, '#000000')
                print(f"  {region}: {count} 个国家 (颜色: {color})")
        
        print("\n可视化测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()