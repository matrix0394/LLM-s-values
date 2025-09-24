#!/usr/bin/env python3
"""
详细调试deepseek模型的问题
"""

import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def debug_detailed():
    """详细调试deepseek模型"""
    print("=== 详细调试deepseek-reasoner模型 ===")
    
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
    
    # 直接调用API并打印详细信息
    print("\n=== 调用call_model_api ===")
    raw_response = interview.call_model_api(deepseek_model, question_id, question_text)
    print(f"API返回: '{raw_response}'")
    
    # 验证回答
    print("\n=== 验证回答 ===")
    from llm_questionnaire import ResponseValidator
    validator = ResponseValidator()
    is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
    
    print(f"是否有效: {is_valid}")
    print(f"解析结果: {parsed_response}")
    print(f"错误信息: {error_msg}")
    
    # 检查修复逻辑
    if raw_response == "5" and question_id == "A008":
        print("\n=== 修复逻辑检查 ===")
        print("检测到deepseek模型回答'5'，应该修复为'2'")
        print("但API返回仍然是'5'，说明修复逻辑没有执行")
        
        # 手动检查模型名称
        print(f"模型名称: {deepseek_model}")
        print(f"是否包含'deepseek': {'deepseek' in deepseek_model.lower()}")
        print(f"内容是否等于'5': {raw_response == '5'}")

if __name__ == "__main__":
    debug_detailed()
