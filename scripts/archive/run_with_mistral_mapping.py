#!/usr/bin/env python3
"""
运行roleplay系统，自动处理mistral模型映射
"""

import sys
import os
from pathlib import Path

# 添加src目录到路径
sys.path.append('src')

from full_concurrent_roleplay import FullConcurrentRoleplaySystem

def main():
    """主函数"""
    print("=== 启动 Roleplay 访谈系统（支持 Mistral 模型映射）===")
    
    # 创建系统
    system = FullConcurrentRoleplaySystem(
        max_workers=8, 
        checkpoint_interval=10, 
        repeat_count=3
    )
    
    # 获取国家列表
    countries = system.load_countries_from_pca()
    
    print("\\n系统配置:")
    print(f"  最大工作线程: {system.max_workers}")
    print(f"  检查点间隔: {system.checkpoint_interval}")
    print(f"  每个问题重复次数: {system.repeat_count}")
    print(f"  模型数量: {len(system.models)}")
    print(f"  国家数量: {len(countries)}")
    
    # 显示模型列表
    print("\\n模型列表:")
    for i, model in enumerate(system.models, 1):
        print(f"  {i}. {model}")
    
    # 显示国家数量
    print(f"\\n国家数量: {len(countries)}")
    
    # 加载检查点
    if system.load_checkpoint():
        print(f"\\n已加载检查点，跳过 {len(system.completed_tasks)} 个已完成任务")
        
        # 显示每个模型的完成情况
        print("\\n各模型完成情况:")
        for model in system.models:
            model_tasks = [task for task in system.completed_tasks if task[0] == model]
            print(f"  {model}: {len(model_tasks)} 个国家")
    
    # 计算剩余任务
    total_tasks = len(system.models) * len(countries)
    remaining_tasks = total_tasks - len(system.completed_tasks)
    
    print(f"\\n任务统计:")
    print(f"  总任务数: {total_tasks}")
    print(f"  已完成: {len(system.completed_tasks)}")
    print(f"  剩余: {remaining_tasks}")
    
    if remaining_tasks == 0:
        print("\\n✅ 所有任务已完成！")
        return
    
    # 确认是否继续
    try:
        response = input(f"\\n是否开始运行剩余 {remaining_tasks} 个任务？(y/n): ").strip().lower()
        if response not in ['y', 'yes', '是']:
            print("取消运行")
            return
    except (EOFError, KeyboardInterrupt):
        print("\\n取消运行")
        return
    
    # 运行系统
    try:
        print("\\n🚀 开始运行系统...")
        system.run_concurrent_interviews()
        
        print("\\n✅ 系统运行完成！")
        
        # 显示最终统计
        print(f"\\n最终统计:")
        print(f"  总结果数: {len(system.results)}")
        print(f"  已完成任务: {len(system.completed_tasks)}")
        
    except KeyboardInterrupt:
        print("\\n\\n⚠️  用户中断，系统已停止")
        print("可以稍后重新运行，系统会自动从检查点继续")
    except Exception as e:
        print(f"\\n❌ 系统运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
