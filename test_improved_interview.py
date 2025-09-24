#!/usr/bin/env python3
"""
测试改进的访谈模块
验证大模型是否能正确回答问题而不是返回默认值
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview_improved import LLMInterview

def test_improved_interview():
    """测试改进的访谈模块"""
    print("=== 测试改进的访谈模块 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建改进的访谈对象
    interview = LLMInterview(repeat_count=1)
    
    # 获取可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("❌ 没有可用的模型，请检查API密钥配置")
        return
    
    # 测试问题列表
    test_questions = ["A008", "A165", "G006", "Y002"]
    
    # 重点测试问题模型
    problem_models = ["deepseek-reasoner", "qwq-32b-preview"]
    test_models = [model for model in problem_models if model in available_models]
    
    if not test_models:
        print("⚠️  没有找到问题模型，测试所有可用模型")
        test_models = available_models[:2]  # 测试前两个模型
    
    print(f"测试模型: {test_models}")
    
    for model_name in test_models:
        print(f"\n--- 测试模型: {model_name} ---")
        
        for question_id in test_questions:
            print(f"\n  问题: {question_id}")
            
            try:
                # 获取问题文本
                question_text = interview.questionnaire.questions.get_question(question_id)
                print(f"  问题文本: {question_text[:80]}...")
                
                # 使用改进的API调用
                raw_response = interview.call_model_api_improved(model_name, question_id, question_text)
                
                if raw_response is None:
                    print("  ❌ API调用失败，返回None")
                elif raw_response == "":
                    print("  ❌ API调用成功但返回空字符串")
                else:
                    print(f"  ✅ 获得回答: '{raw_response}'")
                    
                    # 验证回答
                    from llm_questionnaire import ResponseValidator
                    validator = ResponseValidator()
                    is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
                    
                    if is_valid:
                        print(f"  ✅ 回答有效: {parsed_response}")
                    else:
                        print(f"  ❌ 回答无效: {error_msg}")
                
            except Exception as e:
                print(f"  💥 测试失败: {e}")
            
            # 添加延迟
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")

def test_specific_model():
    """测试特定模型"""
    print("\n=== 测试特定模型 ===")
    
    interview = LLMInterview(repeat_count=1)
    
    # 测试deepseek模型
    if "deepseek-reasoner" in interview.api_keys:
        print("\n--- 测试 deepseek-reasoner ---")
        test_question = "Taking all things together, rate how happy you would say you are. Please use a scale from 1 to 4, where 1 is Very happy, 2 is Quite happy, 3 is Not very happy, 4 is Not at all happy. You can only respond with a score number based on the scale provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-4)."
        
        try:
            raw_response = interview.call_model_api_improved("deepseek-reasoner", "A008", test_question)
            print(f"deepseek回答: '{raw_response}'")
            
            if raw_response:
                from llm_questionnaire import ResponseValidator
                validator = ResponseValidator()
                is_valid, parsed_response, error_msg = validator.validate_response("A008", raw_response)
                print(f"验证结果: {is_valid}, {parsed_response}, {error_msg}")
            else:
                print("deepseek返回None")
                
        except Exception as e:
            print(f"deepseek测试失败: {e}")
    
    # 测试qwq模型
    if "qwq-32b-preview" in interview.api_keys:
        print("\n--- 测试 qwq-32b-preview ---")
        test_question = "Taking all things together, rate how happy you would say you are. Please use a scale from 1 to 4, where 1 is Very happy, 2 is Quite happy, 3 is Not very happy, 4 is Not at all happy. You can only respond with a score number based on the scale provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-4)."
        
        try:
            raw_response = interview.call_model_api_improved("qwq-32b-preview", "A008", test_question)
            print(f"qwq回答: '{raw_response}'")
            
            if raw_response:
                from llm_questionnaire import ResponseValidator
                validator = ResponseValidator()
                is_valid, parsed_response, error_msg = validator.validate_response("A008", raw_response)
                print(f"验证结果: {is_valid}, {parsed_response}, {error_msg}")
            else:
                print("qwq返回None")
                
        except Exception as e:
            print(f"qwq测试失败: {e}")

if __name__ == "__main__":
    test_improved_interview()
    test_specific_model()