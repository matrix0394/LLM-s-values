#!/usr/bin/env python3
"""
清理检查点文件，移除重复任务
"""

import json
from pathlib import Path

def clean_checkpoint():
    """清理检查点文件"""
    
    checkpoint_file = Path("data/llm_responses_roleplay/roleplay_checkpoint.json")
    
    if not checkpoint_file.exists():
        print("检查点文件不存在")
        return
    
    print("=== 清理检查点文件 ===")
    
    # 读取检查点
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        checkpoint = json.load(f)
    
    # 获取任务列表
    completed_tasks = checkpoint.get('completed_tasks', [])
    print(f"原始任务数: {len(completed_tasks)}")
    
    # 去重
    unique_tasks = []
    seen_tasks = set()
    
    for task in completed_tasks:
        task_tuple = tuple(task)
        if task_tuple not in seen_tasks:
            unique_tasks.append(task)
            seen_tasks.add(task_tuple)
    
    print(f"去重后任务数: {len(unique_tasks)}")
    print(f"移除重复任务: {len(completed_tasks) - len(unique_tasks)}")
    
    # 统计各模型的任务数
    model_counts = {}
    for task in unique_tasks:
        model = task[0]
        model_counts[model] = model_counts.get(model, 0) + 1
    
    print("\\n各模型任务数:")
    for model, count in sorted(model_counts.items()):
        print(f"  {model}: {count} 个任务")
    
    # 更新检查点
    checkpoint['completed_tasks'] = unique_tasks
    checkpoint['total_tasks'] = len(unique_tasks)
    
    # 保存清理后的检查点
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    print(f"\\n检查点已清理，总任务数: {checkpoint['total_tasks']}")

if __name__ == "__main__":
    clean_checkpoint()
