#!/usr/bin/env python3
"""
运行统一多语言PCA分析
将真实国家、英文和多语言数据合并在同一PCA空间中进行公平比较
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.multilingual.unified_multilingual_pca_analysis import UnifiedMultilingualPCAAnalysis


def main():
    """主函数"""
    print("🔬 启动统一多语言PCA分析")
    print("=" * 60)
    print("📝 分析目标: 在统一PCA空间中公平比较多语言vs英文角色扮演效果")
    print("=" * 60)
    
    # 创建分析器
    analyzer = UnifiedMultilingualPCAAnalysis()
    
    # 运行完整分析
    result = analyzer.run_complete_unified_analysis()
    
    if result["success"]:
        print("\\n🎉 统一分析成功完成！")
        print("\\n📋 这次的结果是在统一PCA空间中的公平比较:")
        print("   ✅ 所有数据使用相同的PCA变换")
        print("   ✅ 距离计算在同一坐标系中进行")
        print("   ✅ 结果具有可比性和可信度")
        
        # 显示主要发现
        if "report" in result and "key_findings" in result["report"]:
            print("\\n🔍 主要发现:")
            for finding in result["report"]["key_findings"]:
                print(f"   {finding}")
        
        print(f"\\n📁 详细结果请查看: {analyzer.results_dir}")
        
    else:
        print(f"\\n❌ 分析失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()







