#!/usr/bin/env python3
"""
多语言角色扮演演示脚本
快速演示多语言功能，不需要真实的API调用
"""

import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))
sys.path.append('src/roleplay')

from multilingual_roleplay_interview import MultilingualRoleplayInterview

def demo_multilingual_questions():
    """演示多语言问题"""
    print("🌍 多语言角色扮演问题演示")
    print("=" * 60)
    
    # 创建访谈实例
    interviewer = MultilingualRoleplayInterview()
    
    if not interviewer.multilingual_config:
        print("❌ 多语言配置加载失败")
        return
    
    # 显示每种语言的配置
    for lang_code, lang_config in interviewer.multilingual_config["languages"].items():
        print(f"\\n📝 {lang_config['name']} ({lang_code})")
        print(f"🏁 目标国家: {', '.join(lang_config['countries'])}")
        print(f"❓ 问题数量: {len(lang_config['questions'])}")
        
        # 显示系统提示词示例
        if lang_code in interviewer.system_prompts:
            system_prompt = interviewer.system_prompts[lang_code]
            print(f"🤖 系统提示词: {system_prompt[:100]}...")
        
        # 显示几个问题示例
        print("📋 问题示例:")
        questions = lang_config["questions"]
        sample_questions = ["A008", "F063", "Y002"]  # 选择几个代表性问题
        
        for qid in sample_questions:
            if qid in questions:
                q = questions[qid]
                print(f"   {qid}: {q['question'][:150]}...")
                print(f"        量表: {q['scale']}")
        
        print("-" * 60)

def demo_country_context():
    """演示国家文化背景"""
    print("\\n🏛️ 国家文化背景演示")
    print("=" * 60)
    
    interviewer = MultilingualRoleplayInterview()
    
    # 演示每种语言对应国家的文化背景
    test_cases = [
        ("zh-cn", "China"),
        ("ru", "Russian Federation"),
        ("es-la", "Mexico"),
        ("ar", "Egypt")
    ]
    
    for lang_code, country in test_cases:
        context = interviewer._get_country_context(country, lang_code)
        print(f"\\n🌏 {country} ({lang_code}):")
        print(f"   {context}")

def demo_roleplay_prompt():
    """演示完整的角色扮演提示词"""
    print("\\n🎭 角色扮演提示词演示")
    print("=" * 60)
    
    interviewer = MultilingualRoleplayInterview()
    
    # 为每种语言生成完整的角色扮演提示词
    test_cases = [
        ("zh-cn", "China"),
        ("ru", "Russian Federation"),
        ("es-la", "Mexico"),
        ("ar", "Egypt")
    ]
    
    for lang_code, country in test_cases:
        prompt = interviewer._create_roleplay_prompt(country, lang_code)
        print(f"\\n🎯 {country} ({lang_code}) 角色扮演提示词:")
        print(f"   {prompt[:200]}...")
        print("-" * 40)

def main():
    """主演示函数"""
    print("🚀 多语言角色扮演系统演示")
    print("这个演示将展示多语言功能的各个组件")
    print()
    
    try:
        # 演示1: 多语言问题
        demo_multilingual_questions()
        
        # 演示2: 国家文化背景
        demo_country_context()
        
        # 演示3: 角色扮演提示词
        demo_roleplay_prompt()
        
        print("\\n🎉 演示完成！")
        print("\\n📝 总结:")
        print("✅ 支持4种语言: 简体中文、俄语、拉美西语、阿拉伯语")
        print("✅ 覆盖8个目标国家")
        print("✅ 每种语言包含10个IVS问题")
        print("✅ 每种语言都有定制的系统提示词和文化背景")
        
        print("\\n🚀 准备运行真实实验:")
        print("   python start_multilingual_experiment.py")
        
    except Exception as e:
        print(f"❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()







