#!/usr/bin/env python3
"""
快速测试qwen模型修复方案
"""

import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def quick_test():
    """快速测试qwen模型"""
    print("=== 快速测试qwen-32b-preview修复方案 ===")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)  # 只测试一次
    
    # 找到qwen模型
    qwen_model = None
    for model_name in interview.model_configs.keys():
        if "qwq" in model_name.lower():
            qwen_model = model_name
            break
    
    if not qwen_model:
        print("错误: 未找到qwen模型")
        return
    
    print(f"测试模型: {qwen_model}")
    
    # 测试Y002和Y003问题
    test_questions = ["Y002", "Y003"]
    
    for question_id in test_questions:
        print(f"\n--- 测试问题: {question_id} ---")
        
        try:
            # 使用多次提问方法
            response = interview.ask_question_multiple_times(qwen_model, question_id)
            
            print(f"原始回答: '{response.raw_response}'")
            print(f"解析结果: {response.response}")
            print(f"是否有效: {response.is_valid}")
            
            if response.error_message:
                print(f"错误信息: {response.error_message}")
            
            # 检查是否还有"Alright"开头
            if response.raw_response and response.raw_response.lower().startswith('alright'):
                print("⚠️  仍然存在'Alright'开头的问题")
            else:
                print("✓ 没有'Alright'开头问题")
                
        except Exception as e:
            print(f"测试失败: {e}")

if __name__ == "__main__":
    quick_test()
