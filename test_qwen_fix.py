#!/usr/bin/env python3
"""
测试qwen-32b-preview模型修复方案
专门测试Y002和Y003问题的回答质量
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview
from llm_questionnaire import ResponseValidator

def test_qwen_responses():
    """测试qwen模型的回答质量"""
    print("=== 测试qwen-32b-preview模型修复方案 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=3)
    
    # 检查是否有qwen模型的API密钥
    if "qwq" not in [name.lower() for name in interview.api_keys.keys()]:
        print("错误: 未找到qwen模型的API密钥配置")
        return
    
    # 找到qwen模型名称
    qwen_model = None
    for model_name in interview.model_configs.keys():
        if "qwq" in model_name.lower():
            qwen_model = model_name
            break
    
    if not qwen_model:
        print("错误: 未找到qwen模型配置")
        return
    
    print(f"测试模型: {qwen_model}")
    
    # 测试问题列表（重点关注Y002和Y003）
    test_questions = ["Y002", "Y003", "F118", "G006"]
    
    validator = ResponseValidator()
    results = {}
    
    for question_id in test_questions:
        print(f"\n--- 测试问题: {question_id} ---")
        
        # 获取问题文本
        question_text = interview.questionnaire.questions.get_question(question_id)
        if not question_text:
            print(f"  错误: 未找到问题 {question_id}")
            continue
        
        print(f"  问题: {question_text[:100]}...")
        
        # 多次测试
        test_responses = []
        for i in range(3):
            print(f"  测试 {i+1}/3:")
            
            try:
                # 调用API
                raw_response = interview.call_model_api(qwen_model, question_id, question_text)
                
                if raw_response:
                    print(f"    原始回答: '{raw_response}'")
                    
                    # 验证回答
                    is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
                    
                    if is_valid:
                        print(f"    ✓ 有效回答: {parsed_response}")
                        test_responses.append({
                            'raw': raw_response,
                            'parsed': parsed_response,
                            'valid': True
                        })
                    else:
                        print(f"    ✗ 无效回答: {error_msg}")
                        test_responses.append({
                            'raw': raw_response,
                            'parsed': None,
                            'valid': False,
                            'error': error_msg
                        })
                else:
                    print(f"    ✗ API调用失败")
                    test_responses.append({
                        'raw': None,
                        'parsed': None,
                        'valid': False,
                        'error': 'API调用失败'
                    })
                
                # 添加延迟
                time.sleep(1)
                
            except Exception as e:
                print(f"    ✗ 异常: {e}")
                test_responses.append({
                    'raw': None,
                    'parsed': None,
                    'valid': False,
                    'error': str(e)
                })
        
        # 统计结果
        valid_count = sum(1 for r in test_responses if r['valid'])
        results[question_id] = {
            'total': len(test_responses),
            'valid': valid_count,
            'responses': test_responses
        }
        
        print(f"  结果: {valid_count}/{len(test_responses)} 有效回答")
    
    # 打印总结
    print("\n=== 测试总结 ===")
    for question_id, result in results.items():
        print(f"{question_id}: {result['valid']}/{result['total']} 有效回答")
        
        # 显示无效回答的原因
        invalid_responses = [r for r in result['responses'] if not r['valid']]
        if invalid_responses:
            print(f"  无效回答示例:")
            for i, resp in enumerate(invalid_responses[:2]):  # 只显示前2个
                if resp['raw']:
                    print(f"    {i+1}. '{resp['raw'][:50]}...' - {resp.get('error', '未知错误')}")
    
    # 检查是否还有"Alright"开头的问题
    alright_count = 0
    for question_id, result in results.items():
        for resp in result['responses']:
            if resp['raw'] and resp['raw'].lower().startswith('alright'):
                alright_count += 1
    
    print(f"\n'Alright'开头回答数量: {alright_count}")
    
    if alright_count == 0:
        print("✓ 成功！没有发现'Alright'开头的回答")
    else:
        print("✗ 仍然存在'Alright'开头的回答，需要进一步优化")

if __name__ == "__main__":
    test_qwen_responses()
