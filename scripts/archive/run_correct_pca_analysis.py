#!/usr/bin/env python3
"""
使用pkl文件进行正确的PCA分析
"""

import sys
import os
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

# 添加src目录到路径
sys.path.append('src')

def load_roleplay_data_from_pkl():
    """从pkl文件加载roleplay数据"""
    print("从pkl文件加载roleplay数据...")
    
    data_dir = Path("data/llm_responses_roleplay")
    processed_records = []
    
    # 遍历所有模型目录
    for model_dir in data_dir.iterdir():
        if model_dir.is_dir() and not model_dir.name.startswith('.'):
            model_name = model_dir.name.replace('_', '/')
            print(f"  处理模型: {model_name}")
            
            country_count = 0
            for pkl_file in model_dir.glob("*.pkl"):
                country_name = pkl_file.stem
                
                try:
                    with open(pkl_file, 'rb') as f:
                        responses = pickle.load(f)
                    
                    # 跳过空文件
                    if not responses or len(responses) == 0:
                        continue
                    
                    country_count += 1
                    
                    # 创建基础记录
                    processed_record = {
                        'model_name': model_name,
                        'country_name': country_name,
                        'cultural_region': 'AI Roleplay',
                        'roleplay': True
                    }
                    
                    # 处理回答
                    for response in responses:
                        if response and isinstance(response, dict):
                            question_id = response.get('question_id', '')
                            response_value = response.get('response')
                            is_valid = response.get('is_valid', False)
                            
                            # 只处理有效的回答
                            if is_valid and question_id and response_value is not None:
                                # 处理各种类型的回答
                                if isinstance(response_value, list):
                                    # 对于多选，使用第一个值作为代表
                                    if len(response_value) > 0:
                                        processed_record[question_id] = response_value[0]
                                elif isinstance(response_value, str):
                                    # 处理字符串格式的回答
                                    response_value = response_value.strip()
                                    
                                    # 处理Y002和Y003的多选回答（如"[1, 3]"或"1 3"）
                                    if question_id in ['Y002', 'Y003']:
                                        # 提取数字并计算平均值
                                        import re
                                        numbers = re.findall(r'\d+', response_value)
                                        if numbers:
                                            # 对于多选，使用第一个数字作为代表值
                                            processed_record[question_id] = int(numbers[0])
                                        else:
                                            continue
                                    else:
                                        # 单选问题
                                        if response_value.isdigit():
                                            processed_record[question_id] = int(response_value)
                                        else:
                                            # 尝试提取第一个数字
                                            numbers = re.findall(r'\d+', response_value)
                                            if numbers:
                                                processed_record[question_id] = int(numbers[0])
                                            else:
                                                continue
                                else:
                                    # 直接使用数值
                                    processed_record[question_id] = response_value
                    
                    processed_records.append(processed_record)
                    
                except Exception as e:
                    print(f"    错误处理 {country_name}: {e}")
                    continue
            
            print(f"    成功处理 {country_count} 个国家")
    
    df = pd.DataFrame(processed_records)
    print(f"✅ 总共加载了 {len(df)} 条记录")
    return df

def perform_pca_analysis(df):
    """执行PCA分析"""
    if df.empty:
        print("❌ 没有数据可供分析")
        return None
    
    print(f"\n=== 开始PCA分析 ===")
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    
    # 定义IVS问题
    ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
    
    # 检查哪些问题在数据中
    available_questions = [q for q in ivs_questions if q in df.columns]
    print(f"可用的IVS问题: {available_questions}")
    
    if not available_questions:
        print("❌ 没有找到IVS问题数据")
        return None
    
    # 提取数值数据
    numeric_data = df[available_questions].copy()
    
    # 处理缺失值
    print(f"缺失值统计:")
    for col in available_questions:
        missing = numeric_data[col].isnull().sum()
        print(f"  {col}: {missing}/{len(numeric_data)} ({missing/len(numeric_data)*100:.1f}%)")
    
    # 使用更宽松的规则：6个以上问题有回答就算有效
    print(f"使用宽松规则：6个以上问题有回答就算有效")
    
    # 计算每行有效回答的数量
    valid_counts = numeric_data.count(axis=1)
    valid_data_mask = valid_counts >= 6
    
    print(f"有效数据行数: {valid_data_mask.sum()}")
    print(f"有效数据比例: {valid_data_mask.sum()}/{len(numeric_data)} ({valid_data_mask.sum()/len(numeric_data)*100:.1f}%)")
    
    if valid_data_mask.sum() < 2:
        print("❌ 有效数据太少，无法进行PCA分析")
        return None
    
    # 使用有效数据
    complete_data = numeric_data[valid_data_mask]
    
    # 执行PCA
    try:
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        from sklearn.impute import SimpleImputer
        
        # 处理缺失值：用中位数填充
        imputer = SimpleImputer(strategy='median')
        complete_data_filled = imputer.fit_transform(complete_data)
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(complete_data_filled)
        
        # PCA分析
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(scaled_data)
        
        print(f"✅ PCA分析完成")
        print(f"解释方差比: PC1={pca.explained_variance_ratio_[0]:.3f}, PC2={pca.explained_variance_ratio_[1]:.3f}")
        print(f"累计解释方差: {pca.explained_variance_ratio_.sum():.3f}")
        
        # 创建结果DataFrame
        result_df = df.loc[complete_data.index].copy()
        result_df['PC1'] = pca_result[:, 0]
        result_df['PC2'] = pca_result[:, 1]
        
        # 重新缩放PC分数（使用Inglehart-Welzel的缩放参数）
        pc1_rescaled = (result_df['PC1'] * 1.81) + 0.38
        pc2_rescaled = (result_df['PC2'] * 1.61) - 0.01
        
        result_df['PC1_rescaled'] = pc1_rescaled
        result_df['PC2_rescaled'] = pc2_rescaled
        
        return result_df
        
    except ImportError as e:
        print(f"❌ 缺少必要的库: {e}")
        return None
    except Exception as e:
        print(f"❌ PCA分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("=== 使用PKL文件进行Roleplay PCA分析 ===")
    
    # 1. 从pkl文件加载数据
    print("\n1. 从pkl文件加载roleplay数据...")
    df = load_roleplay_data_from_pkl()
    
    if df.empty:
        print("❌ 无法加载数据，退出")
        return
    
    # 2. 执行PCA分析
    print("\n2. 执行PCA分析...")
    result_df = perform_pca_analysis(df)
    
    if result_df is not None:
        # 3. 保存结果
        print("\n3. 保存结果...")
        output_path = "data/llm_responses_roleplay/correct_pca_results.pkl"
        result_df.to_pickle(output_path)
        print(f"✅ PCA结果已保存到: {output_path}")
        
        # 4. 显示结果摘要
        print(f"\n=== 分析结果摘要 ===")
        print(f"总记录数: {len(result_df)}")
        print(f"模型数: {result_df['model_name'].nunique()}")
        print(f"国家数: {result_df['country_name'].nunique()}")
        print(f"PC1范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC1_rescaled'].max():.3f}")
        print(f"PC2范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
        
        print(f"\n模型分布:")
        print(result_df['model_name'].value_counts())
        
        print(f"\n前10条记录:")
        print(result_df[['model_name', 'country_name', 'PC1_rescaled', 'PC2_rescaled']].head(10))
        
    else:
        print("❌ PCA分析失败")

if __name__ == "__main__":
    main()
