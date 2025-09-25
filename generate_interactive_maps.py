#!/usr/bin/env python3
"""
生成交互式HTML地图的独立脚本
生成包含鼠标悬停信息的交互式文化地图
"""

from src.llm_country_roleplay_visualization import LLMCountryRoleplayVisualizer
import os

def main():
    """主函数 - 专门用于生成交互式HTML地图"""
    print("=== Interactive HTML Maps Generator ===")
    print("This script generates interactive maps with hover information")
    print("Maps will be saved to the 'results' directory")
    
    # 创建可视化器
    data_dir = "data"
    results_dir = "results"
    
    visualizer = LLMCountryRoleplayVisualizer(data_dir=data_dir, results_dir=results_dir)
    
    try:
        # 加载数据
        print("\nLoading roleplay analysis data...")
        data = visualizer.load_roleplay_results()
        
        if data.empty:
            print("❌ No data found. Please run the PCA analysis first.")
            return
        
        print(f"✅ Data loaded successfully: {len(data)} entities")
        
        # 生成所有交互式地图
        visualizer.create_all_interactive_maps(data)
        
        # 显示生成的文件
        print("\n=== Generated Files ===")
        results_path = visualizer.results_dir
        
        html_files = list(results_path.glob("interactive_*.html"))
        for html_file in sorted(html_files):
            file_size = html_file.stat().st_size / 1024 / 1024  # MB
            print(f"📄 {html_file.name} ({file_size:.1f} MB)")
        
        print(f"\n✅ Generated {len(html_files)} interactive HTML maps")
        print(f"📁 Location: {results_path.absolute()}")
        
        print("\n=== How to Use ===")
        print("1. Open any .html file in your web browser")
        print("2. Hover over data points to see detailed information")
        print("3. Use the legend to toggle different data series")
        print("4. Zoom and pan to explore the data")
        
        print("\n=== Files Description ===")
        print("• interactive_roleplay_overview.html - Complete overview with all entities")
        print("• interactive_map_*.html - Individual maps for each cultural region")
        
    except Exception as e:
        print(f"❌ Error generating interactive maps: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
