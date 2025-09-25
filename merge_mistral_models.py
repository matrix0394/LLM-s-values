#!/usr/bin/env python3
"""
合并 mistralai/mistral-nemo:free 和 mistralai/mistral-nemo 的回答文件
"""

import os
import json
import pickle
import shutil
from pathlib import Path

def merge_mistral_models():
    """合并两个mistral模型的回答文件"""
    
    # 源目录和目标目录
    free_dir = Path("data/llm_responses_roleplay/mistralai_mistral-nemo:free")
    paid_dir = Path("data/llm_responses_roleplay/mistralai_mistral-nemo")
    merged_dir = Path("data/llm_responses_roleplay/mistralai_mistral-nemo_merged")
    
    print("=== 合并 Mistral 模型回答文件 ===")
    
    # 创建合并目录
    merged_dir.mkdir(parents=True, exist_ok=True)
    
    # 统计信息
    free_count = 0
    paid_count = 0
    merged_count = 0
    
    # 首先复制所有free版本的文件
    if free_dir.exists():
        print(f"复制 free 版本文件从: {free_dir}")
        for file_path in free_dir.glob("*.json"):
            country_name = file_path.stem
            target_file = merged_dir / f"{country_name}.json"
            shutil.copy2(file_path, target_file)
            
            # 同时复制pkl文件
            pkl_file = free_dir / f"{country_name}.pkl"
            if pkl_file.exists():
                target_pkl = merged_dir / f"{country_name}.pkl"
                shutil.copy2(pkl_file, target_pkl)
            
            free_count += 1
            print(f"  复制: {country_name}")
    
    # 然后复制paid版本的文件（如果存在且free版本没有）
    if paid_dir.exists():
        print(f"\\n复制 paid 版本文件从: {paid_dir}")
        for file_path in paid_dir.glob("*.json"):
            country_name = file_path.stem
            target_file = merged_dir / f"{country_name}.json"
            
            # 如果free版本没有这个国家，则复制paid版本
            if not target_file.exists():
                shutil.copy2(file_path, target_file)
                
                # 同时复制pkl文件
                pkl_file = paid_dir / f"{country_name}.pkl"
                if pkl_file.exists():
                    target_pkl = merged_dir / f"{country_name}.pkl"
                    shutil.copy2(pkl_file, target_pkl)
                
                paid_count += 1
                print(f"  复制: {country_name} (paid版本)")
            else:
                print(f"  跳过: {country_name} (free版本已存在)")
    
    # 统计合并后的文件数量
    merged_count = len(list(merged_dir.glob("*.json")))
    
    print(f"\\n=== 合并完成 ===")
    print(f"Free版本文件: {free_count}")
    print(f"Paid版本文件: {paid_count}")
    print(f"合并后总文件: {merged_count}")
    print(f"合并目录: {merged_dir}")
    
    return merged_dir

def update_checkpoint_for_merged_model():
    """更新检查点文件，将mistral-nemo:free的完成状态转移到mistral-nemo"""
    
    checkpoint_file = Path("data/llm_responses_roleplay/roleplay_checkpoint.json")
    
    if not checkpoint_file.exists():
        print("没有找到检查点文件，创建新的检查点")
        # 创建新的检查点文件
        checkpoint = {
            'timestamp': '2024-01-01T00:00:00',
            'completed_tasks': [],
            'results': [],
            'total_tasks': 0,
            'total_results': 0
        }
    else:
        print("\\n=== 更新检查点文件 ===")
        # 读取检查点
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
    
    # 获取已完成的free版本任务
    completed_tasks = checkpoint.get('completed_tasks', [])
    free_completed = []
    
    # 从文件系统中获取free版本已完成的国家
    free_dir = Path("data/llm_responses_roleplay/mistralai_mistral-nemo:free")
    if free_dir.exists():
        for file_path in free_dir.glob("*.json"):
            country_name = file_path.stem
            free_task = ('mistralai/mistral-nemo:free', country_name)
            paid_task = ('mistralai/mistral-nemo', country_name)
            
            if free_task not in completed_tasks:
                completed_tasks.append(list(free_task))
                print(f"  添加free任务: {free_task}")
            
            if paid_task not in completed_tasks:
                completed_tasks.append(list(paid_task))
                print(f"  添加paid任务: {paid_task}")
    
    # 更新检查点
    checkpoint['completed_tasks'] = completed_tasks
    checkpoint['total_tasks'] = len(completed_tasks)
    
    # 保存更新后的检查点
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    print(f"更新检查点完成，总任务数: {checkpoint['total_tasks']}")

def create_merged_model_config():
    """创建合并后的模型配置"""
    
    print("\\n=== 跳过创建合并模型配置 ===")
    print("注意: mistralai/mistral-nemo_merged 不是真实的API模型，不需要添加到配置中")
    print("合并后的文件已保存在 data/llm_responses_roleplay/mistralai_mistral-nemo_merged/ 目录中")

if __name__ == "__main__":
    # 执行合并
    merged_dir = merge_mistral_models()
    
    # 更新检查点
    update_checkpoint_for_merged_model()
    
    # 创建合并模型配置
    create_merged_model_config()
    
    print("\\n=== 所有操作完成 ===")
    print("现在可以运行系统，它会自动跳过已完成的mistral-nemo:free任务")
