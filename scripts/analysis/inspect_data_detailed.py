"""
详细检查 Stage 2 和 Stage 3 的数据内容
"""

import pickle
import pandas as pd
from pathlib import Path

def inspect_stage2_detailed():
    """详细检查 Stage 2 数据"""
    print("=" * 80)
    print("Stage 2 数据详细检查")
    print("=" * 80)
    
    data_path = Path("/Users/yxy/code/LLM's values/data/roleplay_English")
    pca_file = data_path / "roleplay_pca_entity_scores_latest.pkl"
    
    with open(pca_file, 'rb') as f:
        df = pickle.load(f)
    
    print(f"\n总行数: {len(df)}")
    print(f"\ndata_source 的唯一值:")
    print(df['data_source'].value_counts())
    
    # 检查 LLM 数据
    llm_data = df[df['data_source'] == 'LLM']
    print(f"\nLLM 数据行数: {len(llm_data)}")
    
    if len(llm_data) > 0:
        print(f"\n有 model_name 的行数: {llm_data['model_name'].notna().sum()}")
        print(f"\nmodel_name 的唯一值:")
        if 'model_name' in llm_data.columns:
            print(llm_data['model_name'].dropna().unique())
        
        print(f"\nLLM 数据前10行:")
        print(llm_data.head(10))
        
        # 检查国家覆盖
        if 'Country' in llm_data.columns:
            print(f"\nLLM 角色扮演的国家数量: {llm_data['Country'].nunique()}")
            print(f"\n国家列表:")
            print(sorted(llm_data['Country'].dropna().unique()[:20]))
    
def inspect_stage3_detailed():
    """详细检查 Stage 3 数据"""
    print("\n\n" + "=" * 80)
    print("Stage 3 数据详细检查")
    print("=" * 80)
    
    data_path = Path("/Users/yxy/code/LLM's values/data/roleplay_multilingual")
    pca_file = data_path / "multilingual_entity_scores_pca_fixed_20251019_151819.pkl"
    
    with open(pca_file, 'rb') as f:
        df = pickle.load(f)
    
    print(f"\n总行数: {len(df)}")
    print(f"\ndata_source 的唯一值:")
    print(df['data_source'].value_counts())
    
    # 检查 LLM 数据
    llm_data = df[df['data_source'] == 'LLM']
    print(f"\nLLM 数据行数: {len(llm_data)}")
    
    if len(llm_data) > 0:
        print(f"\n有 model_name 的行数: {llm_data['model_name'].notna().sum()}")
        print(f"\nmodel_name 的唯一值:")
        if 'model_name' in llm_data.columns:
            print(llm_data['model_name'].dropna().unique())
        
        print(f"\n有 language 的行数: {llm_data['language'].notna().sum()}")
        print(f"\nlanguage 的唯一值:")
        if 'language' in llm_data.columns:
            print(llm_data['language'].dropna().unique())
        
        # 检查英文数据
        if 'language' in llm_data.columns:
            english_data = llm_data[llm_data['language'] == 'English']
            print(f"\n英文数据行数: {len(english_data)}")
            
            if len(english_data) > 0:
                print(f"\n英文数据前10行:")
                print(english_data.head(10))
                
                # 检查国家覆盖
                if 'Country' in english_data.columns:
                    print(f"\n英文角色扮演的国家数量: {english_data['Country'].nunique()}")
                    print(f"\n国家列表:")
                    print(sorted(english_data['Country'].dropna().unique()))
        
        print(f"\nLLM 数据前10行:")
        print(llm_data.head(10))

if __name__ == "__main__":
    inspect_stage2_detailed()
    inspect_stage3_detailed()






