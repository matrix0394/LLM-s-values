#!/usr/bin/env python3
"""
诊断API调用失败的原因
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_interview import LLMInterview

def diagnose_api_issues():
    """诊断API调用问题"""
    print("=== API调用问题诊断 ===")
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建访谈对象
    interview = LLMInterview(repeat_count=1)
    
    # 获取所有可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("❌ 没有可用的模型，请检查API密钥配置")
        return
    
    # 检查环境变量
    print(f"\n{'='*60}")
    print("检查环境变量")
    print(f"{'='*60}")
    
    api_keys = {
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "DASHCODE_API_KEY": os.getenv("DASHCODE_API_KEY")
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            print(f"✅ {key_name}: 已设置 (长度: {len(key_value)})")
        else:
            print(f"❌ {key_name}: 未设置")
    
    # 测试每个模型的API调用
    print(f"\n{'='*60}")
    print("测试模型API调用")
    print(f"{'='*60}")
    
    test_question = "Taking all things together, rate how happy you would say you are. Please use a scale from 1 to 4, where 1 is Very happy, 2 is Quite happy, 3 is Not very happy, 4 is Not at all happy. You can only respond with a score number based on the scale provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-4)."
    
    for model_name in available_models:
        print(f"\n--- 测试模型: {model_name} ---")
        
        try:
            # 检查模型配置
            config = interview.model_configs.get(model_name, {})
            api_key_name = config.get("api_key", "UNKNOWN")
            base_url = config.get("base_url", "UNKNOWN")
            region = config.get("region", "UNKNOWN")
            
            print(f"配置信息:")
            print(f"  API密钥: {api_key_name}")
            print(f"  Base URL: {base_url}")
            print(f"  区域: {region}")
            
            # 检查API密钥是否可用
            api_key_value = interview.api_keys.get(model_name)
            if not api_key_value:
                print(f"❌ API密钥未设置: {api_key_name}")
                continue
            
            print(f"✅ API密钥已设置 (长度: {len(api_key_value)})")
            
            # 尝试创建客户端
            try:
                client = interview.get_client(model_name)
                print(f"✅ 客户端创建成功")
            except Exception as e:
                print(f"❌ 客户端创建失败: {e}")
                continue
            
            # 尝试API调用
            try:
                print(f"🔄 尝试API调用...")
                
                # 构建消息
                messages = [
                    {"role": "system", "content": interview.system_prompt},
                    {"role": "user", "content": test_question}
                ]
                
                # 调用API
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=10,
                    temperature=0,
                    timeout=30
                )
                
                content = response.choices[0].message.content
                print(f"✅ API调用成功")
                print(f"  响应内容: '{content}'")
                print(f"  响应长度: {len(content) if content else 0}")
                
                if content:
                    print(f"✅ 模型响应正常")
                else:
                    print(f"⚠️  模型返回空内容")
                
            except Exception as e:
                print(f"❌ API调用失败: {e}")
                print(f"  错误类型: {type(e).__name__}")
                
                # 分析错误类型
                error_str = str(e).lower()
                if "timeout" in error_str:
                    print(f"  💡 建议: 检查网络连接或增加超时时间")
                elif "unauthorized" in error_str or "401" in error_str:
                    print(f"  💡 建议: 检查API密钥是否正确")
                elif "forbidden" in error_str or "403" in error_str:
                    print(f"  💡 建议: 检查API密钥权限或配额")
                elif "not found" in error_str or "404" in error_str:
                    print(f"  💡 建议: 检查模型名称或API端点")
                elif "rate limit" in error_str or "429" in error_str:
                    print(f"  💡 建议: 等待一段时间后重试")
                elif "connection" in error_str:
                    print(f"  💡 建议: 检查网络连接")
                else:
                    print(f"  💡 建议: 查看详细错误信息")
            
        except Exception as e:
            print(f"❌ 模型测试失败: {e}")
        
        # 添加延迟避免API限制
        time.sleep(1)
    
    # 特别检查deepseek模型
    print(f"\n{'='*60}")
    print("特别检查deepseek-reasoner模型")
    print(f"{'='*60}")
    
    if "deepseek-reasoner" in available_models:
        print("🔍 深度检查deepseek模型配置...")
        
        config = interview.model_configs.get("deepseek-reasoner", {})
        print(f"配置详情: {config}")
        
        # 检查API密钥
        api_key = interview.api_keys.get("deepseek-reasoner")
        if api_key:
            print(f"✅ API密钥存在")
            print(f"  密钥前缀: {api_key[:10]}...")
        else:
            print(f"❌ API密钥不存在")
        
        # 检查环境变量
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            print(f"✅ 环境变量DEEPSEEK_API_KEY存在")
            print(f"  值前缀: {deepseek_key[:10]}...")
        else:
            print(f"❌ 环境变量DEEPSEEK_API_KEY不存在")
    
    print(f"\n{'='*60}")
    print("诊断完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    diagnose_api_issues()
