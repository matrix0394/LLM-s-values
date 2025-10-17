#!/usr/bin/env python3
"""
多语言角色扮演功能测试脚本
"""

import sys
import os
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

def test_config_loading():
    """测试配置文件加载"""
    print("=== 测试配置文件加载 ===")
    
    config_path = Path("config/multilingual_questions_complete.json")
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置文件加载成功")
        
        # 检查结构
        if "languages" not in config:
            print("❌ 配置文件缺少 'languages' 字段")
            return False
        
        print(f"✅ 找到 {len(config['languages'])} 种语言")
        
        for lang_code, lang_config in config["languages"].items():
            print(f"  📝 {lang_config['name']} ({lang_code})")
            print(f"     国家: {', '.join(lang_config['countries'])}")
            print(f"     问题数: {len(lang_config['questions'])}")
            
            # 检查问题结构
            if lang_config['questions']:
                first_question = list(lang_config['questions'].values())[0]
                required_fields = ['code', 'question', 'scale', 'dimension']
                missing_fields = [field for field in required_fields if field not in first_question]
                if missing_fields:
                    print(f"     ❌ 缺少字段: {missing_fields}")
                else:
                    print(f"     ✅ 问题结构完整")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def test_multilingual_module():
    """测试多语言模块导入"""
    print("\\n=== 测试多语言模块导入 ===")
    
    try:
        # 尝试导入模块
        sys.path.append('src/roleplay')
        from multilingual_roleplay_interview import MultilingualRoleplayInterview
        
        print("✅ 多语言模块导入成功")
        
        # 创建实例
        interviewer = MultilingualRoleplayInterview()
        print("✅ 多语言访谈实例创建成功")
        
        # 检查配置加载
        if interviewer.multilingual_config:
            print(f"✅ 多语言配置加载成功，包含 {len(interviewer.multilingual_config.get('languages', {}))} 种语言")
        else:
            print("❌ 多语言配置加载失败")
            return False
        
        # 检查系统提示词
        if interviewer.system_prompts:
            print(f"✅ 系统提示词加载成功，包含 {len(interviewer.system_prompts)} 种语言")
        else:
            print("❌ 系统提示词加载失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 多语言模块测试失败: {e}")
        return False

def test_question_extraction():
    """测试问题提取"""
    print("\\n=== 测试问题内容 ===")
    
    config_path = Path("config/multilingual_questions_complete.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 检查每种语言的问题
    question_ids = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
    
    for lang_code, lang_config in config["languages"].items():
        print(f"\\n📝 {lang_config['name']} ({lang_code}):")
        
        questions = lang_config["questions"]
        missing_questions = [qid for qid in question_ids if qid not in questions]
        
        if missing_questions:
            print(f"  ❌ 缺少问题: {missing_questions}")
        else:
            print(f"  ✅ 所有10个问题都存在")
        
        # 显示第一个问题作为示例
        if questions:
            first_qid = list(questions.keys())[0]
            first_q = questions[first_qid]
            print(f"  📄 示例问题 {first_qid}: {first_q['question'][:100]}...")
    
    return True

def main():
    """主测试函数"""
    print("🧪 多语言角色扮演功能测试")
    print("=" * 50)
    
    tests = [
        ("配置文件加载", test_config_loading),
        ("多语言模块", test_multilingual_module),
        ("问题内容检查", test_question_extraction)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
    
    print("\\n" + "=" * 50)
    print(f"🏁 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！多语言功能准备就绪。")
        print("\\n下一步可以运行:")
        print("  python start_multilingual_experiment.py")
    else:
        print("⚠️  部分测试失败，请检查配置和代码。")

if __name__ == "__main__":
    main()







