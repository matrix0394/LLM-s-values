import pandas as pd
import numpy as np
import os

def compare_pkl_files():
    """
    比较我们生成的country_scores_pca.pkl与参考项目的数据
    """
    # 文件路径
    our_file = r"e:\Code\value of LLM\llm_9_16\cultural_map_project\data\country_scores_pca.pkl"
    reference_file = r"e:\Code\value of LLM\llm_9_16\model_cultural_comp-main\data\country_scores_pca.pkl"
    
    print("=== PKL文件数据对比分析 ===")
    print()
    
    # 检查文件是否存在
    if not os.path.exists(our_file):
        print(f"❌ 我们的文件不存在: {our_file}")
        return
    
    if not os.path.exists(reference_file):
        print(f"❌ 参考文件不存在: {reference_file}")
        return
    
    try:
        # 加载数据
        print("📁 加载数据文件...")
        our_data = pd.read_pickle(our_file)
        reference_data = pd.read_pickle(reference_file)
        
        print("✅ 数据加载成功")
        print()
        
        # 1. 基本信息对比
        print("📊 === 基本信息对比 ===")
        print(f"我们的数据形状: {our_data.shape}")
        print(f"参考数据形状: {reference_data.shape}")
        print()
        
        print(f"我们的数据类型: {type(our_data)}")
        print(f"参考数据类型: {type(reference_data)}")
        print()
        
        # 2. 列名对比
        print("📋 === 列名对比 ===")
        our_columns = set(our_data.columns)
        ref_columns = set(reference_data.columns)
        
        print(f"我们的列名: {list(our_data.columns)}")
        print(f"参考列名: {list(reference_data.columns)}")
        print()
        
        common_columns = our_columns & ref_columns
        our_only = our_columns - ref_columns
        ref_only = ref_columns - our_columns
        
        print(f"共同列: {list(common_columns)}")
        print(f"仅我们有的列: {list(our_only)}")
        print(f"仅参考有的列: {list(ref_only)}")
        print()
        
        # 3. 数据内容对比
        print("🔍 === 数据内容对比 ===")
        
        # 检查country_code列
        if 'country_code' in our_data.columns and 'country_code' in reference_data.columns:
            our_countries = set(our_data['country_code'].unique())
            ref_countries = set(reference_data['country_code'].unique())
            
            print(f"我们的国家数量: {len(our_countries)}")
            print(f"参考国家数量: {len(ref_countries)}")
            
            common_countries = our_countries & ref_countries
            our_only_countries = our_countries - ref_countries
            ref_only_countries = ref_countries - our_countries
            
            print(f"共同国家数量: {len(common_countries)}")
            print(f"仅我们有的国家数量: {len(our_only_countries)}")
            print(f"仅参考有的国家数量: {len(ref_only_countries)}")
            
            if our_only_countries:
                print(f"仅我们有的国家（前10个）: {list(our_only_countries)[:10]}")
            if ref_only_countries:
                print(f"仅参考有的国家（前10个）: {list(ref_only_countries)[:10]}")
            print()
        
        # 4. PC分数对比（如果有共同国家）
        if 'country_code' in our_data.columns and 'country_code' in reference_data.columns:
            if common_countries:
                print("📈 === PC分数对比（共同国家） ===")
                
                # 选择共同国家进行对比
                common_list = list(common_countries)[:5]  # 取前5个国家作为示例
                
                for country in common_list:
                    our_row = our_data[our_data['country_code'] == country].iloc[0]
                    ref_row = reference_data[reference_data['country_code'] == country].iloc[0]
                    
                    print(f"\n国家: {country}")
                    
                    if 'PC1_rescaled' in our_data.columns and 'PC1_rescaled' in reference_data.columns:
                        print(f"  PC1 - 我们: {our_row['PC1_rescaled']:.4f}, 参考: {ref_row['PC1_rescaled']:.4f}")
                    
                    if 'PC2_rescaled' in our_data.columns and 'PC2_rescaled' in reference_data.columns:
                        print(f"  PC2 - 我们: {our_row['PC2_rescaled']:.4f}, 参考: {ref_row['PC2_rescaled']:.4f}")
        
        # 5. 数据样本展示
        print("\n📋 === 数据样本展示 ===")
        print("\n我们的数据（前5行）:")
        print(our_data.head())
        
        print("\n参考数据（前5行）:")
        print(reference_data.head())
        
        # 6. 统计信息
        print("\n📊 === 统计信息 ===")
        if 'PC1_rescaled' in our_data.columns:
            print(f"我们的PC1范围: [{our_data['PC1_rescaled'].min():.4f}, {our_data['PC1_rescaled'].max():.4f}]")
        if 'PC2_rescaled' in our_data.columns:
            print(f"我们的PC2范围: [{our_data['PC2_rescaled'].min():.4f}, {our_data['PC2_rescaled'].max():.4f}]")
            
        if 'PC1_rescaled' in reference_data.columns:
            print(f"参考PC1范围: [{reference_data['PC1_rescaled'].min():.4f}, {reference_data['PC1_rescaled'].max():.4f}]")
        if 'PC2_rescaled' in reference_data.columns:
            print(f"参考PC2范围: [{reference_data['PC2_rescaled'].min():.4f}, {reference_data['PC2_rescaled'].max():.4f}]")
        
    except Exception as e:
        print(f"❌ 加载或处理数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_pkl_files()