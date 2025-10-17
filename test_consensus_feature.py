#!/usr/bin/env python3
"""
测试多次提问取众数功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.roleplay_English.llm_country_roleplay_interview import LLMCountryRoleplayInterview

def test_consensus_feature():
    """测试多次提问取众数功能"""
    print("🔧 测试多次提问取众数功能")
    print("=" * 60)
    
    try:
        # 创建访谈对象，启用3次提问取众数
        interview = LLMCountryRoleplayInterview(
            repeat_count=1,  # 重试次数
            data_path="data",
            consensus_count=3  # 每个问题提问3次取众数
        )
        
        print(f"✅ 创建访谈对象成功")
        print(f"   重试次数: {interview.repeat_count}")
        print(f"   众数次数: {interview.consensus_count}")
        
        # 检查可用模型
        available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
        print(f"🤖 可用模型: {available_models}")
        
        if not available_models:
            print("❌ 没有可用模型，无法测试")
            return 1
        
        # 测试单个问题的众数功能
        test_model = available_models[0]
        test_country = "China"
        
        print(f"\n🔄 测试 {test_model} 扮演 {test_country}...")
        
        # 创建系统提示词
        system_prompt = interview._create_country_system_prompt(test_country)
        
        # 测试单个问题（选择一个简单的问题）
        test_question = "A008"  # 重要性：宗教
        
        print(f"📋 测试问题: {test_question}")
        
        # 使用众数方法
        response = interview._ask_question_with_consensus(
            test_model, test_question, system_prompt
        )
        
        print(f"\n📊 最终结果:")
        print(f"   问题: {test_question}")
        print(f"   回答: {response.response}")
        print(f"   原始回答: {response.raw_response}")
        print(f"   是否有效: {response.is_valid}")
        
        if response.is_valid:
            print("✅ 多次提问取众数功能测试成功！")
            return 0
        else:
            print("❌ 测试失败，回答无效")
            return 1
            
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = test_consensus_feature()
    sys.exit(exit_code)


