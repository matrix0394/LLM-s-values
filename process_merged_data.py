import json
import pandas as pd
import pickle
from pathlib import Path

def process_merged_responses():
    """直接处理已合并的响应数据"""
    
    # 加载汇总数据
    data_dir = Path("data/llm_responses")
    with open(data_dir / "all_models_responses.json", 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    # 转换为DataFrame
    df = pd.DataFrame(all_data['responses'])
    
    print(f"成功加载数据:")
    print(f"- 模型数量: {all_data['total_models']}")
    print(f"- 总响应数: {all_data['total_responses']}")
    print(f"- 有效响应: {all_data['valid_responses']}")
    print(f"- 模型列表: {', '.join(all_data['models'])}")
    
    # 保存为DataFrame格式供后续处理
    df.to_pickle(data_dir / "merged_responses_df.pkl")
    print(f"\n✅ 已保存DataFrame格式到: merged_responses_df.pkl")
    
    return df

if __name__ == "__main__":
    df = process_merged_responses()
    print(f"\nDataFrame形状: {df.shape}")
    print(f"列名: {list(df.columns)}")