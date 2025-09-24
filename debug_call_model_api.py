#!/usr/bin/env python3
"""
调试call_model_api方法
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def debug_call_model_api():
    """调试call_model_api方法"""
    print("=== 调试call_model_api方法 ===")
    print(f"调试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    model_name = "deepseek-reasoner"
    question_id = "A008"
    question_text = interview.questionnaire.questions.get_question(question_id)
    
    print(f"模型: {model_name}")
    print(f"问题ID: {question_id}")
    print(f"问题文本: {question_text[:100]}...")
    
    # 手动调用API，模拟call_model_api的逻辑
    try:
        client = interview.get_client(model_name)
        print("✅ 客户端创建成功")
        
        # 检查是否为qwen模型
        is_qwen = "qwq" in model_name.lower()
        print(f"是否为qwen模型: {is_qwen}")
        
        if is_qwen:
            system_prompt = interview.qwq_system_prompt
            max_retries = 6
        else:
            system_prompt = interview.system_prompt
            max_retries = 2
        
        print(f"系统提示词: {system_prompt[:100]}...")
        print(f"最大重试次数: {max_retries}")
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question_text}
        ]
        
        print(f"消息数量: {len(messages)}")
        
        # 检查token限制逻辑
        if "deepseek" in model_name.lower():
            max_tokens = 200  # 推理模型需要更多token
        else:
            max_tokens = 100
        
        print(f"使用的max_tokens: {max_tokens}")
        
        # 调用API
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0,
            timeout=30
        )
        
        print("✅ API调用成功")
        
        content = response.choices[0].message.content
        print(f"响应内容: '{content}'")
        print(f"响应长度: {len(content) if content else 0}")
        
        if content:
            content = content.strip()
            print(f"处理后内容: '{content}'")
            print("✅ 获得有效响应")
        else:
            print("❌ 响应为空")
            
            # 检查推理内容
            choice = response.choices[0]
            if hasattr(choice.message, 'reasoning_content') and choice.message.reasoning_content:
                print(f"推理内容: {choice.message.reasoning_content}")
            
            print(f"Finish reason: {choice.finish_reason}")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_call_model_api()
