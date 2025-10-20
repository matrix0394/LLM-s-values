"""
检查 Stage 2 和 Stage 3 的数据结构
"""

import pickle
import pandas as pd
from pathlib import Path

def inspect_stage2():
    """检查 Stage 2 数据"""
    print("=" * 80)
    print("Stage 2 数据结构")
    print("=" * 80)
    
    data_path = Path("/Users/yxy/code/LLM's values/data/roleplay_English")
    pca_file = data_path / "roleplay_pca_entity_scores_latest.pkl"
    
    with open(pca_file, 'rb') as f:
        data = pickle.load(f)
    
    print(f"\n数据类型: {type(data)}")
    
    if isinstance(data, pd.DataFrame):
        print(f"\nDataFrame shape: {data.shape}")
        print(f"\nColumns: {data.columns.tolist()}")
        print(f"\n前5行:")
        print(data.head())
        print(f"\nIndex类型: {type(data.index)}")
        print(f"\n前10个索引:")
        print(data.index[:10].tolist())
    elif isinstance(data, dict):
        print(f"\nKeys: {data.keys()}")
        for key in data.keys():
            print(f"\n{key} 类型: {type(data[key])}")
            if isinstance(data[key], list) and len(data[key]) > 0:
                print(f"  第一个元素: {data[key][0]}")
    
def inspect_stage3():
    """检查 Stage 3 数据"""
    print("\n\n" + "=" * 80)
    print("Stage 3 数据结构")
    print("=" * 80)
    
    data_path = Path("/Users/yxy/code/LLM's values/data/roleplay_multilingual")
    pca_file = data_path / "multilingual_entity_scores_pca_fixed_20251019_151819.pkl"
    
    with open(pca_file, 'rb') as f:
        data = pickle.load(f)
    
    print(f"\n数据类型: {type(data)}")
    
    if isinstance(data, pd.DataFrame):
        print(f"\nDataFrame shape: {data.shape}")
        print(f"\nColumns: {data.columns.tolist()}")
        print(f"\n前5行:")
        print(data.head())
        print(f"\nIndex类型: {type(data.index)}")
        print(f"\n前10个索引:")
        print(data.index[:10].tolist())
        
        # 检查是否有英文数据
        if 'entity' in data.columns or 'entity_name' in data.columns:
            entity_col = 'entity' if 'entity' in data.columns else 'entity_name'
            print(f"\n包含 'English' 的实体示例:")
            english_entities = data[data[entity_col].str.contains('English', na=False)]
            if len(english_entities) > 0:
                print(english_entities.head(10))
            else:
                print("没有找到包含 'English' 的实体")
                print("\n所有实体示例:")
                print(data[entity_col].head(10).tolist())
    elif isinstance(data, dict):
        print(f"\nKeys: {data.keys()}")
        for key in data.keys():
            print(f"\n{key} 类型: {type(data[key])}")
            if isinstance(data[key], list) and len(data[key]) > 0:
                print(f"  第一个元素: {data[key][0]}")

if __name__ == "__main__":
    inspect_stage2()
    inspect_stage3()






