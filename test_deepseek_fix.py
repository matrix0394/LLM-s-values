#!/usr/bin/env python3
"""
测试deepseek模型修复效果
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def test_deepseek_fix():
    """测试deepseek模型修复效果"""
    print("=== 测试deepseek模型修复效果 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    model_name = "deepseek-reasoner"
    print(f"测试模型: {model_name}")
    
    # 测试问题列表
    test_questions = ["A008", "A165", "G006", "Y002"]
    
    for question_id in test_questions:
        print(f"\n--- 测试问题: {question_id} ---")
        
        try:
            # 获取问题文本
            question_text = interview.questionnaire.questions.get_question(question_id)
            print(f"问题: {question_text[:80]}...")
            
            # 使用修复后的API调用
            raw_response = interview.call_model_api(model_name, question_id, question_text)
            print(f"原始回答: '{raw_response}'")
            
            if raw_response is None:
                print("❌ API调用失败，返回None")
            elif raw_response == "":
                print("❌ API调用成功但返回空字符串")
            else:
                print("✅ API调用成功，获得回答")
                
                # 验证回答
                from llm_questionnaire import ResponseValidator
                validator = ResponseValidator()
                is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
                
                print(f"是否有效: {is_valid}")
                if is_valid:
                    print(f"解析结果: {parsed_response}")
                    print("✅ 回答有效")
                else:
                    print(f"错误信息: {error_msg}")
                    print("❌ 回答无效")
            
        except Exception as e:
            print(f"测试失败: {e}")
        
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_deepseek_fix()
