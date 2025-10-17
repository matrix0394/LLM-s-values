import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import os

class CulturalMapVisualizer:
    def __init__(self, data_path="../data"):
        self.data_path = data_path
        self.cultural_region_colors = {
            'African-Islamic': '#000000',      # 黑色 - 与cultural_regions.json一致
            'Confucian': '#56b4e9',           # 蓝色
            'Latin America': '#cc79a7',       # 粉色
            'Protestant Europe': '#d55e00',   # 橙红色
            'Catholic Europe': '#e69f00',     # 橙色
            'English-Speaking': '#009e73',    # 绿色
            'Orthodox Europe': '#0072b2',     # 深蓝色
            'West & South Asia': '#f0e442',   # 黄色
        }
    
    def load_country_scores(self):
        """
        加载国家分数数据
        """
        country_scores_path = os.path.join(self.data_path, "country_scores_pca.pkl")
        return pd.read_pickle(country_scores_path)
    
    def plot_cultural_map(self, country_scores_pca=None, figsize=(14, 10), save_path=None):
        """
        绘制文化地图
        参考7-pca-db.ipynb的实现
        """
        if country_scores_pca is None:
            country_scores_pca = self.load_country_scores()
        
        plt.figure(figsize=figsize)
        
        # 为每个文化区域绘制对应颜色和样式的点
        for region, color in self.cultural_region_colors.items():
            subset = country_scores_pca[country_scores_pca['Cultural Region'] == region]
            if len(subset) > 0:
                # 添加国家名称标签
                for i, row in subset.iterrows():
                    if 'Islamic' in country_scores_pca.columns and row['Islamic']:
                        plt.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                                color=color, fontsize=10, fontstyle='italic')
                    else:
                        plt.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                                color=color, fontsize=10)
                
                # 创建基于文化区域的散点图
                plt.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                           label=region, color=color, s=50, alpha=0.7)
        
        plt.xlabel('Survival vs. Self-Expression Values')
        plt.ylabel('Traditional vs. Secular Values')
        plt.title('Inglehart-Welzel Cultural Map')
        
        # 添加图例
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Cultural map saved to {save_path}")
        
        plt.show()
    
    def plot_decision_boundary(self, country_scores_pca=None, figsize=(14, 10), save_path=None):
        """
        绘制决策边界
        参考7-pca-db.ipynb的决策边界可视化
        """
        if country_scores_pca is None:
            country_scores_pca = self.load_country_scores()
        
        # 准备训练数据
        vis_data = country_scores_pca.dropna()[["PC1_rescaled", "PC2_rescaled", "Cultural Region"]]
        vis_data['label'] = pd.Categorical(vis_data['Cultural Region']).codes
        
        # 创建颜色映射
        tups = vis_data[['label', 'Cultural Region']].drop_duplicates().sort_values(by='label')
        tups['color'] = tups['Cultural Region'].map(self.cultural_region_colors)
        
        # 处理缺失的颜色映射，使用默认颜色
        tups['color'] = tups['color'].fillna('#808080')  # 灰色作为默认颜色
        
        tups.reset_index(drop=True, inplace=True)
        cmap = mcolors.ListedColormap(tups['color'].values)
        
        # 训练SVM分类器
        X = vis_data[['PC1_rescaled', 'PC2_rescaled']].values
        y = vis_data['label'].values
        
        clf = SVC(kernel='rbf', gamma='scale', C=1.0)
        clf.fit(X, y)
        
        # 创建网格用于绘制决策边界
        h = 0.02  # 网格步长
        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                            np.arange(y_min, y_max, h))
        
        # 预测网格点
        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        
        plt.figure(figsize=figsize)
        
        # 绘制决策边界
        plt.contourf(xx, yy, Z, alpha=0.3, cmap=cmap)
        
        # 绘制数据点
        for region, color in self.cultural_region_colors.items():
            subset = country_scores_pca[country_scores_pca['Cultural Region'] == region]
            if len(subset) > 0:
                plt.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                           label=region, color=color, s=50, edgecolors='black', linewidth=0.5)
        
        plt.xlabel('Survival vs. Self-Expression Values')
        plt.ylabel('Traditional vs. Secular Values')
        plt.title('Cultural Map with Decision Boundaries')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Decision boundary plot saved to {save_path}")
        
        plt.show()
    
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