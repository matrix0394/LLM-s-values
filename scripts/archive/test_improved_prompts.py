#!/usr/bin/env python3
"""
测试改进后的prompt效果
"""

import sys
import os
sys.path.append('src')

from llm_country_roleplay_interview import LLMCountryRoleplayInterview
import json

def test_improved_prompts():
    """测试改进后的prompt效果"""
    
    print("=== 测试改进后的Prompt效果 ===\n")
    
    # 初始化访谈器
    interview = LLMCountryRoleplayInterview()
    
    # 测试配置
    test_models = ["openai/gpt-4o-mini", "google/gemini-2.0-flash-001"]
    test_countries = ["United States", "China", "Nigeria"]  # 选择不同难度的国家
    test_questions = ["E018", "G006", "A008"]  # 选择不同难度的问题
    
    results = {}
    
    for model_name in test_models:
        print(f"测试模型: {model_name}")
        results[model_name] = {}
        
        for country_name in test_countries:
            print(f"  测试国家: {country_name}")
            results[model_name][country_name] = {}
            
            for question_id in test_questions:
                print(f"    测试问题: {question_id}")
                
                try:
                    # 调用改进后的方法
                    response = interview.ask_question_roleplay(model_name, country_name, question_id)
                    
                    result = {
                        'raw_response': response.raw_response,
                        'parsed_response': response.response,
                        'is_valid': response.is_valid,
                        'error_message': response.error_message
                    }
                    
                    results[model_name][country_name][question_id] = result
                    
                    # 显示结果
                    status = "✅ 有效" if response.is_valid else "❌ 无效"
                    print(f"      结果: {response.raw_response} -> {response.response} ({status})")
                    
                    if not response.is_valid:
                        print(f"      错误: {response.error_message}")
                    
                except Exception as e:
                    print(f"      错误: {e}")
                    results[model_name][country_name][question_id] = {
                        'error': str(e)
                    }
    
    # 保存测试结果
    with open('results/improved_prompt_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 测试结果分析 ===")
    
    # 统计结果
    total_tests = 0
    valid_responses = 0
    ones_responses = 0
    
    for model_name, model_results in results.items():
        for country_name, country_results in model_results.items():
            for question_id, result in country_results.items():
                if 'error' not in result:
                    total_tests += 1
                    if result['is_valid']:
                        valid_responses += 1
                    if result['raw_response'] == '1':
                        ones_responses += 1
    
    print(f"总测试数: {total_tests}")
    print(f"有效回答数: {valid_responses}")
    print(f"回答'1'数: {ones_responses}")
    print(f"有效率: {valid_responses/total_tests*100:.1f}%")
    print(f"回答'1'率: {ones_responses/total_tests*100:.1f}%")
    
    print(f"\n详细结果已保存到: results/improved_prompt_test_results.json")
    
    return results

if __name__ == "__main__":
    results = test_improved_prompts()
