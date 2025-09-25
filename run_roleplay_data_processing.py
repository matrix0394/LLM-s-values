#!/usr/bin/env python3
"""
使用llm_country_roleplay_data_processor进行数据处理
"""

import sys
import os
from pathlib import Path

# 添加src目录到路径
sys.path.append('src')

from llm_country_roleplay_data_processor import LLMCountryRoleplayDataProcessor

def main():
    """主函数"""
    print("=== 开始使用 LLMCountryRoleplayDataProcessor 处理数据 ===")
    
    # 创建数据处理器
    processor = LLMCountryRoleplayDataProcessor()
    
    try:
        # 1. 加载角色扮演回答数据
        print("\n1. 加载角色扮演回答数据...")
        responses = processor.load_roleplay_responses()
        print(f"  加载了 {len(responses)} 个回答")
        
        # 2. 处理回答数据
        print("\n2. 处理回答数据...")
        processed_responses = processor.process_roleplay_responses(responses)
        print(f"  处理了 {len(processed_responses)} 个回答")
        
        # 3. 创建IVS兼容格式的DataFrame
        print("\n3. 创建IVS兼容格式的DataFrame...")
        ivs_data = processor.create_ivs_compatible_dataframe()
        print(f"  创建了包含 {len(ivs_data)} 行的DataFrame")
        
        if not ivs_data.empty:
            print(f"  DataFrame列: {list(ivs_data.columns)}")
            print(f"  前几行数据:")
            print(ivs_data.head(3))
        
        # 4. 保存处理后的数据（生成pkl文件）
        print("\n4. 保存处理后的数据...")
        processor.save_processed_data()
        
        # 5. 获取摘要统计
        print("\n5. 获取摘要统计...")
        stats = processor.get_summary_statistics()
        print("摘要统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n🎉 数据处理完成！")
        print("\n生成的文件:")
        print("  - data/llm_responses_roleplay/llm_roleplay_processed_responses.pkl")
        print("  - data/llm_responses_roleplay/llm_roleplay_processed_responses_raw.pkl")
        
    except Exception as e:
        print(f"❌ 数据处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
