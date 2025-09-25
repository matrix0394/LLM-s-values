#!/usr/bin/env python3
"""
分析roleplay回答结果，找出所有回答"1"的地方并将其标记为无效
统计哪些问题和哪些国家比较难模仿
"""

import sys
import os
import pickle
import pandas as pd
from collections import defaultdict, Counter
import json

def analyze_roleplay_responses():
    """分析roleplay回答结果"""
    
    # 定义要分析的模型目录
    model_dirs = [
        "data/llm_responses_roleplay/roleplay_intermediate_deepseek_deepseek_chat_v3_0324",
        "data/llm_responses_roleplay/roleplay_intermediate_qwen_qwq_32b"
    ]
    
    # 存储所有回答数据
    all_responses = []
    response_ones = []  # 存储回答"1"的数据
    
    # 问题统计
    question_stats = defaultdict(lambda: {'total': 0, 'ones': 0, 'invalid': 0})
    country_stats = defaultdict(lambda: {'total': 0, 'ones': 0, 'invalid': 0})
    model_stats = defaultdict(lambda: {'total': 0, 'ones': 0, 'invalid': 0})
    
    print("=== 分析Roleplay回答结果 ===\n")
    
    for model_dir in model_dirs:
        if not os.path.exists(model_dir):
            print(f"目录不存在: {model_dir}")
            continue
            
        model_name = os.path.basename(model_dir)
        print(f"分析模型: {model_name}")
        
        # 获取所有pkl文件
        pkl_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl') and not f.startswith('summary')]
        
        for pkl_file in pkl_files:
            country_name = pkl_file.replace(f"{model_name.split('_')[-1]}_", "").replace('.pkl', '')
            file_path = os.path.join(model_dir, pkl_file)
            
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                # 数据是字典格式，键是模型名称，值是回答列表
                if isinstance(data, dict):
                    for model_key, responses in data.items():
                        print(f"  处理国家: {country_name} ({len(responses)} 个回答)")
                        
                        for response in responses:
                            # 统计总数
                            question_stats[response['question_id']]['total'] += 1
                            country_stats[country_name]['total'] += 1
                            model_stats[model_name]['total'] += 1
                            
                            # 检查是否回答"1"
                            if response['raw_response'] == "1":
                                response_ones.append({
                                    'model': model_name,
                                    'country': country_name,
                                    'question_id': response['question_id'],
                                    'raw_response': response['raw_response'],
                                    'is_valid': response['is_valid'],
                                    'error_message': response['error_message']
                                })
                                
                                # 统计回答"1"的情况
                                question_stats[response['question_id']]['ones'] += 1
                                country_stats[country_name]['ones'] += 1
                                model_stats[model_name]['ones'] += 1
                                
                                # 标记为无效
                                response['is_valid'] = False
                                response['error_message'] = "回答为默认值'1'，标记为无效"
                            
                            # 统计无效回答
                            if not response['is_valid']:
                                question_stats[response['question_id']]['invalid'] += 1
                                country_stats[country_name]['invalid'] += 1
                                model_stats[model_name]['invalid'] += 1
                            
                            all_responses.append(response)
                    
            except Exception as e:
                print(f"    错误: 无法读取 {file_path}: {e}")
    
    print(f"\n=== 分析结果 ===")
    print(f"总回答数: {len(all_responses)}")
    print(f"回答'1'的数量: {len(response_ones)}")
    
    # 分析问题难度
    print(f"\n=== 问题难度分析 ===")
    question_difficulty = []
    for question_id, stats in question_stats.items():
        if stats['total'] > 0:
            ones_rate = stats['ones'] / stats['total'] * 100
            invalid_rate = stats['invalid'] / stats['total'] * 100
            question_difficulty.append({
                'question_id': question_id,
                'total': stats['total'],
                'ones': stats['ones'],
                'invalid': stats['invalid'],
                'ones_rate': ones_rate,
                'invalid_rate': invalid_rate
            })
    
    # 按回答"1"的比例排序
    question_difficulty.sort(key=lambda x: x['ones_rate'], reverse=True)
    
    print("最难回答的问题 (按回答'1'的比例排序):")
    for i, q in enumerate(question_difficulty[:10]):
        print(f"{i+1:2d}. {q['question_id']:6s} - 回答'1'率: {q['ones_rate']:5.1f}% ({q['ones']:2d}/{q['total']:2d}) - 总无效率: {q['invalid_rate']:5.1f}%")
    
    # 分析国家难度
    print(f"\n=== 国家难度分析 ===")
    country_difficulty = []
    for country, stats in country_stats.items():
        if stats['total'] > 0:
            ones_rate = stats['ones'] / stats['total'] * 100
            invalid_rate = stats['invalid'] / stats['total'] * 100
            country_difficulty.append({
                'country': country,
                'total': stats['total'],
                'ones': stats['ones'],
                'invalid': stats['invalid'],
                'ones_rate': ones_rate,
                'invalid_rate': invalid_rate
            })
    
    # 按回答"1"的比例排序
    country_difficulty.sort(key=lambda x: x['ones_rate'], reverse=True)
    
    print("最难模仿的国家 (按回答'1'的比例排序):")
    for i, c in enumerate(country_difficulty):
        print(f"{i+1:2d}. {c['country']:20s} - 回答'1'率: {c['ones_rate']:5.1f}% ({c['ones']:2d}/{c['total']:2d}) - 总无效率: {c['invalid_rate']:5.1f}%")
    
    # 分析模型表现
    print(f"\n=== 模型表现分析 ===")
    for model, stats in model_stats.items():
        if stats['total'] > 0:
            ones_rate = stats['ones'] / stats['total'] * 100
            invalid_rate = stats['invalid'] / stats['total'] * 100
            print(f"{model:40s} - 回答'1'率: {ones_rate:5.1f}% ({stats['ones']:3d}/{stats['total']:3d}) - 总无效率: {invalid_rate:5.1f}%")
    
    # 保存分析结果
    analysis_results = {
        'summary': {
            'total_responses': len(all_responses),
            'responses_ones': len(response_ones),
            'ones_rate': len(response_ones) / len(all_responses) * 100 if all_responses else 0
        },
        'question_difficulty': question_difficulty,
        'country_difficulty': country_difficulty,
        'model_stats': dict(model_stats),
        'response_ones_details': response_ones
    }
    
    # 保存到文件
    with open('results/roleplay_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 详细分析结果已保存到: results/roleplay_analysis_results.json ===")
    
    return analysis_results

if __name__ == "__main__":
    results = analyze_roleplay_responses()
