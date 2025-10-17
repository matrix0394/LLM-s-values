#!/usr/bin/env python3
"""
非交互式多语言vs英文对比实验
直接运行实验，不需要用户确认
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from run_multilingual_vs_english_complete import MultilingualVsEnglishExperiment


def main():
    """主函数"""
    print("🚀 启动多语言vs英文文化坐标对比实验 (非交互式)")
    
    # 检查API密钥
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ 请设置 OPENROUTER_API_KEY 环境变量")
        print("   export OPENROUTER_API_KEY=your_api_key")
        return
    
    experiment = MultilingualVsEnglishExperiment()
    
    # 显示实验计划
    total_calls = len(experiment.test_countries) * len(experiment.test_models) * experiment.repeat_count
    print(f"\\n📊 实验计划:")
    print(f"   国家数: {len(experiment.test_countries)}")
    print(f"   模型数: {len(experiment.test_models)}")
    print(f"   重复次数: {experiment.repeat_count}")
    print(f"   总API调用: {total_calls}")
    print(f"   预计费用: ~${total_calls * 0.01:.2f} (估算)")
    
    print("\\n🎬 开始实验...")
    
    # 运行实验
    result = experiment.run_complete_experiment()
    
    if result["success"]:
        print("\\n🎉 实验成功完成！")
        print(f"\\n📁 结果文件:")
        for key, path in result["file_paths"].items():
            print(f"   {key}: {path}")
        
        summary = result["summary"]
        print(f"\\n📈 实验摘要:")
        print(f"   多语言样本: {summary['multilingual_samples']}")
        print(f"   英文样本: {summary['english_samples']}")
        print(f"   真实国家: {summary['real_countries']}")
        print(f"   更好的方法: {summary['better_method']}")
        
    else:
        print(f"\\n❌ 实验失败: {result['error']}")


if __name__ == "__main__":
    main()







