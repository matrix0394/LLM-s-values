#!/usr/bin/env python3
"""
简化的roleplay数据处理流程 - 跳过有问题的pickle文件
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

# 添加src目录到路径
sys.path.append('src')

def load_roleplay_data_from_json():
    """从JSON文件加载roleplay数据"""
    print("从JSON文件加载roleplay数据...")
    
    # 加载合并的结果文件
    results_file = "data/llm_responses_roleplay/roleplay_results.json"
    if not os.path.exists(results_file):
        print(f"❌ 未找到结果文件: {results_file}")
        return None
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ 加载了 {len(data)} 条记录")
    return data

def process_roleplay_data(data):
    """处理roleplay数据"""
    print("处理roleplay数据...")
    
    processed_records = []
    
    # 从results字段获取数据
    results = data.get('results', [])
    
    for record in results:
        model = record.get('model', '')
        country = record.get('country', '')
        responses = record.get('responses', [])
        
        # 创建基础记录
        processed_record = {
            'model': model,
            'country': country,
            'cultural_region': 'AI Roleplay',  # 标记为AI角色扮演
            'roleplay': True
        }
        
        # 处理回答
        for response in responses:
            if response and isinstance(response, dict):
                question_id = response.get('question_id', '')
                response_value = response.get('response')
                if question_id and response_value is not None:
                    processed_record[question_id] = response_value
        
        processed_records.append(processed_record)
    
    print(f"✅ 处理了 {len(processed_records)} 条记录")
    return processed_records

def create_summary_statistics(processed_data):
    """创建摘要统计"""
    print("创建摘要统计...")
    
    # 转换为DataFrame
    df = pd.DataFrame(processed_data)
    
    # 统计信息
    total_records = len(df)
    unique_models = df['model'].nunique()
    unique_countries = df['country'].nunique()
    
    print(f"总记录数: {total_records}")
    print(f"唯一模型数: {unique_models}")
    print(f"唯一国家数: {unique_countries}")
    
    # 按模型统计
    model_counts = df['model'].value_counts()
    print("\n各模型记录数:")
    for model, count in model_counts.items():
        print(f"  {model}: {count}")
    
    # 按国家统计
    country_counts = df['country'].value_counts()
    print(f"\n各国家记录数 (前10个):")
    for country, count in country_counts.head(10).items():
        print(f"  {country}: {count}")
    
    return df

def save_processed_data(df, processed_data):
    """保存处理后的数据"""
    print("保存处理后的数据...")
    
    # 保存为CSV
    csv_file = "data/llm_responses_roleplay/processed_roleplay_data.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✅ CSV文件已保存: {csv_file}")
    
    # 保存为JSON
    json_file = "data/llm_responses_roleplay/processed_roleplay_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"✅ JSON文件已保存: {json_file}")
    
    # 保存摘要统计
    summary_file = "data/llm_responses_roleplay/roleplay_summary.json"
    summary = {
        'total_records': len(df),
        'unique_models': df['model'].nunique(),
        'unique_countries': df['country'].nunique(),
        'model_counts': df['model'].value_counts().to_dict(),
        'country_counts': df['country'].value_counts().to_dict()
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"✅ 摘要统计已保存: {summary_file}")

def main():
    """主函数"""
    print("=== 开始处理 Roleplay 回答数据 (简化版) ===")
    
    # 1. 加载数据
    data = load_roleplay_data_from_json()
    if data is None:
        return
    
    # 2. 处理数据
    processed_data = process_roleplay_data(data)
    
    # 3. 创建统计
    df = create_summary_statistics(processed_data)
    
    # 4. 保存数据
    save_processed_data(df, processed_data)
    
    print("\n🎉 数据处理完成！")
    print("\n生成的文件:")
    print("  - data/llm_responses_roleplay/processed_roleplay_data.csv")
    print("  - data/llm_responses_roleplay/processed_roleplay_data.json")
    print("  - data/llm_responses_roleplay/roleplay_summary.json")

if __name__ == "__main__":
    main()
