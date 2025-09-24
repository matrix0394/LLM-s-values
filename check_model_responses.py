#!/usr/bin/env python3
"""
检查每个模型的回答是自愿的还是设置了默认值
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def check_model_responses():
    """检查每个模型的回答模式"""
    print("=== 检查模型回答模式 ===")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    # 获取所有可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("没有可用的模型，请检查API密钥配置")
        return
    
    # 测试问题列表
    test_questions = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
    
    for model_name in available_models:
        print(f"\n{'='*60}")
        print(f"检查模型: {model_name}")
        print(f"{'='*60}")
        
        # 检查模型是否在特殊处理列表中
        problematic_models = ["qwq", "deepseek", "reasoner"]
        is_problematic = any(problem_model in model_name.lower() for problem_model in problematic_models)
        print(f"是否为问题模型: {is_problematic}")
        
        if is_problematic:
            print("⚠️  此模型使用了特殊处理逻辑，可能包含默认值")
        else:
            print("✓ 此模型使用标准处理逻辑，回答应该是自愿的")
        
        # 测试几个关键问题
        key_questions = ["A008", "A165", "G006", "Y002"]
        
        for question_id in key_questions:
            print(f"\n--- 测试问题: {question_id} ---")
            
            try:
                # 获取问题文本
                question_text = interview.questionnaire.questions.get_question(question_id)
                print(f"问题: {question_text[:80]}...")
                
                # 直接调用API获取原始回答
                raw_response = interview.call_model_api(model_name, question_id, question_text)
                print(f"原始回答: '{raw_response}'")
                
                # 验证回答
                from llm_questionnaire import ResponseValidator
                validator = ResponseValidator()
                is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
                
                print(f"是否有效: {is_valid}")
                if is_valid:
                    print(f"解析结果: {parsed_response}")
                else:
                    print(f"错误信息: {error_msg}")
                
                # 分析回答模式
                if is_problematic:
                    if question_id == "A008" and raw_response == "2":
                        print("🔍 分析: 可能是默认值 (A008要求1-4，返回2)")
                    elif question_id == "A165" and raw_response == "1":
                        print("🔍 分析: 可能是默认值 (A165要求1-2，返回1)")
                    elif question_id == "G006" and raw_response == "2":
                        print("🔍 分析: 可能是默认值 (G006要求1-4，返回2)")
                    elif question_id == "Y002" and raw_response == "1 2":
                        print("🔍 分析: 可能是默认值 (Y002要求两个不同数字1-4，返回1 2)")
                    else:
                        print("🔍 分析: 回答看起来是自愿的")
                else:
                    print("🔍 分析: 标准模型，回答应该是自愿的")
                
                # 添加延迟
                time.sleep(0.5)
                
            except Exception as e:
                print(f"测试失败: {e}")
        
        print(f"\n模型 {model_name} 检查完成")

def check_default_values():
    """检查代码中的默认值设置"""
    print(f"\n{'='*60}")
    print("检查代码中的默认值设置")
    print(f"{'='*60}")
    
    # 读取源代码文件
    code_file = os.path.join(os.path.dirname(__file__), 'src', 'llm_interview.py')
    
    try:
        with open(code_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找默认值设置
        print("🔍 查找默认值设置:")
        
        # 查找deepseek的特殊默认值
        if "deepseek" in content and "A008" in content:
            print("✓ 发现deepseek模型的特殊默认值设置")
            print("  - A008 (幸福感): 默认值 '2'")
            print("  - A165 (信任): 默认值 '1'")
            print("  - E018 (权威尊重): 默认值 '2'")
            print("  - E025 (请愿书): 默认值 '2'")
            print("  - G006 (国家自豪感): 默认值 '2'")
        
        # 查找通用默认值
        if "return \"5\"" in content:
            print("✓ 发现通用默认值 '5'")
        
        if "return \"1 2\"" in content:
            print("✓ 发现Y002默认值 '1 2'")
        
        if "return \"1 3 5\"" in content:
            print("✓ 发现Y003默认值 '1 3 5'")
        
        # 查找问题模型列表
        if "problematic_models" in content:
            print("✓ 发现问题模型列表设置")
            print("  - 包含: qwq, deepseek, reasoner")
            print("  - 这些模型会使用特殊处理逻辑")
        
    except Exception as e:
        print(f"读取代码文件失败: {e}")

def analyze_response_patterns():
    """分析回答模式"""
    print(f"\n{'='*60}")
    print("回答模式分析")
    print(f"{'='*60}")
    
    print("📊 模型分类:")
    print("1. 标准模型 (GPT, Gemini等):")
    print("   - 使用标准提示词")
    print("   - 回答应该是自愿的")
    print("   - 只有在API调用失败时才使用默认值")
    
    print("\n2. 问题模型 (qwq, deepseek, reasoner):")
    print("   - 使用强化提示词")
    print("   - 包含后处理逻辑")
    print("   - 可能包含智能默认值")
    
    print("\n3. 默认值触发条件:")
    print("   - API调用失败")
    print("   - 回答无效")
    print("   - 模型拒绝回答")
    print("   - 达到最大重试次数")

if __name__ == "__main__":
    check_model_responses()
    check_default_values()
    analyze_response_patterns()
