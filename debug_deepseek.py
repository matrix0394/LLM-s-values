#!/usr/bin/env python3
"""
调试deepseek模型的问题
"""

import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def debug_deepseek():
    """调试deepseek模型"""
    print("=== 调试deepseek-reasoner模型 ===")
    
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
    
    # 测试A008问题
    question_id = "A008"
    question_text = interview.questionnaire.questions.get_question(question_id)
    
    print(f"\n测试问题: {question_id}")
    print(f"问题文本: {question_text[:100]}...")
    
    # 直接调用API
    raw_response = interview.call_model_api(deepseek_model, question_id, question_text)
    print(f"原始回答: '{raw_response}'")
    
    # 检查是否是"5"
    if raw_response == "5":
        print("✓ 检测到deepseek模型回答'5'")
        
        # 手动应用修复逻辑
        if question_id == "A008":  # 幸福感 1-4
            fixed_response = "2"  # 中等偏上
            print(f"应用修复: {raw_response} -> {fixed_response}")
        else:
            print("其他问题类型的修复逻辑")
    else:
        print("未检测到'5'回答")

if __name__ == "__main__":
    debug_deepseek()
