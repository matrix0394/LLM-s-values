import os
from src.data_processing import DataProcessor
from src.pca_analysis import PCAAnalyzer
from src.visualization import CulturalMapVisualizer

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "data")
    results_path = os.path.join(current_dir, "results")
    
    # 确保results目录存在
    os.makedirs(results_path, exist_ok=True)
    
    print(f"Using data path: {data_path}")
    print(f"Using results path: {results_path}")
    
    # 1. 数据处理
    print("Step 1: Processing data...")
    processor = DataProcessor(data_path=data_path)
    ivs_df = processor.load_ivs_data()
    processor.save_data()
    
    # 获取过滤后的数据
    filtered_data = processor.get_filtered_data()
    
    # 2. PCA分析
    print("\nStep 2: Performing PCA analysis...")
    analyzer = PCAAnalyzer(data_path="data")
    valid_data = analyzer.perform_pca_analysis(filtered_data)
    country_scores = analyzer.calculate_country_scores()
    analyzer.save_results()
    
    # 3. 可视化
    print("\nStep 3: Creating visualizations...")
    visualizer = CulturalMapVisualizer(data_path=data_path)
    
    # 绘制文化地图
    visualizer.plot_cultural_map(country_scores, save_path=os.path.join(results_path, "cultural_map.png"))
    
    # 绘制决策边界
    visualizer.plot_decision_boundary(country_scores, save_path=os.path.join(results_path, "decision_boundary.png"))
    
    # 显示统计信息
    stats = visualizer.create_summary_statistics(country_scores)
    print("\nAnalysis completed!")

if __name__ == "__main__":
    main()