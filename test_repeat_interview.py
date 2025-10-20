#!/usr/bin/env python3
"""
测试重复访谈功能
演示：问卷重复5次，每次完整10个问题，最后计算众数
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview

def test_repeat_interview():
    """测试重复访谈功能"""
    print("="*80)
    print("🧪 测试重复访谈功能")
    print("="*80)
    print()
    print("📋 测试配置:")
    print("  • 模型: openai/gpt-4o-mini")
    print("  • 国家: China")
    print("  • 语言: 简体中文 (zh-cn)")
    print("  • 重复次数: 3 (测试用)")
    print("  • 问题数: 10")
    print()
    print("📊 预期行为:")
    print("  1. 完整问一遍所有10个问题 (第1轮)")
    print("  2. 再次完整问一遍所有10个问题 (第2轮)")
    print("  3. 第三次完整问一遍所有10个问题 (第3轮)")
    print("  4. 对每个问题计算众数和置信度")
    print("  5. 保存结果到 data/roleplay_multilingual/")
    print()
    
    input("按回车键开始测试...")
    
    # 初始化访谈器（重复3次，测试用）
    interviewer = MultilingualRoleplayInterview(
        repeat_count=3,
        data_path="data/roleplay_multilingual"
    )
    
    # 执行重复访谈
    try:
        result = interviewer.interview_country_multilingual_with_repeats(
            model_name="openai/gpt-4o-mini",
            country="China",
            language="zh-cn"
        )
        
        print("\n" + "="*80)
        print("✅ 测试完成！")
        print("="*80)
        
        # 显示结果摘要
        print(f"\n📊 结果摘要:")
        print(f"  模型: {result['model']}")
        print(f"  国家: {result['country']}")
        print(f"  语言: {result['language']}")
        print(f"  完成轮次: {result['repeat_count']}")
        print(f"  问题总数: {result['total_questions']}")
        print(f"  成功率: {result['success_rate']:.1f}%")
        print(f"  平均置信度: {result['average_confidence']*100:.1f}%")
        
        # 显示几个问题的详细结果
        print(f"\n📝 部分问题详情（前3个）:")
        for i, response in enumerate(result['responses'][:3]):
            print(f"\n  问题 {i+1}: {response['question_id']}")
            print(f"    所有回答: {response['all_responses']}")
            print(f"    最终众数: {response['final_response']}")
            print(f"    置信度: {response['confidence']*100:.1f}%")
            print(f"    回答分布: {response['response_distribution']}")
        
        # 保存测试结果
        import json
        from datetime import datetime
        
        output_file = Path(f"data/roleplay_multilingual/test_repeat_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整结果已保存到:")
        print(f"  {output_file}")
        
        print("\n🎯 数据结构说明:")
        print("  • result['responses']: 每个问题的汇总结果（包含众数）")
        print("  • result['all_rounds']: 每一轮的完整原始数据")
        print("  • response['final_response']: 该问题的众数")
        print("  • response['all_responses']: 该问题在所有轮次的回答")
        print("  • response['confidence']: 众数的置信度")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_single_round():
    """测试单次访谈（对比）"""
    print("\n" + "="*80)
    print("🧪 对比测试：单次访谈")
    print("="*80)
    
    interviewer = MultilingualRoleplayInterview(
        repeat_count=1,  # 单次
        data_path="data/roleplay_multilingual"
    )
    
    result = interviewer.interview_country_multilingual(
        model_name="openai/gpt-4o-mini",
        country="China",
        language="zh-cn"
    )
    
    print(f"\n📊 单次访谈结果:")
    print(f"  成功率: {result['success_rate']:.1f}%")
    print(f"  数据结构: 每个response只有processed_response（无众数）")
    
    return result

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║           重复访谈功能测试                                      ║
║                                                                ║
║  本脚本将演示:                                                 ║
║  1. 整个问卷重复3次（而不是每个问题重复3次）                   ║
║  2. 记录每一轮的完整回答                                        ║
║  3. 计算每个问题的众数和置信度                                  ║
║  4. 保存完整数据到 data/roleplay_multilingual/                ║
║                                                                ║
║  注意: 这是测试脚本，只重复3次（正式实验应该5次）               ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # 运行测试
    success = test_repeat_interview()
    
    if success:
        print("\n✅ 所有测试通过！")
        print("\n📝 接下来可以:")
        print("  1. 运行正式实验: python src/run/run_roleplay_multilingual_analysis.py")
        print("  2. 选择 '选项2: 重新访谈' 将自动使用repeat_count=5")
        print("  3. 数据将保存到 data/roleplay_multilingual/interview_data_*.json")
    else:
        print("\n❌ 测试失败，请检查错误信息")

