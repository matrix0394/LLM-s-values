#!/usr/bin/env python3
"""
详细测试deepseek-reasoner模型的问题
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def test_deepseek_detailed():
    """详细测试deepseek模型"""
    print("=== 详细测试deepseek-reasoner模型 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    model_name = "deepseek-reasoner"
    print(f"测试模型: {model_name}")
    
    # 获取客户端
    try:
        client = interview.get_client(model_name)
        print("✅ 客户端创建成功")
    except Exception as e:
        print(f"❌ 客户端创建失败: {e}")
        return
    
    # 测试不同的提示词和参数
    test_cases = [
        {
            "name": "标准提示词",
            "system_prompt": interview.system_prompt,
            "max_tokens": 10,
            "temperature": 0
        },
        {
            "name": "简化提示词",
            "system_prompt": "You are a helpful assistant. Answer with numbers only.",
            "max_tokens": 10,
            "temperature": 0
        },
        {
            "name": "增加token限制",
            "system_prompt": interview.system_prompt,
            "max_tokens": 50,
            "temperature": 0
        },
        {
            "name": "增加温度",
            "system_prompt": interview.system_prompt,
            "max_tokens": 10,
            "temperature": 0.1
        },
        {
            "name": "更高温度",
            "system_prompt": interview.system_prompt,
            "max_tokens": 10,
            "temperature": 0.5
        }
    ]
    
    test_question = "What is 1+1? Answer with just the number."
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i}: {test_case['name']} ---")
        
        try:
            messages = [
                {"role": "system", "content": test_case["system_prompt"]},
                {"role": "user", "content": test_question}
            ]
            
            print(f"参数: max_tokens={test_case['max_tokens']}, temperature={test_case['temperature']}")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=test_case["max_tokens"],
                temperature=test_case["temperature"],
                timeout=30
            )
            
            content = response.choices[0].message.content
            print(f"响应内容: '{content}'")
            print(f"响应长度: {len(content) if content else 0}")
            
            if content:
                print("✅ 成功获得响应")
            else:
                print("❌ 响应为空")
                
                # 检查响应对象的详细信息
                print(f"响应对象: {response}")
                print(f"Choices数量: {len(response.choices)}")
                if response.choices:
                    choice = response.choices[0]
                    print(f"Choice详情: {choice}")
                    print(f"Finish reason: {choice.finish_reason}")
                    print(f"Message: {choice.message}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            print(f"错误类型: {type(e).__name__}")
        
        time.sleep(1)
    
    # 测试原始问题
    print(f"\n--- 测试原始问题 ---")
    try:
        question_text = interview.questionnaire.questions.get_question("A008")
        print(f"问题: {question_text[:100]}...")
        
        # 直接调用API
        raw_response = interview.call_model_api(model_name, "A008", question_text)
        print(f"原始回答: '{raw_response}'")
        
        if raw_response is None:
            print("❌ 返回None")
        elif raw_response == "":
            print("❌ 返回空字符串")
        else:
            print(f"✅ 返回内容: '{raw_response}'")
            
    except Exception as e:
        print(f"❌ 原始问题测试失败: {e}")

if __name__ == "__main__":
    test_deepseek_detailed()
