#!/usr/bin/env python3
"""
测试deepseek-reasoner模型的问题识别
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def test_deepseek_issues():
    """测试deepseek-reasoner模型的问题"""
    print("=== 测试deepseek-reasoner模型问题识别 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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
    
    # 获取所有问题
    question_ids = list(interview.questionnaire.questions.get_all_questions().keys())
    print(f"总问题数: {len(question_ids)}")
    
    failed_questions = []
    successful_questions = []
    
    for i, question_id in enumerate(question_ids, 1):
        print(f"\n--- 测试问题 {i}/{len(question_ids)}: {question_id} ---")
        
        try:
            # 获取问题文本
            question_text = interview.questionnaire.questions.get_question(question_id)
            print(f"问题: {question_text[:100]}...")
            
            # 调用API
            raw_response = interview.call_model_api(deepseek_model, question_id, question_text)
            
            if raw_response:
                print(f"原始回答: '{raw_response}'")
                
                # 验证回答
                from llm_questionnaire import ResponseValidator
                validator = ResponseValidator()
                is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
                
                if is_valid:
                    print(f"✓ 成功: {parsed_response}")
                    successful_questions.append(question_id)
                else:
                    print(f"✗ 失败: {error_msg}")
                    failed_questions.append({
                        'question_id': question_id,
                        'raw_response': raw_response,
                        'error': error_msg
                    })
            else:
                print("✗ API调用失败")
                failed_questions.append({
                    'question_id': question_id,
                    'raw_response': None,
                    'error': 'API调用失败'
                })
            
            # 添加延迟
            time.sleep(1)
            
        except Exception as e:
            print(f"✗ 异常: {e}")
            failed_questions.append({
                'question_id': question_id,
                'raw_response': None,
                'error': str(e)
            })
    
    # 打印总结
    print(f"\n=== 测试总结 ===")
    print(f"成功问题: {len(successful_questions)}")
    print(f"失败问题: {len(failed_questions)}")
    
    if successful_questions:
        print(f"成功的问题: {successful_questions}")
    
    if failed_questions:
        print(f"\n失败的问题详情:")
        for item in failed_questions:
            print(f"  {item['question_id']}: {item['error']}")
            if item['raw_response']:
                print(f"    原始回答: '{item['raw_response']}'")
    
    # 分析失败原因
    print(f"\n=== 失败原因分析 ===")
    error_types = {}
    for item in failed_questions:
        error = item['error']
        if error not in error_types:
            error_types[error] = []
        error_types[error].append(item['question_id'])
    
    for error, questions in error_types.items():
        print(f"{error}: {questions}")
    
    return failed_questions

if __name__ == "__main__":
    test_deepseek_issues()
