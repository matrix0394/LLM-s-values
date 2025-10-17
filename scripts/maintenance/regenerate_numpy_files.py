import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import json
import pickle

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

def regenerate_ivs_data():
    """重新生成IVS数据文件"""
    print("=== 重新生成IVS数据文件 ===")
    
    try:
        # 从src模块导入数据处理器
        from src.data_processing import DataProcessor
        
        processor = DataProcessor()
        
        # 重新处理数据 - 使用实际存在的方法
        print("1. 重新处理IVS数据...")
        ivs_df = processor.load_ivs_data()
        
        # 保存为新的pickle文件
        output_path = "data/ivs_df_new.pkl"
        ivs_df.to_pickle(output_path)
        print(f"✅ 新的IVS数据已保存: {output_path}")
        
        return ivs_df
        
    except Exception as e:
        print(f"❌ 重新生成IVS数据失败: {e}")
        return None

def regenerate_country_codes():
    """重新生成国家代码文件"""
    print("\n=== 重新生成国家代码文件 ===")
    
    try:
        from src.data_processing import DataProcessor
        
        processor = DataProcessor()
        
        # 重新创建国家代码
        print("1. 重新创建国家代码...")
        country_codes = processor.create_country_codes()
        
        # 保存为新的pickle文件
        output_path = "data/country_codes_new.pkl"
        country_codes.to_pickle(output_path)
        print(f"✅ 新的国家代码已保存: {output_path}")
        
        return country_codes
        
    except Exception as e:
        print(f"❌ 重新生成国家代码失败: {e}")
        return None

def regenerate_valid_data():
    """重新生成有效数据文件"""
    print("\n=== 重新生成有效数据文件 ===")
    
    try:
        from src.data_processing import DataProcessor
        
        processor = DataProcessor()
        
        # 重新创建有效数据 - 使用实际存在的方法
        print("1. 重新创建有效数据...")
        # 先加载IVS数据
        ivs_df = processor.load_ivs_data()
        # 然后获取过滤后的数据
        valid_data = processor.get_filtered_data()
        
        # 保存为新的pickle文件
        output_path = "data/valid_data_new.pkl"
        valid_data.to_pickle(output_path)
        print(f"✅ 新的有效数据已保存: {output_path}")
        
        return valid_data
        
    except Exception as e:
        print(f"❌ 重新生成有效数据失败: {e}")
        return None

def regenerate_llm_processed_responses():
    """重新生成LLM处理后的回答文件"""
    print("\n=== 重新生成LLM处理后的回答文件 ===")
    
    try:
        from src.llm_data_processor import LLMDataProcessor
        
        processor = LLMDataProcessor()
        
        # 重新处理LLM回答
        print("1. 重新处理LLM回答...")
        processed_responses = processor.process_llm_responses()
        
        # 保存为新的pickle文件
        output_path = "data/llm_processed_responses_new.pkl"
        processed_responses.to_pickle(output_path)
        print(f"✅ 新的LLM处理回答已保存: {output_path}")
        
        return processed_responses
        
    except Exception as e:
        print(f"❌ 重新生成LLM处理回答失败: {e}")
        return None

def regenerate_pca_results():
    """重新生成PCA结果文件"""
    print("\n=== 重新生成PCA结果文件 ===")
    
    try:
        from src.pca_analysis import PCAAnalyzer
        
        analyzer = PCAAnalyzer()
        
        # 重新运行PCA分析
        print("1. 重新运行PCA分析...")
        pca_results = analyzer.run_full_analysis()
        
        # 保存为新的pickle文件
        output_path = "data/entity_scores_pca_new.pkl"
        pca_results.to_pickle(output_path)
        print(f"✅ 新的PCA结果已保存: {output_path}")
        
        return pca_results
        
    except Exception as e:
        print(f"❌ 重新生成PCA结果失败: {e}")
        return None

def regenerate_country_scores():
    """重新生成国家分数文件"""
    print("\n=== 重新生成国家分数文件 ===")
    
    try:
        from src.pca_analysis import PCAAnalyzer
        
        analyzer = PCAAnalyzer()
        
        # 重新计算国家分数
        print("1. 重新计算国家分数...")
        country_scores = analyzer.calculate_country_scores()
        
        # 保存为新的pickle文件
        output_path = "data/country_scores_pca_new.pkl"
        country_scores.to_pickle(output_path)
        print(f"✅ 新的国家分数已保存: {output_path}")
        
        return country_scores
        
    except Exception as e:
        print(f"❌ 重新生成国家分数失败: {e}")
        return None

def backup_old_files():
    """备份旧的有问题的文件"""
    print("\n=== 备份旧文件 ===")
    
    problem_files = [
        "data/country_codes_with_llm.pkl",
        "data/pca_results_with_llm.pkl", 
        "data/ivs_df.pkl",
        "data/country_scores_pca.pkl",
        "data/llm_processed_responses.pkl",
        "data/llm_processed_responses_ivs_format.pkl",
        "data/entity_scores_pca.pkl",
        "data/llm_roleplay_processed_responses_raw.pkl",
        "data/llm_roleplay_processed_responses.pkl",
        "data/variable_view.pkl",
        "data/valid_data.pkl"
    ]
    
    backup_dir = "data/backup_numpy_problem_files"
    os.makedirs(backup_dir, exist_ok=True)
    
    for file_path in problem_files:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, filename)
            os.rename(file_path, backup_path)
            print(f"✅ 已备份: {file_path} -> {backup_path}")

def replace_with_new_files():
    """用新文件替换旧文件"""
    print("\n=== 替换文件 ===")
    
    replacements = {
        "data/ivs_df_new.pkl": "data/ivs_df.pkl",
        "data/country_codes_new.pkl": "data/country_codes.pkl", 
        "data/valid_data_new.pkl": "data/valid_data.pkl",
        "data/llm_processed_responses_new.pkl": "data/llm_processed_responses.pkl",
        "data/entity_scores_pca_new.pkl": "data/entity_scores_pca.pkl",
        "data/country_scores_pca_new.pkl": "data/country_scores_pca.pkl"
    }
    
    for new_file, old_file in replacements.items():
        if os.path.exists(new_file):
            if os.path.exists(old_file):
                os.remove(old_file)
            os.rename(new_file, old_file)
            print(f"✅ 已替换: {new_file} -> {old_file}")

def test_new_files():
    """测试新生成的文件"""
    print("\n=== 测试新文件 ===")
    
    test_files = [
        "data/ivs_df.pkl",
        "data/country_codes.pkl",
        "data/valid_data.pkl", 
        "data/llm_processed_responses.pkl",
        "data/entity_scores_pca.pkl",
        "data/country_scores_pca.pkl"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                data = pd.read_pickle(file_path)
                print(f"✅ {file_path}: 正常加载，形状 {data.shape}")
            except Exception as e:
                print(f"❌ {file_path}: 加载失败 - {e}")
        else:
            print(f"⚠️  {file_path}: 文件不存在")

def main():
    """主函数"""
    print("=== 开始重新生成numpy版本不匹配的文件 ===")
    
    # 1. 备份旧文件
    backup_old_files()
    
    # 2. 重新生成各个文件
    print("\n开始重新生成文件...")
    
    # 按依赖顺序重新生成
    country_codes = regenerate_country_codes()
    if country_codes is None:
        print("❌ 无法继续，国家代码生成失败")
        return
    
    valid_data = regenerate_valid_data()
    if valid_data is None:
        print("❌ 无法继续，有效数据生成失败")
        return
    
    ivs_df = regenerate_ivs_data()
    if ivs_df is None:
        print("❌ 无法继续，IVS数据生成失败")
        return
    
    # 3. 替换文件
    replace_with_new_files()
    
    # 4. 测试新文件
    test_new_files()
    
    print("\n🎉 文件重新生成完成！")
    print("\n注意：")
    print("- 旧文件已备份到 data/backup_numpy_problem_files/ 目录")
    print("- 新文件使用当前numpy版本生成，应该可以正常使用")
    print("- 如果还有问题，可以从备份目录恢复旧文件")

if __name__ == "__main__":
    main()
