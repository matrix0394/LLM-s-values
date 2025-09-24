import json
import pickle
import os
from datetime import datetime

def merge_new_model_responses():
    """合并新模型的响应到all_models_responses文件中"""
    
    # 文件路径
    data_dir = "data/llm_responses"
    all_json_path = os.path.join(data_dir, "all_models_responses.json")
    all_pkl_path = os.path.join(data_dir, "all_models_responses.pkl")
    
    # 使用根目录的完整备份文件
    backup_json_path = "all_models_responses.json"
    
    # 新模型文件
    new_models = [
        "mistralai-mistral-nemo-free_responses.json",
        "qwq-32b-preview_responses.json"
    ]
    
    # 从备份文件加载完整数据
    print("从备份文件恢复完整数据...")
    with open(backup_json_path, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    print(f"备份文件中的模型数量: {all_data['total_models']}")
    print(f"备份文件中的响应数量: {all_data['total_responses']}")
    print(f"备份文件中的有效响应: {all_data['valid_responses']}")
    
    # 合并新模型的响应
    for model_file in new_models:
        model_path = os.path.join(data_dir, model_file)
        
        if os.path.exists(model_path):
            with open(model_path, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
            
            model_name = model_data['model_name']
            
            # 检查模型是否已存在
            if model_name not in all_data['models']:
                print(f"添加新模型: {model_name}")
                all_data['models'].append(model_name)
                
                # 添加该模型的所有响应
                for response in model_data['responses']:
                    all_data['responses'].append(response)
                
                print(f"  - 添加了 {len(model_data['responses'])} 个响应")
                print(f"  - 有效响应: {model_data['valid_responses']}")
            else:
                print(f"模型 {model_name} 已存在，跳过")
        else:
            print(f"警告: 文件不存在 {model_path}")
    
    # 更新统计信息
    all_data['total_models'] = len(all_data['models'])
    all_data['total_responses'] = len(all_data['responses'])
    all_data['valid_responses'] = sum(1 for r in all_data['responses'] if r['is_valid'])
    all_data['timestamp'] = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\n合并后统计:")
    print(f"模型数量: {all_data['total_models']}")
    print(f"总响应数: {all_data['total_responses']}")
    print(f"有效响应: {all_data['valid_responses']}")
    
    # 保存更新后的JSON文件
    with open(all_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    # 保存更新后的PKL文件
    with open(all_pkl_path, 'wb') as f:
        pickle.dump(all_data, f)
    
    print(f"\n✅ 成功更新:")
    print(f"  - {all_json_path}")
    print(f"  - {all_pkl_path}")
    
    return all_data

if __name__ == "__main__":
    # 直接执行合并
    result = merge_new_model_responses()
    
    print("\n📊 最终模型列表:")
    for i, model in enumerate(result['models'], 1):
        print(f"  {i}. {model}")