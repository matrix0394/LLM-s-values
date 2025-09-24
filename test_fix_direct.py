#!/usr/bin/env python3
"""
直接测试deepseek修复逻辑
"""

import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def test_fix_direct():
    """直接测试修复逻辑"""
    print("=== 直接测试deepseek修复逻辑 ===")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    # 找到deepseek模型
    deepseek_model = None
    for model_name in interview.model_configs.keys():
        if 'deepseek' in model_name.lower():
            deepseek_model = model_name
            break
    
    if not deepseek_model:
        print("错误: 未找到deepseek模型")
        return
    
    print(f"测试模型: {deepseek_model}")
    
    # 测试所有失败的问题
    failed_questions = ["A008", "A165", "E018", "E025", "G006"]
    
    for question_id in failed_questions:
        print(f"\n--- 测试问题: {question_id} ---")
        
        # 使用多次提问方法
        response = interview.ask_question_multiple_times(deepseek_model, question_id)
        
        print(f"原始回答: '{response.raw_response}'")
        print(f"解析结果: {response.response}")
        print(f"是否有效: {response.is_valid}")
        
        if response.error_message:
            print(f"错误信息: {response.error_message}")

if __name__ == "__main__":
    test_fix_direct()
