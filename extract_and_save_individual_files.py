#!/usr/bin/env python3
"""
从roleplay_results.pkl中提取数据并保存到每个模型对应的pkl文件中
"""

import pickle
import os
import json
from pathlib import Path

def load_roleplay_results():
    """加载roleplay_results.json文件"""
    json_file = 'data/llm_responses_roleplay/roleplay_results.json'
    
    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        return None
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 成功加载 {json_file}")
        print(f"文件大小: {os.path.getsize(json_file)} 字节")
        print(f"数据类型: {type(data)}")
        
        if isinstance(data, dict):
            print(f"字典键: {list(data.keys())}")
            if 'results' in data:
                print(f"results长度: {len(data['results'])}")
                return data['results']
            else:
                print("❌ 没有找到'results'键")
                return None
        else:
            print("❌ 数据不是字典格式")
            return None
            
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        return None

def extract_and_save_individual_files(results):
    """从results中提取数据并保存到各个模型目录"""
    if not results:
        print("❌ 没有数据可处理")
        return
    
    print(f"\n=== 开始提取和保存数据 ===")
    
    # 统计信息
    model_stats = {}
    total_processed = 0
    
    for result in results:
        model = result.get('model', '')
        country = result.get('country', '')
        responses = result.get('responses', [])
        
        if not model or not country or not responses:
            continue
        
        # 统计
        if model not in model_stats:
            model_stats[model] = 0
        model_stats[model] += 1
        total_processed += 1
        
        # 创建模型目录
        model_dir_name = model.replace('/', '_')
        model_dir = Path(f"data/llm_responses_roleplay/{model_dir_name}")
        model_dir.mkdir(exist_ok=True)
        
        # 处理responses（从字符串转换为字典列表）
        processed_responses = []
        for response_str in responses:
            if isinstance(response_str, str):
                # 解析LLMResponse字符串
                try:
                    import re
                    # 提取各个字段
                    question_match = re.search(r"question_id='([^']+)'", response_str)
                    response_match = re.search(r"response=([^,)]+)", response_str)
                    raw_response_match = re.search(r"raw_response='([^']*)'", response_str)
                    is_valid_match = re.search(r"is_valid=([^,)]+)", response_str)
                    error_message_match = re.search(r"error_message=([^,)]+)", response_str)
                    
                    if question_match:
                        response_dict = {
                            'question_id': question_match.group(1),
                            'response': response_match.group(1) if response_match else None,
                            'raw_response': raw_response_match.group(1) if raw_response_match else None,
                            'is_valid': is_valid_match.group(1) == 'True' if is_valid_match else False,
                            'error_message': error_message_match.group(1) if error_message_match else None
                        }
                        processed_responses.append(response_dict)
                except Exception as e:
                    print(f"    警告: 解析响应失败 {country}: {e}")
                    continue
            else:
                processed_responses.append(response_str)
        
        # 保存JSON文件
        json_file = model_dir / f"{country.replace(' ', '_')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(processed_responses, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存PKL文件
        pkl_file = model_dir / f"{country.replace(' ', '_')}.pkl"
        with open(pkl_file, 'wb') as f:
            pickle.dump(processed_responses, f)
        
        if total_processed % 50 == 0:
            print(f"  已处理 {total_processed} 个文件...")
    
    print(f"\n✅ 处理完成！")
    print(f"总共处理了 {total_processed} 个文件")
    print(f"\n各模型统计:")
    for model, count in model_stats.items():
        print(f"  {model}: {count} 个国家")
    
    return model_stats

def verify_saved_files():
    """验证保存的文件"""
    print(f"\n=== 验证保存的文件 ===")
    
    data_dir = Path("data/llm_responses_roleplay")
    total_files = 0
    total_size = 0
    
    for model_dir in data_dir.iterdir():
        if model_dir.is_dir() and not model_dir.name.startswith('.'):
            model_name = model_dir.name.replace('_', '/')
            pkl_files = list(model_dir.glob("*.pkl"))
            json_files = list(model_dir.glob("*.json"))
            
            if pkl_files:
                model_size = sum(f.stat().st_size for f in pkl_files)
                print(f"  {model_name}: {len(pkl_files)} 个pkl文件, {len(json_files)} 个json文件, 总大小: {model_size} 字节")
                total_files += len(pkl_files)
                total_size += model_size
    
    print(f"\n总计: {total_files} 个pkl文件, 总大小: {total_size} 字节")

def main():
    """主函数"""
    print("=== 从roleplay_results.pkl提取并保存个别文件 ===")
    
    # 1. 加载roleplay_results.pkl
    print("\n1. 加载roleplay_results.pkl...")
    results = load_roleplay_results()
    
    if not results:
        print("❌ 无法加载数据，退出")
        return
    
    # 2. 提取并保存到各个模型目录
    print("\n2. 提取并保存数据...")
    model_stats = extract_and_save_individual_files(results)
    
    # 3. 验证保存的文件
    print("\n3. 验证保存的文件...")
    verify_saved_files()
    
    print(f"\n🎉 任务完成！")

if __name__ == "__main__":
    main()
