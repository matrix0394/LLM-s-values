#!/usr/bin/env python3
"""
修复mistral模型映射，确保正确的任务数量
"""

import json
from pathlib import Path

def fix_mistral_mapping():
    """修复mistral模型映射"""
    
    checkpoint_file = Path("data/llm_responses_roleplay/roleplay_checkpoint.json")
    
    if not checkpoint_file.exists():
        print("检查点文件不存在")
        return
    
    print("=== 修复 Mistral 模型映射 ===")
    
    # 读取检查点
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        checkpoint = json.load(f)
    
    # 获取任务列表
    completed_tasks = checkpoint.get('completed_tasks', [])
    print(f"原始任务数: {len(completed_tasks)}")
    
    # 统计各模型的任务数
    model_counts = {}
    for task in completed_tasks:
        model = task[0]
        model_counts[model] = model_counts.get(model, 0) + 1
    
    print("\\n修复前各模型任务数:")
    for model, count in sorted(model_counts.items()):
        print(f"  {model}: {count} 个任务")
    
    # 从文件系统获取实际的free版本完成情况
    free_dir = Path("data/llm_responses_roleplay/mistralai_mistral-nemo:free")
    actual_free_countries = set()
    
    if free_dir.exists():
        for file_path in free_dir.glob("*.json"):
            country_name = file_path.stem
            actual_free_countries.add(country_name)
    
    print(f"\\n实际free版本完成的国家数: {len(actual_free_countries)}")
    
    # 重新构建任务列表
    new_tasks = []
    
    # 保留其他模型的任务
    for task in completed_tasks:
        model, country = task
        if model not in ['mistralai/mistral-nemo:free', 'mistralai/mistral-nemo']:
            new_tasks.append(task)
    
    # 添加free版本的实际任务
    for country in actual_free_countries:
        new_tasks.append(['mistralai/mistral-nemo:free', country])
    
    # 添加paid版本的映射任务（基于实际完成的free版本）
    for country in actual_free_countries:
        new_tasks.append(['mistralai/mistral-nemo', country])
    
    print(f"\\n修复后任务数: {len(new_tasks)}")
    
    # 统计修复后各模型的任务数
    model_counts_new = {}
    for task in new_tasks:
        model = task[0]
        model_counts_new[model] = model_counts_new.get(model, 0) + 1
    
    print("\\n修复后各模型任务数:")
    for model, count in sorted(model_counts_new.items()):
        print(f"  {model}: {count} 个任务")
    
    # 更新检查点
    checkpoint['completed_tasks'] = new_tasks
    checkpoint['total_tasks'] = len(new_tasks)
    
    # 保存修复后的检查点
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    print(f"\\n检查点已修复，总任务数: {checkpoint['total_tasks']}")

if __name__ == "__main__":
    fix_mistral_mapping()
