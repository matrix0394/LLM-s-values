#!/usr/bin/env python3
"""
多语言角色扮演实验启动脚本
简化版本，方便快速测试
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from scripts.experiments.multilingual_roleplay_experiment import MultilingualRoleplayExperiment


def main():
    """主函数"""
    print("=== 多语言角色扮演实验 ===")
    print("这个实验将测试大模型使用本国语言模拟不同国家价值观的效果")
    print()
    
    # 显示实验配置
    print("实验配置:")
    print("- 语言: 简体中文、俄语、拉美西语、阿拉伯语")
    print("- 目标国家:")
    print("  * 简体中文: 中国")
    print("  * 俄语: 俄罗斯")
    print("  * 拉美西语: 墨西哥、阿根廷、哥伦比亚")
    print("  * 阿拉伯语: 埃及、约旦、摩洛哥")
    print("- 默认模型: GPT-4o-mini")
    print()
    
    # 询问用户是否继续
    response = input("是否开始实验？(y/n): ").lower().strip()
    if response != 'y':
        print("实验已取消")
        return
    
    try:
        # 创建实验实例
        experiment = MultilingualRoleplayExperiment()
        
        # 运行实验（使用较小规模进行测试）
        models = ["openai/gpt-4o-mini"]  # 先用一个模型测试
        results = experiment.run_experiment(models=models, max_workers=1)  # 单线程避免API限制
        
        print("\\n=== 实验完成 ===")
        print("结果摘要:")
        
        if "analysis_results" in results:
            analysis = results["analysis_results"]
            print(f"总体成功率: {analysis['overall_stats']['overall_success_rate']:.1f}%")
            
            print("\\n各语言表现:")
            for lang, stats in analysis["language_stats"].items():
                print(f"- {lang}: {stats['success_rate']:.1f}% (测试国家: {len(stats['countries'])})")
        
        if "comparison_results" in results:
            comparison = results["comparison_results"]
            if "improvement_analysis" in comparison:
                improvement = comparison["improvement_analysis"]
                if improvement["best_performing_language"]:
                    print(f"\\n表现最佳语言: {improvement['best_performing_language']}")
        
        print("\\n详细结果已保存到 data/results/multilingual_experiments/ 目录")
        
    except Exception as e:
        print(f"实验运行出错: {e}")
        print("请检查:")
        print("1. API密钥是否正确设置")
        print("2. 网络连接是否正常")
        print("3. 多语言问题配置是否完整")


if __name__ == "__main__":
    main()







