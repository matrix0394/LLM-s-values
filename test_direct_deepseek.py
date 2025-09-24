#!/usr/bin/env python3
"""
直接测试deepseek模型API调用
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def test_direct_deepseek():
    """直接测试deepseek模型"""
    print("=== 直接测试deepseek模型API调用 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    model_name = "deepseek-reasoner"
    print(f"测试模型: {model_name}")
    
    try:
        # 获取客户端
        client = interview.get_client(model_name)
        print("✅ 客户端创建成功")
        
        # 测试简单问题
        test_question = "What is 1+1? Answer with just the number."
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer with numbers only."},
            {"role": "user", "content": test_question}
        ]
        
        print(f"测试问题: {test_question}")
        
        # 使用更大的token限制
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=200,  # 使用更大的token限制
            temperature=0,
            timeout=30
        )
        
        content = response.choices[0].message.content
        print(f"响应内容: '{content}'")
        print(f"响应长度: {len(content) if content else 0}")
        
        if content:
            print("✅ 成功获得响应")
        else:
            print("❌ 响应为空")
            
            # 检查推理内容
            choice = response.choices[0]
            if hasattr(choice.message, 'reasoning_content') and choice.message.reasoning_content:
                print(f"推理内容: {choice.message.reasoning_content}")
                print("💡 模型在推理但没有生成最终答案")
            
            print(f"Finish reason: {choice.finish_reason}")
            print(f"Usage: {response.usage}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")

if __name__ == "__main__":
    test_direct_deepseek()
