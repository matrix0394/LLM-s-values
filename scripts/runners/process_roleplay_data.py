#!/usr/bin/env python3
"""
处理roleplay回答数据的完整流程
"""

import sys
import os
from pathlib import Path

# 添加src目录到路径
sys.path.append('src')

from llm_country_roleplay_data_processor import LLMCountryRoleplayDataProcessor
from llm_country_roleplay_pca_analysis import LLMCountryRoleplayPCAAnalyzer
from llm_country_roleplay_visualization import LLMCountryRoleplayVisualizer

def main():
    """主函数"""
    print("=== 开始处理 Roleplay 回答数据 ===")
    
    # 1. 数据预处理
    print("\n1. 数据预处理...")
    processor = LLMCountryRoleplayDataProcessor()
    
    try:
        # 加载角色扮演回答数据
        print("  加载角色扮演回答数据...")
        responses = processor.load_roleplay_responses()
        print(f"  加载了 {len(responses)} 个回答")
        
        # 处理回答数据
        print("  处理回答数据...")
        processed_responses = processor.process_roleplay_responses(responses)
        print(f"  处理了 {len(processed_responses)} 个回答")
        
        # 创建DataFrame
        print("  创建DataFrame...")
        df = processor.create_ivs_compatible_dataframe()
        print(f"  创建了包含 {len(df)} 行的DataFrame")
        
        # 保存处理后的数据
        print("  保存处理后的数据...")
        processor.save_processed_data()
        print("✅ 数据预处理完成")
        
    except Exception as e:
        print(f"❌ 数据预处理失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. PCA分析
    print("\n2. PCA分析...")
    pca_analyzer = LLMCountryRoleplayPCAAnalyzer()
    
    try:
        # 运行完整的PCA分析
        print("  运行完整的PCA分析...")
        entity_scores = pca_analyzer.run_full_analysis()
        print(f"✅ PCA分析完成，生成了 {len(entity_scores)} 个实体的分数")
        
    except Exception as e:
        print(f"❌ PCA分析失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 可视化
    print("\n3. 生成可视化...")
    visualizer = LLMCountryRoleplayVisualizer()
    
    try:
        # 生成角色扮演文化地图
        print("  生成角色扮演文化地图...")
        visualizer.plot_roleplay_cultural_map()
        print("✅ 文化地图已生成")
        
        # 分析角色扮演准确性
        print("  分析角色扮演准确性...")
        visualizer.analyze_roleplay_accuracy()
        print("✅ 角色扮演准确性分析完成")
        
        # 生成交互式地图
        print("  生成交互式地图...")
        visualizer.plot_interactive_roleplay_cultural_map()
        print("✅ 交互式地图已生成")
        
    except Exception as e:
        print(f"❌ 可视化生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 所有数据处理步骤完成！")
    print("\n生成的文件:")
    print("  - data/llm_responses_roleplay/processed_data.pkl")
    print("  - data/llm_responses_roleplay/pca_results.pkl")
    print("  - data/llm_responses_roleplay/cultural_map_roleplay.html")
    print("  - data/llm_responses_roleplay/roleplay_accuracy_analysis.html")

if __name__ == "__main__":
    main()
