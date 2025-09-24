#!/usr/bin/env python3
"""
测试简化后的提示词和移除默认值的效果
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def test_simplified_prompts():
    """测试简化后的提示词"""
    print("=== 测试简化后的提示词和移除默认值 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    # 获取所有可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("没有可用的模型，请检查API密钥配置")
        return
    
    # 测试问题列表
    test_questions = ["A008", "A165", "G006", "Y002"]
    
    for model_name in available_models:
        print(f"\n{'='*60}")
        print(f"测试模型: {model_name}")
        print(f"{'='*60}")
        
        # 检查是否为qwen模型
        is_qwen = "qwq" in model_name.lower()
        print(f"是否为qwen模型: {is_qwen}")
        
        if is_qwen:
            print("⚠️  此模型使用特殊处理逻辑")
        else:
            print("✓ 此模型使用标准处理逻辑，回答应该是自愿的")
        
        # 测试关键问题
        for question_id in test_questions:
            print(f"\n--- 测试问题: {question_id} ---")
            
            try:
                # 获取问题文本
                question_text = interview.questionnaire.questions.get_question(question_id)
                print(f"问题: {question_text[:80]}...")
                
                # 直接调用API获取原始回答
                raw_response = interview.call_model_api(model_name, question_id, question_text)
                print(f"原始回答: '{raw_response}'")
                
                if raw_response is None:
                    print("❌ API调用失败，返回None (没有默认值)")
                else:
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
                
                # 添加延迟
                time.sleep(0.5)
                
            except Exception as e:
                print(f"测试失败: {e}")
        
        print(f"\n模型 {model_name} 测试完成")

def check_prompt_simplification():
    """检查提示词简化情况"""
    print(f"\n{'='*60}")
    print("检查提示词简化情况")
    print(f"{'='*60}")
    
    # 读取源代码文件
    code_file = os.path.join(os.path.dirname(__file__), 'src', 'llm_interview.py')
    
    try:
        with open(code_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 检查简化情况:")
        
        # 检查标准提示词
        if "You are participating in a cultural values survey" in content:
            print("✓ 标准提示词已简化")
        
        # 检查是否移除了默认值
        if "return \"5\"" not in content:
            print("✓ 已移除通用默认值 '5'")
        else:
            print("⚠️  仍存在通用默认值 '5'")
        
        if "return \"1 2\"" not in content:
            print("✓ 已移除Y002默认值 '1 2'")
        else:
            print("⚠️  仍存在Y002默认值 '1 2'")
        
        if "return \"1 3 5\"" not in content:
            print("✓ 已移除Y003默认值 '1 3 5'")
        else:
            print("⚠️  仍存在Y003默认值 '1 3 5'")
        
        # 检查qwen特殊处理
        if "qwq" in content and "qwen" in content:
            print("✓ 保留了qwen模型的特殊处理")
        
        # 检查是否移除了deepseek特殊处理
        if "deepseek" not in content or "return None" in content:
            print("✓ 已移除deepseek模型的特殊默认值")
        else:
            print("⚠️  仍存在deepseek模型的特殊处理")
        
    except Exception as e:
        print(f"读取代码文件失败: {e}")

if __name__ == "__main__":
    test_simplified_prompts()
    check_prompt_simplification()
