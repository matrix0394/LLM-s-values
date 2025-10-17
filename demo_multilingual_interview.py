#!/usr/bin/env python3
"""
多语言访谈演示脚本
展示交互式选择功能，支持选择使用所有7个模型
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path.cwd()))

from src.run.run_roleplay_multilingual_analysis import RoleplayMultilingualAnalysisRunner

def main():
    """主函数"""
    print("🌐 多语言访谈演示")
    print("=" * 50)
    print("📊 当前配置:")
    print("   - 模型数量: 7个 (所有配置的模型)")
    print("   - 国家数量: 4个 (China, Russian Federation, Mexico, Egypt)")
    print("   - 语言数量: 5个 (en, zh-cn, ru, es, ar)")
    print("   - 总任务数: 7 × 4 × 5 = 140个访谈任务")
    print()
    
    try:
        # 创建运行器
        runner = RoleplayMultilingualAnalysisRunner()
        
        print("🎯 启动多语言分析...")
        print("💡 如果有现有数据，你将看到选择界面")
        print("💡 选择 '2' 将使用所有7个模型重新访谈")
        print()
        
        # 运行完整分析
        success = runner.run_complete_analysis()
        
        if success:
            print("\n🎊 分析完成!")
        else:
            print("\n⚠️ 分析过程中遇到问题")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



