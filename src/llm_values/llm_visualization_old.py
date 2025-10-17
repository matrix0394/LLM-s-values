import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import os

class LLMCulturalMapVisualizer:
    def __init__(self, data_path="../data"):
        self.data_path = data_path
        # 扩展文化区域颜色，包含AI Model
        self.cultural_region_colors = {
            'Africa-Islamic': '#cc79a7',
            'African-Islamic': '#cc79a7',  # 兼容两种命名
            'South Asia': '#56b4e9',
            'West & South Asia': '#f0e442',
            'Latin America': '#999999',
            'Confucian': '#e69f00',
            'Africa': '#cc79a7',
            'Baltic': '#0072b2',
            'Protestant Europe': '#d55e00',
            'Catholic Europe': '#e69f00',
            'English-Speaking': '#009e73',
            'Orthodox Europe': '#0072b2',
            'AI Model': '#ff1493',  # 为AI模型使用特殊颜色
        }


    
    def load_llm_results(self):
        """
        加载包含LLM的PCA结果数据
        """
        # 假设llm_pca_analysis的结果保存为llm_country_scores_pca.pkl
        llm_results_path = os.path.join(self.data_path, "entity_scores_pca.pkl")
        if os.path.exists(llm_results_path):
            return pd.read_pickle(llm_results_path)
        else:
            # 如果没有专门的LLM结果文件，尝试加载普通结果文件
            country_scores_path = os.path.join(self.data_path, "country_scores_pca.pkl")
            return pd.read_pickle(country_scores_path)
    
    def plot_llm_cultural_map(self, data=None, figsize=(16, 12), save_path=None, 
                             show_country_labels=True, show_llm_labels=True,
                             highlight_chinese_llm=True):
        """
        绘制包含LLM和国家的文化地图
        
        Parameters:
        - data: DataFrame, 包含LLM和国家的PCA结果
        - figsize: tuple, 图形大小
        - save_path: str, 保存路径
        - show_country_labels: bool, 是否显示国家标签
        - show_llm_labels: bool, 是否显示LLM标签
        - highlight_chinese_llm: bool, 是否高亮中文LLM
        """
        if data is None:
            data = self.load_llm_results()
        
        plt.figure(figsize=figsize)
        
        # 分离国家和LLM数据
        if 'llm' in data.columns:
            country_data = data[data['llm'] == False]
            llm_data = data[data['llm'] == True]
        else:
            # 如果没有llm列，根据Cultural Region判断
            country_data = data[data['Cultural Region'] != 'AI Model']
            llm_data = data[data['Cultural Region'] == 'AI Model']
        
        # 绘制国家数据
        for region, color in self.cultural_region_colors.items():
            if region == 'AI Model':
                continue  # AI Model单独处理
                
            subset = country_data[country_data['Cultural Region'] == region]
            if len(subset) > 0:
                # 绘制国家散点
                plt.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                           label=region, color=color, s=50, alpha=0.7, 
                           marker='o', edgecolors='black', linewidth=0.5)
                
                # 添加国家标签
                if show_country_labels:
                    for i, row in subset.iterrows():
                        # 检查是否为伊斯兰国家（如果有Islamic列）
                        if 'Islamic' in subset.columns and row['Islamic']:
                            plt.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                                    color=color, fontsize=8, fontstyle='italic', 
                                    ha='center', va='bottom')
                        else:
                            plt.text(row['PC1_rescaled'], row['PC2_rescaled'], row['Country'], 
                                    color=color, fontsize=8, ha='center', va='bottom')
        
        # 绘制LLM数据
        if len(llm_data) > 0:
            if highlight_chinese_llm and 'Chinese LLM' in llm_data.columns:
                # 分别绘制中文和非中文LLM
                chinese_llm = llm_data[llm_data['Chinese LLM'] == True]
                non_chinese_llm = llm_data[llm_data['Chinese LLM'] == False]
                
                # 统一绘制所有LLM
                plt.scatter(llm_data['PC1_rescaled'], llm_data['PC2_rescaled'],
                           label='AI Models', color=self.cultural_region_colors['AI Model'],
                           s=100, marker='D', edgecolors='black', linewidth=1,
                           alpha=0.8)
            
            # 添加LLM标签
            if show_llm_labels:
                for i, row in llm_data.iterrows():
                    # 简化模型名称显示
                    model_name = row['Country']
                    if len(model_name) > 15:
                        model_name = model_name.split('/')[-1] if '/' in model_name else model_name[:15] + '...'
                    
                    plt.text(row['PC1_rescaled'], row['PC2_rescaled'], model_name,
                            color='black', fontsize=9, fontweight='bold',
                            ha='center', va='top', 
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        plt.xlabel('Survival vs. Self-Expression Values', fontsize=12)
        plt.ylabel('Traditional vs. Secular Values', fontsize=12)
        plt.title('Inglehart-Welzel Cultural Map with LLM Models', fontsize=14, fontweight='bold')
        
        # 添加图例
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"LLM Cultural map saved to {save_path}")
        
        plt.show()
    
    def plot_llm_decision_boundary(self, data=None, figsize=(16, 12), save_path=None):
        """
        绘制包含LLM的文化地图决策边界
        """
        if data is None:
            data = self.load_llm_results()
        
        # 准备训练数据（仅使用国家数据训练）
        if 'llm' in data.columns:
            country_data = data[data['llm'] == False]
        else:
            country_data = data[data['Cultural Region'] != 'AI Model']
        
        vis_data = country_data.dropna()[["PC1_rescaled", "PC2_rescaled", "Cultural Region"]]
        vis_data['label'] = pd.Categorical(vis_data['Cultural Region']).codes
        
        # 创建颜色映射
        tups = vis_data[['label', 'Cultural Region']].drop_duplicates().sort_values(by='label')
        tups['color'] = tups['Cultural Region'].map(self.cultural_region_colors)
        tups.reset_index(drop=True, inplace=True)
        cmap = mcolors.ListedColormap(tups['color'].values)
        
        # 训练SVM分类器
        X = vis_data[['PC1_rescaled', 'PC2_rescaled']].values
        y = vis_data['label'].values
        
        clf = SVC(kernel='rbf', gamma='scale', C=1000)
        clf.fit(X, y)
        
        # 创建网格用于绘制决策边界
        h = 0.02
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
        self.plot_llm_cultural_map(data, figsize=figsize, save_path=None, 
                                  show_country_labels=False, show_llm_labels=True)
        
        plt.title('Cultural Map with Decision Boundaries and LLM Models', fontsize=14, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"LLM Decision boundary plot saved to {save_path}")
        
        plt.show()
    
    def predict_llm_cultural_regions(self, data=None):
        """
        使用SVM预测LLM的文化区域归属
        """
        if data is None:
            data = self.load_llm_results()
        
        # 分离国家和LLM数据
        if 'llm' in data.columns:
            country_data = data[data['llm'] == False]
            llm_data = data[data['llm'] == True]
        else:
            country_data = data[data['Cultural Region'] != 'AI Model']
            llm_data = data[data['Cultural Region'] == 'AI Model']
        
        # 准备训练数据
        vis_data = country_data.dropna()[["PC1_rescaled", "PC2_rescaled", "Cultural Region"]]
        vis_data['label'] = pd.Categorical(vis_data['Cultural Region']).codes
        
        # 训练SVM
        X = vis_data[['PC1_rescaled', 'PC2_rescaled']].values
        y = vis_data['label'].values
        clf = SVC(kernel='rbf', gamma=0.05, C=1000)
        clf.fit(X, y)
        
        # 预测LLM的文化区域
        if len(llm_data) > 0:
            X_llm = llm_data[['PC1_rescaled', 'PC2_rescaled']].values
            llm_predictions = clf.predict(X_llm)
            
            # 映射回文化区域名称
            label_to_region = dict(enumerate(pd.Categorical(vis_data['Cultural Region']).categories))
            predicted_regions = [label_to_region[label] for label in llm_predictions]
            
            # 创建结果DataFrame
            results = llm_data.copy()
            results['Predicted Cultural Region'] = predicted_regions
            
            return results[['Country', 'PC1_rescaled', 'PC2_rescaled', 'Chinese LLM', 'Predicted Cultural Region']]
        
        return pd.DataFrame()
    
    def create_llm_summary_statistics(self, data=None):
        """
        创建包含LLM的汇总统计信息
        """
        if data is None:
            data = self.load_llm_results()
        
        print("=== LLM Cultural Map Summary Statistics ===")
        
        # 分离数据
        if 'llm' in data.columns:
            country_data = data[data['llm'] == False]
            llm_data = data[data['llm'] == True]
        else:
            country_data = data[data['Cultural Region'] != 'AI Model']
            llm_data = data[data['Cultural Region'] == 'AI Model']
        
        print(f"Total countries: {len(country_data)}")
        print(f"Total LLM models: {len(llm_data)}")
        
        if len(llm_data) > 0 and 'Chinese LLM' in llm_data.columns:
            chinese_count = llm_data['Chinese LLM'].sum()
            print(f"Chinese LLM models: {chinese_count}")
            print(f"Non-Chinese LLM models: {len(llm_data) - chinese_count}")
        
        if 'Cultural Region' in country_data.columns:
            print("\nCountries by Cultural Region:")
            region_counts = country_data['Cultural Region'].value_counts()
            for region, count in region_counts.items():
                print(f"  {region}: {count}")
        
        print("\nPrincipal Component Statistics:")
        print(f"PC1 range: [{data['PC1_rescaled'].min():.2f}, {data['PC1_rescaled'].max():.2f}]")
        print(f"PC2 range: [{data['PC2_rescaled'].min():.2f}, {data['PC2_rescaled'].max():.2f}]")
        
        # LLM预测结果
        if len(llm_data) > 0:
            print("\n=== LLM Cultural Region Predictions ===")
            predictions = self.predict_llm_cultural_regions(data)
            if len(predictions) > 0:
                for _, row in predictions.iterrows():
                    chinese_flag = "(Chinese)" if row['Chinese LLM'] else "(Non-Chinese)"
                    print(f"  {row['Country']} {chinese_flag}: {row['Predicted Cultural Region']}")
        
        return data.describe()

def main():
    """
    测试LLM可视化模块
    """
    print("=== 测试LLM可视化模块 ===")
    
    # 确保results目录存在
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # 初始化可视化器
    visualizer = LLMCulturalMapVisualizer()
    
    try:
        # 1. 加载LLM结果数据
        print("\n1. 加载LLM结果数据...")
        data = visualizer.load_llm_results()
        print(f"成功加载数据: {len(data)} 条记录")
        
        # 2. 绘制LLM文化地图
        print("\n2. 绘制LLM文化地图...")
        llm_map_path = os.path.join(results_dir, "llm_cultural_map.png")
        visualizer.plot_llm_cultural_map(save_path=llm_map_path)
        
        # 3. 绘制决策边界
        print("\n3. 绘制决策边界...")
        boundary_path = os.path.join(results_dir, "llm_decision_boundary.png")
        visualizer.plot_llm_decision_boundary(save_path=boundary_path)
        
        # 4. 生成汇总统计
        print("\n4. 生成汇总统计...")
        summary_stats = visualizer.create_llm_summary_statistics()
        
        print("\nLLM可视化测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()