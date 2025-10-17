#!/usr/bin/env python3
"""
演示Roleplay English Analysis Runner的功能
展示完整的访谈 -> 数据处理 -> PCA分析流程
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.run.run_roleplay_english_analysis import RoleplayEnglishAnalysisRunner

def demo_analysis_mode():
    """演示仅分析模式"""
    print("🎭 Roleplay English Analysis Runner - 演示")
    print("=" * 60)
    
    try:
        # 创建分析运行器
        runner = RoleplayEnglishAnalysisRunner()
        
        print("\n📊 演示仅分析模式（使用现有数据）...")
        
        # 运行仅分析模式
        success = runner.run_complete_analysis(
            test_mode=True,
            force_restart=False,
            skip_interview=True  # 跳过访谈，直接分析现有数据
        )
        
        if success:
            print("\n🎊 演示完成!")
            print("\n✨ 功能展示:")
            print("  ✅ 数据处理 - 处理访谈结果为IVS格式")
            print("  ✅ PCA分析 - 与IVS数据联合分析")
            print("  ✅ 数据验证 - 检查数据完整性")
            print("  ✅ 可视化支持 - 生成文化地图")
            return 0
        else:
            print("\n⚠️ 演示失败，请检查错误信息")
            return 1
            
    except Exception as e:
        print(f"\n💥 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

def demo_interview_mode():
    """演示访谈模式（仅显示功能，不实际运行）"""
    print("\n🎭 访谈模式功能展示:")
    print("=" * 50)
    
    runner = RoleplayEnglishAnalysisRunner()
    
    print("🌍 支持的国家数量:", len(runner._get_all_countries()))
    print("🤖 可用模型数量:", len(runner.available_models))
    print("📋 测试国家（每个文化区域1个）:")
    
    test_countries = runner._get_test_countries_by_region()
    for region, country in test_countries.items():
        print(f"  • {region}: {country}")
    
    print("\n🚀 访谈功能特性:")
    print("  ✅ 支持109个国家的角色扮演")
    print("  ✅ 支持7个不同的LLM模型")
    print("  ✅ 测试模式：每个文化区域1个国家")
    print("  ✅ 完整模式：所有109个国家")
    print("  ✅ 断点续传：支持中断后继续")
    print("  ✅ 并发处理：提高访谈效率")

if __name__ == "__main__":
    print("🎯 Roleplay English Analysis 功能演示")
    print("=" * 60)
    
    # 演示访谈功能
    demo_interview_mode()
    
    # 演示分析功能
    exit_code = demo_analysis_mode()
    
    print("\n📝 使用说明:")
    print("要运行完整的访谈功能，请使用:")
    print("  python3 src/run/run_roleplay_english_analysis.py")
    print("\n选择模式:")
    print("  1. 测试模式 - 快速测试（推荐）")
    print("  2. 完整模式 - 完整研究数据收集")
    print("  3. 仅分析模式 - 分析现有数据")
    
    sys.exit(exit_code)








