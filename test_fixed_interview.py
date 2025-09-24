#!/usr/bin/env python3
"""
测试修复后的llm_interview.py
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def test_fixed_interview():
    """测试修复后的访谈系统"""
    print("=== 测试修复后的访谈系统 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    # 获取可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("❌ 没有可用的模型")
        return
    
    # 测试问题列表
    test_questions = ["A008", "A165", "G006", "Y002", "Y003"]
    
    # 测试每个模型
    for model_name in available_models:
        print(f"\n--- 测试模型: {model_name} ---")
        
        try:
            # 测试几个关键问题
            for question_id in test_questions[:3]:  # 只测试前3个问题
                print(f"  问题: {question_id}")
                
                # 获取问题文本
                question_text = interview.questionnaire.questions.get_question(question_id)
                if not question_text:
                    print(f"    ❌ 问题不存在")
                    continue
                
                # 调用API
                raw_response = interview.call_model_api(model_name, question_id, question_text)
                print(f"    原始回答: '{raw_response}'")
                
                if raw_response is None:
                    print(f"    ❌ API调用失败或返回None")
                elif raw_response == "":
                    print(f"    ❌ 返回空字符串")
                else:
                    print(f"    ✅ 获得回答")
                    
                    # 验证回答
                    from llm_questionnaire import ResponseValidator
                    validator = ResponseValidator()
                    is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
                    
                    if is_valid:
                        print(f"    ✅ 回答有效: {parsed_response}")
                    else:
                        print(f"    ❌ 回答无效: {error_msg}")
                
                time.sleep(1)  # 避免API限制
            
        except Exception as e:
            print(f"    ❌ 模型测试失败: {e}")
        
        time.sleep(2)  # 模型间延迟
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_fixed_interview()
